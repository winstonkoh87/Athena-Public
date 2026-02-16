"""
athena.memory.sync
==================
Core logic for synchronizing workspace content to Supabase pgvector.
Robustness: Handles absolute/relative path mismatches & Exponential Backoff.
"""

import re
import time
from pathlib import Path

from athena.memory.delta_manifest import DeltaManifest
from athena.memory.vectors import get_client, get_embedding

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def Extract_Metadata_Simplistic(content: str) -> dict:
    """Simple frontmatter extractor."""
    meta = {}
    if content.startswith("---"):
        try:
            end = content.find("---", 3)
            if end != -1:
                yaml_block = content[3:end]
                for line in yaml_block.splitlines():
                    if ":" in line:
                        items = line.split(":", 1)
                        if len(items) == 2:
                            meta[items[0].strip()] = (
                                items[1].strip().strip('"').strip("'")
                            )
        except (ValueError, KeyError, IndexError):
            pass
    return meta


def extract_metadata(content: str, filename: str) -> dict:
    """Extract metadata wrapper."""
    return Extract_Metadata_Simplistic(content)


def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def parse_session_filename(filename: str) -> tuple[str | None, int | None]:
    """Extract date and session number from standard filename."""
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md")
    match = pattern.match(filename)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


def extract_title(content: str) -> str | None:
    """Find the first H1 markdown header."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def sync_file_to_supabase(
    file_path: Path,
    table_name: str,
    extra_metadata: dict | None = None,
    manifest: DeltaManifest | None = None,
    max_retries: int = 3,
):
    """
    Sync a single file with Exponential Backoff Retries.
    """
    abs_root = PROJECT_ROOT.resolve()
    abs_file = file_path.resolve()

    if not abs_file.exists():
        return False

    if manifest and not manifest.should_sync(abs_file):
        return True

    content = abs_file.read_text(encoding="utf-8")
    meta = extract_metadata(content, abs_file.name)
    if extra_metadata:
        meta.update(extra_metadata)

    client = get_client()
    embedding = get_embedding(content[:30000])

    try:
        db_path = str(abs_file.relative_to(abs_root))
    except ValueError:
        db_path = str(abs_file)

    data = {
        "content": content,
        "embedding": embedding,
        "file_path": db_path,
        "title": meta.get("title", abs_file.name),
    }
    _enrich_data_by_table(data, abs_file, table_name, meta)

    # Retry Loop
    for attempt in range(max_retries):
        try:
            client.table(table_name).upsert(data, on_conflict="file_path").execute()
            if manifest:
                manifest.update_entry(abs_file)
            return True
        except Exception as e:
            if "code" in str(e).lower() and table_name in ["protocols", "case_studies"]:
                try:
                    client.table(table_name).upsert(data, on_conflict="code").execute()
                    if manifest:
                        manifest.update_entry(abs_file)
                    return True
                except Exception:
                    pass

            if attempt < max_retries - 1:
                wait = (2**attempt) + 0.5
                # print(f"  ⚠ Retry {attempt+1} for {abs_file.name} in {wait}s...")
                time.sleep(wait)
            else:
                raise e

    return False


def _enrich_data_by_table(data: dict, file_path: Path, table_name: str, meta: dict):
    if table_name == "sessions":
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
        data["date"] = date_match.group(1) if date_match else "2026-01-01"
        data["session_number"] = (
            int(re.search(r"session-(\d+)", file_path.name).group(1))
            if "session-" in file_path.name
            else 1
        )
    elif table_name == "protocols":
        code_match = re.match(r"(\d+)", file_path.name)
        data["code"] = code_match.group(1) if code_match else "000"
        data["name"] = file_path.stem
    elif table_name == "case_studies":
        code_match = re.match(r"(CS-\d+)", file_path.name)
        data["code"] = code_match.group(1) if code_match else file_path.stem
    elif table_name == "capabilities":
        data["name"] = file_path.stem
    elif table_name == "workflows":
        data["name"] = file_path.stem
        if "title" in data:
            del data["title"]
    elif table_name == "system_docs":
        data["filename"] = file_path.name
        data["doc_type"] = "system"
    elif table_name == "memory_bank":
        data["filename"] = file_path.name
        data["doc_type"] = "memory_bank"


def delete_file_from_vector(file_path_str: str):
    client = get_client()
    abs_root = PROJECT_ROOT.resolve()
    try:
        abs_file = Path(file_path_str).resolve()
        db_path = str(abs_file.relative_to(abs_root))
    except (ValueError, OSError):
        db_path = file_path_str

    table_name = "system_docs"
    if "session_logs" in file_path_str:
        table_name = "sessions"
    elif "case_studies" in file_path_str:
        table_name = "case_studies"
    elif "protocols" in file_path_str:
        table_name = "protocols"
    elif "memory_bank" in file_path_str:
        table_name = "system_docs"  # Map memory_bank to system_docs table

    try:
        client.table(table_name).delete().eq("file_path", db_path).execute()
        return True
    except Exception:
        return False
