-- Dyn365Hunter MVP - Database Schema
-- Created: 2025-11-12
-- Phase: G2

-- Drop existing tables and views if they exist (for clean migration)
DROP VIEW IF EXISTS leads_ready CASCADE;
DROP TABLE IF EXISTS lead_scores CASCADE;
DROP TABLE IF EXISTS domain_signals CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS raw_leads CASCADE;

-- Table: raw_leads
-- Stores raw ingested data from CSV, domain input, or webhook
CREATE TABLE raw_leads (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'csv', 'domain', 'webhook'
    company_name VARCHAR(255),
    email VARCHAR(255),
    website VARCHAR(255),
    domain VARCHAR(255) NOT NULL,
    payload JSONB,  -- Additional metadata as JSON
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for raw_leads
CREATE INDEX idx_raw_leads_domain ON raw_leads(domain);
CREATE INDEX idx_raw_leads_source ON raw_leads(source);
CREATE INDEX idx_raw_leads_ingested_at ON raw_leads(ingested_at);

-- Table: companies
-- Stores normalized company information (domain is unique)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    canonical_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,  -- UNIQUE constraint as per requirements
    provider VARCHAR(50),  -- 'M365', 'Google', 'Yandex', 'Hosting', 'Local', 'Unknown'
    country VARCHAR(2),  -- ISO 3166-1 alpha-2 country code
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for companies
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_provider ON companies(provider);
CREATE INDEX idx_companies_updated_at ON companies(updated_at);

-- Table: domain_signals
-- Stores DNS and WHOIS analysis results for domains
CREATE TABLE domain_signals (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    spf BOOLEAN,  -- SPF record exists
    dkim BOOLEAN,  -- DKIM record exists
    dmarc_policy VARCHAR(50),  -- 'none', 'quarantine', 'reject', etc.
    mx_root VARCHAR(255),  -- Root domain of MX record (e.g., 'outlook.com' from 'outlook-com.olc.protection.outlook.com')
    registrar VARCHAR(255),
    expires_at DATE,
    nameservers TEXT[],  -- Array of nameserver hostnames
    scan_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'success', 'dns_timeout', 'whois_failed', 'invalid_domain'
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for domain_signals
CREATE INDEX idx_domain_signals_domain ON domain_signals(domain);
CREATE INDEX idx_domain_signals_scan_status ON domain_signals(scan_status);
CREATE INDEX idx_domain_signals_scanned_at ON domain_signals(scanned_at);
CREATE INDEX idx_domain_signals_mx_root ON domain_signals(mx_root);

-- Table: lead_scores
-- Stores calculated readiness scores and segments for domains
CREATE TABLE lead_scores (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    readiness_score INTEGER NOT NULL,  -- 0-100 score
    segment VARCHAR(50) NOT NULL,  -- 'Migration', 'Existing', 'Cold', 'Skip'
    reason TEXT,  -- Human-readable explanation of score/segment
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for lead_scores
CREATE INDEX idx_lead_scores_domain ON lead_scores(domain);
CREATE INDEX idx_lead_scores_segment ON lead_scores(segment);
CREATE INDEX idx_lead_scores_readiness_score ON lead_scores(readiness_score);
CREATE INDEX idx_lead_scores_updated_at ON lead_scores(updated_at);

-- View: leads_ready
-- Combined view of companies, domain_signals, and lead_scores for easy querying
CREATE VIEW leads_ready AS
SELECT 
    c.id AS company_id,
    c.canonical_name,
    c.domain,
    c.provider,
    c.country,
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

-- Comments for documentation
COMMENT ON TABLE raw_leads IS 'Raw ingested data from various sources';
COMMENT ON TABLE companies IS 'Normalized company information with unique domain constraint';
COMMENT ON TABLE domain_signals IS 'DNS and WHOIS analysis results for domains';
COMMENT ON TABLE lead_scores IS 'Calculated readiness scores and segments for domains';
COMMENT ON VIEW leads_ready IS 'Combined view for querying ready leads with all related data';

