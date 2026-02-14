#!/usr/bin/env python3
"""
Reranker Module for Athena Semantic Search.
Uses a Cross-Encoder to refine the top-k results from the initial retrieval.
"""

import sys
import time
# Try importing SearchResult type for type hinting if available, otherwise ignore
try:
    from smart_search import SearchResult
except ImportError:
    pass

# Operational Default: Lazy load model to save memory/startup time if not needed
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import CrossEncoder
            # fast and accurate for MS MARCO (passage retrieval)
            model_name = 'cross-encoder/ms-marco-MiniLM-L6-v2' 
            # print(f"   🧠 Loading Reranker: {model_name}...", file=sys.stderr)
            _model = CrossEncoder(model_name)
        except ImportError:
            print("   ⚠️  Result reranking skipped: 'sentence_transformers' not installed.", file=sys.stderr)
            return None
        except Exception as e:
            print(f"   ⚠️  Result reranking skipped: Model load failed ({e})", file=sys.stderr)
            return None
    return _model

def rerank_results(query: str, results: list, top_k: int = 5) -> list:
    """
    Rerank a list of SearchResult objects using a Cross-Encoder.
    Returns the top_k results.
    """
    model = get_model()
    if not model or not results:
        return results[:top_k]

    # Prepare pairs: (query, content)
    # Note: content might be long, model handles truncation (normally 512 tokens)
    pairs = [(query, doc.content) for doc in results]

    start_time = time.time()
    try:
        scores = model.predict(pairs)
        
        # Attach scores and re-sort
        for doc, score in zip(results, scores):
            # doc is a SearchResult object instance
            # We add a reranker signal
            
            # Note: CrossEncoder returns logits (unbounded).
            # We store it for debugging and sorting.
            if not hasattr(doc, 'signals'):
                 doc.signals = {}
            doc.signals['reranker'] = {"score": float(score)}
            
            # We DO NOT overwrite rrf_score (fused_score) because that represents the fusion confidence.
            # But the FINAL sort order should be by reranker score.
            
        # Sort descending by reranker score
        reranked = sorted(results, key=lambda x: x.signals['reranker']['score'], reverse=True)
        
        duration = time.time() - start_time
        
        return reranked[:top_k]
        
    except Exception as e:
        print(f"   ⚠️  Reranking failed: {e}", file=sys.stderr)
        return results[:top_k]
