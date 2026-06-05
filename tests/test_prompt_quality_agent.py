from agents.prompt_quality_agent import PromptQualityAgent


def test_prompt_quality_accepts_clear_direct_analysis_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate("show missing values")

    assert result.is_acceptable
    assert result.issue_type is None


def test_prompt_quality_rejects_empty_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate("")

    assert not result.is_acceptable
    assert result.issue_type == "empty_prompt"


def test_prompt_quality_rejects_vague_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate("help me")

    assert not result.is_acceptable
    assert result.issue_type == "vague_prompt"
    assert result.suggested_prompts


def test_prompt_quality_detects_multi_intent_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate(
        "show missing values and draw bar chart of revenue by region"
    )

    assert not result.is_acceptable
    assert result.issue_type == "multi_intent_prompt"
    assert "DIRECT_ANALYSIS" in result.detected_intents
    assert "VISUALIZATION" in result.detected_intents


def test_prompt_quality_detects_unsupported_model_training():
    agent = PromptQualityAgent()

    result = agent.evaluate("train a model to predict revenue")

    assert not result.is_acceptable
    assert result.issue_type == "unsupported_request"


def test_prompt_quality_formats_bad_prompt_as_markdown():
    agent = PromptQualityAgent()

    result = agent.evaluate("help me")
    markdown = agent.format_result_as_markdown(result)

    assert "could not process" in markdown
    assert "Try one of these prompts" in markdown


def test_prompt_quality_accepts_vietnamese_missing_values_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate("cho mình xem giá trị thiếu")

    assert result.is_acceptable


def test_prompt_quality_detects_vietnamese_multi_intent_prompt():
    agent = PromptQualityAgent()

    result = agent.evaluate("cho mình xem giá trị thiếu và vẽ biểu đồ doanh thu")

    assert not result.is_acceptable
    assert result.issue_type == "multi_intent_prompt"