---
protocol: 517
name: Homeostatic Pressure
domain: architecture
created: 2026-03-05
last_updated: 2026-11-13
status: active
epistemic_status: advisory  # discretionary checklist heuristic, not a background daemon
---

# Protocol 517: Homeostatic Pressure (Synthetic Hormone System)

> **Source**: HORA (HOmeostatic Regulation Architecture, Bastos & Correia, DOI `10.1007/978-3-032-05176-9_31`) + LIDA cognitive cycles. Adapted to prompt-layer resource management.
>
> **Epistemic note**: There is no background daemon or computed scalar in Python enforcing these thresholds automatically; apply this table as an explicit discretionary self-check when under high context or tool-failure load.

## Problem

Athena's cognitive systems have no feedback mechanism for resource exhaustion. A deep ULTRA query can trigger co-activation chains 4-5 clusters deep, saturating the context window and degrading output quality. Without pressure signals, the system runs itself into the ground — the computational equivalent of metabolic collapse.

## Mechanism

The Maintenance system continuously monitors internal resource signals. When any threshold is breached, it emits a **synthetic hormone** — a scalar modifier that raises the activation threshold for expensive cognitive systems, forcing the organism toward low-cost survival responses.

### Pressure Signals and Thresholds

| Signal | Threshold | Forced Action |
|---|---|---|
| Context window saturation | > 80% utilized | Force SNIPER mode. No new co-activation chains. |
| Context window critical | > 90% utilized | Trigger `context-compactor` BEFORE responding. |
| Consecutive tool failures | ≥ 2 failures | Circuit breaker (P514). Stop, diagnose, await override. |
| Co-activation chain depth | > 4 clusters deep | Force exit to Quality Gate. No further cascading. |
| Session duration | > 3 hours continuous | Emit compaction advisory. Suggest `/save` or `/end`. |

### Hormone Cascade

```text
Pressure signal detected
  → Maintenance system emits hormone (scalar weight modifier)
  → Activation threshold RAISED for: Execution, Growth, Strategic Reasoning, Research
  → Activation threshold UNCHANGED for: Survival, Maintenance
  → Incoming queries forced to SNIPER pathway
  → System stabilizes → hormone decays → normal routing resumes
```

### Priority Suppression Order

When homeostatic pressure is active, systems are suppressed in reverse priority order:

1. **First suppressed**: Growth (📣) — marketing/distribution can wait
2. **Then**: Learning (📖) — knowledge acquisition is non-urgent
3. **Then**: Execution (⚙️) — stop building until stable
4. **Then**: Strategic Reasoning (🎯) — deep analysis is expensive
5. **Never suppressed**: Survival (🛡️), Maintenance (🔄) — these ARE the pressure response

### Recovery

Homeostatic pressure is a temporary state, not a permanent downgrade. Once resource signals return below threshold:

- Context < 60% → Resume STANDARD routing
- Tool failures resolved → Resume normal execution
- Chain depth reset → Allow new co-activation

## Biological Analogy

When the body is under metabolic stress, cortisol suppresses non-essential functions (immune response, digestion, growth) and redirects resources to immediate survival (fight-or-flight). The synthetic hormone does the same — it suppresses expensive cognitive functions and redirects processing to fast, cheap, survival-mode responses.

## Integration Points

- **Wired into**: `/start` boot sequence (Law #6 Compliance section)
- **Triggers**: Context compactor, circuit breaker, session management
- **Cooperates with**: P514 (Sovereign Safety), P516 (Memory Paging)

## References

- [HORA: From Homeostatic Principles to Discrete Emotions in an Agent Architecture (Bastos & Correia, 2025/2026)](https://doi.org/10.1007/978-3-032-05176-9_31)
- [EILS: Emotion-Inspired Learning Signals (Tiwari, 2025)](https://arxiv.org/abs/2512.22200)
- [Surprise! Using Physiological Stress for Allostatic Regulation Under the Active Inference Framework (Khan & Lowe, 2024)](https://arxiv.org/abs/2406.08471)
- [LIDA Cognitive Architecture](https://ccrg.cs.memphis.edu/tutorial/)
- Protocol 514: Sovereign Safety Sequence (see CLUSTER_INDEX #14)
