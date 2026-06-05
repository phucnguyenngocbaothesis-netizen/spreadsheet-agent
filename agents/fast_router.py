from __future__ import annotations

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

    def __init__(self) -> None:
        self.route_keywords: dict[str, list[str]] = {
            self.ROUTE_DIRECT_ANALYSIS: [
                "shape",
                "size",
                "rows",
                "columns",
                "column names",
                "data types",
                "dtype",
                "missing",
                "null",
                "nan",
                "duplicate",
                "duplicated",
                "sample rows",
                "preview",
                "head",
                "first rows",
                "numeric summary",
                "statistics",
                "stats",
                "describe",
                "categorical summary",
                "top values",
                "value counts",
                "unique",
                "distinct",
            ],
            self.ROUTE_VISUALIZATION: [
                "chart",
                "plot",
                "visualize",
                "visualization",
                "graph",
                "bar chart",
                "line chart",
                "scatter",
                "histogram",
                "distribution", 
                "trend chart",
                "draw",
                "show chart",
            ],
            self.ROUTE_CODEGEN_SQL: [
                "code",
                "pandas",
                "python code",
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
                "explain like",
                "for manager",
                "for business",
                "technical",
                "non-technical",
                "concise",
                "detailed",
                "personalized",
                "personalize",
                "customize",
                "adapt",
                "make it easier",
                "make it simpler",
            ],
            self.ROUTE_CLEANING: [
                "clean",
                "normalize",
                "fix data",
                "remove empty",
                "convert types",
                "standardize",
            ],
            self.ROUTE_EDA_INSIGHT: [
                "insight",
                "eda",
                "analyze",
                "analysis",
                "pattern",
                "trend",
                "correlation",
                "outlier",
            ],
        }

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

    def _select_best_route(self, route_scores: dict[str, list[str]]) -> str:
        """
        Select route by:
        1. More matched keywords
        2. Priority order if tied
        """

        priority_order = [
            self.ROUTE_CODEGEN_SQL,
            self.ROUTE_PLANNING,
            self.ROUTE_VISUALIZATION,
            self.ROUTE_PERSONALIZATION,
            self.ROUTE_CLEANING,
            self.ROUTE_DIRECT_ANALYSIS,
            self.ROUTE_EDA_INSIGHT,
        ]

        best_route = None
        best_score = -1

        for route in priority_order:
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
        ]

        if self._contains_any(question, column_question_keywords):
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