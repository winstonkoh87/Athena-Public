---
type: protocol
id: 108
title: Semantic Search Standards
created: 2026-02-14
source: Cursor Agent System Prompt
tags: [coding, guidelines, search, context]
author: Athena (via Cursor)
---

# Protocol 108: Semantic Search Standards

> **Philosophy**: "Ask specific questions to get specific answers."
> **Origin**: Adapted from the **Cursor Agent** system prompt (Leaked Feb 2026).
> **Purpose**: To maximize the effectiveness of `smart_search.py` (semantic search) and `codebase_search` tools.

## 1. Principles of Effective Search

Semantic search works by embedding meaning, not keywords. Therefore, queries must be phrased as **Natural Language Questions**, not keyword fragments.

### The Golden Rule
>
> **BAD**: "AuthService"
> **GOOD**: "How does the AuthService handle token validation?"

## 2. Query Guidelines

### 2.1 Be Specific

Ask exactly what you want to know. Avoid vague terms like "logic" or "implementation" without context.

**Examples**:

- ❌ "User logic"
- ✅ "Where are user profile updates handled in the backend?"
- ❌ "Database schema"
- ✅ "How is the `users` table defined in the migration files?"

### 2.2 Don't Combine Questions

Semantic search embeddings get confused by multi-part questions. Split them.

- ❌ "How does auth work and where are the API routes?"
- ✅ "How does the authentication flow work?" (Query 1)
- ✅ "Where are the API routes defined?" (Query 2)

### 2.3 Use Code Context

Include variable names or function signatures if you know them, but wrap them in context.

- ❌ "processOrder"
- ✅ "Where is the `processOrder` function called in the checkout flow?"

## 3. Search Strategy (The Funnel)

1. **Exploratory (Broad)**
    - *Query*: "How does the payment system handle webhooks?"
    - *Scope*: `[]` (Entire Repo)
    - *Goal*: Identify key files/directories.

2. **Targeted (Narrow)**
    - *Query*: "Where is stripe signature validation implemented?"
    - *Scope*: `['src/payments/webhooks']` (Specific Directory)
    - *Goal*: Pinpoint exact logic.

3. **Specific (Precision)**
    - *Query*: "What error types does the `validateSignature` function throw?"
    - *Scope*: `['src/payments/utils/validation.ts']` (Specific File)
    - *Goal*: Understand edge cases.

## 4. When to Use What

| Goal | Tool | Strategy |
|------|------|----------|
| **Concept/Understanding** | `smart_search` | Ask "How/Why" questions. |
| **Exact String Location** | `grep` / `ripgrep` | Use unique strings/error codes. |
| **File Location** | `find_file` | Use filename patterns. |
| **Definition Lookup** | `read_file` | Read the file directly if location is known. |

## 5. Anti-Patterns (What NOT to do)

- **Keyword Stacking**: `auth login user token` -> Returns garbage. Use a sentence.
- **Vague Nouns**: `backend` -> Too broad. Be specific.
- **Assuming Knowledge**: Don't assume you know the file structure. Search first.

---

**Autonomic Trigger**: When formulating a `smart_search` query, run this protocol mentally against the candidate query. If it fails the guidelines, rewrite it.
