-- Migration: G16 - Webhook + Lead Enrichment
-- Date: 2025-11-14
-- Description: Adds API key authentication, webhook retry tables, and lead enrichment fields

-- Add enrichment fields to companies table
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS contact_emails JSONB,
ADD COLUMN IF NOT EXISTS contact_quality_score INTEGER,
ADD COLUMN IF NOT EXISTS linkedin_pattern VARCHAR(255);

-- Create index for contact_quality_score
CREATE INDEX IF NOT EXISTS idx_companies_contact_quality_score ON companies(contact_quality_score);

-- Create api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    rate_limit_per_minute INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255)
);

-- Create indexes for api_keys
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_api_keys_last_used_at ON api_keys(last_used_at);

-- Create webhook_retries table
CREATE TABLE IF NOT EXISTS webhook_retries (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id) ON DELETE SET NULL,
    payload JSONB NOT NULL,
    domain VARCHAR(255),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_retry_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for webhook_retries
CREATE INDEX IF NOT EXISTS idx_webhook_retries_status ON webhook_retries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_retries_next_retry_at ON webhook_retries(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_webhook_retries_domain ON webhook_retries(domain);
CREATE INDEX IF NOT EXISTS idx_webhook_retries_api_key_id ON webhook_retries(api_key_id);

-- Update leads_ready view to include enrichment fields
DROP VIEW IF EXISTS leads_ready CASCADE;
CREATE VIEW leads_ready AS
SELECT 
    c.id AS company_id,
    c.canonical_name,
    c.domain,
    c.provider,
    c.country,
    c.contact_emails,
    c.contact_quality_score,
    c.linkedin_pattern,
    c.updated_at AS company_updated_at,
    ds.id AS signal_id,
    ds.spf,
    ds.dkim,
    ds.dmarc_policy,
    ds.mx_root,
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

-- Add comments
COMMENT ON TABLE api_keys IS 'API keys for webhook authentication (G16)';
COMMENT ON TABLE webhook_retries IS 'Failed webhook requests for retry with exponential backoff (G16)';
COMMENT ON COLUMN companies.contact_emails IS 'Array of contact email addresses (G16: Lead enrichment)';
COMMENT ON COLUMN companies.contact_quality_score IS 'Quality score 0-100 (G16: Lead enrichment)';
COMMENT ON COLUMN companies.linkedin_pattern IS 'Detected LinkedIn email pattern (G16: Lead enrichment)';

