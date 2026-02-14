import os
import sys
import json
import signal
from datetime import datetime
from athena.boot.constants import (
    PROJECT_ROOT, SAFE_BOOT_SCRIPT, BOOT_TIMEOUT_SECONDS,
    RED, YELLOW, BOLD, DIM, RESET
)
from athena.boot.loaders.ui import UILoader

class StateLoader:
    @staticmethod
    def boot_timeout_handler(signum, frame):
        """Handle boot timeout - trigger safe mode and dump forensics."""
        print(f"\n{RED}{'=' * 60}{RESET}")
        print(f"{RED}{BOLD}⚠️  BOOT TIMEOUT - {BOOT_TIMEOUT_SECONDS}s EXCEEDED{RESET}")
        print(f"{RED}{'=' * 60}{RESET}")
        
        # Dump crash report
        try:
            crash_file = PROJECT_ROOT / ".athena" / "crash_reports" / f"boot_timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            crash_file.parent.mkdir(parents=True, exist_ok=True)
            report = {
                "timestamp": datetime.now().isoformat(),
                "reason": "BOOT_TIMEOUT_SIGALRM",
                "timeout_seconds": BOOT_TIMEOUT_SECONDS,
                "pid": os.getpid()
            }
            crash_file.write_text(json.dumps(report, indent=2))
            print(f"{YELLOW}Forensics dumped to: .athena/crash_reports/{RESET}")
        except Exception as e:
            print(f"{YELLOW}Failed to dump forensics: {e}{RESET}")

        print(f"\n{YELLOW}Triggering safe mode fallback...{RESET}")
        
        if SAFE_BOOT_SCRIPT.exists():
            print(f"{DIM}Run: ./safe_boot.sh{RESET}")
        else:
            print(f"{DIM}Manual recovery: Load Core_Identity.md directly{RESET}")
        
        sys.exit(1)

    @staticmethod
    def check_prior_crashes():
        """Check for prior crash reports."""
        crash_dir = PROJECT_ROOT / ".athena" / "crash_reports"
        if not crash_dir.exists():
            return
        
        crash_files = sorted(crash_dir.glob("*.json"), reverse=True)
        if crash_files:
            latest = crash_files[0]
            try:
                report = json.loads(latest.read_text())
                timestamp = report.get("timestamp", "unknown")
                reason = report.get("reason", "unknown")
                print(f"\n{YELLOW}{'=' * 60}{RESET}")
                print(f"{YELLOW}⚠️  RECOVERED FROM PRIOR CRASH{RESET}")
                print(f"{YELLOW}{'=' * 60}{RESET}")
                print(f"   Timestamp: {timestamp}")
                print(f"   Reason: {reason}")
                print(f"   Log: .athena/crash_reports/{latest.name}")
                print(f"{YELLOW}{'=' * 60}{RESET}\n")
            except Exception:
                pass

    @staticmethod
    def check_canary_overdue():
        """Check if DEAD_MAN_SWITCH audit is overdue."""
        canary_file = PROJECT_ROOT / "DEAD_MAN_SWITCH.md"
        if not canary_file.exists():
            return
        
        try:
            import re
            content = canary_file.read_text()
            match = re.search(r'\*\*Next Required Audit\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})', content)
            if match:
                audit_date_str = match.group(1)
                audit_date = datetime.strptime(audit_date_str, "%Y-%m-%d")
                today = datetime.now()
                
                if today > audit_date:
                    days_overdue = (today - audit_date).days
                    print(f"\n{RED}{'=' * 60}{RESET}")
                    print(f"{RED}🚨 DEAD MAN SWITCH: AUDIT OVERDUE BY {days_overdue} DAYS{RESET}")
                    print(f"{RED}{'=' * 60}{RESET}")
                    
                    overdue_flag = PROJECT_ROOT / ".athena" / "overdue_audit.flag"
                    overdue_flag.parent.mkdir(parents=True, exist_ok=True)
                    overdue_flag.write_text(f"overdue_since={audit_date_str}\ndays_overdue={days_overdue}\n")
        except Exception:
            pass

    @classmethod
    def enable_watchdog(cls):
        try:
            signal.signal(signal.SIGALRM, cls.boot_timeout_handler)
            signal.alarm(BOOT_TIMEOUT_SECONDS)
        except (AttributeError, ValueError):
            pass

    @staticmethod
    def disable_watchdog():
        try:
            signal.alarm(0)
        except (AttributeError, ValueError):
            pass
