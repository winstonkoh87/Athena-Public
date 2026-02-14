-- ==============================================================================
-- MIGRATION 014: AUTO-TAGGING TRIGGERS (THE "DEMONSYNTH" UPGRADE)
-- ==============================================================================
-- Purpose:
-- Automate the harvesting of metadata tags as suggested by u/DemonSynth.
-- Instead of manual tagging only, we automatically inject the record's 
-- Name and Title into the `metadata->'auto_tags'` JSONB array.
--
-- Logic:
-- 1. Create a generic Trigger Function `auto_enrich_metadata()`.
-- 2. It checks if `name` or `title` exists in the record.
-- 3. It lowercases the value and appends it to `metadata['auto_tags']`.
-- 4. It ensures `metadata` is never null.
-- ==============================================================================
-- 1. DEFINE THE TRIGGER FUNCTION
-- ==============================================================================
CREATE OR REPLACE FUNCTION auto_enrich_metadata() RETURNS TRIGGER AS $$
DECLARE entity_name TEXT;
current_meta JSONB;
auto_tags JSONB;
BEGIN -- 1. Identify the source field (Name or Title)
-- We use a "best effort" approach to find a descriptive string.
-- We cast to JSONB to safely check key existence dynamically.
IF (to_jsonb(NEW) ? 'name') THEN entity_name := NEW.name;
ELSIF (to_jsonb(NEW) ? 'title') THEN entity_name := NEW.title;
END IF;
-- 2. Initialize Metadata if null
IF NEW.metadata IS NULL THEN NEW.metadata := '{}'::jsonb;
END IF;
current_meta := NEW.metadata;
-- 3. Update 'auto_tags' if we found a name
IF entity_name IS NOT NULL THEN -- Safely retrieve existing auto_tags or create empty array
auto_tags := COALESCE(current_meta->'auto_tags', '[]'::jsonb);
-- Add the normalized name to the array (if not already present? 
-- JSONB generic '||' doesn't dedup easily without query, 
-- so we just append. Dedup happens at query time or refined logic).
-- For simplicity and speed: We create a single-item array matching the name.
-- "Tag Schema for Free": simple normalization.
-- Logic: Set 'auto_tags' to contain at least the entity name.
-- We won't accumulate history here to avoid infinite growth on updates.
-- We just ensure the CURRENT name is tagged.
NEW.metadata := current_meta || jsonb_build_object(
    'auto_tags',
    jsonb_build_array(lower(entity_name))
);
END IF;
-- 4. Timestamp sync (Bonus hygiene)
IF (to_jsonb(NEW) ? 'updated_at') THEN NEW.updated_at := NOW();
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- 2. ATTACH TRIGGERS TO TABLES
-- ==============================================================================
-- Sessions (Has 'title')
DROP TRIGGER IF EXISTS tr_sessions_auto_tag ON sessions;
CREATE TRIGGER tr_sessions_auto_tag BEFORE
INSERT
    OR
UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Case Studies (Has 'title')
DROP TRIGGER IF EXISTS tr_case_studies_auto_tag ON case_studies;
CREATE TRIGGER tr_case_studies_auto_tag BEFORE
INSERT
    OR
UPDATE ON case_studies FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Protocols (Has 'name', 'title')
DROP TRIGGER IF EXISTS tr_protocols_auto_tag ON protocols;
CREATE TRIGGER tr_protocols_auto_tag BEFORE
INSERT
    OR
UPDATE ON protocols FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Capabilities (Has 'name', 'title')
DROP TRIGGER IF EXISTS tr_capabilities_auto_tag ON capabilities;
CREATE TRIGGER tr_capabilities_auto_tag BEFORE
INSERT
    OR
UPDATE ON capabilities FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Playbooks (Has 'name', 'title')
DROP TRIGGER IF EXISTS tr_playbooks_auto_tag ON playbooks;
CREATE TRIGGER tr_playbooks_auto_tag BEFORE
INSERT
    OR
UPDATE ON playbooks FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- References (Has 'name', 'title')
DROP TRIGGER IF EXISTS tr_references_auto_tag ON "references";
CREATE TRIGGER tr_references_auto_tag BEFORE
INSERT
    OR
UPDATE ON "references" FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Frameworks (Has 'name', 'title')
DROP TRIGGER IF EXISTS tr_frameworks_auto_tag ON frameworks;
CREATE TRIGGER tr_frameworks_auto_tag BEFORE
INSERT
    OR
UPDATE ON frameworks FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- Workflows (Has 'name')
DROP TRIGGER IF EXISTS tr_workflows_auto_tag ON workflows;
CREATE TRIGGER tr_workflows_auto_tag BEFORE
INSERT
    OR
UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- ==============================================================================
-- AUTOMATION COMPLETE
-- ==============================================================================