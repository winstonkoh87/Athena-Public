-- ==============================================================================
-- MIGRATION 013: FIX SEARCH FUNCTIONS (DROP AND RECREATE)
-- ==============================================================================
-- Purpose:
-- 1. Resolve Error 42P13: "cannot change return type of existing function".
-- 2. Explicitly DROP the old functions first.
-- 3. Recreate them with the new `metadata JSONB` return column.
-- ==============================================================================
-- 1. DROP EXISTING FUNCTIONS (To allow return type change)
-- ==============================================================================
DROP FUNCTION IF EXISTS search_sessions(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_case_studies(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_protocols(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_capabilities(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_playbooks(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_references(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_frameworks(vector, double precision, integer);
DROP FUNCTION IF EXISTS search_workflows(vector, double precision, integer);
-- 2. RECREATE FUNCTIONS (With Metadata)
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
-- FIX COMPLETE
-- ==============================================================================