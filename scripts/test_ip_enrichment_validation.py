"""IP Enrichment Validation Test Script

Tests IP enrichment with real-world domains across different scenarios:
1. Türkiye hosting / kurumsal
2. Global big tech (microsoft.com, google.com)
3. CDN / WAF / Cloudflare
4. Proxy / datacenter IP
5. Boş / zayıf domain

Usage:
    python scripts/test_ip_enrichment_validation.py
"""

import sys
import json
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.core.enrichment_service import latest_ip_enrichment
from app.core.analyzer_dns import resolve_domain_ip_candidates, get_mx_records
from app.core.analyzer_enrichment import enrich_ip
from app.core.logging import logger
from app.config import settings


# Test domain set (gerçek domain'ler - UI'dan alındı)
TEST_DOMAINS = [
    # 1. Türkiye hosting / Local (TR'de host edilen, Local provider)
    {"domain": "otega.com.tr", "category": "Türkiye hosting / Local", "expected": "TR country, Local provider, hosting ISP"},
    {"domain": "rollmech.com", "category": "Türkiye hosting / Local", "expected": "TR country, Local provider, hosting ISP"},
    {"domain": "tarimsalkimya.com.tr", "category": "Türkiye hosting / Local", "expected": "TR country, Local provider"},
    {"domain": "unalsan.com", "category": "Türkiye hosting / Local", "expected": "TR country, Local provider"},
    {"domain": "yurektekstil.com.tr", "category": "Türkiye hosting / Local", "expected": "TR country, Local provider"},
    
    # 2. M365 Kurumsal (M365 provider, medium/large tenant)
    {"domain": "asteknikvana.com", "category": "M365 Kurumsal", "expected": "TR/EU country, M365 provider, medium tenant"},
    {"domain": "baritmaden.com", "category": "M365 Kurumsal", "expected": "TR/EU country, M365 provider"},
    {"domain": "batmaztekstil.com.tr", "category": "M365 Kurumsal", "expected": "TR/EU country, M365 provider"},
    {"domain": "ertugmetal.com", "category": "M365 Kurumsal", "expected": "TR/EU country, M365 provider"},
    
    # 3. Global big tech (reference)
    {"domain": "microsoft.com", "category": "Global big tech", "expected": "US/EU country, M365 provider"},
    {"domain": "google.com", "category": "Global big tech", "expected": "US/EU country, Google provider"},
]


def test_domain_enrichment(domain: str, db) -> Dict[str, Any]:
    """
    Test IP enrichment for a single domain.
    
    Returns:
        Dictionary with test results
    """
    result = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "ip_resolution": {
            "success": False,
            "ips": [],
            "error": None,
        },
        "enrichment": {
            "success": False,
            "results": [],
            "errors": [],
        },
        "database": {
            "record_exists": False,
            "record": None,
        },
    }
    
    # Step 1: Get MX records and resolve domain to IP(s)
    try:
        mx_records = get_mx_records(domain)
        ips = resolve_domain_ip_candidates(domain, mx_records)
        if ips:
            result["ip_resolution"]["success"] = True
            result["ip_resolution"]["ips"] = ips
            result["ip_resolution"]["mx_records"] = mx_records
        else:
            result["ip_resolution"]["error"] = "No IPs resolved"
            result["ip_resolution"]["mx_records"] = mx_records
    except Exception as e:
        result["ip_resolution"]["error"] = str(e)
        logger.error("ip_resolution_failed", domain=domain, error=str(e))
        return result
    
    # Step 2: Enrich each IP
    for ip in ips[:3]:  # Limit to first 3 IPs
        try:
            enrichment_result = enrich_ip(ip, use_cache=True)
            if enrichment_result:
                result["enrichment"]["success"] = True
                result["enrichment"]["results"].append({
                    "ip": ip,
                    "country": enrichment_result.country,
                    "city": enrichment_result.city,
                    "asn": enrichment_result.asn,
                    "asn_org": enrichment_result.asn_org,
                    "isp": enrichment_result.isp,
                    "usage_type": enrichment_result.usage_type,
                    "is_proxy": enrichment_result.is_proxy,
                    "proxy_type": enrichment_result.proxy_type,
                })
        except Exception as e:
            result["enrichment"]["errors"].append({
                "ip": ip,
                "error": str(e),
            })
            logger.error("ip_enrichment_failed", domain=domain, ip=ip, error=str(e))
    
    # Step 3: Check database record
    try:
        db_record = latest_ip_enrichment(domain, db)
        if db_record:
            result["database"]["record_exists"] = True
            result["database"]["record"] = {
                "ip_address": db_record.ip_address,
                "country": db_record.country,
                "city": db_record.city,
                "asn": db_record.asn,
                "asn_org": db_record.asn_org,
                "isp": db_record.isp,
                "usage_type": db_record.usage_type,
                "is_proxy": db_record.is_proxy,
                "proxy_type": db_record.proxy_type,
            }
    except Exception as e:
        logger.error("db_query_failed", domain=domain, error=str(e))
    
    return result


def main():
    """Run IP enrichment validation tests."""
    print("=" * 80)
    print("IP Enrichment Validation Test")
    print("=" * 80)
    print(f"Enrichment Enabled: {settings.enrichment_enabled}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    if not settings.enrichment_enabled:
        print("⚠️  WARNING: IP Enrichment is disabled (HUNTER_ENRICHMENT_ENABLED=false)")
        print("   Enable it in .env file to run full validation tests.")
        print()
    
    db = SessionLocal()
    all_results = []
    
    try:
        for test_case in TEST_DOMAINS:
            domain = test_case["domain"]
            category = test_case["category"]
            expected = test_case["expected"]
            
            print(f"Testing: {domain} ({category})")
            print(f"  Expected: {expected}")
            
            result = test_domain_enrichment(domain, db)
            result["category"] = category
            result["expected"] = expected
            all_results.append(result)
            
            # Print summary
            if result["ip_resolution"]["success"]:
                print(f"  ✅ IP Resolution: {len(result['ip_resolution']['ips'])} IP(s) found")
                if result["ip_resolution"].get("mx_records"):
                    print(f"     MX Records: {', '.join(result['ip_resolution']['mx_records'][:3])}")
            else:
                print(f"  ❌ IP Resolution: {result['ip_resolution']['error']}")
            
            if result["enrichment"]["success"]:
                print(f"  ✅ Enrichment: {len(result['enrichment']['results'])} result(s)")
                for enrichment in result["enrichment"]["results"]:
                    country = enrichment.get('country', 'N/A')
                    city = enrichment.get('city', 'N/A')
                    isp = enrichment.get('isp', 'N/A')
                    asn_org = enrichment.get('asn_org', 'N/A')
                    print(f"     IP {enrichment['ip']}: {country} / {city}")
                    print(f"       ISP: {isp} | ASN Org: {asn_org}")
                    if enrichment.get("is_proxy"):
                        print(f"       ⚠️  Proxy: {enrichment.get('proxy_type', 'Unknown')}")
                    if enrichment.get("usage_type"):
                        print(f"       Usage Type: {enrichment.get('usage_type')}")
            else:
                print(f"  ❌ Enrichment: No results")
                if result["enrichment"].get("errors"):
                    for err in result["enrichment"]["errors"]:
                        print(f"     Error for {err['ip']}: {err['error']}")
            
            if result["database"]["record_exists"]:
                db_rec = result["database"]["record"]
                print(f"  ✅ Database: Record exists (IP: {db_rec.get('ip_address')}, Country: {db_rec.get('country')})")
            else:
                print(f"  ⚠️  Database: No record found (domain may not be scanned yet)")
            
            print()
        
        # Save results to file
        output_file = "docs/active/IP-ENRICHMENT-VALIDATION-RESULTS.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")
        print()
        print("=" * 80)
        print("Validation Complete")
        print("=" * 80)
        print(f"Total domains tested: {len(all_results)}")
        print(f"Successful IP resolutions: {sum(1 for r in all_results if r['ip_resolution']['success'])}")
        print(f"Successful enrichments: {sum(1 for r in all_results if r['enrichment']['success'])}")
        print(f"Database records: {sum(1 for r in all_results if r['database']['record_exists'])}")
        
    except Exception as e:
        logger.error("validation_test_failed", error=str(e), exc_info=True)
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

