---
created: 2026-01-30
last_updated: 2026-01-30
graphrag_extracted: true
---

---title: "Protocol 106: Sunset Protocol (Entropy Defense)"
type: "maintenance"
tags: ["entropy", "maintenance", "cleanup", "red-team"]
created: 2026-01-30
source: "Red-Team Audit 2026-01-30"
last_updated: 2026-01-30
---

# Protocol 106: Sunset Protocol

> **The Law**: "Complexity is a cancer. It must be cut out regularly."

## 1. The Entropy Physics

* **The Problem**: Knowledge Bases rot. Protocols proliferate. Indexing slows down.
* **The Cause**: We add files when excited (Dopamine), but never delete them when bored.
* **The Result**: "Index Bloat" -> Retrieval Speed Drops -> Retrieval Quality Drops -> System Abandonment.

## 2. The Sunset Mechanism (90-Day Rule)

Any "Skill File" or "Protocol" in `.agent/skills/` that has not been **accessed, read, or modified** in **90 Days** is considered "Dead Code".

### Execution Logic (The Reaper)

1. **Scan**: A cron job/script scans `last_accessed_at` metadata for all `.md` files in `.agent/`.
2. **Sort**: Files > 90 days dormant are flagged.
3. **Archive**: Flagged files are MOVED to `.agent/skills/archive/`.
    * *Note*: They are NOT deleted. They are just removed from the "Hot" Context Window availability.
4. **Log**: The Reaper logs the "death" in `Sunset_Log.md`.

## 3. The Resurrection

If a user specifically requests an archived protocol (e.g., "Where is the 2024 crypto strategy?"), the Agent can:

1. Search `archive/`.
2. Restore the file to `active/`.
3. Reset the 90-day timer.

## 4. Implementation (Target State)

* **Script**: `.agent/scripts/reaper.py`
* **Frequency**: Run on every `/diagnose` or Weekly reset.

---

> **Tags**: #maintenance #entropy #cleanup
