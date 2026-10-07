"""
Offline Local FTS5/BM25 Search Engine for Athena's Exocortex memory.
"""

import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

SDK_PATH = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SDK_PATH))

import athena.core.config as config


def compile_fts_query(query: str) -> str:
    """
    Compiles and sanitizes an arbitrary user query string into valid SQLite FTS5 MATCH syntax.

    Protects against:
    - Hyphens treated as unary NOT or column operators (e.g. 'CS-101' -> '"CS-101"')
    - Question marks and punctuation causing FTS5 syntax errors (e.g. 'DOC-123?' -> 'DOC-123')
    - Colons interpreted as nonexistent column filters (e.g. 'DOC-123: what was decided?' -> 'DOC-123 what was decided')
    - Unbalanced quotes
    - Stray boolean operators (AND, OR, NOT) at edges or isolated
    - Preserves intentional prefix search (e.g. 'Autocomp*' or '"Autocomp" *')
    """
    if not query or not query.strip():
        return ""

    raw = query.strip()
    quoted_matches = re.findall(r'"([^"]+)"(\s*\*?)', raw)
    remainder = re.sub(r'"[^"]*"\s*\*?', " ", raw)

    # Protect hyphenated alphanumeric terms as quoted tokens
    hyphenated = re.findall(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b", remainder)
    for h in hyphenated:
        quoted_matches.append((h, ""))
    remainder = re.sub(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b", " ", remainder)

    # Strip syntax-critical operators while allowing word-internal or trailing *
    cleaned_remainder = re.sub(r"[:\?\^\~\(\)\{\}\[\]\+\=\<\>\/\\\;\,\|\!\@\#\$\%\&]", " ", remainder)
    words = cleaned_remainder.split()

    operators = {"AND", "OR", "NOT"}
    tokens: list[str] = []

    for phrase, star in quoted_matches:
        clean_p = phrase.replace('"', "").strip()
        if clean_p:
            if star:
                tokens.append(f'"{clean_p}" *')
            else:
                tokens.append(f'"{clean_p}"')

    for w in words:
        has_star = w.endswith("*") and len(w) > 1 and w[:-1].isalnum()
        clean_w = w.rstrip("*").strip('"-._')
        if not clean_w:
            continue
        if clean_w in operators:
            tokens.append(f'"{clean_w}"')
        else:
            if has_star:
                tokens.append(f"{clean_w}*")
            else:
                tokens.append(clean_w)

    if not tokens:
        fallback_words = re.findall(r"\w+", raw)
        return " ".join(f'"{w}"' for w in fallback_words if w)

    return " ".join(tokens)


class ExocortexFTS:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path if db_path is not None else config.PROJECT_ROOT / ".athena" / "exocortex_fts.db"
        self._ensure_db_dir()

    def _ensure_db_dir(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS search_index")
        cursor.execute("DROP TABLE IF EXISTS index_meta")

        cursor.execute('''
            CREATE VIRTUAL TABLE search_index USING fts5(
                file_path, title, content,
                tokenize='porter'
            )
        ''')

        cursor.execute('''
            CREATE TABLE index_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()

    def _get_md_files(self) -> list[Path]:
        files = []

        # Directories to search
        dirs_to_search = [
            config.CONTEXT_DIR,
            config.AGENT_DIR / "skills",
            config.AGENT_DIR / "workflows",
        ]

        for d in dirs_to_search:
            if d.exists() and d.is_dir():
                for root, _, filenames in os.walk(d):
                    for fname in filenames:
                        if fname.endswith(".md"):
                            files.append(Path(root) / fname)

        return list(set(files))

    def _extract_title(self, content: str, default_title: str) -> str:
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return default_title

    def build(self) -> dict[str, Any]:
        """Builds or rebuilds the full FTS index."""
        start_time = time.time()

        files = self._get_md_files()

        total_size = 0
        file_count = 0

        conn = self._get_connection()
        self._init_db(conn)

        cursor = conn.cursor()

        for fpath in files:
            try:
                content = fpath.read_text(encoding='utf-8')
                total_size += len(content)
                title = self._extract_title(content, fpath.name)

                # Make file_path relative to PROJECT_ROOT for cleaner display and stability
                # Handle cases where file is not under PROJECT_ROOT (like in some tests)
                try:
                    rel_path = str(fpath.relative_to(config.PROJECT_ROOT))
                except ValueError:
                    rel_path = str(fpath)

                cursor.execute(
                    "INSERT INTO search_index (file_path, title, content) VALUES (?, ?, ?)",
                    (rel_path, title, content)
                )
                file_count += 1
            except Exception:
                pass

        now_ts = str(int(time.time()))
        cursor.execute("INSERT INTO index_meta (key, value) VALUES ('indexed_at', ?)", (now_ts,))
        cursor.execute("INSERT INTO index_meta (key, value) VALUES ('file_count', ?)", (str(file_count),))
        cursor.execute("INSERT INTO index_meta (key, value) VALUES ('total_size', ?)", (str(total_size),))

        conn.commit()
        conn.close()

        elapsed = time.time() - start_time
        return {
            "file_count": file_count,
            "total_size": total_size,
            "elapsed_time": elapsed
        }

    def _format_results(self, rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        results = []
        for row in rows:
            r_dict = dict(row)
            results.append({
                "file_path": r_dict["file_path"],
                "title": r_dict["title"],
                "snippet": r_dict.get("snippet", ""),
                "bm25_score": r_dict.get("bm25_score", 0.0),
                "line_number": 0
            })
        return results

    def is_stale(self, max_age_hours: float = 24.0, min_file_count: int = 100) -> bool:
        """Determines if the FTS index is missing, corrupted, underpopulated, or older than max_age_hours."""
        if not self.db_path.exists():
            return True
        st = self.stats()
        if st["file_count"] < min_file_count or st["total_size"] < 1000:
            return True
        now_ts = time.time()
        age_hours = (now_ts - st["indexed_at"]) / 3600.0
        return age_hours > max_age_hours

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """BM25-ranked keyword search."""
        if not query.strip():
            return []

        # If production index is missing or underpopulated/corrupted, auto-heal
        if self.db_path == config.PROJECT_ROOT / ".athena" / "exocortex_fts.db" and self.is_stale():
            try:
                self.build()
            except Exception:
                pass

        compiled_query = compile_fts_query(query)
        if not compiled_query:
            return []

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = '''
                SELECT
                    file_path,
                    title,
                    snippet(search_index, 2, '[MATCH]', '[/MATCH]', '...', 64) as snippet,
                    bm25(search_index) as bm25_score
                FROM search_index
                WHERE search_index MATCH ?
                ORDER BY bm25_score
                LIMIT ?
            '''

            try:
                cursor.execute(sql, (compiled_query, limit))
                rows = cursor.fetchall()
                return self._format_results(rows)
            except sqlite3.OperationalError:
                # Resilient fallback: extract purely alphanumeric tokens
                tokens = re.findall(r"\w+", query)
                if not tokens:
                    return []
                fallback_query = " ".join(f'"{t}"' for t in tokens if t)
                cursor.execute(sql, (fallback_query, limit))
                rows = cursor.fetchall()
                return self._format_results(rows)
        except Exception:
            return []
        finally:
            if conn is not None:
                conn.close()

    def stats(self) -> dict[str, Any]:
        """Returns indexed file count, total content size, last indexed timestamp."""
        stats_dict = {
            "file_count": 0,
            "total_size": 0,
            "indexed_at": 0
        }

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM index_meta")
            rows = cursor.fetchall()
            for r in rows:
                if r['key'] == 'file_count':
                    stats_dict['file_count'] = int(r['value'])
                elif r['key'] == 'total_size':
                    stats_dict['total_size'] = int(r['value'])
                elif r['key'] == 'indexed_at':
                    stats_dict['indexed_at'] = int(r['value'])
        except sqlite3.OperationalError:
            pass # Table doesn't exist
        finally:
            if 'conn' in locals():
                conn.close()

        return stats_dict

    def search_exact(self, phrase: str, limit: int = 10) -> list[dict[str, Any]]:
        """Exact phrase match."""
        if not phrase.strip():
            return []
        # Enclose phrase in double quotes for exact match in FTS5
        # Escape internal quotes if necessary
        clean_phrase = phrase.replace('"', '""')
        query = f'"{clean_phrase}"'
        return self.search(query, limit)

    def search_prefix(self, prefix: str, limit: int = 10) -> list[dict[str, Any]]:
        """Prefix search for autocomplete."""
        if not prefix.strip():
            return []
        clean_prefix = prefix.replace('"', '""')
        query = f'"{clean_prefix}" *'
        return self.search(query, limit)
