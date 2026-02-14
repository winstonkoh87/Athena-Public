-- ==============================================================================
-- MIGRATION 010: UPGRADE ARCHITECTURE (HNSW + JSONB)
-- ==============================================================================
-- Purpose:
-- 1. Add `metadata` JSONB column to all core tables for future-proofing schema.
-- 2. Replace `ivfflat` indexes with `hnsw` for superior vector search performance.
-- 3. Update search functions to return `metadata`.
--
-- USAGE:
-- Run this in the Supabase SQL Editor.
-- ==============================================================================
-- 1. ADD JSONB METADATA COLUMNS
-- ==============================================================================
ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE case_studies
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE protocols
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE capabilities
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE playbooks
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE "references"
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE frameworks
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE workflows
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- 2. SWITCH TO HNSW INDEXES
-- ==============================================================================
-- NOTE: We drop the old indexes first to free up resources.
-- Sessions
DROP INDEX IF EXISTS idx_sessions_embedding;
CREATE INDEX IF NOT EXISTS idx_sessions_embedding_hnsw ON sessions USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Case Studies
DROP INDEX IF EXISTS idx_case_studies_embedding;
CREATE INDEX IF NOT EXISTS idx_case_studies_embedding_hnsw ON case_studies USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Protocols
DROP INDEX IF EXISTS idx_protocols_embedding;
CREATE INDEX IF NOT EXISTS idx_protocols_embedding_hnsw ON protocols USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Capabilities
DROP INDEX IF EXISTS idx_capabilities_embedding;
CREATE INDEX IF NOT EXISTS idx_capabilities_embedding_hnsw ON capabilities USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Playbooks
DROP INDEX IF EXISTS idx_playbooks_embedding;
CREATE INDEX IF NOT EXISTS idx_playbooks_embedding_hnsw ON playbooks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- References
DROP INDEX IF EXISTS idx_references_embedding;
CREATE INDEX IF NOT EXISTS idx_references_embedding_hnsw ON "references" USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Frameworks
DROP INDEX IF EXISTS idx_frameworks_embedding;
CREATE INDEX IF NOT EXISTS idx_frameworks_embedding_hnsw ON frameworks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Workflows
DROP INDEX IF EXISTS idx_workflows_embedding;
CREATE INDEX IF NOT EXISTS idx_workflows_embedding_hnsw ON workflows USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- 3. UPDATE SEARCH FUNCTIONS
-- ==============================================================================
-- Search sessions
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        date DATE,
        title TEXT,
        summary TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT s.id,
    s.date,
    s.title,
    s.summary,
    s.metadata,
    1 - (s.embedding <=> query_embedding) AS similarity
FROM sessions s
WHERE s.embedding IS NOT NULL
    AND 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search case_studies
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        code TEXT,
        title TEXT,
        tags TEXT [],
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT cs.id,
    cs.code,
    cs.title,
    cs.tags,
    cs.metadata,
    1 - (cs.embedding <=> query_embedding) AS similarity
FROM case_studies cs
WHERE cs.embedding IS NOT NULL
    AND 1 - (cs.embedding <=> query_embedding) > match_threshold
ORDER BY cs.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search protocols
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
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.code,
    p.name,
    p.category,
    p.title,
    p.file_path,
    p.metadata,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM protocols p
WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search capabilities
CREATE OR REPLACE FUNCTION search_capabilities(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT c.id,
    c.name,
    c.title,
    c.file_path,
    c.metadata,
    1 - (c.embedding <=> query_embedding) AS similarity
FROM capabilities c
WHERE c.embedding IS NOT NULL
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search playbooks
CREATE OR REPLACE FUNCTION search_playbooks(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.name,
    p.title,
    p.file_path,
    p.metadata,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM playbooks p
WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search references
CREATE OR REPLACE FUNCTION search_references(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT r.id,
    r.name,
    r.title,
    r.file_path,
    r.metadata,
    1 - (r.embedding <=> query_embedding) AS similarity
FROM "references" r
WHERE r.embedding IS NOT NULL
    AND 1 - (r.embedding <=> query_embedding) > match_threshold
ORDER BY r.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search frameworks
CREATE OR REPLACE FUNCTION search_frameworks(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        title TEXT,
        file_path TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT f.id,
    f.name,
    f.title,
    f.file_path,
    f.metadata,
    1 - (f.embedding <=> query_embedding) AS similarity
FROM frameworks f
WHERE f.embedding IS NOT NULL
    AND 1 - (f.embedding <=> query_embedding) > match_threshold
ORDER BY f.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search workflows
CREATE OR REPLACE FUNCTION search_workflows(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        description TEXT,
        file_path TEXT,
        metadata JSONB,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT w.id,
    w.name,
    w.description,
    w.file_path,
    w.metadata,
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
-- ==============================================================================