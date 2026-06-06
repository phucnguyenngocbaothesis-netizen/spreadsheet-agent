from agents.llm_explanation_agent import LLMExplanationAgent
from llm.local_llm_client import LLMResponse
import pandas as pd


class FakeUnavailableClient:
    model_name = "fake-model"

    def get_status(self):
        class Status:
            available = False
            message = "Local LLM unavailable."

        return Status()

    def validate_model(self):
        raise AssertionError("validate_model should not be called when server is unavailable.")

    def generate(self, *args, **kwargs):
        raise AssertionError("generate should not be called when server is unavailable.")


class FakeInvalidModelClient:
    model_name = "missing-model"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = False
            message = "Model not found."

        return Validation()

    def generate(self, *args, **kwargs):
        raise AssertionError("generate should not be called when model is invalid.")


class FakeSuccessfulClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=True,
            content="This is a grounded explanation.",
            model=self.model_name,
            provider="local_ollama",
        )


class FakeFailedGenerationClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=False,
            content="",
            model=self.model_name,
            provider="local_ollama",
            error="Generation failed.",
        )


def make_profile():
    return {
        "shape": {
            "rows": 10,
            "columns": 3,
        }
    }


def test_llm_explanation_agent_uses_fallback_when_server_unavailable():
    agent = LLMExplanationAgent(FakeUnavailableClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="No missing values.",
        profile=make_profile(),
    )

    assert not result.success
    assert result.fallback_used
    assert result.source == "deterministic_fallback"


def test_llm_explanation_agent_uses_fallback_when_model_invalid():
    agent = LLMExplanationAgent(FakeInvalidModelClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="No missing values.",
        profile=make_profile(),
    )

    assert not result.success
    assert result.fallback_used
    assert "Model not found" in result.error


def test_llm_explanation_agent_returns_successful_explanation():
    agent = LLMExplanationAgent(FakeSuccessfulClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="No missing values.",
        profile=make_profile(),
    )

    assert result.success
    assert not result.fallback_used
    assert result.source == "local_llm"
    assert "grounded explanation" in result.explanation


def test_llm_explanation_agent_handles_generation_failure():
    agent = LLMExplanationAgent(FakeFailedGenerationClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="No missing values.",
        profile=make_profile(),
    )

    assert not result.success
    assert result.fallback_used
    assert "Generation failed" in result.error


def test_llm_explanation_agent_explains_chart_result():
    agent = LLMExplanationAgent(FakeSuccessfulClient())

    result = agent.explain_chart_result(
        user_question="draw revenue by product",
        chart_metadata={
            "chart_type": "bar",
            "x_column": "product",
            "y_column": "revenue",
        },
        chart_insights_markdown="Laptop has highest revenue.",
    )

    assert result.success
    assert result.prompt_type == "chart_explanation"

class FakeShortResponseClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=True,
            content="Too short.",
            model=self.model_name,
            provider="local_ollama",
        )


class FakeIncompleteResponseClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=True,
            content="The revenue column has one missing value and",
            model=self.model_name,
            provider="local_ollama",
        )


def test_llm_explanation_agent_warns_when_response_too_short():
    agent = LLMExplanationAgent(FakeShortResponseClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="Revenue has 1 missing value.",
        profile=make_profile(),
    )

    assert result.success
    assert any("too short" in warning for warning in result.warnings)


def test_llm_explanation_agent_warns_when_response_incomplete():
    agent = LLMExplanationAgent(FakeIncompleteResponseClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="Revenue has 1 missing value.",
        profile=make_profile(),
    )

    assert result.success
    assert any("incomplete" in warning for warning in result.warnings)

def test_llm_explanation_agent_explains_with_table_context():
    agent = LLMExplanationAgent(FakeSuccessfulClient())
    language="vi",
    df = pd.DataFrame(
        {
            "region": ["HCMC", "Hanoi", "Danang"],
            "revenue": [1200.0, 300.0, 150.0],
        }
    )

    profile = {
        "shape": {
            "rows": 3,
            "columns": 2,
        },
        "columns": ["region", "revenue"],
        "dtypes": {
            "region": "object",
            "revenue": "float64",
        },
        "missing_values": {
            "region": 0,
            "revenue": 0,
        },
        "missing_percentage": {
            "region": 0.0,
            "revenue": 0.0,
        },
        "numeric_summary": {
            "revenue": {
                "count": 3,
                "mean": 550.0,
                "median": 300.0,
                "min": 150.0,
                "max": 1200.0,
            }
        },
        "categorical_summary": {
            "region": {
                "unique_count": 3,
                "top_values": {
                    "HCMC": 1,
                    "Hanoi": 1,
                    "Danang": 1,
                },
            }
        },
    }

    result = agent.explain_eda_result_with_table_context(
        user_question="tell me about revenue",
        deterministic_result="Column summary for revenue.",
        df=df,
        profile=profile,
    )

    assert result.success
    assert result.prompt_type == "eda_explanation_with_table_context"
    assert result.source == "local_llm"

class FakeEmptyResponseClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "Local LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=True,
            content="",
            model=self.model_name,
            provider="local_ollama",
        )

def test_llm_explanation_agent_falls_back_when_response_empty():
    agent = LLMExplanationAgent(FakeEmptyResponseClient())

    result = agent.explain_eda_result(
        user_question="show missing values",
        deterministic_result="Revenue has 1 missing value.",
        profile=make_profile(),
    )

    assert not result.success
    assert result.fallback_used
    assert result.error == "Empty LLM response."
    assert any("empty" in warning.lower() for warning in result.warnings)