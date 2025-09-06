from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

from dkernel.config import get_settings
from .llm_interface import LLMProvider, LLMProviderError


class MockProvider(LLMProvider):
    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # Deterministic mock output
        return {
            "assumptions": ["prices stable"],
            "risks": ["supplier delay"],
            "tweak_actions": ["increase safety stock for A SKUs"],
        }


class OllamaProvider(LLMProvider):  # pragma: no cover - network
    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        base = get_settings().OLLAMA_BASE
        model = get_settings().OLLAMA_MODEL
        if not base:
            raise LLMProviderError("OLLAMA_BASE not set")
        resp = requests.post(
            f"{base}/api/generate",
            json={"model": model, "prompt": prompt},
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "{}")
        try:
            return json.loads(text)
        except Exception as e:
            raise LLMProviderError("Invalid JSON from Ollama") from e


class LMStudioProvider(LLMProvider):  # pragma: no cover - network
    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        base = get_settings().LMSTUDIO_BASE
        model = get_settings().LMSTUDIO_MODEL
        if not base:
            raise LLMProviderError("LMSTUDIO_BASE not set")
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        resp = requests.post(f"{base}/v1/chat/completions", headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        return json.loads(text)


def provider_factory(name: Optional[str] = None) -> LLMProvider:
    name = (name or get_settings().LLM_PROVIDER).lower()
    if name == "mock":
        return MockProvider()
    if name == "ollama":
        return OllamaProvider()
    if name == "lmstudio":
        return LMStudioProvider()
    # For brevity, hf/azure/openai not implemented in detail here; tests will mock.
    return MockProvider()

