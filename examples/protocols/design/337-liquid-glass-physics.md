---
title: "Liquid Glass: Interface Physics"
id: 337
type: design
author: [AUTHOR] (Antigravity)
created: 2026-02-12
tags: [design, ui, ux, framer-motion, glassmorphism]
source: "Explore-Singapore (Aditya Prasad)"
---

# Protocol 337: Liquid Glass (Interface Physics)

> **Philosophy**: "It shouldn't just look good; it should feel alive."
> **Mission**: Deprecate "Static UI" for "Kinetic Interfaces."

## 1. The Aesthetic: Liquid Glass

We move beyond flat design to **Material Intelligence**.
The interface simulates a physical pane of glass that reacts to presence.

### 1.1 The Texture (Glassmorphism)

- **Background**: `rgba(255, 255, 255, 0.05)` (Ultra-thin)
- **Blur**: `backdrop-filter: blur(25px)` (Heavy frost)
- **Border**: `1px solid rgba(255, 255, 255, 0.1)` (Subtle rim)
- **Shadow**: `0 8px 32px 0 rgba(31, 38, 135, 0.37)` (Deep ambient)

### 1.2 The Physics (Springs > Durations)

Linear transitions (`0.3s ease-in-out`) are dead. We use **Spring Physics**.

**Standard Config (Framer Motion):**

```javascript
transition: {
  type: "spring",
  stiffness: 400,
  damping: 30,
  mass: 1
}
```

## 2. Interactive States

### Hover: Lateral Expansion

Elements don't just "highlight"; they **displace**.

- **Action**: `x: 10` (Slide right)
- **Feedback**: A subtle resistance, like pushing a physical object.

### Click: Tactile Compression

- **Action**: `scale: 0.95`
- **Sound**: Subtle 15ms click (optional).

## 3. Typographic Pairing

To balance the "soft" glass, we use "hard" typography.

- **Font**: San Francisco (SF Pro) or Inter.
- **Weight**: 400/600 pairings.
- **Tracking**: `-0.02em` (Tight).

## 4. Implementation Snippet (React)

```jsx
<motion.div
  className="glass-panel"
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  whileHover={{ 
    x: 5, 
    filter: "brightness(1.2)",
    boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.50)" 
  }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
  style={{
    background: "rgba(255, 255, 255, 0.05)",
    backdropFilter: "blur(25px)",
    borderRadius: "16px",
    border: "1px solid rgba(255, 255, 255, 0.1)"
  }}
>
  {children}
</motion.div>
```

## 5. Usage

- **Dashboards**: Mandatory.
- **Widgets**: Mandatory.
- **Documents**: Optional (Readability first).

---
**Tags**: #protocol #ui #ux #design #glassmorphism #framer-motion #interface-physics
