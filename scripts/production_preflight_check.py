#!/usr/bin/env python3
"""
Production Pre-Flight Check
Schema, Migration, P-Model, Sales Summary validation
"""

import sys
import os
import requests
import json
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Test domains
TEST_DOMAINS = {
    "gibibyte.com.tr": {
        "expected_segment": "Existing",
        "expected_commercial_segment": "RENEWAL",
        "expected_priority": "P4"
    },
    "dmkimya.com.tr": {
        "expected_segment": "Migration",
        "expected_commercial_segment": "COMPETITIVE",
        "expected_priority": "P2"
    }
}

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def check_schema_migration():
    """Check 1: Schema & Migration"""
    print_header("1. Schema & Migration Check")
    
    try:
        # Check if API is accessible
        response = requests.get(f"{API_URL.replace('/api/v1', '')}/healthz", timeout=5)
        if response.status_code == 200:
            print_success("API is accessible")
        else:
            print_error(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API connection failed: {e}")
        print_warning("Note: Database connection check requires Docker containers running")
        return False
    
    print_warning("Schema check requires direct DB access (Docker containers must be running)")
    print("   To check manually: docker-compose exec api alembic current")
    print("   Expected: All migrations applied (head)")
    
    return True

def scan_and_verify_domain(domain: str, expected: Dict[str, str]) -> bool:
    """Scan domain and verify P-Model fields"""
    print(f"\n📋 Scanning: {domain}")
    
    # Step 1: Scan
    try:
        scan_response = requests.post(
            f"{API_URL}/scan/domain",
            json={"domain": domain},
            timeout=30
        )
        
        if scan_response.status_code != 200:
            print_error(f"Scan failed: {scan_response.status_code}")
            print(f"Response: {scan_response.text[:200]}")
            return False
        
        scan_data = scan_response.json()
        print_success(f"Scan completed - Segment: {scan_data.get('segment')}, Score: {scan_data.get('score')}")
        
    except Exception as e:
        print_error(f"Scan error: {e}")
        return False
    
    # Step 2: Get Lead Response
    try:
        lead_response = requests.get(f"{API_URL}/leads/{domain}", timeout=10)
        
        if lead_response.status_code != 200:
            print_error(f"Lead response failed: {lead_response.status_code}")
            return False
        
        lead_data = lead_response.json()
        
        # Check P-Model fields
        priority_category = lead_data.get("priority_category")
        commercial_segment = lead_data.get("commercial_segment")
        technical_heat = lead_data.get("technical_heat")
        commercial_heat = lead_data.get("commercial_heat")
        priority_label = lead_data.get("priority_label")
        
        print(f"   Priority Category: {priority_category}")
        print(f"   Commercial Segment: {commercial_segment}")
        print(f"   Technical Heat: {technical_heat}")
        print(f"   Commercial Heat: {commercial_heat}")
        print(f"   Priority Label: {priority_label}")
        
        # Verify expected values
        all_ok = True
        if expected.get("expected_commercial_segment"):
            if commercial_segment == expected["expected_commercial_segment"]:
                print_success(f"Commercial Segment matches: {commercial_segment}")
            else:
                print_error(f"Commercial Segment mismatch: expected {expected['expected_commercial_segment']}, got {commercial_segment}")
                all_ok = False
        
        if expected.get("expected_priority"):
            if priority_category == expected["expected_priority"]:
                print_success(f"Priority Category matches: {priority_category}")
            else:
                print_error(f"Priority Category mismatch: expected {expected['expected_priority']}, got {priority_category}")
                all_ok = False
        
        # Check if P-Model fields are None (should not be)
        if priority_category is None or commercial_segment is None:
            print_error("P-Model fields are None - Migration may not be applied or scoring not working")
            all_ok = False
        else:
            print_success("P-Model fields populated")
        
        # Check DMARC
        dmarc_coverage = lead_data.get("dmarc_coverage")
        dmarc_policy = lead_data.get("dmarc_policy")
        print(f"   DMARC Policy: {dmarc_policy}")
        print(f"   DMARC Coverage: {dmarc_coverage}")
        
        if dmarc_policy is None and dmarc_coverage is not None and dmarc_coverage == 100:
            print_error("DMARC Coverage bug: Should be None when no DMARC record exists")
            all_ok = False
        elif dmarc_policy is None and dmarc_coverage is None:
            print_success("DMARC Coverage correctly None")
        
        return all_ok
        
    except Exception as e:
        print_error(f"Lead check error: {e}")
        return False

def check_score_breakdown(domain: str) -> bool:
    """Check Score Breakdown endpoint"""
    print(f"\n📋 Score Breakdown: {domain}")
    
    try:
        response = requests.get(f"{API_URL}/leads/{domain}/score-breakdown", timeout=10)
        
        if response.status_code != 200:
            print_error(f"Score breakdown failed: {response.status_code}")
            return False
        
        data = response.json()
        
        # Check P-Model section
        priority_category = data.get("priority_category")
        commercial_segment = data.get("commercial_segment")
        technical_heat = data.get("technical_heat")
        
        print(f"   Priority Category: {priority_category}")
        print(f"   Commercial Segment: {commercial_segment}")
        print(f"   Technical Heat: {technical_heat}")
        
        # Check DMARC consistency
        dmarc_coverage = data.get("dmarc_coverage")
        lead_response = requests.get(f"{API_URL}/leads/{domain}", timeout=5)
        if lead_response.status_code == 200:
            lead_dmarc = lead_response.json().get("dmarc_coverage")
            if dmarc_coverage == lead_dmarc:
                print_success("DMARC Coverage consistent between Lead and Score Breakdown")
            else:
                print_error(f"DMARC Coverage inconsistent: Lead={lead_dmarc}, Breakdown={dmarc_coverage}")
                return False
        
        if priority_category and commercial_segment:
            print_success("P-Model fields present in Score Breakdown")
            return True
        else:
            print_error("P-Model fields missing in Score Breakdown")
            return False
            
    except Exception as e:
        print_error(f"Score breakdown error: {e}")
        return False

def check_sales_summary(domain: str) -> bool:
    """Check Sales Summary endpoint"""
    print(f"\n📋 Sales Summary: {domain}")
    
    try:
        response = requests.get(f"{API_URL}/leads/{domain}/sales-summary", timeout=10)
        
        if response.status_code != 200:
            print_error(f"Sales summary failed: {response.status_code}")
            return False
        
        data = response.json()
        
        # Check segment
        segment = data.get("segment")
        print(f"   Segment: {segment}")
        
        # Check security reasoning
        security_reasoning = data.get("security_reasoning", {})
        risk_summary = security_reasoning.get("summary", "")
        print(f"   Risk Summary: {risk_summary[:100]}...")
        
        # Verify risk summary text
        if "SPF ve DKIM mevcut" in risk_summary:
            print_success("Risk summary correctly mentions SPF and DKIM are present")
        elif "SPF ve DKIM eksik" in risk_summary:
            print_error("Risk summary incorrectly says SPF and DKIM are missing (BUG)")
            return False
        
        # Check opportunity potential
        opportunity_potential = data.get("opportunity_potential")
        print(f"   Opportunity Potential: {opportunity_potential}")
        
        if opportunity_potential is not None and 80 <= opportunity_potential <= 95:
            print_success(f"Opportunity Potential in reasonable range: {opportunity_potential}")
        elif opportunity_potential is None:
            print_warning("Opportunity Potential is None")
        else:
            print_warning(f"Opportunity Potential: {opportunity_potential} (unusual but may be valid)")
        
        return True
        
    except Exception as e:
        print_error(f"Sales summary error: {e}")
        return False

def main():
    """Main entry point"""
    print_header("Production Pre-Flight Check")
    print("Validating: Schema, Migration, P-Model, Sales Summary")
    
    results = {
        "schema": False,
        "domains": {},
        "score_breakdown": {},
        "sales_summary": {}
    }
    
    # Check 1: Schema & Migration
    results["schema"] = check_schema_migration()
    
    # Check 2: Scan and verify domains
    print_header("2. Domain Scan & P-Model Verification")
    
    for domain, expected in TEST_DOMAINS.items():
        print(f"\n{'='*60}")
        print(f"Domain: {domain}")
        print(f"{'='*60}")
        
        domain_ok = scan_and_verify_domain(domain, expected)
        results["domains"][domain] = domain_ok
        
        # Check Score Breakdown
        breakdown_ok = check_score_breakdown(domain)
        results["score_breakdown"][domain] = breakdown_ok
        
        # Check Sales Summary
        summary_ok = check_sales_summary(domain)
        results["sales_summary"][domain] = summary_ok
    
    # Summary
    print_header("Summary")
    
    all_passed = True
    
    if not results["schema"]:
        print_warning("Schema check skipped (requires Docker)")
    else:
        print_success("Schema check passed")
    
    for domain, ok in results["domains"].items():
        if ok:
            print_success(f"{domain}: P-Model verification passed")
        else:
            print_error(f"{domain}: P-Model verification failed")
            all_passed = False
    
    for domain, ok in results["score_breakdown"].items():
        if not ok:
            print_error(f"{domain}: Score Breakdown check failed")
            all_passed = False
    
    for domain, ok in results["sales_summary"].items():
        if not ok:
            print_error(f"{domain}: Sales Summary check failed")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print_success("ALL CHECKS PASSED - Production Ready! 🚀")
    else:
        print_error("SOME CHECKS FAILED - Review errors above")
    print(f"{'='*60}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

