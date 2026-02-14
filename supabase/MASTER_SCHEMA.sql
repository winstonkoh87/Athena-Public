-- ==============================================================================
-- ATHENA v9.3 MASTER SCHEMA (3072-dim Unified + JSONB Metadata)
-- ==============================================================================
-- Single source of truth for all Supabase tables, indexes, and search functions.
-- Supports 12 tables, HNSW indexes, JSONB metadata, and auto-tagging triggers.
--
-- CHANGELOG:
--   v9.3 (2026-02-15): Added JSONB metadata, HNSW indexes, auto-tagging triggers
--   v9.2 (2026-02-07): Initial 12-table unified schema
--
-- LAST UPDATED: 2026-02-15 04:30 SGT
-- ==============================================================================
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- ==============================================================================
-- 1. CORE TABLES (UUID-based)
-- ==============================================================================
-- sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    session_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sessions_embedding ON sessions USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_metadata ON sessions USING gin (metadata);
-- case_studies
CREATE TABLE IF NOT EXISTS case_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_case_studies_embedding ON case_studies USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_case_studies_metadata ON case_studies USING gin (metadata);
-- protocols
CREATE TABLE IF NOT EXISTS protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    name TEXT NOT NULL,
    category TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_protocols_embedding ON protocols USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_protocols_metadata ON protocols USING gin (metadata);
-- capabilities
CREATE TABLE IF NOT EXISTS capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_capabilities_embedding ON capabilities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_capabilities_metadata ON capabilities USING gin (metadata);
-- playbooks
CREATE TABLE IF NOT EXISTS playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_playbooks_embedding ON playbooks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_playbooks_metadata ON playbooks USING gin (metadata);
-- references
CREATE TABLE IF NOT EXISTS "references" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_references_embedding ON "references" USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_references_metadata ON "references" USING gin (metadata);
-- frameworks
CREATE TABLE IF NOT EXISTS frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_frameworks_embedding ON frameworks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_frameworks_metadata ON frameworks USING gin (metadata);
-- workflows
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_workflows_embedding ON workflows USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_workflows_metadata ON workflows USING gin (metadata);
-- insights
CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    title TEXT,
    content TEXT,
    file_path TEXT UNIQUE NOT NULL,
    embedding VECTOR(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_insights_embedding ON insights USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_insights_metadata ON insights USING gin (metadata);
-- ==============================================================================
-- 2. EXTENDED TABLES (Serial-based)
-- ==============================================================================
-- system_docs
CREATE TABLE IF NOT EXISTS system_docs (
    id SERIAL PRIMARY KEY,
    doc_type TEXT,
    filename TEXT,
    content TEXT,
    file_path TEXT UNIQUE NOT NULL,
    embedding VECTOR(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_system_docs_embedding ON system_docs USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_system_docs_metadata ON system_docs USING gin (metadata);
-- user_profile
CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    title TEXT,
    category TEXT,
    content TEXT,
    file_path TEXT UNIQUE NOT NULL,
    embedding VECTOR(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_profile_embedding ON user_profile USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_user_profile_metadata ON user_profile USING gin (metadata);
-- entities
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    entity_name TEXT,
    entity_type TEXT,
    content TEXT,
    file_path TEXT UNIQUE NOT NULL,
    embedding VECTOR(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_entities_embedding ON entities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_entities_metadata ON entities USING gin (metadata);
-- ==============================================================================
-- 3. SEARCH FUNCTIONS (RPC)
-- ==============================================================================
-- Universal semantic search across any table
CREATE OR REPLACE FUNCTION search_table(
        target_table TEXT,
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY EXECUTE format(
        'SELECT
            t.id::text,
            COALESCE(t.title, t.name, t.filename, ''Untitled'') as title,
            LEFT(t.content, 500) as content,
            t.file_path,
            1 - (t.embedding <=> $1) AS similarity
        FROM public.%I t
        WHERE t.embedding IS NOT NULL
            AND 1 - (t.embedding <=> $1) > $2
        ORDER BY t.embedding <=> $1
        LIMIT $3',
        target_table
    ) USING query_embedding,
    match_threshold,
    match_count;
END;
$$;
-- Dedicated session search (returns structured session data)
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.7,
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
FROM public.sessions s
WHERE s.embedding IS NOT NULL
    AND 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Dedicated case study search
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.7,
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
FROM public.case_studies cs
WHERE cs.embedding IS NOT NULL
    AND 1 - (cs.embedding <=> query_embedding) > match_threshold
ORDER BY cs.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Dedicated protocol search
CREATE OR REPLACE FUNCTION search_protocols(
        query_embedding vector(3072),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        code TEXT,
        name TEXT,
        category TEXT,
        title TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.code,
    p.name,
    p.category,
    p.title,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM public.protocols p
WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Exact metadata search (for tag/category filtering)
CREATE OR REPLACE FUNCTION search_by_metadata(
        target_table TEXT,
        metadata_key TEXT,
        metadata_value TEXT,
        result_limit INT DEFAULT 20
    ) RETURNS TABLE (
        id TEXT,
        title TEXT,
        file_path TEXT,
        metadata JSONB
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY EXECUTE format(
        'SELECT
            t.id::text,
            COALESCE(t.title, t.name, t.filename, ''Untitled'') as title,
            t.file_path,
            t.metadata
        FROM public.%I t
        WHERE t.metadata->>$1 = $2
        ORDER BY t.created_at DESC
        LIMIT $3',
        target_table
    ) USING metadata_key,
    metadata_value,
    result_limit;
END;
$$;
-- ==============================================================================
-- 4. AUTO-TAGGING TRIGGER (DemonSynth Protocol)
-- ==============================================================================
-- Automatically extracts metadata from content on INSERT/UPDATE.
-- Populates the JSONB metadata column with: word_count, has_code, category, etc.
CREATE OR REPLACE FUNCTION auto_tag_metadata() RETURNS TRIGGER AS $$ BEGIN -- Auto-populate metadata from content analysis
    NEW.metadata = COALESCE(NEW.metadata, '{}'::jsonb) || jsonb_build_object(
        'word_count',
        array_length(
            string_to_array(COALESCE(NEW.content, ''), ' '),
            1
        ),
        'has_code',
        (COALESCE(NEW.content, '') LIKE '%```%'),
        'last_indexed',
        NOW()
    );
-- Auto-set updated_at
NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- Apply trigger to all core tables
DO $$
DECLARE tbl TEXT;
BEGIN FOR tbl IN
SELECT unnest(
        ARRAY [
        'sessions', 'case_studies', 'protocols', 'capabilities',
        'playbooks', 'references', 'frameworks', 'workflows',
        'insights', 'system_docs', 'user_profile', 'entities'
    ]
    ) LOOP EXECUTE format(
        'DROP TRIGGER IF EXISTS trg_auto_tag_%I ON %I; ' || 'CREATE TRIGGER trg_auto_tag_%I ' || 'BEFORE INSERT OR UPDATE ON %I ' || 'FOR EACH ROW EXECUTE FUNCTION auto_tag_metadata();',
        tbl,
        tbl,
        tbl,
        tbl
    );
END LOOP;
END;
$$;
-- ==============================================================================
-- 5. PERMISSIONS
-- ==============================================================================
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon,
    authenticated,
    service_role;
-- ==============================================================================
-- MIGRATION NOTES (from v9.2)
-- ==============================================================================
-- If upgrading from v9.2, run these ALTER statements:
--
-- ALTER TABLE sessions ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- ALTER TABLE sessions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
-- (repeat for all tables)
--
-- To switch from IVFFlat to HNSW:
-- DROP INDEX IF EXISTS idx_sessions_embedding;
-- CREATE INDEX idx_sessions_embedding ON sessions USING hnsw (embedding vector_cosine_ops);
-- (repeat for all tables)
-- ==============================================================================