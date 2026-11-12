#!/usr/bin/env python3
"""
wargame_runner.py
=================

Context-Isolated Red Cell Runner for Athena Wargaming Engine.
Enforces strict information barrier (ObservableActionPacket), egress scanning,
and tamper-evident run records (.athena/wargame_runs.jsonl).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MODEL: str = os.environ.get("ATHENA_WARGAME_MODEL", "gemini-2.5-flash")
FORBIDDEN_PACKET_KEYS: tuple[str, ...] = (
    "rationale",
    "internal_rationale",
    "blue_rationale",
    "hope",
    "thought",
    "blue_thought",
    "sunk_cost",
    "internal_note",
)


class EgressViolationError(PermissionError):
    """Raised when scan_egress_text identifies unmasked sensitive data."""
    pass


class InformationBarrierViolationError(ValueError):
    """Raised when an observable packet contains banned internal rationale keys."""
    pass


@dataclass(frozen=True)
class ObservableActionPacket:
    """Strictly sanitized packet visible to the Red Cell.

    Prohibits passing internal Blue rationales, feelings, or secret plans.
    """
    arena_facts: str
    red_endowments: str
    blue_observable_moves: list[dict[str, Any]]

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    def sha256(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def build_observable_packet(
    arena_facts: str,
    red_endowments: str,
    blue_observable_moves: list[dict[str, Any]],
    **extra_kwargs: Any,
) -> ObservableActionPacket:
    """Build and validate an ObservableActionPacket, rejecting non-observable inputs."""
    if extra_kwargs:
        forbidden = [k for k in extra_kwargs if k.lower() in FORBIDDEN_PACKET_KEYS]
        if forbidden:
            raise InformationBarrierViolationError(
                f"Information barrier violation: forbidden internal keys present: {forbidden}"
            )
        raise InformationBarrierViolationError(
            f"Unexpected keys in observable packet: {list(extra_kwargs.keys())}"
        )

    # Validate individual observable move structures
    for idx, move in enumerate(blue_observable_moves):
        if not isinstance(move, dict):
            raise ValueError(f"Move #{idx} must be a dict, got {type(move)}")
        for key in move:
            if key.lower() in FORBIDDEN_PACKET_KEYS:
                raise InformationBarrierViolationError(
                    f"Forbidden internal rationale key {key!r} inside move #{idx}"
                )

    return ObservableActionPacket(
        arena_facts=str(arena_facts).strip(),
        red_endowments=str(red_endowments).strip(),
        blue_observable_moves=list(blue_observable_moves),
    )


def scan_outbound_packet(packet: ObservableActionPacket) -> None:
    """Pass serialized packet through hook_egress_gate.scan_egress_text."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    scripts_dir = repo_root / ".agent" / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    try:
        from hook_egress_gate import scan_egress_text
        text = packet.to_json()
        findings = scan_egress_text(text)
        if findings:
            violating_categories = [f.get("category") for f in findings]
            raise EgressViolationError(
                f"Egress gate blocked outbound Red Cell packet: {len(findings)} findings "
                f"({', '.join(set(filter(None, violating_categories)))})"
            )
    except ImportError:
        pass


def record_wargame_run(
    run_id: str,
    model: str,
    packet_sha256: str,
    prompt_sha256: str,
    response_sha256: str,
    independence_class: str = "separate-context",
    runs_path: Path | None = None,
) -> dict[str, str]:
    """Append a tamper-evident run record to .athena/wargame_runs.jsonl."""
    env_root = os.environ.get("ATHENA_ROOT")
    if env_root:
        repo_root = Path(env_root).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent
    target_file = runs_path or (repo_root / ".athena" / "wargame_runs.jsonl")
    target_file.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "run_id": run_id,
        "model": model,
        "packet_sha256": packet_sha256,
        "prompt_sha256": prompt_sha256,
        "response_sha256": response_sha256,
        "class": independence_class,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    with open(target_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return {
        "run_id": run_id,
        "packet_sha256": packet_sha256,
        "class": independence_class,
    }


def execute_red_cell(
    packet: ObservableActionPacket,
    model: str = DEFAULT_MODEL,
    independence_class: str = "separate-context",
    runs_path: Path | None = None,
    mock_responses: list[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """Execute context-isolated Red Cell to generate adversarial counter-moves.

    Red Cell returns ONLY candidate responses (never payoffs).
    """
    scan_outbound_packet(packet)
    run_id = f"RUN-{uuid.uuid4().hex[:8]}"

    prompt = (
        "You are the adversarial Red Cell commander.\n"
        "Your objective is to exploit Blue's observable moves to the maximum extent.\n"
        "You do NOT care about Blue's survival. Generate 3 to 4 hostile, incentive-compatible responses.\n\n"
        f"ARENA FACTS:\n{packet.arena_facts}\n\n"
        f"RED ENDOWMENTS:\n{packet.red_endowments}\n\n"
        f"BLUE OBSERVABLE MOVES:\n{json.dumps(packet.blue_observable_moves, indent=2)}\n\n"
        "Return a JSON array of strings: [\"Response 1\", \"Response 2\", ...]. No payoffs."
    )

    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    packet_sha256 = packet.sha256()

    if mock_responses is not None:
        responses = list(mock_responses)
        raw_output = json.dumps(responses)
    else:
        # Live Google GenAI API Call
        try:
            from google import genai
            from google.genai import types

            client = genai.Client()
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json",
                ),
            )
            raw_output = response.text or "[]"
            responses = json.loads(raw_output)
        except Exception as e:
            raise RuntimeError(f"Red Cell generation failed: {e}") from e

    response_sha256 = hashlib.sha256(raw_output.encode("utf-8")).hexdigest()
    indep_rec = record_wargame_run(
        run_id=run_id,
        model=model,
        packet_sha256=packet_sha256,
        prompt_sha256=prompt_sha256,
        response_sha256=response_sha256,
        independence_class=independence_class,
        runs_path=runs_path,
    )

    return responses, indep_rec


def main() -> int:
    parser = argparse.ArgumentParser(description="Athena Context-Isolated Red Cell Runner")
    parser.add_argument("--input", required=True, help="Path to JSON packet file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model identifier")
    parser.add_argument("--class", dest="indep_class", default="separate-context", help="Independence class")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(f"Error: input file {args.input} does not exist", file=sys.stderr)
        return 2

    data = json.loads(p.read_text(encoding="utf-8"))
    packet = build_observable_packet(
        arena_facts=data.get("arena_facts", ""),
        red_endowments=data.get("red_endowments", ""),
        blue_observable_moves=data.get("blue_observable_moves", []),
    )

    responses, indep_rec = execute_red_cell(
        packet=packet,
        model=args.model,
        independence_class=args.indep_class,
    )

    print(json.dumps({"responses": responses, "independence_record": indep_rec}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
