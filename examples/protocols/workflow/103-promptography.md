---

created: 2025-12-18
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2025-12-18
last_updated: 2026-01-11
---

# Protocol 103: Promptography (Visual Syntax)

> **Source**: Harvested from r/AI_UGC_Marketing (bertranddo)
> **Status**: ACTIVE
> **Purpose**: Structured prompting for accurate AI image generation

---

## 1. Core Concept

**Promptography** (Visual Syntax): The interaction between the prompt and image input(s) in image-to-image generation.

Key insight: **Image inputs and prompt params are interchangeable**. What you input as an image doesn't need to be described as text.

---

## 2. Master Prompt Structure

```
[DESIGN TYPE]: Photo, Vector, 3D, Illustration, etc.
[SUBJECT]: The Hero Object(s) — what the image is about
[VISUAL CHARACTER]: Mood, Action, Lighting, Emotional tone
[CONTEXT]: Environment, Setting, Location
[TECHNICAL]: Camera, Lens (Macro/Wide), Film type, Aperture
[STYLE/REFERENCE]: Aesthetic (Vogue, Cyberpunk, Editorial, etc.)
```

---

## 3. Example Application

**Task**: Teenager applying acne cream, Danish bathroom, editorial style

```
Prefix: "Using the provided images, create a..."

[DESIGN TYPE]: "Professional product photography... 9:16 vertical"
[SUBJECT]: "Teenage blonde girl from [image1]... holding cream jar from [image2]"
[VISUAL CHARACTER]: "Applying cream... Authentic, vulnerable vibe"
[CONTEXT]: "Danish Dansani bathroom, Douglas fir floor"
[TECHNICAL]: "Close-up... Sharp frosted glass... Soft-focus background"
[STYLE]: "Beige and soft pastel... LYSA brand alignment"
```

---

## 4. The Three Criteria for AI Photography

| Criterion | Question | Fail State |
|-----------|----------|------------|
| **Accuracy** | Does it represent product dimensions, colors, textures correctly? | Customer complaints, bad reviews |
| **Realism** | Does it look real, not plastic/AI-ish? | Trust erosion, "AI slop" detection |
| **On-Brand** | Does it incorporate brand identity, target ICP, correct environments? | Off-message, misaligned visuals |

---

## 5. Accuracy Techniques

### Reference Sheets

For dimensional accuracy, create reference sheets with descriptive language:

**Necklace Lengths:**

| Length | Position | Description |
|--------|----------|-------------|
| 45 cm | Base of neck | "tight around neck base" |
| 60 cm | Upper chest | "reaches upper chest" |
| 80 cm | Lower chest | "extends toward lower chest" |

**Pendant Sizes:**

| Size | Description |
|------|-------------|
| 1-2 cm | "very tiny minimalist pendant" |
| 3-4 cm | "very tiny refined pendant" |
| 5-6 cm | "small pendant resting on mid-chest" |

### Measurement Validation

1. **Physical Reference**: Use tape measure on real objects, compare to generated image
2. **Image Reference**: Compare against reference images with known dimensions
3. **LLM Measurement**: "Estimate the product's visible length using proportional visual references, output in table with cm/inches plus confidence note"

---

## 6. Image Transfer Technique

When product shape is too complex to describe:

1. Take iPhone photos focusing ONLY on composition
2. Ignore lighting, environment, mood in photo
3. Use photo as base reference for AI
4. AI enhances with environment, lighting, style
5. Product shape/proportions preserved from photo

---

## 7. Realism Techniques

- Avoid letting AI create people from scratch (Barbie/Ken effect)
- Use real photographer style references
- Specify technical details: "iPhone", specific lenses
- Add imperfections: "slight motion blur", "natural skin texture"
- Reference real film stocks: "Kodak Portra 400", "Fuji 400H"

---

## 8. Integration with Development Execution Standard (Visual Verification)

After generation, validate:

- [ ] Dimensions match reference sheet
- [ ] No AI artifacts (extra fingers, floating objects)
- [ ] Brand colors accurate
- [ ] Environment matches brief
- [ ] Would pass customer scrutiny (not "slop")

---

## Tagging

# protocol #image-generation #promptography #accuracy #realism
