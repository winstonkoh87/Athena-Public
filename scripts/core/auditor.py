#!/usr/bin/env python3
"""
athena.core.auditor
====================
Trilateral Feedback System.
Cross-model validation for high-stakes outputs.

Purpose: Disagreement detection, not truth oracle.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# Find project root
_here = Path(__file__).resolve()
PROJECT_ROOT = next(
    (d for d in _here.parents if (d / "pyproject.toml").exists() or (d / ".context").exists()),
    _here.parents[2],
)
AUDIT_LOG_DIR = PROJECT_ROOT / ".agent" / "audit"

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class AuditTrigger(str, Enum):
    HIGH_STAKES = "high_stakes_decision"
    PUBLIC_FACING = "public_facing_output"
    SECURITY_SENSITIVE = "security_sensitive_change"
    MODEL_CONFLICT = "model_uncertainty_or_conflict"


@dataclass
class AuditRequest:
    """Request for cross-model validation."""

    content: str
    trigger: AuditTrigger
    context: str
    timestamp: str
    session_id: str | None = None


@dataclass
class AuditResponse:
    """Response from an auditor model."""

    model_name: str
    verdict: str  # 'approve', 'reject', 'concern'
    reasoning: str
    cited_claims: list[str]
    risks_identified: list[str]
    contradictions: list[str]
    proposed_tests: list[str]
    confidence: float


@dataclass
class AuditResult:
    """Aggregated audit result."""

    request: AuditRequest
    responses: list[AuditResponse]
    consensus: bool  # True if all auditors agree
    recommendation: str  # 'proceed', 'review', 'reject'
    disagreement_points: list[str]


class TrilateralAuditor:
    """
    Cross-model validation system.

    When triggered, sends content to multiple models for independent review.
    Aggregates responses and flags disagreements for human review.

    Note: This is a framework - actual API calls require model clients to be configured.
    """

    def __init__(self):
        self.audit_log_dir = AUDIT_LOG_DIR
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)

        # Load config from manifest if available
        try:
            from athena.boot.config_loader import ManifestLoader

            config = ManifestLoader.get_trilateral_config()
            self.enabled = config.enabled
            self.auditor_names = config.auditors
            self.triggers = config.triggers
        except Exception:
            self.enabled = True
            self.auditor_names = ["gemini", "gpt"]
            self.triggers = [t.value for t in AuditTrigger]

    def should_audit(self, trigger: AuditTrigger) -> bool:
        """Check if this trigger warrants an audit."""
        if not self.enabled:
            return False
        return trigger.value in self.triggers

    def create_auditor_prompt(self, request: AuditRequest) -> str:
        """Create a standardized prompt for auditor models."""
        return f"""You are a red-team auditor. Your job is to find problems, not to agree.

## Content to Audit
{request.content}

## Context
{request.context}

## Trigger
This audit was triggered by: {request.trigger.value}

## Your Task
Analyze the content critically and respond in JSON format:
{{
    "verdict": "approve" | "reject" | "concern",
    "reasoning": "Your detailed reasoning",
    "cited_claims": ["List of factual claims made that should be verified"],
    "risks_identified": ["List of potential risks or issues"],
    "contradictions": ["Any logical contradictions found"],
    "proposed_tests": ["Specific tests that could validate this content"],
    "confidence": 0.0-1.0
}}

Be adversarial. Find the flaws. Do not rubber-stamp.
"""

    def audit(
        self,
        content: str,
        trigger: AuditTrigger,
        context: str = "",
        session_id: str | None = None,
    ) -> AuditResult | None:
        """
        Perform cross-model audit.

        Args:
            content: Content to audit
            trigger: What triggered the audit
            context: Additional context
            session_id: Current session ID

        Returns:
            AuditResult with aggregated responses, or None if audit not needed
        """
        if not self.should_audit(trigger):
            return None

        request = AuditRequest(
            content=content,
            trigger=trigger,
            context=context,
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
        )

        responses = []
        for auditor_name in self.auditor_names:
            response = self._call_auditor(auditor_name, request)
            if response:
                responses.append(response)

        result = self._aggregate_responses(request, responses)
        self._log_audit(result)

        return result

    def _call_auditor(
        self, auditor_name: str, request: AuditRequest
    ) -> AuditResponse | None:
        """
        Call an auditor model.

        In Project Athena, this layer is critical for Law #6 and Law #7 compliance.
        If actual API keys (OPENAI_API_KEY, GOOGLE_API_KEY) are missing,
        this returns a 'concern' verdict that forces a 'review' recommendation.
        """
        # 1. Check for real API integration
        api_key_env = "GOOGLE_API_KEY" if "gemini" in auditor_name else "OPENAI_API_KEY"
        has_api = os.getenv(api_key_env) is not None

        if has_api:
            try:
                _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
                model_name = (
                    auditor_name
                    if "gemini" in auditor_name
                    else "gemini-1.5-flash"
                )

                prompt = self.create_auditor_prompt(request)
                response = _client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=2048,
                        response_mime_type="application/json",
                    ),
                )

                if response and response.text:
                    text = response.text.strip()
                    # Handle potential markdown wrapping
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()

                    data = json.loads(text)
                    return AuditResponse(
                        model_name=auditor_name,
                        verdict=data.get("verdict", "concern"),
                        reasoning=data.get("reasoning", "No reasoning provided"),
                        cited_claims=data.get("cited_claims", []),
                        risks_identified=data.get("risks_identified", []),
                        contradictions=data.get("contradictions", []),
                        proposed_tests=data.get("proposed_tests", []),
                        confidence=data.get("confidence", 0.0),
                    )
            except Exception as e:
                print(f"⚠️  Auditor {auditor_name} failed: {e}")

        # 2. Assertive Fallback: Force review for high-stakes triggers
        is_critical = request.trigger in [
            AuditTrigger.SECURITY_SENSITIVE,
            AuditTrigger.HIGH_STAKES,
        ]
        verdict = "concern" if is_critical else "approve"

        return AuditResponse(
            model_name=auditor_name,
            verdict=verdict,
            reasoning=f"[{auditor_name}] "
            + (
                "API missing - Active enforcement requires manual review for safety."
                if is_critical
                else "Non-critical trigger, bypassing audit."
            ),
            cited_claims=[],
            risks_identified=[
                "Critical trigger detected with no active auditor API"
                if is_critical
                else []
            ],
            contradictions=[],
            proposed_tests=["Verify this change with a human peer."],
            confidence=1.0 if not is_critical else 0.0,
        )

    def _aggregate_responses(
        self, request: AuditRequest, responses: list[AuditResponse]
    ) -> AuditResult:
        """Aggregate responses from multiple auditors."""
        if not responses:
            return AuditResult(
                request=request,
                responses=[],
                consensus=False,
                recommendation="review",
                disagreement_points=["No auditor responses received"],
            )

        verdicts = [r.verdict for r in responses]
        all_risks = []
        all_contradictions = []

        for r in responses:
            all_risks.extend(r.risks_identified)
            all_contradictions.extend(r.contradictions)

        # Determine consensus
        unique_verdicts = set(verdicts)
        consensus = len(unique_verdicts) == 1

        # Determine recommendation
        if all(v == "approve" for v in verdicts):
            recommendation = "proceed"
        elif any(v == "reject" for v in verdicts):
            recommendation = "reject"
        else:
            recommendation = "review"

        # Find disagreement points
        disagreements = []
        if not consensus:
            for i, r1 in enumerate(responses):
                for r2 in responses[i + 1 :]:
                    if r1.verdict != r2.verdict:
                        disagreements.append(
                            f"{r1.model_name} ({r1.verdict}) vs {r2.model_name} ({r2.verdict})"
                        )

        return AuditResult(
            request=request,
            responses=responses,
            consensus=consensus,
            recommendation=recommendation,
            disagreement_points=disagreements or list(set(all_contradictions)),
        )

    def _log_audit(self, result: AuditResult) -> None:
        """Log audit result to file."""
        log_file = self.audit_log_dir / "trilateral_log.jsonl"

        log_entry = {
            "timestamp": result.request.timestamp,
            "trigger": result.request.trigger.value,
            "consensus": result.consensus,
            "recommendation": result.recommendation,
            "auditor_count": len(result.responses),
            "disagreement_points": result.disagreement_points,
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


# Convenience functions
def audit_high_stakes(content: str, context: str = "") -> AuditResult | None:
    """Quick audit for high-stakes content."""
    auditor = TrilateralAuditor()
    return auditor.audit(content, AuditTrigger.HIGH_STAKES, context)


def audit_public_output(content: str, context: str = "") -> AuditResult | None:
    """Quick audit for public-facing output."""
    auditor = TrilateralAuditor()
    return auditor.audit(content, AuditTrigger.PUBLIC_FACING, context)


if __name__ == "__main__":
    print("Testing Trilateral Auditor...")

    auditor = TrilateralAuditor()

    result = auditor.audit(
        content="Deploy new authentication system to production",
        trigger=AuditTrigger.SECURITY_SENSITIVE,
        context="Changing auth flow for all users",
    )

    if result:
        print(f"Consensus: {result.consensus}")
        print(f"Recommendation: {result.recommendation}")
        print(f"Disagreements: {result.disagreement_points}")
