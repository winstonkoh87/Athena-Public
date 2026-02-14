-- ==============================================================================
-- ATHENA v9.3 UPGRADE A: THE MEMORY PRISM (Indexable Shadow Column)
-- ==============================================================================
-- ⚠️ PROBLEM: 3072-dim vectors cannot be indexed by pgvector (max 2000).
--
-- ✅ SOLUTION: Matryoshka Representation Learning (MRL) Slicing
--    1. Add `index_embedding` column (FIRST 1536 dims of the 3072 vector).
--    2. Create HNSW indexes on `index_embedding` for O(log n) search.
--    3. Search hits the fast index, then re-ranks with full 3072 vector.
--
-- LAST UPDATED: 2026-02-08 04:28 SGT
-- ==============================================================================
--------------------------------------------------------------------------------
-- STEP 1: ADD SHADOW INDEX COLUMN TO ALL 12 TABLES
--------------------------------------------------------------------------------
DO $$
DECLARE table_name TEXT;
BEGIN FOR table_name IN
SELECT unnest(
        ARRAY [
        'sessions', 'case_studies', 'protocols', 'capabilities',
        'playbooks', 'references', 'frameworks', 'workflows',
        'system_docs', 'user_profile', 'entities', 'insights'
    ]
    ) LOOP EXECUTE format(
        'ALTER TABLE %I ADD COLUMN IF NOT EXISTS index_embedding vector(1536)',
        table_name
    );
RAISE NOTICE 'Added index_embedding column to %',
table_name;
END LOOP;
END $$;
--------------------------------------------------------------------------------
-- STEP 2: POPULATE INDEX COLUMN (SLICE FIRST 1536 DIMS)
--------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION slice_vector_1536(v vector(3072)) RETURNS vector(1536) AS $$ BEGIN IF v IS NULL THEN RETURN NULL;
END IF;
-- pgvector casts to real[], not float8[] - use array slicing
RETURN (v::real []) [1:1536]::vector(1536);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
-- Populate for all tables
DO $$
DECLARE table_name TEXT;
BEGIN FOR table_name IN
SELECT unnest(
        ARRAY [
        'sessions', 'case_studies', 'protocols', 'capabilities',
        'playbooks', 'references', 'frameworks', 'workflows',
        'system_docs', 'user_profile', 'entities', 'insights'
    ]
    ) LOOP EXECUTE format(
        'UPDATE %I SET index_embedding = slice_vector_1536(embedding) WHERE embedding IS NOT NULL AND index_embedding IS NULL',
        table_name
    );
RAISE NOTICE 'Populated index_embedding for %',
table_name;
END LOOP;
END $$;
--------------------------------------------------------------------------------
-- STEP 3: CREATE HNSW INDEXES ON SHADOW COLUMN
--------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sessions_index_embedding ON sessions USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_case_studies_index_embedding ON case_studies USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_protocols_index_embedding ON protocols USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_capabilities_index_embedding ON capabilities USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_playbooks_index_embedding ON playbooks USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_references_index_embedding ON "references" USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_frameworks_index_embedding ON frameworks USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_workflows_index_embedding ON workflows USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_system_docs_index_embedding ON system_docs USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_user_profile_index_embedding ON user_profile USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_entities_index_embedding ON entities USING hnsw (index_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_insights_index_embedding ON insights USING hnsw (index_embedding vector_cosine_ops);
--------------------------------------------------------------------------------
-- STEP 4: CREATE TRIGGER TO AUTO-POPULATE ON INSERT/UPDATE
--------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION auto_populate_index_embedding() RETURNS TRIGGER AS $$ BEGIN IF NEW.embedding IS NOT NULL THEN NEW.index_embedding := slice_vector_1536(NEW.embedding);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DO $$
DECLARE table_name TEXT;
BEGIN FOR table_name IN
SELECT unnest(
        ARRAY [
        'sessions', 'case_studies', 'protocols', 'capabilities',
        'playbooks', 'references', 'frameworks', 'workflows',
        'system_docs', 'user_profile', 'entities', 'insights'
    ]
    ) LOOP EXECUTE format(
        'DROP TRIGGER IF EXISTS trg_auto_index_embedding ON %I',
        table_name
    );
EXECUTE format(
    'CREATE TRIGGER trg_auto_index_embedding BEFORE INSERT OR UPDATE OF embedding ON %I FOR EACH ROW EXECUTE FUNCTION auto_populate_index_embedding()',
    table_name
);
RAISE NOTICE 'Created auto-populate trigger for %',
table_name;
END LOOP;
END $$;
--------------------------------------------------------------------------------
-- STEP 5: VERIFICATION
--------------------------------------------------------------------------------
SELECT schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE indexname LIKE '%index_embedding%'
ORDER BY tablename;
SELECT '✅ MEMORY PRISM COMPLETE: 12 Tables with HNSW-indexed 1536-dim shadow columns.' AS status;