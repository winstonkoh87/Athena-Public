#!/bin/bash
# exec_deep_reindex.sh
# Full deep reindex and refactor pipeline
# Usage: ./exec_deep_reindex.sh > reindex.log 2>&1 &

echo "=================================================="
echo "🚀 ATHENA DEEP REINDEX PROTOCOL INITIATED"
echo "=================================================="
date

echo "--- Phase 1: Deep Entity Extraction (Gemini 2.0 Flash) ---"
python3 -u .agent/scripts/extract_entities.py || { echo "❌ Extraction failed"; exit 1; }

echo "--- Phase 2: Knowledge Graph Build (Leiden + Gemini) ---"
python3 -u .agent/scripts/build_graph.py || { echo "❌ Graph build failed"; exit 1; }

echo "--- Phase 3: Workspace Refactor Automation ---"
echo ">> Running Orphan Detector..."
python3 .agent/scripts/orphan_detector.py
echo ">> Running Supabase Sync..."
python3 .agent/scripts/supabase_sync.py || echo "⚠️ Supabase sync warning"
echo ">> Generate Tag Index..."
python3 .agent/scripts/generate_tag_index.py

echo "=================================================="
echo "✅ MISSION COMPLETE: Deep Reindex & Refactor Finished"
echo "=================================================="
date
