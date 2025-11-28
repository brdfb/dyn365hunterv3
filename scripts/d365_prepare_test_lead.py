#!/usr/bin/env python3
"""
D365 Test Lead Data Preparation

Selects a test lead from leads_ready view and validates required fields.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.priority import calculate_priority_score
from app.core.enrichment_service import build_infra_summary
import json


def find_test_lead(db):
    """Find a suitable test lead from leads_ready view."""
    query = """
    SELECT 
        lr.company_id,
        lr.canonical_name,
        lr.domain,
        lr.provider,
        lr.tenant_size,
        lr.country,
        lr.contact_emails,
        lr.readiness_score,
        lr.segment,
        lr.technical_heat,
        lr.commercial_segment,
        lr.commercial_heat,
        lr.priority_category,
        lr.priority_label,
        c.d365_lead_id,
        c.d365_sync_status,
        c.d365_sync_last_at,
        c.d365_sync_error,
        c.d365_sync_attempt_count,
        pcr.referral_id,
        pcr.azure_tenant_id,
        pcr.referral_type
    FROM leads_ready lr
    LEFT JOIN companies c ON lr.company_id = c.id
    LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
    WHERE lr.readiness_score IS NOT NULL
      AND lr.segment IS NOT NULL
      AND lr.domain IS NOT NULL
      AND lr.canonical_name IS NOT NULL
    ORDER BY lr.readiness_score DESC
    LIMIT 5
    """
    
    result = db.execute(text(query))
    rows = result.fetchall()
    
    if not rows:
        return None
    
    # Return first suitable lead
    return rows[0]


def validate_lead_data(row):
    """Validate that lead data has all required fields."""
    required_fields = {
        'company_id': row.company_id,
        'domain': row.domain,
        'canonical_name': row.canonical_name,
        'readiness_score': row.readiness_score,
        'segment': row.segment,
    }
    
    optional_fields = {
        'provider': row.provider,
        'tenant_size': row.tenant_size,
        'country': row.country,
        'contact_emails': row.contact_emails,
        'technical_heat': row.technical_heat,
        'commercial_segment': row.commercial_segment,
        'commercial_heat': row.commercial_heat,
        'priority_category': row.priority_category,
        'priority_label': row.priority_label,
        'referral_id': row.referral_id,
        'azure_tenant_id': row.azure_tenant_id,
        'referral_type': row.referral_type,
    }
    
    # Check required fields
    missing_required = [k for k, v in required_fields.items() if v is None]
    if missing_required:
        return False, f"Missing required fields: {missing_required}"
    
    return True, None


def prepare_lead_data(row, db):
    """Prepare lead data dictionary for mapping."""
    # Calculate priority score
    priority_score = calculate_priority_score(row.segment, row.readiness_score)
    
    # Build infrastructure summary
    infrastructure_summary = build_infra_summary(row.domain, db)
    
    lead_data = {
        "company_id": row.company_id,
        "canonical_name": row.canonical_name,
        "domain": row.domain,
        "provider": row.provider,
        "tenant_size": row.tenant_size,
        "country": row.country,
        "contact_emails": row.contact_emails,
        "readiness_score": row.readiness_score,
        "segment": row.segment,
        "priority_score": priority_score,
        "infrastructure_summary": infrastructure_summary,
        "technical_heat": row.technical_heat,
        "commercial_segment": row.commercial_segment,
        "commercial_heat": row.commercial_heat,
        "priority_category": row.priority_category,
        "priority_label": row.priority_label,
        "d365_sync_last_at": row.d365_sync_last_at,
        "d365_sync_error": row.d365_sync_error,
        "d365_sync_attempt_count": row.d365_sync_attempt_count,
        "d365_sync_status": row.d365_sync_status,
        "referral_id": row.referral_id,
        "azure_tenant_id": row.azure_tenant_id,
        "referral_type": row.referral_type,
    }
    
    return lead_data


def main():
    """Main function."""
    print("=" * 60)
    print("D365 Test Lead Data Preparation")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Find test lead
        print("\n[1] Searching for test lead in leads_ready view...")
        row = find_test_lead(db)
        
        if not row:
            print("[ERROR] No suitable test lead found in database")
            print("        Requirements:")
            print("        - readiness_score IS NOT NULL")
            print("        - segment IS NOT NULL")
            print("        - domain IS NOT NULL")
            print("        - canonical_name IS NOT NULL")
            sys.exit(1)
        
        print(f"[OK] Found test lead:")
        print(f"     Company ID: {row.company_id}")
        print(f"     Domain: {row.domain}")
        print(f"     Company Name: {row.canonical_name}")
        print(f"     Readiness Score: {row.readiness_score}")
        print(f"     Segment: {row.segment}")
        
        # Validate lead data
        print("\n[2] Validating lead data...")
        is_valid, error = validate_lead_data(row)
        
        if not is_valid:
            print(f"[ERROR] Validation failed: {error}")
            sys.exit(1)
        
        print("[OK] All required fields present")
        
        # Prepare lead data
        print("\n[3] Preparing lead data for mapping...")
        lead_data = prepare_lead_data(row, db)
        
        # Display prepared data
        print("\n[OK] Lead data prepared successfully!")
        print("\n" + "=" * 60)
        print("Prepared Lead Data Summary")
        print("=" * 60)
        print(f"Company ID: {lead_data['company_id']}")
        print(f"Domain: {lead_data['domain']}")
        print(f"Company Name: {lead_data['canonical_name']}")
        print(f"Provider: {lead_data.get('provider', 'N/A')}")
        print(f"Tenant Size: {lead_data.get('tenant_size', 'N/A')}")
        print(f"Readiness Score: {lead_data['readiness_score']}")
        print(f"Segment: {lead_data['segment']}")
        print(f"Priority Score: {lead_data['priority_score']}")
        print(f"Infrastructure Summary: {lead_data.get('infrastructure_summary', 'N/A')[:100]}...")
        print(f"Contact Emails: {len(lead_data.get('contact_emails', [])) if isinstance(lead_data.get('contact_emails'), list) else 'N/A'}")
        print(f"D365 Sync Status: {lead_data.get('d365_sync_status', 'N/A')}")
        print(f"Referral ID: {lead_data.get('referral_id', 'N/A')}")
        
        # Save to file for next step
        output_file = Path("test_lead_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert non-serializable types
            serializable_data = {}
            for k, v in lead_data.items():
                if v is None:
                    serializable_data[k] = None
                elif isinstance(v, (str, int, float, bool)):
                    serializable_data[k] = v
                elif isinstance(v, list):
                    serializable_data[k] = v
                elif hasattr(v, 'isoformat'):  # datetime
                    serializable_data[k] = v.isoformat()
                else:
                    serializable_data[k] = str(v)
            
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Lead data saved to: {output_file}")
        print("\n" + "=" * 60)
        print("Next Steps")
        print("=" * 60)
        print("1. Test mapping function:")
        print("   python -c \"from app.integrations.d365.mapping import map_lead_to_d365; import json; data = json.load(open('test_lead_data.json')); print(map_lead_to_d365(data))\"")
        print("\n2. Test D365 API push (Task 5)")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

