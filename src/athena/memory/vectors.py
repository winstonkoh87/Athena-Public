"""
athena.memory.vectors — Thread-Safe v1.2

Optimizations:
    - Thread-Local Clients: Prevents httpx connection state corruption in parallel loops.
    - Atomic Cache: PersistentEmbeddingCache now uses Locks and Atomic Writes.
"""

import contextlib
import hashlib
import json
import os
import random
import sqlite3
import sys
import threading
import time
from typing import Any

# This module's stdout belongs to callers that parse it. run_search(json_output=
# True) pipes stdout straight into json.loads, so a single diagnostic line here
# — an API-key error, a retry notice — corrupts the payload, the caller's parse
# raises, and the query is scored as a retrieval miss rather than the
# credentials failure it actually was.
#
# Every print in this module is a diagnostic; none of them is data. Bind the
# name once at module scope rather than annotating ~16 call sites and missing
# the next one somebody adds.
_stdout_print = print


def print(*args, **kwargs):  # noqa: A001 — deliberate module-scoped shadow
    """Diagnostics go to stderr. See the note above before changing this."""
    kwargs.setdefault("file", sys.stderr)
    _stdout_print(*args, **kwargs)


# Global cache instance
_embedding_cache = None
_embedding_cache_lock = threading.Lock()

# Rate limiter: serialize embedding API calls to prevent 429 on free-tier Gemini
_embedding_semaphore = threading.Semaphore(1)
_consecutive_429_count = 0
_consecutive_429_lock = threading.Lock()


class EmbeddingQuotaExhausted(RuntimeError):
    """Raised when consecutive HTTP 429 rate limit errors exceed the safety threshold."""
    pass


def emit_api_alert(status_code: int) -> None:
    """Surface prominent terminal banner when Google Gemini API credits or quota are exhausted (TD-081)."""
    if status_code == 402:
        banner = (
            "\n" + "=" * 60 + "\n"
            "🚨 [ACTION REQUIRED: GOOGLE API CREDITS DEPLETED]\n"
            "   Google API returned HTTP 402 (Payment Required).\n"
            "   Your Google AI Studio prepay balance on Project Athena is USD 0.00.\n"
            "   Please top up USD 20 at: https://aistudio.google.com\n"
            + "=" * 60 + "\n"
        )
    elif status_code == 429:
        banner = (
            "\n" + "=" * 60 + "\n"
            "🚨 [ACTION REQUIRED: GOOGLE API QUOTA EXHAUSTED / RATE LIMITED]\n"
            "   Google API returned HTTP 429 (Resource Exhausted / Rate Limit).\n"
            "   Your Google AI Studio rate limit or daily quota on Project Athena is saturated.\n"
            "   Please check quota or upgrade Tier at: https://aistudio.google.com\n"
            + "=" * 60 + "\n"
        )
    else:
        return
    print(banner, file=sys.stderr)



def get_embedding_cache():
    global _embedding_cache
    with _embedding_cache_lock:
        if _embedding_cache is None:
            _embedding_cache = PersistentEmbeddingCache()
        return _embedding_cache


# Thread-local storage for Supabase clients
_thread_local = threading.local()


def get_client() -> Any:
    """Returns a thread-safe Supabase client instance."""
    if not hasattr(_thread_local, "client"):
        from dotenv import load_dotenv

        from supabase import create_client

        load_dotenv()

        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in environment.")
        _thread_local.client = create_client(url, key)
    return _thread_local.client


class PersistentEmbeddingCache:
    """SQLite-backed embedding cache (drop-in replacement for the old JSON cache).

    The previous design kept every embedding in one JSON file that was loaded into RAM
    at startup and rewritten wholesale on each save — O(n) per write, O(n^2) under bulk
    load, growing unbounded (177MB+). SQLite gives O(1) INSERT OR REPLACE, O(1) keyed
    lookup, WAL crash-safety, and never rewrites the whole store.

    Public API is unchanged: get(hash) / set(hash, emb) / set_many({hash: emb}).
    On first use it transparently imports the legacy embedding_cache.json (if present)
    and renames it to *.migrated, so the import runs exactly once and the old file is
    kept as a backup.
    """

    def __init__(self, filename: str = "embedding_cache.json"):
        from athena.core.config import AGENT_DIR

        state_dir = AGENT_DIR / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_json = state_dir / filename
        self.db_path = state_dir / "embedding_cache.db"
        self.lock = threading.Lock()
        # check_same_thread=False: the cache is shared across the sync's worker threads;
        # every access is serialized by self.lock, so single-connection use stays safe.
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        with self.lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS embeddings "
                "(hash TEXT PRIMARY KEY, vec TEXT NOT NULL)"
            )
            self._conn.commit()
        self._migrate_legacy_json()

    def _migrate_legacy_json(self):
        """One-time idempotent import of the old monolithic JSON cache, then archive it."""
        try:
            if not self.legacy_json.exists():
                return
            # May be large or mid-write from an old-code process; on any failure we keep
            # the JSON untouched and retry on a later run (no data loss).
            data = json.loads(self.legacy_json.read_text(encoding="utf-8"))
            rows = [
                (h, json.dumps(v))
                for h, v in data.items()
                if isinstance(v, list) and v
            ]
            print(
                f"  ⚙️  Migrating {len(rows)} embeddings: legacy JSON → SQLite "
                f"({self.db_path.name})...",
                flush=True,
            )
            with self.lock:
                self._conn.executemany(
                    "INSERT OR REPLACE INTO embeddings (hash, vec) VALUES (?, ?)", rows
                )
                self._conn.commit()
            self._archive_legacy()
            print("  ✅ Embedding cache migrated to SQLite.", flush=True)
        except Exception as e:
            print(f"  ⚠️  Legacy cache migration deferred ({e}); JSON kept for retry.", flush=True)

    def _reconnect(self):
        """Attempt to re-establish the SQLite connection if dropped or stale."""
        with contextlib.suppress(Exception):
            if hasattr(self, "_conn") and self._conn:
                self._conn.close()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")

    def _archive_legacy(self):
        with contextlib.suppress(Exception):
            self.legacy_json.rename(
                self.legacy_json.parent / (self.legacy_json.name + ".migrated")
            )

    def get(self, text_hash: str) -> list[float] | None:
        try:
            with self.lock:
                row = self._conn.execute(
                    "SELECT vec FROM embeddings WHERE hash = ?", (text_hash,)
                ).fetchone()
            if row is None:
                return None
            try:
                return json.loads(row[0])
            except Exception:
                return None
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            # Reconnect attempt for stale connection/locks, otherwise graceful cache miss
            try:
                with self.lock:
                    self._reconnect()
                    row = self._conn.execute(
                        "SELECT vec FROM embeddings WHERE hash = ?", (text_hash,)
                    ).fetchone()
                if row is not None:
                    return json.loads(row[0])
            except Exception:
                pass
            return None
        except Exception:
            return None

    def set(self, text_hash: str, embedding: list[float]):
        try:
            with self.lock:
                self._conn.execute(
                    "INSERT OR REPLACE INTO embeddings (hash, vec) VALUES (?, ?)",
                    (text_hash, json.dumps(embedding)),
                )
                self._conn.commit()
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            try:
                with self.lock:
                    self._reconnect()
                    self._conn.execute(
                        "INSERT OR REPLACE INTO embeddings (hash, vec) VALUES (?, ?)",
                        (text_hash, json.dumps(embedding)),
                    )
                    self._conn.commit()
            except Exception:
                pass
        except Exception:
            pass

    def set_many(self, items: "dict[str, list[float]]"):
        """Bulk insert in one transaction — O(1) per row, no full-file rewrite."""
        if not items:
            return
        rows = [(h, json.dumps(v)) for h, v in items.items()]
        try:
            with self.lock:
                self._conn.executemany(
                    "INSERT OR REPLACE INTO embeddings (hash, vec) VALUES (?, ?)", rows
                )
                self._conn.commit()
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            try:
                with self.lock:
                    self._reconnect()
                    self._conn.executemany(
                        "INSERT OR REPLACE INTO embeddings (hash, vec) VALUES (?, ?)", rows
                    )
                    self._conn.commit()
            except Exception:
                pass
        except Exception:
            pass


def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def get_embedding(text: str, max_retries: int = 7) -> list[float]:
    """Generate embedding with persistent disk caching and exponential backoff.

    Uses gemini-embedding-001 (3072 dimensions).
    Retries on 429 (rate limit) and 5xx (server error) with exponential backoff + jitter.
    Semaphore-gated (1 concurrent) to prevent thundering herd on free-tier Gemini API.
    Backoff ceiling: 60s. Floor delay: 1s per call to avoid burst patterns.
    """
    text_hash = _hash_text(text)
    cache = get_embedding_cache()
    cached = cache.get(text_hash)
    if cached:
        return cached

    # Fetch remote (Gemini) - Lazy load requests
    import requests
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing.")

    # Pass the key via header, NOT the query string. A key in the URL leaks into
    # every requests exception/response repr (the URL is echoed in error messages),
    # which is logged below — clear-text secret logging. The header is never logged.
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    headers = {"x-goog-api-key": api_key}
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
    }

    last_error = None
    for attempt in range(max_retries):
        with _embedding_semaphore:
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=60)  # type: ignore[arg-type]

                # If client error that is not 429, do not retry! It is non-retriable.
                if response.status_code >= 400 and response.status_code < 500 and response.status_code != 429:
                    if response.status_code == 402:
                        emit_api_alert(402)
                    print(f"  ❌ Client error {response.status_code} in get_embedding: {response.text[:200]}")
                    response.raise_for_status()

                if response.status_code == 429 or response.status_code >= 500:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait = min(float(retry_after), 60)
                    else:
                        wait = min((2 ** attempt) + random.uniform(0, 1), 60)
                    print(f"  ⚠️  HTTP {response.status_code} in get_embedding (attempt {attempt+1}/{max_retries}). Retrying in {wait:.2f}s...")
                    last_error = f"HTTP {response.status_code}"
                    if response.status_code == 429:
                        with _consecutive_429_lock:
                            global _consecutive_429_count
                            _consecutive_429_count += 1
                            if _consecutive_429_count >= 5:
                                emit_api_alert(429)
                                raise EmbeddingQuotaExhausted(
                                    f"Aborting: {_consecutive_429_count} consecutive HTTP 429 errors. "
                                    "Gemini API quota exhausted — retry later."
                                )
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(wait)
                        continue
                    else:
                        if response.status_code == 429:
                            emit_api_alert(429)
                        response.raise_for_status()

                response.raise_for_status()
                embedding = response.json()["embedding"]["values"]
                with _consecutive_429_lock:
                    _consecutive_429_count = 0
                cache.set(text_hash, embedding)
                # Floor delay: prevent burst even on success (free-tier courtesy)
                time.sleep(1)
                return embedding

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                # Check if it is a non-retriable client error raised during request
                if hasattr(e, 'response') and e.response is not None:
                    code = e.response.status_code
                    if code >= 400 and code < 500 and code != 429:
                        print(f"  ❌ Non-retriable request exception (HTTP {code}): {e}")
                        raise

                if attempt < max_retries - 1:
                    import time
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  ⚠️  Request exception in get_embedding: {e}. Retrying in {wait:.2f}s...")
                    time.sleep(wait)
                else:
                    raise

    raise RuntimeError(f"get_embedding failed after {max_retries} retries: {last_error}")


def get_embeddings_batch(
    texts: list[str], batch_size: int = 25, max_retries: int = 7
) -> list[list[float] | None]:
    """Embed many texts via Gemini :batchEmbedContents, warming the persistent cache.

    Why this exists: get_embedding() is Semaphore(1)-serialized with a 1s floor delay
    per call, so embedding N files costs ~1.5-2s EACH, serially (the real reason a sync
    takes 20+ min). batchEmbedContents collapses N cache-misses into ceil(N/batch_size)
    requests. Cache hits are skipped entirely (no API). On ANY batch failure it falls
    back to the proven per-item get_embedding(), so correctness/latency is never WORSE
    than the single-call path — only better.

    Returns embeddings aligned to `texts` (None for any that ultimately failed).
    Side effect: populates the on-disk embedding cache, so a subsequent per-file
    get_embedding(text) for the same text is an instant cache hit.
    """
    cache = get_embedding_cache()
    results: list[list[float] | None] = [None] * len(texts)
    misses = []  # list of (index, text, hash)
    for i, t in enumerate(texts):
        h = _hash_text(t)
        cached = cache.get(h)
        if cached is not None:
            results[i] = cached
        else:
            misses.append((i, t, h))

    if not misses:
        return results

    import requests
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing.")

    # Key goes in a header, never the query string — a key in the URL leaks into
    # logged requests exceptions/response reprs (clear-text secret logging).
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-embedding-001:batchEmbedContents"
    )
    headers = {"x-goog-api-key": api_key}

    total_batches = (len(misses) + batch_size - 1) // batch_size
    print(
        f"  ⚡ {len(misses)} embeds needed "
        f"({len(texts) - len(misses)} cache hits) → {total_batches} batches",
        flush=True,
    )
    new_embeddings: dict[str, list[float]] = {}

    for start in range(0, len(misses), batch_size):
        group = misses[start : start + batch_size]
        payload = {
            "requests": [
                {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": t}]}}
                for _, t, _ in group
            ]
        }
        got: list[list[float]] | None = None
        for attempt in range(max_retries):
            with _embedding_semaphore:
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=120)  # type: ignore[arg-type]

                    # Fail immediately on non-retriable client errors
                    if resp.status_code >= 400 and resp.status_code < 500 and resp.status_code != 429:
                        if resp.status_code == 402:
                            emit_api_alert(402)
                        print(f"  ❌ Client error {resp.status_code} in batch query: {resp.text[:200]}")
                        resp.raise_for_status()

                    if resp.status_code == 429 or resp.status_code >= 500:
                        retry_after = resp.headers.get("Retry-After")
                        wait = (
                            min(float(retry_after), 60)
                            if retry_after
                            else min((2 ** attempt) + random.uniform(0, 1), 60)
                        )
                        print(f"  ⚠️  HTTP {resp.status_code} in batch query (attempt {attempt+1}/{max_retries}). Retrying in {wait:.2f}s...")
                        if resp.status_code == 429:
                            with _consecutive_429_lock:
                                global _consecutive_429_count
                                _consecutive_429_count += 1
                                if _consecutive_429_count >= 5:
                                    emit_api_alert(429)
                                    raise EmbeddingQuotaExhausted(
                                        f"Aborting: {_consecutive_429_count} consecutive HTTP 429 errors. "
                                        "Gemini API quota exhausted — retry later."
                                    )
                        if attempt < max_retries - 1:
                            time.sleep(wait)
                            continue
                        if resp.status_code == 429:
                            emit_api_alert(429)
                        resp.raise_for_status()

                    resp.raise_for_status()
                    got = [e["values"] for e in resp.json()["embeddings"]]
                    with _consecutive_429_lock:
                        _consecutive_429_count = 0
                    time.sleep(1)  # free-tier courtesy: ONE delay per batch, not per text
                    break
                except EmbeddingQuotaExhausted:
                    raise
                except Exception as e:
                    # If it's a client error (HTTP 400/413), raise immediately without retry so we fall back
                    if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                        code = e.response.status_code
                        if code >= 400 and code < 500 and code != 429:
                            print(f"  ❌ Non-retriable batch HTTP error {code}: {e}. Falling back to per-item.")
                            got = None
                            break

                    if attempt < max_retries - 1:
                        wait = (2 ** attempt) + random.uniform(0, 1)
                        print(f"  ⚠️  Exception in batch query: {e}. Retrying in {wait:.2f}s...")
                        time.sleep(wait)
                    else:
                        print(f"  ❌ Batch query failed after {max_retries} attempts: {e}. Falling back to per-item.")
                        got = None

        if got is not None and len(got) == len(group):
            for (i, t, h), emb in zip(group, got, strict=False):
                results[i] = emb
                new_embeddings[h] = emb  # buffered; flushed in one coalesced save below
        else:
            print(f"  🔄 Safe degrade: embedding {len(group)} items individually...")
            # Safe degrade: per-item via the proven single-call path.
            for i, t, h in group:
                try:
                    results[i] = get_embedding(t)
                except EmbeddingQuotaExhausted:
                    raise
                except Exception as e:
                    print(f"    ❌ Failed to embed item: {e}")
                    results[i] = None

        print(f"  ⚡ batch {start // batch_size + 1}/{total_batches} done", flush=True)

        # Checkpoint every ~500 new embeds (one coalesced save) for crash safety.
        if len(new_embeddings) >= 500:
            cache.set_many(new_embeddings)
            new_embeddings = {}

    # Final flush of the remainder — one bulk write, never per-item O(n^2).
    if new_embeddings:
        cache.set_many(new_embeddings)
    return results


def search_rpc(
    rpc_name: str, query_embedding: list[float], limit: int = 5, threshold: float = 0.3
) -> list[dict]:
    client = get_client()
    result = client.rpc(
        rpc_name,
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


# --- Collection-Specific Wrappers ---


def search_sessions(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_sessions", query_embedding, limit, threshold)


def search_case_studies(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_case_studies", query_embedding, limit, threshold)


def search_protocols(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_protocols", query_embedding, limit, threshold)


def search_capabilities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_capabilities", query_embedding, limit, threshold)


def search_playbooks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_playbooks", query_embedding, limit, threshold)


def search_references(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_references", query_embedding, limit, threshold)


def search_frameworks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_frameworks", query_embedding, limit, threshold)


def search_workflows(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_workflows", query_embedding, limit, threshold)


def search_entities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_entities", query_embedding, limit, threshold)


def search_user_profile(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_user_profile", query_embedding, limit, threshold)


def search_system_docs(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_system_docs", query_embedding, limit, threshold)


def search_insights(client, query_embedding, limit=5, threshold=0.3):
    """Search insights table (Marketing Analysis, Strategic Notes)."""
    return search_rpc("search_insights", query_embedding, limit, threshold)
