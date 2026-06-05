import pandas as pd

from evaluation.run_codegen_eval import (
    make_eval_profile,
    normalize_optional_value,
    summarize_results,
)


def test_codegen_eval_make_profile():
    profile = make_eval_profile()

    assert "columns" in profile
    assert "revenue" in profile["columns"]
    assert profile["dtypes"]["revenue"] == "float64"


def test_codegen_eval_normalize_optional_value_blank():
    result = normalize_optional_value("")

    assert result is None


def test_codegen_eval_normalize_optional_value_text():
    result = normalize_optional_value("GROUP BY")

    assert result == "GROUP BY"


def test_codegen_eval_summary():
    results_df = pd.DataFrame(
        {
            "is_correct": [True, False, True, True],
        }
    )

    summary = summarize_results(results_df)

    assert summary["total_cases"] == 4
    assert summary["correct_cases"] == 3
    assert summary["incorrect_cases"] == 1
    assert summary["accuracy"] == 0.75