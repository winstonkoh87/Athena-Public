-- ============================================
-- ATHENA v8: SUPABASE MEMORY LAYER
-- Run this in Supabase SQL Editor
-- ============================================
-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
-- ============================================
-- TABLE: sessions
-- Stores session logs with embeddings
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    session_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    embedding vector(768),
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Prevent duplicates based on file path
    UNIQUE(file_path)
);
-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date DESC);
-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_sessions_embedding ON sessions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- ============================================
-- TABLE: case_studies
-- Stores case studies with embeddings
-- ============================================
CREATE TABLE IF NOT EXISTS case_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT [],
    embedding vector(768),
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Prevent duplicates
    UNIQUE(code),
    UNIQUE(file_path)
);
-- Index for code lookup
CREATE INDEX IF NOT EXISTS idx_case_studies_code ON case_studies(code);
-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_case_studies_embedding ON case_studies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- ============================================
-- FUNCTION: search_sessions
-- Semantic search across sessions
-- ============================================
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding vector(768),
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
-- ============================================
-- FUNCTION: search_case_studies
-- Semantic search across case studies
-- ============================================
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding vector(768),
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
-- ============================================
-- SETUP COMPLETE
-- ============================================
-- Tables created:
--   - sessions (for session logs)
--   - case_studies (for case studies)
-- Functions created:
--   - search_sessions(embedding, threshold, count)
--   - search_case_studies(embedding, threshold, count)
-- ============================================