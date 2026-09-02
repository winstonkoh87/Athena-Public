#!/usr/bin/env python3
"""
sync_agents_md.py — Auto-Recount Assets & Inject Counts Across All Surfaces

Reads canonical counts from the filesystem, updates .agent/config/CAPS.json,
and patches AGENTS.md, README.md, ARCHITECTURE.md, docs/ARCHITECTURE.md,
productContext.md, and KNOWLEDGE_GRAPH.md to terminate the manual audit treadmill.

Usage:
    python3 .agent/scripts/sync_agents_md.py [--dry-run]
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # .agent/scripts/ → Project Athena/
CAPS = ROOT / ".agent" / "config" / "CAPS.json"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
ARCH = ROOT / "ARCHITECTURE.md"
DOCS_ARCH = ROOT / "docs" / "ARCHITECTURE.md"
PRODUCT_CTX = ROOT / ".context" / "memory_bank" / "productContext.md"
KNOWLEDGE_GRAPH = ROOT / ".context" / "KNOWLEDGE_GRAPH.md"

DRY_RUN = "--dry-run" in sys.argv


def recount_assets() -> dict:
    """Natively recount all Athena filesystem assets."""
    counts = {}

    protocols_dir = ROOT / ".agent" / "skills" / "protocols"
    skills_dir = ROOT / ".agent" / "skills"
    archive_skills_dir = ROOT / ".agent" / "archive_skills"
    workflows_dir = ROOT / ".agent" / "workflows"
    domain_workflows_dir = workflows_dir / "_domain"
    scripts_dir = ROOT / ".agent" / "scripts"
    memories_dir = ROOT / ".context" / "memories"

    # 1. Count Protocols
    active_protos = 0
    archived_protos = 0
    categories = 0
    if protocols_dir.exists():
        for p in protocols_dir.rglob("*.md"):
            if p.name == "README.md":
                continue
            if "archive" in p.parts:
                archived_protos += 1
            else:
                active_protos += 1

        for p in protocols_dir.iterdir():
            if p.is_dir() and p.name != "archive":
                categories += 1

    counts["protocols_active"] = active_protos
    counts["protocols_archived"] = archived_protos
    counts["protocols_total"] = active_protos + archived_protos
    counts["protocols_categories"] = categories

    # 2. Count Skills
    active_skills = 0
    conditional_skills = 0
    if skills_dir.exists():
        for p in skills_dir.glob("*/SKILL.md"):
            active_skills += 1
            try:
                text = p.read_text(errors="ignore")
                if "context_trigger" in text:
                    conditional_skills += 1
            except Exception:
                pass

    archived_skills = 0
    if archive_skills_dir.exists():
        for p in archive_skills_dir.iterdir():
            if p.is_dir():
                archived_skills += 1

    counts["skills_active"] = active_skills
    counts["skills_archived"] = archived_skills
    counts["skills_conditional"] = conditional_skills

    # 3. Count Workflows
    root_wf = 0
    if workflows_dir.exists():
        for p in workflows_dir.glob("*.md"):
            root_wf += 1

    domain_wf = 0
    if domain_workflows_dir.exists():
        for p in domain_workflows_dir.glob("*.md"):
            domain_wf += 1

    counts["workflows_root"] = root_wf
    counts["workflows_domain"] = domain_wf
    counts["workflows_total"] = root_wf + domain_wf

    # 4. Count Scripts
    scripts_count = 0
    if scripts_dir.exists():
        for p in scripts_dir.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                scripts_count += 1
    counts["scripts"] = scripts_count

    # 5. Count Memories
    memories_count = 0
    if memories_dir.exists():
        for p in memories_dir.rglob("*"):
            if p.is_file():
                memories_count += 1
    counts["memories"] = memories_count

    # Session Logs
    session_logs = 0
    session_logs_dir = memories_dir / "session_logs"
    if session_logs_dir.exists():
        for p in session_logs_dir.rglob("*"):
            if p.is_file():
                session_logs += 1
    counts["session_logs"] = session_logs

    # Case Studies
    case_studies = 0
    case_studies_dir = memories_dir / "case_studies"
    if case_studies_dir.exists():
        for p in case_studies_dir.rglob("*"):
            if p.is_file():
                case_studies += 1
    counts["case_studies"] = case_studies

    # 6. Count source files & test files
    src_dir = ROOT / "src"
    tests_dir = ROOT / "tests"

    src_count = 0
    if src_dir.exists():
        for p in src_dir.rglob("*.py"):
            src_count += 1
    counts["source_sdk"] = src_count

    tests_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            tests_count += 1
    counts["source_tests"] = tests_count

    return counts


def update_caps_json(counts: dict) -> dict:
    """Load, update, and save CAPS.json. Returns the full dict."""
    with open(CAPS) as f:
        caps = json.load(f)

    caps["protocols"]["total"] = counts["protocols_total"]
    caps["protocols"]["active"] = counts["protocols_active"]
    caps["protocols"]["archived"] = counts["protocols_archived"]
    caps["protocols"]["categories"] = counts["protocols_categories"]

    caps["skills"]["active"] = counts["skills_active"]
    caps["skills"]["archived"] = counts["skills_archived"]
    caps["skills"]["conditional_count"] = counts["skills_conditional"]

    caps["workflows"]["root"] = counts["workflows_root"]
    caps["workflows"]["domain"] = counts["workflows_domain"]
    caps["workflows"]["total"] = counts["workflows_total"]

    caps["scripts"] = counts["scripts"]
    caps["memories"]["total_files"] = counts["memories"]
    caps["_generated"] = datetime.now().strftime("%Y-%m-%d")

    if not DRY_RUN:
        with open(CAPS, "w") as f:
            json.dump(caps, f, indent=2)
        print("  [UPDATE] CAPS.json updated with dynamic filesystem counts.")
    else:
        print("  [DRY-RUN] Would update CAPS.json.")

    return caps


def patch_agents(content: str, caps: dict) -> tuple[str, int]:
    """Patch AGENTS.md content."""
    patches = 0
    proto = caps["protocols"]
    skills = caps["skills"]
    wf = caps["workflows"]

    # Protocols active / archived / total categories
    old_proto = re.search(
        r"\((\d+) active \+ (\d+) archived = (\d+) total, across (\d+) categories\)",
        content,
    )
    if old_proto:
        old = old_proto.group(0)
        new = f"({proto['active']} active + {proto['archived']} archived = {proto['total']} total, across {proto['categories']} categories)"
        if old != new:
            content = content.replace(old, new, 1)
            patches += 1

    # Skills active / archived
    old_skills = re.search(r"\((\d+) active, (\d+) archived\).*SKILL_INDEX", content)
    if old_skills:
        old = old_skills.group(0)
        new = f"({skills['active']} active, {skills['archived']} archived)" + old[old.index(")")  + 1:]
        if old != new:
            content = content.replace(old_skills.group(0), new, 1)
            patches += 1

    # Workflows root / domain / total
    old_wf = re.search(r"\((\d+) root \+ (\d+) _domain = (\d+) total\)", content)
    if old_wf:
        old = old_wf.group(0)
        new = f"({wf['root']} root + {wf['domain']} _domain = {wf['total']} total)"
        if old != new:
            content = content.replace(old, new, 1)
            patches += 1

    # Non-conditional skills count
    old_cond = re.search(r"(\d+) skills without `context_trigger`", content)
    if old_cond:
        remaining = skills["active"] - skills["conditional_count"]
        old = old_cond.group(0)
        new = f"{remaining} skills without `context_trigger`"
        if old != new:
            content = content.replace(old, new, 1)
            patches += 1

    # Version lines
    ver = caps["version"]
    old_ver = re.search(r"\*\*System\*\*: v[\d.]+", content)
    if old_ver:
        old = old_ver.group(0)
        new = f"**System**: {ver['system']}"
        if old != new:
            content = content.replace(old, new, 1)
            patches += 1

    old_fw = re.search(r"\*\*Framework\*\*: v[\d.]+-\w+", content)
    if old_fw:
        old = old_fw.group(0)
        new = f"**Framework**: {ver['framework']}"
        if old != new:
            content = content.replace(old, new, 1)
            patches += 1

    return content, patches


def patch_readme(content: str, counts: dict, system_ver: str) -> tuple[str, int]:
    """Patch README.md content."""
    patches = 0

    # 1. Table values in "What This Is"
    proto_old = re.search(r"\|\s*\*\*Protocols\*\*\s*\|\s*(\d+)\s*\(\d+\s*active\s*\+\s*\d+\s*archived\)\s*\|", content)
    if proto_old:
        new_str = f"| **Protocols** | {counts['protocols_total']} ({counts['protocols_active']} active + {counts['protocols_archived']} archived) |"
        if proto_old.group(0) != new_str:
            content = content.replace(proto_old.group(0), new_str, 1)
            patches += 1

    skills_old = re.search(r"\|\s*\*\*Skills\*\*\s*\|\s*(\d+)\s*active\s*\(\d+\s*conditional\)\s*\|", content)
    if skills_old:
        new_str = f"| **Skills** | {counts['skills_active']} active ({counts['skills_conditional']} conditional) |"
        if skills_old.group(0) != new_str:
            content = content.replace(skills_old.group(0), new_str, 1)
            patches += 1

    wf_old = re.search(r"\|\s*\*\*Workflows\*\*\s*\|\s*(\d+)\s*\(\+\d+\s*domain\)\s*\|", content)
    if wf_old:
        new_str = f"| **Workflows** | {counts['workflows_root']} (+{counts['workflows_domain']} domain) |"
        if wf_old.group(0) != new_str:
            content = content.replace(wf_old.group(0), new_str, 1)
            patches += 1

    session_old = re.search(r"\|\s*\*\*Session Logs\*\*\s*\|\s*[\d,]+\s*\|", content)
    if session_old:
        new_str = f"| **Session Logs** | {counts['session_logs']:,} |"
        if session_old.group(0) != new_str:
            content = content.replace(session_old.group(0), new_str, 1)
            patches += 1

    mem_old = re.search(r"\|\s*\*\*Memory Files\*\*\s*\|\s*[\d,]+\s*\|", content)
    if mem_old:
        new_str = f"| **Memory Files** | {counts['memories']:,} |"
        if mem_old.group(0) != new_str:
            content = content.replace(mem_old.group(0), new_str, 1)
            patches += 1

    scripts_old = re.search(r"\|\s*\*\*Scripts\*\*\s*\|\s*(\d+)\s*\|", content)
    if scripts_old:
        new_str = f"| **Scripts** | {counts['scripts']} |"
        if scripts_old.group(0) != new_str:
            content = content.replace(scripts_old.group(0), new_str, 1)
            patches += 1

    # 2. Directory tree inline comments
    skills_comment = re.search(r"#\s*\d+\s*active\s*skills\s*\+\s*protocol\s*store\s*\(\d+\)", content)
    if skills_comment:
        new_str = f"#   {counts['skills_active']} active skills + protocol store ({counts['protocols_total']})"
        if skills_comment.group(0) != new_str:
            content = content.replace(skills_comment.group(0), new_str, 1)
            patches += 1

    cat_comment = re.search(r"#\s*\d+\s*categories\s*\(source\s*of\s*truth\)", content)
    if cat_comment:
        new_str = f"#     {counts['protocols_categories']} categories (source of truth)"
        if cat_comment.group(0) != new_str:
            content = content.replace(cat_comment.group(0), new_str, 1)
            patches += 1

    wf_comment = re.search(r"#\s*\d+\s*slash-command\s*workflows\s*\(\+\d+\s*domain\)", content)
    if wf_comment:
        new_str = f"#   {counts['workflows_root']} slash-command workflows (+{counts['workflows_domain']} domain)"
        if wf_comment.group(0) != new_str:
            content = content.replace(wf_comment.group(0), new_str, 1)
            patches += 1

    scripts_comment = re.search(r"#\s*\d+\s*automation\s*scripts", content)
    if scripts_comment:
        new_str = f"#   {counts['scripts']} automation scripts"
        if scripts_comment.group(0) != new_str:
            content = content.replace(scripts_comment.group(0), new_str, 1)
            patches += 1

    memories_comment = re.search(r"#\s*[\d,]+\s*memory\s*files", content)
    if memories_comment:
        new_str = f"#   {counts['memories']:,} memory files"
        if memories_comment.group(0) != new_str:
            content = content.replace(memories_comment.group(0), new_str, 1)
            patches += 1

    session_comment = re.search(r"#\s*[\d,]+\s*session\s*logs\s*\(active\s*\+\s*archived\)", content)
    if session_comment:
        new_str = f"#     {counts['session_logs']:,} session logs (active + archived)"
        if session_comment.group(0) != new_str:
            content = content.replace(session_comment.group(0), new_str, 1)
            patches += 1

    # 3. Cognitive Stack Diagram
    cs_skills = re.search(r"│\s*\d+\s*Skills\s*│", content)
    if cs_skills:
        new_str = f"│      {counts['skills_active']} Skills          │"
        if cs_skills.group(0) != new_str:
            content = content.replace(cs_skills.group(0), new_str, 1)
            patches += 1

    cs_protos = re.search(r"│\s*\d+\s*Protocols\s*│", content)
    if cs_protos:
        new_str = f"│    {counts['protocols_total']} Protocols        │"
        if cs_protos.group(0) != new_str:
            content = content.replace(cs_protos.group(0), new_str, 1)
            patches += 1

    cs_cats = re.search(r"│\s*\d+\s*categories\s*│", content)
    if cs_cats:
        new_str = f"│  {counts['protocols_categories']} categories          │"
        if cs_cats.group(0) != new_str:
            content = content.replace(cs_cats.group(0), new_str, 1)
            patches += 1

    # 4. Bottom Metrics Table
    # Pattern matching lines in the metrics section
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if "| Protocols (total) |" in line:
            new_line = f"| Protocols (total) | {counts['protocols_total']} ({counts['protocols_active']} active + {counts['protocols_archived']} archived) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Skills (active) |" in line:
            new_line = f"| Skills (active) | {counts['skills_active']} ({counts['skills_conditional']} conditional) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Workflows |" in line:
            new_line = f"| Workflows | {counts['workflows_root']} (+{counts['workflows_domain']} domain) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Automation Scripts |" in line:
            new_line = f"| Automation Scripts | {counts['scripts']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Session Logs |" in line:
            new_line = f"| Session Logs | {counts['session_logs']:,} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Case Studies |" in line:
            new_line = f"| Case Studies | {counts['case_studies']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Total Memory Files |" in line:
            new_line = f"| Total Memory Files | {counts['memories']:,} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Source Files (SDK) |" in line:
            new_line = f"| Source Files (SDK) | {counts['source_sdk']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Version |" in line:
            new_line = f"| Version | v{system_ver} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1

    content = "\n".join(lines)
    return content, patches


def patch_arch(content: str, counts: dict, system_ver: str) -> tuple[str, int]:
    """Patch ARCHITECTURE.md content."""
    patches = 0

    # 1. Version header
    old_ver = re.search(r">\s*\*\*Version\*\*:\s*[\d.]+", content)
    if old_ver:
        new_str = f"> **Version**: {system_ver}"
        if old_ver.group(0) != new_str:
            content = content.replace(old_ver.group(0), new_str, 1)
            patches += 1

    # 2. File tree comments
    skills_old = re.search(r"#\s*\d+\s*active\s*skills\s*\(\d+\s*with\s*context_trigger\)", content)
    if skills_old:
        new_str = f"#   {counts['skills_active']} active skills ({counts['skills_conditional']} with context_trigger)"
        if skills_old.group(0) != new_str:
            content = content.replace(skills_old.group(0), new_str, 1)
            patches += 1

    proto_old = re.search(r"#\s*\d+\s*active\s*\+\s*\d+\s*archived\s*=\s*\d+\s*total,\s*\d+\s*categories", content)
    if proto_old:
        new_str = f"#   {counts['protocols_active']} active + {counts['protocols_archived']} archived = {counts['protocols_total']} total, {counts['protocols_categories']} categories"
        if proto_old.group(0) != new_str:
            content = content.replace(proto_old.group(0), new_str, 1)
            patches += 1

    wf_old = re.search(r"#\s*\d+\s*root\s*\+\s*\d+\s*_domain\s*=\s*\d+\s*slash-command\s*workflows", content)
    if wf_old:
        new_str = f"#   {counts['workflows_root']} root + {counts['workflows_domain']} _domain = {counts['workflows_total']} slash-command workflows"
        if wf_old.group(0) != new_str:
            content = content.replace(wf_old.group(0), new_str, 1)
            patches += 1

    scripts_old = re.search(r"#\s*\d+\s*automation\s*scripts", content)
    if scripts_old:
        new_str = f"#   {counts['scripts']} automation scripts"
        if scripts_old.group(0) != new_str:
            content = content.replace(scripts_old.group(0), new_str, 1)
            patches += 1

    mems_old = re.search(r"#\s*[\d,]+\s*memory\s*files\s*\(session\s*logs\s*\+\s*case\s*studies\s*\+\s*profile\)", content)
    if mems_old:
        new_str = f"#   {counts['memories']:,} memory files (session logs + case studies + profile)"
        if mems_old.group(0) != new_str:
            content = content.replace(mems_old.group(0), new_str, 1)
            patches += 1

    cs_old = re.search(r"#\s*\d+\s*documented\s*patterns", content)
    if cs_old:
        new_str = f"#     {counts['case_studies']} documented patterns"
        if cs_old.group(0) != new_str:
            content = content.replace(cs_old.group(0), new_str, 1)
            patches += 1

    # 3. Inventory Section Table
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if "| Skills |" in line:
            new_line = f"| Skills | {counts['skills_active']} active ({counts['skills_archived']} archived) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Protocols |" in line:
            new_line = f"| Protocols | {counts['protocols_active']} active ({counts['protocols_archived']} archived; {counts['protocols_total']} total) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Workflows |" in line:
            new_line = f"| Workflows | {counts['workflows_total']} ({counts['workflows_root']} root + {counts['workflows_domain']} _domain/) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Automation Scripts |" in line:
            new_line = f"| Automation Scripts | {counts['scripts']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Case Studies |" in line:
            new_line = f"| Case Studies | {counts['case_studies']} (15 domains, 7 archived) |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Session Logs |" in line:
            new_line = f"| Session Logs | {counts['session_logs']:,} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Total Memory Files |" in line:
            new_line = f"| Total Memory Files | {counts['memories']:,} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Source Files (SDK) |" in line:
            new_line = f"| Source Files (SDK) | {counts['source_sdk']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1
        elif "| Test Files |" in line:
            new_line = f"| Test Files | {counts['source_tests']} |"
            if line != new_line:
                lines[idx] = new_line
                patches += 1

    # 4. Node Legend
    legend_skills = re.search(r"\|\s*⚔️ SKILLS\s*\|\s*\d+\s*active\s*Protocols\s*\(\d+\s*total\),\s*\d+\s*active\s*Skills\s*\|", content)
    if legend_skills:
        new_str = f"| ⚔️ SKILLS | {counts['protocols_active']} active Protocols ({counts['protocols_total']} total), {counts['skills_active']} active Skills |"
        if legend_skills.group(0) != new_str:
            content = content.replace(legend_skills.group(0), new_str, 1)
            patches += 1

    legend_tools = re.search(r"\|\s*🔧 TOOLS\s*\|\s*\d+\s*Scripts,\s*Automation\s*\|", content)
    if legend_tools:
        new_str = f"| 🔧 TOOLS | {counts['scripts']} Scripts, Automation |"
        if legend_tools.group(0) != new_str:
            content = content.replace(legend_tools.group(0), new_str, 1)
            patches += 1

    # 5. Workflow index index line
    wf_idx = re.search(r"## 4\. Workflow Index\s*\(\d+\s*registered:\s*\d+\s*root\s*\+\s*\d+\s*`_domain/`\)", content)
    if wf_idx:
        new_str = f"## 4. Workflow Index ({counts['workflows_total']} registered: {counts['workflows_root']} root + {counts['workflows_domain']} `_domain/` SGT)"
        # Note: replace carefully
        content = content.replace(wf_idx.group(0), f"## 4. Workflow Index ({counts['workflows_total']} registered: {counts['workflows_root']} root + {counts['workflows_domain']} `_domain/`)", 1)
        patches += 1

    wf_state = re.search(r"reflect\s*the\s*\d+-workflow\s*state", content)
    if wf_state:
        new_str = f"reflect the {counts['workflows_total']}-workflow state"
        content = content.replace(wf_state.group(0), new_str, 1)
        patches += 1

    content = "\n".join(lines)
    return content, patches


def patch_docs_arch(content: str, counts: dict, system_ver: str) -> tuple[str, int]:
    """Patch docs/ARCHITECTURE.md content."""
    patches = 0

    # Version header
    old_ver = re.search(r">\s*\*\*System Version\*\*:\s*v[\d.]+", content)
    if old_ver:
        new_str = f"> **System Version**: v{system_ver}"
        if old_ver.group(0) != new_str:
            content = content.replace(old_ver.group(0), new_str, 1)
            patches += 1

    # File tree inline comments
    cs_old = re.search(r"#\s*\d+\+\s*documented\s*patterns", content)
    if cs_old:
        new_str = f"# {counts['case_studies']}+ documented patterns"
        if cs_old.group(0) != new_str:
            content = content.replace(cs_old.group(0), new_str, 1)
            patches += 1

    proto_old = re.search(r"#\s*\d+\+\s*modular\s*skill\s*files", content)
    if proto_old:
        new_str = f"# {counts['protocols_total']}+ modular skill files"
        if proto_old.group(0) != new_str:
            content = content.replace(proto_old.group(0), new_str, 1)
            patches += 1

    wf_old = re.search(r"#\s*\d+\s*slash\s*commands", content)
    if wf_old:
        new_str = f"# {counts['workflows_total']} slash commands"
        if wf_old.group(0) != new_str:
            content = content.replace(wf_old.group(0), new_str, 1)
            patches += 1

    scripts_old = re.search(r"#\s*\d+\+\s*Python\s*automation\s*scripts", content)
    if scripts_old:
        new_str = f"# {counts['scripts']}+ Python automation scripts"
        if scripts_old.group(0) != new_str:
            content = content.replace(scripts_old.group(0), new_str, 1)
            patches += 1

    return content, patches


def patch_product_ctx(content: str, counts: dict) -> tuple[str, int]:
    """Patch productContext.md content."""
    patches = 0
    scale = re.search(r"-\s*\*\*Scale\*\*:\s*\d+\+\s*protocols,\s*\d+\+\s*workflows,\s*[\d,]+\+\s*sessions,\s*\d+\+\s*case\s*studies\.", content)
    if scale:
        new_str = f"- **Scale**: {counts['protocols_active']}+ protocols, {counts['workflows_total']}+ workflows, {counts['session_logs']:,}+ sessions, {counts['case_studies']}+ case studies."
        if scale.group(0) != new_str:
            content = content.replace(scale.group(0), new_str, 1)
            patches += 1
    return content, patches


def patch_kg(content: str, counts: dict) -> tuple[str, int]:
    """Patch KNOWLEDGE_GRAPH.md content."""
    patches = 0

    # 1. Inventory header
    inv_old = re.search(r">\s*\*\*Inventory\s*\([^)]*\)\*\*:\s*\d+\s*active\s*protocols\s*\(\d+\s*total\s*incl\.\s*\d+\s*archived\),\s*\d+\s*active\s*skills\s*\(\d+\s*total\s*incl\.\s*\d+\s*archived\),\s*\d+\s*workflows\s*\(\d+\s*root\s*\+\s*\d+\s*_domain\),\s*\d+\s*scripts,\s*[\d,]+\s*memory\s*files\.", content)
    if inv_old:
        new_str = f"> **Inventory ({datetime.now().strftime('%Y-%m-%d')})**: {counts['protocols_active']} active protocols ({counts['protocols_total']} total incl. {counts['protocols_archived']} archived), {counts['skills_active']} active skills ({counts['skills_active'] + counts['skills_archived']} total incl. {counts['skills_archived']} archived), {counts['workflows_total']} workflows ({counts['workflows_root']} root + {counts['workflows_domain']} _domain), {counts['scripts']} scripts, {counts['memories']:,} memory files."
        if inv_old.group(0) != new_str:
            content = content.replace(inv_old.group(0), new_str, 1)
            patches += 1

    # 2. Mermaid node definitions
    skills_node = re.search(r"SKILLS\s*\[\"⚔️ SKILLS\s*&\s*PROTOCOLS\s*\(\d+\s*active\s*/\s*\d+\s*total\)\"\]", content)
    if skills_node:
        new_str = f"SKILLS[\"⚔️ SKILLS & PROTOCOLS ({counts['protocols_active']} active / {counts['protocols_total']} total)\"]"
        if skills_node.group(0) != new_str:
            content = content.replace(skills_node.group(0), new_str, 1)
            patches += 1

    cs_node = re.search(r"CS\s*\[\d+\s*Case\s*Studies\]", content)
    if cs_node:
        new_str = f"CS [{counts['case_studies']} Case Studies]"
        if cs_node.group(0) != new_str:
            content = content.replace(cs_node.group(0), new_str, 1)
            patches += 1

    sl_node = re.search(r"SL\s*\[[\d,]+\s*Memory\s*Files\]", content)
    if sl_node:
        new_str = f"SL [{counts['memories']:,} Memory Files]"
        if sl_node.group(0) != new_str:
            content = content.replace(sl_node.group(0), new_str, 1)
            patches += 1

    tools_node = re.search(r"TOOLS\s*\[\"🔧 TOOLING\s*\(\d+\s*scripts\)\"\]", content)
    if tools_node:
        new_str = f"TOOLS[\"🔧 TOOLING ({counts['scripts']} scripts)\"]"
        if tools_node.group(0) != new_str:
            content = content.replace(tools_node.group(0), new_str, 1)
            patches += 1

    sk_node = re.search(r"SK\s*\[\d+\s*Compound\s*Skills\]", content)
    if sk_node:
        new_str = f"SK [{counts['skills_active']} Compound Skills]"
        if sk_node.group(0) != new_str:
            content = content.replace(sk_node.group(0), new_str, 1)
            patches += 1

    wf_node = re.search(r"WF2\s*\[\d+\s*Workflows\]", content)
    if wf_node:
        new_str = f"WF2 [{counts['workflows_total']} Workflows]"
        if wf_node.group(0) != new_str:
            content = content.replace(wf_node.group(0), new_str, 1)
            patches += 1

    # 3. Headers of Inventory Sections
    proto_head = re.search(r"## 2\. Protocol Inventory\s*\(\d+\s*active\s*/\s*\d+\s*total,\s*\d+\s*categories\)", content)
    if proto_head:
        new_str = f"## 2. Protocol Inventory ({counts['protocols_active']} active / {counts['protocols_total']} total, {counts['protocols_categories']} categories)"
        if proto_head.group(0) != new_str:
            content = content.replace(proto_head.group(0), new_str, 1)
            patches += 1

    skills_head = re.search(r"## 3\. Compound Skills\s*\(\d+\s*active\s*/\s*\d+\s*total\s*incl\.\s*\d+\s*archived\)", content)
    if skills_head:
        new_str = f"## 3. Compound Skills ({counts['skills_active']} active / {counts['skills_active'] + counts['skills_archived']} total incl. {counts['skills_archived']} archived)"
        if skills_head.group(0) != new_str:
            content = content.replace(skills_head.group(0), new_str, 1)
            patches += 1

    skills_desc = re.search(r"current\s*\d+\s*active\s*skills", content)
    if skills_desc:
        new_str = f"current {counts['skills_active']} active skills"
        if skills_desc.group(0) != new_str:
            content = content.replace(skills_desc.group(0), new_str, 1)
            patches += 1

    wf_head = re.search(r"## 4\. Workflow Index\s*\(\d+\s*registered:\s*\d+\s*root\s*\+\s*\d+\s*`_domain/`\)", content)
    if wf_head:
        new_str = f"## 4. Workflow Index ({counts['workflows_total']} registered: {counts['workflows_root']} root + {counts['workflows_domain']} `_domain/` SGT)"
        content = content.replace(wf_head.group(0), f"## 4. Workflow Index ({counts['workflows_total']} registered: {counts['workflows_root']} root + {counts['workflows_domain']} `_domain/`)", 1)
        patches += 1

    wf_desc = re.search(r"reflect\s*the\s*\d+-workflow\s*state", content)
    if wf_desc:
        new_str = f"reflect the {counts['workflows_total']}-workflow state"
        content = content.replace(wf_desc.group(0), new_str, 1)
        patches += 1

    # 4. Node Legend
    legend_skills = re.search(r"\|\s*⚔️ SKILLS\s*\|\s*\d+\s*active\s*Protocols\s*\(\d+\s*total\),\s*\d+\s*active\s*Skills\s*\|", content)
    if legend_skills:
        new_str = f"| ⚔️ SKILLS | {counts['protocols_active']} active Protocols ({counts['protocols_total']} total), {counts['skills_active']} active Skills |"
        if legend_skills.group(0) != new_str:
            content = content.replace(legend_skills.group(0), new_str, 1)
            patches += 1

    legend_tools = re.search(r"\|\s*🔧 TOOLS\s*\|\s*\d+\s*Scripts,\s*Automation\s*\|", content)
    if legend_tools:
        new_str = f"| 🔧 TOOLS | {counts['scripts']} Scripts, Automation |"
        if legend_tools.group(0) != new_str:
            content = content.replace(legend_tools.group(0), new_str, 1)
            patches += 1

    return content, patches


def main():
    if not CAPS.exists():
        print(f"ERROR: {CAPS} not found")
        sys.exit(1)

    print("🤖 Recounting workspace assets...")
    counts = recount_assets()

    # Load version context from existing CAPS
    with open(CAPS) as f:
        caps_temp = json.load(f)
    system_ver = caps_temp.get("version", {}).get("system", "9.9.0")

    print(f"File counts: active_protocols={counts['protocols_active']}, total={counts['protocols_total']}, skills={counts['skills_active']}, workflows={counts['workflows_total']}, scripts={counts['scripts']}, memories={counts['memories']}")

    caps = update_caps_json(counts)

    # 1. Patch AGENTS.md
    if AGENTS.exists():
        content = AGENTS.read_text(encoding="utf-8")
        new_content, patches = patch_agents(content, caps)
        if patches > 0:
            if not DRY_RUN:
                AGENTS.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] AGENTS.md: {patches} update(s) applied.")
        else:
            print("  AGENTS.md is already up to date.")

    # 2. Patch README.md
    if README.exists():
        content = README.read_text(encoding="utf-8")
        new_content, patches = patch_readme(content, counts, system_ver)
        if patches > 0:
            if not DRY_RUN:
                README.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] README.md: {patches} update(s) applied.")
        else:
            print("  README.md is already up to date.")

    # 3. Patch ARCHITECTURE.md (root)
    if ARCH.exists():
        content = ARCH.read_text(encoding="utf-8")
        new_content, patches = patch_arch(content, counts, system_ver)
        if patches > 0:
            if not DRY_RUN:
                ARCH.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] ARCHITECTURE.md: {patches} update(s) applied.")
        else:
            print("  ARCHITECTURE.md is already up to date.")

    # 4. Patch docs/ARCHITECTURE.md
    if DOCS_ARCH.exists():
        content = DOCS_ARCH.read_text(encoding="utf-8")
        new_content, patches = patch_docs_arch(content, counts, system_ver)
        if patches > 0:
            if not DRY_RUN:
                DOCS_ARCH.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] docs/ARCHITECTURE.md: {patches} update(s) applied.")
        else:
            print("  docs/ARCHITECTURE.md is already up to date.")

    # 5. Patch productContext.md
    if PRODUCT_CTX.exists():
        content = PRODUCT_CTX.read_text(encoding="utf-8")
        new_content, patches = patch_product_ctx(content, counts)
        if patches > 0:
            if not DRY_RUN:
                PRODUCT_CTX.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] productContext.md: {patches} update(s) applied.")
        else:
            print("  productContext.md is already up to date.")

    # 6. Patch KNOWLEDGE_GRAPH.md
    if KNOWLEDGE_GRAPH.exists():
        content = KNOWLEDGE_GRAPH.read_text(encoding="utf-8")
        new_content, patches = patch_kg(content, counts)
        if patches > 0:
            if not DRY_RUN:
                KNOWLEDGE_GRAPH.write_text(new_content, encoding="utf-8")
            print(f"  [PATCH] KNOWLEDGE_GRAPH.md: {patches} update(s) applied.")
        else:
            print("  KNOWLEDGE_GRAPH.md is already up to date.")

    print("\n✅ Count automation completed successfully.")


if __name__ == "__main__":
    main()
