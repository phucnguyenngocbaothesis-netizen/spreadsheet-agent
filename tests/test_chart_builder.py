from unittest import result

import matplotlib.figure
import pandas as pd
import pytest

from agents.chart_builder import ChartBuilderAgent


def test_chart_builder_creates_bar_chart():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    result = agent.build_chart("draw bar chart of revenue by product", df)

    assert not result.chart_data.empty
    assert list(result.chart_data.columns) == ["product", "revenue"]
    assert result.chart_type == "bar"
    assert result.x_column == "product"
    assert result.y_column == "revenue"
    assert isinstance(result.figure, matplotlib.figure.Figure)


def test_chart_builder_creates_histogram():
    df = pd.DataFrame(
        {
            "revenue": [1200, 150, 300, 800, 500],
        }
    )

    agent = ChartBuilderAgent()
    result = agent.build_chart("show histogram of revenue", df)

    assert not result.chart_data.empty
    assert list(result.chart_data.columns) == ["revenue"]
    assert result.chart_type == "histogram"
    assert result.x_column == "revenue"
    assert result.y_column is None
    assert isinstance(result.figure, matplotlib.figure.Figure)


def test_chart_builder_creates_line_chart():
    df = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    result = agent.build_chart("show line chart of revenue over order date", df)

    assert not result.chart_data.empty
    assert list(result.chart_data.columns) == ["order_date", "revenue"]
    assert result.chart_type == "line"
    assert result.x_column == "order_date"
    assert result.y_column == "revenue"
    assert isinstance(result.figure, matplotlib.figure.Figure)


def test_chart_builder_creates_scatter_plot():
    df = pd.DataFrame(
        {
            "quantity": [3, 10, 5],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    result = agent.build_chart("show scatter plot of quantity and revenue", df)

    assert not result.chart_data.empty
    assert list(result.chart_data.columns) == ["quantity", "revenue"]
    assert result.chart_type == "scatter"
    assert result.x_column == "quantity"
    assert result.y_column == "revenue"
    assert isinstance(result.figure, matplotlib.figure.Figure)

def test_chart_builder_bar_chart_aggregates_values():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Laptop", "Mouse"],
            "revenue": [1000, 200, 150],
        }
    )

    agent = ChartBuilderAgent()
    result = agent.build_chart("draw bar chart of revenue by product", df)

    laptop_revenue = result.chart_data.loc[
        result.chart_data["product"] == "Laptop",
        "revenue",
    ].iloc[0]

    assert laptop_revenue == 1200

def test_chart_builder_recommends_bar_chart():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    recommendation = agent.recommend_chart("visualize revenue by product", df)

    assert recommendation.chart_type == "bar"
    assert recommendation.x_column == "product"
    assert recommendation.y_column == "revenue"


def test_chart_builder_recommends_histogram():
    df = pd.DataFrame(
        {
            "revenue": [1200, 150, 300, 800, 500],
        }
    )

    agent = ChartBuilderAgent()
    recommendation = agent.recommend_chart("show distribution of revenue", df)

    assert recommendation.chart_type == "histogram"
    assert recommendation.x_column == "revenue"
    assert recommendation.y_column is None


def test_chart_builder_recommends_line_chart():
    df = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    recommendation = agent.recommend_chart("show revenue trend over order date", df)

    assert recommendation.chart_type == "line"
    assert recommendation.x_column == "order_date"
    assert recommendation.y_column == "revenue"


def test_chart_builder_recommends_scatter_plot():
    df = pd.DataFrame(
        {
            "quantity": [3, 10, 5],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()
    recommendation = agent.recommend_chart("show scatter plot of quantity and revenue", df)

    assert recommendation.chart_type == "scatter"
    assert recommendation.x_column == "quantity"
    assert recommendation.y_column == "revenue"

def test_chart_builder_histogram_requires_numeric_column():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
        }
    )

    agent = ChartBuilderAgent()

    with pytest.raises(ValueError, match="numeric column"):
        agent.build_chart("show histogram", df)


def test_chart_builder_scatter_requires_two_numeric_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()

    with pytest.raises(ValueError, match="two numeric columns"):
        agent.build_chart("show scatter plot", df)


def test_chart_builder_line_requires_datetime_and_numeric_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    agent = ChartBuilderAgent()

    with pytest.raises(ValueError, match="datetime column"):
        agent.build_chart("show line chart", df)


def test_chart_builder_bar_requires_categorical_and_numeric_columns():
    df = pd.DataFrame(
        {
            "revenue": [1200, 150, 300],
            "quantity": [3, 10, 5],
        }
    )

    agent = ChartBuilderAgent()

    with pytest.raises(ValueError, match="categorical column"):
        agent.build_chart("draw bar chart", df)

def test_chart_builder_creates_pie_chart():
    df = pd.DataFrame(
        {
            "region": ["HCMC", "Hanoi", "Danang", "HCMC"],
            "gross_revenue": [1000, 500, 250, 700],
        }
    )

    agent = ChartBuilderAgent()

    result = agent.build_chart(
        "draw pie chart of gross revenue by region",
        df,
    )

    assert result.chart_type == "pie"
    assert result.x_column == "region"
    assert result.y_column == "gross_revenue"
    assert result.figure is not None
    assert not result.chart_data.empty