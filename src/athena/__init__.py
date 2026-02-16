"""
Athena SDK
==========

The programmatic core of the Athena Bionic OS.

Modules:
- core: Runtime, identity, and orchestration primitives.
- memory: Context management, vector DB interfaces.
- tools: Agent tool implementations.
- cli: Command-line interface for workspace management.

Usage:
    python -m athena              # Boot the orchestrator
    python -m athena init         # Initialize a new workspace
    python -m athena --doctor     # Run system health check
    python -m athena --end        # Shutdown sequence
    python -m athena --help       # Show help
"""

__version__ = "9.2.0"

# Auto-load environment variables on import
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional for minimal installs
