from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.column_validation_agent import ColumnValidationAgent
from agents.fast_router import FastRouterAgent
from agents.prompt_quality_agent import PromptQualityAgent


def make_eval_profile() -> dict:
    return {
        "shape": {
            "rows": 10,
            "columns": 6,
        },
        "columns": [
            "product",
            "region",
            "gross_revenue",
            "discount_rate",
            "order_date",
            "profit",
        ],
        "dtypes": {
            "product": "object",
            "region": "object",
            "gross_revenue": "float64",
            "discount_rate": "float64",
            "order_date": "datetime64[ns]",
            "profit": "float64",
        },
    }


def normalize_optional_value(value) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text == "":
        return None

    return text


def run_prompt_stress_evaluation(
    input_path: str = "evaluation/data/prompt_stress_eval_cases.csv",
    output_path: str = "evaluation/outputs/prompt_stress_eval_results.csv",
) -> pd.DataFrame:
    cases = pd.read_csv(input_path)

    prompt_quality_agent = PromptQualityAgent()
    column_validation_agent = ColumnValidationAgent()
    router = FastRouterAgent()
    profile = make_eval_profile()

    results = []

    for _, row in cases.iterrows():
        user_question = str(row["user_question"])
        expected_behavior = str(row["expected_behavior"])
        expected_route = normalize_optional_value(row["expected_route"])
        expected_issue_type = normalize_optional_value(row["expected_issue_type"])

        prompt_quality_result = prompt_quality_agent.evaluate(user_question)

        predicted_behavior = "ROUTE"
        predicted_route = None
        predicted_issue_type = prompt_quality_result.issue_type

        if not prompt_quality_result.is_acceptable:
            predicted_behavior = "REJECT"
        else:
            route_result = router.route(user_question, profile)
            predicted_route = route_result.route

            column_sensitive_routes = {
                "DIRECT_ANALYSIS",
                "VISUALIZATION",
                "CODEGEN_SQL",
            }

            if (
                route_result.route in column_sensitive_routes
                and column_validation_agent.should_validate_question_columns(
                    question=user_question,
                    route=route_result.route,
                )
            ):
                column_validation_result = column_validation_agent.validate_question_columns(
                    question=user_question,
                    available_columns=profile["columns"],
                )

                if column_validation_result.has_missing_columns:
                    predicted_behavior = "COLUMN_REJECT"
                    predicted_route = None

            if predicted_behavior != "COLUMN_REJECT":
                if route_result.route == "UNKNOWN":
                    predicted_behavior = "ROUTE_OR_UNKNOWN"
                else:
                    predicted_behavior = "ROUTE"

        behavior_correct = (
            predicted_behavior == expected_behavior
            or expected_behavior == "ROUTE_OR_UNKNOWN"
            and predicted_behavior in ["ROUTE", "ROUTE_OR_UNKNOWN"]
        )

        route_correct = (
            expected_route is None
            or predicted_route == expected_route
        )

        issue_type_correct = (
            expected_issue_type is None
            or predicted_issue_type == expected_issue_type
        )

        is_correct = behavior_correct and route_correct and issue_type_correct

        results.append(
            {
                "id": row["id"],
                "user_question": user_question,
                "expected_behavior": expected_behavior,
                "predicted_behavior": predicted_behavior,
                "behavior_correct": behavior_correct,
                "expected_route": expected_route,
                "predicted_route": predicted_route,
                "route_correct": route_correct,
                "expected_issue_type": expected_issue_type,
                "predicted_issue_type": predicted_issue_type,
                "issue_type_correct": issue_type_correct,
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

    print("Prompt Stress Evaluation Summary")
    print("===============================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")

    incorrect_df = results_df[~results_df["is_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect prompt stress cases found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "user_question",
                "expected_behavior",
                "predicted_behavior",
                "expected_route",
                "predicted_route",
                "expected_issue_type",
                "predicted_issue_type",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_prompt_stress_evaluation()
    print_summary(results)