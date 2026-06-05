from __future__ import annotations

import json
from pathlib import Path
from typing import Any


from dataclasses import dataclass


@dataclass
class RouteResult:
    route: str
    confidence: float
    matched_keywords: list[str]
    reason: str


class FastRouterAgent:
    """
    Week 2 v0.2:
    Rule-based router for spreadsheet analysis requests.

    The goal is to avoid unnecessary LLM calls by sending simple
    deterministic questions to DirectAnalysisAgent.
    """

    ROUTE_DIRECT_ANALYSIS = "DIRECT_ANALYSIS"
    ROUTE_VISUALIZATION = "VISUALIZATION"
    ROUTE_CODEGEN_SQL = "CODEGEN_SQL"
    ROUTE_PLANNING = "PLANNING"
    ROUTE_PERSONALIZATION = "PERSONALIZATION"
    ROUTE_CLEANING = "CLEANING"
    ROUTE_EDA_INSIGHT = "EDA_INSIGHT"
    ROUTE_UNKNOWN = "UNKNOWN"
    DEFAULT_KEYWORD_CONFIG_PATH = "config/route_keywords.json"

    def __init__(
        self,
        keyword_config_path: str | None = None,
    ) -> None:
        self.keyword_config_path = keyword_config_path or self.DEFAULT_KEYWORD_CONFIG_PATH

        self.route_keywords = self._load_route_keywords(
            config_path=self.keyword_config_path,
        )

        self.priority_order = [
            self.ROUTE_CODEGEN_SQL,
            self.ROUTE_PLANNING,
            self.ROUTE_VISUALIZATION,
            self.ROUTE_PERSONALIZATION,
            self.ROUTE_CLEANING,
            self.ROUTE_DIRECT_ANALYSIS,
            self.ROUTE_EDA_INSIGHT,
        ]
    def route(
        self,
        user_question: str,
        profile: dict | None = None,
    ) -> RouteResult:
        question = user_question.lower().strip()

        if not question:
            return RouteResult(
                route=self.ROUTE_UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                reason="Empty user question.",
            )
        
        schema_route_result = self._route_schema_aware_question(
            question=question,
            profile=profile,
        )

        if schema_route_result is not None:
            return schema_route_result

        route_scores: dict[str, list[str]] = {}

        for route, keywords in self.route_keywords.items():
            matched = [
                keyword
                for keyword in keywords
                if keyword in question
            ]

            if matched:
                route_scores[route] = matched

        if not route_scores:
            return RouteResult(
                route=self.ROUTE_UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                reason="No matching route keywords found.",
            )

        selected_route = self._select_best_route(route_scores)
        matched_keywords = route_scores[selected_route]

        confidence = self._calculate_confidence(
            matched_keyword_count=len(matched_keywords),
            question_length=len(question.split()),
        )

        return RouteResult(
            route=selected_route,
            confidence=confidence,
            matched_keywords=matched_keywords,
            reason=f"Matched keywords for route {selected_route}: {matched_keywords}",
        )

    def _load_route_keywords(
        self,
        config_path: str,
    ) -> dict[str, list[str]]:
        path = Path(config_path)

        if not path.exists():
            return self._get_default_route_keywords()

        try:
            with path.open("r", encoding="utf-8") as file:
                loaded_keywords = json.load(file)

            return self._validate_route_keywords(loaded_keywords)

        except (json.JSONDecodeError, OSError, TypeError):
            return self._get_default_route_keywords()

    def _validate_route_keywords(
        self,
        loaded_keywords: dict[str, Any],
    ) -> dict[str, list[str]]:
        default_keywords = self._get_default_route_keywords()

        valid_routes = set(default_keywords.keys())

        validated_keywords: dict[str, list[str]] = {}

        for route_name, keywords in loaded_keywords.items():
            if route_name not in valid_routes:
                continue

            if not isinstance(keywords, list):
                continue

            validated_keywords[route_name] = [
                str(keyword).lower().strip()
                for keyword in keywords
                if str(keyword).strip()
            ]

        for route_name, default_route_keywords in default_keywords.items():
            if route_name not in validated_keywords:
                validated_keywords[route_name] = default_route_keywords

        return validated_keywords
    
    def _get_default_route_keywords(self) -> dict[str, list[str]]:
        return {
            self.ROUTE_DIRECT_ANALYSIS: [
                "shape",
                "rows",
                "columns",
                "data types",
                "dtypes",
                "missing",
                "null",
                "nan",
                "duplicate",
                "sample",
                "preview",
                "numeric summary",
                "categorical summary",
                "unique",
                "unique values",
                "distinct",
                "distinct values",
            ],
            self.ROUTE_VISUALIZATION: [
                "chart",
                "plot",
                "visualize",
                "visualization",
                "graph",
                "bar chart",
                "line chart",
                "histogram",
                "scatter",
                "draw",
                "unique",
                "unique values",
                "distinct",
                "distinct values",
            ],
            self.ROUTE_EDA_INSIGHT: [
                "insight",
                "insights",
                "analyze",
                "analysis",
                "trend",
                "patterns",
                "eda",
            ],
            self.ROUTE_CODEGEN_SQL: [
                "code",
                "pandas",
                "sql",
                "query",
                "generate code",
                "write code",
            ],
            self.ROUTE_PLANNING: [
                "plan",
                "workflow",
                "steps",
                "what should i do",
                "what should i do next",
                "next steps",
                "analysis plan",
                "roadmap",
                "process",
                "pipeline",
            ],
            self.ROUTE_PERSONALIZATION: [
                "beginner",
                "simple",
                "simplify",
                "technical",
                "non-technical",
                "concise",
                "detailed",
                "personalize",
                "customize",
                "adapt",
            ],
            self.ROUTE_CLEANING: [
                "clean",
                "preprocess",
                "pre-process",
                "convert types",
                "handle missing",
                "handle null",
                "handle nan",
                "remove duplicates",
                "data cleaning",
                "data preprocessing",
                "làm sạch",
                "tiền xử lý",
                "chuẩn hóa",
            ],
        }

    def _select_best_route(self, route_scores: dict[str, list[str]]) -> str:
        best_route = None
        best_score = -1

        for route in self.priority_order:
            if route not in route_scores:
                continue

            score = len(route_scores[route])

            if score > best_score:
                best_route = route
                best_score = score

        if best_route is None:
            return self.ROUTE_UNKNOWN

        return best_route

    def _calculate_confidence(
        self,
        matched_keyword_count: int,
        question_length: int,
    ) -> float:
        if question_length <= 0:
            return 0.0

        confidence = 0.5 + matched_keyword_count * 0.15
        return min(round(confidence, 2), 0.95)
    
    def _route_schema_aware_question(
        self,
        question: str,
        profile: dict | None,
    ) -> RouteResult | None:
        if profile is None:
            return None

        columns = profile.get("columns", [])

        mentioned_columns = self._find_mentioned_columns(
            question=question,
            columns=columns,
        )

        if not mentioned_columns:
            return None

        column_question_keywords = [
            "tell me about",
            "what is",
            "what are",
            "describe",
            "summarize",
            "summary of",
            "information about",
            "explain",
            "about",
            "cho mình biết về",
            "cho tôi biết về",
            "nói về",
            "mô tả",
            "tóm tắt",
            "giải thích",
            "thông tin về",
        ]

        normalized_question = self._normalize_text_for_matching(question)
        if self._contains_any(normalized_question, column_question_keywords):
            return RouteResult(
                route=self.ROUTE_DIRECT_ANALYSIS,
                confidence=0.75,
                matched_keywords=[
                    "schema_aware_column_query",
                    *[f"column:{column}" for column in mentioned_columns],
                ],
                reason=(
                    "Detected a schema-aware column question for columns: "
                    f"{mentioned_columns}"
                ),
            )

        return None

    def _find_mentioned_columns(
        self,
        question: str,
        columns: list[str],
    ) -> list[str]:
        normalized_question = self._normalize_text_for_matching(question)

        mentioned_columns = []

        sorted_columns = sorted(
            columns,
            key=lambda column: len(str(column)),
            reverse=True,
        )

        for column in sorted_columns:
            column_name = str(column)
            normalized_column = self._normalize_text_for_matching(column_name)

            if normalized_column in normalized_question:
                mentioned_columns.append(column_name)

        return mentioned_columns

    def _normalize_text_for_matching(self, text: str) -> str:
        normalized = str(text).lower()
        normalized = normalized.replace("_", " ")
        normalized = normalized.replace("-", " ")
        normalized = normalized.replace('"', " ")
        normalized = normalized.replace("'", " ")
        normalized = normalized.replace("`", " ")
        normalized = " ".join(normalized.split())

        return normalized

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)