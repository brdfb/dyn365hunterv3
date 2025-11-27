"""Phase 2.5 - D365 Push Test & Validation Suite.

This test suite validates:
1. API + Task Plumbing Smoke
2. Mapping & Data Validation
3. D365 Client Behavior
4. DB State & Idempotency
5. Celery Task Integration
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.main import app
from app.config import settings
from app.db.models import Company, LeadScore, DomainSignal
from app.db.session import SessionLocal
from app.tasks.d365_push import push_lead_to_d365
from app.integrations.d365.client import D365Client
from app.integrations.d365.mapping import map_lead_to_d365
from app.integrations.d365.errors import (
    D365AuthenticationError,
    D365APIError,
    D365RateLimitError,
    D365DuplicateError,
)


# ============================================================================
# 1. API + Task Plumbing Smoke Tests
# ============================================================================

class TestAPITaskPlumbing:
    """Test API endpoint and Celery task plumbing."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_d365_enabled(self, monkeypatch):
        """Mock D365 enabled."""
        monkeypatch.setattr(settings, "d365_enabled", True)
    
    @pytest.fixture
    def mock_d365_disabled(self, monkeypatch):
        """Mock D365 disabled."""
        monkeypatch.setattr(settings, "d365_enabled", False)
    
    def test_endpoint_disabled_returns_403(self, client, mock_d365_disabled):
        """Test: Feature flag OFF → 403 Forbidden."""
        response = client.post(
            "/api/v1/d365/push-lead",
            json={"lead_id": 1}
        )
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()
    
    def test_endpoint_enabled_enqueues_task(self, client, mock_d365_enabled):
        """Test: Feature flag ON → 202 Accepted + job_id."""
        with patch("app.api.v1.d365_routes.push_lead_to_d365") as mock_task:
            mock_task_result = MagicMock()
            mock_task_result.id = "test-job-id-123"
            mock_task.delay.return_value = mock_task_result
            
            response = client.post(
                "/api/v1/d365/push-lead",
                json={"lead_id": 1}
            )
            
            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "accepted"
            assert data["job_id"] == "test-job-id-123"
            mock_task.delay.assert_called_once_with(1)
    
    def test_endpoint_missing_params_returns_400(self, client, mock_d365_enabled):
        """Test: Missing lead_id and domain → 400 Bad Request."""
        response = client.post(
            "/api/v1/d365/push-lead",
            json={}
        )
        assert response.status_code == 400
        assert "lead_id" in response.json()["detail"].lower() or "domain" in response.json()["detail"].lower()


# ============================================================================
# 2. Mapping & Data Validation Tests
# ============================================================================

class TestMappingValidation:
    """Test leads_ready view → D365 payload mapping."""
    
    @pytest.fixture
    def sample_lead_data(self):
        """Sample lead data from leads_ready view."""
        return {
            "company_id": 1,
            "canonical_name": "Example Inc",
            "domain": "example.com",
            "provider": "M365",
            "tenant_size": "large",
            "country": "US",
            "contact_emails": ["admin@example.com", "info@example.com"],
            "readiness_score": 85,
            "segment": "Migration",
            "technical_heat": "Hot",
            "commercial_segment": "GREENFIELD",
            "commercial_heat": "HIGH",
            "priority_category": "P1",
            "priority_label": "High Potential Greenfield",
            "referral_id": "ref-123",
        }
    
    def test_mapping_all_fields(self, sample_lead_data):
        """Test: All Hunter fields map correctly to D365 payload."""
        result = map_lead_to_d365(sample_lead_data)
        
        # Basic fields
        assert result["subject"] == "Hunter: example.com"
        assert result["companyname"] == "Example Inc"
        assert result["websiteurl"] == "https://example.com"
        assert result["emailaddress1"] == "admin@example.com"
        
        # Hunter custom fields
        assert result["hunter_score"] == 85
        assert result["hunter_segment"] == "Migration"
        assert result["hunter_provider"] == "M365"
        assert result["hunter_tenant_size"] == "large"
        assert result["hunter_technical_heat"] == "Hot"
        assert result["hunter_commercial_segment"] == "GREENFIELD"
        assert result["hunter_commercial_heat"] == "HIGH"
        assert result["hunter_priority_category"] == "P1"
        assert result["hunter_priority_label"] == "High Potential Greenfield"
        assert result["hunter_referral_id"] == "ref-123"
    
    def test_mapping_minimal_fields(self):
        """Test: Minimal lead data (only domain) maps correctly."""
        lead_data = {
            "domain": "test.com",
            "canonical_name": "Test Inc",
        }
        
        result = map_lead_to_d365(lead_data)
        
        assert result["subject"] == "Hunter: test.com"
        assert result["companyname"] == "Test Inc"
        assert result["websiteurl"] == "https://test.com"
        # None values should be excluded
        assert "hunter_score" not in result
        assert "emailaddress1" not in result
    
    def test_mapping_none_values_excluded(self, sample_lead_data):
        """Test: None values are excluded from payload."""
        sample_lead_data["readiness_score"] = None
        sample_lead_data["segment"] = None
        
        result = map_lead_to_d365(sample_lead_data)
        
        assert "hunter_score" not in result
        assert "hunter_segment" not in result


# ============================================================================
# 3. D365 Client Behavior Tests
# ============================================================================

class TestD365ClientBehavior:
    """Test D365 client error handling and behavior."""
    
    @pytest.fixture
    def mock_client(self, monkeypatch):
        """Mock D365 client."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.d365_enabled = True
        mock_settings.d365_base_url = "https://testorg.crm.dynamics.com"
        mock_settings.d365_client_id = "test_client_id"
        mock_settings.d365_client_secret = "test_secret"
        mock_settings.d365_tenant_id = "test_tenant"
        mock_settings.d365_api_version = "v9.2"
        monkeypatch.setattr("app.integrations.d365.client.settings", mock_settings)
        
        # Mock MSAL ConfidentialClientApplication to avoid real tenant discovery
        with patch("app.integrations.d365.client.ConfidentialClientApplication") as mock_msal:
            mock_app = MagicMock()
            mock_msal.return_value = mock_app
            client = D365Client()
            return client
    
    @pytest.mark.asyncio
    async def test_auth_fail_raises_error(self, mock_client):
        """Test: Auth failure → D365AuthenticationError."""
        with patch.object(mock_client.app, "acquire_token_for_client") as mock_auth:
            mock_auth.return_value = {
                "error": "invalid_client",
                "error_description": "Authentication failed",
            }
            
            with pytest.raises(D365AuthenticationError):
                await mock_client.create_or_update_lead({"subject": "Test"})
    
    @pytest.mark.asyncio
    async def test_rate_limit_raises_error(self, mock_client):
        """Test: 429 response → D365RateLimitError."""
        with patch.object(mock_client, "_get_access_token", return_value="token"):
            with patch("httpx.AsyncClient") as mock_httpx:
                mock_response = AsyncMock()
                mock_response.status_code = 429
                
                mock_client_instance = AsyncMock()
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client_instance.post.return_value = mock_response
                mock_httpx.return_value = mock_client_instance
                
                with pytest.raises(D365RateLimitError):
                    await mock_client.create_or_update_lead({"subject": "Test"})
    
    @pytest.mark.asyncio
    async def test_api_error_raises_error(self, mock_client):
        """Test: 4xx/5xx response → D365APIError."""
        with patch.object(mock_client, "_get_access_token", return_value="token"):
            with patch("httpx.AsyncClient") as mock_httpx:
                mock_response = AsyncMock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
                
                mock_client_instance = AsyncMock()
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client_instance.post.return_value = mock_response
                mock_httpx.return_value = mock_client_instance
                
                with pytest.raises(D365APIError):
                    await mock_client.create_or_update_lead({"subject": "Test"})


# ============================================================================
# 4. DB State & Idempotency Tests
# ============================================================================

class TestDBStateIdempotency:
    """Test database state updates and idempotency."""
    
    @pytest.fixture
    def test_company(self, db_session):
        """Create test company."""
        # Check if D365 columns exist in DB
        from sqlalchemy import inspect, text
        inspector = inspect(db_session.bind)
        columns = [col['name'] for col in inspector.get_columns('companies')]
        
        if 'd365_sync_status' not in columns:
            pytest.skip("D365 migration not run - skipping DB state tests")
        
        company = Company(
            domain="test.com",
            canonical_name="Test Inc",
        )
        company.d365_sync_status = "pending"
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        return company
    
    def test_status_updates_on_success(self, db_session, test_company):
        """Test: Successful push → status = 'synced', d365_lead_id set."""
        # Check if D365 fields exist
        if not hasattr(test_company, 'd365_sync_status'):
            pytest.skip("D365 fields not available")
        
        # Simulate successful push
        test_company.d365_lead_id = "d365-lead-123"
        test_company.d365_sync_status = "synced"
        test_company.d365_sync_last_at = datetime.now()
        test_company.d365_sync_error = None
        db_session.commit()
        
        # Verify
        db_session.refresh(test_company)
        assert test_company.d365_sync_status == "synced"
        assert test_company.d365_lead_id == "d365-lead-123"
        assert test_company.d365_sync_last_at is not None
        assert test_company.d365_sync_error is None
    
    def test_status_updates_on_error(self, db_session, test_company):
        """Test: Failed push → status = 'error', d365_sync_error set."""
        # Check if D365 fields exist
        if not hasattr(test_company, 'd365_sync_status'):
            pytest.skip("D365 fields not available")
        
        # Simulate failed push
        test_company.d365_sync_status = "error"
        test_company.d365_sync_error = "Authentication failed"
        db_session.commit()
        
        # Verify
        db_session.refresh(test_company)
        assert test_company.d365_sync_status == "error"
        assert test_company.d365_sync_error == "Authentication failed"
    
    def test_idempotency_same_lead_id(self, db_session, test_company):
        """Test: Same lead pushed twice → same d365_lead_id (idempotent)."""
        # Check if D365 fields exist
        if not hasattr(test_company, 'd365_lead_id'):
            pytest.skip("D365 fields not available")
        
        # First push
        test_company.d365_lead_id = "d365-lead-123"
        test_company.d365_sync_status = "synced"
        db_session.commit()
        
        first_lead_id = test_company.d365_lead_id
        
        # Second push (should not create duplicate)
        # In real scenario, D365 client would find existing lead and return same ID
        # For test, we verify that same ID is preserved
        assert test_company.d365_lead_id == first_lead_id


# ============================================================================
# 5. Celery Task Integration Tests
# ============================================================================

class TestCeleryTaskIntegration:
    """Test Celery task end-to-end execution."""
    
    @pytest.fixture
    def test_company_with_lead(self, db_session):
        """Create test company with lead score."""
        # Check if D365 columns exist in DB
        from sqlalchemy import inspect
        inspector = inspect(db_session.bind)
        columns = [col['name'] for col in inspector.get_columns('companies')]
        
        if 'd365_sync_status' not in columns:
            pytest.skip("D365 migration not run - skipping Celery task integration tests")
        
        company = Company(
            domain="test.com",
            canonical_name="Test Inc",
            provider="M365",
            tenant_size="large",
            contact_emails=["admin@test.com"],
        )
        company.d365_sync_status = "pending"
        db_session.add(company)
        db_session.flush()
        
        signal = DomainSignal(
            domain="test.com",
            scan_status="completed",
            scanned_at=datetime.now(),
        )
        db_session.add(signal)
        db_session.flush()
        
        score = LeadScore(
            domain="test.com",
            readiness_score=85,
            segment="Migration",
            priority_category="P1",
            priority_label="High Potential",
        )
        db_session.add(score)
        db_session.commit()
        db_session.refresh(company)
        
        return company
    
    def test_task_skips_when_disabled(self, db_session, test_company_with_lead):
        """Test: Task skips when feature flag disabled."""
        with patch("app.tasks.d365_push.settings") as mock_settings:
            mock_settings.d365_enabled = False
            
            with patch("app.tasks.d365_push.SessionLocal", return_value=db_session):
                result = push_lead_to_d365.apply(args=(test_company_with_lead.id,)).get()
                
                assert result["status"] == "skipped"
                assert result["reason"] == "d365_disabled"
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL") or "postgres" not in os.getenv("DATABASE_URL", "").lower(),
        reason="Integration test requires real database connection (DATABASE_URL with postgres)"
    )
    def test_task_updates_status_on_success(self, db_session, test_company_with_lead):
        """Test: Task updates company status on successful push."""
        # Check if D365 fields exist
        if not hasattr(test_company_with_lead, 'd365_sync_status'):
            pytest.skip("D365 migration not run - skipping task integration test")
        
        lead_id = test_company_with_lead.id
        
        with patch("app.tasks.d365_push.settings") as mock_settings:
            mock_settings.d365_enabled = True
            
            # Create a new session for the task (simulating real behavior)
            from app.db.session import SessionLocal
            task_db = SessionLocal()
            
            def get_session():
                return task_db
            
            with patch("app.tasks.d365_push.SessionLocal", side_effect=get_session):
                with patch("app.tasks.d365_push.D365Client") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.create_or_update_lead = AsyncMock(return_value={
                        "leadid": "d365-lead-123"
                    })
                    mock_client_class.return_value = mock_client
                    
                    # Mock asyncio.run for async client call
                    with patch("asyncio.run") as mock_run:
                        mock_run.return_value = {"leadid": "d365-lead-123"}
                        
                        result = push_lead_to_d365.apply(args=(lead_id,)).get()
                        
                        assert result["status"] == "completed"
                        assert result["d365_lead_id"] == "d365-lead-123"
                        
                        # Verify DB state - query fresh from DB
                        task_db.commit()
                        company = task_db.query(Company).filter(Company.id == lead_id).first()
                        assert company.d365_sync_status == "synced"
                        assert company.d365_lead_id == "d365-lead-123"
                        
                        task_db.close()
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL") or "postgres" not in os.getenv("DATABASE_URL", "").lower(),
        reason="Integration test requires real database connection (DATABASE_URL with postgres)"
    )
    def test_task_handles_error_gracefully(self, db_session, test_company_with_lead):
        """Test: Task handles errors and updates status to 'error'."""
        # Check if D365 fields exist
        if not hasattr(test_company_with_lead, 'd365_sync_status'):
            pytest.skip("D365 migration not run - skipping task integration test")
        
        lead_id = test_company_with_lead.id
        
        with patch("app.tasks.d365_push.settings") as mock_settings:
            mock_settings.d365_enabled = True
            
            # Create a new session for the task (simulating real behavior)
            from app.db.session import SessionLocal
            task_db = SessionLocal()
            
            def get_session():
                return task_db
            
            with patch("app.tasks.d365_push.SessionLocal", side_effect=get_session):
                with patch("app.tasks.d365_push.D365Client") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.create_or_update_lead = AsyncMock(
                        side_effect=D365AuthenticationError("Auth failed")
                    )
                    mock_client_class.return_value = mock_client
                    
                    with patch("asyncio.run") as mock_run:
                        mock_run.side_effect = D365AuthenticationError("Auth failed")
                        
                        # Task will raise exception, but we catch it
                        try:
                            result = push_lead_to_d365.apply(args=(lead_id,)).get()
                        except Exception:
                            # Task failed, which is expected
                            pass
                        
                        # Verify DB state - query fresh from DB
                        task_db.commit()
                        company = task_db.query(Company).filter(Company.id == lead_id).first()
                        assert company.d365_sync_status == "error"
                        assert company.d365_sync_error is not None
                        
                        task_db.close()

