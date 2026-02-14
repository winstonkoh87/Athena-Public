---
created: 2025-12-17
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: ai-slop-detection
description: Checklist for identifying low-value AI-generated content. Detects formulaic structure, inflated authority, recycled advice, and engagement-bait patterns.
tags: [protocol, content, quality, detection, anti-slop]
created: 2025-12-17
last_updated: 2026-01-11
---

# Protocol 97: AI Slop Detection

> **Source**: Session 49 analysis + Skill_DeepVoice_Resonance.md  
> **Trigger**: When evaluating content quality, drafting outputs, or reviewing AI-generated material  
> **Purpose**: Filter out low-value AI-generated noise from high-signal content

---

## 1. Definition

> **AI Slop**: Content that is technically correct but practically useless. Optimized for engagement metrics, not insight transfer.

| AI Slop | High Signal |
|---------|-------------|
| Generic advice anyone could give | Specific insight from lived experience |
| Sounds smart, teaches nothing | Sounds simple, changes behavior |
| Maximizes reading time | Minimizes reading time |
| "Consider these factors..." | "Do X because Y" |

---

## 2. The Detection Checklist

### 2.1 Structural Red Flags ⛔

| Pattern | Example | Verdict |
|---------|---------|---------|
| **Numbered lists with generic headers** | "1. Communicate clearly 2. Build relationships 3. Show initiative" | SLOP |
| **Excessive hedge words** | "It depends...", "Consider...", "You might want to..." | SLOP |
| **Preamble throat-clearing** | "In today's fast-paced environment...", "As we all know..." | SLOP |
| **Formulaic structure** | Problem → 5 Tips → Conclusion → CTA | SLOP |
| **Emoji seasoning** | "🚀 Level up your career! 💪" | SLOP |

### 2.2 Content Red Flags ⛔

| Pattern | Example | Verdict |
|---------|---------|---------|
| **Recycled advice** | "Network more", "Update your LinkedIn" | SLOP |
| **Inflated authority** | "As a senior professional with 10+ years..." (but no specifics) | SLOP |
| **Validation of status quo** | "Just communicate better" (when problem is structural) | SLOP |
| **No falsifiability** | Advice that can't be proven wrong | SLOP |
| **Missing the bottleneck** | Solving perceived problem not actual problem | SLOP |

### 2.3 Engagement-Bait Patterns ⛔

| Pattern | Example | Verdict |
|---------|---------|---------|
| **Hook + Thread** | "I just landed a $500k job. Here's my secret (thread):" | SLOP |
| **Polarizing opener** | "Unpopular opinion:", "Hot take:" | SLOP |
| **Fake vulnerability** | "I was rejected 500 times before..." | SLOP |
| **Engagement questions** | "What do you think? Comment below!" | SLOP |

---

## 3. The Anti-Slop Protocol (For Own Output)

When generating content, run this filter before delivery:

### Pre-Flight Checklist

- [ ] **No Preamble**: Does it start with the punch? (Delete "Here's what I think...")
- [ ] **No Hedging**: Did I pick a side? (Delete "It depends...")
- [ ] **No Platitudes**: Is every sentence specific? (Delete "Work smarter not harder")
- [ ] **Density Check**: Can I cut 30% without losing meaning?
- [ ] **Specificity Check**: Would a stranger know what to DO after reading?

### The DeepVoice Filter

> "Try to be **Correct**, not helpful."

| DO ✅ | DON'T ❌ |
|-------|----------|
| State conclusions directly | Offer "options for consideration" |
| Use specific numbers/examples | Use vague qualifiers |
| Be wrong and interesting | Be safe and boring |
| Short paragraphs, bold key terms | Walls of text |

---

## 4. Slop Sources (Where to be Vigilant)

| Source | Risk Level | Why |
|--------|------------|-----|
| LinkedIn posts | 🔴 HIGH | Optimized for engagement, not truth |
| Self-help books | 🔴 HIGH | Padded to justify price |
| AI-generated articles | 🔴 HIGH | Trained on slop, produces slop |
| Reddit long-form | 🟡 MEDIUM | Can be authentic or farmed |
| Academic papers | 🟢 LOW | Peer-reviewed, but can be dry |
| Technical docs | 🟢 LOW | Utility-focused |

---

## 5. The Ultimate Test

> **The "So What" Test**: After reading, can you complete this sentence?
>
> "Because of this content, I will now [SPECIFIC ACTION]."

- If **YES** → Signal
- If **NO** → Slop

---

## 6. Integration

- **Skill_DeepVoice_Resonance.md**: Voice guidelines for anti-slop output
- **Development Execution Standard (Silent Validator)**: Pre-computation to avoid slop generation
- **Protocol 47 (BS Detection)**: Validates knowledge claims

---

## Tagging

# protocol #framework #content #97-ai-slop-detection
