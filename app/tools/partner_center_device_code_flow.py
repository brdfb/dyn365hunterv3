#!/usr/bin/env python3
"""Partner Center Device Code Flow - Initial Authentication Script

This script performs the initial authentication for Partner Center integration
using Device Code Flow. After successful authentication, the token cache will
be saved and can be used for silent token acquisition in background jobs.

Usage:
    docker-compose exec api python -m app.tools.partner_center_device_code_flow
"""

import sys
from msal import PublicClientApplication
from app.config import settings

def main():
    """Perform Device Code Flow authentication."""
    
    # Check if feature flag is enabled
    if not settings.partner_center_enabled:
        print("⚠️  WARNING: Partner Center feature flag is disabled.")
        print("   Set HUNTER_PARTNER_CENTER_ENABLED=true in .env file.")
        print("   However, we can still test authentication...")
        print()
    
    # Check required configuration
    if not all([
        settings.partner_center_client_id,
        settings.partner_center_tenant_id,
        settings.partner_center_api_url,
    ]):
        print("❌ ERROR: Partner Center credentials not configured!")
        print("   Required: CLIENT_ID, TENANT_ID, API_URL")
        sys.exit(1)
    
    # Create MSAL app
    authority = f"https://login.microsoftonline.com/{settings.partner_center_tenant_id}"
    app = PublicClientApplication(
        client_id=settings.partner_center_client_id,
        authority=authority,
    )
    
    print("=" * 60)
    print("Partner Center - Device Code Flow Authentication")
    print("=" * 60)
    print()
    
    # Initiate device code flow
    try:
        flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])
    except Exception as e:
        print(f"❌ ERROR: Failed to initiate device code flow: {e}")
        sys.exit(1)
    
    # Display instructions
    print("📱 Authentication Instructions:")
    print()
    print(f"1. Open your browser and go to:")
    print(f"   {flow['verification_uri']}")
    print()
    print(f"2. Enter this code:")
    print(f"   {flow['user_code']}")
    print()
    print("3. Complete the authentication (login + consent)")
    print("   (MFA will be required if enabled)")
    print()
    print("=" * 60)
    print("⏳ Waiting for authentication...")
    print("   (This may take up to 15 minutes)")
    print("=" * 60)
    print()
    
    # Wait for authentication
    try:
        result = app.acquire_token_by_device_flow(flow)
    except KeyboardInterrupt:
        print("\n❌ Authentication cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Authentication failed: {e}")
        sys.exit(1)
    
    # Check result
    if "access_token" in result:
        print("✅ SUCCESS: Token acquired!")
        print()
        print("Token Information:")
        print(f"  - Expires in: {result.get('expires_in', 'N/A')} seconds")
        print(f"  - Token type: {result.get('token_type', 'N/A')}")
        print(f"  - Scope: {result.get('scope', 'N/A')}")
        print()
        print("Token cache saved to: .token_cache")
        print()
        print("✅ FAZ 2 PASSED: Authentication successful!")
        print()
        print("Next steps:")
        print("  1. Token cache is now available for silent token acquisition")
        print("  2. Background jobs can use silent token acquisition")
        print("  3. You can proceed to FAZ 3 (Feature Flag ON validation)")
        return 0
    else:
        print("❌ ERROR: Token acquisition failed")
        print()
        print("Error details:")
        print(f"  - Error: {result.get('error', 'Unknown')}")
        print(f"  - Description: {result.get('error_description', 'N/A')}")
        print(f"  - Error codes: {result.get('error_codes', [])}")
        print()
        print("Troubleshooting:")
        print("  1. Check Azure AD App Registration permissions")
        print("  2. Verify Partner Center API permissions are granted")
        print("  3. Check if admin consent is required")
        print("  4. Verify CLIENT_ID and TENANT_ID are correct")
        return 1


if __name__ == "__main__":
    sys.exit(main())

