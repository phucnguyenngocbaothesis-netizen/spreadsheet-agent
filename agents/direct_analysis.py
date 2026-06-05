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

        if self._contains_any(
            question_lower,
            ["missing", "null", "nan", "thiếu", "giá trị thiếu", "dữ liệu thiếu"],
        ):
            return self._answer_missing_values(profile, language)

        if self._contains_any(
            question_lower,
            ["duplicate", "duplicates", "trùng", "lặp", "trùng lặp", "dòng trùng"],
        ):
            return self._answer_duplicates(profile, language)

        if self._contains_any(
            question_lower,
            ["sample", "preview", "head", "show sample rows", "xem trước", "mẫu dữ liệu", "dòng mẫu"],
        ):
            return self._answer_sample_rows(profile, language)

        if self._contains_any(
            question_lower,
            ["columns", "column names", "show columns", "cột", "tên cột"],
        ):
            return self._answer_columns(profile, language)

        if self._contains_any(
            question_lower,
            ["data types", "dtypes", "types", "kiểu dữ liệu", "loại dữ liệu"],
        ):
            return self._answer_dtypes(profile, language)

        mentioned_column = self._find_mentioned_column(question_lower, profile)

        if mentioned_column is not None and self._is_column_summary_question(question_lower):
            return self._answer_column_summary(profile, mentioned_column, language)

        if self._contains_any(
            question_lower,
            [
                "numeric summary",
                "statistics",
                "stats",
                "describe",
                "thống kê số",
                "tóm tắt số",
            ],
        ):
            return self._answer_numeric_summary(profile, language)

        if self._contains_any(
            question_lower,
            [
                "categorical summary",
                "unique",
                "unique values",
                "category",
                "categorical",
                "tóm tắt phân loại",
                "giá trị duy nhất",
                "giá trị khác nhau",
            ],
        ):
            return self._answer_categorical_summary(profile, language)

        if self._contains_any(
            question_lower,
            ["shape", "rows", "columns count", "số dòng", "số cột", "kích thước"],
        ):
            return self._answer_shape(profile, language)

        return (
            "This version can answer questions about shape, columns, data types, "
            "missing values, duplicate rows, numeric summary, categorical summary, "
            "unique values, and sample rows."
        )
    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _answer_shape(self, profile: dict[str, Any], language: str = "en") -> str:
        rows = profile["shape"]["rows"]
        columns = profile["shape"]["columns"]

        if language == "vi":
            return f"Dataset có **{rows} dòng** và **{columns} cột**."

        return f"The dataset has **{rows} rows** and **{columns} columns**."

    def _answer_columns(
        self,
        profile: dict,
        language: str = "en",
    ) -> str:
        columns = profile.get("columns", [])

        if language == "vi":
            lines = ["Các cột trong dataset:", ""]
        else:
            lines = ["Dataset columns:", ""]

        for column in columns:
            lines.append(f"- `{column}`")

        return "\n".join(lines)

    def _answer_dtypes(
        self,
        profile: dict,
        language: str = "en",
    ) -> str:
        dtypes = profile.get("dtypes", {})

        if language == "vi":
            lines = ["Kiểu dữ liệu của các cột:", ""]
        else:
            lines = ["Column data types:", ""]

        for column, dtype in dtypes.items():
            lines.append(f"- `{column}`: `{dtype}`")

        return "\n".join(lines)

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

    def _answer_numeric_summary(self, profile: dict, language: str = "en") -> str:
        numeric_summary = profile.get("numeric_summary", {})

        if not numeric_summary:
            if language == "vi":
                return "Không có cột số nào được phát hiện."
            return "No numeric columns were detected."

        if language == "vi":
            lines = ["Tóm tắt các cột số:", ""]
        else:
            lines = ["Numeric column summary:", ""]

        for column, stats in numeric_summary.items():
            lines.append(f"### `{column}`")
            lines.append(f"- Count: {stats['count']}")
            lines.append(f"- Mean: {stats['mean']}")
            lines.append(f"- Median: {stats['median']}")
            lines.append(f"- Standard deviation: {stats['std']}")
            lines.append(f"- Min: {stats['min']}")
            lines.append(f"- Max: {stats['max']}")

        return "Numeric summary:\n\n" + "\n".join(lines)

    def _answer_categorical_summary(self, profile: dict[str, Any], language: str = "en") -> str:
        categorical_summary = profile.get("categorical_summary", {})

        if not categorical_summary:
            if language == "vi":
                return "Không có cột phân loại nào được phát hiện."
            return "No categorical columns were detected."

        if language == "vi":
            lines = ["Tóm tắt các cột phân loại:", ""] 
        else:
            lines = ["Categorical column summary:", ""]

        for column, summary in categorical_summary.items():
            lines.append(f"### `{column}`")
            lines.append(f"- Unique values: {summary['unique_count']}")

            top_values = summary["top_values"]

            if top_values:
                lines.append("- Top values:")
                for value, count in top_values.items():
                    lines.append(f"  - `{value}`: {count}")

        return "Categorical summary:\n\n" + "\n".join(lines)

    def _answer_unique_values(self, profile: dict[str, Any], language: str = "en") -> str:
        categorical_summary = profile.get("categorical_summary", {})

        if not categorical_summary:
            if language == "vi":
                return "Không có cột phân loại nào được phát hiện." 
            return "No categorical columns were detected."

        if language == "vi":
            lines = ["Tóm tắt số lượng giá trị duy nhất:", ""]
        else:
            lines = ["Unique value count:", ""]

        for column, summary in categorical_summary.items():
            lines.append(f"- `{column}`: {summary['unique_count']} unique values")

        return "\n".join(lines)

    def _answer_sample_rows(self, profile: dict[str, Any], language: str = "en") -> str:
        sample_rows = profile.get("sample_rows", [])

        if not sample_rows:
            if language == "vi":
                return "Không có hàng mẫu nào khả dụng."
            return "No sample rows are available."

        if language == "vi":
            lines = ["Giá trị mẫu:", ""]
        else:
            lines = ["Sample rows:", ""]

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
                "cho mình biết về",
                "cho tôi biết về",
                "nói về",
                "mô tả",
                "tóm tắt",
                "giải thích",
                "thông tin về",
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
        profile: dict,
        column: str,
        language: str = "en",
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

        if language == "vi":
            lines = [
                f"Tóm tắt cột `{column}`:",
                "",
                f"- Kiểu dữ liệu: `{dtype}`",
                f"- Giá trị thiếu: {missing_count} ({missing_pct}%)",
            ]
        else:
            lines = [
                f"Column summary for `{column}`:",
                "",
                f"- Data type: `{dtype}`",
                f"- Missing values: {missing_count} ({missing_pct}%)",
            ]

        if column in numeric_summary:
            stats = numeric_summary[column]

            if language == "vi":
                lines.extend(
                    [
                        "- Loại cột: numeric",
                        f"- Count: {stats.get('count')}",
                        f"- Mean: {stats.get('mean')}",
                        f"- Median: {stats.get('median')}",
                        f"- Min: {stats.get('min')}",
                        f"- Max: {stats.get('max')}",
                    ]
                )
            else:
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

            if language == "vi":
                lines.extend(
                    [
                        "- Loại cột: categorical",
                        f"- Số giá trị duy nhất: {summary.get('unique_count')}",
                    ]
                )
            else:
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

        elif "datetime" in str(dtype).lower():
            lines.append(
                "- Loại cột: datetime"
                if language == "vi"
                else "- Column kind: datetime"
            )
        else:
            lines.append(
                "- Loại cột: text hoặc unknown"
                if language == "vi"
                else "- Column kind: text or unknown"
            )
        sample_values = []

        for row in sample_rows:
            if column in row and row[column] is not None:
                sample_values.append(row[column])

        if sample_values:
            unique_sample_values = list(dict.fromkeys(sample_values))[:5]
            lines.append("- Giá trị mẫu:" if language == "vi" else "- Sample values:")

            for value in unique_sample_values:
                lines.append(f"  - `{value}`")

        return "\n".join(lines)