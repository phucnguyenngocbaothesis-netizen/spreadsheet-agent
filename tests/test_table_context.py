import pandas as pd

from agents.table_context_agent import TableContextAgent


def make_df():
    return pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "region": ["HCMC", "Hanoi", "Danang"],
            "gross_revenue": [1200.0, 150.0, 300.0],
            "discount_rate": [0.1, 0.15, 0.2],
            "order_date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
        }
    )


def make_profile():
    return {
        "shape": {
            "rows": 3,
            "columns": 5,
        },
        "columns": [
            "product",
            "region",
            "gross_revenue",
            "discount_rate",
            "order_date",
        ],
        "dtypes": {
            "product": "object",
            "region": "object",
            "gross_revenue": "float64",
            "discount_rate": "float64",
            "order_date": "datetime64[ns]",
        },
        "missing_values": {
            "product": 0,
            "region": 0,
            "gross_revenue": 1,
            "discount_rate": 0,
            "order_date": 0,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 0.0,
            "gross_revenue": 33.33,
            "discount_rate": 0.0,
            "order_date": 0.0,
        },
        "numeric_summary": {
            "gross_revenue": {
                "count": 2,
                "mean": 750.0,
                "median": 750.0,
                "min": 300.0,
                "max": 1200.0,
            },
            "discount_rate": {
                "count": 3,
                "mean": 0.15,
                "median": 0.15,
                "min": 0.1,
                "max": 0.2,
            },
        },
        "categorical_summary": {
            "region": {
                "unique_count": 3,
                "top_values": {
                    "HCMC": 1,
                    "Hanoi": 1,
                    "Danang": 1,
                },
            },
            "product": {
                "unique_count": 3,
                "top_values": {
                    "Laptop": 1,
                    "Mouse": 1,
                    "Keyboard": 1,
                },
            },
        },
    }


def test_table_context_selects_directly_mentioned_column():
    agent = TableContextAgent()

    result = agent.build_context(
        question="tell me about gross revenue",
        df=make_df(),
        profile=make_profile(),
    )

    assert "gross_revenue" in result.selected_columns
    assert result.column_contexts[0].column == "gross_revenue"


def test_table_context_matches_spaces_to_underscore_column():
    agent = TableContextAgent()

    result = agent.build_context(
        question="describe discount rate",
        df=make_df(),
        profile=make_profile(),
    )

    assert "discount_rate" in result.selected_columns


def test_table_context_prioritizes_missing_column():
    agent = TableContextAgent()

    result = agent.build_context(
        question="which column has missing values",
        df=make_df(),
        profile=make_profile(),
    )

    assert "gross_revenue" in result.selected_columns


def test_table_context_creates_sample_rows_for_selected_columns():
    agent = TableContextAgent()

    result = agent.build_context(
        question="tell me about region",
        df=make_df(),
        profile=make_profile(),
        max_sample_rows=2,
    )

    assert result.sample_rows
    assert len(result.sample_rows) == 2
    assert "region" in result.sample_rows[0]


def test_table_context_fallback_when_no_column_is_relevant():
    agent = TableContextAgent()

    result = agent.build_context(
        question="hello there",
        df=make_df(),
        profile=make_profile(),
        max_columns=2,
    )

    assert len(result.selected_columns) == 2
    assert result.warnings


def test_table_context_formats_markdown():
    agent = TableContextAgent()

    result = agent.build_context(
        question="tell me about region",
        df=make_df(),
        profile=make_profile(),
    )

    markdown = agent.format_context_as_markdown(result)

    assert "Query-Aware Table Context" in markdown
    assert "region" in markdown
    assert "Column Context" in markdown