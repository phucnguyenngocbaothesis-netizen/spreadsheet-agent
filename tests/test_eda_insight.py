from agents.eda_insight import EDAInsightAgent
import pandas as pd

def make_profile():
    return {
        "shape": {
            "rows": 5,
            "columns": 4,
        },
        "columns": ["product", "region", "revenue", "quantity"],
        "dtypes": {
            "product": "object",
            "region": "object",
            "revenue": "float64",
            "quantity": "int64",
        },
        "missing_values": {
            "product": 0,
            "region": 0,
            "revenue": 1,
            "quantity": 0,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 0.0,
            "revenue": 20.0,
            "quantity": 0.0,
        },
        "duplicate_rows": 1,
        "sample_rows": [],
        "numeric_summary": {
            "revenue": {
                "count": 4,
                "mean": 612.5,
                "median": 400.0,
                "std": 460.0,
                "min": 150.0,
                "max": 1200.0,
            }
        },
        "categorical_summary": {
            "product": {
                "unique_count": 4,
                "top_values": {
                    "Laptop": 2,
                    "Mouse": 1,
                },
            }
        },
    }


def test_eda_insight_generates_result():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    assert result.summary
    assert len(result.insights) > 0


def test_eda_insight_detects_dataset_overview():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    titles = [insight.title for insight in result.insights]

    assert "Dataset overview" in titles


def test_eda_insight_detects_missing_values():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    details = [insight.detail for insight in result.insights]

    assert any("missing values" in detail for detail in details)
    assert any("revenue" in detail for detail in details)


def test_eda_insight_detects_duplicate_rows():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    titles = [insight.title for insight in result.insights]

    assert "Duplicate rows detected" in titles


def test_eda_insight_detects_numeric_summary():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    details = [insight.detail for insight in result.insights]

    assert any("ranges from" in detail for detail in details)
    assert any("1200" in detail for detail in details)


def test_eda_insight_detects_categorical_top_value():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    details = [insight.detail for insight in result.insights]

    assert any("Laptop" in detail for detail in details)

def test_eda_insight_generates_bar_chart_insights():
    chart_data = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    agent = EDAInsightAgent()
    result = agent.generate_chart_insights(
        chart_type="bar",
        chart_data=chart_data,
        x_column="product",
        y_column="revenue",
    )

    details = [insight.detail for insight in result.insights]

    assert any("Laptop" in detail for detail in details)
    assert any("highest" in detail for detail in details)


def test_eda_insight_generates_line_chart_insights():
    chart_data = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            "revenue": [100, 200, 300],
        }
    )

    agent = EDAInsightAgent()
    result = agent.generate_chart_insights(
        chart_type="line",
        chart_data=chart_data,
        x_column="order_date",
        y_column="revenue",
    )

    details = [insight.detail for insight in result.insights]

    assert any("increased" in detail for detail in details)


def test_eda_insight_generates_histogram_insights():
    chart_data = pd.DataFrame(
        {
            "revenue": [1200, 150, 300, 800, 500],
        }
    )

    agent = EDAInsightAgent()
    result = agent.generate_chart_insights(
        chart_type="histogram",
        chart_data=chart_data,
        x_column="revenue",
        y_column=None,
    )

    details = [insight.detail for insight in result.insights]

    assert any("ranges from" in detail for detail in details)
    assert any("mean" in detail for detail in details)


def test_eda_insight_generates_scatter_insights():
    chart_data = pd.DataFrame(
        {
            "quantity": [1, 2, 3, 4],
            "revenue": [100, 200, 300, 400],
        }
    )

    agent = EDAInsightAgent()
    result = agent.generate_chart_insights(
        chart_type="scatter",
        chart_data=chart_data,
        x_column="quantity",
        y_column="revenue",
    )

    details = [insight.detail for insight in result.insights]

    assert any("correlation" in detail for detail in details)

def test_eda_insight_adds_recommendations():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    assert any(insight.recommendation for insight in result.insights)


def test_eda_insight_formats_result_as_markdown():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())
    markdown = agent.format_result_as_markdown(result)

    assert "## EDA Insights" in markdown
    assert "Recommendation" in markdown
    assert "Evidence" in markdown


def test_eda_insight_missing_value_severity_warning():
    agent = EDAInsightAgent()

    result = agent.generate_insights(make_profile())

    missing_insights = [
        insight
        for insight in result.insights
        if "Missing values" in insight.title
    ]

    assert missing_insights
    assert missing_insights[0].severity == "warning"