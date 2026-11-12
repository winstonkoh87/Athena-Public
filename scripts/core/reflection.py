#!/usr/bin/env python3
"""
athena.core.reflection
=======================
Automatic reflection extraction on failures.
Implements the Reflexion pattern (Shinn et al., 2023).

Writes lessons, anti-patterns, and checklist items to persistent storage.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Find project root
_here = Path(__file__).resolve()
PROJECT_ROOT = next(
    (d for d in _here.parents if (d / "pyproject.toml").exists() or (d / ".context").exists()),
    _here.parents[2],
)
REFLECTIONS_DIR = PROJECT_ROOT / ".context" / "reflections"


class ReflectionType(str, Enum):
    LESSON = "lesson"
    ANTI_PATTERN = "anti_pattern"
    CHECKLIST_ITEM = "checklist_item"


@dataclass
class Reflection:
    """A single reflection entry."""

    type: ReflectionType
    title: str
    description: str
    context: str  # What was happening when this was learned
    trigger: (
        str  # What triggered the reflection (tool_failure, plan_failure, session_end)
    )
    timestamp: str
    session_id: str | None = None
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    def to_markdown(self) -> str:
        """Format as markdown for human readability."""
        return f"""## {self.title}

**Type**: {self.type.value}
**Trigger**: {self.trigger}
**Timestamp**: {self.timestamp}
**Tags**: {", ".join(self.tags) if self.tags else "none"}

### Context
{self.context}

### Description
{self.description}

---
"""


class ReflectionStore:
    """
    Persistent storage for reflections.
    Supports both JSON (machine) and Markdown (human) formats.
    """

    def __init__(self, store_dir: Path | None = None):
        self.store_dir = store_dir or REFLECTIONS_DIR
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.json_path = self.store_dir / "reflections.jsonl"
        self.md_path = self.store_dir / "LESSONS_LEARNED.md"

    def add(self, reflection: Reflection) -> None:
        """Add a reflection to the store."""
        # Append to JSONL
        with open(self.json_path, "a") as f:
            f.write(json.dumps(reflection.to_dict()) + "\n")

        # Append to Markdown
        with open(self.md_path, "a") as f:
            f.write(reflection.to_markdown())

    def get_all(self) -> list[Reflection]:
        """Load all reflections from store."""
        if not self.json_path.exists():
            return []

        reflections = []
        with open(self.json_path) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    data["type"] = ReflectionType(data["type"])
                    reflections.append(Reflection(**data))

        return reflections

    def search(
        self, query: str, type_filter: ReflectionType | None = None
    ) -> list[Reflection]:
        """Search reflections by content."""
        query_lower = query.lower()
        results = []

        for ref in self.get_all():
            if type_filter and ref.type != type_filter:
                continue

            # Simple text matching
            if (
                query_lower in ref.title.lower()
                or query_lower in ref.description.lower()
                or query_lower in ref.context.lower()
            ):
                results.append(ref)

        return results

    def get_recent(self, n: int = 5) -> list[Reflection]:
        """Get the N most recent reflections."""
        all_refs = self.get_all()
        return all_refs[-n:]


class ReflectionExtractor:
    """
    Extracts reflections from failures and session events.

    Triggers:
    - tool_failure: A tool call returned an error
    - plan_failure: A multi-step plan failed to complete
    - session_end: End of session reflection
    """

    def __init__(self):
        self.store = ReflectionStore()

    def on_tool_failure(
        self,
        tool_name: str,
        error_message: str,
        context: str,
        session_id: str | None = None,
    ) -> Reflection:
        """
        Extract lesson from a tool failure.

        Args:
            tool_name: Name of the failed tool
            error_message: Error message received
            context: What was being attempted
            session_id: Current session ID

        Returns:
            The created reflection
        """
        reflection = Reflection(
            type=ReflectionType.ANTI_PATTERN,
            title=f"Tool Failure: {tool_name}",
            description=f"Error: {error_message}\n\nLesson: Verify preconditions before calling {tool_name}.",
            context=context,
            trigger="tool_failure",
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            tags=[tool_name, "failure", "tool"],
        )

        self.store.add(reflection)
        return reflection

    def on_plan_failure(
        self,
        plan_description: str,
        failure_point: str,
        root_cause: str,
        session_id: str | None = None,
    ) -> Reflection:
        """Extract lesson from a plan failure."""
        reflection = Reflection(
            type=ReflectionType.LESSON,
            title=f"Plan Failure: {plan_description[:50]}...",
            description=f"Failed at: {failure_point}\n\nRoot cause: {root_cause}",
            context=plan_description,
            trigger="plan_failure",
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            tags=["planning", "failure"],
        )

        self.store.add(reflection)
        return reflection

    def on_session_end(
        self,
        session_summary: str,
        key_decisions: list[str],
        session_id: str | None = None,
    ) -> list[Reflection]:
        """Extract checklist items from session end."""
        reflections = []

        for decision in key_decisions:
            reflection = Reflection(
                type=ReflectionType.CHECKLIST_ITEM,
                title=f"Decision: {decision[:50]}...",
                description=decision,
                context=session_summary,
                trigger="session_end",
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                tags=["decision", "session"],
            )
            self.store.add(reflection)
            reflections.append(reflection)

        return reflections

    def recall_relevant(self, context: str, limit: int = 3) -> list[Reflection]:
        """Recall reflections relevant to current context."""
        # Extract keywords from context
        keywords = [w for w in context.lower().split() if len(w) > 4]

        all_matches = []
        for keyword in keywords[:5]:  # Limit keyword search
            matches = self.store.search(keyword)
            all_matches.extend(matches)

        # Deduplicate
        seen = set()
        unique = []
        for ref in all_matches:
            key = (ref.title, ref.timestamp)
            if key not in seen:
                seen.add(key)
                unique.append(ref)

        return unique[:limit]


# Convenience functions
def record_failure(tool_name: str, error: str, context: str) -> Reflection:
    """Quick access to record a tool failure."""
    extractor = ReflectionExtractor()
    return extractor.on_tool_failure(tool_name, error, context)


def recall_lessons(context: str) -> list[Reflection]:
    """Quick access to recall relevant lessons."""
    extractor = ReflectionExtractor()
    return extractor.recall_relevant(context)


if __name__ == "__main__":
    # Test the reflection system
    print("Testing Reflection Extractor...")

    extractor = ReflectionExtractor()

    # Simulate a tool failure
    ref = extractor.on_tool_failure(
        tool_name="replace_file_content",
        error_message="Content mismatch: expected 'foo' but found 'bar'",
        context="Attempting to update project_state.md with new session entry",
        session_id="test-session-001",
    )

    print(f"Created reflection: {ref.title}")
    print(f"Stored at: {extractor.store.json_path}")

    # Recall
    relevant = extractor.recall_relevant("update project state")
    print(f"Found {len(relevant)} relevant reflections")
