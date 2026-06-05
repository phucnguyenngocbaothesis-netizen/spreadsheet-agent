from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from llm.local_llm_client import LocalLLMClient, LLMResponse
from llm.prompt_templates import PromptTemplates


@dataclass
class LLMExplanationResult:
    success: bool
    explanation: str
    source: str
    model: str
    fallback_used: bool
    error: str | None
    prompt_type: str
    warnings: list[str]


class LLMExplanationAgent:
    """
    Week 10 v0.1:
    Optional LLM-assisted explanation layer.

    This agent never replaces deterministic output.
    It only explains deterministic results.
    """

    def __init__(self, llm_client: LocalLLMClient) -> None:
        self.llm_client = llm_client

    def explain_eda_result(
        self,
        user_question: str,
        deterministic_result: str,
        profile: dict[str, Any],
    ) -> LLMExplanationResult:
        prompt = PromptTemplates.eda_explanation_prompt(
            user_question=user_question,
            deterministic_result=deterministic_result,
            profile=profile,
        )

        return self._generate_explanation(
            prompt=prompt,
            prompt_type="eda_explanation",
        )

    def explain_chart_result(
        self,
        user_question: str,
        chart_metadata: dict[str, Any],
        chart_insights_markdown: str,
    ) -> LLMExplanationResult:
        prompt = PromptTemplates.chart_explanation_prompt(
            user_question=user_question,
            chart_metadata=chart_metadata,
            chart_insights_markdown=chart_insights_markdown,
        )

        return self._generate_explanation(
            prompt=prompt,
            prompt_type="chart_explanation",
        )

    def _generate_explanation(
        self,
        prompt: str,
        prompt_type: str,
    ) -> LLMExplanationResult:
        warnings: list[str] = []

        status = self.llm_client.get_status()

        if not status.available:
            return LLMExplanationResult(
                success=False,
                explanation="Local LLM is not available. Deterministic output was used instead.",
                source="deterministic_fallback",
                model=self.llm_client.model_name,
                fallback_used=True,
                error=status.message,
                prompt_type=prompt_type,
                warnings=[status.message],
            )

        model_validation = self.llm_client.validate_model()

        if not model_validation.is_valid:
            warnings.append(model_validation.message)

            return LLMExplanationResult(
                success=False,
                explanation="Selected local model is not available. Deterministic output was used instead.",
                source="deterministic_fallback",
                model=self.llm_client.model_name,
                fallback_used=True,
                error=model_validation.message,
                prompt_type=prompt_type,
                warnings=warnings,
            )

        llm_response: LLMResponse = self.llm_client.generate(
            prompt=prompt,
            system_prompt=(
                "You explain deterministic spreadsheet analysis results. "
                "Do not invent numbers. Do not add unsupported claims. "
                "Use concise, structured language."
            ),
            temperature=0.2,
            max_tokens=512,
        )

        if not llm_response.success:
            return LLMExplanationResult(
                success=False,
                explanation="LLM generation failed. Deterministic output was used instead.",
                source="deterministic_fallback",
                model=self.llm_client.model_name,
                fallback_used=True,
                error=llm_response.error,
                prompt_type=prompt_type,
                warnings=[llm_response.error or "Unknown LLM generation error."],
            )

        cleaned_explanation = self._clean_response(llm_response.content)
        quality_warnings = self._validate_explanation_quality(cleaned_explanation)
        warnings.extend(quality_warnings)

        return LLMExplanationResult(
            success=True,
            explanation=cleaned_explanation,
            source="local_llm",
            model=self.llm_client.model_name,
            fallback_used=False,
            error=None,
            prompt_type=prompt_type,
            warnings=warnings,
        )

    def _clean_response(self, content: str) -> str:
        cleaned = content.strip()

        if not cleaned:
            return "The LLM returned an empty explanation."

        return cleaned
    
    def _validate_explanation_quality(self, explanation: str) -> list[str]:
        warnings: list[str] = []

        stripped = explanation.strip()

        if not stripped:
            warnings.append("LLM explanation is empty.")
            return warnings

        word_count = len(stripped.split())

        if word_count < 15:
            warnings.append("LLM explanation may be too short.")

        if word_count > 250:
            warnings.append("LLM explanation may be too long.")

        incomplete_endings = (
            ",",
            ":",
            ";",
            "(",
            "[",
            "and",
            "or",
            "but",
        )

        lower_stripped = stripped.lower()

        if lower_stripped.endswith(incomplete_endings):
            warnings.append("LLM explanation may be incomplete or cut off.")

        return warnings