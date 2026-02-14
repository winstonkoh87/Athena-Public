-- ==============================================================================
-- MIGRATION: 768 → 3072 DIMENSION UPGRADE
-- ==============================================================================
-- Required because text-embedding-004 (768d) was deprecated Jan 14, 2026.
-- New model: gemini-embedding-001 (3072d)
--
-- WARNING: This is a BREAKING CHANGE. All existing embeddings will be cleared.
--          You must re-sync all documents after running this migration.
--
-- USAGE:
--   1. Run this migration in Supabase SQL Editor
--   2. Run `python3 .agent/scripts/supabase_sync.py --force` to re-embed all docs
--
-- CREATED: 2026-02-08
-- ==============================================================================
-- Step 0: Drop triggers that depend on embedding columns
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON sessions;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON case_studies;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON protocols;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON capabilities;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON playbooks;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON "references";
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON frameworks;
DROP TRIGGER IF EXISTS trg_auto_index_embedding ON workflows;
-- Also drop any other triggers that might reference embedding
DROP TRIGGER IF EXISTS on_embedding_change ON sessions;
DROP TRIGGER IF EXISTS on_embedding_change ON case_studies;
DROP TRIGGER IF EXISTS on_embedding_change ON protocols;
DROP TRIGGER IF EXISTS on_embedding_change ON capabilities;
DROP TRIGGER IF EXISTS on_embedding_change ON playbooks;
DROP TRIGGER IF EXISTS on_embedding_change ON "references";
DROP TRIGGER IF EXISTS on_embedding_change ON frameworks;
DROP TRIGGER IF EXISTS on_embedding_change ON workflows;
-- Step 1: Drop existing indexes (required before column type change)
DROP INDEX IF EXISTS idx_sessions_embedding;
DROP INDEX IF EXISTS idx_case_studies_embedding;
DROP INDEX IF EXISTS idx_protocols_embedding;
DROP INDEX IF EXISTS idx_capabilities_embedding;
DROP INDEX IF EXISTS idx_playbooks_embedding;
DROP INDEX IF EXISTS idx_references_embedding;
DROP INDEX IF EXISTS idx_frameworks_embedding;
DROP INDEX IF EXISTS idx_workflows_embedding;
-- Step 2: Alter column types from vector(768) to vector(3072)
ALTER TABLE sessions
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE case_studies
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE protocols
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE capabilities
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE playbooks
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE "references"
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE frameworks
ALTER COLUMN embedding TYPE vector(3072);
ALTER TABLE workflows
ALTER COLUMN embedding TYPE vector(3072);
-- Step 3: Clear existing embeddings (incompatible dimensions)
UPDATE sessions
SET embedding = NULL;
UPDATE case_studies
SET embedding = NULL;
UPDATE protocols
SET embedding = NULL;
UPDATE capabilities
SET embedding = NULL;
UPDATE playbooks
SET embedding = NULL;
UPDATE "references"
SET embedding = NULL;
UPDATE frameworks
SET embedding = NULL;
UPDATE workflows
SET embedding = NULL;
-- Step 4: Skip index recreation
-- NOTE: pgvector IVFFlat has 2000 dimension limit, HNSW also has limits
-- For 3072 dimensions, we use sequential scan (no index)
-- This is acceptable for datasets under ~100k rows
-- Alternative: Use dimensionality reduction (PCA) or Matryoshka embeddings
-- The following indexes are COMMENTED OUT due to dimension limits:
-- CREATE INDEX idx_sessions_embedding ON sessions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_case_studies_embedding ON case_studies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_protocols_embedding ON protocols USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
-- CREATE INDEX idx_capabilities_embedding ON capabilities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_playbooks_embedding ON playbooks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_references_embedding ON "references" USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_frameworks_embedding ON frameworks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_workflows_embedding ON workflows USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Step 5: Recreate search functions with new dimension
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        date DATE,
        title TEXT,
        summary TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT s.id,
    s.date,
    s.title,
    s.summary,
    1 - (s.embedding <=> query_embedding) AS similarity
FROM sessions s
WHERE s.embedding IS NOT NULL
    AND 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        code TEXT,
        title TEXT,
        tags TEXT [],
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT cs.id,
    cs.code,
    cs.title,
    cs.tags,
    1 - (cs.embedding <=> query_embedding) AS similarity
FROM case_studies cs
WHERE cs.embedding IS NOT NULL
    AND 1 - (cs.embedding <=> query_embedding) > match_threshold
ORDER BY cs.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_protocols(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        code TEXT,
        name TEXT,
        category TEXT,
        title TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.code,
    p.name,
    p.category,
    p.title,
    p.file_path,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM protocols p
WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_capabilities(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT c.id,
    c.name,
    c.title,
    c.file_path,
    1 - (c.embedding <=> query_embedding) AS similarity
FROM capabilities c
WHERE c.embedding IS NOT NULL
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_playbooks(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.name,
    p.title,
    p.file_path,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM playbooks p
WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_references(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT r.id,
    r.name,
    r.title,
    r.file_path,
    1 - (r.embedding <=> query_embedding) AS similarity
FROM "references" r
WHERE r.embedding IS NOT NULL
    AND 1 - (r.embedding <=> query_embedding) > match_threshold
ORDER BY r.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_frameworks(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT f.id,
    f.name,
    f.title,
    f.file_path,
    1 - (f.embedding <=> query_embedding) AS similarity
FROM frameworks f
WHERE f.embedding IS NOT NULL
    AND 1 - (f.embedding <=> query_embedding) > match_threshold
ORDER BY f.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
CREATE OR REPLACE FUNCTION search_workflows(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        description TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT w.id,
    w.name,
    w.description,
    w.file_path,
    1 - (w.embedding <=> query_embedding) AS similarity
FROM workflows w
WHERE w.embedding IS NOT NULL
    AND 1 - (w.embedding <=> query_embedding) > match_threshold
ORDER BY w.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- ==============================================================================
-- MIGRATION COMPLETE
-- Next step: Run `python3 .agent/scripts/supabase_sync.py --force` to re-embed
-- ==============================================================================