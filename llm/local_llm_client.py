from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class LLMResponse:
    success: bool
    content: str
    model: str
    provider: str
    error: str | None = None
    raw_response: dict[str, Any] | None = None

@dataclass
class LLMStatus:
    available: bool
    provider: str
    model: str
    base_url: str
    message: str

@dataclass
class ModelValidationResult:
    is_valid: bool
    requested_model: str
    available_models: list[str]
    message: str

class LocalLLMClient:
    """
    Week 8 v0.1:
    Local LLM client wrapper.

    This client is optional. If the local LLM server is unavailable,
    the system should fall back to deterministic output.
    """


    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1:8b",
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.provider = "local_ollama"

    def is_available(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> LLMResponse:
        if not prompt.strip():
            return LLMResponse(
                success=False,
                content="",
                model=self.model_name,
                provider=self.provider,
                error="Empty prompt received.",
            )

        full_prompt = self._build_prompt(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()

            data = response.json()
            content = data.get("response", "").strip()

            return LLMResponse(
                success=True,
                content=content,
                model=self.model_name,
                provider=self.provider,
                raw_response=data,
            )

        except Exception as error:
            return LLMResponse(
                success=False,
                content="",
                model=self.model_name,
                provider=self.provider,
                error=str(error),
            )

    def _build_prompt(
        self,
        prompt: str,
        system_prompt: str | None,
    ) -> str:
        if not system_prompt:
            return prompt

        return (
            f"System instruction:\n{system_prompt.strip()}\n\n"
            f"User request:\n{prompt.strip()}"
        )
    
    def get_status(self) -> LLMStatus:
        available = self.is_available()

        if available:
            message = "Local LLM server is available."
        else:
            message = "Local LLM server is not available. The app will use deterministic fallback output."

        return LLMStatus(
            available=available,
            provider=self.provider,
            model=self.model_name,
            base_url=self.base_url,
            message=message,
        )
    def list_models(self) -> list[str]:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()

            data = response.json()
            models = data.get("models", [])

            return [
                model.get("name", "")
                for model in models
                if model.get("name")
            ]

        except Exception:
            return []


    def validate_model(self) -> ModelValidationResult:
        available_models = self.list_models()

        if not available_models:
            return ModelValidationResult(
                is_valid=False,
                requested_model=self.model_name,
                available_models=[],
                message=(
                    "No local models were detected. Make sure Ollama is running "
                    "and at least one model is installed."
                ),
            )

        if self.model_name not in available_models:
            return ModelValidationResult(
                is_valid=False,
                requested_model=self.model_name,
                available_models=available_models,
                message=(
                    f"The requested model `{self.model_name}` was not found in local Ollama models."
                ),
            )

        return ModelValidationResult(
            is_valid=True,
            requested_model=self.model_name,
            available_models=available_models,
            message=f"The requested model `{self.model_name}` is available.",
        )