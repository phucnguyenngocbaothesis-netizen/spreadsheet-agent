from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SchemaValidationResult:
    is_valid: bool
    valid_columns: list[str]
    invalid_columns: list[str]
    warnings: list[str]


@dataclass
class CodegenResult:
    mode: str
    code: str
    explanation: str
    warnings: list[str]
    generated_code_type: str
    required_inputs: list[str]
    assumptions: list[str]


class CodegenSQLAgent:
    """
    Week 5:
    Rule-based pandas / SQL code generator.

    This version does not use an LLM.
    It generates schema-grounded code from the dataset profile.
    """

    SQL_TABLE_NAME = "uploaded_table"

    def generate(self, question: str, profile: dict[str, Any]) -> CodegenResult:
        question_lower = question.lower().strip()

        if self._is_sql_request(question_lower):
            return self._generate_sql(question_lower, profile)

        return self._generate_pandas(question_lower, profile)

    def _generate_pandas(
        self,
        question_lower: str,
        profile: dict[str, Any],
    ) -> CodegenResult:
        columns = profile.get("columns", [])
        numeric_columns = self._get_numeric_columns(profile)
        categorical_columns = self._get_categorical_columns(profile)

        mentioned_columns = self._find_mentioned_columns(question_lower, columns)

        if self._contains_any(question_lower, ["missing", "null", "nan"]):
            code = (
                "missing_summary = df.isna().sum().reset_index()\n"
                "missing_summary.columns = ['column', 'missing_count']\n"
                "missing_summary['missing_percentage'] = (\n"
                "    missing_summary['missing_count'] / len(df) * 100\n"
                ")\n"
                "missing_summary"
            )

            return CodegenResult(
                mode="pandas",
                code=code,
                explanation="Generated pandas code to calculate missing values and missing percentages.",
                warnings=[],
                generated_code_type="pandas_missing_summary",
                required_inputs=["df"],
                assumptions=[
                    "The dataframe is already loaded as `df`.",
                    "Missing values are represented as pandas null values.",
                ],
            )

        if self._contains_any(
            question_lower,
            ["describe", "statistics", "stats", "numeric summary"],
        ):
            code = "df.describe()"

            return CodegenResult(
                mode="pandas",
                code=code,
                explanation="Generated pandas code to calculate descriptive statistics for numeric columns.",
                warnings=[],
                generated_code_type="pandas_describe",
                required_inputs=["df"],
                assumptions=[
                    "The dataframe is already loaded as `df`.",
                    "Numeric columns have already been normalized.",
                ],
            )

        if self._contains_any(question_lower, ["group", "groupby", "by"]):
            invalid_mentions = self.detect_invalid_column_mentions(
                question_lower=question_lower,
                profile=profile,
            )

            if invalid_mentions:
                warnings = [
                    f"The requested column `{column}` does not exist in the dataset."
                    for column in invalid_mentions
                ]

                return CodegenResult(
                    mode="pandas",
                    code="# Unable to generate groupby code because requested columns were not found.",
                    explanation="Code generation stopped because the user mentioned columns that are not in the dataset schema.",
                    warnings=warnings,
                    generated_code_type="pandas_groupby_failed_invalid_columns",
                    required_inputs=["df"],
                    assumptions=[
                        "The dataframe is already loaded as `df`.",
                        "Code generation should not silently replace missing user-requested columns.",
                    ],
                )

            group_column = self._select_column(mentioned_columns, categorical_columns)
            value_column = self._select_column(mentioned_columns, numeric_columns)

            if group_column is None and categorical_columns:
                group_column = categorical_columns[0]

            if value_column is None and numeric_columns:
                value_column = numeric_columns[0]

            validation = self.validate_groupby_request(
                group_column=group_column,
                value_column=value_column,
                profile=profile,
            )

            warnings = list(validation.warnings)

            if not validation.is_valid:
                code = "# Unable to generate groupby code because schema validation failed."
                generated_code_type = "pandas_groupby_failed_schema_validation"
            else:
                code = (
                    f'grouped = df.groupby("{group_column}", as_index=False)["{value_column}"].sum()\n'
                    f'grouped = grouped.sort_values("{value_column}", ascending=False)\n'
                    "grouped"
                )
                generated_code_type = "pandas_groupby_sum"

            return CodegenResult(
                mode="pandas",
                code=code,
                explanation="Generated pandas code for grouped aggregation.",
                warnings=warnings,
                generated_code_type=generated_code_type,
                required_inputs=["df"],
                assumptions=[
                    "The dataframe is already loaded as `df`.",
                    "The dataframe has already been normalized.",
                    "The aggregation operation uses sum by default.",
                ],
            )

        if self._contains_any(question_lower, ["sample", "preview", "head", "first rows"]):
            code = "df.head()"

            return CodegenResult(
                mode="pandas",
                code=code,
                explanation="Generated pandas code to preview the first rows of the dataframe.",
                warnings=[],
                generated_code_type="pandas_preview",
                required_inputs=["df"],
                assumptions=[
                    "The dataframe is already loaded as `df`.",
                ],
            )

        code = "df.head()"

        return CodegenResult(
            mode="pandas",
            code=code,
            explanation="No specific code pattern was detected, so generated a safe dataframe preview.",
            warnings=[
                "This is a fallback code template. More advanced code generation will be added later."
            ],
            generated_code_type="pandas_fallback_preview",
            required_inputs=["df"],
            assumptions=[
                "The dataframe is already loaded as `df`.",
                "The request was not specific enough for a specialized code template.",
            ],
        )

    def _generate_sql(
        self,
        question_lower: str,
        profile: dict[str, Any],
    ) -> CodegenResult:
        columns = profile.get("columns", [])
        numeric_columns = self._get_numeric_columns(profile)
        categorical_columns = self._get_categorical_columns(profile)

        mentioned_columns = self._find_mentioned_columns(question_lower, columns)

        if self._contains_any(question_lower, ["missing", "null"]):
            warnings = [
                "SQL missing-value checks are generated column by column.",
                "The table name is assumed to be uploaded_table.",
            ]

            select_parts = [
                (
                    f"SUM(CASE WHEN {self._quote_sql_identifier(column)} IS NULL "
                    f"THEN 1 ELSE 0 END) AS "
                    f"{self._quote_sql_identifier(column + '_missing')}"
                )
                for column in columns
            ]

            code = (
                "SELECT\n    "
                + ",\n    ".join(select_parts)
                + f"\nFROM {self.SQL_TABLE_NAME};"
            )

            return CodegenResult(
                mode="sql",
                code=code,
                explanation="Generated SQL query to count NULL values for each column.",
                warnings=warnings,
                generated_code_type="sql_missing_summary",
                required_inputs=[self.SQL_TABLE_NAME],
                assumptions=[
                    "The uploaded dataframe is available as a SQL table named uploaded_table.",
                    "Missing values are represented as SQL NULL values.",
                ],
            )

        if self._contains_any(question_lower, ["group", "group by", "by"]):
            invalid_mentions = self.detect_invalid_column_mentions(
                question_lower=question_lower,
                profile=profile,
            )

            if invalid_mentions:
                warnings = ["The table name is assumed to be uploaded_table."]
                warnings.extend(
                    f"The requested column `{column}` does not exist in the dataset."
                    for column in invalid_mentions
                )

                return CodegenResult(
                    mode="sql",
                    code="-- Unable to generate GROUP BY query because requested columns were not found.",
                    explanation="SQL generation stopped because the user mentioned columns that are not in the dataset schema.",
                    warnings=warnings,
                    generated_code_type="sql_groupby_failed_invalid_columns",
                    required_inputs=[self.SQL_TABLE_NAME],
                    assumptions=[
                        "The uploaded dataframe is available as a SQL table named uploaded_table.",
                        "SQL generation should not silently replace missing user-requested columns.",
                    ],
                )

            group_column = self._select_column(mentioned_columns, categorical_columns)
            value_column = self._select_column(mentioned_columns, numeric_columns)

            if group_column is None and categorical_columns:
                group_column = categorical_columns[0]

            if value_column is None and numeric_columns:
                value_column = numeric_columns[0]

            validation = self.validate_groupby_request(
                group_column=group_column,
                value_column=value_column,
                profile=profile,
            )

            warnings = ["The table name is assumed to be uploaded_table."]
            warnings.extend(validation.warnings)

            if not validation.is_valid:
                code = "-- Unable to generate GROUP BY query because schema validation failed."
                generated_code_type = "sql_groupby_failed_schema_validation"
            else:
                group_col_sql = self._quote_sql_identifier(group_column)
                value_col_sql = self._quote_sql_identifier(value_column)
                total_alias = self._quote_sql_identifier(f"total_{value_column}")

                code = (
                    f"SELECT\n"
                    f"    {group_col_sql},\n"
                    f"    SUM({value_col_sql}) AS {total_alias}\n"
                    f"FROM {self.SQL_TABLE_NAME}\n"
                    f"GROUP BY {group_col_sql}\n"
                    f"ORDER BY {total_alias} DESC;"
                )
                generated_code_type = "sql_groupby_sum"

            return CodegenResult(
                mode="sql",
                code=code,
                explanation="Generated SQL query for grouped aggregation.",
                warnings=warnings,
                generated_code_type=generated_code_type,
                required_inputs=[self.SQL_TABLE_NAME],
                assumptions=[
                    "The uploaded dataframe is available as a SQL table named uploaded_table.",
                    "The aggregation operation uses SUM by default.",
                ],
            )

        code = f"SELECT *\nFROM {self.SQL_TABLE_NAME}\nLIMIT 5;"

        return CodegenResult(
            mode="sql",
            code=code,
            explanation="Generated SQL query to preview the first rows of the table.",
            warnings=[
                "The table name is assumed to be uploaded_table.",
                "This is a fallback SQL template.",
            ],
            generated_code_type="sql_fallback_preview",
            required_inputs=[self.SQL_TABLE_NAME],
            assumptions=[
                "The uploaded dataframe is available as a SQL table named uploaded_table.",
                "The request was not specific enough for a specialized SQL template.",
            ],
        )

    def validate_columns(
        self,
        requested_columns: list[str],
        profile: dict[str, Any],
    ) -> SchemaValidationResult:
        available_columns = profile.get("columns", [])

        valid_columns = [
            column
            for column in requested_columns
            if column in available_columns
        ]

        invalid_columns = [
            column
            for column in requested_columns
            if column not in available_columns
        ]

        warnings = []

        if invalid_columns:
            warnings.append(
                f"These columns do not exist in the dataset: {invalid_columns}"
            )

        return SchemaValidationResult(
            is_valid=len(invalid_columns) == 0,
            valid_columns=valid_columns,
            invalid_columns=invalid_columns,
            warnings=warnings,
        )

    def validate_groupby_request(
        self,
        group_column: str | None,
        value_column: str | None,
        profile: dict[str, Any],
    ) -> SchemaValidationResult:
        requested_columns = [
            column
            for column in [group_column, value_column]
            if column is not None
        ]

        validation = self.validate_columns(requested_columns, profile)

        warnings = list(validation.warnings)

        numeric_columns = self._get_numeric_columns(profile)
        categorical_columns = self._get_categorical_columns(profile)

        if group_column is None:
            warnings.append("No group column was selected.")
        elif group_column not in categorical_columns:
            warnings.append(
                f"`{group_column}` is not detected as a categorical column."
            )

        if value_column is None:
            warnings.append("No value column was selected.")
        elif value_column not in numeric_columns:
            warnings.append(
                f"`{value_column}` is not detected as a numeric column."
            )

        is_valid = (
            validation.is_valid
            and group_column is not None
            and value_column is not None
            and group_column in categorical_columns
            and value_column in numeric_columns
        )

        return SchemaValidationResult(
            is_valid=is_valid,
            valid_columns=validation.valid_columns,
            invalid_columns=validation.invalid_columns,
            warnings=warnings,
        )

    def detect_invalid_column_mentions(
        self,
        question_lower: str,
        profile: dict[str, Any],
    ) -> list[str]:
        """
        Detect column-like words mentioned by the user that do not exist
        in the uploaded dataset schema.

        This is intentionally conservative and mainly targets groupby-style
        code generation requests.
        """

        if not self._contains_any(question_lower, ["group", "groupby", "by"]):
            return []

        available_columns = profile.get("columns", [])

        normalized_question = question_lower

        for column in available_columns:
            column_text = str(column).lower()
            column_text_with_spaces = column_text.replace("_", " ")

            normalized_question = normalized_question.replace(column_text, " ")
            normalized_question = normalized_question.replace(column_text_with_spaces, " ")

        tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", normalized_question)

        stopwords = {
            "write",
            "generate",
            "create",
            "show",
            "give",
            "me",
            "code",
            "pandas",
            "python",
            "sql",
            "query",
            "to",
            "for",
            "the",
            "a",
            "an",
            "by",
            "group",
            "groupby",
            "grouped",
            "sum",
            "total",
            "average",
            "mean",
            "count",
            "sort",
            "sorted",
            "descending",
            "ascending",
            "order",
            "using",
            "with",
            "and",
            "of",
            "from",
            "table",
            "data",
            "dataset",
            "df",
        }

        invalid_candidates = []

        for token in tokens:
            if token in stopwords:
                continue

            if token not in invalid_candidates:
                invalid_candidates.append(token)

        return invalid_candidates

    def _is_sql_request(self, question_lower: str) -> bool:
        return self._contains_any(question_lower, ["sql", "query"])

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _get_numeric_columns(self, profile: dict[str, Any]) -> list[str]:
        dtypes = profile.get("dtypes", {})

        numeric_markers = ["int", "float", "number"]

        return [
            column
            for column, dtype in dtypes.items()
            if any(marker in dtype.lower() for marker in numeric_markers)
        ]

    def _get_categorical_columns(self, profile: dict[str, Any]) -> list[str]:
        dtypes = profile.get("dtypes", {})

        categorical_markers = ["object", "string", "category", "bool"]

        return [
            column
            for column, dtype in dtypes.items()
            if any(marker in dtype.lower() for marker in categorical_markers)
        ]

    def _find_mentioned_columns(
        self,
        question_lower: str,
        columns: list[str],
    ) -> list[str]:
        mentioned = []

        for column in columns:
            column_text = str(column).lower()
            column_text_with_spaces = column_text.replace("_", " ")

            if column_text in question_lower or column_text_with_spaces in question_lower:
                mentioned.append(column)

        return mentioned

    def _select_column(
        self,
        mentioned_columns: list[str],
        candidates: list[str],
    ) -> str | None:
        for column in mentioned_columns:
            if column in candidates:
                return column

        return None

    def _quote_sql_identifier(self, identifier: str) -> str:
        safe_identifier = re.sub(r"[^a-zA-Z0-9_]", "_", identifier)

        return f'"{safe_identifier}"'