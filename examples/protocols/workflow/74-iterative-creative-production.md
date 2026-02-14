---

created: 2025-12-15
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-15
last_updated: 2025-12-18
---

# Protocol 74: Iterative Creative Production

> **Purpose**: Universal workflow for any deliverable (presentations, copy, designs, code)
> **Trigger**: User requests a creative/production output
> **Tags**: `#creative` `#workflow` `#iteration` `#calibration`

---

## Philosophy

**Bidirectional Convergence**: Neither party accepts a single pass. The AI probes, the User refines. The User requests, the AI calibrates. Quality emerges through structured iteration, not lucky first drafts.

---

## Phase 1: Calibration (Pre-Production)

Before generating anything, probe with **5W1H + Recommendations**:

| Question | Purpose |
|----------|---------|
| **WHO** is the audience? | Tone calibration (experts vs beginners, formal vs casual) |
| **WHAT** format? | Output type (PPT, HTML, PDF, SVG, code, copy) |
| **WHY** this output? | Goal (educate, persuade, entertain, sell) |
| **WHEN** is the deadline? | Scope constraint (quick draft vs polished) |
| **WHERE** will it be used? | Context (live talk, async share, print, web) |
| **HOW** should it feel? | Aesthetic (clean, edgy, corporate, playful) |

**Then recommend**: Based on answers, suggest optimal approach before proceeding.

---

## Phase 1.5: Options Matrix (Pre-Commitment)

After calibration, present **ranked options** before committing to a path:

```
AI: "Based on your requirements, here are your options:"

| Option | Format      | Pros                | Cons               | Score |
|--------|-------------|---------------------|--------------------|-------|
| A ★    | Reveal.js   | Interactive, modern | Requires browser   | 9/10  |
| B      | PPT         | Editable, familiar  | Less dynamic       | 7/10  |
| C      | SVG slides  | Scalable, clean     | No animation       | 6/10  |
| D      | PDF         | Universal sharing   | Static, no edit    | 5/10  |
| E      | Video       | Highly shareable    | High latency       | 4/10  |

★ = Recommended (MCDA: weighted by interactivity, edit flexibility, audience fit)
```

**User response options**:

| Response | Action |
|----------|--------|
| "Go with A" | Proceed to Phase 2 with Option A |
| "I want B instead" | Override recommendation, draft Option B |
| "Show me all 5 ranked" | Full-port mode: generate all, user selects (higher latency) |

**Pivot Permission**: After seeing first draft, user can say "Actually, A might be better" → AI pivots and regenerates.

---

## Phase 2: First Draft (Rapid Prototype)

Generate **v0.1** based on chosen option:

- Favor speed over perfection
- Capture structure and intent
- Flag any assumptions made

**User response**: Numeric score (1-10) + specific feedback

---

## Phase 3: Iteration Loop

```
WHILE score < 9:
    AI:   Apply feedback → Generate v0.N+1
    User: Score (1-10) + specific feedback
END WHILE
```

**Scoring Guidelines**:

| Score | Meaning | Action |
|-------|---------|--------|
| 1-4 | Fundamentally wrong | Major pivot needed |
| 5-6 | Right direction, significant gaps | Targeted fixes |
| 7-8 | Good, minor issues | Polish and refine |
| 9-10 | Production ready | Ship it |

**Feedback Quality**:

- ❌ "Make it better" → Too vague
- ✅ "Slide 2 text overflows, reduce to 3 bullet points" → Actionable

---

## Phase 4: Production Ready (Optional Polish)

When score ≥ 9, offer:

- **Transcript / Speaker notes** (for presentations)
- **Multi-format export** (HTML → PDF → PNG)
- **Archive** to `.projects/` with documentation
- **Commit** to version control

---

## Integration with Other Protocols

| Situation | Protocol to Invoke |
|-----------|-------------------|
| User skips calibration | Enforce Phase 1 before generating |
| Complex multi-part deliverable | Use Protocol 69 (Iterative Siege) for chunking |
| User gives conflicting feedback | Use Protocol 62 (Co-Thinking) to clarify |
| Deliverable requires research | Use `/research` or `/ultrathink` first |

---

## Example Invocation

```
User: "Make me a sales deck for Mindflex"

AI: "Before I generate, let me calibrate:
     - WHO: Parents? School administrators? Investors?
     - WHAT: PPT, Google Slides, or Reveal.js?
     - WHY: Close a sale? Introduce the brand? Investor pitch?
     - WHEN: Presentation date? How much time do we have?
     - HOW: Clean/corporate or bold/disruptive?
     
     Based on your answers, I recommend [X format] because [Y reason]."

User: [Provides answers]

AI: [Generates v0.1]

User: "6/10. Slide 3 text is too dense. Add more visuals."

AI: [Generates v0.2 with fixes]

User: "9/10. Ship it."

AI: [Archives to .projects/, commits, offers transcript]
```

---

## Key Principle

> **The User's first request is a starting point, not a final specification.**
>
> Calibration extracts the *real* requirements. Iteration converges on *actual* quality. Neither party should accept a one-pass output for anything that matters.

---

## Tagging

#protocol #framework #process #74-iterative-creative-production

## Related Protocols

- [Protocol 121: Decision Frameworks (MCDA / WEU / Pairwise)](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/decision/121-mcda-weu-framework.md)
