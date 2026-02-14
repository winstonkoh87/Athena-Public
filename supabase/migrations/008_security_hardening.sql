-- ============================================================
-- 008_security_hardening.sql
-- Purpose: 
-- 1. Fix "mutable search_path" security issues in search functions.
-- 2. Fix insecure RLS policy on 'telegram_messages'.
-- 3. Ensure vector indexes exist for performance.
-- ============================================================
-- ============================================================
-- PART 1: SECURE SEARCH FUNCTIONS (Fixed search_path)
-- ============================================================
-- 1. SEARCH SESSIONS
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        date DATE,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT s.id::text,
    s.date,
    s.title,
    s.content,
    s.file_path,
    1 - (s.embedding <=> query_embedding) AS similarity
FROM sessions s
WHERE 1 - (s.embedding <=> query_embedding) > match_threshold
ORDER BY s.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 2. SEARCH PROTOCOLS
CREATE OR REPLACE FUNCTION search_protocols(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        code TEXT,
        name TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT p.id::text,
    p.code,
    p.name,
    p.content,
    p.file_path,
    1 - (p.embedding <=> query_embedding) AS similarity
FROM protocols p
WHERE 1 - (p.embedding <=> query_embedding) > match_threshold
ORDER BY p.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 3. SEARCH CASE STUDIES
CREATE OR REPLACE FUNCTION search_case_studies(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        code TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT cs.id::text,
    cs.code,
    cs.title,
    cs.content,
    cs.file_path,
    1 - (cs.embedding <=> query_embedding) AS similarity
FROM case_studies cs
WHERE 1 - (cs.embedding <=> query_embedding) > match_threshold
ORDER BY cs.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 4. SEARCH CAPABILITIES
CREATE OR REPLACE FUNCTION search_capabilities(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        name TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT c.id::text,
    c.name,
    c.content,
    c.file_path,
    1 - (c.embedding <=> query_embedding) AS similarity
FROM capabilities c
WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 5. SEARCH PLAYBOOKS
CREATE OR REPLACE FUNCTION search_playbooks(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        name TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT pb.id::text,
    pb.name,
    pb.title,
    pb.content,
    pb.file_path,
    1 - (pb.embedding <=> query_embedding) AS similarity
FROM playbooks pb
WHERE 1 - (pb.embedding <=> query_embedding) > match_threshold
ORDER BY pb.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 6. SEARCH REFERENCES
CREATE OR REPLACE FUNCTION search_references(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        name TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT r.id::text,
    r.name,
    r.title,
    r.content,
    r.file_path,
    1 - (r.embedding <=> query_embedding) AS similarity
FROM "references" r
WHERE 1 - (r.embedding <=> query_embedding) > match_threshold
ORDER BY r.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 7. SEARCH FRAMEWORKS
CREATE OR REPLACE FUNCTION search_frameworks(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        name TEXT,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT f.id::text,
    f.name,
    f.title,
    f.content,
    f.file_path,
    1 - (f.embedding <=> query_embedding) AS similarity
FROM frameworks f
WHERE 1 - (f.embedding <=> query_embedding) > match_threshold
ORDER BY f.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 8. SEARCH WORKFLOWS
CREATE OR REPLACE FUNCTION search_workflows(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        name TEXT,
        description TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT w.id::text,
    w.name,
    w.description,
    w.content,
    w.file_path,
    1 - (w.embedding <=> query_embedding) AS similarity
FROM workflows w
WHERE 1 - (w.embedding <=> query_embedding) > match_threshold
ORDER BY w.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
-- 9. SEARCH USER PROFILE
CREATE OR REPLACE FUNCTION search_user_profile(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        filename TEXT,
        title TEXT,
        category TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT up.id::text,
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
-- 10. SEARCH SYSTEM DOCS
CREATE OR REPLACE FUNCTION search_system_docs(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        doc_type TEXT,
        filename TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT sd.id::text,
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
-- 11. SEARCH ENTITIES
CREATE OR REPLACE FUNCTION search_entities(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 10
    ) RETURNS TABLE (
        id TEXT,
        entity_name TEXT,
        entity_type TEXT,
        content TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
SELECT e.id::text,
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
-- 12. SEARCH INSIGHTS
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
    ) LANGUAGE plpgsql
SET search_path = public,
    extensions AS $$ BEGIN RETURN QUERY
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
-- ============================================================
-- PART 2: FIX TELEGRAM MESSAGES RLS
-- ============================================================
DO $$ BEGIN IF EXISTS (
    SELECT
    FROM pg_tables
    WHERE schemaname = 'public'
        AND tablename = 'telegram_messages'
) THEN
ALTER TABLE telegram_messages ENABLE ROW LEVEL SECURITY;
-- Dropping potential bad policies
DROP POLICY IF EXISTS "Enable insert for service role only" ON telegram_messages;
DROP POLICY IF EXISTS "Enable read access for all users" ON telegram_messages;
-- Re-creating secure policy
CREATE POLICY "Enable insert for service role only" ON telegram_messages FOR
INSERT TO service_role WITH CHECK (true);
END IF;
END $$;
-- ============================================================
-- PART 3: ENSURE PERFORMANCE INDEXES
-- ============================================================
-- Ensure HNSW or IVFFlat indexes exist (idempotent)
-- Note: Assuming vector extension is active and ivfflat is preferred for this scale.
CREATE INDEX IF NOT EXISTS idx_sessions_embedding ON sessions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_protocols_embedding ON protocols USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_case_studies_embedding ON case_studies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_capabilities_embedding ON capabilities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_playbooks_embedding ON playbooks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_references_embedding ON "references" USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_frameworks_embedding ON frameworks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_workflows_embedding ON workflows USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_user_profile_embedding ON user_profile USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_system_docs_embedding ON system_docs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_entities_embedding ON entities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_insights_embedding ON insights USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
SELECT 'All security and performance issues fixed.' as status;