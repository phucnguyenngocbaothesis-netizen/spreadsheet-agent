from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.fast_router import FastRouterAgent


def run_routing_evaluation(
    input_path: str = "evaluation/data/routing_eval_cases.csv",
    output_path: str = "evaluation/outputs/routing_eval_results.csv",
) -> pd.DataFrame:
    router = FastRouterAgent()

    cases = pd.read_csv(input_path)

    results = []

    for _, row in cases.iterrows():
        user_question = str(row["user_question"])
        expected_route = str(row["expected_route"])

        route_result = router.route(user_question)

        is_correct = route_result.route == expected_route

        results.append(
            {
                "id": row["id"],
                "user_question": user_question,
                "expected_route": expected_route,
                "predicted_route": route_result.route,
                "is_correct": is_correct,
                "confidence": route_result.confidence,
                "matched_keywords": "|".join(route_result.matched_keywords),
                "reason": route_result.reason,
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

    print("Routing Evaluation Summary")
    print("==========================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")

    incorrect_df = results_df[~results_df["is_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect routes found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "user_question",
                "expected_route",
                "predicted_route",
                "matched_keywords",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_routing_evaluation()
    print_summary(results)