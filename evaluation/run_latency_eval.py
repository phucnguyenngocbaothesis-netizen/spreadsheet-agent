from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.fast_router import FastRouterAgent
from agents.prompt_quality_agent import PromptQualityAgent
from agents.column_validation_agent import ColumnValidationAgent


def make_eval_profile() -> dict:
    return {
        "shape": {"rows": 50, "columns": 6},
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


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def run_latency_evaluation(
    input_path: str = "evaluation/data/latency_eval_cases.csv",
    output_path: str = "evaluation/outputs/latency_eval_results.csv",
) -> pd.DataFrame:
    cases = pd.read_csv(input_path)

    prompt_quality_agent = PromptQualityAgent()
    column_validation_agent = ColumnValidationAgent()
    router = FastRouterAgent()
    profile = make_eval_profile()

    results = []

    for _, row in cases.iterrows():
        user_question = str(row["user_question"])
        expected_route = str(row["expected_route"])
        llm_expected = parse_bool(row["llm_expected"])

        start_time = time.perf_counter()

        prompt_quality_result = prompt_quality_agent.evaluate(user_question)

        route = "PROMPT_REJECTED"
        llm_used = False
        rejected_by_column_validation = False

        if prompt_quality_result.is_acceptable:
            route_result = router.route(user_question, profile)
            route = route_result.route

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
                    route = "COLUMN_VALIDATION_REJECTED"
                    rejected_by_column_validation = True

            if route_result.route == "UNKNOWN":
                # This evaluation does not call the real LLM.
                # It only marks that an LLM fallback would be needed.
                llm_used = True

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 4)

        results.append(
            {
                "id": row["id"],
                "user_question": user_question,
                "expected_route": expected_route,
                "predicted_route": route,
                "route_correct": route == expected_route or llm_expected,
                "llm_expected": llm_expected,
                "llm_used": llm_used,
                "llm_call_avoided": not llm_used,
                "rejected_by_column_validation": rejected_by_column_validation,
                "latency_ms": latency_ms,
            }
        )

    results_df = pd.DataFrame(results)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_file, index=False)

    return results_df


def summarize_results(results_df: pd.DataFrame) -> dict[str, float | int]:
    total_cases = len(results_df)
    correct_cases = int(results_df["route_correct"].sum())
    llm_used_cases = int(results_df["llm_used"].sum())
    llm_avoided_cases = int(results_df["llm_call_avoided"].sum())

    accuracy = correct_cases / total_cases if total_cases > 0 else 0.0
    llm_avoidance_rate = llm_avoided_cases / total_cases if total_cases > 0 else 0.0
    avg_latency_ms = float(results_df["latency_ms"].mean()) if total_cases > 0 else 0.0

    return {
        "total_cases": total_cases,
        "correct_cases": correct_cases,
        "incorrect_cases": total_cases - correct_cases,
        "accuracy": round(accuracy, 4),
        "llm_used_cases": llm_used_cases,
        "llm_avoided_cases": llm_avoided_cases,
        "llm_avoidance_rate": round(llm_avoidance_rate, 4),
        "avg_latency_ms": round(avg_latency_ms, 4),
    }


def print_summary(results_df: pd.DataFrame) -> None:
    summary = summarize_results(results_df)

    print("Latency and LLM Call Reduction Evaluation Summary")
    print("================================================")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Correct cases: {summary['correct_cases']}")
    print(f"Incorrect cases: {summary['incorrect_cases']}")
    print(f"Accuracy: {summary['accuracy']}")
    print(f"LLM used cases: {summary['llm_used_cases']}")
    print(f"LLM avoided cases: {summary['llm_avoided_cases']}")
    print(f"LLM avoidance rate: {summary['llm_avoidance_rate']}")
    print(f"Average latency ms: {summary['avg_latency_ms']}")

    incorrect_df = results_df[~results_df["route_correct"]]

    if incorrect_df.empty:
        print("\nNo incorrect latency evaluation cases found.")
        return

    print("\nIncorrect cases:")
    print(
        incorrect_df[
            [
                "id",
                "user_question",
                "expected_route",
                "predicted_route",
                "latency_ms",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    results = run_latency_evaluation()
    print_summary(results)