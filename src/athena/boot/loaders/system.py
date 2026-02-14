import subprocess
import os
from athena.boot.constants import GREEN, RESET


class SystemLoader:
    @staticmethod
    def sync_ui():
        """Launch UI components and sync hardware state."""
        print(f"🔄 Syncing UI Components...")

        # Antigravity Launch with GPU flags
        cmd = [
            "open",
            "-a",
            "Antigravity",
            "--args",
            "--disable-gpu-driver-bug-workarounds",
            "--ignore-gpu-blacklist",
            "--enable-gpu-rasterization",
        ]

        try:
            # We use Popen to not block the boot sequence
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   {GREEN}✅ Antigravity Sync Initiated{RESET}")
        except Exception as e:
            print(f"   ⚠️  Failed to sync Antigravity: {e}")
