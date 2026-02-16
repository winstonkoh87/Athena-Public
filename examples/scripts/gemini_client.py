#!/usr/bin/env python3
"""
Gemini Client
Reusable wrapper for Google Gemini API (for Athena).
"""

import os
import re
import time
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """Retrieve API key from env, preferring GEMINI_API_KEY."""
    candidate = os.environ.get("GEMINI_API_KEY")
    if candidate and "your_gemini_api_key_here" not in candidate:
        return candidate
    return os.environ.get("GOOGLE_API_KEY", "")


class GeminiClient:
    """Stateful Gemini client with conversation history support."""

    def __init__(
        self, model: str = "gemini-3-flash-preview", system_prompt: str = None
    ):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        genai.configure(api_key=api_key)

        self.model_name = model
        self.system_prompt = system_prompt or ""
        self.history = []

        # Configure model with system instruction and thinking budget
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self.system_prompt if self.system_prompt else None,
            generation_config=genai.GenerationConfig(
                temperature=1.0,  # Enable creative thinking
                max_output_tokens=8192,  # Allow longer responses
            ),
        )
        self.chat_session = self.model.start_chat(history=[])

    def _generate_with_fallback(self, func, *args, **kwargs):
        """Execute a generation function with model fallback cascade + retry."""
        # Expanded cascade: Strictly Gemini 3 Flash (User Decree 2026-02-01)
        cascade_models = [
            "gemini-3-flash-preview",
        ]

        # Ensure current model is first
        if self.model_name in cascade_models:
            cascade_models.remove(self.model_name)
        cascade_models.insert(0, self.model_name)

        last_error = None
        max_retries = 2  # Total attempts through the cascade

        for attempt in range(max_retries):
            for model_name in cascade_models:
                print(
                    f"✨ Athena thinking with {model_name}... (attempt {attempt + 1})"
                )
                try:
                    temp_model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=self.system_prompt
                        if self.system_prompt
                        else None,
                        generation_config=genai.GenerationConfig(
                            temperature=1.0,
                            max_output_tokens=8192,
                        ),
                    )

                    if func.__name__ == "send_message":
                        history = self.chat_session.history
                        temp_session = temp_model.start_chat(history=history)
                        response = temp_session.send_message(*args, **kwargs)
                        self.model = temp_model
                        self.chat_session = temp_session
                        return response.text
                    else:
                        response = temp_model.generate_content(*args, **kwargs)
                        return response.text

                except Exception as e:
                    error_str = str(e)
                    last_error = e

                    # Check for retryable errors
                    if (
                        "429" in error_str
                        or "503" in error_str
                        or "ResourceExhausted" in error_str
                    ):
                        # Extract retry delay if provided
                        match = re.search(
                            r"retry in ([\d.]+)s", error_str, re.IGNORECASE
                        )
                        wait_time = min(float(match.group(1)) + 1, 30) if match else 20
                        print(f"⚠️ {model_name} rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    elif "404" in error_str or "NotFound" in error_str:
                        print(f"⚠️ {model_name} not found. Trying next model...")
                        continue
                    else:
                        # Non-retryable error (e.g. safety block)
                        raise e

            # If we've exhausted all models, wait and retry the whole cascade
            if attempt < max_retries - 1:
                print("⏳ All models exhausted. Waiting 20s before retry...")
                time.sleep(20)

        raise last_error or Exception("All models exhausted after retries.")

    def generate(self, prompt: str) -> str:
        """One-shot generation (no history)."""
        return self._generate_with_fallback(self.model.generate_content, prompt)

    def chat(self, message: str) -> str:
        """Conversational generation (maintains history)."""
        return self._generate_with_fallback(self.chat_session.send_message, message)

    def chat_structured(self, message: str, schema: dict) -> dict:
        """Conversational generation enforcing a JSON schema (Protocol 110)."""
        import json

        # Update generation config for JSON output
        config = genai.GenerationConfig(
            temperature=1.0,
            max_output_tokens=8192,
            response_mime_type="application/json",
            response_schema=schema if schema else None,
        )

        response_text = self._generate_with_fallback(
            self.chat_session.send_message, message, generation_config=config
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback for older models or parsing errors
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse structured response: {response_text}")

    def clear_history(self):
        """Reset conversation history."""
        self.chat_session = self.model.start_chat(history=[])
        self.history = []


def get_client(system_prompt: str = None) -> GeminiClient:
    """Factory function for quick client creation."""
    return GeminiClient(system_prompt=system_prompt)


# --- Mobile System Prompt Generator ---
def get_mobile_system_prompt() -> str:
    """Load a condensed Athena identity for mobile use."""

    # Try to load Core Identity
    workspace = Path(__file__).resolve().parent.parent.parent
    core_identity_path = (
        workspace / ".framework" / "v7.0" / "modules" / "Core_Identity.md"
    )
    user_profile_path = workspace / "Winston" / "profile" / "User_Profile.md"

    identity_snippet = ""
    user_snippet = ""

    if core_identity_path.exists():
        content = core_identity_path.read_text()
        # Extract first 1500 chars (condensed)
        identity_snippet = content[:1500]

    if user_profile_path.exists():
        content = user_profile_path.read_text()
        # Extract first 1000 chars
        user_snippet = content[:1000]

    prompt = f"""You are Athena, a powerful AI assistant operating via Telegram.

## Your Identity (Condensed)
{identity_snippet}

## User Context
{user_snippet}

## Mobile Constraints
- Keep responses concise (under 3000 characters).
- Use bullet points and structure for readability.
- Maintain your analytical, direct, and honest personality.
- You can reference past conversation in this session.
"""
    return prompt


if __name__ == "__main__":
    # Quick test
    client = get_client(system_prompt="You are a helpful assistant.")
    print(client.generate("Say hello in 3 words."))
