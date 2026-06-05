import pandas as pd

from evaluation.run_chart_eval import (
    create_dummy_dataframe,
    normalize_optional_value,
    parse_pipe_list,
    summarize_results,
)


def test_chart_eval_parse_pipe_list():
    result = parse_pipe_list("product|revenue|region")

    assert result == ["product", "revenue", "region"]


def test_chart_eval_normalize_optional_value_blank():
    result = normalize_optional_value("")

    assert result is None


def test_chart_eval_create_dummy_dataframe():
    df = create_dummy_dataframe(
        columns=["product", "revenue", "order_date"],
        dtypes=["object", "float64", "datetime64[ns]"],
    )

    assert list(df.columns) == ["product", "revenue", "order_date"]
    assert pd.api.types.is_object_dtype(df["product"])
    assert pd.api.types.is_float_dtype(df["revenue"])
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])


def test_chart_eval_summary():
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