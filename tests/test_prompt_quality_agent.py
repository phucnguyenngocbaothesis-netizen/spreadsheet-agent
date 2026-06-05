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

def test_prompt_quality_loads_custom_json_config(tmp_path):
    config_path = tmp_path / "prompt_quality_patterns.json"
    config_path.write_text(
        """
{
  "vague_prompts": ["custom vague"],
  "unsupported_patterns": ["custom unsupported"],
  "intent_keywords": {
    "DIRECT_ANALYSIS": ["custom missing"]
  },
  "default_suggestions": ["custom suggestion"],
  "unsupported_suggestions": ["custom unsupported suggestion"]
}
""",
        encoding="utf-8",
    )

    agent = PromptQualityAgent(config_path=str(config_path))

    vague_result = agent.evaluate("custom vague")
    unsupported_result = agent.evaluate("custom unsupported")
    acceptable_result = agent.evaluate("custom missing")

    assert not vague_result.is_acceptable
    assert vague_result.issue_type == "vague_prompt"
    assert vague_result.suggested_prompts == ["custom suggestion"]

    assert not unsupported_result.is_acceptable
    assert unsupported_result.issue_type == "unsupported_request"
    assert unsupported_result.suggested_prompts == ["custom unsupported suggestion"]

    assert acceptable_result.is_acceptable
    assert acceptable_result.detected_intents == ["DIRECT_ANALYSIS"]


def test_prompt_quality_falls_back_when_config_missing():
    agent = PromptQualityAgent(config_path="missing_config.json")

    result = agent.evaluate("help me")

    assert not result.is_acceptable
    assert result.issue_type == "vague_prompt"