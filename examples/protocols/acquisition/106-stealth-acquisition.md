# Protocol 106: Stealth Acquisition
>
> **Role**: Intelligence Officer (Protocol 052)
> **Scope**: External Data Acquisition (Web)
> **Tool**: `scrapling_wrapper.py`

---

## 1. The Directive

Standard retrieval (requests, curl) is obsolete for high-value targets. Protocol 106 mandates the use of **Stealth Acquisition** for all financial, news, and competitor analysis tasks.

## 2. The Tool: Scrapling

We utilize the `scrapling` library to mimic human TLS fingerprints (JA3/JA4) and HTTP/3 headers.

### Usage

```bash
# Fetch a single URL (Output: JSON)
python3 .agent/scripts/scrapling_wrapper.py --url "https://finance.yahoo.com/quote/AAPL"
```

### JSON Output Schema

```json
{
  "status": "success",
  "url": "https://...",
  "length": 12345,
  "content": "<html>...</html>"
}
```

## 3. Targeting Policy

### Classified Targets (Must use Scrapling)

- **Finance**: Bloomberg, Yahoo Finance, Investing.com, TradingView.
- **Social**: Twitter/X (Public Interface), Reddit, LinkedIn.
- **Security**: Cloudflare-protected domains ("Just a moment...").

### Permissive Targets (Can use standard requests)

- **APIs**: Official JSON endpoints.
- **Documentation**: GitHub, ReadTheDocs.
- **Gov**: .gov domains.

## 4. Evasion Tactics

When integrating this protocol into an automated loop:

1. **Jitter**: Introduce random delays (2-7 seconds) between calls.
2. **Diversity**: Do not hammer a single domain sequentially. Rotate through target list.
3. **Extraction**: Use the `content` field for LLM processing. Do not try to parse complex DOM in the shell; pass HTML to the Agent/LLM for extraction.
