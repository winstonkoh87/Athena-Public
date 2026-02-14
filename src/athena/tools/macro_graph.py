#!/usr/bin/env python3
"""
athena.tools.macro_graph
========================
Automatically regenerates the .context/KNOWLEDGE_GRAPH.md file.
Reflects the actual workspace structure in a Mermaid diagram.
"""

from pathlib import Path
import os
import sys

# SDK Imports
SDK_PATH = Path(__file__).resolve().parent.parent.parent
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.config import PROJECT_ROOT

GRAPH_FILE = PROJECT_ROOT / ".context" / "KNOWLEDGE_GRAPH.md"


def generate_mermaid() -> str:
    """Generate Mermaid graph code based on actual existence of directories."""

    # Check for actual presence to avoid ghost nodes
    nodes = {
        "CI": PROJECT_ROOT
        / ".framework"
        / "v8.6-stable"
        / "modules"
        / "Core_Identity.md",
        "PR": PROJECT_ROOT / ".agent" / "skills" / "protocols",
        "CS": PROJECT_ROOT / ".context" / "memories" / "case_studies",
        "SL": PROJECT_ROOT / ".context" / "memories" / "session_logs",
        "SDK": PROJECT_ROOT / "src" / "athena",
        "PUB": PROJECT_ROOT / "Athena-Public",
        "MKT": PROJECT_ROOT / ".context" / "marketing",
    }

    # Filter only existing ones
    exists = {k: v.exists() for k, v in nodes.items()}

    mermaid = """graph TB
    subgraph CORE["🧠 CORE (Identity & SDK)"]
        CI[Core_Identity.md]
        SDK[Athena SDK]
    end

    subgraph MEMORY["💾 LONG-TERM MEMORY"]
        CS[Case Studies]
        SL[Session Logs]
    end

    subgraph SKILLS["⚔️ SKILLS & PROTOCOLS"]
        PR[Protocols]
        WF[Workflows]
    end

    subgraph OFFENSE["🚀 DISTRIBUTION & OFFENSE"]
        PUB[Athena-Public Repo]
        MKT[Marketing Automation]
    end

    %% Flow
    CI --> SDK
    SDK --> PR
    SDK --> SL
    SL --> CS
    PR --> CS
    
    SDK --> PUB
    SDK --> MKT
    MKT --> PUB

    style CI fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
    style SDK fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style PUB fill:#FF9800,stroke:#EF6C00,stroke-width:2px
    style MKT fill:#E91E63,stroke:#880E4F,stroke-width:2px
"""
    return mermaid


def regenerate_file():
    """Write the new graph to the KB."""
    print("🕸️ Regenerating Macro Knowledge Graph...")
    mermaid = generate_mermaid()

    content = f"""# Workspace Knowledge Graph (Macro View)

> **Purpose**: Automated visual reference for the Athena structure.
> **Last Updated**: {Path(GRAPH_FILE).stat().st_mtime if GRAPH_FILE.exists() else "Just now"} (Auto-generated)

---

```mermaid
{mermaid}
```

---

## Node Legend

| Cluster | Purpose | Focus |
|---------|---------|-------|
| 🧠 CORE | Identity, SDK, and Autonomic processes | Stabilization |
| 💾 MEMORY | Session history and extracted knowledge | Persistence |
| ⚔️ SKILLS | Procedural knowledge and structured workflows | Capability |
| 🚀 OFFENSE | Distribution, Public Sync, and Marketing | Growth |

---

#documentation #knowledge-graph #automated
"""
    GRAPH_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Knowledge Graph updated: {GRAPH_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    regenerate_file()
