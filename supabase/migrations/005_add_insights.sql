-- ============================================================
-- 005_add_insights.sql
-- Purpose: Add 'insights' table for semantic search of analysis/ directory.
-- ============================================================
-- 1. Create Table
CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    filename TEXT NOT NULL,
    title TEXT,
    content TEXT,
    file_path TEXT UNIQUE NOT NULL,
    embedding VECTOR(768) -- Gemini 1.5 Dimensions
);
-- 2. Enable RLS
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
-- Allow read access to everyone (public repo style)
CREATE POLICY "Public read access" ON insights FOR
SELECT USING (true);
-- Allow write access to service role only
CREATE POLICY "Service role write access" ON insights FOR ALL USING (auth.role() = 'service_role');
-- 3. Create Index (IVFFlat for speed, or HNSW if preferred, sticking to IVFFlat for consistency)
CREATE INDEX IF NOT EXISTS idx_insights_embedding ON insights USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- 4. Create Search Function
DROP FUNCTION IF EXISTS search_insights(vector, float, int);
CREATE OR REPLACE FUNCTION search_insights(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        filename TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
SELECT i.id::text,
    i.filename,
    i.title,
    i.content,
    i.file_path,
    1 - (i.embedding <=> query_embedding) AS similarity
FROM insights i
WHERE 1 - (i.embedding <=> query_embedding) > match_threshold
ORDER BY i.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 5. Grant Permissions
GRANT SELECT ON insights TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_insights TO anon,
    authenticated,
    service_role;
SELECT 'Created insights table and search function.' as status;