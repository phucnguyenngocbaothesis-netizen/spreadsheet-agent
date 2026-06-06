from agents.column_validation_agent import ColumnValidationAgent


def test_column_validation_accepts_existing_column():
    agent = ColumnValidationAgent()

    result = agent.validate_question_columns(
        question="tell me about gross revenue",
        available_columns=["gross_revenue", "region"],
    )

    assert not result.has_missing_columns
    assert "gross_revenue" in result.existing_columns


def test_column_validation_detects_missing_column():
    agent = ColumnValidationAgent()

    result = agent.validate_question_columns(
        question="tell me about profit margin",
        available_columns=["profit", "gross_revenue", "discount_rate"],
    )

    assert result.has_missing_columns
    assert "profit margin" in result.missing_columns


def test_column_validation_suggests_similar_columns():
    agent = ColumnValidationAgent()

    result = agent.validate_question_columns(
        question="tell me about profit margin",
        available_columns=["profit", "gross_revenue", "discount_rate"],
    )

    suggestions = result.suggestions["profit margin"]

    assert "profit" in suggestions


def test_column_validation_formats_missing_column_result():
    agent = ColumnValidationAgent()

    result = agent.validate_question_columns(
        question="draw chart of net income by country",
        available_columns=["gross_revenue", "region", "profit"],
    )

    markdown = agent.format_result_as_markdown(result)

    assert "do not exist" in markdown
    assert "Missing columns" in markdown


def test_column_validation_handles_underscore_matching():
    agent = ColumnValidationAgent()

    result = agent.validate_question_columns(
        question="tell me about discount rate",
        available_columns=["discount_rate", "gross_revenue"],
    )

    assert not result.has_missing_columns
    assert "discount_rate" in result.existing_columns