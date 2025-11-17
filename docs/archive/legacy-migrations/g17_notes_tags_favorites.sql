-- Migration: G17 - Notes, Tags, and Favorites
-- Date: 2025-11-14
-- Description: Adds CRM-lite features: notes, tags (with auto-tagging), and favorites

-- Table: notes
-- Stores user notes for domains
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE
);

-- Indexes for notes
CREATE INDEX IF NOT EXISTS idx_notes_domain ON notes(domain);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);

-- Table: tags
-- Stores tags for domains (many-to-many relationship)
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE,
    UNIQUE(domain, tag)  -- One tag per domain (no duplicates)
);

-- Indexes for tags
CREATE INDEX IF NOT EXISTS idx_tags_domain ON tags(domain);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_tags_domain_tag ON tags(domain, tag);

-- Table: favorites
-- Stores user favorites for domains (session-based, no auth yet)
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,  -- Session-based user identifier
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain) REFERENCES companies(domain) ON DELETE CASCADE,
    UNIQUE(domain, user_id)  -- One favorite per domain per user
);

-- Indexes for favorites
CREATE INDEX IF NOT EXISTS idx_favorites_domain ON favorites(domain);
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_domain_user_id ON favorites(domain, user_id);

-- Add comments
COMMENT ON TABLE notes IS 'User notes for domains (G17: CRM-lite)';
COMMENT ON TABLE tags IS 'Tags for domains with auto-tagging support (G17: CRM-lite)';
COMMENT ON TABLE favorites IS 'User favorites for domains, session-based (G17: CRM-lite)';

