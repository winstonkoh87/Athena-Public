-- 007_drop_insights_index.sql
-- Purpose: Drop IVFFlat index. For small tables (<1000 rows), sequential scan is faster and 100% accurate.
-- High 'lists' value (100) on 2 rows causes index lookup failures.
DROP INDEX IF EXISTS idx_insights_embedding;
SELECT 'Dropped index idx_insights_embedding to force sequential scan.' as status;