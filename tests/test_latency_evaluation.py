import pandas as pd

from evaluation.run_latency_eval import (
    parse_bool,
    summarize_results,
)


def test_latency_eval_parse_bool_true():
    assert parse_bool("True")


def test_latency_eval_parse_bool_false():
    assert not parse_bool("False")


def test_latency_eval_summary():
    results_df = pd.DataFrame(
        {
            "route_correct": [True, True, False],
            "llm_used": [False, True, False],
            "llm_call_avoided": [True, False, True],
            "latency_ms": [1.0, 2.0, 3.0],
        }
    )

    summary = summarize_results(results_df)

    assert summary["total_cases"] == 3
    assert summary["correct_cases"] == 2
    assert summary["incorrect_cases"] == 1
    assert summary["llm_used_cases"] == 1
    assert summary["llm_avoided_cases"] == 2
    assert summary["llm_avoidance_rate"] == round(2 / 3, 4)
    assert summary["avg_latency_ms"] == 2.0