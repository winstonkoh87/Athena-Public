---
description: 4-step pipeline for building premium websites with AI — Research → Copy → Design → Code
created: 2026-03-20
source: Anti-Slop Pipeline (Stolen Pattern)
---

# /web-build — Premium Website Build Pipeline

> **Philosophy**: Separation of concerns. Design AI ≠ Coding AI. Copy drives design, not the reverse.
> **Source**: Anti-Slop Pipeline (Separation of design and coding AI concerns)

## Prerequisites

- Client brief completed (or `/brief` output)
- Brand identity basics (name, rough positioning)

## Pipeline

### Step 1: Audience Research
// turbo
1. Run target audience research — identify ideal customer, search intent, pain points
2. Output: JSON or structured `.md` with customer profile + keywords
3. Tools: Deep research (Gemini/Grok/ChatGPT triangulation per §244), or Brave Brand Intelligence

### Step 2: SEO Copywriting
4. Using research output, write SEO-optimized copy for **every page**
5. One `.md` file per page: `homepage.md`, `about.md`, `services.md`, `blog.md`, `contact.md`
6. Structure each file by section: headline, sub-headline, problem, solution, benefits, CTA
7. Human review pass — AI gets 90%, you refine the remaining 10%

> [!IMPORTANT]
> ALL copy must be written and finalized BEFORE touching any design or code tool. Copy drives design.

### Step 3: Visual Design (Design System Separation)
8. Open [Variant AI](https://variant.ai) (or equivalent visual exploration tool)
9. Feed **hero section copy** first — this sets the design tone for the entire site
10. Prompt: *"Help me come up with designs for my homepage hero section that illustrate the copy really well. It should feel [adjectives matching brand]."*
11. Iterate on hero until locked — use "Shuffle layout" / "Vary strong" / "Vary subtle"
12. Once hero locked → **"New Chat from Design"** to carry design system forward
13. Feed remaining sections one by one: *"Following this design system, create the next section. Please use the copy exactly as I'm about to paste it."*
14. Build components section-by-section (don't worry about final page assembly)
15. Don't worry about logo placement or images — those are refined in code

> [!TIP]
> You only need to design the homepage in Variant. The coding AI can extrapolate the design system to remaining pages.

### Step 4: Code Build (Multi-Session)

**Session 1 — Skeleton**:
16. Create project folder locally
17. Export hero HTML from Variant (or copy code)
18. Prompt: *"I want to start building the homepage. This is the hero section and the design style we'll be following. Build section by section. I'll paste in HTML from designs we've already done."*
19. Transfer all designed sections from Variant into the codebase

**Session 2 — Copy Pass**:
20. Start new session (keeps context fresh)
21. Prompt: *"The design system is in place. Here is the actual copy. Ensure it matches the copy MD file. You have creative freedom on layout within the design system."*
22. Point to copy `.md` files

**Session 3 — Multi-Page Build**:
23. Start new session
24. Prompt: *"Build the remaining pages. Ensure the design style from homepage is used across all pages, keeping things clean and premium."*
25. Add copy `.md` files for each page
26. Claude will often auto-build all pages from the copy files

**Session 4 — Refinement**:
27. Add real images (human photos, brand assets, videos)
28. Add brand fonts and colors
29. Add sticky header/navigation
30. Mobile optimization pass
31. Performance pass (lazy loading, image optimization)
32. SEO meta tags, schema markup, sitemap

## Anti-Slop Checklist

Before shipping, verify:

- [ ] Real images (not AI-generated unless intentional)
- [ ] Brand fonts loaded (not system defaults)
- [ ] Consistent typography (max 2-3 font sizes per section)
- [ ] Human-in-the-loop design review (trust your gut — if it's not good enough, iterate)
- [ ] Copy matches finalized `.md` files exactly
- [ ] Mobile responsive
- [ ] Page speed acceptable
- [ ] SEO meta tags on every page

## Key Principle

> **Variant = Creative Director. Claude = Engineer.**
> Never ask the coding AI to be both designer and builder — that produces slop.

## Applicability

- Any web design client work
- Personal site redesigns
- Portfolio website updates
