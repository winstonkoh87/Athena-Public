"""Web search provider layer for Athena.

Provides a pluggable provider architecture for web search with:
- API-first providers (Serper, Brave) for reliability
- Hardened DuckDuckGo fallback
- Explicit ProviderFailure instead of silent empty results
- Health checking and provider selection
"""

from __future__ import annotations

import html
import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "WebResult",
    "ProviderFailure",
    "WebProvider",
    "SerperProvider",
    "BraveProvider",
    "DuckDuckGoProvider",
    "get_provider_chain",
    "web_search",
    "get_web_health",
]

logger = logging.getLogger("athena.web_providers")


def _get_ssl_context():
    """Create a robust SSL context for macOS, using certifi when available."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()


@dataclass
class WebResult:
    """A single web search result."""
    title: str
    snippet: str
    url: str
    fetched_at: str  # ISO 8601 timestamp
    provider: str
    position: int  # 0-indexed rank from provider


class ProviderFailure(Exception):
    """Raised when a web search provider fails.

    This replaces the old `except: pass` pattern that silently returned []
    and made the web channel invisibly dead.
    """
    def __init__(self, provider: str, reason: str, recoverable: bool = True):
        self.provider = provider
        self.reason = reason
        self.recoverable = recoverable
        super().__init__(f"{provider}: {reason}")


class WebProvider(ABC):
    """Abstract base class for web search providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[WebResult]:
        """Execute a web search. Raises ProviderFailure on any error."""
        ...

    @abstractmethod
    def healthy(self) -> bool:
        """Quick health check — is this provider likely to work?"""
        ...


class SerperProvider(WebProvider):
    @property
    def name(self) -> str:
        return "serper"

    def healthy(self) -> bool:
        return bool(os.environ.get("SERPER_API_KEY"))

    def search(self, query: str, limit: int = 5) -> list[WebResult]:
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            raise ProviderFailure(self.name, "SERPER_API_KEY not set", recoverable=False)

        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=json.dumps({"q": query, "num": limit}).encode("utf-8"),
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=8, context=_get_ssl_context()) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise ProviderFailure(self.name, str(e)) from e

        results = []
        now = datetime.now(timezone.utc).isoformat()
        organic = body.get("organic", [])
        for i, res in enumerate(organic[:limit]):
            results.append(WebResult(
                title=res.get("title", ""),
                snippet=res.get("snippet", ""),
                url=res.get("link", ""),
                fetched_at=now,
                provider=self.name,
                position=i
            ))
        return results


class BraveProvider(WebProvider):
    @property
    def name(self) -> str:
        return "brave"

    def healthy(self) -> bool:
        return bool(os.environ.get("BRAVE_API_KEY"))

    def search(self, query: str, limit: int = 5) -> list[WebResult]:
        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            raise ProviderFailure(self.name, "BRAVE_API_KEY not set", recoverable=False)

        url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={limit}"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=8, context=_get_ssl_context()) as response:
                if response.info().get("Content-Encoding") == "gzip":
                    import gzip
                    body = json.loads(gzip.decompress(response.read()).decode("utf-8"))
                else:
                    body = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise ProviderFailure(self.name, str(e)) from e

        results = []
        now = datetime.now(timezone.utc).isoformat()
        web = body.get("web", {}).get("results", [])
        for i, res in enumerate(web[:limit]):
            results.append(WebResult(
                title=res.get("title", ""),
                snippet=res.get("description", ""),
                url=res.get("url", ""),
                fetched_at=now,
                provider=self.name,
                position=i
            ))
        return results


class DuckDuckGoProvider(WebProvider):
    @property
    def name(self) -> str:
        return "duckduckgo"

    def healthy(self) -> bool:
        return True

    def search(self, query: str, limit: int = 5) -> list[WebResult]:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )

        last_err = None
        html_content = ""
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=8, context=_get_ssl_context()) as response:
                    html_content = response.read().decode("utf-8")
                break
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(1)
                else:
                    raise ProviderFailure(self.name, str(last_err)) from last_err

        results = []
        now = datetime.now(timezone.utc).isoformat()

        pattern = re.compile(
            r'<a class="result__url" href="([^"]+)".*?>(.*?)</a>.*?'
            r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL
        )
        matches = pattern.findall(html_content)

        if not matches:
            pattern2 = re.compile(
                r'<h2 class="result__title">.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?<a class="result__snippet[^"]*"[^>]*>(.*?)</a>',
                re.IGNORECASE | re.DOTALL
            )
            matches = pattern2.findall(html_content)

        count = 0
        for match in matches:
            if count >= limit:
                break
            raw_url, title, snippet = match

            actual_url = raw_url
            if "uddg=" in raw_url or raw_url.startswith("/l/?") or "u=" in raw_url:
                parsed = urllib.parse.urlparse(raw_url)
                qs = urllib.parse.parse_qs(parsed.query)
                if "uddg" in qs:
                    actual_url = qs["uddg"][0]
                elif "u" in qs:
                    actual_url = qs["u"][0]

            clean_title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
            clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', snippet)).strip()

            if clean_title and clean_snippet:
                results.append(WebResult(
                    title=clean_title,
                    snippet=clean_snippet,
                    url=actual_url,
                    fetched_at=now,
                    provider=self.name,
                    position=count
                ))
                count += 1

        if not results:
            raise ProviderFailure(self.name, "No results parsed from HTML (possible anti-bot or parse failure)")

        return results


def get_provider_chain() -> list[WebProvider]:
    """Build the provider priority chain from env config.

    Reads WEB_PROVIDERS env var (comma-separated, e.g. 'serper,brave,duckduckgo').
    Default: 'serper,brave,duckduckgo' — first healthy provider wins.
    """
    providers_env = os.environ.get("WEB_PROVIDERS", "serper,brave,duckduckgo")
    provider_names = [p.strip().lower() for p in providers_env.split(",") if p.strip()]

    available = {
        "serper": SerperProvider(),
        "brave": BraveProvider(),
        "duckduckgo": DuckDuckGoProvider()
    }

    chain = []
    for name in provider_names:
        if name in available:
            chain.append(available[name])

    if not chain:
        chain.append(DuckDuckGoProvider())

    return chain


def web_search(query: str, limit: int = 5) -> tuple[list[WebResult], dict[str, Any]]:
    """Execute web search with automatic provider failover.

    Returns:
        Tuple of (results, metadata) where metadata includes:
        - provider: str — which provider succeeded
        - degraded: bool — True if all preferred providers failed
        - errors: list[str] — error messages from failed providers
        - fetched_at: str — ISO timestamp

    Never crashes. If ALL providers fail:
        Returns ([], {"provider": "none", "degraded": True, "errors": [...]})
    """
    chain = get_provider_chain()
    errors = []

    for provider in chain:
        if not provider.healthy() and provider.name != chain[-1].name:
            # Skip unhealthy providers, unless it's the last resort
            errors.append(f"{provider.name}: Not healthy/configured")
            continue

        try:
            results = provider.search(query, limit)
            metadata = {
                "provider": provider.name,
                "degraded": provider != chain[0],
                "errors": errors,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            return results, metadata
        except ProviderFailure as e:
            logger.warning(f"Provider {provider.name} failed: {e.reason}")
            errors.append(f"{provider.name}: {e.reason}")
        except Exception as e:
            logger.warning(f"Provider {provider.name} crashed: {str(e)}")
            errors.append(f"{provider.name}: {str(e)}")

    # All failed
    return [], {
        "provider": "none",
        "degraded": True,
        "errors": errors,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def get_web_health() -> dict[str, Any]:
    """Return web provider health status for health_check MCP tool."""
    chain = get_provider_chain()
    active_provider = None

    providers_info = []

    all_providers = [SerperProvider(), BraveProvider(), DuckDuckGoProvider()]

    for provider in all_providers:
        is_healthy = provider.healthy()
        providers_info.append({
            "name": provider.name,
            "healthy": is_healthy,
            "configured": is_healthy  # Simplified logic
        })

    # Find active
    for provider in chain:
        if provider.healthy():
            active_provider = provider.name
            break

    if not active_provider:
        active_provider = "duckduckgo"

    return {
        "providers": providers_info,
        "active_provider": active_provider,
        "degraded": active_provider != chain[0].name if chain else True
    }
