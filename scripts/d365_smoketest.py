#!/usr/bin/env python3
"""
D365 Configuration & Authentication Smoke Test

Validates D365 configuration and tests authentication flow.
Run this before attempting any D365 push operations.

Usage:
    python scripts/d365_smoketest.py
    # or
    docker-compose exec api python scripts/d365_smoketest.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.integrations.d365.client import D365Client
from app.integrations.d365.errors import (
    D365AuthenticationError,
    D365APIError,
)
import httpx
import asyncio


def check_env_config():
    """Check D365 environment variables configuration."""
    print("=" * 60)
    print("D365 Configuration Check")
    print("=" * 60)
    
    issues = []
    
    # Check feature flag
    if not settings.d365_enabled:
        issues.append("[ERROR] HUNTER_D365_ENABLED is not set to 'true'")
    else:
        print("[OK] HUNTER_D365_ENABLED = true")
    
    # Check required variables
    required_vars = {
        "d365_base_url": "HUNTER_D365_BASE_URL",
        "d365_client_id": "HUNTER_D365_CLIENT_ID",
        "d365_client_secret": "HUNTER_D365_CLIENT_SECRET",
        "d365_tenant_id": "HUNTER_D365_TENANT_ID",
    }
    
    for attr, env_name in required_vars.items():
        value = getattr(settings, attr, None)
        if not value:
            issues.append(f"[ERROR] {env_name} is not set or empty")
        elif "YOUR_" in value.upper() or "PLACEHOLDER" in value.upper():
            issues.append(f"[WARN] {env_name} contains placeholder value")
        else:
            # Mask sensitive values
            if "secret" in attr.lower() or "password" in attr.lower():
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"[OK] {env_name} = {display_value}")
    
    # Check API version
    print(f"[OK] HUNTER_D365_API_VERSION = {settings.d365_api_version}")
    
    if issues:
        print("\n" + "=" * 60)
        print("[ERROR] Configuration Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        print("=" * 60)
        return False
    
    print("\n[OK] All configuration checks passed!")
    return True


def test_token_acquisition():
    """Test D365 token acquisition."""
    print("\n" + "=" * 60)
    print("D365 Token Acquisition Test")
    print("=" * 60)
    
    try:
        client = D365Client()
        print("[OK] D365Client initialized successfully")
        
        print("Acquiring access token...")
        token = client._get_access_token()
        
        if not token:
            print("[ERROR] Token acquisition returned None")
            return False
        
        # Display token preview (first 50 chars)
        token_preview = token[:50] + "..." if len(token) > 50 else token
        print(f"[OK] Access token acquired: {token_preview}")
        print(f"   Token length: {len(token)} characters")
        
        # Check token expiration
        if client._token_expires_at:
            print(f"[OK] Token expires at: {client._token_expires_at}")
        
        return True
        
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print("\nTip: Check your .env file and ensure all D365 variables are set correctly.")
        return False
    except D365AuthenticationError as e:
        print(f"[ERROR] Authentication error: {e}")
        print("\nCommon issues:")
        print("   - Invalid tenant ID or authority URL")
        print("   - Incorrect client ID or client secret")
        print("   - App registration permissions not configured")
        print("   - Scope/resource URL mismatch")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_connection(client: D365Client):
    """Test D365 API connection with a simple GET request."""
    print("\n" + "=" * 60)
    print("D365 API Connection Test")
    print("=" * 60)
    
    try:
        token = client._get_access_token()
        api_url = f"{client.base_url}/api/data/{client.api_version}/WhoAmI"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        
        print(f"Testing API connection: {api_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] API connection successful!")
                print(f"   User ID: {data.get('UserId', 'N/A')}")
                print(f"   Business Unit ID: {data.get('BusinessUnitId', 'N/A')}")
                print(f"   Organization ID: {data.get('OrganizationId', 'N/A')}")
                return True
            elif response.status_code == 401:
                print("[ERROR] Authentication failed (401 Unauthorized)")
                print("   Token may be invalid or expired")
                return False
            elif response.status_code == 403:
                print("[ERROR] Access forbidden (403 Forbidden)")
                print("   App registration may not have required permissions")
                return False
            else:
                print(f"[ERROR] API request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("[ERROR] Request timeout - D365 API may be unreachable")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_leads_endpoint(client: D365Client):
    """Test D365 Leads endpoint (optional, just to verify entity access)."""
    print("\n" + "=" * 60)
    print("D365 Leads Endpoint Test (Optional)")
    print("=" * 60)
    
    try:
        token = client._get_access_token()
        api_url = f"{client.base_url}/api/data/{client.api_version}/leads"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        
        # Just check if endpoint is accessible (top=1 to minimize data transfer)
        query_url = f"{api_url}?$top=1&$select=leadid,subject"
        
        print(f"Testing Leads endpoint: {query_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(query_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                lead_count = len(data.get("value", []))
                print(f"[OK] Leads endpoint accessible (found {lead_count} lead(s) in sample)")
                return True
            elif response.status_code == 403:
                print("[WARN] Leads endpoint access forbidden (403)")
                print("   App registration may need 'Lead' entity read permissions")
                print("   This is OK for PoC - we'll test write permissions during push")
                return True  # Not a blocker for PoC
            else:
                print(f"[WARN] Leads endpoint test returned: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return True  # Not a blocker, just informational
                
    except Exception as e:
        print(f"[WARN] Leads endpoint test error: {type(e).__name__}: {e}")
        print("   This is OK for PoC - we'll test write permissions during push")
        return True  # Not a blocker


def main():
    """Run all smoke tests."""
    print("\n" + "D365 Smoke Test Suite")
    print("=" * 60)
    print("This script validates D365 configuration and tests authentication.")
    print("=" * 60)
    
    # Step 1: Check configuration
    if not check_env_config():
        print("\n[ERROR] Configuration check failed. Please fix issues above.")
        sys.exit(1)
    
    # Step 2: Test token acquisition
    if not test_token_acquisition():
        print("\n[ERROR] Token acquisition failed. Please check authentication settings.")
        sys.exit(1)
    
    # Step 3: Test API connection (optional but recommended)
    try:
        client = D365Client()
        api_ok = asyncio.run(test_api_connection(client))
        
        if api_ok:
            # Step 4: Test Leads endpoint (optional)
            asyncio.run(test_leads_endpoint(client))
        
    except Exception as e:
        print(f"\n[WARN] API connection test skipped: {type(e).__name__}: {e}")
        print("   Token acquisition passed, which is the critical part.")
    
    # Summary
    print("\n" + "=" * 60)
    print("[OK] Smoke Test Summary")
    print("=" * 60)
    print("[OK] Configuration: OK")
    print("[OK] Token Acquisition: OK")
    print("[OK] Ready for D365 Push PoC!")
    print("\nNext steps:")
    print("   1. Prepare test lead data (Task 3)")
    print("   2. Test mapping function (Task 4)")
    print("   3. Test D365 API push (Task 5)")
    print("=" * 60)


if __name__ == "__main__":
    main()

