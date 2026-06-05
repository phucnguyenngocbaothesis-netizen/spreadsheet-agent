import pandas as pd

from evaluation.run_routing_eval import summarize_results


def test_routing_eval_summary_all_correct():
    results_df = pd.DataFrame(
        {
            "is_correct": [True, True, True],
        }
    )

    summary = summarize_results(results_df)

    assert summary["total_cases"] == 3
    assert summary["correct_cases"] == 3
    assert summary["incorrect_cases"] == 0
    assert summary["accuracy"] == 1.0


def test_routing_eval_summary_some_incorrect():
    results_df = pd.DataFrame(
        {
            "is_correct": [True, False, True, False],
        }
    )

    summary = summarize_results(results_df)

    assert summary["total_cases"] == 4
    assert summary["correct_cases"] == 2
    assert summary["incorrect_cases"] == 2
    assert summary["accuracy"] == 0.5