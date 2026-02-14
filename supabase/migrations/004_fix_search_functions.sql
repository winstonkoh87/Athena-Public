-- ============================================================
-- 004_fix_search_functions.sql (v3)
-- Purpose: Fix "operator does not exist" error AND return type mismatch
-- Strategy: Cast all IDs to TEXT to handle mixed UUID/INT schema.
-- ============================================================
-- 1. SEARCH SESSIONS
DROP FUNCTION IF EXISTS search_sessions(vector, float, int);
DROP FUNCTION IF EXISTS search_sessions(vector, double precision, integer);
CREATE OR REPLACE FUNCTION search_sessions(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.3,
        match_count INT DEFAULT 5
    ) RETURNS TABLE (
        id TEXT,
        -- Changed to TEXT to handle UUID or INT
        date DATE,
        title TEXT,
        content TEXT,
        file_path TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
SELECT s.id::text,
    -- Explicit cast
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
DROP FUNCTION IF EXISTS search_protocols(vector, float, int);
DROP FUNCTION IF EXISTS search_protocols(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_case_studies(vector, float, int);
DROP FUNCTION IF EXISTS search_case_studies(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_capabilities(vector, float, int);
DROP FUNCTION IF EXISTS search_capabilities(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_playbooks(vector, float, int);
DROP FUNCTION IF EXISTS search_playbooks(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_references(vector, float, int);
DROP FUNCTION IF EXISTS search_references(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_frameworks(vector, float, int);
DROP FUNCTION IF EXISTS search_frameworks(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_workflows(vector, float, int);
DROP FUNCTION IF EXISTS search_workflows(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_user_profile(vector, float, int);
DROP FUNCTION IF EXISTS search_user_profile(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_system_docs(vector, float, int);
DROP FUNCTION IF EXISTS search_system_docs(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
DROP FUNCTION IF EXISTS search_entities(vector, float, int);
DROP FUNCTION IF EXISTS search_entities(vector, double precision, integer);
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
    ) LANGUAGE plpgsql AS $$ BEGIN
SET search_path = public,
    extensions;
RETURN QUERY
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
-- GRANTS
GRANT EXECUTE ON FUNCTION search_sessions TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_protocols TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_case_studies TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_capabilities TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_playbooks TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_references TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_frameworks TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_workflows TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_user_profile TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_system_docs TO anon,
    authenticated,
    service_role;
GRANT EXECUTE ON FUNCTION search_entities TO anon,
    authenticated,
    service_role;
SELECT 'All functions updated to return ID as TEXT (UUID/INT compatible)!' AS status;