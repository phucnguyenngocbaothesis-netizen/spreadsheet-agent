from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlanStep:
    step_number: int
    title: str
    description: str
    target_agent: str
    expected_output: str


@dataclass
class PlanningResult:
    goal: str
    plan_type: str
    estimated_difficulty: str
    recommended_next_agent: str
    steps: list[PlanStep]
    assumptions: list[str]
    warnings: list[str]

class PlanningAgent:
    """
    Week 6 v0.1:
    Rule-based workflow planner.

    This version does not use an LLM.
    It maps high-level analysis goals to existing agents.
    """

    def create_plan(
        self,
        question: str,
        profile: dict[str, Any],
    ) -> PlanningResult:
        question_lower = question.lower().strip()

        if self._contains_any(question_lower, ["clean", "preprocess", "normalize"]):
            return self._create_cleaning_plan(profile)

        if self._contains_any(question_lower, ["chart", "visualize", "visualization", "plot", "graph"]):
            return self._create_visualization_plan(profile)

        if self._contains_any(question_lower, ["code", "sql", "pandas", "query"]):
            return self._create_codegen_plan(profile)

        return self._create_general_eda_plan(profile)

    def _create_general_eda_plan(self, profile: dict[str, Any]) -> PlanningResult:
        rows = profile.get("shape", {}).get("rows", 0)
        columns = profile.get("shape", {}).get("columns", 0)

        steps = [
            PlanStep(
                step_number=1,
                title="Validate loaded dataset",
                description="Check whether the uploaded file was loaded with the correct rows, columns, and headers.",
                target_agent="DatasetProfilerAgent",
                expected_output="Dataset shape, column names, and data types.",
            ),
            PlanStep(
                step_number=2,
                title="Check data quality",
                description="Inspect missing values and duplicate rows before deeper analysis.",
                target_agent="DirectAnalysisAgent",
                expected_output="Missing value summary and duplicate row count.",
            ),
            PlanStep(
                step_number=3,
                title="Generate EDA insights",
                description="Create rule-based insights from the dataset profile.",
                target_agent="EDAInsightAgent",
                expected_output="Dataset-level insights with severity, recommendation, and evidence.",
            ),
            PlanStep(
                step_number=4,
                title="Create visualizations",
                description="Select suitable charts for numeric, categorical, and datetime columns.",
                target_agent="ChartBuilderAgent",
                expected_output="Bar chart, line chart, scatter plot, or histogram.",
            ),
            PlanStep(
                step_number=5,
                title="Generate reusable analysis code",
                description="Create pandas or SQL templates for repeated analysis.",
                target_agent="CodegenSQLAgent",
                expected_output="Schema-grounded pandas or SQL code.",
            ),
        ]

        return PlanningResult(
            goal="General exploratory data analysis workflow.",
            plan_type="general_eda",
            estimated_difficulty="medium",
            recommended_next_agent="EDAInsightAgent",
            steps=steps,
            assumptions=[
                "The dataset has already been loaded and normalized.",
                f"The current dataset has {rows} rows and {columns} columns.",
                "The workflow uses deterministic Python logic before any LLM-based explanation.",
            ],
            warnings=[],
        )

    def _create_cleaning_plan(self, profile: dict[str, Any]) -> PlanningResult:
        missing_values = profile.get("missing_values", {})
        duplicate_rows = profile.get("duplicate_rows", 0)

        columns_with_missing = [
            column
            for column, count in missing_values.items()
            if count > 0
        ]

        warnings = []

        if columns_with_missing:
            warnings.append(
                f"Columns with missing values detected: {columns_with_missing}"
            )

        if duplicate_rows > 0:
            warnings.append(
                f"Duplicate rows detected: {duplicate_rows}"
            )

        steps = [
            PlanStep(
                step_number=1,
                title="Inspect missing values",
                description="Identify columns with missing values and their missing percentages.",
                target_agent="DirectAnalysisAgent",
                expected_output="Missing value summary.",
            ),
            PlanStep(
                step_number=2,
                title="Inspect duplicate rows",
                description="Check whether duplicate rows are valid repeated observations or accidental duplicates.",
                target_agent="DirectAnalysisAgent",
                expected_output="Duplicate row count.",
            ),
            PlanStep(
                step_number=3,
                title="Review normalized data types",
                description="Confirm numeric, percentage, datetime, and categorical conversions.",
                target_agent="GenericNormalizerAgent",
                expected_output="Normalization report.",
            ),
            PlanStep(
                step_number=4,
                title="Generate cleaning code",
                description="Create pandas code for missing-value handling or duplicate-row handling.",
                target_agent="CodegenSQLAgent",
                expected_output="Pandas cleaning template.",
            ),
        ]

        return PlanningResult(
            goal="Data cleaning and preprocessing workflow.",
            plan_type="cleaning",
            estimated_difficulty="medium",
            recommended_next_agent="DirectAnalysisAgent",
            steps=steps,
            assumptions=[
                "The dataframe has already passed through SmartLoaderAgent.",
                "The GenericNormalizerAgent has already attempted basic type conversion.",
            ],
            warnings=warnings,
        )

    def _create_visualization_plan(self, profile: dict[str, Any]) -> PlanningResult:
        numeric_columns = self._get_numeric_columns(profile)
        categorical_columns = self._get_categorical_columns(profile)
        datetime_columns = self._get_datetime_columns(profile)

        warnings = []

        if not numeric_columns:
            warnings.append("No numeric columns were detected. Visualization options may be limited.")

        steps = [
            PlanStep(
                step_number=1,
                title="Select chart-relevant columns",
                description="Identify categorical, numeric, and datetime columns that can be visualized.",
                target_agent="DatasetProfilerAgent",
                expected_output="Column type summary.",
            ),
            PlanStep(
                step_number=2,
                title="Recommend chart type",
                description="Use rule-based chart recommendation based on selected column types.",
                target_agent="ChartBuilderAgent",
                expected_output="ChartRecommendation with chart type, x column, y column, and reason.",
            ),
            PlanStep(
                step_number=3,
                title="Render chart",
                description="Generate the chart using Python visualization logic.",
                target_agent="ChartBuilderAgent",
                expected_output="Rendered chart and chart data.",
            ),
            PlanStep(
                step_number=4,
                title="Generate chart-grounded insights",
                description="Explain chart data using deterministic insights.",
                target_agent="EDAInsightAgent",
                expected_output="Highest category, trend, distribution summary, or correlation insight.",
            ),
        ]

        return PlanningResult(
            goal="Visualization workflow.",
            plan_type="visualization",
            estimated_difficulty="easy",
            recommended_next_agent="ChartBuilderAgent",
            steps=steps,
            assumptions=[
                f"Numeric columns detected: {numeric_columns}",
                f"Categorical columns detected: {categorical_columns}",
                f"Datetime columns detected: {datetime_columns}",
            ],
            warnings=warnings,
        )

    def _create_codegen_plan(self, profile: dict[str, Any]) -> PlanningResult:
        steps = [
            PlanStep(
                step_number=1,
                title="Inspect available schema",
                description="Read available columns and data types before generating code.",
                target_agent="DatasetProfilerAgent",
                expected_output="Column names and dtypes.",
            ),
            PlanStep(
                step_number=2,
                title="Validate requested columns",
                description="Check whether user-mentioned columns exist in the dataset schema.",
                target_agent="CodegenSQLAgent",
                expected_output="SchemaValidationResult.",
            ),
            PlanStep(
                step_number=3,
                title="Generate code template",
                description="Generate pandas or SQL code from supported rule-based templates.",
                target_agent="CodegenSQLAgent",
                expected_output="CodegenResult with code, explanation, warnings, and assumptions.",
            ),
            PlanStep(
                step_number=4,
                title="Review generated code",
                description="Check warnings and assumptions before running the generated code.",
                target_agent="User",
                expected_output="User-approved code.",
            ),
        ]

        return PlanningResult(
            goal="Schema-grounded code generation workflow.",
            plan_type="codegen_sql",
            estimated_difficulty="medium",
            recommended_next_agent="CodegenSQLAgent",
            steps=steps,
            assumptions=[
                "Generated code uses the normalized dataframe schema.",
                "The dataframe is assumed to be available as `df` for pandas code.",
                "The SQL table is assumed to be named `uploaded_table`.",
            ],
            warnings=[],
        )

    def format_result_as_markdown(self, result: PlanningResult) -> str:
        lines = [
            "## Planning Result",
            "",
            f"**Goal:** {result.goal}",
            f"**Plan type:** {result.plan_type}",
            f"**Estimated difficulty:** {result.estimated_difficulty}",
            f"**Recommended next agent:** {result.recommended_next_agent}",
            "",
        ]

        if result.assumptions:
            lines.append("### Assumptions")
            for assumption in result.assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if result.warnings:
            lines.append("### Warnings")
            for warning in result.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        lines.append("### Workflow Steps")

        for step in result.steps:
            lines.append(f"#### Step {step.step_number}: {step.title}")
            lines.append(step.description)
            lines.append("")
            lines.append(f"- **Target agent:** `{step.target_agent}`")
            lines.append(f"- **Expected output:** {step.expected_output}")
            lines.append("")

        return "\n".join(lines)

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _get_numeric_columns(self, profile: dict[str, Any]) -> list[str]:
        dtypes = profile.get("dtypes", {})
        return [
            column
            for column, dtype in dtypes.items()
            if "int" in dtype.lower() or "float" in dtype.lower()
        ]

    def _get_categorical_columns(self, profile: dict[str, Any]) -> list[str]:
        dtypes = profile.get("dtypes", {})
        return [
            column
            for column, dtype in dtypes.items()
            if any(marker in dtype.lower() for marker in ["object", "string", "category", "bool"])
        ]

    def _get_datetime_columns(self, profile: dict[str, Any]) -> list[str]:
        dtypes = profile.get("dtypes", {})
        return [
            column
            for column, dtype in dtypes.items()
            if "datetime" in dtype.lower()
        ]