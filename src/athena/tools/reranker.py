"""
athena.tools.reranker
=====================

Cross-Encoder Reranking logic.

Two inference paths, tried in order:

1. ONNX fast path (default): tokenizers + onnxruntime against the locally
   exported quantized model in .agent/models/reranker-onnx/. No torch, no
   transformers — ~0.4s cold load vs ~13-58s for the torch path. Scores match
   the torch model within ~0.005 (verified 2026-07-03; qint8_arm64 quantization).
2. sentence_transformers CrossEncoder fallback: used only if the ONNX assets
   or onnxruntime are unavailable.

Regenerate the ONNX assets (e.g. after a model upgrade) by downloading
onnx/model_qint8_arm64.onnx + tokenizer.json from the HF repo
cross-encoder/ms-marco-MiniLM-L6-v2 into .agent/models/reranker-onnx/.
"""

import importlib.util
import os

# CRITICAL (S527): force transformers onto the PyTorch backend BEFORE it is imported.
# Without this, transformers probes for TensorFlow, imports it (~20s on this machine),
# then crashes on the Keras 3 incompatibility ("install tf-keras"). Only relevant to
# the CrossEncoder fallback path, but cheap to set unconditionally.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys
from pathlib import Path
from typing import Any

from athena.core.models import SearchResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def get_onnx_dir() -> Path:
    """Resolve ONNX model directory across local repo, custom env var, or user cache."""
    if os.environ.get("ATHENA_RERANKER_DIR"):
        return Path(os.environ["ATHENA_RERANKER_DIR"])
    repo_dir = PROJECT_ROOT / ".agent" / "models" / "reranker-onnx"
    if repo_dir.exists():
        return repo_dir
    cache_dir = Path.home() / ".cache" / "athena" / "models" / "reranker-onnx"
    if cache_dir.exists():
        return cache_dir
    return repo_dir


ONNX_DIR = get_onnx_dir()
# Prefer the arm64-quantized model (4x smaller, faster); fall back to fp32.
ONNX_MODEL_CANDIDATES = ["model_qint8_arm64.onnx", "model.onnx"]
MAX_LENGTH = 256
RERANK_BATCH_SIZE = 8

# Lazy-loaded singletons
_onnx_session = None
_onnx_tokenizer = None
_onnx_failed = False
_model = None  # CrossEncoder fallback

# Cap on how many candidates we rerank. Widened 12→50 (2026-07-03): 12-of-25 sat
# below every published range — 2025 industry norm is 50-100 candidates into the
# cross-encoder (ZeroEntropy/Cohere/Ailog guides); a first-stage miss below the cap
# can never be rescued. The ONNX fast path scores 50 pairs in ~0.1s, so the old
# torch-latency rationale for a tight cap no longer applies.
RERANK_CANDIDATE_CAP = 50


def check_reranker_health() -> dict[str, Any]:
    """Check availability of ONNX reranker model and libraries for doctor / telemetry (F-04 fix)."""
    onnx_dir = get_onnx_dir()
    has_onnx_dir = onnx_dir.exists()
    model_file = next(
        (onnx_dir / name for name in ONNX_MODEL_CANDIDATES if (onnx_dir / name).exists()),
        None,
    ) if has_onnx_dir else None
    has_tokenizer = (onnx_dir / "tokenizer.json").exists() if has_onnx_dir else False

    # Availability probes only — find_spec checks importability without
    # paying the import cost (torch alone is seconds) or binding unused names.
    can_import_onnx = importlib.util.find_spec("onnxruntime") is not None
    can_import_tokenizers = importlib.util.find_spec("tokenizers") is not None
    can_import_torch = importlib.util.find_spec("sentence_transformers") is not None

    is_operational = bool((model_file and has_tokenizer and can_import_onnx and can_import_tokenizers) or can_import_torch)

    return {
        "operational": is_operational,
        "mode": "onnx" if (model_file and has_tokenizer and can_import_onnx and can_import_tokenizers) else ("torch" if can_import_torch else "none"),
        "model_path": str(model_file) if model_file else None,
        "has_model_file": model_file is not None,
        "has_tokenizer": has_tokenizer,
        "has_onnxruntime": can_import_onnx,
        "has_tokenizers": can_import_tokenizers,
        "has_torch_fallback": can_import_torch,
    }


def _get_onnx():
    """Load the ONNX session + tokenizer. Returns (session, tokenizer) or None."""
    global _onnx_session, _onnx_tokenizer, _onnx_failed
    if _onnx_failed:
        return None
    if _onnx_session is not None:
        return _onnx_session, _onnx_tokenizer
    try:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = next(
            (ONNX_DIR / name for name in ONNX_MODEL_CANDIDATES if (ONNX_DIR / name).exists()),
            None,
        )
        tokenizer_path = ONNX_DIR / "tokenizer.json"
        if model_path is None or not tokenizer_path.exists():
            _onnx_failed = True
            return None

        tokenizer = Tokenizer.from_file(str(tokenizer_path))
        tokenizer.enable_truncation(max_length=MAX_LENGTH)
        tokenizer.enable_padding()
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = min(4, max(1, os.cpu_count() or 4))
        opts.inter_op_num_threads = 1
        opts.add_session_config_entry("session.intra_op.allow_spinning", "0")
        session = ort.InferenceSession(
            str(model_path),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        _onnx_session, _onnx_tokenizer = session, tokenizer
        return session, tokenizer
    except Exception:
        _onnx_failed = True
        return None


def _predict_onnx(pairs: "list[tuple[str, str]]") -> "list[float] | None":
    """Score (query, doc) pairs via length-sorted mini-batches in the ONNX session."""
    if not pairs:
        return []
    loaded = _get_onnx()
    if not loaded:
        return None
    session, tokenizer = loaded
    try:
        import numpy as np

        indexed = sorted(enumerate(pairs), key=lambda item: len(item[1][1]))
        scores = [0.0] * len(pairs)
        for start in range(0, len(indexed), RERANK_BATCH_SIZE):
            chunk = indexed[start : start + RERANK_BATCH_SIZE]
            encodings = tokenizer.encode_batch([pair for _, pair in chunk])
            feeds = {
                "input_ids": np.array([e.ids for e in encodings], dtype=np.int64),
                "attention_mask": np.array([e.attention_mask for e in encodings], dtype=np.int64),
                "token_type_ids": np.array([e.type_ids for e in encodings], dtype=np.int64),
            }
            logits = session.run(None, feeds)[0].ravel()
            for (orig_idx, _), logit in zip(chunk, logits, strict=False):
                scores[orig_idx] = float(logit)
        return scores
    except Exception as e:
        print(f"   ⚠️  ONNX rerank failed ({e}); falling back to CrossEncoder.", file=sys.stderr)
        return None


def get_model():
    """CrossEncoder fallback (torch path). Lazy-loaded; None if unavailable."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import CrossEncoder
            model_name = 'cross-encoder/ms-marco-MiniLM-L6-v2'
            _model = CrossEncoder(model_name)
        except ImportError:
            return None
        except Exception:
            return None
    return _model


def _predict(pairs: "list[tuple[str, str]]") -> "list[float] | None":
    """Score pairs: ONNX fast path first, CrossEncoder fallback second."""
    scores = _predict_onnx(pairs)
    if scores is not None:
        return scores
    model = get_model()
    if model is None:
        return None
    return [float(s) for s in model.predict(pairs)]


class SafeCrossEncoder:
    """
    Resilient CrossEncoder wrapper. Handles ONNX fast path, CrossEncoder fallback,
    and graceful degradation on timeout or missing dependencies.
    """
    def __init__(self, timeout_sec: int = 5):
        self.timeout_sec = timeout_sec
        self.fallback_used = False

    def rerank(self, query: str, results: list[SearchResult], top_k: int = 5) -> tuple[list[SearchResult], bool]:
        if not results:
            return results, False

        candidates = results[:RERANK_CANDIDATE_CAP]
        pairs = [(query, doc.content or "") for doc in candidates]

        try:
            scores = _predict_onnx(pairs)
            if scores is None:
                self.fallback_used = True
                model = get_model()
                if model is None:
                    return results[:top_k], True
                scores = [float(s) for s in model.predict(pairs)]

            for doc, score in zip(candidates, scores, strict=False):
                if not doc.signals:
                    doc.signals = {}
                doc.signals['reranker'] = {"score": score}

            reranked = sorted(candidates, key=lambda x: x.signals['reranker']['score'], reverse=True)
            return reranked[:top_k], self.fallback_used

        except Exception as e:
            print(f"   ⚠️  Reranking failed ({e}); returning candidate slice.", file=sys.stderr)
            return results[:top_k], True


def rerank_results(query: str, results: list[SearchResult], top_k: int = 5) -> list[SearchResult]:
    """
    Rerank a list of SearchResult objects using SafeCrossEncoder.
    Returns top_k results.
    """
    safe_encoder = SafeCrossEncoder()
    reranked, _ = safe_encoder.rerank(query, results, top_k=top_k)
    return reranked

