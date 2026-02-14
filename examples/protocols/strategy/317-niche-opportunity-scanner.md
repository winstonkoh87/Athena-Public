---

created: 2026-01-12
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-12
last_updated: 2026-01-12
---

# Protocol 317: Niche Opportunity Scanner

> **Purpose**: Systematic deep research prompt for identifying high-pull, underserved service niches.
> **Trigger**: Evaluating new markets, validating business ideas.

---

## The Deep Research Prompt (Gemini/Claude)

```markdown
# Deep Research: [MARKET] Service Niche Opportunity Analysis

## Objective
Identify high-demand, underserved service niches in [MARKET] suitable for a solo founder to build a scalable, exitable business within 3-5 years.

## Criteria for "High Pull" Niche
1. **Demand Signal**: Consumers actively searching (not needs education)
2. **Willingness to Pay**: Transaction >$500/mo OR LTV >$3,000
3. **Recurring Revenue**: Subscription or repeat purchase possible
4. **Low Regulatory Barrier**: No professional license required
5. **Scalable Delivery**: 1-to-many possible (group, digital, hybrid)

## Criteria for "Market Gap"
1. **Fragmented Supply**: No dominant player with >20% share
2. **Quality Complaints**: Reviews show dissatisfaction with existing providers
3. **Underserved Segment**: Specific demographic ignored by mass-market
4. **Digital Lag**: Existing players have poor online presence

## For Each Niche, Provide:
1. Demand Analysis (search volume, trends, seasonality)
2. Competitive Landscape (top 3 players, pricing, channels)
3. Market Gap (segment, pricing, delivery, marketing)
4. Unit Economics (pricing, LTV, CAC, margin)
5. Scalability Score (1-10)

## Output
Rank top 5 niches by: Demand × Gap × Scalability
```

---

## The Validation Stack (Ground Truth)

| Source | Signal |
|--------|--------|
| **Carousell** | Real demand, pricing, competitor density |
| **Google Keyword Planner** | Search volume, CPC (high = money) |
| **IG/TikTok Search** | Content saturation, winning angles |
| **HardwareZone/Reddit** | Pain points, complaints, unmet needs |
| **Google Reviews** | Quality gaps ("good but expensive") |

**Sequence**: Gemini → Carousell → Keywords → Social → Reviews

---

## Tags

# strategy #niche-selection #research #market-gap
