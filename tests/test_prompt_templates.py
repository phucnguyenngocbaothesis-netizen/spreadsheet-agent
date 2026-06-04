from llm.prompt_templates import PromptTemplates


def test_eda_explanation_prompt_contains_required_parts():
    profile = {
        "shape": {
            "rows": 10,
            "columns": 3,
        }
    }

    prompt = PromptTemplates.eda_explanation_prompt(
        user_question="show missing values",
        deterministic_result="Column revenue has 2 missing values.",
        profile=profile,
    )

    assert "show missing values" in prompt
    assert "Column revenue has 2 missing values" in prompt
    assert "Rows: 10" in prompt
    assert "Do not invent numbers" in prompt


def test_chart_explanation_prompt_contains_required_parts():
    chart_metadata = {
        "chart_type": "bar",
        "x_column": "product",
        "y_column": "revenue",
    }

    prompt = PromptTemplates.chart_explanation_prompt(
        user_question="draw revenue by product",
        chart_metadata=chart_metadata,
        chart_insights_markdown="Laptop has the highest revenue.",
    )

    assert "draw revenue by product" in prompt
    assert "bar" in prompt
    assert "Laptop has the highest revenue" in prompt
    assert "Do not invent values" in prompt