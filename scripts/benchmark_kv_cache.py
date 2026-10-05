#!/usr/bin/env python3
"""
benchmark_kv_cache.py — Local LLM TTFT & KV Cache Scaling Benchmark
===================================================================
Measures Time to First Token (TTFT), generation throughput (tokens/s),
and VRAM footprint across context depths (2K, 8K, 16K, 32K tokens) on
local Ollama or llama.cpp servers.

Designed to provide reproducible empirical receipts for context distillation
trade-offs (e.g., Athena 2K surgical boot vs. monolithic 32K context).

Usage:
    python3 .agent/scripts/benchmark_kv_cache.py --model qwen2.5-coder:14b
    python3 .agent/scripts/benchmark_kv_cache.py --endpoint http://localhost:8080/v1 --model local-model
    python3 .agent/scripts/benchmark_kv_cache.py --sizes 2048 8192 16384 32768
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def get_gpu_memory_used_mb() -> int | None:
    """Query nvidia-smi if available to track VRAM usage."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        )
        lines = out.strip().split("\n")
        if lines and lines[0].strip().isdigit():
            return int(lines[0].strip())
    except Exception:
        pass
    return None


def get_ollama_vram_mb(base_url: str) -> int | None:
    """Query Ollama's /api/ps endpoint to inspect loaded model VRAM allocation."""
    try:
        # Normalize base URL from /v1 to /api/ps
        root_url = base_url.replace("/v1", "").rstrip("/")
        ps_url = f"{root_url}/api/ps"
        req = urllib.request.Request(ps_url)
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            if models:
                vram_bytes = models[0].get("size_vram", 0)
                if vram_bytes:
                    return int(vram_bytes // (1024 * 1024))
    except Exception:
        pass
    return None


def generate_synthetic_code_context(approx_tokens: int) -> str:
    """Generate deterministic, structured technical context matching real codebases."""
    # ~4.2 chars per token in code/markdown
    block = (
        "def verify_data_contract(payload: dict) -> bool:\n"
        "    # Check data contract invariants and schema constraints\n"
        "    if not payload.get('session_id'):\n"
        "        raise ValueError('Missing session identifier')\n"
        "    return payload.get('status') == 'ACTIVE'\n\n"
    )
    multiplier = max(1, int((approx_tokens * 4.2) // len(block)))
    return (block * multiplier)[: int(approx_tokens * 4.2)]


def run_benchmark_trial(
    endpoint: str,
    model: str,
    tokens: int,
    timeout_sec: int = 120,
) -> dict[str, Any]:
    """Run a single streaming trial against an OpenAI-compatible endpoint."""
    prompt_content = generate_synthetic_code_context(tokens)
    url = f"{endpoint.rstrip('/')}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a deterministic code verification harness.",
            },
            {
                "role": "user",
                "content": f"{prompt_content}\n\nTask: Output the exact word 'VERIFIED' and nothing else.",
            },
        ],
        "max_tokens": 16,
        "temperature": 0.0,
        "stream": True,
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={"Content-Type": "application/json"},
    )

    t_start = time.perf_counter()
    ttft: float | None = None
    generated_tokens = 0

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            for line in resp:
                raw_line = line.decode("utf-8").strip()
                if not raw_line.startswith("data: "):
                    continue
                data_str = raw_line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        if delta.get("content"):
                            if ttft is None:
                                ttft = time.perf_counter() - t_start
                            generated_tokens += 1
                except json.JSONDecodeError:
                    continue

        t_end = time.perf_counter()
        total_duration = t_end - t_start
        gen_duration = total_duration - (ttft if ttft is not None else 0.0)
        tps = (
            (generated_tokens / gen_duration)
            if (gen_duration > 0 and generated_tokens > 0)
            else 0.0
        )

        vram_mb = get_ollama_vram_mb(endpoint) or get_gpu_memory_used_mb()

        return {
            "tokens": tokens,
            "status": "ok",
            "ttft_ms": round((ttft if ttft is not None else total_duration) * 1000, 1),
            "total_ms": round(total_duration * 1000, 1),
            "tokens_generated": generated_tokens,
            "tps": round(tps, 1),
            "vram_mb": vram_mb,
        }

    except urllib.error.URLError as e:
        return {
            "tokens": tokens,
            "status": "error",
            "error": f"Connection failed: {e.reason}",
        }
    except Exception as e:
        return {
            "tokens": tokens,
            "status": "error",
            "error": str(e),
        }


def format_markdown_table(
    results: list[dict[str, Any]], model: str, endpoint: str
) -> str:
    """Format benchmark results into clean, publication-ready Markdown."""
    lines = [
        f"### Local Inference Benchmark: `{model}`",
        f"- **Endpoint**: `{endpoint}`",
        f"- **Timestamp**: `{time.strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "| Context Depth | Prompt Tokens | TTFT (ms) | Speedup vs 32K | Gen (tok/s) | VRAM (MB) |",
        "|:--------------|:--------------|:----------|:---------------|:------------|:----------|",
    ]

    baseline_32k = next(
        (
            r["ttft_ms"]
            for r in results
            if r.get("tokens") >= 30000 and r.get("status") == "ok"
        ),
        None,
    )

    for r in results:
        if r.get("status") != "ok":
            lines.append(
                f"| {r['tokens'] // 1024}K | {r['tokens']:,} | FAILED | - | - | {r.get('error', 'Error')} |"
            )
            continue

        ttft = r["ttft_ms"]
        if baseline_32k and r.get("tokens", 0) >= 30000:
            speedup = "Baseline"
        elif baseline_32k and ttft > 0:
            speedup = f"{round(baseline_32k / ttft, 1)}x"
        else:
            speedup = "N/A"
        vram = f"{r['vram_mb']:,} MB" if r.get("vram_mb") else "N/A"
        lines.append(
            f"| {r['tokens'] // 1024}K | {r['tokens']:,} | {ttft:,.1f} ms | {speedup} | {r['tps']} | {vram} |"
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark TTFT, throughput, and VRAM scaling for local LLMs.",
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:11434/v1",
        help="Local OpenAI-compatible API base (default: http://localhost:11434/v1)",
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:14b",
        help="Model tag to benchmark (default: qwen2.5-coder:14b)",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[2048, 8192, 16384, 32768],
        help="Context token sizes to test (default: 2048 8192 16384 32768)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write markdown results table",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Timeout per trial in seconds (default: 180)",
    )

    args = parser.parse_args()

    print(
        "===========================================================", file=sys.stderr
    )
    print("Athena KV Cache & TTFT Scaling Benchmark", file=sys.stderr)
    print(f"Model: {args.model} | Endpoint: {args.endpoint}", file=sys.stderr)
    print(f"Testing depths: {args.sizes}", file=sys.stderr)
    print(
        "===========================================================", file=sys.stderr
    )

    results = []
    for ctx_size in args.sizes:
        print(f"[*] Running trial: {ctx_size:,} tokens...", file=sys.stderr)
        res = run_benchmark_trial(
            args.endpoint, args.model, ctx_size, timeout_sec=args.timeout
        )
        if res.get("status") == "ok":
            print(
                f"    -> TTFT: {res['ttft_ms']} ms | Gen: {res['tps']} tok/s",
                file=sys.stderr,
            )
        else:
            print(f"    -> ERROR: {res.get('error')}", file=sys.stderr)
        results.append(res)

    md_output = format_markdown_table(results, args.model, args.endpoint)
    print("\n" + md_output)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_output + "\n")
        print(f"\nSaved results to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
