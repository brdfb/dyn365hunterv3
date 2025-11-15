-- Migration: G19 - Favorites Migration (Session-based → User-based)
-- Date: 2025-01-28
-- Description: Migrates favorites table from session-based (user_id VARCHAR) to user-based (user_id INTEGER)

-- Step 1: Add new user_id column (INTEGER, nullable for migration)
ALTER TABLE favorites
ADD COLUMN IF NOT EXISTS user_id_new INTEGER;

-- Step 2: Create index for new column
CREATE INDEX IF NOT EXISTS idx_favorites_user_id_new ON favorites(user_id_new);

-- Step 3: Add foreign key constraint (deferred, will be enabled after migration)
-- Note: Foreign key will be added after data migration is complete
-- ALTER TABLE favorites ADD CONSTRAINT fk_favorites_user_id_new 
--     FOREIGN KEY (user_id_new) REFERENCES users(id) ON DELETE CASCADE;

-- Step 4: Drop old unique constraint (domain, user_id) - user_id is VARCHAR
-- We'll recreate it with new user_id_new column after migration
ALTER TABLE favorites
DROP CONSTRAINT IF EXISTS favorites_domain_user_id_key;

-- Step 5: Migration will be done in application code (first login)
-- This SQL migration only prepares the schema

-- Note: After application code migration is complete:
-- 1. Drop old user_id column: ALTER TABLE favorites DROP COLUMN user_id;
-- 2. Rename user_id_new to user_id: ALTER TABLE favorites RENAME COLUMN user_id_new TO user_id;
-- 3. Add foreign key: ALTER TABLE favorites ADD CONSTRAINT fk_favorites_user_id 
--        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
-- 4. Add unique constraint: ALTER TABLE favorites ADD CONSTRAINT favorites_domain_user_id_key 
--        UNIQUE (domain, user_id);
-- 5. Recreate index: CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);

