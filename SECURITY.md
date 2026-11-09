# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v9.x    | :white_check_mark: |
| < 9.0   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities via email/Telegram to the maintainer.

## Known Vulnerabilities & Mitigations

### CVE-2025-69872 (DiskCache Unsafe Pickle)

- **Status**: Mitigated :white_check_mark:
- **Component**: `dspy-ai` -> `diskcache`
- **Impact**: Arbitrary code execution via malicious cache files.
- **Mitigation**: Runtime patch in `athena.core.security` swaps `dspy` caches to `diskcache-community`'s `SafeJSONDisk` serializer with `on_error="miss"`, completely rejecting and dropping untrusted pickle payloads.
- **Verification**: `athena.boot.orchestrator` applies this patch on startup; regression tested against planted pickle entries in `tests/test_security.py`.
