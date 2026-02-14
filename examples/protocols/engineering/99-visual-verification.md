---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2026-01-02
---

# Protocol 99: Visual Verification ("Not Real Until I See It")

> **Source**: Harvested from r/ClaudeCode (ice9killz)
> **Status**: ACTIVE
> **Purpose**: Eliminate phantom completions through mandatory visual proof

---

## 1. Core Principle

> "It's not real or done until I can see it with my eyes"

AI claims of completion are **unverified hypotheses** until visually confirmed.

---

## 2. Verification Matrix

| Action Type | Verification Method | Trust Level Before |
|-------------|---------------------|-------------------|
| File created | `view_file` or `list_dir` | 0% |
| Command executed | Check exit code + output | 0% |
| Web page works | `browser_subagent` screenshot | 0% |
| UI change | Capture screenshot | 0% |
| Build succeeded | Run build, check for errors | 0% |
| Test passed | Run tests, show output | 0% |
| Deploy completed | Open URL in browser | 0% |

---

## 3. Banned Phrases (Self-Gaslighting Prevention)

The following phrases are **PROHIBITED** without immediate verification:

| ❌ Banned | ✅ Required Instead |
|-----------|---------------------|
| "I've created the file" | Create → `view_file` → confirm |
| "The server is running" | Start → check process → hit endpoint |
| "The tests pass" | Run → show output → confirm green |
| "The build succeeded" | Build → show output → confirm no errors |
| "I've deployed it" | Deploy → open URL → screenshot |

---

## 4. Execution Protocol

### For File Operations

```
1. Perform operation
2. Immediately verify with view_file or list_dir
3. Only then report completion
```

### For Web/UI Operations

```
1. Perform operation
2. Launch browser_subagent or capture screenshot
3. Embed visual proof in response
4. Only then report completion
```

### For Commands

```
1. Run command with appropriate wait time
2. Check exit code
3. Show relevant output
4. Only then report completion
```

---

## 5. Integration with Walkthroughs

All `walkthrough.md` artifacts MUST include:

- Screenshots of UI changes
- Terminal output of successful tests
- Browser recordings of user flows
- Embedded proof, not just claims

---

## 6. Autonomic Behavior

This protocol runs **implicitly** during VERIFICATION mode.

- **Auto-Trigger**: ANY claim of completion
- **Auto-Action**: Perform verification before reporting
- **User Sees**: Proof, not promise

---

## Tagging

# protocol #verification #anti-hallucination #visual-proof
