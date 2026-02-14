-- ==============================================================================
-- ATHENA v8.1 MASTER SCHEMA (CONSOLIDATED)
-- ==============================================================================
-- Single source of truth for all Supabase tables, search functions, and triggers.
--
-- STATUS: PRODUCTION (2026-02-12)
-- ARCHITECTURE:
--   - Storage: Postgres Tables + JSONB Metadata
--   - Vector:  text-embedding-3-large (3072 dims)
--   - Index:   NONE (Exact Search) - due to pgvector < 0.5.0 limit (2000 dims)
--   - Automation: Auto-Tagging Triggers (on Insert/Update)
--
-- USAGE:
--   1. Open Supabase SQL Editor
--   2. Enable pgvector: Extensions → pgvector → Enable
--   3. Paste and run this entire file
-- ==============================================================================
-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
-- ==============================================================================
-- CORE TABLES
-- ==============================================================================
-- -----------------------------------------------------------------------------
-- TABLE: sessions
-- Stores session logs with embeddings
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    session_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    embedding vector(3072),
    file_path TEXT UNIQUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Note: Index intentionally omitted for <100k rows (Exact Search preferred over broken Index)
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date DESC);
-- -----------------------------------------------------------------------------
-- TABLE: case_studies
-- Stores case studies with embeddings
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_case_studies_code ON case_studies(code);
-- -----------------------------------------------------------------------------
-- TABLE: protocols
-- Stores reusable thinking patterns
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_protocols_code ON protocols(code);
CREATE INDEX IF NOT EXISTS idx_protocols_category ON protocols(category);
-- -----------------------------------------------------------------------------
-- TABLE: capabilities
-- Stores tool/capability definitions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- -----------------------------------------------------------------------------
-- TABLE: playbooks
-- Stores operational playbooks
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- -----------------------------------------------------------------------------
-- TABLE: references
-- Stores reference documents
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "references" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- -----------------------------------------------------------------------------
-- TABLE: frameworks
-- Stores framework documents
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- -----------------------------------------------------------------------------
-- TABLE: workflows
-- Stores workflow definitions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    file_path TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- ==============================================================================
-- SEARCH FUNCTIONS (RPC)
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
-- AUTOMATION TRIGGERS
-- ==============================================================================
-- 1. DEFINE TRIGGER FUNCTION
CREATE OR REPLACE FUNCTION auto_enrich_metadata() RETURNS TRIGGER AS $$
DECLARE entity_name TEXT;
current_meta JSONB;
auto_tags JSONB;
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
-- 2. ATTACH TRIGGERS
DROP TRIGGER IF EXISTS tr_sessions_auto_tag ON sessions;
CREATE TRIGGER tr_sessions_auto_tag BEFORE
INSERT
    OR
UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_case_studies_auto_tag ON case_studies;
CREATE TRIGGER tr_case_studies_auto_tag BEFORE
INSERT
    OR
UPDATE ON case_studies FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_protocols_auto_tag ON protocols;
CREATE TRIGGER tr_protocols_auto_tag BEFORE
INSERT
    OR
UPDATE ON protocols FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_capabilities_auto_tag ON capabilities;
CREATE TRIGGER tr_capabilities_auto_tag BEFORE
INSERT
    OR
UPDATE ON capabilities FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_playbooks_auto_tag ON playbooks;
CREATE TRIGGER tr_playbooks_auto_tag BEFORE
INSERT
    OR
UPDATE ON playbooks FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_references_auto_tag ON "references";
CREATE TRIGGER tr_references_auto_tag BEFORE
INSERT
    OR
UPDATE ON "references" FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_frameworks_auto_tag ON frameworks;
CREATE TRIGGER tr_frameworks_auto_tag BEFORE
INSERT
    OR
UPDATE ON frameworks FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
DROP TRIGGER IF EXISTS tr_workflows_auto_tag ON workflows;
CREATE TRIGGER tr_workflows_auto_tag BEFORE
INSERT
    OR
UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION auto_enrich_metadata();
-- ==============================================================================
-- SCHEMA COMPLETE
-- ==============================================================================