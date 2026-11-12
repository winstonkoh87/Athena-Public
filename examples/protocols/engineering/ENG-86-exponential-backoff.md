# Infrastructure & Continuity Hub: Exponential Backoff (Autonomous Monitoring)

> **Source**: Harvested from `ykdojo/claude-code-tips` (Dec 2025)
> **Use Case**: Long-running jobs (CI, Docker builds, deployments)

---

## Core Pattern

When monitoring async processes, use exponential backoff to minimize token waste while maintaining awareness.

```
Check → Wait 1m → Check → Wait 2m → Check → Wait 4m → Check → Wait 8m → ...
```

---

## Implementation

### Manual (AI-Executed)

```
1. Run initial check command
2. If not complete: sleep 60 && check again
3. If not complete: sleep 120 && check again
4. If not complete: sleep 240 && check again
5. Continue doubling until complete or max_wait (30m)
```

### Example: GitHub Actions

```bash
# Token-efficient: single line output
gh run view <run-id> | grep <job-name>
```

**Avoid**: `gh run watch` (continuous output, token-heavy)

---

## When to Use

| Scenario | Apply Backoff? |
|----------|----------------|
| Docker build | ✅ Yes |
| GitHub CI | ✅ Yes |
| npm install | ❌ No (fast enough) |
| Full vector / FTS reindex | ✅ Yes (~130s) |
| Git operations | ❌ No |

---

## Background Process Pattern

1. Start command with `&` or move to background (Ctrl+B in Claude Code)
2. Store process ID / command ID
3. Apply exponential backoff to status checks
4. Report completion when detected

---

## Integration

- Works with: Protocol 77 (Adaptive Latency)
- Complements: Container sandboxing for risky autonomous tasks

---

## Tags

# monitoring #async #automation #harvested

---

## Tagging

#protocol #framework #process #86-exponential-backoff
