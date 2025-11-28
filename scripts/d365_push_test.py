#!/usr/bin/env python3
"""
D365 API Push Test (E2E)

Tests real D365 API push with test lead data.
This will create/update a lead in D365.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.priority import calculate_priority_score
from app.core.enrichment_service import build_infra_summary
from app.integrations.d365.mapping import map_lead_to_d365
from app.integrations.d365.client import D365Client
from app.integrations.d365.errors import (
    D365Error,
    D365AuthenticationError,
    D365APIError,
    D365RateLimitError,
    D365DuplicateError,
)


def get_test_lead_data(db, company_id=86):
    """Get test lead data from database."""
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
        lr.priority_label
    FROM leads_ready lr
    WHERE lr.company_id = :company_id
    LIMIT 1
    """
    
    result = db.execute(text(query), {"company_id": company_id})
    row = result.fetchone()
    
    if not row:
        return None
    
    # Calculate priority score
    priority_score = calculate_priority_score(row.segment, row.readiness_score)
    
    # Build infrastructure summary
    infrastructure_summary = build_infra_summary(row.domain, db)
    
    lead_data = {
        'company_id': row.company_id,
        'canonical_name': row.canonical_name,
        'domain': row.domain,
        'provider': row.provider,
        'tenant_size': row.tenant_size,
        'country': row.country,
        'contact_emails': row.contact_emails,
        'readiness_score': row.readiness_score,
        'segment': row.segment,
        'priority_score': priority_score,
        'infrastructure_summary': infrastructure_summary,
        'technical_heat': row.technical_heat,
        'commercial_segment': row.commercial_segment,
        'commercial_heat': row.commercial_heat,
        'priority_category': row.priority_category,
        'priority_label': row.priority_label,
    }
    
    return lead_data


async def test_d365_push(lead_data):
    """Test D365 API push."""
    print("=" * 60)
    print("D365 API Push Test (E2E)")
    print("=" * 60)
    
    # Map to D365 payload
    print("\n[1] Mapping lead data to D365 payload...")
    d365_payload = map_lead_to_d365(lead_data)
    print(f"[OK] Payload prepared ({len(d365_payload)} fields)")
    
    # Initialize D365 client
    print("\n[2] Initializing D365 client...")
    try:
        client = D365Client()
        print("[OK] D365 client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize D365 client: {e}")
        return None
    
    # Test token acquisition
    print("\n[3] Acquiring access token...")
    try:
        token = client._get_access_token()
        print(f"[OK] Token acquired (length: {len(token)})")
    except D365AuthenticationError as e:
        print(f"[ERROR] Authentication failed: {e}")
        return None
    
    # Push to D365
    print("\n[4] Pushing lead to D365...")
    print(f"     Domain: {lead_data['domain']}")
    print(f"     Company: {lead_data['canonical_name']}")
    
    try:
        result = await client.create_or_update_lead(d365_payload)
        
        if result and 'leadid' in result:
            d365_lead_id = result['leadid']
            print(f"\n[OK] Lead pushed successfully!")
            print(f"     D365 Lead ID: {d365_lead_id}")
            print(f"     Subject: {d365_payload.get('subject', 'N/A')}")
            
            # Display result
            print("\n" + "=" * 60)
            print("D365 API Response")
            print("=" * 60)
            print(f"Lead ID: {d365_lead_id}")
            if 'subject' in result:
                print(f"Subject: {result.get('subject')}")
            if 'companyname' in result:
                print(f"Company Name: {result.get('companyname')}")
            
            return {
                'status': 'success',
                'd365_lead_id': d365_lead_id,
                'result': result
            }
        else:
            print("[ERROR] D365 response missing leadid")
            print(f"Response: {result}")
            return None
            
    except D365RateLimitError as e:
        print(f"[ERROR] Rate limit exceeded: {e}")
        print("     Tip: Wait a few minutes and try again")
        return None
    except D365DuplicateError as e:
        print(f"[WARN] Duplicate lead detected: {e}")
        print("     This is OK - lead already exists in D365")
        return {'status': 'duplicate', 'error': str(e)}
    except D365APIError as e:
        print(f"[ERROR] API error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test D365 API push')
    parser.add_argument('--company-id', type=int, default=86, help='Company ID to test (default: 86)')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        # Get test lead data
        print("=" * 60)
        print("D365 Push Test - Preparing Test Lead")
        print("=" * 60)
        print(f"\n[0] Loading test lead (Company ID: {args.company_id})...")
        
        lead_data = get_test_lead_data(db, args.company_id)
        
        if not lead_data:
            print(f"[ERROR] Test lead not found (Company ID: {args.company_id})")
            sys.exit(1)
        
        print(f"[OK] Test lead loaded:")
        print(f"     Domain: {lead_data['domain']}")
        print(f"     Company: {lead_data['canonical_name']}")
        print(f"     Score: {lead_data['readiness_score']}")
        print(f"     Segment: {lead_data['segment']}")
        
        # Test D365 push
        result = asyncio.run(test_d365_push(lead_data))
        
        if result:
            if result.get('status') == 'success':
                print("\n" + "=" * 60)
                print("[OK] D365 Push Test PASSED!")
                print("=" * 60)
                print(f"D365 Lead ID: {result['d365_lead_id']}")
                print("\nNext steps:")
                print("1. Check D365 form to verify fields are populated")
                print("2. Verify Hunter custom fields (hnt_*) are visible")
                print("3. Test error handling scenarios (Task 6)")
            elif result.get('status') == 'duplicate':
                print("\n" + "=" * 60)
                print("[WARN] Duplicate lead detected")
                print("=" * 60)
                print("Lead already exists in D365 (this is OK for PoC)")
                print("Try with a different company_id or delete existing lead")
            else:
                print("\n[ERROR] Push failed")
                sys.exit(1)
        else:
            print("\n[ERROR] Push test failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

