-- Phase 2-4: Additional Supabase Tables for Full Workspace Sync
-- Run this in Supabase SQL Editor

-- ============================================================
-- TABLE: user_profile
-- Purpose: Store user psychology, constraints, operating principles
-- ============================================================

CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    title TEXT,
    category TEXT,  -- 'psychology', 'constraints', 'principles', 'profile', 'general'
    content TEXT NOT NULL,
    file_path TEXT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for similarity search
CREATE INDEX IF NOT EXISTS user_profile_embedding_idx ON user_profile 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ============================================================
-- TABLE: system_docs
-- Purpose: Store TAG_INDEX, project_state, patterns, etc.
-- ============================================================

CREATE TABLE IF NOT EXISTS system_docs (
    id SERIAL PRIMARY KEY,
    doc_type TEXT NOT NULL,  -- 'index', 'state', 'manifest', 'pattern', 'system'
    filename TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS system_docs_embedding_idx ON system_docs 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ============================================================
-- TABLE: entities (for result.json - Phase 3)
-- Purpose: Store parsed entity data from Telegram export
-- ============================================================

CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT,  -- 'person', 'conversation', 'group'
    chunk_index INTEGER DEFAULT 0,  -- For multi-chunk entities
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS entities_embedding_idx ON entities 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS entities_name_idx ON entities(entity_name);

-- ============================================================
-- SEARCH FUNCTIONS
-- ============================================================

-- Search user_profile
CREATE OR REPLACE FUNCTION search_user_profile(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id INT,
    filename TEXT,
    title TEXT,
    category TEXT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        up.id,
        up.filename,
        up.title,
        up.category,
        up.content,
        1 - (up.embedding <=> query_embedding) AS similarity
    FROM user_profile up
    WHERE 1 - (up.embedding <=> query_embedding) > match_threshold
    ORDER BY up.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Search system_docs
CREATE OR REPLACE FUNCTION search_system_docs(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id INT,
    doc_type TEXT,
    filename TEXT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sd.id,
        sd.doc_type,
        sd.filename,
        sd.content,
        1 - (sd.embedding <=> query_embedding) AS similarity
    FROM system_docs sd
    WHERE 1 - (sd.embedding <=> query_embedding) > match_threshold
    ORDER BY sd.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Search entities
CREATE OR REPLACE FUNCTION search_entities(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id INT,
    entity_name TEXT,
    entity_type TEXT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.entity_name,
        e.entity_type,
        e.content,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM entities e
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION search_user_profile TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION search_system_docs TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION search_entities TO anon, authenticated, service_role;

-- ============================================================
-- DONE
-- ============================================================
SELECT 'Tables and functions created successfully!' AS status;
