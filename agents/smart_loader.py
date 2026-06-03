from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class LoadedDataset:
    dataframe: pd.DataFrame
    metadata: dict[str, Any]


class SmartLoaderAgent:
    """
    Week 1 v0.2:
    - Load CSV files
    - Load XLSX/XLS files
    - Support single-sheet Excel only
    - Detect likely header row
    - Remove fully empty rows and columns
    - Clean column names
    - Apply basic type restoration for numeric columns
    """

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
    MAX_HEADER_SCAN_ROWS = 25

    def load(self, uploaded_file) -> LoadedDataset:
        file_name = uploaded_file.name
        extension = self._get_extension(file_name)

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                "Please upload a CSV or Excel file."
            )

        if extension == ".csv":
            raw_df = self._read_csv_raw(uploaded_file)
            sheet_name = None
        else:
            raw_df, sheet_name = self._read_excel_raw(uploaded_file)

        original_shape = raw_df.shape

        header_row_index = self._detect_header_row(raw_df)
        df = self._build_dataframe_from_header(raw_df, header_row_index)

        metadata = {
            "file_name": file_name,
            "file_type": extension,
            "sheet_name": sheet_name,
            "original_shape": original_shape,
            "cleaned_shape": df.shape,
            "detected_header_row": int(header_row_index),
        }

        return LoadedDataset(dataframe=df, metadata=metadata)

    def _get_extension(self, file_name: str) -> str:
        dot_index = file_name.rfind(".")
        if dot_index == -1:
            return ""
        return file_name[dot_index:].lower()

    def _read_csv_raw(self, uploaded_file) -> pd.DataFrame:
        uploaded_file.seek(0)

        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
        else:
            content = uploaded_file.read()

        if isinstance(content, str):
            text = content
        else:
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1")

        delimiter = self._detect_csv_delimiter(text)
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))

        if not rows:
            raise ValueError("The uploaded CSV file is empty.")

        max_columns = max(len(row) for row in rows)
        padded_rows = [
            row + [""] * (max_columns - len(row))
            for row in rows
        ]

        raw_df = pd.DataFrame(padded_rows)
        raw_df = raw_df.replace("", pd.NA)

        return raw_df

    def _detect_csv_delimiter(self, text: str) -> str:
        sample = text[:4096]

        try:
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
        except csv.Error:
            return ","

    def _read_excel_raw(self, uploaded_file) -> tuple[pd.DataFrame, str]:
        uploaded_file.seek(0)

        excel_file = pd.ExcelFile(uploaded_file)
        sheet_name = excel_file.sheet_names[0]

        uploaded_file.seek(0)
        raw_df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name,
            header=None,
        )

        return raw_df, sheet_name

    def _detect_header_row(self, raw_df: pd.DataFrame) -> int:
        if raw_df.empty:
            raise ValueError("The uploaded file does not contain any readable data.")

        best_index = 0
        best_score = float("-inf")

        scan_limit = min(len(raw_df), self.MAX_HEADER_SCAN_ROWS)

        for row_index in range(scan_limit):
            row = raw_df.iloc[row_index]
            score = self._score_header_candidate(row)

            if score > best_score:
                best_score = score
                best_index = row_index

        return best_index

    def _score_header_candidate(self, row: pd.Series) -> float:
        values = [
            value
            for value in row.tolist()
            if not self._is_empty(value)
        ]

        if len(values) < 2:
            return float("-inf")

        text_values = [str(value).strip() for value in values]
        unique_values = set(value.lower() for value in text_values)

        text_count = sum(
            1 for value in text_values
            if self._looks_like_text(value)
        )

        numeric_count = sum(
            1 for value in text_values
            if self._looks_like_number(value)
        )

        empty_count = len(row) - len(values)
        unique_ratio = len(unique_values) / len(text_values)

        score = 0.0
        score += len(values) * 2.0
        score += text_count * 1.5
        score += unique_ratio * 2.0
        score -= numeric_count * 1.0
        score -= empty_count * 0.1

        if unique_ratio < 0.7:
            score -= 2.0

        return score

    def _build_dataframe_from_header(
        self,
        raw_df: pd.DataFrame,
        header_row_index: int,
    ) -> pd.DataFrame:
        raw_columns = raw_df.iloc[header_row_index].tolist()
        columns = self._clean_column_names(raw_columns)

        df = raw_df.iloc[header_row_index + 1:].copy()
        df = df.iloc[:, :len(columns)]
        df.columns = columns

        df = self._basic_cleanup(df)
        df = self._restore_basic_numeric_types(df)

        return df

    def _clean_column_names(self, raw_columns: list[Any]) -> list[str]:
        cleaned_columns = []
        seen_counts: dict[str, int] = {}

        for index, column in enumerate(raw_columns):
            if self._is_empty(column):
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

    def _basic_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")
        df = df.reset_index(drop=True)
        return df

    def _restore_basic_numeric_types(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()

        for column in result.columns:
            series = result[column]

            if series.empty:
                continue

            numeric_series = pd.to_numeric(
                series.astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )

            non_missing_mask = series.notna()
            non_missing_count = int(non_missing_mask.sum())

            if non_missing_count == 0:
                continue

            successful_numeric_count = int(numeric_series[non_missing_mask].notna().sum())
            success_ratio = successful_numeric_count / non_missing_count

            if success_ratio >= 0.9:
                result[column] = numeric_series

        return result

    def _is_empty(self, value: Any) -> bool:
        if pd.isna(value):
            return True

        return str(value).strip() == ""

    def _looks_like_text(self, value: str) -> bool:
        return any(character.isalpha() for character in value)

    def _looks_like_number(self, value: str) -> bool:
        cleaned = value.strip()
        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace("%", "")

        try:
            float(cleaned)
            return True
        except ValueError:
            return False