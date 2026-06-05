from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ColumnContext:
    column: str
    dtype: str
    missing_count: int
    missing_percentage: float
    score: float
    reasons: list[str]
    summary: dict[str, Any]


@dataclass
class TableContextResult:
    selected_columns: list[str]
    dropped_columns: list[str]
    column_contexts: list[ColumnContext]
    sample_rows: list[dict[str, Any]]
    row_count: int
    column_count: int
    warnings: list[str]


class TableContextAgent:
    """
    Week 11 v0.7:
    Query-aware table context selector.

    This agent selects the most relevant columns and compact table context
    for downstream LLM explanation or analysis.
    """

    def build_context(
        self,
        question: str,
        df: pd.DataFrame,
        profile: dict[str, Any],
        max_columns: int = 6,
        max_sample_rows: int = 5,
    ) -> TableContextResult:
        columns = profile.get("columns", list(df.columns))
        warnings: list[str] = []

        scored_columns = [
            self._score_column(question, column, profile)
            for column in columns
        ]

        scored_columns = sorted(
            scored_columns,
            key=lambda item: item.score,
            reverse=True,
        )

        selected_contexts = [
            context
            for context in scored_columns
            if context.score > 0
        ][:max_columns]

        if not selected_contexts:
            warnings.append(
                "No query-specific columns were detected. Selected the first columns as fallback context."
            )
            selected_columns = [str(column) for column in columns[:max_columns]]
            selected_contexts = [
                self._score_column(question, column, profile)
                for column in selected_columns
            ]
        else:
            selected_columns = [
                context.column
                for context in selected_contexts
            ]

        dropped_columns = [
            str(column)
            for column in columns
            if str(column) not in selected_columns
        ]

        sample_rows = self._build_sample_rows(
            df=df,
            selected_columns=selected_columns,
            max_sample_rows=max_sample_rows,
        )

        return TableContextResult(
            selected_columns=selected_columns,
            dropped_columns=dropped_columns,
            column_contexts=selected_contexts,
            sample_rows=sample_rows,
            row_count=profile.get("shape", {}).get("rows", len(df)),
            column_count=profile.get("shape", {}).get("columns", len(df.columns)),
            warnings=warnings,
        )

    def format_context_as_markdown(self, result: TableContextResult) -> str:
        lines = [
            "## Query-Aware Table Context",
            "",
            f"- Rows: {result.row_count}",
            f"- Columns: {result.column_count}",
            f"- Selected columns: {', '.join(result.selected_columns)}",
            "",
        ]

        if result.warnings:
            lines.append("### Warnings")
            for warning in result.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        lines.append("### Column Context")

        for context in result.column_contexts:
            lines.append(f"#### `{context.column}`")
            lines.append(f"- Data type: `{context.dtype}`")
            lines.append(
                f"- Missing values: {context.missing_count} ({context.missing_percentage}%)"
            )
            lines.append(f"- Relevance score: {context.score}")

            if context.reasons:
                lines.append("- Selection reasons:")
                for reason in context.reasons:
                    lines.append(f"  - {reason}")

            if context.summary:
                lines.append("- Summary:")
                for key, value in context.summary.items():
                    lines.append(f"  - `{key}`: {value}")

            lines.append("")

        if result.sample_rows:
            lines.append("### Sample Rows")
            for index, row in enumerate(result.sample_rows, start=1):
                lines.append(f"- Row {index}: {row}")

        return "\n".join(lines)

    def _score_column(
        self,
        question: str,
        column: str,
        profile: dict[str, Any],
    ) -> ColumnContext:
        column = str(column)

        question_normalized = self._normalize_text(question)
        column_normalized = self._normalize_text(column)

        dtypes = profile.get("dtypes", {})
        missing_values = profile.get("missing_values", {})
        missing_percentage = profile.get("missing_percentage", {})
        numeric_summary = profile.get("numeric_summary", {})
        categorical_summary = profile.get("categorical_summary", {})

        dtype = str(dtypes.get(column, "unknown"))
        missing_count = int(missing_values.get(column, 0))
        missing_pct = float(missing_percentage.get(column, 0.0))

        score = 0.0
        reasons: list[str] = []

        if column_normalized in question_normalized:
            score += 5.0
            reasons.append("Column name was directly mentioned in the question.")

        column_terms = set(column_normalized.split())
        question_terms = set(question_normalized.split())

        overlapping_terms = column_terms.intersection(question_terms)

        if overlapping_terms:
            score += len(overlapping_terms)
            reasons.append(
                f"Question shares terms with column name: {sorted(overlapping_terms)}."
            )

        if self._contains_any(question_normalized, ["missing", "null", "nan", "thiếu"]):
            if missing_count > 0:
                score += 3.0
                reasons.append("Question asks about missing values and this column has missing values.")

        if self._contains_any(
            question_normalized,
            ["numeric", "number", "mean", "median", "min", "max", "statistics", "summary"],
        ):
            if column in numeric_summary:
                score += 2.0
                reasons.append("Question asks for numeric/statistical information.")

        if self._contains_any(
            question_normalized,
            ["category", "categorical", "top", "unique", "group", "region", "product"],
        ):
            if column in categorical_summary:
                score += 2.0
                reasons.append("Question asks for categorical information.")

        if self._contains_any(question_normalized, ["date", "time", "trend", "over time"]):
            if "datetime" in dtype.lower() or "date" in column_normalized:
                score += 2.0
                reasons.append("Question asks for time-related information.")

        if self._contains_any(question_normalized, ["chart", "plot", "visualize", "graph", "biểu đồ"]):
            if column in numeric_summary or column in categorical_summary or "datetime" in dtype.lower():
                score += 1.0
                reasons.append("Column is useful for visualization context.")

        summary = self._build_column_summary(
            column=column,
            profile=profile,
        )

        return ColumnContext(
            column=column,
            dtype=dtype,
            missing_count=missing_count,
            missing_percentage=missing_pct,
            score=score,
            reasons=reasons,
            summary=summary,
        )

    def _build_column_summary(
        self,
        column: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        numeric_summary = profile.get("numeric_summary", {})
        categorical_summary = profile.get("categorical_summary", {})

        if column in numeric_summary:
            stats = numeric_summary[column]

            return {
                "kind": "numeric",
                "count": stats.get("count"),
                "mean": stats.get("mean"),
                "median": stats.get("median"),
                "min": stats.get("min"),
                "max": stats.get("max"),
            }

        if column in categorical_summary:
            summary = categorical_summary[column]

            return {
                "kind": "categorical",
                "unique_count": summary.get("unique_count"),
                "top_values": summary.get("top_values", {}),
            }

        dtype = str(profile.get("dtypes", {}).get(column, ""))

        if "datetime" in dtype.lower():
            return {
                "kind": "datetime",
            }

        return {
            "kind": "text_or_unknown",
        }

    def _build_sample_rows(
        self,
        df: pd.DataFrame,
        selected_columns: list[str],
        max_sample_rows: int,
    ) -> list[dict[str, Any]]:
        available_columns = [
            column
            for column in selected_columns
            if column in df.columns
        ]

        if not available_columns:
            return []

        sample_df = df[available_columns].head(max_sample_rows)

        rows = []

        for row in sample_df.to_dict(orient="records"):
            rows.append(
                {
                    key: self._to_serializable(value)
                    for key, value in row.items()
                }
            )

        return rows

    def _to_serializable(self, value: Any) -> Any:
        if pd.isna(value):
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        if hasattr(value, "item"):
            return value.item()

        return value

    def _normalize_text(self, text: str) -> str:
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