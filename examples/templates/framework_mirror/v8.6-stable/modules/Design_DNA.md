---
created: 2026-02-03
last_updated: 2026-02-03
graphrag_extracted: true
---

# Design DNA (The Aesthetic Constitution)

> **Purpose**: Immutable design defaults to prevent "Generic AI Slop" aesthetics.
> **Origin**: Stolen from "Claude Code vs Antigravity" Analysis (Calming > Crypto).
> **Trigger**: Applied to ALL new web apps unless explicitly overridden.

---

## 1. The Core Vibe: "Premium Calm"

**The Rule**: We do not build "dashboards." We build **Sanctuaries**.
The user should feel *slower* and *calmer* when they open our apps, not amped up.

| Element | Default Setting | Banned (The "Crypto" Look) |
| :--- | :--- | :--- |
| **Radius** | `rounded-xl` or `rounded-2xl` | `rounded-none` or `rounded-sm` |
| **Shadows** | `shadow-lg` + `shadow-slate-200/50` | Hard black shadows, Neon glows |
| **Borders** | `border-slate-100` (Subtle) | `border-blue-500` (High contrast) |
| **Bg** | White / Slate-50 / Grainy Noise | Pitch Black / Grid Lines |

---

## 2. Typography Stack (The Voice)

**Primary**: **Inter** (The Gold Standard)
**Secondary**: **Plus Jakarta Sans** (For friendlier headers) or **Outfit** (For modern crispness).

**Hierarchy**:

- **H1**: `text-4xl font-semibold tracking-tight text-slate-900`
- **Body**: `text-base text-slate-600 leading-relaxed`
- **Label**: `text-xs font-medium uppercase tracking-wider text-slate-400`

> **Note**: Never use pure black (`#000000`). Use `text-slate-900`.

---

## 3. Color Palette: "The Wellness Stack"

Avoid the "Default Blue" (`blue-500`). Use refined, desaturated tones.

### The "Calm" Palette (Default)

- **Primary**: `indigo-500` (Soft Purple-Blue) → `hover:indigo-600`
- **Surface**: `slate-50` (Off-white)
- **Text**: `slate-600` (Soft Grey)
- **Success**: `emerald-500` (Natural Green)
- **Error**: `rose-500` (Soft Red)

### The "Glass" Effect

- **Panel**: `bg-white/70 backdrop-blur-md border border-white/20 shadow-xl`
- **Context**: Use for floating cards, navbars, and modals.

---

## 4. Component DNA

### Buttons

- **Style**: `rounded-full px-6 py-2.5 font-medium transition-all active:scale-95`
- **Primary**: `bg-slate-900 text-white hover:bg-slate-800 shadow-lg shadow-slate-900/20`
- **Secondary**: `bg-white text-slate-600 border border-slate-200 hover:bg-slate-50`

### Inputs

- **Style**: `bg-slate-50 border-0 ring-1 ring-slate-200 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all`

### Cards

- **Style**: `bg-white rounded-2xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow duration-300`

---

## 5. Animation (The "Alive" Feel)

Static interfaces feel dead. Use **Micro-Interactions**.

- **Hover**: Power elements must lift (`-translate-y-0.5`).
- **Click**: Buttons must press (`scale-95`).
- **Load**: Content must fade in (`animate-fade-in-up`).

---

## 6. Metadata

# design #ui #ux #aesthetic #dna #calming
