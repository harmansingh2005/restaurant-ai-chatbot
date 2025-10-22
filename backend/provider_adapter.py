"""
provider_adapter.py

A small adapter to talk to an OpenAI-compatible Chat Completions API using httpx.
Reads base URL, API key and model from environment variables so you can point it at
OpenAI, Azure OpenAI (with compat), or a self-hosted compatible endpoint.
"""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import httpx

PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL", "https://api.openai.com/v1")
PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY", "")
PROVIDER_MODEL = os.getenv("PROVIDER_MODEL", "gpt-4o-mini")
PROVIDER_KIND = os.getenv("PROVIDER_KIND", "openai").strip().lower()  # openai | azure | other
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")


class ChatProvider:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or PROVIDER_BASE_URL
        self.api_key = api_key or PROVIDER_API_KEY
        self.model = model or PROVIDER_MODEL

        # Configure endpoint and headers according to provider kind
        if (self.base_url.endswith("/v1") or self.base_url.endswith("/v1/") or PROVIDER_KIND in {"openai", "other"}) and PROVIDER_KIND != "azure":
            # Standard OpenAI-compatible (OpenAI, Groq, etc.)
            self._chat_url = f"{self.base_url.rstrip('/')}/chat/completions"
            self._headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            # Azure OpenAI compatibility
            # Expect base_url like: https://{resource}.openai.azure.com/openai
            # model is the deployment name; api-version is required
            if not AZURE_OPENAI_API_VERSION:
                raise ValueError("AZURE_OPENAI_API_VERSION is required for PROVIDER_KIND=azure")
            base = self.base_url.rstrip('/')
            if not base.endswith('/openai'):
                base = base + '/openai'
            self._chat_url = f"{base}/deployments/{self.model}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
            self._headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json",
            }

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 512) -> str:
        """Send a chat completion request and return the assistant message text.
        If the provider fails, raise an exception so the caller can handle fallback.
        """
        if not (self.api_key and self.api_key.strip()):
            raise ValueError("Missing PROVIDER_API_KEY. Set it in .env and restart the server.")
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(self._chat_url, headers=self._headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # OpenAI-like shape
            return data["choices"][0]["message"]["content"].strip()
