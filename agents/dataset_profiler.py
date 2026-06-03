from __future__ import annotations

from typing import Any

import pandas as pd


class DatasetProfilerAgent:
    """
    Week 2 v0.3:
    Create a compact dataset profile after loading and normalization.
    """

    TOP_VALUE_LIMIT = 5
    SAMPLE_ROW_LIMIT = 5

    def profile(self, df: pd.DataFrame) -> dict[str, Any]:
        row_count, column_count = df.shape

        missing_values = df.isna().sum()
        missing_percentage = (
            missing_values / row_count * 100
            if row_count > 0
            else missing_values
        )

        profile = {
            "shape": {
                "rows": int(row_count),
                "columns": int(column_count),
            },
            "columns": list(df.columns),
            "dtypes": {
                column: str(dtype)
                for column, dtype in df.dtypes.items()
            },
            "missing_values": {
                column: int(value)
                for column, value in missing_values.items()
            },
            "missing_percentage": {
                column: round(float(value), 2)
                for column, value in missing_percentage.items()
            },
            "duplicate_rows": int(df.duplicated().sum()),
            "sample_rows": self._get_sample_rows(df),
            "numeric_summary": self._get_numeric_summary(df),
            "categorical_summary": self._get_categorical_summary(df),
        }

        return profile

    def _get_sample_rows(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        sample_df = df.head(self.SAMPLE_ROW_LIMIT).copy()
        sample_df = sample_df.where(pd.notna(sample_df), None)

        records = sample_df.to_dict(orient="records")

        return [
            {
                column: self._serialize_value(value)
                for column, value in row.items()
            }
            for row in records
        ]

    def _get_numeric_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        numeric_df = df.select_dtypes(include=["number"])

        summary: dict[str, Any] = {}

        for column in numeric_df.columns:
            series = numeric_df[column].dropna()

            if series.empty:
                summary[column] = {
                    "count": 0,
                    "mean": None,
                    "median": None,
                    "std": None,
                    "min": None,
                    "max": None,
                }
                continue

            summary[column] = {
                "count": int(series.count()),
                "mean": self._round_or_none(series.mean()),
                "median": self._round_or_none(series.median()),
                "std": self._round_or_none(series.std()),
                "min": self._round_or_none(series.min()),
                "max": self._round_or_none(series.max()),
            }

        return summary

    def _get_categorical_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        categorical_df = df.select_dtypes(include=["object", "string", "category", "bool"])

        summary: dict[str, Any] = {}

        for column in categorical_df.columns:
            series = categorical_df[column].dropna()

            value_counts = series.value_counts().head(self.TOP_VALUE_LIMIT)

            summary[column] = {
                "unique_count": int(series.nunique()),
                "top_values": {
                    str(index): int(value)
                    for index, value in value_counts.items()
                },
            }

        return summary

    def _round_or_none(self, value: Any) -> float | None:
        if pd.isna(value):
            return None

        return round(float(value), 4)

    def _serialize_value(self, value: Any) -> Any:
        if pd.isna(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        if hasattr(value, "item"):
            return value.item()

        return value