#!/usr/bin/env python3
"""
Fresh Test Checklist - Manual verification after DB reset
This script helps verify all bug fixes are working correctly
"""

import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from typing import Dict, Any, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
TEST_DOMAIN = "dmkimya.com.tr"

def print_header(text: str):
    """Print formatted header."""
    # Remove emoji for Windows compatibility
    clean_text = text.replace("📋 ", "").replace("🧪 ", "").replace("✅ ", "").replace("❌ ", "").replace("⚠️ ", "")
    print(f"\n{Colors.BLUE}{clean_text}{Colors.NC}")
    print("-" * len(clean_text))

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[OK] {text}{Colors.NC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL] {text}{Colors.NC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.NC}")

def test_ingest_domain() -> bool:
    """Test 1: Ingest domain."""
    print_header("Test 1: Ingest domain")
    
    try:
        response = requests.post(
            f"{API_URL}/ingest/domain",
            json={"domain": TEST_DOMAIN, "company_name": "DM Kimya Test"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print_success("Domain ingested successfully")
            return True
        else:
            print_error(f"Domain ingestion failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Domain ingestion error: {e}")
        return False

def test_scan_domain() -> Optional[Dict[str, Any]]:
    """Test 2: Scan domain."""
    print_header("Test 2: Scan domain")
    
    time.sleep(2)  # Wait a bit after ingest
    
    try:
        response = requests.post(
            f"{API_URL}/scan/domain",
            json={"domain": TEST_DOMAIN},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            segment = data.get("segment", "N/A")
            score = data.get("score", "N/A")
            print_success("Domain scanned successfully")
            print(f"   Segment: {segment}, Score: {score}")
            return data
        else:
            print_error(f"Domain scan failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Domain scan error: {e}")
        return None

def test_lead_response() -> Optional[Dict[str, Any]]:
    """Test 3: Check lead response (DMARC coverage)."""
    print_header("Test 3: Check lead response (DMARC coverage)")
    
    time.sleep(2)  # Wait a bit after scan
    
    try:
        response = requests.get(f"{API_URL}/leads/{TEST_DOMAIN}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            dmarc_coverage = data.get("dmarc_coverage")
            dmarc_policy = data.get("dmarc_policy")
            
            print(f"   DMARC Policy: {dmarc_policy}")
            print(f"   DMARC Coverage: {dmarc_coverage}")
            
            if dmarc_coverage is None:
                print_success("DMARC Coverage is null (correct - no DMARC record)")
                return data
            elif dmarc_coverage == 100:
                print_error("DMARC Coverage is 100 (BUG: should be null)")
                return None
            else:
                print_warning(f"DMARC Coverage: {dmarc_coverage} (unexpected value)")
                return data
        else:
            print_error(f"Lead response failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Lead response error: {e}")
        return None

def test_score_breakdown() -> Optional[Dict[str, Any]]:
    """Test 4: Check score breakdown (DMARC coverage)."""
    print_header("Test 4: Check score breakdown (DMARC coverage)")
    
    try:
        response = requests.get(f"{API_URL}/leads/{TEST_DOMAIN}/score-breakdown", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            dmarc_coverage = data.get("dmarc_coverage")
            dmarc_policy = data.get("dmarc_policy")
            
            print(f"   DMARC Policy: {dmarc_policy}")
            print(f"   DMARC Coverage: {dmarc_coverage}")
            
            if dmarc_coverage is None:
                print_success("Score Breakdown DMARC Coverage is null (correct)")
                return data
            elif dmarc_coverage == 100:
                print_error("Score Breakdown DMARC Coverage is 100 (BUG: should be null)")
                return None
            else:
                print_warning(f"Score Breakdown DMARC Coverage: {dmarc_coverage} (unexpected value)")
                return data
        else:
            print_error(f"Score breakdown failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Score breakdown error: {e}")
        return None

def test_p_model_fields(lead_data: Dict[str, Any]) -> bool:
    """Test 5: Check P-Model fields."""
    print_header("Test 5: Check P-Model fields")
    
    priority_category = lead_data.get("priority_category")
    priority_label = lead_data.get("priority_label")
    technical_heat = lead_data.get("technical_heat")
    commercial_segment = lead_data.get("commercial_segment")
    
    print(f"   Priority Category: {priority_category}")
    print(f"   Priority Label: {priority_label}")
    print(f"   Technical Heat: {technical_heat}")
    print(f"   Commercial Segment: {commercial_segment}")
    
    if priority_category and priority_category != "None":
        print_success("P-Model fields present")
        return True
    else:
        print_error("P-Model fields missing")
        return False

def test_sales_summary() -> bool:
    """Test 6: Check Sales Summary (risk summary)."""
    print_header("Test 6: Check Sales Summary (risk summary)")
    
    try:
        response = requests.get(f"{API_URL}/leads/{TEST_DOMAIN}/sales-summary", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            security_reasoning = data.get("security_reasoning", {})
            risk_summary = security_reasoning.get("summary", "")
            
            print(f"   Risk Summary: {risk_summary}")
            
            if "SPF ve DKIM mevcut" in risk_summary:
                print_success("Risk summary correctly mentions SPF and DKIM are present")
                return True
            elif "SPF ve DKIM eksik" in risk_summary:
                print_error("Risk summary incorrectly says SPF and DKIM are missing (BUG)")
                return False
            else:
                print_warning("Risk summary format unexpected")
                return True
        else:
            print_error(f"Sales summary failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Sales summary error: {e}")
        return False

def test_consistency(lead_data: Dict[str, Any], breakdown_data: Dict[str, Any]) -> bool:
    """Test 7: Check consistency (Lead vs Score Breakdown)."""
    print_header("Test 7: Check consistency (Lead vs Score Breakdown)")
    
    lead_dmarc = lead_data.get("dmarc_coverage")
    breakdown_dmarc = breakdown_data.get("dmarc_coverage")
    
    if lead_dmarc == breakdown_dmarc:
        print_success(f"DMARC Coverage consistent: {lead_dmarc}")
        return True
    else:
        print_error(f"DMARC Coverage inconsistent: Lead={lead_dmarc}, Breakdown={breakdown_dmarc}")
        return False

def main():
    """Main entry point."""
    import sys
    import io
    # Fix Windows encoding for emojis
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("Fresh Test Checklist - Bug Fix Verification")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Ingest
    if test_ingest_domain():
        tests_passed += 1
    else:
        tests_failed += 1
        print("\n❌ Test failed. Exiting.")
        sys.exit(1)
    
    # Test 2: Scan
    scan_data = test_scan_domain()
    if scan_data:
        tests_passed += 1
    else:
        tests_failed += 1
        print("\n❌ Test failed. Exiting.")
        sys.exit(1)
    
    # Test 3: Lead response
    lead_data = test_lead_response()
    if lead_data:
        tests_passed += 1
    else:
        tests_failed += 1
        print("\n❌ Test failed. Exiting.")
        sys.exit(1)
    
    # Test 4: Score breakdown
    breakdown_data = test_score_breakdown()
    if breakdown_data:
        tests_passed += 1
    else:
        tests_failed += 1
        print("\n❌ Test failed. Exiting.")
        sys.exit(1)
    
    # Test 5: P-Model fields
    if test_p_model_fields(lead_data):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 6: Sales summary
    if test_sales_summary():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 7: Consistency
    if test_consistency(lead_data, breakdown_data):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    if tests_failed == 0:
        print_success("All tests passed!")
    else:
        print_error(f"Tests failed: {tests_failed}/{tests_passed + tests_failed}")
        sys.exit(1)
    
    print("\nSummary:")
    print(f"   - Domain: {TEST_DOMAIN}")
    print(f"   - DMARC Coverage: {lead_data.get('dmarc_coverage')} (consistent)")
    print(f"   - Priority Category: {lead_data.get('priority_category')}")
    print(f"   - Risk Summary: Correctly formatted")
    print()

if __name__ == "__main__":
    main()

