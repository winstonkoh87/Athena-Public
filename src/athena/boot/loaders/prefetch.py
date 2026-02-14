import json
from pathlib import Path
from athena.boot.constants import PROJECT_ROOT, DIM, RESET


class PrefetchLoader:
    @staticmethod
    def prefetch_hot_files():
        """Reads files from hot_manifest.json to prime them in the context."""
        manifest_path = PROJECT_ROOT / ".context" / "cache" / "hot_manifest.json"
        if not manifest_path.exists():
            return

        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            files = manifest.get("files", [])
            print(f"\n{DIM}🔥 Prefetching {len(files)} hot files...{RESET}")

            for f_info in files:
                f_path = PROJECT_ROOT / f_info["path"]
                if f_path.exists():
                    # Just read it to bring it into the "conscious" memory of the system
                    # In a real environment, this ensures the content is ready for the agent.
                    f_path.read_text(encoding="utf-8")
                    # print(f"   {DIM}• {f_info['name']}{RESET}")

        except Exception as e:
            # print(f"{DIM}⚠️ Prefetch error: {e}{RESET}")
            pass
