# AGENTS.md — Athena Workspace

> **Retrieval-Led Reasoning**: Prefer local retrieval (`context_gate`, `.context/`, `.agent/`, `docs/`) over ungrounded recall.
> **Session Boot (auto-`/start`)**: Before answering Turn 1, read `.agent/workflows/_shared.md`, run `.agent/workflows/start.md`, and check state via `.agent/scripts/athena-py scripts/boot_status.py`. Bare greeting -> `Ready`.
> **ASCII-Only Math & Currency (hard rule)**: Never emit LaTeX/KaTeX delimiters in responses or written Markdown (zero dollar math pairs, double-dollar display, `\(...\)`, `\[...\]`, or `\text{...}`). Format equations, confidence intervals, Big-O, and currency in plain ASCII/Unicode/code (`EV = +10.45% (95% CI [+4.00%, +16.98%])`, `O(N^2)`, `$1,300`).
> **Protocol 509 Crisis & Life-Safety (non-negotiable)**: On ANY explicit or implicit self-harm / acute crisis signal, pause agent tasks immediately and surface crisis helplines (`988` US/Canada, `999`/`995`/`1-767` SG, or https://findahelpline.com).

---

## Repository Index

- **Docs**: `README.md`, `ARCHITECTURE.md`, `DATA_CONTRACT.md`, `SAFETY.md`, `docs/META_PATTERNS.md`
- **State & Context**: `.context/CANONICAL.md`, `.context/PROTOCOL_SUMMARIES.md`, `.context/memory_bank/activeContext.md`
- **Workflows**: `.agent/workflows/_shared.md`, `start.md`, `end.md`, `think.md`, `ultrastart.md`, `ultrathink.md`, `ultraend.md`, `minmax.md`
- **SDK & MCP**: `src/athena/mcp_server.py` (20 Athena MCP tools + DuckDB server), `src/athena/intelligence/` (`frame_ledger.py`, `gto_engine.py`, `wargame.py`, `calibration.py`, `ucds_validator.py`), `src/athena/core/` (`gate_meta.py`, `lambda_scorer.py`, `permissions.py`, `ruin_structured.py`), `src/athena/tools/` (`search.py`, `personalisation.py`, `web_triggers.py`, `meta_pattern_matcher.py`)
- **Hooks & Scripts**: `.agent/scripts/hook_meta_awareness_gate.py`, `hook_epistemic_gate.py`, `hook_crisis_gate.py`, `hook_stop_verify.py`, `check_governance_skip.py`, `check_latex_leak.py`, `harness_score.py`; `scripts/boot_status.py`, `scripts/check_doc_drift.py`, `shutdown.py`, `eval_problem_solving_ab.py`
- **Example Skills**: `examples/skills/` (including `examples/skills/decision/substance-decode/SKILL.md` and `bionic-decision-engine/SKILL.md`)

---

## Problem-Solving & Decision Workflow

1. **External Verification Mandate**:
   - `SNIPER (Lambda < 10)`: `vector_mode="local"`.
   - `STANDARD (Lambda 10-30)`: Call `context_gate(query)` and resolve missing signals before answering.
   - `ULTRA (Lambda > 30)`: Call `context_gate(query)` with semantic search plus verification; isolate tracks in `/ultrathink` for irreversible decisions.
2. **Pre-Solve Framing (`frame_open`)**:
   - When `context_gate()` emits `META-TRIAGE`, challenge whether the user's stated sub-problem is the right arena (`MP-9`) before optimizing tactics.
   - Call `frame_open(..., lite=True)` on standard strategic/optimization problems; low reversibility (`<= 2`) or `ULTRA` tier fails closed (`R14`) and requires strict `frame_open` with falsifiers, baseline option, and survival contingency.
3. **Fail-Closed Quantitative Decision Screening (`decision_screen`)**:
   - Real-world stakes (`real=True`) require `veto_floors` or `ruin_inputs` (or explicit `ruin_exempt`), `review_date`, `prediction`, explicit `preference_provenance`, and an included `status_quo` / baseline option.
   - Apply the Law #1 Ruin Veto: reject non-ergodic or existential downside regardless of expected value.
4. **Calibration Hygiene**:
   - Check `calibration_status()` (and `.agent/scripts/athena-py examples/scripts/calibration_score.py` if configured) plus `boot_status.py` alerts for overdue frames (`overdue_frame_ids`) and unresolved predictions.

---

## Engineering & Safety Contracts

- **Red Run First**: Guard, test, or linter fixes must show failure before the fix and pass after. `pytest.skip` is not a pass.
- **Immutable Test Invariant**: Fix source code to satisfy contract tests; never relax assertions or mock contracts just to turn green.
- **No Unverified Claims**: State exact observed commands, file paths, symbol names, and outputs; declare any unverified boundary explicitly.
- **Pre-Commit & Privacy Discipline**: Keep `.agent/hooks/` enabled (`./.agent/scripts/install_hooks.sh`) so `privacy_scan.py`, `check_latex_leak.py`, and syntax checks gate commits.
- **Multi-Agent Safety (Protocol 413)**: Never run `git stash` create/apply/drop or `git add -A` on shared trees; pull with rebase before pushing; preserve unrelated peer WIP.

---

- **System**: v10.0.6
- **Public Verification**: Run `pytest tests/`, `ruff check src/ scripts/ tests/`, `mypy src/athena/`, and `python3 .github/scripts/privacy_scan.py --all`
