from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from agents.table_context_agent import TableContextAgent

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
        self.table_context_agent = TableContextAgent()

    def explain_eda_result(
        self,
        user_question: str,
        deterministic_result: str,
        profile: dict[str, Any],
        language: str = "en",
    ) -> LLMExplanationResult:
        prompt = PromptTemplates.eda_explanation_prompt(
            user_question=user_question,
            deterministic_result=deterministic_result,
            profile=profile,
            language=language,
        )

        return self._generate_explanation(
            prompt=prompt,
            prompt_type="eda_explanation",
            fallback_explanation=deterministic_result,
        )

    def explain_eda_result_with_table_context(
        self,
        user_question: str,
        deterministic_result: str,
        df: pd.DataFrame,
        profile: dict[str, Any],
        language: str = "en",
    ) -> LLMExplanationResult:
        table_context = self.table_context_agent.build_context(
            question=user_question,
            df=df,
            profile=profile,
        )

        table_context_markdown = self.table_context_agent.format_context_as_markdown(
            table_context
        )

        prompt = PromptTemplates.eda_explanation_with_table_context_prompt(
            user_question=user_question,
            deterministic_result=deterministic_result,
            table_context_markdown=table_context_markdown,
            language=language,
        )

        result = self._generate_explanation(
            prompt=prompt,
            prompt_type="eda_explanation_with_table_context",
            fallback_explanation=deterministic_result,
        )

        if table_context.warnings:
            result.warnings.extend(table_context.warnings)

        return result

    def explain_chart_result(
        self,
        user_question: str,
        chart_metadata: dict[str, Any],
        chart_insights_markdown: str,
        language: str = "en",
    ) -> LLMExplanationResult:
        prompt = PromptTemplates.chart_explanation_prompt(
            user_question=user_question,
            chart_metadata=chart_metadata,
            chart_insights_markdown=chart_insights_markdown,
            language=language,
        )

        return self._generate_explanation(
            prompt=prompt,
            prompt_type="chart_explanation",
            fallback_explanation=chart_insights_markdown,
        )

    def _generate_explanation(
        self,
        prompt: str,
        prompt_type: str,
        fallback_explanation: str,
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

        raw_content = llm_response.content.strip()

        if not raw_content:
            warnings.append("LLM returned an empty explanation. Retrying once with a shorter prompt.")

            retry_prompt = self._build_retry_prompt(prompt)

            retry_response = self.llm_client.generate(
                prompt=retry_prompt,
                system_prompt=(
                    "You explain spreadsheet analysis results. "
                    "Return a short, useful explanation. Do not return an empty response."
                ),
                temperature=0.1,
                max_tokens=200,
            )

            if retry_response.success and retry_response.content.strip():
                cleaned_explanation = self._clean_response(retry_response.content)
                quality_warnings = self._validate_explanation_quality(cleaned_explanation)
                warnings.extend(quality_warnings)

                return LLMExplanationResult(
                    success=True,
                    explanation=cleaned_explanation,
                    source="local_llm_retry",
                    model=self.llm_client.model_name,
                    fallback_used=False,
                    error=None,
                    prompt_type=prompt_type,
                    warnings=warnings,
                )

            warnings.append("LLM retry also returned an empty or failed explanation.")

            return LLMExplanationResult(
                success=False,
                explanation=(
                    "The local LLM returned an empty explanation after retrying.\n\n"
                    "The deterministic result is still valid, so the system is showing a "
                    "deterministic fallback explanation instead:\n\n"
                    f"{fallback_explanation}"
                ),
                source="deterministic_fallback",
                model=self.llm_client.model_name,
                fallback_used=True,
                error="Empty LLM response after retry.",
                prompt_type=prompt_type,
                warnings=warnings,
            )

        cleaned_explanation = self._clean_response(raw_content)
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
        return content.strip()
    
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
    
    def _build_retry_prompt(self, original_prompt: str) -> str:
        return f"""
    The previous response may have been empty.

    Please answer briefly and clearly.

    Use only the information below.
    Do not invent numbers.
    Write 3 to 5 bullet points maximum.

    Context:
    {original_prompt}
    """.strip()