from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProviderError(RuntimeError):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON object following the provided schema."""

    def train(self, dataset_path: str) -> None:  # pragma: no cover - optional
        return None

