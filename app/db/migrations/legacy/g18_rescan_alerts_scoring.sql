-- Migration: G18 - ReScan + Alerts + Enhanced Scoring
-- Date: 2025-11-14
-- Description: Adds history tables for change tracking and alerts system

-- Table: signal_change_history
-- Stores history of signal changes (SPF, DKIM, DMARC, MX)
CREATE TABLE IF NOT EXISTS signal_change_history (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,  -- 'spf', 'dkim', 'dmarc', 'mx'
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for signal_change_history
CREATE INDEX IF NOT EXISTS idx_signal_change_history_domain ON signal_change_history(domain);
CREATE INDEX IF NOT EXISTS idx_signal_change_history_signal_type ON signal_change_history(signal_type);
CREATE INDEX IF NOT EXISTS idx_signal_change_history_changed_at ON signal_change_history(changed_at);

-- Table: score_change_history
-- Stores history of score and segment changes
CREATE TABLE IF NOT EXISTS score_change_history (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    old_score INTEGER,
    new_score INTEGER,
    old_segment VARCHAR(50),
    new_segment VARCHAR(50),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for score_change_history
CREATE INDEX IF NOT EXISTS idx_score_change_history_domain ON score_change_history(domain);
CREATE INDEX IF NOT EXISTS idx_score_change_history_changed_at ON score_change_history(changed_at);

-- Table: alerts
-- Stores generated alerts for domain changes
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- 'mx_changed', 'dmarc_added', 'expire_soon', 'score_changed'
    alert_message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    notification_method VARCHAR(50),  -- 'email', 'webhook', 'slack'
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_domain ON alerts(domain);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- Table: alert_config
-- Stores alert configuration preferences
CREATE TABLE IF NOT EXISTS alert_config (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) DEFAULT 'default',  -- Session-based user identifier
    alert_type VARCHAR(50) NOT NULL,  -- 'mx_changed', 'dmarc_added', 'expire_soon', 'score_changed'
    notification_method VARCHAR(50) NOT NULL,  -- 'email', 'webhook', 'slack'
    enabled BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(50) DEFAULT 'immediate',  -- 'immediate', 'daily_digest'
    webhook_url TEXT,  -- For webhook notifications
    email_address VARCHAR(255),  -- For email notifications
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, alert_type, notification_method)
);

-- Indexes for alert_config
CREATE INDEX IF NOT EXISTS idx_alert_config_user_id ON alert_config(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_config_alert_type ON alert_config(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_config_enabled ON alert_config(enabled);

-- Add comments
COMMENT ON TABLE signal_change_history IS 'History of signal changes (SPF, DKIM, DMARC, MX) (G18)';
COMMENT ON TABLE score_change_history IS 'History of score and segment changes (G18)';
COMMENT ON TABLE alerts IS 'Generated alerts for domain changes (G18)';
COMMENT ON TABLE alert_config IS 'Alert configuration preferences (G18)';

