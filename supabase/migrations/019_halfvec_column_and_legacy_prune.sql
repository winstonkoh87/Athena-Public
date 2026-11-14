-- Migration: Compact database under Free Plan 500 MB cap
-- Created: 2026-11-14
-- Purpose:
--   1. Purge redundant full-file text (`content`) and stale `vector(3072)` columns
--      from legacy parent tables (only `document_chunks` is queried by `search_all_vectors`).
--   2. Convert `public.document_chunks.embedding` from `vector(3072)` (float32) to
--      `halfvec(3072)` (float16) so the table stores half-precision once instead of
--      duplicating float32 heap/TOAST data alongside the halfvec HNSW index.

-- 1. Purge redundant legacy content & unqueried legacy embeddings
UPDATE public.sessions SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.protocols SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.capabilities SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.case_studies SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.system_docs SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.workflows SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public."references" SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.frameworks SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.playbooks SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
UPDATE public.insights SET content = '', embedding = NULL WHERE content <> '' OR embedding IS NOT NULL;
TRUNCATE TABLE public.entities;

-- 2. Drop expression HNSW index prior to altering the column type in-place
DROP INDEX IF EXISTS public.document_chunks_embedding_halfvec_idx;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'document_chunks'
          AND column_name = 'embedding'
          AND udt_name = 'vector'
    ) THEN
        ALTER TABLE public.document_chunks
            ALTER COLUMN embedding TYPE halfvec(3072)
            USING embedding::halfvec(3072);
    END IF;
END;
$$;

-- 3. Create direct HNSW index on halfvec(3072) column
CREATE INDEX IF NOT EXISTS document_chunks_embedding_halfvec_idx
    ON public.document_chunks
    USING hnsw (embedding halfvec_cosine_ops);

-- 4. Update search_all_vectors RPC to query halfvec(3072) column directly without per-row cast
CREATE OR REPLACE FUNCTION public.search_all_vectors(
    query_embedding vector,
    match_threshold double precision DEFAULT 0.3,
    match_count integer DEFAULT 5
)
RETURNS TABLE(
    source_table text,
    id text,
    file_path text,
    similarity double precision,
    title text,
    content text,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
DECLARE
    q_half halfvec(3072);
BEGIN
    q_half := query_embedding::halfvec(3072);
    RETURN QUERY
    SELECT
        dc.table_name AS source_table,
        dc.id::text,
        dc.file_path,
        (1 - (dc.embedding <=> q_half))::double precision AS similarity,
        dc.title,
        dc.content,
        dc.metadata || jsonb_build_object('chunk_index', dc.chunk_index) AS metadata
    FROM public.document_chunks dc
    WHERE dc.embedding IS NOT NULL
      AND (1 - (dc.embedding <=> q_half)) > match_threshold
    ORDER BY dc.embedding <=> q_half
    LIMIT match_count;
END;
$$;
