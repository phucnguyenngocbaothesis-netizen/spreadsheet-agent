import pandas as pd

from evaluation.run_all_evaluations import calculate_overall_summary


def test_all_evaluations_calculates_overall_summary():
    summary_df = pd.DataFrame(
        {
            "evaluation_name": ["routing", "normalization"],
            "total_cases": [10, 5],
            "correct_cases": [8, 5],
            "incorrect_cases": [2, 0],
            "accuracy": [0.8, 1.0],
        }
    )

    overall = calculate_overall_summary(summary_df)

    assert overall["total_cases"] == 15
    assert overall["correct_cases"] == 13
    assert overall["incorrect_cases"] == 2
    assert overall["overall_accuracy"] == round(13 / 15, 4)


def test_all_evaluations_handles_empty_summary():
    summary_df = pd.DataFrame(
        {
            "evaluation_name": [],
            "total_cases": [],
            "correct_cases": [],
            "incorrect_cases": [],
            "accuracy": [],
        }
    )

    overall = calculate_overall_summary(summary_df)

    assert overall["total_cases"] == 0
    assert overall["correct_cases"] == 0
    assert overall["incorrect_cases"] == 0
    assert overall["overall_accuracy"] == 0.0