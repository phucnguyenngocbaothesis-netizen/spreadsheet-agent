from __future__ import annotations

from typing import Any


class DirectAnalysisAgent:
    """
    Week 2 v0.3:
    Answer deterministic questions using the dataset profile.
    No LLM is used here.
    """

    def answer(
        self,
        question: str,
        profile: dict,
        language: str = "en",
    ) -> str:
        question_lower = question.lower().strip()

        if self._contains_any(question_lower, ["duplicate", "duplicated",  "trùng", "lặp", "trùng lặp", "dòng trùng"]):
            return self._answer_duplicates(profile, language)

        if self._contains_any(
            question_lower,
            ["missing", "null", "nan", "thiếu", "giá trị thiếu", "dữ liệu thiếu"],
        ):
            return self._answer_missing_values(profile, language)

        mentioned_column = self._find_mentioned_column(question_lower, profile)

        if mentioned_column is not None and self._is_column_summary_question(question_lower):
            return self._answer_column_summary(profile, mentioned_column)

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

    def _answer_missing_values(
        self,
        profile: dict,
        language: str = "en",
    ) -> str:
        missing_values = profile.get("missing_values", {})
        missing_percentage = profile.get("missing_percentage", {})

        if language == "vi":
            lines = ["Tóm tắt giá trị thiếu:", ""]

            for column, count in missing_values.items():
                percentage = missing_percentage.get(column, 0.0)
                lines.append(
                    f"- `{column}`: {count} giá trị thiếu ({percentage}%)"
                )

            return "\n".join(lines)

        lines = ["Missing value summary:", ""]

        for column, count in missing_values.items():
            percentage = missing_percentage.get(column, 0.0)
            lines.append(
                f"- `{column}`: {count} missing values ({percentage}%)"
            )

        return "\n".join(lines)


    def _answer_duplicates(
        self,
        profile: dict,
        language: str = "en",
    ) -> str:
        duplicate_rows = profile.get("duplicate_rows", 0)

        if language == "vi":
            return f"Dataset có **{duplicate_rows} dòng trùng lặp**."

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
    
    def _is_column_summary_question(self, question_lower: str) -> bool:
        return self._contains_any(
            question_lower,
            [
                "tell me about",
                "what is",
                "what are",
                "describe",
                "summarize",
                "summary of",
                "information about",
                "explain",
                "about",
            ],
        )

    def _find_mentioned_column(
        self,
        question_lower: str,
        profile: dict[str, Any],
    ) -> str | None:
        columns = profile.get("columns", [])
        normalized_question = self._normalize_text_for_matching(question_lower)

        sorted_columns = sorted(
            columns,
            key=lambda column: len(str(column)),
            reverse=True,
        )

        for column in sorted_columns:
            normalized_column = self._normalize_text_for_matching(str(column))

            if normalized_column in normalized_question:
                return str(column)

        return None

    def _normalize_text_for_matching(self, text: str) -> str:
        normalized = str(text).lower()
        normalized = normalized.replace("_", " ")
        normalized = normalized.replace("-", " ")
        normalized = normalized.replace('"', " ")
        normalized = normalized.replace("'", " ")
        normalized = normalized.replace("`", " ")
        normalized = " ".join(normalized.split())

        return normalized

    def _answer_column_summary(
        self,
        profile: dict[str, Any],
        column: str,
    ) -> str:
        dtypes = profile.get("dtypes", {})
        missing_values = profile.get("missing_values", {})
        missing_percentage = profile.get("missing_percentage", {})
        numeric_summary = profile.get("numeric_summary", {})
        categorical_summary = profile.get("categorical_summary", {})
        sample_rows = profile.get("sample_rows", [])

        dtype = dtypes.get(column, "unknown")
        missing_count = missing_values.get(column, 0)
        missing_pct = missing_percentage.get(column, 0.0)

        lines = [
            f"Column summary for `{column}`:",
            "",
            f"- Data type: `{dtype}`",
            f"- Missing values: {missing_count} ({missing_pct}%)",
        ]

        if column in numeric_summary:
            stats = numeric_summary[column]

            lines.extend(
                [
                    "- Column kind: numeric",
                    f"- Count: {stats.get('count')}",
                    f"- Mean: {stats.get('mean')}",
                    f"- Median: {stats.get('median')}",
                    f"- Min: {stats.get('min')}",
                    f"- Max: {stats.get('max')}",
                ]
            )

        elif column in categorical_summary:
            summary = categorical_summary[column]
            top_values = summary.get("top_values", {})

            lines.extend(
                [
                    "- Column kind: categorical",
                    f"- Unique values: {summary.get('unique_count')}",
                ]
            )

            if top_values:
                lines.append("- Top values:")

                for value, count in top_values.items():
                    lines.append(f"  - `{value}`: {count}")

        elif "datetime" in dtype.lower():
            lines.append("- Column kind: datetime")

        else:
            lines.append("- Column kind: text or unknown")

        sample_values = []

        for row in sample_rows:
            if column in row and row[column] is not None:
                sample_values.append(row[column])

        if sample_values:
            unique_sample_values = list(dict.fromkeys(sample_values))[:5]
            lines.append("- Sample values:")

            for value in unique_sample_values:
                lines.append(f"  - `{value}`")

        return "\n".join(lines)