"""
delta_manifest.py — High-Performance Manifest Engine (v1.1)

Optimizations:
    - O(1) Quick-Check: Compares size/mtime before expensive hashing.
    - Thread-Safe: Uses Locks for shared manifest updates.
    - Path Stable: All paths stored as relative to PROJECT_ROOT.
"""

import hashlib
import json
import os
import threading
import tempfile
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timezone

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MANIFEST_PATH = PROJECT_ROOT / ".athena" / "state" / "manifest.json"
MANIFEST_VERSION = "1.1"


class DeltaManifest:
    def __init__(self, manifest_path: Path = MANIFEST_PATH):
        self.manifest_path = manifest_path
        self.lock = threading.Lock()
        self.data: Dict = {"version": MANIFEST_VERSION, "files": {}}
        self._load()

    def _load(self):
        """Load manifest from disk."""
        if not self.manifest_path.exists():
            return

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            # print(f"⚠️ Corrupt manifest detected: {e}. Starting fresh.")
            self.data = {"version": MANIFEST_VERSION, "files": {}}

    def save(self):
        """Atomic save of manifest."""
        with self.lock:
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write pattern
            fd, temp_path = tempfile.mkstemp(dir=self.manifest_path.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2)
                os.replace(temp_path, self.manifest_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise

    def _get_rel_path(self, path: Path) -> str:
        """Ensure path is relative to PROJECT_ROOT for manifest stability."""
        try:
            return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
        except (ValueError, AttributeError):
            # Fallback if path is already relative or root mismatch
            return str(path)

    def normalize_content(self, content: str) -> bytes:
        """Normalize content for hashing."""
        return content.strip().replace("\r\n", "\n").encode("utf-8")

    def _get_file_stats(self, path: Path) -> Tuple[int, float]:
        """Return (size, mtime)."""
        stats = path.stat()
        return stats.st_size, stats.st_mtime

    def calculate_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of normalized file content."""
        if not file_path.exists():
            return None
        try:
            content = file_path.read_text(encoding="utf-8")
            normalized = self.normalize_content(content)
            return hashlib.sha256(normalized).hexdigest()
        except Exception:
            # Fallback for binary or read errors
            try:
                return hashlib.sha256(file_path.read_bytes()).hexdigest()
            except Exception:
                return None

    def should_sync(self, file_path: Path) -> bool:
        """
        Decision engine: O(1) checks first, then O(N) hash.
        """
        if not file_path.exists():
            return False

        rel_path = self._get_rel_path(file_path)

        # 1. New file check
        if rel_path not in self.data["files"]:
            return True

        stored = self.data["files"][rel_path]
        try:
            curr_size, curr_mtime = self._get_file_stats(file_path)
        except (OSError, FileNotFoundError):
            return False

        # 2. O(1) Quick-Check (Size + Mtime)
        if stored.get("size") == curr_size and stored.get("mtime") == curr_mtime:
            return False  # Likely unchanged

        # 3. O(N) Deep-Check (Hash)
        curr_hash = self.calculate_hash(file_path)
        if not curr_hash:
            return False

        return curr_hash != stored.get("hash")

    def update_entry(self, file_path: Path, remote_id: Optional[str] = None):
        """Update manifest entry after successful sync."""
        if not file_path.exists():
            return

        rel_path = self._get_rel_path(file_path)
        curr_hash = self.calculate_hash(file_path)
        try:
            curr_size, curr_mtime = self._get_file_stats(file_path)
        except (OSError, FileNotFoundError):
            return

        with self.lock:
            self.data["files"][rel_path] = {
                "hash": curr_hash,
                "size": curr_size,
                "mtime": curr_mtime,
                "last_synced": datetime.now(timezone.utc).isoformat(),
                "remote_id": remote_id,
            }

    def remove_entry(self, file_path: Path):
        """Remove entry (e.g., file deleted)."""
        rel_path = self._get_rel_path(file_path)
        with self.lock:
            if rel_path in self.data["files"]:
                del self.data["files"][rel_path]

    def get_stale_files(self, current_files: List[Path]) -> List[str]:
        """Identify files in manifest that no longer exist on disk."""
        current_rel_paths = set(self._get_rel_path(p) for p in current_files)
        with self.lock:
            manifest_files = set(self.data["files"].keys())
            return list(manifest_files - current_rel_paths)
