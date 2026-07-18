"""
LLM Client — Provider-Agnostic AI Interface
=============================================
Switch between Gemini, Groq, and Ollama with ONE config change.

STRATEGY PATTERN:
- One interface, multiple implementations
- The rest of the app calls llm_client.generate()
- It doesn't care WHICH LLM provider handles the request
- Change LLM_PROVIDER in .env → entire app switches providers

THIS IS THE HEART OF THE AI ENGINE.

SUPPORTED PROVIDERS:
- Gemini 2.5 Flash (Free tier: ~10 RPM, ~250 RPD)
- Groq Llama 3.3 70B (Free tier: ~30 RPM)
- Ollama Local (Unlimited — runs on your machine)
"""

import json
import logging

import httpx
from google import genai
from google.genai import types as genai_types
from groq import AsyncGroq

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified interface to talk to any LLM provider.

    Usage:
        response = await llm_client.generate(
            prompt="Generate test cases for login page",
            system_prompt="You are a QA engineer"
        )
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._setup_providers()

    def _setup_providers(self):
        """Initialize API clients based on configured provider."""
        # Gemini setup — new google-genai SDK with native async support
        self._gemini_client = (
            genai.Client(api_key=settings.GEMINI_API_KEY)
            if settings.GEMINI_API_KEY
            else None
        )

        # Groq setup (client created per-call for async safety)
        self._groq_api_key = settings.GROQ_API_KEY

        # Ollama setup
        self._ollama_base_url = settings.OLLAMA_BASE_URL
        self._ollama_model = settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        json_mode: bool = True,
    ) -> str:
        """
        Send a prompt to the configured LLM and get a response.

        Args:
            prompt: The user/task prompt
            system_prompt: Instructions for how the LLM should behave
            json_mode: If True, force JSON output (default — used by Phase 1
                       analyze/generate). If False, return raw text/code
                       (used by Phase 2 script generation).

        Returns:
            The LLM's text response

        Raises:
            ValueError: If provider is unknown
            RuntimeError: If LLM call fails after retries
        """
        try:
            if self.provider == "gemini":
                return await self._call_gemini(prompt, system_prompt, json_mode)
            elif self.provider == "groq":
                return await self._call_groq(prompt, system_prompt)
            elif self.provider == "ollama":
                return await self._call_ollama(prompt, system_prompt)
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM call failed ({self.provider}): {e}")
            raise RuntimeError(
                f"Failed to get response from {self.provider}: {e}"
            ) from e

    # ── Gemini (Google) ────────────────────────────────────────────

    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: str,
        json_mode: bool = True,
    ) -> str:
        """
        Call Google Gemini API via the new google-genai SDK.

        Speed optimizations applied:
        1. Native async (client.aio) — no thread executor needed
        2. thinking_budget=0 — disables Gemini 2.5 Flash "thinking" (2-4x faster)
        3. response_mime_type='application/json' (when json_mode=True) — forces clean JSON
        4. Lower temperature — more deterministic, fewer retries

        Model: gemini-2.5-flash (configurable via .env)
        Free tier: ~10 RPM, ~250 RPD
        """
        if self._gemini_client is None:
            raise RuntimeError("GEMINI_API_KEY not configured in .env")

        config_kwargs = {
            "system_instruction": system_prompt or None,
            "temperature": 0.3,
            "thinking_config": genai_types.ThinkingConfig(thinking_budget=0),
        }
        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"

        config = genai_types.GenerateContentConfig(**config_kwargs)

        response = await self._gemini_client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=config,
        )

        return response.text

    # ── Groq (Llama 3.3) ──────────────────────────────────────────

    async def _call_groq(self, prompt: str, system_prompt: str) -> str:
        """
        Call Groq API with Llama 3.3 70B.

        Uses official groq async SDK.
        Model: llama-3.3-70b-versatile (configurable via .env)
        Free tier: ~30 RPM
        """
        client = AsyncGroq(api_key=self._groq_api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    # ── Ollama (Local) ─────────────────────────────────────────────

    async def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """
        Call local Ollama server via REST API.

        Uses httpx for async HTTP calls.
        Model: llama3.1:8b (configurable via .env)
        Unlimited — runs on your machine
        """
        url = f"{self._ollama_base_url}/api/generate"
        payload = {
            "model": self._ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4096,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        return result.get("response", "")

    # ── Utility: Parse JSON from LLM response ─────────────────────

    @staticmethod
    def parse_json_response(response_text: str) -> list | dict:
        """
        Extract and parse JSON from LLM response.

        LLMs often wrap JSON in markdown code blocks like:
        ```json
        [{"key": "value"}]
        ```

        This method handles all common formats.
        """
        text = response_text.strip()

        # Remove markdown code block wrappers if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # Try parsing as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON array or object in the text
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            start_idx = text.find(start_char)
            end_idx = text.rfind(end_char)
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx : end_idx + 1])
                except json.JSONDecodeError:
                    continue

        logger.error(f"Failed to parse JSON from LLM response: {text[:200]}...")
        raise ValueError("Could not parse JSON from LLM response")


# Single instance used across the app
llm_client = LLMClient()
