-- ============================================================
-- 006_fix_search_insights.sql
-- Purpose: Repair the search_insights function which returns empty results.
-- ============================================================
-- 1. Drop existing functions to clear signature (handling potential float vs double precision ambiguity)
DROP FUNCTION IF EXISTS search_insights(vector, float, int);
DROP FUNCTION IF EXISTS search_insights(vector, double precision, integer);
-- 2. Re-create the function with explicit casting and correct return types
CREATE OR REPLACE FUNCTION search_insights(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        -- Explicitly return as TEXT
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
-- 3. Grant Permissions
GRANT EXECUTE ON FUNCTION search_insights TO anon,
    authenticated,
    service_role;
SELECT 'Fixed search_insights function.' as status;