import sys
import os
import re
import urllib.parse
from pathlib import Path

# Add project root and src/ to sys.path
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT_DIR / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from athena.core.config import PROJECT_ROOT

WORKSPACE = PROJECT_ROOT
WORKSPACE_URI = f"file://{WORKSPACE}"


def build_global_map():
    p_map = {}
    id_map = {}
    for root, _, files in os.walk(WORKSPACE):
        if any(x in root for x in [".git", "node_modules", "chroma_db"]):
            continue
        for f in files:
            if f.endswith(".md"):
                rel_path = Path(root).relative_to(WORKSPACE) / f
                if f not in p_map:
                    p_map[f] = rel_path
                match = re.search(r"([0-9]+)", f)
                if match:
                    if match.group(1) not in id_map or ".agent" in str(rel_path):
                        id_map[match.group(1)] = rel_path
    return p_map, id_map


def repair():
    p_map, id_map = build_global_map()
    total = 0

    overrides = {
        "197-consigliere-mode.md": "329-consiglieri-protocol.md",
        "197-consigliere-protocol.md": "329-consiglieri-protocol.md",
        "114-missing-baseline.md": "113-missing-baseline-model.md",
        "65-arbitrage-mechanics.md": "65-arbitrage-formula.md",
        "311-social-audit-defense.md": "98-social-audit-defense.md",
        "CS044_ILP_Trust_Arbitrage.md": "CS-044-ilp-trust-arbitrage.md",
        "Case_Tutor_Distribution_Trap.md": "CS-118-tutor-distribution-trap.md",
        "Case_Jeremy_Dignity_Trap.md": "CS-125-jeremy-ryan-case.md",
        "User_Profile.md": "User_Profile_Core.md",
        "Operating_Principles.md": "Operating_Principles.md",
        "LAW1_RUIN.md": "001-law-of-ruin.md",
        "SDR_CALCULATOR.md": "124-sdr-calculator.md",
        "CS-TBT-outcome-economy-tuition.md": "CS-273-outcome-economy-tuition.md",
        "LinkedIn_Publication_Strategy.md": "001-linkedin-strategy.md",
        "CS-197-bmad-scale-adaptive-framework.md": "CS-197-bmad-scale-adaptive-framework.md",
        "CS-198-anthropic-doc-coauthoring.md": "CS-198-anthropic-doc-coauthoring.md",
        "DIAG-001-knowledge-action-gap.md": "002-baseline-check.md",  # Fallback
        "DIAG-002-baseline-check.md": "002-baseline-check.md",
        "DIAG-003-frame-collision.md": "003-frame-collision.md",
        "DIAG-004-chat-forensics.md": "004-chat-forensics.md",
    }

    for root, _, files in os.walk(WORKSPACE):
        if any(x in root for x in [".git", "node_modules", "chroma_db"]):
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            path = Path(root) / f
            try:
                content = path.read_text()
            except:
                continue

            orig = content

            # SANITY CLEANUP: Remove double-nesting
            double_pat = f"{WORKSPACE_URI}/{WORKSPACE_URI}/"
            content = content.replace(double_pat, f"{WORKSPACE_URI}/")

            # FIX WRONG PATHS: /Desktop/Athena/ -> /Desktop/Project Athena/
            # Note: Legacies might still exist
            content = content.replace(
                "file:///Users/[AUTHOR]/Desktop/Athena/", f"{WORKSPACE_URI}/"
            )
            content = content.replace(
                "file:///Users/[AUTHOR]/Desktop/Project Athena/", f"{WORKSPACE_URI}/"
            )
            content = content.replace(f"file://{PROJECT_ROOT}/", f"{WORKSPACE_URI}/")

            # 1. file:/// links
            def subst_file(m):
                fname_raw = m.group(1)
                fname = urllib.parse.unquote(fname_raw).split("/")[-1]
                target = overrides.get(fname, fname)

                found_path = p_map.get(target)
                if not found_path:
                    id_m = re.search(r"([0-9]+)", target)
                    if id_m and id_m.group(1) in id_map:
                        found_path = id_map[id_m.group(1)]

                if found_path:
                    return f"{WORKSPACE_URI}/{found_path}"
                return m.group(0)

            pattern_file = r"file:///.*?/([^/\]\)\s]*?\.md)"
            content = re.sub(pattern_file, subst_file, content)

            # 2. Markdown links
            def subst_md(m):
                prefix = m.group(1)
                fname_raw = m.group(2)
                suffix = m.group(3)

                fname = urllib.parse.unquote(fname_raw).split("/")[-1]
                if fname == "...":
                    return m.group(0)  # Skip placeholders

                target = overrides.get(fname, fname)

                found_path = p_map.get(target)
                if not found_path:
                    id_m = re.search(r"([0-9]+)", target)
                    if id_m and id_m.group(1) in id_map:
                        found_path = id_map[id_m.group(1)]

                if found_path:
                    return f"{prefix}{WORKSPACE_URI}/{found_path}{suffix}"
                return m.group(0)

            pattern_md = r"(?<!file:///)(?:(\[.*?\]\(|\[\[))([^\]\)\s]*?\.md)([\)\]]|$)"
            content = re.sub(pattern_md, subst_md, content)

            if content != orig:
                path.write_text(content)
                total += 1

    print(f"Total files fixed: {total}")


if __name__ == "__main__":
    repair()
