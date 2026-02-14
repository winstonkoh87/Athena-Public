-- RE-INDEXING SCRIPT
REINDEX INDEX idx_sessions_embedding;
REINDEX INDEX idx_protocols_embedding;
REINDEX INDEX idx_case_studies_embedding;
REINDEX INDEX playbooks_embedding_idx;
REINDEX INDEX capabilities_embedding_idx;
REINDEX INDEX references_embedding_idx;
REINDEX INDEX frameworks_embedding_idx;
REINDEX INDEX workflows_embedding_idx;
REINDEX INDEX user_profile_embedding_idx;
REINDEX INDEX system_docs_embedding_idx;
REINDEX INDEX entities_embedding_idx;

-- Standard Indexes
REINDEX INDEX idx_sessions_date;
REINDEX INDEX idx_case_studies_code;
REINDEX INDEX idx_protocols_code;
REINDEX INDEX idx_protocols_category;