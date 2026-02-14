-- 009_cleanup_duplicates.sql
-- Fix duplicate indexes and RLS policy issues
-- Run Date: 2026-01-21
-- ============================================================
-- PART 1: DROP DUPLICATE INDEXES
-- ============================================================
DROP INDEX IF EXISTS idx_capabilities_embedding;
DROP INDEX IF EXISTS idx_frameworks_embedding;
DROP INDEX IF EXISTS idx_playbooks_embedding;
DROP INDEX IF EXISTS idx_references_embedding;
DROP INDEX IF EXISTS idx_workflows_embedding;
-- ============================================================
-- PART 2: FIX INSIGHTS RLS POLICIES
-- ============================================================
-- Drop conflicting policies
DROP POLICY IF EXISTS "Public read access" ON insights;
DROP POLICY IF EXISTS "Service role write access" ON insights;
-- Re-create with optimized pattern (using SELECT for auth function)
CREATE POLICY "Public read access" ON insights FOR
SELECT USING (true);
CREATE POLICY "Service role write access" ON insights FOR ALL USING (
    (
        SELECT auth.role()
    ) = 'service_role'
) WITH CHECK (
    (
        SELECT auth.role()
    ) = 'service_role'
);
-- ============================================================
-- PART 3: SEPARATE INSIGHTS POLICIES (No overlap)
-- ============================================================
DROP POLICY IF EXISTS "Public read access" ON insights;
DROP POLICY IF EXISTS "Service role write access" ON insights;
-- Read access for everyone
CREATE POLICY "Public read access" ON insights FOR
SELECT TO public USING (true);
-- Write access ONLY for service_role (INSERT, UPDATE, DELETE)
CREATE POLICY "Service role insert" ON insights FOR
INSERT TO service_role WITH CHECK (true);
CREATE POLICY "Service role update" ON insights FOR
UPDATE TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role delete" ON insights FOR DELETE TO service_role USING (true);
SELECT 'Cleanup complete: Duplicate indexes dropped, RLS policies fixed.' as status;