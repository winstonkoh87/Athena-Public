# data/ — Active Datasets & Benchmark Telemetry

> **Protocol Reference**: [Protocol 543: GitHub Repo Scaffold](../docs/ARCHITECTURE.md)  
> **Retention Policy**: Only active, current-iteration datasets, benchmarks, and media assets are maintained here. Historical takes, superseded test runs, and intermediate blobs are pruned or archived to prevent repository bloat.

---

## Directory Structure

```text
data/
└── README.md                     # This file (purpose & retention invariant)
```

## Invariants

1. **Latest Iteration Only**: Historical takes, intermediate scratch files, and stale benchmark runs are pruned immediately upon release.
2. **Binary Hygiene**: Large binary files (>10MB) must be excluded or tracked via Git LFS / external storage.
3. **Public Data Boundary**: All data stored here is strictly sanitized, anonymized, and public-safe (Zero PII, Zero credentials).
