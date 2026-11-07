# ==============================================================================
# Athena-Public — Local-First Cognitive Infrastructure & Agent Governance
# ==============================================================================
.PHONY: help install install-dev test test-fast test-cov lint typecheck privacy-check check-all clean

PYTHON ?= python3

help:
	@echo "Athena-Public — Standard Development Commands"
	@echo "  make install         Install core package and dependencies in editable mode"
	@echo "  make install-dev     Install development and testing dependencies"
	@echo "  make test            Run full pytest test suite"
	@echo "  make test-fast       Run core fast unit tests"
	@echo "  make test-cov        Run test suite with test coverage reporting"
	@echo "  make lint            Run ruff code linter across source, scripts, and tests"
	@echo "  make typecheck       Run mypy static type checking"
	@echo "  make privacy-check   Run privacy scan against blocklist and PII patterns"
	@echo "  make check-all       Run all verification gates (lint, typecheck, privacy, test)"
	@echo "  make clean           Clean bytecode, coverage, and cache artifacts"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pip install mypy pip-audit

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-fast:
	$(PYTHON) -m pytest tests/test_agent_gate.py tests/test_eval_harness.py tests/test_gto_engine.py tests/test_trade_guardian.py tests/test_gto_engine_capabilities.py -q

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=src/athena --cov-report=term-missing --cov-fail-under=15

lint:
	ruff check src/ scripts/ tests/
	ruff check examples/ --select F821,F822,F823,E9

typecheck:
	mypy src/athena/ --ignore-missing-imports --no-error-summary

privacy-check:
	$(PYTHON) .github/scripts/privacy_scan.py --all

check-all: lint typecheck privacy-check test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov build dist
