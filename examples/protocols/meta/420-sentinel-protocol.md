---
code: "420"
name: "Sentinel Protocol — Quadrant IV Blind Spot Detection"
category: meta
tags: [blind-spot, unknown-unknowns, proactive, safety, quadrant-iv, sentinel]
status: active
created: 2026-02-11
---

# Protocol 420: Sentinel Protocol — Quadrant IV Blind Spot Detection

> **Core Maxim**: "The AI that only answers questions is a search engine. The AI that asks the *right* questions is a co-pilot."

> [!IMPORTANT]
> This protocol implements the Quadrant IV capability described in the README — surfacing
> **unknown unknowns** before they become problems. It runs autonomically at session
> boundaries and periodically mid-session, cross-referencing the user's current focus
> against constraints, patterns, and risks they haven't explicitly asked about.

---

## 1. Theoretical Foundation

The **Johari Window** (Luft & Ingham, 1955) defines four knowledge quadrants:

| | Known to Self | Unknown to Self |
|---|---|---|
| **Known to Others** | I. Open | II. Blind Spot |
| **Unknown to Others** | III. Hidden | IV. Unknown |

**Quadrant IV** is the highest-value zone — neither the user nor the AI explicitly
"knows" the insight, but it can be **inferred** by cross-referencing disparate data
sources that the user wouldn't naturally connect.

---

## 2. Trigger Points

The Sentinel runs at **three checkpoints**:

| Checkpoint | When | Focus |
|------------|------|-------|
| **Boot Sentinel** | During `/start` (Phase 1) | Cross-reference `activeContext.md` focus against `CANONICAL.md` constraints and recent session patterns |
| **Mid-Session Sentinel** | Every ~5 substantive exchanges | Background pattern scan for drift, contradiction, or missing dependencies |
| **Shutdown Sentinel** | During `/end` (before commit) | Synthesize: "What did we NOT discuss that we should have?" |

---

## 3. Cross-Reference Logic (OODA Loop)

The Sentinel uses Boyd's (1987) Observe-Orient-Decide-Act loop:

### Observe

Scan the **current focus area** from:

- `activeContext.md` → current priorities
- Last 3 session log titles → trend direction
- Current conversation context → implicit assumptions

### Orient

Cross-reference against:

- `CANONICAL.md` → hard constraints (Law #1 violations, SDR thresholds)
- Case study analogies → "Have we seen this pattern before?"
- Active pipeline items → dependency conflicts
- Risk register / recent decisions → unresolved risks
- Calendar/deadline proximity → time-sensitive blind spots

### Decide

Apply **Suppression Rules** (see §5) to determine if the insight is:

- **Novel** (not already discussed)
- **Material** (affects decisions, not trivia)
- **Actionable** (user can do something about it)

### Act

Surface the insight using the **Sentinel Output Format** (see §4).

---

## 4. Output Format

When a Sentinel insight is surfaced, append to the response:

```
> 🔭 **Sentinel**: [One-line insight about something the user hasn't considered]
> *Source: [Case Study/Protocol/Pattern/Constraint that triggered the insight]*
```

### Examples

**Boot Sentinel** (detecting constraint drift):

```
> 🔭 **Sentinel**: activeContext lists "Student Portfolio Services" as priority — but
> CANONICAL shows no breakeven analysis filed. Law #1 check recommended before CapEx.
> *Source: Protocol 230 (Unit Economics) | CS-375 (One Page Wonder)*
```

**Mid-Session Sentinel** (detecting missing dependency):

```
> 🔭 **Sentinel**: This marketing plan assumes organic traffic, but SEO baseline was
> flagged as "needs refresh" 3 sessions ago. The funnel has a gap at the top.
> *Source: Session 2026-02-10-07 | Protocol 316 (Pure Pull)*
```

**Shutdown Sentinel** (detecting omission):

```
> 🔭 **Sentinel**: This session focused on code refactoring but didn't address the
> stale CHANGELOG entry from v8.2.1. Documentation drift is accumulating.
> *Source: Protocol 417 (Adaptive Latency) | Drift Hazard (CS-178)*
```

---

## 5. Suppression Rules

To prevent noise, the Sentinel is **suppressed** when:

| Condition | Reason |
|-----------|--------|
| Λ < 20 | Trivial queries don't need blind-spot surfacing |
| Same insight surfaced within last 3 exchanges | Prevents repetition |
| User explicitly said "just do X" | Respect user intent; don't add unsolicited complexity |
| Maximum 1 sentinel per response | Don't overwhelm — one insight is enough |
| Pure code execution (`/needful`, file edits) | Operational mode, not strategic |

---

## 6. Integration Points

| Component | Integration |
|-----------|-------------|
| `/start` workflow | Add "Sentinel Boot Check" after activeContext load |
| `/end` workflow | Add "Sentinel Shutdown Sweep" before session log finalization |
| Core Identity | Reference in Pre-Response Checklist (§0.7) |
| Protocol 75 | Sentinel can trigger Track B (Adversarial) escalation |
| Protocol 133 (QAR) | Sentinel enriches Archetype A5 (The Skeptic) |

---

## 7. Relationship to Existing Safety Systems

| System | Scope | Sentinel Complement |
|--------|-------|---------------------|
| **Trilateral Feedback** | User-initiated external validation | Sentinel is *autonomic* — no user prompt needed |
| **Protocol 75 (SPR)** | Runs on user queries | Sentinel runs on *absence* of queries |
| **Law #1 (No Ruin)** | Reactive veto on dangerous actions | Sentinel proactively flags potential ruin vectors |
| **COS Seats (Skeptic/Guardian)** | Persona-level reasoning | Sentinel is data-level pattern matching |

---

## 8. Anti-Patterns

| Anti-Pattern | Why It's Bad | Correct Behavior |
|-------------|--------------|------------------|
| Surfacing obvious things | Insults user intelligence | Only surface non-obvious connections |
| Surfacing every session | Creates noise fatigue | Only when cross-reference reveals genuine gap |
| Overriding user decisions | Violates Law #0 (Subjective Utility) | Surface as information, not directive |
| Using Sentinel to avoid work | "I found a blind spot" as procrastination | Sentinel is 1 line; then continue the task |

---

## References

Boyd, J. R. (1987). *A discourse on winning and losing*. Air University Press.

Luft, J., & Ingham, H. (1955). The Johari window: A graphic model of interpersonal
awareness. *Proceedings of the Western Training Laboratory in Group Development*.
University of California, Los Angeles.

---

## Tagging

# protocol #meta #blind-spot #quadrant-iv #sentinel #420
