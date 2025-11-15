#!/usr/bin/env python3
"""
Azure AD Authentication Test Script
Tests Azure AD authentication endpoints and configuration.
"""

import sys
import requests
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.NC}")

def test_health_check(base_url: str) -> bool:
    """Test if backend is running."""
    print(f"\n{Colors.YELLOW}Test 1: Health Check{Colors.NC}")
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        if response.status_code == 200:
            print_success("Backend is running")
            data = response.json()
            print_info(f"  Status: {data.get('status', 'unknown')}")
            print_info(f"  Database: {data.get('database', 'unknown')}")
            print_info(f"  Redis: {data.get('redis', 'unknown')}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend is not running")
        print_info("  Run: docker-compose up api")
        print_info("  Or: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking health: {e}")
        return False

def test_azure_ad_configuration(auth_base: str) -> bool:
    """Test if Azure AD is configured."""
    print(f"\n{Colors.YELLOW}Test 2: Azure AD Configuration{Colors.NC}")
    try:
        # Don't follow redirects to check the response
        response = requests.get(f"{auth_base}/login", allow_redirects=False, timeout=5)
        
        if response.status_code == 503:
            print_error("Azure AD is not configured")
            print_info("  Check .env file for:")
            print_info("    - HUNTER_AZURE_CLIENT_ID")
            print_info("    - HUNTER_AZURE_CLIENT_SECRET")
            print_info("    - HUNTER_AZURE_TENANT_ID")
            return False
        elif response.status_code in [302, 307]:
            print_success("Azure AD is configured and redirecting")
            redirect_url = response.headers.get('Location', '')
            if redirect_url:
                print_info(f"  Redirect URL: {redirect_url}")
                if 'login.microsoftonline.com' in redirect_url:
                    print_success("  Redirect URL points to Microsoft login")
                    
                    # Parse redirect URL to check parameters
                    parsed = urlparse(redirect_url)
                    params = parse_qs(parsed.query)
                    
                    if 'client_id' in params:
                        print_info(f"  Client ID in URL: {params['client_id'][0][:20]}...")
                    if 'redirect_uri' in params:
                        print_info(f"  Redirect URI: {params['redirect_uri'][0]}")
                    if 'scope' in params:
                        print_info(f"  Scopes: {params['scope'][0]}")
                    if 'state' in params:
                        print_info(f"  State (CSRF token): {params['state'][0][:20]}...")
                else:
                    print_warning("  Redirect URL doesn't look like Microsoft login")
            return True
        else:
            print_warning(f"Unexpected response: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend")
        return False
    except Exception as e:
        print_error(f"Error testing Azure AD configuration: {e}")
        return False

def test_callback_endpoint(auth_base: str) -> bool:
    """Test callback endpoint without code."""
    print(f"\n{Colors.YELLOW}Test 3: Callback Endpoint (without code){Colors.NC}")
    try:
        response = requests.get(f"{auth_base}/callback", timeout=5)
        if response.status_code == 400:
            print_success("Callback endpoint correctly rejects requests without code")
            try:
                data = response.json()
                detail = data.get('detail', '')
                print_info(f"  Error message: {detail}")
            except:
                pass
            return True
        else:
            print_warning(f"Unexpected response: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing callback endpoint: {e}")
        return False

def test_me_endpoint(auth_base: str) -> bool:
    """Test /auth/me endpoint (should require authentication)."""
    print(f"\n{Colors.YELLOW}Test 4: /auth/me Endpoint (requires authentication){Colors.NC}")
    try:
        response = requests.get(f"{auth_base}/me", timeout=5)
        if response.status_code in [401, 403]:
            print_success("/auth/me correctly requires authentication")
            try:
                data = response.json()
                detail = data.get('detail', '')
                print_info(f"  Error message: {detail}")
            except:
                pass
            return True
        else:
            print_warning(f"Unexpected response: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing /auth/me endpoint: {e}")
        return False

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    auth_base = f"{base_url}/auth"
    
    print("=" * 50)
    print("Azure AD Authentication Test")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Auth Base: {auth_base}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check(base_url)))
    if results[-1][1]:  # Only continue if backend is running
        results.append(("Azure AD Configuration", test_azure_ad_configuration(auth_base)))
        results.append(("Callback Endpoint", test_callback_endpoint(auth_base)))
        results.append(("Me Endpoint", test_me_endpoint(auth_base)))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓{Colors.NC}" if result else f"{Colors.RED}✗{Colors.NC}"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print_success("All tests passed!")
    else:
        print_warning("Some tests failed. Check the output above for details.")
    
    print("\n" + "=" * 50)
    print("Next Steps")
    print("=" * 50)
    print("1. Open browser and navigate to:")
    print(f"   {auth_base}/login")
    print("2. Complete Microsoft login")
    print("3. You should be redirected to:")
    print(f"   {auth_base}/callback")
    print("4. After successful login, you'll be redirected to frontend with tokens")
    print("\nManual Test:")
    print(f"   curl -v {auth_base}/login")
    print("   # Follow redirects to complete OAuth flow")
    print()

if __name__ == "__main__":
    main()

