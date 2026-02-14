-- ============================================================
-- Supabase Migration: Add Semantic Search Functions
-- Run this in Supabase SQL Editor
-- ============================================================
-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;
-- ============================================================
-- Function: search_sessions
-- Semantic search over session logs using cosine similarity
-- ============================================================
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding vector(768),
        match_threshold float DEFAULT 0.3,
        match_count int DEFAULT 5
    ) RETURNS TABLE (
        id uuid,
        date text,
        session_number int,
        title text,
        file_path text,
        similarity float
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT s.id,
    s.date,
    s.session_number,
    s.title,
    s.file_path,
    1 - (s.embedding <=> query_embedding) as similarity
FROM public.sessions s
WHERE 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- ============================================================
-- Function: search_case_studies
-- Semantic search over case studies using cosine similarity
-- ============================================================
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding vector(768),
        match_threshold float DEFAULT 0.3,
        match_count int DEFAULT 5
    ) RETURNS TABLE (
        id uuid,
        code text,
        title text,
        tags text [],
        file_path text,
        similarity float
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT c.id,
    c.code,
    c.title,
    c.tags,
    c.file_path,
    1 - (c.embedding <=> query_embedding) as similarity
FROM public.case_studies c
WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- ============================================================
-- Grant permissions (if using RLS)
-- ============================================================
GRANT EXECUTE ON FUNCTION search_sessions TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_case_studies TO anon,
    authenticated,
    service_role;
-- ============================================================
-- Verify functions were created
-- ============================================================
SELECT 'search_sessions' as function_name,
    proname
FROM pg_proc
WHERE proname = 'search_sessions'
UNION ALL
SELECT 'search_case_studies' as function_name,
    proname
FROM pg_proc
WHERE proname = 'search_case_studies';