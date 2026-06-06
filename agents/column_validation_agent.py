from __future__ import annotations

import difflib
from dataclasses import dataclass


@dataclass
class ColumnValidationResult:
    has_missing_columns: bool
    mentioned_columns: list[str]
    missing_columns: list[str]
    existing_columns: list[str]
    suggestions: dict[str, list[str]]
    warnings: list[str]


class ColumnValidationAgent:
    """
    Detects likely column mentions that do not exist in the dataset schema.
    This is a lightweight guard against hallucinated or invalid columns.
    """

    def validate_question_columns(
        self,
        question: str,
        available_columns: list[str],
    ) -> ColumnValidationResult:
        normalized_question = self._normalize_text(question)

        existing_columns = []
        missing_columns = []

        for column in available_columns:
            normalized_column = self._normalize_text(column)

            if normalized_column in normalized_question:
                existing_columns.append(column)

        candidate_phrases = self._extract_candidate_phrases(
            question=question,
            available_columns=available_columns,
        )

        for phrase in candidate_phrases:
            normalized_phrase = self._normalize_text(phrase)

            if not normalized_phrase:
                continue

            if self._matches_existing_column(
                normalized_phrase=normalized_phrase,
                available_columns=available_columns,
            ):
                continue

            if normalized_phrase not in [
                self._normalize_text(column)
                for column in missing_columns
            ]:
                missing_columns.append(phrase)

        suggestions = {
            missing_column: self._suggest_columns(
                missing_column=missing_column,
                available_columns=available_columns,
            )
            for missing_column in missing_columns
        }

        warnings = []

        if missing_columns:
            warnings.append(
                "The prompt appears to mention columns that are not in the dataset."
            )

        return ColumnValidationResult(
            has_missing_columns=bool(missing_columns),
            mentioned_columns=existing_columns + missing_columns,
            missing_columns=missing_columns,
            existing_columns=existing_columns,
            suggestions=suggestions,
            warnings=warnings,
        )

    def format_result_as_markdown(
        self,
        result: ColumnValidationResult,
    ) -> str:
        if not result.has_missing_columns:
            return "All mentioned columns appear to exist in the dataset."

        lines = [
            "I found possible column names that do not exist in the dataset.",
            "",
            "Missing columns:",
        ]

        for column in result.missing_columns:
            lines.append(f"- `{column}`")

            suggested_columns = result.suggestions.get(column, [])

            if suggested_columns:
                lines.append("  Similar available columns:")

                for suggestion in suggested_columns:
                    lines.append(f"  - `{suggestion}`")

        lines.extend(
            [
                "",
                "Please revise the prompt using valid dataset columns.",
            ]
        )

        return "\n".join(lines)

    def _extract_candidate_phrases(
        self,
        question: str,
        available_columns: list[str],
    ) -> list[str]:
        """
        Lightweight extraction for common column-like phrases.

        Important:
        If a multi-word phrase already matches an existing column
        such as "gross revenue" -> gross_revenue,
        do not also treat "gross" and "revenue" as missing columns.
        """
        normalized_question = self._normalize_text(question)

        known_words = {
            "show",
            "tell",
            "me",
            "about",
            "draw",
            "chart",
            "of",
            "by",
            "group",
            "write",
            "pandas",
            "code",
            "sql",
            "query",
            "to",
            "the",
            "a",
            "an",
            "for",
            "with",
            "and",
            "over",
            "under",
            "between",
            "theo",
            "vẽ",
            "biểu",
            "đồ",
            "cho",
            "mình",
            "xem",
            "biết",
            "về",
            "nhóm",
            "viết",
            "mã",
            "truy",
            "vấn",
        }

        tokens = [
            token
            for token in normalized_question.split()
            if token not in known_words
        ]

        available_normalized = [
            self._normalize_text(column)
            for column in available_columns
        ]

        candidates: list[str] = []
        used_token_indexes: set[int] = set()

        # First handle two-token phrases.
        # This catches phrases like "profit margin" or "net income".
        # It also protects existing columns like "gross revenue" from being split.
        for index in range(len(tokens) - 1):
            if index in used_token_indexes or index + 1 in used_token_indexes:
                continue

            phrase = f"{tokens[index]} {tokens[index + 1]}"

            if phrase in available_normalized:
                used_token_indexes.add(index)
                used_token_indexes.add(index + 1)
                continue

            if self._looks_like_column_phrase(phrase):
                candidates.append(phrase)
                used_token_indexes.add(index)
                used_token_indexes.add(index + 1)

        # Then handle remaining single-token candidates.
        for index, token in enumerate(tokens):
            if index in used_token_indexes:
                continue

            if token in available_normalized:
                continue

            if self._looks_like_column_word(token):
                candidates.append(token)

        return list(dict.fromkeys(candidates))
    
    def _matches_existing_column(
        self,
        normalized_phrase: str,
        available_columns: list[str],
    ) -> bool:
        available_normalized = [
            self._normalize_text(column)
            for column in available_columns
        ]

        return normalized_phrase in available_normalized

    def _suggest_columns(
        self,
        missing_column: str,
        available_columns: list[str],
        limit: int = 3,
    ) -> list[str]:
        normalized_available = {
            self._normalize_text(column): column
            for column in available_columns
        }

        close_matches = difflib.get_close_matches(
            self._normalize_text(missing_column),
            list(normalized_available.keys()),
            n=limit,
            cutoff=0.35,
        )

        return [
            normalized_available[match]
            for match in close_matches
        ]

    def _looks_like_column_word(self, token: str) -> bool:
        if len(token) <= 2:
            return False

        blocked = {
            "missing",
            "values",
            "value",
            "chart",
            "histogram",
            "scatter",
            "line",
            "bar",
            "summary",
            "data",
            "dataset",
            "rows",
            "columns",
            "column",
        }

        return token not in blocked

    def _looks_like_column_phrase(self, phrase: str) -> bool:
        blocked_phrases = {
            "missing values",
            "bar chart",
            "line chart",
            "scatter plot",
            "numeric summary",
            "categorical summary",
        }

        return phrase not in blocked_phrases

    def _normalize_text(self, text: str) -> str:
        normalized = str(text).lower()
        normalized = normalized.replace("_", " ")
        normalized = normalized.replace("-", " ")
        normalized = normalized.replace('"', " ")
        normalized = normalized.replace("'", " ")
        normalized = normalized.replace("`", " ")
        normalized = " ".join(normalized.split())

        return normalized