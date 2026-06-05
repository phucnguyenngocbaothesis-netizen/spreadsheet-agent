from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.generic_normalizer import GenericNormalizerAgent


def parse_values(value_string: str) -> list[Any]:
    values = str(value_string).split("|")

    return [
        None if value == "" else value
        for value in values
    ]


def detect_result_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    return "text"


def find_column_conversion(
    normalization_report: dict[str, Any],
    column_name: str,
) -> str:
    conversions = normalization_report.get("conversions", [])

    for conversion in conversions:
        if conversion.get("column") == column_name:
            return str(conversion.get("conversion"))

    return "unchanged"


def run_normalization_evaluation(
    input_path: str = "evaluation/data/normalization_eval_cases.csv",
    output_path: str = "evaluation/outputs/normalization_eval_results.csv",
) -> pd.DataFrame:
    cases = pd.read_csv(input_path)
    normalizer = GenericNormalizerAgent()

    results = []

    for _, row in cases.iterrows():
        column_name = str(row["column_name"])
        values = parse_values(str(row["input_values"]))

        df = pd.DataFrame({column_name: values})

        normalized_dataset = normalizer.normalize(df)
        normalized_df = normalized_dataset.dataframe
        report = normalized_dataset.report

        result_type = detect_result_type(normalized_df[column_name])
        result_conversion = find_column_conversion(report, column_name)

        expected_type = str(row["expected_type"])
        expected_conversion = str(row["expected_conversion"])

        type_correct = result_type == expected_type
        conversion_correct = result_conversion == expected_conversion
        is_correct = type_correct and conversion_correct

        results.append(
            {
                "id": row["id"],
                "case_name": row["case_name"],
                "column_name": column_name,
                "expected_type": expected_type,
                "result_type": result_type,
                "type_correct": type_correct,
                "expected_conversion": expected_conversion,
                "result_conversion": result_conversion,
                "conversion_correct": conversion_correct,
                "is_correct": is_correct,
            }
        )

    results_df = pd.DataFrame(results)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_file, index=False)

    return results_df


def summarize_results(results_df: pd.DataFrame) -> dict[str, float | int]:
    total_cases = len(results_df)
    correct_cases = int(results_df["is_correct"].sum())
    incorrect_cases = total_cases - correct_cases
    accuracy = correct_cases / total_cases if total_cases > 0 else 0.0

    return {
        "total_cases": total_cases,
        "correct_cases": correct_cases,
        "incorrect_cases": incorrect_cases,
        "accuracy": round(accuracy, 4),
    }


def print_summary(results_df: pd.DataFrame) -> None:
    summary = summarize_results(results_df)

    print("Normalization Evaluation Summary")
    print("===============================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")

    incorrect_df = results_df[~results_df["is_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect normalization cases found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "case_name",
                "column_name",
                "expected_type",
                "result_type",
                "expected_conversion",
                "result_conversion",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_normalization_evaluation()
    print_summary(results)