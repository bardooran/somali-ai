"""Model adapters for the Somali conversational assistant.

The production adapter uses the OpenAI Responses API with the Python standard
library, so the repository does not require an SDK dependency just to run.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol, Sequence

from .types import ChatMessage


class ModelConfigurationError(RuntimeError):
    pass


class ModelRequestError(RuntimeError):
    pass


class ModelAdapter(Protocol):
    model_name: str

    def generate(self, messages: Sequence[ChatMessage], instructions: str) -> str:
        ...


def _extract_output_text(payload: dict) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    output = payload.get("output", [])
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
    text = "".join(chunks).strip()
    if not text:
        raise ModelRequestError("Model response contained no text output.")
    return text


@dataclass
class OpenAIResponsesAdapter:
    """Minimal OpenAI Responses API adapter.

    Environment defaults:
    - OPENAI_API_KEY: required
    - SOMALI_AI_MODEL: optional model override
    - OPENAI_BASE_URL: optional API base override
    """

    api_key: str
    model_name: str = "gpt-5.6-terra"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 90.0

    @classmethod
    def from_env(cls) -> "OpenAIResponsesAdapter":
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ModelConfigurationError(
                "OPENAI_API_KEY is not set. Export an API key before starting the assistant."
            )
        model = os.environ.get("SOMALI_AI_MODEL", "gpt-5.6-terra").strip()
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        return cls(api_key=api_key, model_name=model, base_url=base_url)

    def generate(self, messages: Sequence[ChatMessage], instructions: str) -> str:
        body = {
            "model": self.model_name,
            "instructions": instructions,
            "input": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "store": False,
        }
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=encoded,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelRequestError(f"Model API returned HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ModelRequestError(f"Model API request failed: {exc}") from exc

        if not isinstance(payload, dict):
            raise ModelRequestError("Model API returned an unexpected response shape.")
        return _extract_output_text(payload)


@dataclass
class StaticModelAdapter:
    """Deterministic adapter for tests and local pipeline experiments."""

    response: str
    model_name: str = "static-test-model"

    def generate(self, messages: Sequence[ChatMessage], instructions: str) -> str:
        del messages, instructions
        return self.response
