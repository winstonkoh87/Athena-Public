"""
Athena Governance Engine

Enforces the Triple-Lock protocol (Semantic Search → Web Search → Quicksave)
to ensure all AI interactions are properly grounded before checkpointing.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any


class GovernanceEngine:
    """
    Governance Engine for Project Athena.
    Enforces autonomic Triple-Lock protocol (Search → Web → Save).

    The Triple-Lock ensures:
    1. Semantic Search: Query the knowledge base before responding
    2. Web Research: External grounding when applicable
    3. Quicksave: Checkpoint the session with verified context
    """

    def __init__(self, state_dir: Path = None):
        if state_dir is None:
            # Backward compat: try importing AGENT_DIR, fall back to ~/.athena
            try:
                from athena.core.config import AGENT_DIR

                self.state_dir = AGENT_DIR / "state"
            except ImportError:
                self.state_dir = Path.home() / ".athena" / "state"
        else:
            self.state_dir = state_dir
        self.state_file = self.state_dir / "exchange_state.json"
        self._state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {
            "semantic_search_performed": False,
            "web_search_performed": False,
            "last_search_time": 0,
        }

    def _save_state(self):
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps(self._state))
        except Exception:
            pass

    def mark_search_performed(self, query: str):
        """Register that a semantic search was performed for the current turn."""
        self._state["semantic_search_performed"] = True
        self._state["last_search_time"] = time.time()
        self._save_state()

    def mark_web_search_performed(self, query: str):
        """Register that a web search was performed for the current turn."""
        self._state["web_search_performed"] = True
        self._save_state()

    def verify_exchange_integrity(self) -> bool:
        """
        Verify if the Triple-Lock protocols were followed.
        Returns True if both Semantic Search AND Web Search were performed.
        Resets state after check.
        """
        semantic = self._state.get("semantic_search_performed", False)
        web = self._state.get("web_search_performed", False)

        integrity = semantic and web

        # Reset for next turn
        self._state["semantic_search_performed"] = False
        self._state["web_search_performed"] = False
        self._save_state()

        return integrity

    def get_integrity_score(self) -> float:
        """
        Calculate current integrity score based on protocol compliance.
        Returns 1.0 if Triple-Lock is satisfied, 0.0 otherwise.
        """
        semantic = self._state.get("semantic_search_performed", False)
        web = self._state.get("web_search_performed", False)
        return 1.0 if (semantic and web) else 0.0


# Singleton instance (lazy)
_governance_engine = None


def get_governance() -> GovernanceEngine:
    """Get the singleton governance engine instance."""
    global _governance_engine
    if _governance_engine is None:
        _governance_engine = GovernanceEngine()
    return _governance_engine
