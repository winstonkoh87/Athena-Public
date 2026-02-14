---

created: 2025-12-27
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-27
last_updated: 2026-01-16
---

# Protocol 220: Blog Post Gold Standard

**Reference Implementation:** [`case-study-p6-math-tuition.html`](file:///Users/[AUTHOR]/Desktop/[AUTHOR]87.github.io/articles/case-study-p6-math-tuition.html)

**Assets:**

- [`article.css`](file:///Users/[AUTHOR]/Desktop/[AUTHOR]87.github.io/assets/css/article.css) — Reusable article styles
- [`_template.html`](file:///Users/[AUTHOR]/Desktop/[AUTHOR]87.github.io/articles/_template.html) — Starter template

---

## Purpose

This protocol defines the quality bar for blog posts on Winston's portfolio. Every future article should meet or exceed this standard.

---

## Structural Requirements

### 1. Article Metadata

- [ ] `<title>` matches headline
- [ ] `<meta description>` is compelling, <160 chars
- [ ] Open Graph tags (og:title, og:description, og:image, og:type, og:url)
- [ ] Twitter Card tags
- [ ] JSON-LD BlogPosting schema
- [ ] Canonical URL
- [ ] Published + Modified dates with timezone (`+08:00`)

### 2. Content Structure

- [ ] **TL;DR / AI Summary** at top (3 bullets max)
- [ ] **Table of Contents** (Wikipedia-style, numbered)
- [ ] **7 parts max** (enough depth without bloat)
- [ ] **Hidden Gem Check**: Every section MUST have one "insider" insight (not found in top 10 search results)
- [ ] **Key Insight boxes** for quotable takeaways
- [ ] **Limits/Risks section** (anti-hype, builds trust)
- [ ] **Next Steps** (jumping-off point for action) instead of a generic Conclusion
- [ ] **AI-Friendly Formatting** (Per [Protocol 231](file:///Users/[AUTHOR]/Desktop/Project Athena/.agent/skills/protocols/content/231-llm-seeding-geo-strategy.md))
  - [ ] Concise section summaries for LLM extraction
  - [ ] Tables for data comparison (high AI parseability)
  - [ ] Proprietary terms/frameworks tagged for "Citation Bait"

### 3. Case Studies

- [ ] **Specific numbers** (not vague claims)
- [ ] **Primary source links** for any regulation/fact claims
- [ ] **Assumptions disclosed** (e.g., "40% Y1 failure rate, 10% discount rate")
- [ ] **Disclaimer** ("not financial/legal advice")
- [ ] **Human judgment moment** — show *why* the human layer mattered
- [ ] **Link to full report** if available

---

## Credibility Checklist

| Claim Type | Requirement |
| :--- | :--- |
| Statistics (e.g., "40% of jobs") | Source or soften ("a huge chunk") |
| Regulations (e.g., NEA rules) | Hyperlink to official source |
| Financial projections (e.g., EV) | Disclose assumptions |
| Bold claims (e.g., "3-5x throughput") | Define the metric |

---

## Tone & Style

### Do

- ✅ **Justified text** with `hyphens: auto`
- ✅ **The 3-Sentence Rule**: Paragraphs $\le 3$ sentences (Strict Readability)
- ✅ **Specific, relatable examples** (not generic "imagine if...")
- ✅ **Soften polarizing statements** (e.g., "prompting is table stakes" instead of "prompting is just typing")
- ✅ **Acknowledge counterpoints** ("Yes, AI will eliminate some roles...")
- ✅ **Use "Table 1:" labels** for tables

### Don't

- ❌ Over-hype without substance
- ❌ Use buzzwords without definition
- ❌ Leave claims unsourced
- ❌ Use literal `\n` or broken formatting

---

## Technical Standards

### CSS

- External `style.css` for global styles (Follow [Protocol 221](file:///Users/[AUTHOR]/Desktop/Project Athena/Athena-Public/docs/protocols/content/221-high-performance-ux-design.md) for UI/UX standards)
- Inline styles only for targeted overrides (ToC, table caption)
- `prefers-reduced-motion` support for animations

### Performance

- `loading="lazy"` on images
- `decoding="async"` on images
- Preconnect to Google Fonts

### Accessibility

- `scope="col"` on table headers
- `<caption>` on tables
- `aria-label` on nav elements
- `<time datetime="...">` for dates

---

## Final Pre-Publish Checklist

- [ ] All numbers internally consistent
- [ ] No literal `\n` or formatting artifacts
- [ ] All links work (internal + external)
- [ ] JSON-LD validates at schema.org validator
- [ ] No privacy leaks (friend/stall names obscured)
- [ ] Mobile responsive (test at 375px)
- [ ] WhatsApp float button works
- [ ] **SYNC `writing.html`** — Ensure title and excerpt match article H1

---

## Example Commits (This Article)

| Commit | Fix |
| :--- | :--- |
| `aff8cd1` | Correct BCM figures ($100K/4 partners) |
| `6f13c6d` | Add NEA source, EV assumptions, disclaimer |
| `73ea3c8` | Acknowledge AI will eliminate some roles |
| `8cbcf42` | Remove `\n` artifacts, scope NEA claim |

---

*Last updated: 27 December 2025*
*Reference article: The Bionic Operator*

## Related Protocols
- [CS044: ILP Trust Arbitrage](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS044_ILP_Trust_Arbitrage.md)

- [CS044: ILP Trust Arbitrage](file:///Users/[AUTHOR]/Desktop/Project Athena/.context/memories/case_studies/CS-044-ilp-trust-arbitrage.md)
