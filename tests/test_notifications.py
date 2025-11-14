"""Tests for notification engine (G18)."""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Alert, AlertConfig, Company
from app.db.session import SessionLocal
from app.core.notifications import (
    send_webhook_notification,
    send_email_notification,
    process_pending_alerts,
)


@pytest.fixture
def db():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def test_company(db: Session):
    """Create a test company."""
    company = Company(canonical_name="Test Company", domain="test-notifications.com")
    db.add(company)
    db.commit()
    return company


@pytest.fixture
def test_alert(db: Session, test_company):
    """Create a test alert."""
    alert = Alert(
        domain=test_company.domain,
        alert_type="mx_changed",
        alert_message="MX root changed from outlook.com to google.com",
        status="pending",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


class TestWebhookNotification:
    """Tests for send_webhook_notification."""

    @pytest.mark.asyncio
    async def test_send_webhook_notification_success(self, test_alert):
        """Test successful webhook notification."""
        webhook_url = "https://example.com/webhook"

        with patch("app.core.notifications.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            mock_response.status_code = 200

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            result = await send_webhook_notification(webhook_url, test_alert)

            assert result is True
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            assert call_args[0][0] == webhook_url
            assert "alert_id" in call_args[1]["json"]
            assert call_args[1]["json"]["domain"] == test_alert.domain

    @pytest.mark.asyncio
    async def test_send_webhook_notification_http_error(self, test_alert):
        """Test webhook notification with HTTP error."""
        webhook_url = "https://example.com/webhook"

        with patch("app.core.notifications.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Not Found", request=MagicMock(), response=mock_response
                )
            )
            mock_response.status_code = 404

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            result = await send_webhook_notification(webhook_url, test_alert)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_notification_timeout(self, test_alert):
        """Test webhook notification with timeout."""
        webhook_url = "https://example.com/webhook"

        with patch("app.core.notifications.httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            mock_client.return_value = mock_client_instance

            result = await send_webhook_notification(webhook_url, test_alert)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_notification_connection_error(self, test_alert):
        """Test webhook notification with connection error."""
        webhook_url = "https://example.com/webhook"

        with patch("app.core.notifications.httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_instance.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )
            mock_client.return_value = mock_client_instance

            result = await send_webhook_notification(webhook_url, test_alert)

            assert result is False


class TestEmailNotification:
    """Tests for send_email_notification."""

    @pytest.mark.asyncio
    async def test_send_email_notification_success(self, test_alert):
        """Test successful email notification (placeholder)."""
        email_address = "test@example.com"

        result = await send_email_notification(email_address, test_alert)

        assert result is True

    @pytest.mark.asyncio
    async def test_send_email_notification_exception(self, test_alert):
        """Test email notification with exception."""
        email_address = "test@example.com"

        with patch("app.core.notifications.logger") as mock_logger:
            mock_logger.info = MagicMock(side_effect=Exception("Log error"))

            result = await send_email_notification(email_address, test_alert)

            # Should still return True (placeholder implementation)
            assert result is True


class TestProcessPendingAlerts:
    """Tests for process_pending_alerts."""

    @pytest.mark.asyncio
    async def test_process_pending_alerts_no_alerts(self, db: Session):
        """Test processing when no pending alerts exist."""
        processed = await process_pending_alerts(db)

        assert processed == 0

    @pytest.mark.asyncio
    async def test_process_pending_alerts_no_config(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with no configuration."""
        # Alert should be marked as sent (no notification needed)
        processed = await process_pending_alerts(db)

        assert processed == 1
        db.refresh(test_alert)
        assert test_alert.status == "sent"
        assert test_alert.sent_at is not None

    @pytest.mark.asyncio
    async def test_process_pending_alerts_webhook_success(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with webhook config (success)."""
        # Create webhook config
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="webhook",
            enabled=True,
            frequency="immediate",
            webhook_url="https://example.com/webhook",
        )
        db.add(config)
        db.commit()

        with patch("app.core.notifications.send_webhook_notification") as mock_webhook:
            mock_webhook.return_value = True

            processed = await process_pending_alerts(db)

            assert processed == 1
            db.refresh(test_alert)
            assert test_alert.status == "sent"
            assert test_alert.notification_method == "webhook"
            assert test_alert.sent_at is not None
            mock_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pending_alerts_webhook_failure(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with webhook config (failure)."""
        # Create webhook config
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="webhook",
            enabled=True,
            frequency="immediate",
            webhook_url="https://example.com/webhook",
        )
        db.add(config)
        db.commit()

        with patch("app.core.notifications.send_webhook_notification") as mock_webhook:
            mock_webhook.return_value = False

            processed = await process_pending_alerts(db)

            assert processed == 1
            db.refresh(test_alert)
            assert test_alert.status == "failed"
            mock_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pending_alerts_email_success(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with email config (success)."""
        # Create email config
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="email",
            enabled=True,
            frequency="immediate",
            email_address="test@example.com",
        )
        db.add(config)
        db.commit()

        with patch("app.core.notifications.send_email_notification") as mock_email:
            mock_email.return_value = True

            processed = await process_pending_alerts(db)

            assert processed == 1
            db.refresh(test_alert)
            assert test_alert.status == "sent"
            assert test_alert.notification_method == "email"
            assert test_alert.sent_at is not None
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pending_alerts_email_failure(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with email config (failure)."""
        # Create email config
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="email",
            enabled=True,
            frequency="immediate",
            email_address="test@example.com",
        )
        db.add(config)
        db.commit()

        with patch("app.core.notifications.send_email_notification") as mock_email:
            mock_email.return_value = False

            processed = await process_pending_alerts(db)

            assert processed == 1
            db.refresh(test_alert)
            assert test_alert.status == "failed"
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pending_alerts_disabled_config(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with disabled config."""
        # Create disabled config
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="webhook",
            enabled=False,  # Disabled
            frequency="immediate",
            webhook_url="https://example.com/webhook",
        )
        db.add(config)
        db.commit()

        processed = await process_pending_alerts(db)

        # Should be marked as sent (no config match)
        assert processed == 1
        db.refresh(test_alert)
        assert test_alert.status == "sent"

    @pytest.mark.asyncio
    async def test_process_pending_alerts_multiple_configs(
        self, db: Session, test_company, test_alert
    ):
        """Test processing alerts with multiple configs (first success wins)."""
        # Create multiple configs
        config1 = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="webhook",
            enabled=True,
            frequency="immediate",
            webhook_url="https://example.com/webhook1",
        )
        config2 = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="email",
            enabled=True,
            frequency="immediate",
            email_address="test@example.com",
        )
        db.add(config1)
        db.add(config2)
        db.commit()

        with patch("app.core.notifications.send_webhook_notification") as mock_webhook:
            mock_webhook.return_value = True

            processed = await process_pending_alerts(db)

            assert processed == 1
            db.refresh(test_alert)
            assert test_alert.status == "sent"
            assert test_alert.notification_method == "webhook"
            # Only webhook should be called (first success)
            mock_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_pending_alerts_multiple_alerts(
        self, db: Session, test_company
    ):
        """Test processing multiple pending alerts."""
        # Create multiple alerts
        alert1 = Alert(
            domain=test_company.domain,
            alert_type="mx_changed",
            alert_message="MX changed 1",
            status="pending",
        )
        alert2 = Alert(
            domain=test_company.domain,
            alert_type="dmarc_added",
            alert_message="DMARC added",
            status="pending",
        )
        db.add(alert1)
        db.add(alert2)
        db.commit()

        # Create config for mx_changed only
        config = AlertConfig(
            user_id="test-user",
            alert_type="mx_changed",
            notification_method="webhook",
            enabled=True,
            frequency="immediate",
            webhook_url="https://example.com/webhook",
        )
        db.add(config)
        db.commit()

        with patch("app.core.notifications.send_webhook_notification") as mock_webhook:
            mock_webhook.return_value = True

            processed = await process_pending_alerts(db)

            assert processed == 2
            db.refresh(alert1)
            db.refresh(alert2)
            assert alert1.status == "sent"  # Has config
            assert alert2.status == "sent"  # No config, marked as sent
            mock_webhook.assert_called_once()  # Only for alert1
