import pandas as pd

from evaluation.run_normalization_eval import (
    detect_result_type,
    find_column_conversion,
    parse_values,
    summarize_results,
)


def test_normalization_eval_parse_values():
    values = parse_values("1200||300")

    assert values == ["1200", None, "300"]


def test_normalization_eval_detects_numeric_type():
    series = pd.Series([1, 2, 3])

    assert detect_result_type(series) == "numeric"


def test_normalization_eval_detects_datetime_type():
    series = pd.to_datetime(
        pd.Series(["2026-01-01", "2026-01-02"])
    )

    assert detect_result_type(series) == "datetime"


def test_normalization_eval_finds_column_conversion():
    report = {
        "conversions": [
            {
                "column": "revenue",
                "conversion": "numeric_string_to_number",
            }
        ]
    }

    conversion = find_column_conversion(report, "revenue")

    assert conversion == "numeric_string_to_number"


def test_normalization_eval_summary():
    results_df = pd.DataFrame(
        {
            "is_correct": [True, True, False, True],
        }
    )

    summary = summarize_results(results_df)

    assert summary["total_cases"] == 4
    assert summary["correct_cases"] == 3
    assert summary["incorrect_cases"] == 1
    assert summary["accuracy"] == 0.75