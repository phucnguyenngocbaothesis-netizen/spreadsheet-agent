from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.chart_builder import ChartBuilderAgent


def create_dummy_dataframe(columns: list[str], dtypes: list[str]) -> pd.DataFrame:
    data: dict[str, Any] = {}

    for column, dtype in zip(columns, dtypes):
        dtype_lower = dtype.lower()

        if "datetime" in dtype_lower:
            data[column] = pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            )
        elif "int" in dtype_lower:
            data[column] = [1, 2, 3]
        elif "float" in dtype_lower:
            data[column] = [100.0, 200.0, 300.0]
        else:
            data[column] = ["A", "B", "C"]

    return pd.DataFrame(data)


def parse_pipe_list(value: str) -> list[str]:
    return [
        item.strip()
        for item in str(value).split("|")
        if item.strip()
    ]


def normalize_optional_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text == "":
        return None

    return text


def run_chart_evaluation(
    input_path: str = "evaluation/data/chart_eval_cases.csv",
    output_path: str = "evaluation/outputs/chart_eval_results.csv",
) -> pd.DataFrame:
    cases = pd.read_csv(input_path)
    chart_builder = ChartBuilderAgent()

    results = []

    for _, row in cases.iterrows():
        columns = parse_pipe_list(row["columns"])
        dtypes = parse_pipe_list(row["dtypes"])

        df = create_dummy_dataframe(columns, dtypes)

        user_question = str(row["user_question"])

        expected_chart_type = str(row["expected_chart_type"])
        expected_x_column = normalize_optional_value(row["expected_x_column"])
        expected_y_column = normalize_optional_value(row["expected_y_column"])

        recommendation = chart_builder.recommend_chart(user_question, df)

        chart_type_correct = recommendation.chart_type == expected_chart_type
        x_column_correct = recommendation.x_column == expected_x_column
        y_column_correct = recommendation.y_column == expected_y_column

        is_correct = (
            chart_type_correct
            and x_column_correct
            and y_column_correct
        )

        results.append(
            {
                "id": row["id"],
                "user_question": user_question,
                "expected_chart_type": expected_chart_type,
                "predicted_chart_type": recommendation.chart_type,
                "chart_type_correct": chart_type_correct,
                "expected_x_column": expected_x_column,
                "predicted_x_column": recommendation.x_column,
                "x_column_correct": x_column_correct,
                "expected_y_column": expected_y_column,
                "predicted_y_column": recommendation.y_column,
                "y_column_correct": y_column_correct,
                "is_correct": is_correct,
                "reason": recommendation.reason,
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

    print("Chart Recommendation Evaluation Summary")
    print("======================================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")

    incorrect_df = results_df[~results_df["is_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect chart recommendations found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "user_question",
                "expected_chart_type",
                "predicted_chart_type",
                "expected_x_column",
                "predicted_x_column",
                "expected_y_column",
                "predicted_y_column",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_chart_evaluation()
    print_summary(results)