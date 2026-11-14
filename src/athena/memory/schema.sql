-- ============================================================================
-- Athena VectorRAG Schema for Supabase + pgvector
-- ============================================================================
-- 
-- Run this in your Supabase SQL Editor to set up the semantic memory system.
-- 
-- Prerequisites:
--   1. Create a Supabase project at https://supabase.com
--   2. Enable pgvector: Extensions → pgvector → Enable
--   3. Run this SQL in the SQL Editor
--
-- After setup, add to your .env:
--   SUPABASE_URL=https://your-project.supabase.co
--   SUPABASE_ANON_KEY=your-anon-key
-- ============================================================================
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- ============================================================================
-- CORE TABLES
-- ============================================================================
-- Sessions: Daily interaction logs
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    session_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    file_path TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Case Studies: Pattern analysis documents
CREATE TABLE IF NOT EXISTS case_studies (
    id SERIAL PRIMARY KEY,
    case_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    file_path TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Protocols: Reusable thinking patterns
CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    protocol_id TEXT UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    file_path TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Document Chunks: Segment-level half-precision (halfvec) text embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    table_name TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    embedding halfvec(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(file_path, chunk_index)
);
-- ============================================================================
-- INDEXES (HNSW on halfvec(3072) bypasses pgvector's 2000-dim float32 cap)
-- ============================================================================
CREATE INDEX IF NOT EXISTS document_chunks_embedding_halfvec_idx
    ON document_chunks USING hnsw (embedding halfvec_cosine_ops);
-- ============================================================================
-- SEARCH FUNCTIONS (RPC)
-- ============================================================================
-- Search sessions by semantic similarity
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding VECTOR(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id INT,
        date DATE,
        title TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT s.id,
    s.date,
    s.title,
    s.content,
    1 - (s.embedding <=> query_embedding) AS similarity
FROM sessions s
WHERE 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search case studies by semantic similarity
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding VECTOR(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id INT,
        case_id TEXT,
        title TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT c.id,
    c.case_id,
    c.title,
    c.content,
    1 - (c.embedding <=> query_embedding) AS similarity
FROM case_studies c
WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- Search protocols by semantic similarity
CREATE OR REPLACE FUNCTION search_protocols(
        query_embedding VECTOR(3072),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id INT,
        protocol_id TEXT,
        title TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT p.id,
    p.protocol_id,
    p.title,
    p.content,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM protocols p
WHERE 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- ============================================================================
-- ROW-LEVEL SECURITY (Optional but recommended)
-- ============================================================================
-- Enable RLS on all tables (uncomment after setting up auth)
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE case_studies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE protocols ENABLE ROW LEVEL SECURITY;
-- Example policy: Allow all operations for authenticated users
-- CREATE POLICY "authenticated_access" ON sessions
--     FOR ALL USING (auth.role() = 'authenticated');
-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Run this to verify setup:
-- SELECT COUNT(*) FROM sessions;
-- SELECT COUNT(*) FROM case_studies;
-- SELECT COUNT(*) FROM protocols;