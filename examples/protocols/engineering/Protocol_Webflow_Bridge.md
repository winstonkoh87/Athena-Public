---

created: 2026-01-13
last_updated: 2026-01-30
graphrag_extracted: true
---

---created: 2026-01-13
last_updated: 2026-01-13
---

# Protocol 66: Webflow Bridge (Hybrid Code)

> **Role**: Interface
> **Status**: Active
> **Version**: 1.0

## 1. Core Philosophy: The Separation of Concerns

We treat Webflow not as a "No-Code" builder, but as a **High-Fidelity Renderer**.

- **Webflow**: Handling Hosting, CMS, Visual CSS, DOM Structure.
- **Athena**: Handling Business Logic, API Integrations, Complex State, Calculations.

## 2. The Binding System (Data Attributes)

Never rely on Webflow automatic class names (which change). Use **Data Attributes** to bind logic to the DOM.

| Attribute | Value Example | Purpose |
| :--- | :--- | :--- |
| `data-athena` | `calculator-wrapper` | The scope for a specific logic component. |
| `data-bind` | `input-age` | Binding a specific input field. |
| `data-trigger` | `submit-calc` | Binding a click event. |
| `data-state` | `loading` | CSS hooks for state changes (managed by JS). |

**Example**:

```html
<div data-athena="mortgage-calc">
  <input type="text" data-bind="loan-amount">
  <button data-trigger="calculate">Calculate</button>
  <div data-bind="result-display"></div>
</div>
```

## 3. Standard Utility Classes

Add these to the Webflow "Style Guide" page to ensure the code can manipulate visibility without conflict.

- `.u-cloak` -> `opacity: 0` (Hides element until JS loads to prevent flash)
- `.u-hidden` -> `display: none !important` (Hard hide)
- `.is-active` -> (State class for toggles)

## 4. The Injection Workflow

1. **Develop**: Athena writes the functionality in a local `.js` file (e.g., `calculator.js`).
2. **Test**: We test logic locally using `index.html`.
3. **Deploy**:
    - **Option A (Small)**: Paste script inside `<script>` tags in the page **"Before </body> tag"** settings.
    - **Option B (Large)**: Host the `.js` file on GitHub Pages/CDN and `<script src="...">` it.

## 5. Security Rules

- **No API Keys**: Never put private API keys in Webflow client-side code. Use a Middleware (Cloudflare Worker or Vercel Function) if secrets are needed.
- **Input Sanitization**: Always validate inputs in JS before processing.
