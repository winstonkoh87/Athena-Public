# Developer & Utility Scripts (`scripts/`)

This directory houses development utilities, benchmarking tools, demo generators, and synchronization scripts.

## 📜 Key Scripts

- [`boot_status.py`](boot_status.py) — Batched concurrent session boot telemetry, index health, and calibration probe (`< 1.0s`).
- [`shutdown.py`](shutdown.py) — Session close orchestrator with micro checkpointing, safe git commits, and JSONL log rotation.
- [`harness_score.py`](harness_score.py) — 6-pillar zero-iteration agent harness capability (`C`) and enforcement (`E`) scorer.
- [`maintenance_ratio.py`](maintenance_ratio.py) — Output-vs-maintenance commit ratio analyzer and backlog gate.
- [`decision_ledger.py`](decision_ledger.py) — Decision logging, outcome auditing, and Brier calibration score calculator.
- [`benchmark_kv_cache.py`](benchmark_kv_cache.py) — Benchmarks KV cache latency, token throughput, and TTFT across supported model providers.
- [`generate_demo_gif.py`](generate_demo_gif.py) — Programmatically captures and compiles terminal walkthroughs into high-fidelity animated demo GIFs.
- [`sync_version.py`](sync_version.py) — Enforces synchronized semantic versioning across `pyproject.toml`, documentation, and manifest files.
- [`sync_to_public.py`](sync_to_public.py) — Default-deny allowlist synchronizer enforcing Phase 0/1 security and privacy barriers.
- [`sync_privacy_secret.py`](sync_privacy_secret.py) — Manages privacy pattern detection and local secret environment mapping.
- [`gto_exec.sh`](gto_exec.sh) — Shell wrapper executing GTO decision screening and risk audit routines.

## 🚀 Execution

All scripts are executable via Python 3:

```bash
python3 scripts/sync_version.py --check
```
