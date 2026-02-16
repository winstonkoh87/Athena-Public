# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v1.5.x  | :white_check_mark: |
| < 1.5   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities via email/Telegram to the maintainer.

## Known Vulnerabilities & Mitigations

### CVE-2025-69872 (DiskCache Unsafe Pickle)

- **Status**: Mitigated :white_check_mark:
- **Component**: `dspy-ai` -> `diskcache`
- **Impact**: Arbitrary code execution via malicious cache files.
- **Mitigation**: Runtime patch in `athena.core.security` enforces `diskcache.JSONDisk` serializer, blocking pickle exploits.
- **Verification**: `athena.boot.orchestrator` applies this patch on startup.
