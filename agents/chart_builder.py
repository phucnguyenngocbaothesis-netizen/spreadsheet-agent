from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class ChartRecommendation:
    chart_type: str
    x_column: str | None
    y_column: str | None
    reason: str


@dataclass
class ChartResult:
    figure: Any
    chart_type: str
    x_column: str | None
    y_column: str | None
    chart_data: pd.DataFrame
    reason: str


class ChartBuilderAgent:
    """
    Week 3:
    Rule-based chart recommendation and chart rendering.

    Supported charts:
        - Bar chart: categorical + numeric
        - Line chart: datetime + numeric
        - Scatter plot: numeric + numeric
        - Histogram: one numeric column
        - Pie chart: categorical + numeric
    """

    def recommend_chart(self, question: str, df: pd.DataFrame) -> ChartRecommendation:
        question_lower = question.lower().strip()

        numeric_columns = list(df.select_dtypes(include=["number"]).columns)
        datetime_columns = list(df.select_dtypes(include=["datetime64"]).columns)
        categorical_columns = list(
            df.select_dtypes(include=["object", "string", "category", "bool"]).columns
        )

        mentioned_columns = self._find_mentioned_columns(question_lower, df.columns)

        mentioned_columns = self._find_mentioned_columns(question_lower, df.columns)

        pie_keywords = [
            "pie",
            "pie chart",
            "share",
            "composition",
            "proportion",
            "percentage share",
            "revenue share",
            "sales share",
            "biểu đồ tròn",
            "tỷ trọng",
            "tỉ trọng",
            "cơ cấu",
        ]

        if any(keyword in question_lower for keyword in pie_keywords):
            x_column = self._select_column(mentioned_columns, categorical_columns)
            y_column = self._select_column(mentioned_columns, numeric_columns)

            if x_column is None:
                x_column = categorical_columns[0] if categorical_columns else None

            if y_column is None:
                y_column = numeric_columns[0] if numeric_columns else None

            if x_column is None or y_column is None:
                raise ValueError("Pie chart requires one categorical column and one numeric column.")

            return ChartRecommendation(
                chart_type="pie",
                x_column=x_column,
                y_column=y_column,
                reason=(
                    "Recommended pie chart because the request asks for share, "
                    "composition, or proportion by category."
                ),
            )

        if "histogram" in question_lower or "distribution" in question_lower:
            numeric_column = self._select_column(mentioned_columns, numeric_columns)

            if numeric_column is None:
                numeric_column = numeric_columns[0] if numeric_columns else None

            if numeric_column is None:
                raise ValueError("No numeric column is available for histogram.")

            return ChartRecommendation(
                chart_type="histogram",
                x_column=numeric_column,
                y_column=None,
                reason="Recommended histogram because the request asks for the distribution of one numeric column.",
            )

        if "scatter" in question_lower:
            selected_numeric = [
                column
                for column in mentioned_columns
                if column in numeric_columns
            ]

            if len(selected_numeric) >= 2:
                x_column, y_column = selected_numeric[:2]
            elif len(numeric_columns) >= 2:
                x_column, y_column = numeric_columns[:2]
            else:
                raise ValueError("At least two numeric columns are required for scatter plot.")

            return ChartRecommendation(
                chart_type="scatter",
                x_column=x_column,
                y_column=y_column,
                reason="Recommended scatter plot because the request uses two numeric columns.",
            )

        if "line" in question_lower or "trend" in question_lower:
            x_column = self._select_column(mentioned_columns, datetime_columns)
            y_column = self._select_column(mentioned_columns, numeric_columns)

            if x_column is None:
                x_column = datetime_columns[0] if datetime_columns else None

            if y_column is None:
                y_column = numeric_columns[0] if numeric_columns else None

            if x_column is None or y_column is None:
                raise ValueError("Line chart requires one datetime column and one numeric column.")

            return ChartRecommendation(
                chart_type="line",
                x_column=x_column,
                y_column=y_column,
                reason="Recommended line chart because the request uses a datetime column and a numeric column.",
            )

        x_column = self._select_column(mentioned_columns, categorical_columns)
        y_column = self._select_column(mentioned_columns, numeric_columns)

        if x_column is None:
            x_column = categorical_columns[0] if categorical_columns else None

        if y_column is None:
            y_column = numeric_columns[0] if numeric_columns else None

        if x_column is None or y_column is None:
            raise ValueError("Bar chart requires one categorical column and one numeric column.")

        return ChartRecommendation(
            chart_type="bar",
            x_column=x_column,
            y_column=y_column,
            reason="Recommended bar chart because the request uses one categorical column and one numeric column.",
        )

    def build_chart(self, question: str, df: pd.DataFrame) -> ChartResult:
        recommendation = self.recommend_chart(question, df)

        if recommendation.chart_type == "histogram":
            if recommendation.x_column is None:
                raise ValueError(
                    "Cannot create a histogram because no numeric column was found. "
                    "Please use a dataset with at least one numeric column."
                )

            return self._build_histogram(
                df=df,
                numeric_column=recommendation.x_column,
                reason=recommendation.reason,
            )

        if recommendation.chart_type == "scatter":
            if recommendation.x_column is None or recommendation.y_column is None:
                raise ValueError(
                    "Cannot create a scatter plot because the required numeric columns were not found. "
                    "Please use a dataset with at least two numeric columns."
                )

            return self._build_scatter(
                df=df,
                x_column=recommendation.x_column,
                y_column=recommendation.y_column,
                reason=recommendation.reason,
            )

        if recommendation.chart_type == "line":
            if recommendation.x_column is None or recommendation.y_column is None:
                raise ValueError(
                    "Cannot create a line chart because the required columns were not found. "
                    "Please use a dataset with a datetime column and a numeric column."
                )

            return self._build_line_chart(
                df=df,
                x_column=recommendation.x_column,
                y_column=recommendation.y_column,
                reason=recommendation.reason,
            )

        if recommendation.chart_type == "pie":
            if recommendation.x_column is None or recommendation.y_column is None:
                raise ValueError(
                    "Cannot create a pie chart because the required columns were not found. "
                    "Please use a dataset with one categorical column and one numeric column."
                )

            return self._build_pie_chart(
                df=df,
                x_column=recommendation.x_column,
                y_column=recommendation.y_column,
                reason=recommendation.reason,
            )

        if recommendation.chart_type == "bar":
            if recommendation.x_column is None or recommendation.y_column is None:
                raise ValueError(
                    "Cannot create a bar chart because the required columns were not found. "
                    "Please use a dataset with a categorical column and a numeric column."
                )

            return self._build_bar_chart(
                df=df,
                x_column=recommendation.x_column,
                y_column=recommendation.y_column,
                reason=recommendation.reason,
            )

        raise ValueError(f"Unsupported chart type: {recommendation.chart_type}")

    def _find_mentioned_columns(
        self,
        question_lower: str,
        columns: pd.Index,
    ) -> list[str]:
        mentioned = []

        for column in columns:
            column_name = str(column)
            column_text = column_name.lower()
            column_text_with_spaces = column_text.replace("_", " ")

            if column_text in question_lower or column_text_with_spaces in question_lower:
                mentioned.append(column_name)

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

    def _build_bar_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        reason: str,
    ) -> ChartResult:
        chart_data = (
            df[[x_column, y_column]]
            .dropna()
            .groupby(x_column, as_index=False)[y_column]
            .sum()
            .sort_values(y_column, ascending=False)
            .head(20)
        )

        figure, axis = plt.subplots()
        axis.bar(chart_data[x_column].astype(str), chart_data[y_column])
        axis.set_xlabel(x_column)
        axis.set_ylabel(y_column)
        axis.set_title(f"{y_column} by {x_column}")
        axis.tick_params(axis="x", rotation=45)
        figure.tight_layout()

        return ChartResult(
            figure=figure,
            chart_type="bar",
            x_column=x_column,
            y_column=y_column,
            chart_data=chart_data,
            reason=reason,
        )

    def _build_pie_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        reason: str,
    ) -> ChartResult:
        chart_data = (
            df[[x_column, y_column]]
            .dropna()
            .groupby(x_column, as_index=False)[y_column]
            .sum()
            .sort_values(y_column, ascending=False)
        )

        # Pie charts cannot represent negative or zero slices meaningfully.
        chart_data = chart_data[chart_data[y_column] > 0]

        if chart_data.empty:
            raise ValueError(
                "Cannot create a pie chart because there are no positive values to plot."
            )

        max_slices = 6

        if len(chart_data) > max_slices:
            top_data = chart_data.head(max_slices - 1)
            other_value = chart_data.iloc[max_slices - 1:][y_column].sum()

            other_row = pd.DataFrame(
                {
                    x_column: ["Other"],
                    y_column: [other_value],
                }
            )

            chart_data = pd.concat([top_data, other_row], ignore_index=True)

        figure, axis = plt.subplots(figsize=(8, 6))

        axis.pie(
            chart_data[y_column],
            labels=chart_data[x_column].astype(str),
            autopct="%1.1f%%",
            startangle=90,
        )

        axis.set_title(f"{y_column} share by {x_column}")
        axis.axis("equal")
        figure.tight_layout()

        return ChartResult(
            figure=figure,
            chart_type="pie",
            x_column=x_column,
            y_column=y_column,
            chart_data=chart_data,
            reason=reason,
        )

    def _build_line_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        reason: str,
    ) -> ChartResult:
        chart_data = (
            df[[x_column, y_column]]
            .dropna()
            .groupby(x_column, as_index=False)[y_column]
            .sum()
            .sort_values(x_column)
        )

        figure, axis = plt.subplots()
        axis.plot(chart_data[x_column], chart_data[y_column], marker="o")
        axis.set_xlabel(x_column)
        axis.set_ylabel(y_column)
        axis.set_title(f"{y_column} over {x_column}")
        axis.tick_params(axis="x", rotation=45)
        figure.tight_layout()

        return ChartResult(
            figure=figure,
            chart_type="line",
            x_column=x_column,
            y_column=y_column,
            chart_data=chart_data,
            reason=reason,
        )

    def _build_scatter(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        reason: str,
    ) -> ChartResult:
        chart_data = df[[x_column, y_column]].dropna()

        figure, axis = plt.subplots()
        axis.scatter(chart_data[x_column], chart_data[y_column])
        axis.set_xlabel(x_column)
        axis.set_ylabel(y_column)
        axis.set_title(f"{y_column} vs {x_column}")
        figure.tight_layout()

        return ChartResult(
            figure=figure,
            chart_type="scatter",
            x_column=x_column,
            y_column=y_column,
            chart_data=chart_data,
            reason=reason,
        )

    def _build_histogram(
        self,
        df: pd.DataFrame,
        numeric_column: str,
        reason: str,
    ) -> ChartResult:
        chart_data = df[[numeric_column]].dropna()

        figure, axis = plt.subplots()
        axis.hist(chart_data[numeric_column], bins=10)
        axis.set_xlabel(numeric_column)
        axis.set_ylabel("Frequency")
        axis.set_title(f"Distribution of {numeric_column}")
        figure.tight_layout()

        return ChartResult(
            figure=figure,
            chart_type="histogram",
            x_column=numeric_column,
            y_column=None,
            chart_data=chart_data,
            reason=reason,
        )