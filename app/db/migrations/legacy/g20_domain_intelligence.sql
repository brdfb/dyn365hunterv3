-- G20: Domain Intelligence Layer - Local Provider, Tenant Size, DMARC Coverage
-- Created: 2025-01-28
-- Phase: G20 (Domain Intelligence)

-- Add local_provider column to domain_signals
ALTER TABLE domain_signals
ADD COLUMN IF NOT EXISTS local_provider VARCHAR(255);

-- Add tenant_size column to companies
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS tenant_size VARCHAR(50);  -- 'small', 'medium', 'large', NULL

-- Add dmarc_coverage column to domain_signals
ALTER TABLE domain_signals
ADD COLUMN IF NOT EXISTS dmarc_coverage INTEGER;  -- 0-100, NULL if not set

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_domain_signals_local_provider ON domain_signals(local_provider);
CREATE INDEX IF NOT EXISTS idx_companies_tenant_size ON companies(tenant_size);
CREATE INDEX IF NOT EXISTS idx_domain_signals_dmarc_coverage ON domain_signals(dmarc_coverage);

-- Update leads_ready view to include new columns
DROP VIEW IF EXISTS leads_ready;

CREATE VIEW leads_ready AS
SELECT 
    c.id AS company_id,
    c.canonical_name,
    c.domain,
    c.provider,
    c.tenant_size,
    c.country,
    c.contact_emails,
    c.contact_quality_score,
    c.linkedin_pattern,
    c.updated_at AS company_updated_at,
    ds.id AS signal_id,
    ds.spf,
    ds.dkim,
    ds.dmarc_policy,
    ds.dmarc_coverage,
    ds.mx_root,
    ds.local_provider,
    ds.registrar,
    ds.expires_at,
    ds.nameservers,
    ds.scan_status,
    ds.scanned_at,
    ls.id AS score_id,
    ls.readiness_score,
    ls.segment,
    ls.reason,
    ls.updated_at AS score_updated_at
FROM companies c
LEFT JOIN domain_signals ds ON c.domain = ds.domain
LEFT JOIN lead_scores ls ON c.domain = ls.domain;

