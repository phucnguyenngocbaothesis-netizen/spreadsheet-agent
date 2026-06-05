from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from evaluation.run_chart_eval import (
    run_chart_evaluation,
    summarize_results as summarize_chart_results,
)
from evaluation.run_codegen_eval import (
    run_codegen_evaluation,
    summarize_results as summarize_codegen_results,
)
from evaluation.run_normalization_eval import (
    run_normalization_evaluation,
    summarize_results as summarize_normalization_results,
)
from evaluation.run_routing_eval import (
    run_routing_evaluation,
    summarize_results as summarize_routing_results,
)


def run_single_evaluation(
    evaluation_name: str,
    run_function: Callable[[], pd.DataFrame],
    summarize_function: Callable[[pd.DataFrame], dict[str, float | int]],
) -> dict[str, float | int | str]:
    results_df = run_function()
    summary = summarize_function(results_df)

    return {
        "evaluation_name": evaluation_name,
        "total_cases": summary["total_cases"],
        "correct_cases": summary["correct_cases"],
        "incorrect_cases": summary["incorrect_cases"],
        "accuracy": summary["accuracy"],
    }


def run_all_evaluations(
    output_path: str = "evaluation/outputs/evaluation_summary.csv",
) -> pd.DataFrame:
    summaries = [
        run_single_evaluation(
            evaluation_name="routing",
            run_function=run_routing_evaluation,
            summarize_function=summarize_routing_results,
        ),
        run_single_evaluation(
            evaluation_name="normalization",
            run_function=run_normalization_evaluation,
            summarize_function=summarize_normalization_results,
        ),
        run_single_evaluation(
            evaluation_name="chart_recommendation",
            run_function=run_chart_evaluation,
            summarize_function=summarize_chart_results,
        ),
        run_single_evaluation(
            evaluation_name="codegen_validation",
            run_function=run_codegen_evaluation,
            summarize_function=summarize_codegen_results,
        ),
    ]

    summary_df = pd.DataFrame(summaries)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_file, index=False)

    return summary_df


def calculate_overall_summary(summary_df: pd.DataFrame) -> dict[str, float | int]:
    total_cases = int(summary_df["total_cases"].sum())
    correct_cases = int(summary_df["correct_cases"].sum())
    incorrect_cases = int(summary_df["incorrect_cases"].sum())

    overall_accuracy = correct_cases / total_cases if total_cases > 0 else 0.0

    return {
        "total_cases": total_cases,
        "correct_cases": correct_cases,
        "incorrect_cases": incorrect_cases,
        "overall_accuracy": round(overall_accuracy, 4),
    }


def print_summary(summary_df: pd.DataFrame) -> None:
    print("Evaluation Summary")
    print("==================")
    print(summary_df.to_string(index=False))

    overall_summary = calculate_overall_summary(summary_df)

    print("\nOverall")
    print("=======")
    print(f"Total cases: {overall_summary['total_cases']}")
    print(f"Correct cases: {overall_summary['correct_cases']}")
    print(f"Incorrect cases: {overall_summary['incorrect_cases']}")
    print(f"Overall accuracy: {overall_summary['overall_accuracy']}")


if __name__ == "__main__":
    summary = run_all_evaluations()
    print_summary(summary)