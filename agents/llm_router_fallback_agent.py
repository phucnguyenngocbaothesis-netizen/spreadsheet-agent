from __future__ import annotations

from dataclasses import dataclass

from agents.fast_router import RouteResult
from llm.local_llm_client import LocalLLMClient


@dataclass
class LLMRouteFallbackResult:
    used_llm: bool
    route_result: RouteResult
    raw_response: str
    error: str | None
    warnings: list[str]


class LLMRouterFallbackAgent:
    """
    Optional LLM-based route classifier.

    This agent is only used when FastRouterAgent returns UNKNOWN.
    It does not replace the deterministic router.
    """

    ALLOWED_ROUTES = [
        "DIRECT_ANALYSIS",
        "VISUALIZATION",
        "EDA_INSIGHT",
        "CODEGEN_SQL",
        "PLANNING",
        "PERSONALIZATION",
        "UNKNOWN",
    ]

    def __init__(self, llm_client: LocalLLMClient) -> None:
        self.llm_client = llm_client

    def classify_unknown_route(
        self,
        user_question: str,
    ) -> LLMRouteFallbackResult:
        status = self.llm_client.get_status()

        if not status.available:
            return self._fallback_unknown(
                user_question=user_question,
                error=status.message,
                warning="Local LLM is unavailable, so route fallback was skipped.",
            )

        model_validation = self.llm_client.validate_model()

        if not model_validation.is_valid:
            return self._fallback_unknown(
                user_question=user_question,
                error=model_validation.message,
                warning="Selected local LLM model is invalid, so route fallback was skipped.",
            )

        prompt = self._build_route_prompt(user_question)

        llm_response = self.llm_client.generate(
            prompt=prompt,
            system_prompt=(
                "You classify spreadsheet analysis user requests into one route. "
                "Return only one route name. Do not explain."
            ),
            temperature=0.0,
            max_tokens=20,
        )

        if not llm_response.success:
            return self._fallback_unknown(
                user_question=user_question,
                error=llm_response.error,
                warning="LLM route fallback generation failed.",
            )

        predicted_route = self._parse_route(llm_response.content)

        route_result = RouteResult(
            route=predicted_route,
            confidence=0.55 if predicted_route != "UNKNOWN" else 0.0,
            matched_keywords=["llm_route_fallback"] if predicted_route != "UNKNOWN" else [],
            reason=(
                "Route predicted by optional LLM fallback."
                if predicted_route != "UNKNOWN"
                else "LLM fallback did not return a valid known route."
            ),
        )

        return LLMRouteFallbackResult(
            used_llm=True,
            route_result=route_result,
            raw_response=llm_response.content,
            error=None,
            warnings=[],
        )

    def _build_route_prompt(self, user_question: str) -> str:
        return f"""
Classify this spreadsheet analysis request into exactly one route.

Allowed routes:
- DIRECT_ANALYSIS: shape, columns, data types, missing values, duplicates, summaries, column descriptions
- VISUALIZATION: charts, plots, graphs, histograms, scatter plots, line charts, bar charts
- EDA_INSIGHT: insights, trends, patterns, exploratory analysis
- CODEGEN_SQL: pandas code, SQL query, code generation
- PLANNING: workflow, analysis plan, next steps, process
- PERSONALIZATION: make output simpler, more technical, concise, detailed, beginner-friendly
- UNKNOWN: none of the above

User request:
{user_question}

Return only the route name.
""".strip()

    def _parse_route(self, raw_response: str) -> str:
        normalized = raw_response.strip().upper()

        for route in self.ALLOWED_ROUTES:
            if route in normalized:
                return route

        return "UNKNOWN"

    def _fallback_unknown(
        self,
        user_question: str,
        error: str | None,
        warning: str,
    ) -> LLMRouteFallbackResult:
        return LLMRouteFallbackResult(
            used_llm=False,
            route_result=RouteResult(
                route="UNKNOWN",
                confidence=0.0,
                matched_keywords=[],
                reason=(
                    "No matching route keywords found and LLM route fallback was unavailable."
                ),
            ),
            raw_response="",
            error=error,
            warnings=[warning],
        )