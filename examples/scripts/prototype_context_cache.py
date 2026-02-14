import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Config
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 1. Prepare Content
# We need a large enough context to make caching worth it (>32k tokens usually, but let's try with what we have)
# For prototype, we'll just synthesize a large prompt or load a file.
# Rate Limit: We have TPM limits.


def prototype_caching():
    print("🧠 Gemini Context Caching Prototype (v1)")

    # Check if caching is supported on the key/model
    # Note: Caching is often paid or specific to 1.5 Pro. Flash might not support it in Free Tier.

    large_context = (
        "This is a test of the specific caching mechanism. " * 5000
    )  # ~50k characters ~12k tokens? No, 1 token ~ 4 chars. ~12k tokens.

    print(f"📦 Payload Size: {len(large_context)} chars")

    try:
        # Create a cache
        # Ref: https://ai.google.dev/gemini-api/docs/caching/python
        from google.generativeai import caching

        # Try a list of potential caching models
        candidates = [
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro-001",
        ]

        cache = None
        for m in candidates:
            try:
                print(f"👉 Trying model: {m}")
                cache = caching.CachedContent.create(
                    model=m,
                    display_name="Athena_Prototype_Cache",
                    system_instruction="You are a cached assistant.",
                    contents=[large_context],
                    ttl=300,
                )
                print(f"✅ Cache Created with {m}")
                break
            except Exception as e:
                print(f"   Failed {m}: {e}")

        if not cache:
            print("❌ All candidates failed.")
            return False

        print(f"✅ Cache Created: {cache.name}")
        print(f"   Expiration: {cache.expire_time}")

        # Ensure we can use it
        model = genai.GenerativeModel.from_cached_content(cached_content=cache)

        t0 = time.time()
        response = model.generate_content("Summarize the text.")
        t1 = time.time()

        print(f"⚡ Cached Response ({t1 - t0:.2f}s): {response.text[:100]}...")

        # Cleanup
        cache.delete()
        print("🗑️ Cache deleted.")
        return True

    except Exception as e:
        print(f"❌ Caching Failed: {e}")
        # Common error: Free tier doesn't support caching or wrong model
        if "403" in str(e):
            print("   (likely permission/tier issue)")
        return False


if __name__ == "__main__":
    prototype_caching()
