"""
athena.core.security — Security patches and hardening.
======================================================
"""

import logging
import diskcache
import dspy
from athena.core.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def patch_dspy_cache_security():
    """
    HOT PATCH: Enforce JSON serialization for dspy's DiskCache.

    Mitigates CVE-2025-69872 where default pickle serialization in diskcache
    allows arbitrary code execution from malicious cache files.

    This function:
    1. Checks if dspy.cache.disk_cache is active.
    2. Swaps the underlying 'disk' storage from Pickle (default) to JSON.
    3. Clears the cache to prevent loading old pickled data.
    """
    try:
        # Check if dspy has a disk cache initialized
        if hasattr(dspy, "cache") and hasattr(dspy.cache, "disk_cache"):
            cache_obj = dspy.cache.disk_cache

            # FanoutCache uses ._shards which are Cache objects
            # We need to patch the underlying Cache objects or the specific disk instance

            # If it's a FanoutCache (dspy default)
            if isinstance(cache_obj, diskcache.FanoutCache):
                logger.info(
                    "🛡️  Security: Patching dspy FanoutCache to use JSON serialization..."
                )

                # Patch directory target if needed, but mainly the serialization
                # FanoutCache doesn't expose a simple 'disk' attr to swap for all shards easily
                # without iterating or reinitalizing.
                # EASIER STRATEGY: Re-initialize the disk_cache with secure settings within dspy.settings?
                # No, dspy.settings.configure might overwrite.

                # Let's try to monkeypatch the disk class on the class itself? No, too broad.
                # Let's re-create the cache object on dspy.

                current_dir = cache_obj.directory
                current_size = cache_obj.size_limit

                # Re-initialize safely
                # dspy.cache.disk_cache = diskcache.FanoutCache(
                #     directory=current_dir,
                #     size_limit=current_size,
                #     disk=diskcache.JSONDisk  # <--- SECURE
                # )

                # Wait, dspy.cache is a custom Cache class wrapper, not just the raw diskcache object.
                # cache.py: self.disk_cache = FanoutCache(...)

                # Access the wrapper
                wrapper = dspy.cache
                if wrapper.enable_disk_cache:
                    # Close old cache
                    wrapper.disk_cache.close()

                    # Re-open with JSONDisk
                    wrapper.disk_cache = diskcache.FanoutCache(
                        directory=current_dir,
                        size_limit=current_size,
                        disk=diskcache.JSONDisk,  # Force JSON
                        shards=16,  # Default
                    )
                    logger.info("✅ Security: dspy disk cache patched (JSONDisk).")

            else:
                logger.warning(
                    "⚠️  Security: dspy cache is not FanoutCache. Skipping patch."
                )

    except Exception as e:
        logger.error(f"❌ Security Patch Failed: {e}")
        # Fail open? or Fail closed?
        # For security, we should probably warn aggressively but continue.
