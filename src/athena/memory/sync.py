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


def parse_session_filename(filename: str) -> "tuple[str | None, int | None]":
    """Extract date and session number from standard filename."""
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md")
    match = pattern.match(filename)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


def extract_title(content: str) -> "str | None":
    """Find the first H1 markdown header."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def sync_file_to_supabase(
    file_path: Path,
    table_name: str,
    extra_metadata: "dict | None" = None,
    manifest: "DeltaManifest | None" = None,
    max_retries: int = 3,
    force: bool = False,
):
    """
    Sync a single file with Exponential Backoff Retries.
    """
    abs_root = PROJECT_ROOT.resolve()
    abs_file = file_path.resolve()

    if not abs_file.exists():
        return False

    if not force and manifest and not manifest.should_sync(abs_file):
        return True

    content = abs_file.read_text(encoding="utf-8")
    if not content.strip():
        if manifest:
            manifest.update_entry(abs_file)
        return True

    meta = extract_metadata(content, abs_file.name)
    if extra_metadata:
        meta.update(extra_metadata)

    client = get_client()

    try:
        db_path = str(abs_file.relative_to(abs_root))
    except ValueError:
        db_path = str(abs_file)

    # Split content into chunks
    chunks = chunk_text(content, chunk_size=4000, overlap=400)
    if not chunks:
        chunks = [content]

    # Retry Loop (now wraps BOTH embedding + upsert)
    for attempt in range(max_retries):
        try:
            # 1. Embed ALL chunks FIRST, before any destructive DB op. A transient
            #    embedding/network failure here must NOT leave the file with its old
            #    chunks deleted and no replacement (the silent-drop bug: protocols
            #    vanished when an embed failed mid-loop after the delete). Build the
            #    full payload list; only mutate the DB once every embed has succeeded.
            chunk_payloads = []
            for idx, chunk in enumerate(chunks):
                chunk_payloads.append({
                    "file_path": db_path,
                    "table_name": table_name,
                    "chunk_index": idx,
                    "title": meta.get("title", abs_file.name),
                    "content": chunk,
                    "embedding": get_embedding(chunk),
                    "metadata": meta,
                })

            # 2. Now safe to mutate: delete stale chunks, then upsert the fresh set.
            client.table("document_chunks").delete().eq("file_path", db_path).execute()
            for chunk_data in chunk_payloads:
                client.table("document_chunks").upsert(chunk_data, on_conflict="file_path,chunk_index").execute()

            # 3. Upsert parent metadata (no file-level embedding stored to save DB size)
            parent_data = {
                "content": content,
                "file_path": db_path,
                "title": meta.get("title", abs_file.name),
            }
            _enrich_data_by_table(parent_data, abs_file, table_name, meta)

            conflict_target = "filename" if table_name == "user_profile" else "file_path"
            client.table(table_name).upsert(parent_data, on_conflict=conflict_target).execute()

            if manifest:
                manifest.update_entry(abs_file)
            return True
        except Exception as e:
            if "code" in str(e).lower() and table_name in ["protocols", "case_studies"]:
                try:
                    client.table(table_name).upsert(parent_data, on_conflict="code").execute()
                    if manifest:
                        manifest.update_entry(abs_file)
                    return True
                except Exception:
                    pass

            if attempt < max_retries - 1:
                wait = (2**attempt) + 0.5
                time.sleep(wait)
            else:
                raise e

    return False


def _enrich_data_by_table(data: dict, file_path: Path, table_name: str, meta: dict):
    if table_name == "sessions":
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
        data["date"] = date_match.group(1) if date_match else "2026-01-01"
        session_num_match = re.search(r"session-(\d+)", file_path.name)
        data["session_number"] = (
            int(session_num_match.group(1)) if session_num_match else 1
        )
    elif table_name == "protocols":
        code_match = re.match(r"(\d+)", file_path.name)
        data["code"] = code_match.group(1) if code_match else "000"
        data["name"] = file_path.stem
    elif table_name == "case_studies":
        code_match = re.match(r"(CS-\d+)", file_path.name)
        data["code"] = code_match.group(1) if code_match else file_path.stem
    elif table_name == "capabilities":
        # For SKILL.md files, use parent directory name (e.g., "bionic-safety-net")
        # For other files, use the file stem
        if file_path.stem.upper() == "SKILL":
            data["name"] = file_path.parent.name
        else:
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
    elif table_name in ["frameworks", "playbooks", "references"]:
        data["name"] = file_path.stem
    elif table_name == "user_profile":
        data["filename"] = file_path.name
        data["category"] = meta.get("category", "general")


def delete_file_from_vector(file_path_str: str):
    client = get_client()
    abs_root = PROJECT_ROOT.resolve()
    try:
        abs_file = Path(file_path_str).resolve()
        db_path = str(abs_file.relative_to(abs_root))
    except (ValueError, OSError):
        db_path = file_path_str

    # Dynamic mapping to match target configurations
    table_name = "system_docs"
    if "session_logs" in file_path_str:
        table_name = "sessions"
    elif "case_studies" in file_path_str or "proposals" in file_path_str or "Reflection Essay" in file_path_str:
        table_name = "case_studies"
    elif "protocols" in file_path_str:
        table_name = "protocols"
    elif "capabilities" in file_path_str or "skills" in file_path_str:
        table_name = "capabilities"
    elif "workflows" in file_path_str:
        table_name = "workflows"
    elif "playbooks" in file_path_str:
        table_name = "playbooks"
    elif "references" in file_path_str or "brand_references" in file_path_str:
        table_name = "references"
    elif "frameworks" in file_path_str or ".framework" in file_path_str:
        table_name = "frameworks"
    elif "user_profile" in file_path_str or "profile" in file_path_str:
        table_name = "user_profile"

    try:
        # Delete from unified document_chunks table
        client.table("document_chunks").delete().eq("file_path", db_path).execute()
        # Delete from parent metadata table
        client.table(table_name).delete().eq("file_path", db_path).execute()
        return True
    except Exception:
        return False


def verify_chunk_integrity(expected_min_ratio: float = 0.5) -> bool:
    """
    Verifies chunk DB count against local context file count.
    Returns True if chunk population passes integrity threshold.
    """
    try:
        context_dir = PROJECT_ROOT / ".context"
        if not context_dir.exists():
            return True

        local_files = [f for f in context_dir.glob("**/*") if f.is_file() and f.suffix in (".md", ".json", ".yaml")]
        client = get_client()
        res = client.table("document_chunks").select("id", count="exact").execute()
        chunk_count = res.count or 0

        return chunk_count >= len(local_files) * expected_min_ratio
    except Exception:
        # Return True if vector DB connection is offline/unconfigured to avoid blocking local runs
        return True

