#!/usr/bin/env python3
"""
Protocol Heat Map Generator

Scans session logs to track protocol/skill/workflow usage frequency.
Produces a heat map for arsenal utilization analysis and pruning.

Usage:
    python3 protocol_heatmap.py               # Full analysis
    python3 protocol_heatmap.py --update      # Incremental update (non-blocking)

Output:
    .context/PROTOCOL_HEATMAP.md              # Human-readable heat map
    .context/protocol_heatmap.json            # Machine-readable data
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent.parent  # Project Athena root
SESSION_LOGS_DIR = ROOT / ".context" / "memories" / "session_logs"
ACTIVE_CONTEXT = ROOT / ".context" / "memory_bank" / "activeContext.md"
HEATMAP_MD = ROOT / ".context" / "PROTOCOL_HEATMAP.md"
HEATMAP_JSON = ROOT / ".context" / "protocol_heatmap.json"
PROTOCOLS_DIR = ROOT / ".agent" / "skills" / "protocols"
SKILLS_DIR = ROOT / ".agent" / "skills"
WORKFLOWS_DIR = ROOT / ".agent" / "workflows"

# ─── Patterns ────────────────────────────────────────────────────────

# Protocol references: P001, P528, Protocol 528, etc.
PROTOCOL_PATTERN = re.compile(r'\b[Pp](?:rotocol\s*)?(\d{1,4})\b')

# Skill references: backtick-wrapped or plain skill names
SKILL_NAMES = set()
if SKILLS_DIR.exists():
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith(('.', '_')) and item.name != 'protocols':
            SKILL_NAMES.add(item.name)

# Workflow references: /start, /end, /ultrastart, etc.
WORKFLOW_PATTERN = re.compile(r'(?:^|[\s`])/([a-z][a-z0-9-]+)\b')

# Law references: Law #0, Law #1, etc.
LAW_PATTERN = re.compile(r'\bLaw\s*#(\d+)\b', re.IGNORECASE)

# CANONICAL references: §123, CANONICAL §123
CANONICAL_PATTERN = re.compile(r'§(\d+)')


# ─── Scanner ─────────────────────────────────────────────────────────

def scan_file(filepath: Path) -> dict:
    """Scan a single file for protocol/skill/workflow references."""
    try:
        text = filepath.read_text(encoding='utf-8', errors='replace')
    except (OSError, UnicodeDecodeError):
        return {}

    refs = defaultdict(int)

    # Protocols
    for match in PROTOCOL_PATTERN.finditer(text):
        refs[f"P{match.group(1).zfill(3)}"] += 1

    # Skills
    for skill_name in SKILL_NAMES:
        # Match as whole word (case-insensitive)
        pattern = re.compile(rf'\b{re.escape(skill_name)}\b', re.IGNORECASE)
        count = len(pattern.findall(text))
        if count > 0:
            refs[f"skill:{skill_name}"] += count

    # Workflows
    for match in WORKFLOW_PATTERN.finditer(text):
        workflow_name = match.group(1)
        if (WORKFLOWS_DIR / f"{workflow_name}.md").exists():
            refs[f"workflow:/{workflow_name}"] += 1

    # Laws
    for match in LAW_PATTERN.finditer(text):
        refs[f"Law#{match.group(1)}"] += 1

    # CANONICAL sections
    for match in CANONICAL_PATTERN.finditer(text):
        refs[f"CANONICAL§{match.group(1)}"] += 1

    return dict(refs)


def scan_all_sessions() -> tuple[dict, int]:
    """Scan all session logs and activeContext."""
    total_refs = Counter()
    per_session = defaultdict(Counter)
    sessions_analyzed = 0

    # Scan session logs
    if SESSION_LOGS_DIR.exists():
        for log_file in sorted(SESSION_LOGS_DIR.glob("*.md")):
            refs = scan_file(log_file)
            if refs:
                session_name = log_file.stem
                per_session[session_name] = Counter(refs)
                total_refs.update(refs)
                sessions_analyzed += 1

    # Also scan activeContext for recent references
    if ACTIVE_CONTEXT.exists():
        refs = scan_file(ACTIVE_CONTEXT)
        if refs:
            total_refs.update(refs)

    return dict(total_refs), sessions_analyzed, dict(per_session)


# ─── Known Protocols Registry ────────────────────────────────────────

def get_known_protocols() -> set:
    """Get all protocol files in the protocols directory."""
    known = set()
    if PROTOCOLS_DIR.exists():
        for proto_file in PROTOCOLS_DIR.rglob("*.md"):
            # Extract protocol number from filename like 528-execution-enforcement.md
            match = re.match(r'^(\d+)', proto_file.name)
            if match:
                known.add(f"P{match.group(1).zfill(3)}")
    return known


# ─── Report Generator ────────────────────────────────────────────────

def generate_report(total_refs: dict, sessions_analyzed: int) -> str:
    """Generate the PROTOCOL_HEATMAP.md report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    known_protocols = get_known_protocols()

    # Separate by category
    protocols = {k: v for k, v in total_refs.items() if k.startswith('P') and not k.startswith('PROT')}
    skills = {k: v for k, v in total_refs.items() if k.startswith('skill:')}
    workflows = {k: v for k, v in total_refs.items() if k.startswith('workflow:')}
    laws = {k: v for k, v in total_refs.items() if k.startswith('Law#')}
    canonical = {k: v for k, v in total_refs.items() if k.startswith('CANONICAL')}

    total_unique = len(protocols) + len(skills) + len(workflows)
    total_known = len(known_protocols) + len(SKILL_NAMES)
    utilization = (total_unique / total_known * 100) if total_known > 0 else 0

    lines = [
        "# Protocol Heat Map (Auto-Generated)",
        "",
        f"> Last run: {now} | Sessions analyzed: {sessions_analyzed} | Arsenal utilization: {utilization:.0f}%",
        "",
        "---",
        "",
    ]

    # Hot Protocols
    if protocols:
        lines.append("## 🔥 Hot Protocols (Most Referenced)")
        lines.append("")
        lines.append("| Rank | Protocol | References |")
        lines.append("| :--- | :--- | :--- |")
        for i, (proto, count) in enumerate(sorted(protocols.items(), key=lambda x: -x[1])[:20], 1):
            lines.append(f"| {i} | {proto} | {count} |")
        lines.append("")

    # Hot Skills
    if skills:
        lines.append("## 🔥 Hot Skills (Most Referenced)")
        lines.append("")
        lines.append("| Rank | Skill | References |")
        lines.append("| :--- | :--- | :--- |")
        for i, (skill, count) in enumerate(sorted(skills.items(), key=lambda x: -x[1])[:15], 1):
            lines.append(f"| {i} | {skill.replace('skill:', '')} | {count} |")
        lines.append("")

    # Hot Workflows
    if workflows:
        lines.append("## 🔥 Hot Workflows (Most Referenced)")
        lines.append("")
        lines.append("| Rank | Workflow | References |")
        lines.append("| :--- | :--- | :--- |")
        for i, (wf, count) in enumerate(sorted(workflows.items(), key=lambda x: -x[1])[:10], 1):
            lines.append(f"| {i} | {wf.replace('workflow:', '')} | {count} |")
        lines.append("")

    # Laws
    if laws:
        lines.append("## ⚖️ Law References")
        lines.append("")
        lines.append("| Law | References |")
        lines.append("| :--- | :--- |")
        for law, count in sorted(laws.items(), key=lambda x: -x[1]):
            lines.append(f"| {law} | {count} |")
        lines.append("")

    # Cold Protocols (0 references in any session)
    cold = known_protocols - set(protocols.keys())
    if cold and sessions_analyzed >= 10:
        lines.append("## 🧊 Cold Protocols (0 references across sessions)")
        lines.append("")
        lines.append("> These protocols exist in the codebase but were never referenced in session logs.")
        lines.append("> Candidates for archival to `.agent/skills/protocols/_archived/`.")
        lines.append("")
        for proto in sorted(cold):
            lines.append(f"- {proto}")
        lines.append("")
        lines.append(f"**Recommendation**: Archive {len(cold)} cold protocols to recover ~{len(cold) * 0.5:.0f}K boot tokens.")
        lines.append("")

    # Cold Skills
    cold_skills = SKILL_NAMES - {k.replace('skill:', '') for k in skills}
    if cold_skills and sessions_analyzed >= 10:
        lines.append("## 🧊 Cold Skills (0 references across sessions)")
        lines.append("")
        for skill in sorted(cold_skills):
            lines.append(f"- {skill}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> Generated by `protocol_heatmap.py` on {now}")
    lines.append("")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    incremental = "--update" in sys.argv

    print(f"[heatmap] Scanning session logs in {SESSION_LOGS_DIR}...")
    total_refs, sessions_analyzed, per_session = scan_all_sessions()
    print(f"[heatmap] Analyzed {sessions_analyzed} sessions, found {len(total_refs)} unique references.")

    # Write JSON
    data = {
        "generated_at": datetime.now().isoformat(),
        "sessions_analyzed": sessions_analyzed,
        "total_references": total_refs,
    }
    HEATMAP_JSON.write_text(json.dumps(data, indent=2, sort_keys=True))
    print(f"[heatmap] JSON written to {HEATMAP_JSON}")

    # Write Markdown
    report = generate_report(total_refs, sessions_analyzed)
    HEATMAP_MD.write_text(report)
    print(f"[heatmap] Report written to {HEATMAP_MD}")

    if not incremental:
        print(f"\n{report}")


if __name__ == "__main__":
    main()
