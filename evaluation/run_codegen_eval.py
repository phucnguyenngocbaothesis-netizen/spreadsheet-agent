from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.codegen_sql import CodegenSQLAgent


def make_eval_profile() -> dict[str, Any]:
    return {
        "shape": {
            "rows": 5,
            "columns": 4,
        },
        "columns": ["product", "region", "revenue", "quantity"],
        "dtypes": {
            "product": "object",
            "region": "object",
            "revenue": "float64",
            "quantity": "int64",
        },
        "missing_values": {
            "product": 0,
            "region": 0,
            "revenue": 1,
            "quantity": 0,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 0.0,
            "revenue": 20.0,
            "quantity": 0.0,
        },
        "duplicate_rows": 1,
        "sample_rows": [],
        "numeric_summary": {},
        "categorical_summary": {},
    }


def normalize_optional_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text == "":
        return None

    return text


def run_codegen_evaluation(
    input_path: str = "evaluation/data/codegen_eval_cases.csv",
    output_path: str = "evaluation/outputs/codegen_eval_results.csv",
) -> pd.DataFrame:
    cases = pd.read_csv(input_path)
    agent = CodegenSQLAgent()
    profile = make_eval_profile()

    results = []

    for _, row in cases.iterrows():
        user_question = str(row["user_question"])

        expected_mode = str(row["expected_mode"])
        expected_code_type = str(row["expected_code_type"])
        expected_contains = normalize_optional_value(row["expected_contains"])
        expected_warning_contains = normalize_optional_value(
            row["expected_warning_contains"]
        )

        result = agent.generate(user_question, profile)

        warning_text = " | ".join(result.warnings)

        mode_correct = result.mode == expected_mode
        code_type_correct = result.generated_code_type == expected_code_type

        contains_correct = (
            expected_contains is None
            or expected_contains in result.code
        )

        warning_correct = (
            expected_warning_contains is None
            or expected_warning_contains in warning_text
        )

        is_correct = (
            mode_correct
            and code_type_correct
            and contains_correct
            and warning_correct
        )

        results.append(
            {
                "id": row["id"],
                "user_question": user_question,
                "expected_mode": expected_mode,
                "predicted_mode": result.mode,
                "mode_correct": mode_correct,
                "expected_code_type": expected_code_type,
                "predicted_code_type": result.generated_code_type,
                "code_type_correct": code_type_correct,
                "expected_contains": expected_contains,
                "contains_correct": contains_correct,
                "expected_warning_contains": expected_warning_contains,
                "warning_text": warning_text,
                "warning_correct": warning_correct,
                "is_correct": is_correct,
                "code": result.code,
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

    print("Codegen Evaluation Summary")
    print("==========================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")

    incorrect_df = results_df[~results_df["is_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect codegen cases found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "user_question",
                "expected_mode",
                "predicted_mode",
                "expected_code_type",
                "predicted_code_type",
                "expected_contains",
                "contains_correct",
                "expected_warning_contains",
                "warning_correct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_codegen_evaluation()
    print_summary(results)