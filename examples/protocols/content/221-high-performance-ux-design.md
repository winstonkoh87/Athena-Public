---
created: 2025-12-27
last_updated: 2026-01-30
graphrag_extracted: true
---

---name: high-performance-ux-design
description: Protocol for building high-conversion, premium aesthetic websites. Focuses on visual hierarchy, navigation conventions, and readability physics.
tags: [protocol, web-design, ux, ui, conversion, 2026-standards]
created: 2025-12-27
last_updated: 2025-12-27
---

# Protocol 221: High-Performance UX & Design

> **Source**: Contentsquare UX Guide + Big Cat Creative DIY Best Practices + Reddit Research  
> **Trigger**: Before building a new page/site or conducting a design audit.  
> **Purpose**: Ensure all Athena-managed web assets maintain a "Premier" standard that builds trust and drives conversion.

---

## 1. Visual Hierarchy & "Breathability"

The objective is to guide the eye through the page without causing "Analysis Paralysis."

- **Rule of Padding**: Every major section must have at least `8vh` - `10vh` vertical padding to "Let it Breathe."
- **The "Hero" Focus**: Use a high-contrast headline (H1) that states the **Outcome** first, then the mechanism.
- **Color Constraint**: Stick to a 3-color palette (Primary, Secondary, Accent). Use accent colors *only* for CTAs.

---

## 2. Navigational Physics (The "No-Guess" Rule)

Users should never have to think about where to click next.

| Element | Standard |
| :--- | :--- |
| **Menu Labels** | Use standard conventions: Home, About, Services, Writing, Contact. |
| **Search Bar** | Include for sites with >10 pages. |
| **Logo** | Top-left or center, always linked to `/index.html`. |
| **Breadcrumbs** | Required for deep hierarchies (e.g., e-commerce or complex wikis). |
| **CTAs** | Strategic placement: Hero, Mid-page, and Footer. Minimum 2 per landing page. |

---

## 3. Readability & Typography Physics

Websites are primarily meant to be read. If reading is hard, the site fails.

- **Typeface**: Use modern Sans-Serif for body text (e.g., *Inter, Roboto, Outfit*).
- **Font Size**: Minimum `16px` for body text, `18px` preferred for readability.
- **Line Height**: `1.5` to `1.6` for optimal tracking.
- **Text Blocks**: Max `4-5` lines per paragraph. Use bullet points for any list of >2 items.
- **Contrast**: Black/Dark Grey on White/Off-white (Ratio > 4.5:1).

---

## 4. Interaction Feedback (Micro-animations)

A static site feels "dead." Micro-interactions make the site feel alive and responsive.

- **Button Hover**: Must change color or scale slightly (`1.05x`) upon hover.
- **Loading States**: Use skeletal loaders or progress indicators for data-heavy sections.
- **Scroll reveal**: Subtle entry animations for major sections to guide the user's attention.

---

## 5. Performance & Technical Baseline

- **Mobile Responsiveness**: Design for thumb accessibility (CTAs must be large enough to tap easily).
- **Image Hygiene**: Compress all images. Use `.webp` format. Max size `500KB`.
- **Accessibility**: All images must have `alt` tags. All buttons must have `aria-label` if they utilize icons only.
- **SEO Core**: Single `h1` per page. Unique `title` and `meta description` reflecting page content.

---

## 6. Verification Audit

Before launching, check:

- [ ] Does the "Hero" pass the **3-second value test**?
- [ ] Are all fonts legible on a mobile device?
- [ ] Does the logo link back to Home?
- [ ] Is there a CTA in the footer?
- [ ] Do buttons respond to hover?

---

## Tagging

```text
#protocol #web-design #ux #ui #conversion #221-high-performance-ux-design
```
