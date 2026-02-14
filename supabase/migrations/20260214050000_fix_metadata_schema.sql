-- Migration: fix_metadata_schema
-- Description: Adds missing 'metadata' JSONB column to all vector tables to match MASTER_SCHEMA.sql
-- Reason: Fixes "column does not exist" errors in search RPCs.
-- 1. Protocols
ALTER TABLE protocols
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 2. Sessions
ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 3. Case Studies
ALTER TABLE case_studies
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 4. Capabilities
ALTER TABLE capabilities
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 5. Playbooks
ALTER TABLE playbooks
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 6. References
ALTER TABLE "references"
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 7. Frameworks
ALTER TABLE frameworks
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 8. Workflows
ALTER TABLE workflows
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 9. Entities (GraphRAG support)
ALTER TABLE entities
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 10. User Profile
ALTER TABLE user_profile
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 11. System Docs
ALTER TABLE system_docs
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 12. Insights
ALTER TABLE insights
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- Re-apply Trigger Functions (ensure they exist and are up to date)
CREATE OR REPLACE FUNCTION auto_enrich_metadata() RETURNS TRIGGER AS $$
DECLARE entity_name TEXT;
current_meta JSONB;
BEGIN -- Identify source field (Name or Title)
IF (to_jsonb(NEW) ? 'name') THEN entity_name := NEW.name;
ELSIF (to_jsonb(NEW) ? 'title') THEN entity_name := NEW.title;
END IF;
-- Initialize Metadata
IF NEW.metadata IS NULL THEN NEW.metadata := '{}'::jsonb;
END IF;
current_meta := NEW.metadata;
-- Update 'auto_tags'
IF entity_name IS NOT NULL THEN NEW.metadata := current_meta || jsonb_build_object(
    'auto_tags',
    jsonb_build_array(lower(entity_name))
);
END IF;
-- Timestamp sync
IF (to_jsonb(NEW) ? 'updated_at') THEN NEW.updated_at := NOW();
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- Ensure triggers are attached (Idempotent)
DROP TRIGGER IF EXISTS tr_protocols_auto_tag ON protocols;
CREATE TRIGGER tr_protocols_auto_tag BEFORE
INSERT
    OR
UPDATE ON protocols FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_sessions_auto_tag ON sessions;
CREATE TRIGGER tr_sessions_auto_tag BEFORE
INSERT
    OR
UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- (Repeat for others if needed, but usually once function is there it works if triggers exist)