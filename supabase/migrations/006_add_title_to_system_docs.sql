-- Migration: 006_add_title_to_system_docs.sql
-- Created: 2026-01-07
-- Purpose: Fix schema mismatch where sync script expects 'title' column.
ALTER TABLE system_docs
ADD COLUMN IF NOT EXISTS title TEXT;
-- Populate title from filename if empty (fallback)
UPDATE system_docs
SET title = name
WHERE title IS NULL;
-- Ensure search index includes title
-- Note: Assuming there's a search function or index that needs updating.
-- If using pgvector or full-text search, we might need to recreate the searchable index.