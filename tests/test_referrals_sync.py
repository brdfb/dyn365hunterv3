"""Backend tests for Partner Center referral sync (Task 2.4)."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.tasks import sync_partner_center_referrals_task
from app.db.session import SessionLocal


class TestReferralsSyncEndpoint:
    """Tests for POST /api/referrals/sync endpoint."""

    def test_sync_endpoint_feature_flag_disabled(self, client: TestClient):
        """Test that endpoint returns 400 when feature flag is disabled."""
        with patch("app.api.referrals.settings") as mock_settings:
            mock_settings.partner_center_enabled = False

            response = client.post("/api/referrals/sync")

            assert response.status_code == 400
            assert "disabled" in response.json()["detail"].lower()
            assert "feature flag" in response.json()["detail"].lower()

    def test_sync_endpoint_feature_flag_enabled_enqueues_task(
        self, client: TestClient
    ):
        """Test that endpoint enqueues Celery task when feature flag is enabled."""
        with patch("app.api.referrals.settings") as mock_settings:
            mock_settings.partner_center_enabled = True

            with patch(
                "app.api.referrals.sync_partner_center_referrals_task"
            ) as mock_task:
                # Mock Celery task result
                mock_task_result = MagicMock()
                mock_task_result.id = "test-task-id-123"
                mock_task.delay.return_value = mock_task_result

                response = client.post("/api/referrals/sync")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["enqueued"] is True
                assert data["task_id"] == "test-task-id-123"
                assert "enqueued" in data["message"].lower()

                # Verify task was called
                mock_task.delay.assert_called_once()

    def test_sync_endpoint_error_handling(self, client: TestClient):
        """Test that endpoint handles errors gracefully (500)."""
        with patch("app.api.referrals.settings") as mock_settings:
            mock_settings.partner_center_enabled = True

            with patch(
                "app.api.referrals.sync_partner_center_referrals_task"
            ) as mock_task:
                # Mock task to raise exception
                mock_task.delay.side_effect = Exception("Task enqueue failed")

                response = client.post("/api/referrals/sync")

                assert response.status_code == 500
                assert "failed" in response.json()["detail"].lower()


class TestReferralsSyncTask:
    """Tests for sync_partner_center_referrals_task Celery task."""

    @pytest.fixture
    def db(self):
        """Create a database session for testing."""
        db = SessionLocal()
        try:
            yield db
            db.rollback()
        finally:
            db.close()

    def test_task_skips_when_feature_flag_disabled(self, db: Session):
        """Test that task skips execution when feature flag is disabled."""
        with patch("app.core.tasks.settings") as mock_settings:
            mock_settings.partner_center_enabled = False
            mock_settings.environment = "test"

            # Mock task context (bind=True means self is passed automatically)
            mock_task = MagicMock()
            mock_task.request = MagicMock()
            mock_task.request.id = "test-task-id"

            # For bind=True tasks, we need to patch SessionLocal to use our test db
            # Then call the task function directly (same pattern as process_pending_alerts_task)
            # Note: sync_referrals_from_partner_center takes db as parameter, so we patch SessionLocal
            with patch("app.core.tasks.SessionLocal", return_value=db):
                with patch("app.core.referral_ingestion.sync_referrals_from_partner_center") as mock_sync:
                    # Call task directly - Celery wrapper will pass mock_task as 'self'
                    # But Celery wrapper adds 'self' automatically, so we get TypeError
                    # Solution: Use apply() method or call run() directly
                    result = sync_partner_center_referrals_task.apply(args=()).get()

            assert result["status"] == "skipped"
            assert result["reason"] == "Feature flag disabled"
            assert result["success_count"] == 0
            assert result["failure_count"] == 0
            assert result["skipped_count"] == 0

    def test_task_calls_sync_referrals_from_partner_center(self, db: Session):
        """Test that task calls sync_referrals_from_partner_center() when enabled."""
        with patch("app.core.tasks.settings") as mock_settings:
            mock_settings.partner_center_enabled = True
            mock_settings.environment = "test"

            with patch(
                "app.core.referral_ingestion.sync_referrals_from_partner_center"
            ) as mock_sync:
                # Mock sync result
                mock_sync.return_value = {
                    "success_count": 5,
                    "failure_count": 1,
                    "skipped_count": 2,
                }

                # Mock task context (bind=True means self is passed automatically)
                mock_task = MagicMock()
                mock_task.request = MagicMock()
                mock_task.request.id = "test-task-id"

                # Call task using apply() method (bypasses Celery wrapper issues)
                with patch("app.core.tasks.SessionLocal", return_value=db):
                    result = sync_partner_center_referrals_task.apply(args=()).get()

                # Verify sync was called
                mock_sync.assert_called_once_with(db)

                # Verify result
                assert result["status"] == "completed"
                assert result["success_count"] == 5
                assert result["failure_count"] == 1
                assert result["skipped_count"] == 2

    def test_task_handles_errors_gracefully(self, db: Session):
        """Test that task handles errors gracefully (logs but doesn't crash)."""
        with patch("app.core.tasks.settings") as mock_settings:
            mock_settings.partner_center_enabled = True
            mock_settings.environment = "test"

            with patch(
                "app.core.referral_ingestion.sync_referrals_from_partner_center"
            ) as mock_sync:
                # Mock sync to raise exception
                mock_sync.side_effect = Exception("Sync failed")

                # Mock task context
                mock_task = MagicMock()
                mock_task.request = MagicMock()
                mock_task.request.id = "test-task-id"

                with patch("app.core.tasks.logger") as mock_logger:
                    # Call task using apply() method (bypasses Celery wrapper issues)
                    with patch("app.core.tasks.SessionLocal", return_value=db):
                        result = sync_partner_center_referrals_task.apply(args=()).get()

                    # Verify error was logged
                    mock_logger.error.assert_called_once()
                    error_call = mock_logger.error.call_args
                    assert "partner_center_sync_task_error" in str(error_call)
                    assert "source" in error_call.kwargs
                    assert error_call.kwargs["source"] == "partner_center"

                    # Verify result indicates failure but doesn't crash
                    assert result["status"] == "failed"
                    assert "error" in result
                    assert result["success_count"] == 0
                    assert result["failure_count"] == 0
                    assert result["skipped_count"] == 0

    def test_task_logs_structured_data(self, db: Session):
        """Test that task logs structured data (source, duration, env, etc.)."""
        with patch("app.core.tasks.settings") as mock_settings:
            mock_settings.partner_center_enabled = True
            mock_settings.environment = "test"

            with patch(
                "app.core.referral_ingestion.sync_referrals_from_partner_center"
            ) as mock_sync:
                mock_sync.return_value = {
                    "success_count": 3,
                    "failure_count": 0,
                    "skipped_count": 1,
                }

                # Mock task context
                mock_task = MagicMock()
                mock_task.request = MagicMock()
                mock_task.request.id = "test-task-id"

                with patch("app.core.tasks.logger") as mock_logger:
                    # Call task using apply() method (bypasses Celery wrapper issues)
                    with patch("app.core.tasks.SessionLocal", return_value=db):
                        result = sync_partner_center_referrals_task.apply(args=()).get()

                    # Verify structured logging
                    # Check start log
                    start_calls = [
                        call
                        for call in mock_logger.info.call_args_list
                        if "partner_center_sync_task_started" in str(call)
                    ]
                    assert len(start_calls) > 0
                    start_call = start_calls[0]
                    assert "source" in start_call.kwargs
                    assert start_call.kwargs["source"] == "partner_center"
                    assert "task_id" in start_call.kwargs
                    assert "feature_flag_state" in start_call.kwargs
                    assert "env" in start_call.kwargs

                    # Check completion log
                    completion_calls = [
                        call
                        for call in mock_logger.info.call_args_list
                        if "partner_center_sync_task_completed" in str(call)
                    ]
                    assert len(completion_calls) > 0
                    completion_call = completion_calls[0]
                    assert "source" in completion_call.kwargs
                    assert "duration_sec" in completion_call.kwargs
                    assert "duration_ms" in completion_call.kwargs
                    assert "success_count" in completion_call.kwargs
                    assert "failure_count" in completion_call.kwargs
                    assert "skipped_count" in completion_call.kwargs

                    # Verify result
                    assert result["status"] == "completed"

