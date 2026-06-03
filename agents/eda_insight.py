from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class Insight:
    title: str
    detail: str
    severity: str
    evidence: dict[str, Any]
    recommendation: str | None = None


@dataclass
class EDAInsightResult:
    summary: str
    insights: list[Insight]


class EDAInsightAgent:
    """
    Week 4:
    Rule-based EDA insight generator.

    This agent does not use an LLM.
    It generates:
    - dataset-level insights from profile
    - chart-grounded insights from chart data
    - formatted markdown summaries
    """

    SEVERITY_ORDER = {
        "critical": 0,
        "warning": 1,
        "info": 2,
    }

    def generate_insights(
        self,
        profile: dict[str, Any],
        max_insights: int = 8,
    ) -> EDAInsightResult:
        insights: list[Insight] = []

        insights.append(self._create_dataset_overview_insight(profile))

        insights.extend(self._create_missing_value_insights(profile))
        insights.extend(self._create_duplicate_row_insights(profile))
        insights.extend(self._create_numeric_summary_insights(profile))
        insights.extend(self._create_categorical_summary_insights(profile))

        insights = self._sort_insights(insights)
        insights = insights[:max_insights]

        summary = (
            f"Generated {len(insights)} rule-based EDA insights from the dataset profile."
        )

        return EDAInsightResult(summary=summary, insights=insights)

    def generate_chart_insights(
        self,
        chart_type: str,
        chart_data: pd.DataFrame,
        x_column: str | None,
        y_column: str | None,
    ) -> EDAInsightResult:
        if chart_data.empty:
            return EDAInsightResult(
                summary="No chart insights generated because the chart data is empty.",
                insights=[],
            )

        if chart_type == "bar":
            insights = self._generate_bar_chart_insights(
                chart_data=chart_data,
                x_column=x_column,
                y_column=y_column,
            )
        elif chart_type == "line":
            insights = self._generate_line_chart_insights(
                chart_data=chart_data,
                x_column=x_column,
                y_column=y_column,
            )
        elif chart_type == "histogram":
            insights = self._generate_histogram_insights(
                chart_data=chart_data,
                x_column=x_column,
            )
        elif chart_type == "scatter":
            insights = self._generate_scatter_insights(
                chart_data=chart_data,
                x_column=x_column,
                y_column=y_column,
            )
        else:
            insights = []

        insights = self._sort_insights(insights)

        return EDAInsightResult(
            summary=f"Generated {len(insights)} chart-grounded insights.",
            insights=insights,
        )

    def format_result_as_markdown(self, result: EDAInsightResult) -> str:
        lines = [f"## EDA Insights", "", result.summary, ""]

        if not result.insights:
            lines.append("No insights were generated.")
            return "\n".join(lines)

        for insight in result.insights:
            lines.append(f"### [{insight.severity.upper()}] {insight.title}")
            lines.append(insight.detail)

            if insight.recommendation:
                lines.append("")
                lines.append(f"**Recommendation:** {insight.recommendation}")

            if insight.evidence:
                lines.append("")
                lines.append("**Evidence:**")
                for key, value in insight.evidence.items():
                    lines.append(f"- `{key}`: {value}")

            lines.append("")

        return "\n".join(lines)

    def _sort_insights(self, insights: list[Insight]) -> list[Insight]:
        return sorted(
            insights,
            key=lambda insight: self.SEVERITY_ORDER.get(insight.severity, 99),
        )

    def _create_dataset_overview_insight(self, profile: dict[str, Any]) -> Insight:
        rows = profile["shape"]["rows"]
        columns = profile["shape"]["columns"]

        return Insight(
            title="Dataset overview",
            detail=f"The dataset contains {rows} rows and {columns} columns.",
            severity="info",
            evidence={
                "rows": rows,
                "columns": columns,
            },
            recommendation="Use this overview to confirm that the uploaded file was loaded correctly.",
        )

    def _create_missing_value_insights(self, profile: dict[str, Any]) -> list[Insight]:
        insights = []

        missing_values = profile.get("missing_values", {})
        missing_percentage = profile.get("missing_percentage", {})

        columns_with_missing = [
            column
            for column, count in missing_values.items()
            if count > 0
        ]

        if not columns_with_missing:
            insights.append(
                Insight(
                    title="No missing values detected",
                    detail="No missing values were found in the dataset profile.",
                    severity="info",
                    evidence={},
                    recommendation="No missing-value action is needed at this stage.",
                )
            )
            return insights

        for column in columns_with_missing:
            count = missing_values[column]
            percentage = missing_percentage[column]
            severity = self._get_missing_value_severity(percentage)

            insights.append(
                Insight(
                    title=f"Missing values in `{column}`",
                    detail=(
                        f"The column `{column}` has {count} missing values "
                        f"({percentage}%)."
                    ),
                    severity=severity,
                    evidence={
                        "column": column,
                        "missing_count": count,
                        "missing_percentage": percentage,
                    },
                    recommendation=(
                        f"Investigate why `{column}` has missing values. "
                        "Depending on the analysis goal, consider imputation, row removal, "
                        "or keeping missingness as a separate signal."
                    ),
                )
            )

        return insights

    def _create_duplicate_row_insights(self, profile: dict[str, Any]) -> list[Insight]:
        duplicate_rows = profile.get("duplicate_rows", 0)
        total_rows = profile.get("shape", {}).get("rows", 0)

        if duplicate_rows == 0:
            return [
                Insight(
                    title="No duplicate rows detected",
                    detail="The dataset profile does not report any duplicate rows.",
                    severity="info",
                    evidence={
                        "duplicate_rows": duplicate_rows,
                    },
                    recommendation="No duplicate-row action is needed at this stage.",
                )
            ]

        duplicate_percentage = (
            round(duplicate_rows / total_rows * 100, 2)
            if total_rows > 0
            else 0.0
        )

        severity = self._get_duplicate_severity(duplicate_percentage)

        return [
            Insight(
                title="Duplicate rows detected",
                detail=(
                    f"The dataset contains {duplicate_rows} duplicate rows "
                    f"({duplicate_percentage}% of rows)."
                ),
                severity=severity,
                evidence={
                    "duplicate_rows": duplicate_rows,
                    "duplicate_percentage": duplicate_percentage,
                },
                recommendation=(
                    "Check whether duplicate rows are valid repeated records or accidental duplicates. "
                    "If accidental, remove them before analysis."
                ),
            )
        ]

    def _create_numeric_summary_insights(self, profile: dict[str, Any]) -> list[Insight]:
        insights = []

        numeric_summary = profile.get("numeric_summary", {})

        for column, stats in numeric_summary.items():
            count = stats.get("count", 0)

            if count == 0:
                continue

            min_value = stats.get("min")
            max_value = stats.get("max")
            mean_value = stats.get("mean")

            insights.append(
                Insight(
                    title=f"Numeric range for `{column}`",
                    detail=(
                        f"The numeric column `{column}` ranges from {min_value} "
                        f"to {max_value}, with a mean of {mean_value}."
                    ),
                    severity="info",
                    evidence={
                        "column": column,
                        "min": min_value,
                        "max": max_value,
                        "mean": mean_value,
                    },
                    recommendation=(
                        f"Review the range of `{column}` to detect possible outliers "
                        "or unrealistic values."
                    ),
                )
            )

        return insights

    def _create_categorical_summary_insights(
        self,
        profile: dict[str, Any],
    ) -> list[Insight]:
        insights = []

        categorical_summary = profile.get("categorical_summary", {})

        for column, summary in categorical_summary.items():
            unique_count = summary.get("unique_count", 0)
            top_values = summary.get("top_values", {})

            if not top_values:
                continue

            top_value, top_count = next(iter(top_values.items()))

            insights.append(
                Insight(
                    title=f"Most common value in `{column}`",
                    detail=(
                        f"The most common value in `{column}` is `{top_value}`, "
                        f"appearing {top_count} times. The column has "
                        f"{unique_count} unique values."
                    ),
                    severity="info",
                    evidence={
                        "column": column,
                        "top_value": top_value,
                        "top_count": top_count,
                        "unique_count": unique_count,
                    },
                    recommendation=(
                        f"Check whether `{top_value}` dominating `{column}` is expected "
                        "or indicates class imbalance."
                    ),
                )
            )

        return insights

    def _generate_bar_chart_insights(
        self,
        chart_data: pd.DataFrame,
        x_column: str | None,
        y_column: str | None,
    ) -> list[Insight]:
        if x_column is None or y_column is None:
            return []

        if x_column not in chart_data.columns or y_column not in chart_data.columns:
            return []

        sorted_data = chart_data.sort_values(y_column, ascending=False)

        top_row = sorted_data.iloc[0]
        bottom_row = sorted_data.iloc[-1]

        top_category = top_row[x_column]
        top_value = top_row[y_column]

        bottom_category = bottom_row[x_column]
        bottom_value = bottom_row[y_column]

        return [
            Insight(
                title=f"Highest `{y_column}` category",
                detail=(
                    f"`{top_category}` has the highest `{y_column}` value "
                    f"with {self._format_number(top_value)}."
                ),
                severity="info",
                evidence={
                    "x_column": x_column,
                    "y_column": y_column,
                    "top_category": str(top_category),
                    "top_value": self._to_python_value(top_value),
                },
                recommendation=(
                    f"Use `{top_category}` as the main reference category when comparing `{y_column}`."
                ),
            ),
            Insight(
                title=f"Lowest `{y_column}` category",
                detail=(
                    f"`{bottom_category}` has the lowest `{y_column}` value "
                    f"with {self._format_number(bottom_value)}."
                ),
                severity="info",
                evidence={
                    "x_column": x_column,
                    "y_column": y_column,
                    "bottom_category": str(bottom_category),
                    "bottom_value": self._to_python_value(bottom_value),
                },
                recommendation=(
                    f"Review why `{bottom_category}` has the lowest `{y_column}` value."
                ),
            ),
        ]

    def _generate_line_chart_insights(
        self,
        chart_data: pd.DataFrame,
        x_column: str | None,
        y_column: str | None,
    ) -> list[Insight]:
        if x_column is None or y_column is None:
            return []

        if x_column not in chart_data.columns or y_column not in chart_data.columns:
            return []

        sorted_data = chart_data.sort_values(x_column)

        if len(sorted_data) < 2:
            return []

        first_value = sorted_data[y_column].iloc[0]
        last_value = sorted_data[y_column].iloc[-1]

        change = last_value - first_value

        if change > 0:
            direction = "increased"
        elif change < 0:
            direction = "decreased"
        else:
            direction = "remained stable"

        return [
            Insight(
                title=f"Trend in `{y_column}`",
                detail=(
                    f"`{y_column}` {direction} from "
                    f"{self._format_number(first_value)} to "
                    f"{self._format_number(last_value)} over `{x_column}`."
                ),
                severity="info",
                evidence={
                    "x_column": x_column,
                    "y_column": y_column,
                    "first_value": self._to_python_value(first_value),
                    "last_value": self._to_python_value(last_value),
                    "change": self._to_python_value(change),
                },
                recommendation=(
                    f"Use this trend as an initial signal, then inspect more time points "
                    f"before making conclusions about `{y_column}`."
                ),
            )
        ]

    def _generate_histogram_insights(
        self,
        chart_data: pd.DataFrame,
        x_column: str | None,
    ) -> list[Insight]:
        if x_column is None:
            return []

        if x_column not in chart_data.columns:
            return []

        series = chart_data[x_column].dropna()

        if series.empty:
            return []

        return [
            Insight(
                title=f"Distribution summary for `{x_column}`",
                detail=(
                    f"`{x_column}` ranges from {self._format_number(series.min())} "
                    f"to {self._format_number(series.max())}, with a mean of "
                    f"{self._format_number(series.mean())}."
                ),
                severity="info",
                evidence={
                    "column": x_column,
                    "min": self._to_python_value(series.min()),
                    "max": self._to_python_value(series.max()),
                    "mean": self._to_python_value(series.mean()),
                },
                recommendation=(
                    f"Inspect the distribution of `{x_column}` for skewness or extreme values."
                ),
            )
        ]

    def _generate_scatter_insights(
        self,
        chart_data: pd.DataFrame,
        x_column: str | None,
        y_column: str | None,
    ) -> list[Insight]:
        if x_column is None or y_column is None:
            return []

        if x_column not in chart_data.columns or y_column not in chart_data.columns:
            return []

        clean_data = chart_data[[x_column, y_column]].dropna()

        if len(clean_data) < 2:
            return []

        correlation = clean_data[x_column].corr(clean_data[y_column])

        if pd.isna(correlation):
            return []

        severity = "info"

        if abs(float(correlation)) >= 0.8:
            severity = "warning"

        return [
            Insight(
                title=f"Relationship between `{x_column}` and `{y_column}`",
                detail=(
                    f"The correlation between `{x_column}` and `{y_column}` "
                    f"is {round(float(correlation), 4)}."
                ),
                severity=severity,
                evidence={
                    "x_column": x_column,
                    "y_column": y_column,
                    "correlation": round(float(correlation), 4),
                },
                recommendation=(
                    "Correlation does not imply causation. Use this as a signal for further analysis."
                ),
            )
        ]

    def _get_missing_value_severity(self, percentage: float) -> str:
        if percentage >= 50:
            return "critical"

        if percentage >= 20:
            return "warning"

        return "info"

    def _get_duplicate_severity(self, duplicate_percentage: float) -> str:
        if duplicate_percentage >= 50:
            return "critical"

        if duplicate_percentage >= 10:
            return "warning"

        return "info"

    def _format_number(self, value: Any) -> str:
        if pd.isna(value):
            return "N/A"

        if isinstance(value, float):
            return str(round(value, 4))

        return str(value)

    def _to_python_value(self, value: Any) -> Any:
        if pd.isna(value):
            return None

        if hasattr(value, "item"):
            return value.item()

        return value