#!/usr/bin/env python3
"""
harness_score.py — Athena Harness Capability & Enforcement Auditor
==================================================================

Computes the live Athena Harness Score (0-100) by probing actual repo state
and measuring both Designed Capability (C) and Enforcement Coefficient (E):

    Effective Score = C x E

Usage:
    python3 .agent/scripts/harness_score.py            # Run live probe and print summary
    python3 .agent/scripts/harness_score.py --json     # Output machine-readable JSON
    python3 .agent/scripts/harness_score.py --check    # Exit 1 if score < threshold
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / ".agent" / "config" / "harness_scorecard.yaml"
TELEMETRY_PATH = REPO_ROOT / ".context" / "telemetry" / "harness_score.jsonl"
CLAUDE_SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
AGENT_SETTINGS_PATH = REPO_ROOT / ".agent" / "config" / "settings.json"
CI_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def load_yaml_fallback(path: Path) -> dict:
    """Load YAML with PyYAML or minimal fallback parser."""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    # Simple parser for the specific structure of harness_scorecard.yaml
    data = {"pillars": {}}
    current_pillar = None
    current_sub = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.rstrip()
            if not line_str or line_str.strip().startswith("#"):
                continue
            m_p = re.match(r"^\s{2}(P\d+):", line_str)
            if m_p:
                current_pillar = m_p.group(1)
                data["pillars"][current_pillar] = {"sub_variables": {}}
                current_sub = None
                continue
            m_p_name = re.match(r'^\s{4}name:\s*"([^"]+)"', line_str)
            if m_p_name and current_pillar and not current_sub:
                data["pillars"][current_pillar]["name"] = m_p_name.group(1)
                continue
            m_p_w = re.match(r"^\s{4}weight:\s*(\d+)", line_str)
            if m_p_w and current_pillar and not current_sub:
                data["pillars"][current_pillar]["weight"] = int(m_p_w.group(1))
                continue
            m_sub = re.match(r"^\s{6}(\d+\.\d+):", line_str)
            if m_sub and current_pillar:
                current_sub = m_sub.group(1)
                data["pillars"][current_pillar]["sub_variables"][current_sub] = {}
                continue
            if current_pillar and current_sub:
                sub_dict = data["pillars"][current_pillar]["sub_variables"][current_sub]
                m_s_name = re.match(r'^\s{8}name:\s*"([^"]+)"', line_str)
                if m_s_name:
                    sub_dict["name"] = m_s_name.group(1)
                m_s_w = re.match(r"^\s{8}w:\s*([\d\.]+)", line_str)
                if m_s_w:
                    sub_dict["w"] = float(m_s_w.group(1))
                m_s_c = re.match(r"^\s{8}C:\s*([\d\.]+)", line_str)
                if m_s_c:
                    sub_dict["C"] = float(m_s_c.group(1))
                m_s_p = re.match(r'^\s{8}probe:\s*"([^"]+)"', line_str)
                if m_s_p:
                    sub_dict["probe"] = m_s_p.group(1)
    return data


def probe_git_hooks() -> float:
    try:
        res = subprocess.run(
            ["git", "config", "core.hooksPath"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout.strip() == ".agent/hooks":
            return 0.85
    except Exception:
        pass
    return 0.50


def probe_claude_settings() -> dict:
    if not CLAUDE_SETTINGS_PATH.exists():
        return {}
    try:
        with open(CLAUDE_SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def probe_ci_hard_fail() -> float:
    if not CI_WORKFLOW_PATH.exists():
        return 0.50
    try:
        content = CI_WORKFLOW_PATH.read_text(encoding="utf-8")
        if '|| echo "::warning::' in content:
            return 0.65
        return 0.95
    except Exception:
        return 0.50


def probe_reranker() -> float:
    try:
        import sentence_transformers  # noqa: F401
        return 0.85
    except ImportError:
        return 0.50


def run_probe(probe_name: str, claude_settings: dict) -> float:
    hooks = claude_settings.get("hooks", {})
    
    if probe_name == "git_hooks_path":
        return probe_git_hooks()
    
    elif probe_name == "session_lifecycle":
        has_start = "SessionStart" in hooks
        has_end = "SessionEnd" in hooks
        if has_start and has_end:
            return 0.80
        elif has_start or has_end:
            return 0.60
        return 0.20

    elif probe_name == "input_gates":
        if "UserPromptSubmit" in hooks:
            return 0.60  # text injection
        return 0.10

    elif probe_name == "output_stop_gate":
        if "Stop" in hooks or "SubagentStop" in hooks:
            return 0.85
        return 0.05

    elif probe_name == "ci_hard_fail":
        return probe_ci_hard_fail()

    elif probe_name == "pre_tool_secrets":
        if "PreToolUse" in hooks:
            return 0.90
        if AGENT_SETTINGS_PATH.exists():
            try:
                agent_settings = json.loads(AGENT_SETTINGS_PATH.read_text(encoding="utf-8"))
                if "PreToolUse" in agent_settings.get("hooks", {}):
                    return 0.25  # Registered in wrong file
            except Exception:
                pass
        return 0.05

    elif probe_name == "loop_middleware":
        if "PostToolUse" in hooks:
            return 0.70
        return 0.10

    elif probe_name == "oracle_protection":
        if (REPO_ROOT / ".agent" / "hooks" / "pre-commit").exists():
            return 0.60
        return 0.20

    elif probe_name == "tiered_loading":
        # Actual probe: check if CANONICAL.md and CANONICAL_TIER2.md exist
        has_t1 = (REPO_ROOT / ".context" / "CANONICAL.md").exists()
        has_t2 = (REPO_ROOT / ".context" / "CANONICAL_TIER2.md").exists()
        if has_t1 and has_t2:
            return 0.90
        elif has_t1:
            return 0.65
        return 0.30

    elif probe_name == "skill_triggers":
        # Actual probe: check SKILL_INDEX.md exists and is non-trivial
        idx = REPO_ROOT / ".agent" / "skills" / "SKILL_INDEX.md"
        if idx.exists() and idx.stat().st_size > 500:
            return 0.70
        return 0.30

    elif probe_name == "durable_session":
        # Actual probe: check activeContext.md exists and has checkpoint blocks
        ac = REPO_ROOT / ".context" / "memory_bank" / "activeContext.md"
        if ac.exists():
            content = ac.read_text(encoding="utf-8", errors="ignore")
            if "!checkpoint" in content:
                return 0.80
            return 0.50
        return 0.20

    elif probe_name == "reranker_runtime":
        return probe_reranker()

    elif probe_name == "structured_handoff":
        return 0.50  # STATIC ESTIMATE — no instrumentation yet

    elif probe_name == "compaction_tools":
        # Actual probe: check context-compactor skill exists
        cc = REPO_ROOT / ".agent" / "skills" / "context-compactor" / "SKILL.md"
        return 0.70 if cc.exists() else 0.20

    elif probe_name == "eval_regression_actuator":
        return 0.30  # STATIC ESTIMATE — TD-064: 6 detections, 0 actions

    elif probe_name == "plan_execute_separation":
        return 0.65  # STATIC ESTIMATE — depends on agent discretion

    elif probe_name == "machine_dod":
        return 0.45  # STATIC ESTIMATE — no machine-checkable DoD format yet

    elif probe_name == "interrogation_ritual":
        # Actual probe: spec-driven-dev skill exists
        sdd = REPO_ROOT / ".agent" / "skills" / "spec-driven-dev" / "SKILL.md"
        return 0.50 if sdd.exists() else 0.20

    elif probe_name == "spec_drift":
        return 0.40  # STATIC ESTIMATE — no spec-artifact drift checker built

    elif probe_name == "test_suite":
        # Actual probe: check tests directory has test files
        tests_dir = REPO_ROOT / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            if len(test_files) >= 5:
                return 0.90
            elif len(test_files) >= 1:
                return 0.60
        return 0.20

    elif probe_name == "golden_eval_recent":
        return 0.50  # STATIC ESTIMATE — no recent golden eval run detected

    elif probe_name == "output_quality_oracle":
        if "Stop" in hooks:
            return 0.75
        if (REPO_ROOT / ".agent" / "scripts" / "check_latex_leak.py").exists():
            return 0.30
        return 0.05

    elif probe_name == "independent_critic":
        return 0.30  # STATIC ESTIMATE — requires fresh-context adversarial review

    elif probe_name == "behavioral_golden":
        return 0.80  # STATIC ESTIMATE — AGENTS.md encodes behavioral expectations

    elif probe_name == "scheduled_eval":
        return 0.30  # STATIC ESTIMATE — no cron/daemon eval schedule exists

    elif probe_name == "tool_search":
        if claude_settings.get("mcp", {}).get("tool_search"):
            return 0.70
        return 0.30

    elif probe_name == "error_payloads":
        return 0.50  # STATIC ESTIMATE — partial: some tools have structured errors

    elif probe_name == "token_bounds":
        return 0.60  # STATIC ESTIMATE — context-compactor exists, no hard enforcer

    elif probe_name == "fail_loud":
        return 0.50  # STATIC ESTIMATE — mixed: some scripts exit 1, others swallow

    elif probe_name == "skill_library":
        # Actual probe: count skill directories
        skills_dir = REPO_ROOT / ".agent" / "skills"
        if skills_dir.exists():
            skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
            if len(skill_dirs) >= 30:
                return 0.85
            elif len(skill_dirs) >= 10:
                return 0.65
            return 0.40
        return 0.10

    elif probe_name == "skill_compiler_trigger":
        return 0.25  # STATIC ESTIMATE — skill-compiler exists but no auto-trigger

    elif probe_name == "reflexion_harvester":
        return 0.35  # STATIC ESTIMATE — Reflexion journaling is agent-discretion

    elif probe_name == "delta_merge":
        return 0.30  # STATIC ESTIMATE — no automated delta-merge process

    elif probe_name == "anti_bloat_hygiene":
        # Actual probe: check archive directory exists
        has_archive = (REPO_ROOT / ".agent" / "archive_skills").exists()
        return 0.60 if has_archive else 0.30

    return 0.50  # Unknown probe — default


def calculate_scores(config: dict) -> dict:
    claude_settings = probe_claude_settings()
    results = {"pillars": {}, "total_enforced": 0.0, "total_capability": 0.0}

    for p_id, p_data in config.get("pillars", {}).items():
        p_name = p_data.get("name", p_id)
        p_weight = p_data.get("weight", 0)
        sub_vars = p_data.get("sub_variables", {})

        p_enforced_sum = 0.0
        p_cap_sum = 0.0

        sub_results = {}
        for s_id, s_data in sub_vars.items():
            w = s_data.get("w", 0.0)
            c = s_data.get("C", 0.0)
            probe_name = s_data.get("probe", "")
            e = run_probe(probe_name, claude_settings)
            eff = c * e

            p_enforced_sum += w * eff
            p_cap_sum += w * c

            sub_results[s_id] = {
                "name": s_data.get("name", ""),
                "w": w,
                "C": c,
                "E": round(e, 3),
                "eff": round(eff, 3),
            }

        p_enforced_score = p_weight * p_enforced_sum
        p_cap_score = p_weight * p_cap_sum

        results["pillars"][p_id] = {
            "name": p_name,
            "weight": p_weight,
            "enforced_score": round(p_enforced_score, 2),
            "capability_score": round(p_cap_score, 2),
            "sub_variables": sub_results,
        }

        results["total_enforced"] += p_enforced_score
        results["total_capability"] += p_cap_score

    results["total_enforced"] = round(results["total_enforced"], 1)
    results["total_capability"] = round(results["total_capability"], 1)
    results["enforcement_gap"] = round(results["total_capability"] - results["total_enforced"], 1)
    results["timestamp"] = datetime.now(timezone.utc).isoformat()
    return results


def log_telemetry(results: dict):
    TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": results["timestamp"],
        "enforced_score": results["total_enforced"],
        "capability_score": results["total_capability"],
        "gap": results["enforcement_gap"],
        "pillars": {
            p_id: p_data["enforced_score"]
            for p_id, p_data in results["pillars"].items()
        },
    }
    with open(TELEMETRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def print_summary(results: dict):
    print("=" * 70)
    print(" ATHENA HARNESS SCORECARD — LIVE AUDIT PROBE")
    print("=" * 70)
    print(f" DESIGNED CAPABILITY (C):  {results['total_capability']:>5.1f} / 100")
    print(f" ENFORCED CAPABILITY (E):  {results['total_enforced']:>5.1f} / 100")
    print(f" THE ENFORCEMENT GAP:      {results['enforcement_gap']:>5.1f} points")
    print("-" * 70)
    print(f"{'PILLAR':<40} {'WEIGHT':>7} {'ENFORCED':>9} {'CAPABILITY':>11}")
    print("-" * 70)

    for p_id, p_data in results["pillars"].items():
        name = f"{p_id} {p_data['name'][:35]}"
        print(
            f"{name:<40} {p_data['weight']:>7} "
            f"{p_data['enforced_score']:>8.1f} {p_data['capability_score']:>10.1f}"
        )

    print("=" * 70)


def main():
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)

    config = load_yaml_fallback(CONFIG_PATH)
    results = calculate_scores(config)
    log_telemetry(results)

    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
        return

    print_summary(results)

    if "--check" in sys.argv:
        threshold = 35.0
        for arg in sys.argv:
            if arg.startswith("--min="):
                threshold = float(arg.split("=")[1])
        if results["total_enforced"] < threshold:
            print(f"\n❌ FAILED: Enforced score {results['total_enforced']} is below threshold {threshold}")
            sys.exit(1)
        else:
            print(f"\n✅ PASSED: Enforced score {results['total_enforced']} >= threshold {threshold}")


if __name__ == "__main__":
    main()
