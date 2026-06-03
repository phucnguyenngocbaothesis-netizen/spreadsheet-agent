from __future__ import annotations

from typing import Any


class DirectAnalysisAgent:
    """
    Week 2 v0.3:
    Answer deterministic questions using the dataset profile.
    No LLM is used here.
    """

    def answer(self, question: str, profile: dict[str, Any]) -> str:
        question_lower = question.lower().strip()

        if self._contains_any(question_lower, ["duplicate", "duplicated"]):
            return self._answer_duplicates(profile)

        if self._contains_any(question_lower, ["missing", "null", "nan"]):
            return self._answer_missing_values(profile)

        if self._contains_any(question_lower, ["numeric summary", "statistics", "stats", "describe"]):
            return self._answer_numeric_summary(profile)

        if self._contains_any(question_lower, ["categorical summary", "top values", "value counts"]):
            return self._answer_categorical_summary(profile)

        if self._contains_any(question_lower, ["unique", "distinct"]):
            return self._answer_unique_values(profile)

        if self._contains_any(question_lower, ["sample", "preview", "head", "first rows"]):
            return self._answer_sample_rows(profile)

        if self._contains_any(question_lower, ["dtype", "data type", "types"]):
            return self._answer_dtypes(profile)

        if self._contains_any(question_lower, ["column names", "columns", "fields"]):
            return self._answer_columns(profile)

        if self._contains_any(question_lower, ["shape", "size", "row count", "column count", "how many rows"]):
            return self._answer_shape(profile)

        return (
            "This version can answer questions about shape, columns, data types, "
            "missing values, duplicate rows, numeric summary, categorical summary, "
            "unique values, and sample rows."
        )

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _answer_shape(self, profile: dict[str, Any]) -> str:
        rows = profile["shape"]["rows"]
        columns = profile["shape"]["columns"]

        return f"The dataset has **{rows} rows** and **{columns} columns**."

    def _answer_columns(self, profile: dict[str, Any]) -> str:
        columns = profile["columns"]
        column_text = "\n".join(f"- `{column}`" for column in columns)

        return f"The dataset contains these columns:\n\n{column_text}"

    def _answer_dtypes(self, profile: dict[str, Any]) -> str:
        dtypes = profile["dtypes"]
        dtype_text = "\n".join(
            f"- `{column}`: `{dtype}`"
            for column, dtype in dtypes.items()
        )

        return f"Detected data types:\n\n{dtype_text}"

    def _answer_missing_values(self, profile: dict[str, Any]) -> str:
        missing_values = profile["missing_values"]
        missing_percentage = profile["missing_percentage"]

        rows = []
        for column, missing_count in missing_values.items():
            percentage = missing_percentage[column]
            rows.append(f"- `{column}`: {missing_count} missing values ({percentage}%)")

        return "Missing value summary:\n\n" + "\n".join(rows)

    def _answer_duplicates(self, profile: dict[str, Any]) -> str:
        duplicate_rows = profile["duplicate_rows"]

        return f"The dataset has **{duplicate_rows} duplicate rows**."

    def _answer_numeric_summary(self, profile: dict[str, Any]) -> str:
        numeric_summary = profile.get("numeric_summary", {})

        if not numeric_summary:
            return "No numeric columns were detected."

        lines = []

        for column, stats in numeric_summary.items():
            lines.append(f"### `{column}`")
            lines.append(f"- Count: {stats['count']}")
            lines.append(f"- Mean: {stats['mean']}")
            lines.append(f"- Median: {stats['median']}")
            lines.append(f"- Standard deviation: {stats['std']}")
            lines.append(f"- Min: {stats['min']}")
            lines.append(f"- Max: {stats['max']}")

        return "Numeric summary:\n\n" + "\n".join(lines)

    def _answer_categorical_summary(self, profile: dict[str, Any]) -> str:
        categorical_summary = profile.get("categorical_summary", {})

        if not categorical_summary:
            return "No categorical columns were detected."

        lines = []

        for column, summary in categorical_summary.items():
            lines.append(f"### `{column}`")
            lines.append(f"- Unique values: {summary['unique_count']}")

            top_values = summary["top_values"]

            if top_values:
                lines.append("- Top values:")
                for value, count in top_values.items():
                    lines.append(f"  - `{value}`: {count}")

        return "Categorical summary:\n\n" + "\n".join(lines)

    def _answer_unique_values(self, profile: dict[str, Any]) -> str:
        categorical_summary = profile.get("categorical_summary", {})

        if not categorical_summary:
            return "No categorical columns were detected."

        lines = []

        for column, summary in categorical_summary.items():
            lines.append(f"- `{column}`: {summary['unique_count']} unique values")

        return "Unique value count:\n\n" + "\n".join(lines)

    def _answer_sample_rows(self, profile: dict[str, Any]) -> str:
        sample_rows = profile.get("sample_rows", [])

        if not sample_rows:
            return "No sample rows are available."

        lines = []

        for index, row in enumerate(sample_rows, start=1):
            lines.append(f"### Row {index}")
            for column, value in row.items():
                lines.append(f"- `{column}`: {value}")

        return "Sample rows:\n\n" + "\n".join(lines)