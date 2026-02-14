---
created: 2026-01-05
last_updated: 2026-01-30
---

---created: 2026-01-05
last_updated: 2026-01-05
---

# Protocol 273: Hybrid Prototyping Bridge (Gemini UI ⇄ Athena IDE)

> **Source**: Session 2026-01-05-15
> **Purpose**: The definitive workflow for "building fast" by leveraging the comparative advantage of Web UI (creative visualization) vs. IDE (structural engineering/deployment).

---

## 1. The Core Loop

| Stage | Platform | Role | Action |
| :--- | :--- | :--- | :--- |
| **01. Spark** | **Gemini Web UI** | *The Artist* | "Generate a landing page for [Niche]. Make it look premium." |
| **02. Harvest** | **Athena (IDE)** | *The Engineer* | `task_boundary` "Porting Design". Copy code to local repo. |
| **03. Inject** | **Athena (IDE)** | *The Integrator* | Generate assets (Images/Logos) locally. Inject into code. |
| **04. Deploy** | **GitHub/Terminal** | *The Publisher* | `git push` or `wrangler deploy`. Live URL in minutes. |

## 2. Why This Works (Comparative Advantage)

* **Gemini Web UI**:
  * **Pro**: 100x faster at "Vibe". Rendering visuals instantly allows for rapid "Yes/No" decisions.
  * **Con**: Code is trapped in chat. Zero deployment capability. "Fake" assets (Unsplash placeholders).
* **Athena (IDE)**:
  * **Pro**: Full file system access. Can generate *real* assets (Flux/Imagen). Can deploy to *real* URLs.
  * **Con**: Iterating on CSS "blind" is slower than seeing the Web UI preview.

## 3. Execution Checklist

1. [ ] **Prompt in Web UI**: Get the look right.
2. [ ] **Grab the HTML**: Copy the raw artifact.
3. [ ] **Scaffold**: Create local folder `projects/[name]`.
4. [ ] **Port**: Paste HTML into `index.html`.
5. [ ] **Asset Swap**:
    * Find instances of `unsplash.com` or placeholders.
    * Run `generate_image` tool in IDE to create proprietary assets.
    * Update `src` tags to local paths.
6. [ ] **Ship**: Push to GitHub Pages or Cloudflare.

## 4. Tagging

# workflow #hybrid-design #gemini #deployment #speed
