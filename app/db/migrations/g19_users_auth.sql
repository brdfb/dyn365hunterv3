-- Migration: G19 - Users & Authentication
-- Date: 2025-01-28
-- Description: Adds users table for Microsoft SSO authentication

-- Table: users
-- Stores user information from Microsoft SSO
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    microsoft_id VARCHAR(255) UNIQUE NOT NULL,  -- Azure AD object ID
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    refresh_token_encrypted TEXT,  -- Encrypted refresh token (optional, for future use)
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_microsoft_id ON users(microsoft_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_last_login_at ON users(last_login_at);

-- Note: Favorites migration (session-based → user-based) will be handled
-- in application code on first login, not in this migration.

