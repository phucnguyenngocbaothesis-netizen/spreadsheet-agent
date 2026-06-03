from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class NormalizedDataset:
    dataframe: pd.DataFrame
    report: dict[str, Any]


class GenericNormalizerAgent:
    """
    Week 2 v0.1:
    - Standardize column names
    - Replace empty strings with missing values
    - Remove fully empty rows and columns
    - Convert percentage strings to decimal numbers
    - Convert numeric strings to numeric dtype
    - Convert date-like strings to datetime dtype
    - Keep categorical/text columns as object/string
    """

    NUMERIC_SUCCESS_THRESHOLD = 0.85
    PERCENTAGE_SUCCESS_THRESHOLD = 0.85
    DATETIME_SUCCESS_THRESHOLD = 0.80

    def normalize(self, df: pd.DataFrame) -> NormalizedDataset:
        result = df.copy()

        original_shape = result.shape
        original_dtypes = {
            column: str(dtype)
            for column, dtype in result.dtypes.items()
        }

        result.columns = self._clean_column_names(list(result.columns))
        result = self._replace_empty_strings(result)
        result = self._remove_empty_rows_and_columns(result)

        conversions = []

        for column in result.columns:
            original_dtype = str(result[column].dtype)

            converted_series, conversion_type, success_ratio = self._convert_series(result[column])

            if conversion_type != "unchanged":
                result[column] = converted_series
                conversions.append(
                    {
                        "column": column,
                        "original_dtype": original_dtype,
                        "new_dtype": str(result[column].dtype),
                        "conversion": conversion_type,
                        "success_ratio": round(success_ratio, 3),
                    }
                )

        report = {
            "original_shape": original_shape,
            "normalized_shape": result.shape,
            "original_dtypes": original_dtypes,
            "normalized_dtypes": {
                column: str(dtype)
                for column, dtype in result.dtypes.items()
            },
            "conversions": conversions,
        }

        return NormalizedDataset(dataframe=result, report=report)

    def _clean_column_names(self, columns: list[Any]) -> list[str]:
        cleaned_columns = []
        seen_counts: dict[str, int] = {}

        for index, column in enumerate(columns):
            if pd.isna(column) or str(column).strip() == "":
                cleaned = f"column_{index + 1}"
            else:
                cleaned = str(column).strip().lower()
                cleaned = re.sub(r"\s+", "_", cleaned)
                cleaned = re.sub(r"[^a-zA-Z0-9_]", "", cleaned)
                cleaned = cleaned.strip("_")

                if not cleaned:
                    cleaned = f"column_{index + 1}"

            if cleaned in seen_counts:
                seen_counts[cleaned] += 1
                cleaned = f"{cleaned}_{seen_counts[cleaned]}"
            else:
                seen_counts[cleaned] = 1

            cleaned_columns.append(cleaned)

        return cleaned_columns

    def _replace_empty_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()

        for column in result.columns:
            if result[column].dtype == "object":
                result[column] = result[column].replace(r"^\s*$", pd.NA, regex=True)

        return result

    def _remove_empty_rows_and_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.dropna(axis=0, how="all")
        result = result.dropna(axis=1, how="all")
        result = result.reset_index(drop=True)
        return result

    def _convert_series(self, series: pd.Series) -> tuple[pd.Series, str, float]:
        if series.empty:
            return series, "unchanged", 0.0

        non_missing_count = int(series.notna().sum())

        if non_missing_count == 0:
            return series, "unchanged", 0.0

        if pd.api.types.is_numeric_dtype(series):
            return series, "unchanged", 1.0

        percentage_series, percentage_ratio = self._try_convert_percentage(series)

        if percentage_ratio >= self.PERCENTAGE_SUCCESS_THRESHOLD:
            return percentage_series, "percentage_to_decimal", percentage_ratio

        numeric_series, numeric_ratio = self._try_convert_numeric(series)

        if numeric_ratio >= self.NUMERIC_SUCCESS_THRESHOLD:
            return numeric_series, "numeric_string_to_number", numeric_ratio

        datetime_series, datetime_ratio = self._try_convert_datetime(series)

        if datetime_ratio >= self.DATETIME_SUCCESS_THRESHOLD:
            return datetime_series, "date_string_to_datetime", datetime_ratio

        return series, "unchanged", 0.0

    def _try_convert_percentage(self, series: pd.Series) -> tuple[pd.Series, float]:
        text_series = series.astype("string")

        non_missing_mask = text_series.notna()
        non_missing_count = int(non_missing_mask.sum())

        if non_missing_count == 0:
            return series, 0.0

        contains_percent = text_series[non_missing_mask].str.contains("%", regex=False, na=False)
        percent_count = int(contains_percent.sum())

        if percent_count == 0:
            return series, 0.0

        cleaned = (
            text_series
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        numeric = pd.to_numeric(cleaned, errors="coerce") / 100

        successful_count = int(numeric[non_missing_mask].notna().sum())
        success_ratio = successful_count / non_missing_count

        return numeric, success_ratio

    def _try_convert_numeric(self, series: pd.Series) -> tuple[pd.Series, float]:
        text_series = series.astype("string")

        non_missing_mask = text_series.notna()
        non_missing_count = int(non_missing_mask.sum())

        if non_missing_count == 0:
            return series, 0.0

        cleaned = (
            text_series
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        numeric = pd.to_numeric(cleaned, errors="coerce")

        successful_count = int(numeric[non_missing_mask].notna().sum())
        success_ratio = successful_count / non_missing_count

        return numeric, success_ratio

    def _try_convert_datetime(self, series: pd.Series) -> tuple[pd.Series, float]:
        text_series = series.astype("string")

        non_missing_mask = text_series.notna()
        non_missing_count = int(non_missing_mask.sum())

        if non_missing_count == 0:
            return series, 0.0

        non_missing_values = text_series[non_missing_mask].str.strip()

        date_like_count = int(
            non_missing_values.apply(self._looks_like_date_string).sum()
        )

        date_like_ratio = date_like_count / non_missing_count

        if date_like_ratio < self.DATETIME_SUCCESS_THRESHOLD:
            return series, 0.0

        datetime_series = pd.to_datetime(text_series, errors="coerce")

        successful_count = int(datetime_series[non_missing_mask].notna().sum())
        success_ratio = successful_count / non_missing_count

        return datetime_series, success_ratio
    
    def _looks_like_date_string(self, value: str) -> bool:
        value = str(value).strip()

        date_patterns = [
            r"^\d{4}-\d{1,2}-\d{1,2}$",       # 2026-01-01
            r"^\d{1,2}/\d{1,2}/\d{4}$",       # 01/01/2026
            r"^\d{1,2}-\d{1,2}-\d{4}$",       # 01-01-2026
            r"^\d{4}/\d{1,2}/\d{1,2}$",       # 2026/01/01
        ]

        return any(re.match(pattern, value) for pattern in date_patterns)