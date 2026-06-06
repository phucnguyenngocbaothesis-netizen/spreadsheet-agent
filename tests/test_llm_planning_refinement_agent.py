from agents.llm_planning_refinement_agent import LLMPlanningRefinementAgent
from llm.local_llm_client import LLMResponse


class FakeSuccessfulPlanningClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = True
            message = "Model available."

        return Validation()

    def generate(self, *args, **kwargs):
        return LLMResponse(
            success=True,
            content="1. Check missing values.\n2. Review numeric columns.\n3. Create charts.",
            model=self.model_name,
            provider="local_ollama",
        )


class FakeUnavailablePlanningClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = False
            message = "LLM unavailable."

        return Status()

    def validate_model(self):
        raise AssertionError("validate_model should not be called.")

    def generate(self, *args, **kwargs):
        raise AssertionError("generate should not be called.")


class FakeEmptyPlanningClient:
    model_name = "qwen3:4b"

    def get_status(self):
        class Status:
            available = True
            message = "LLM available."

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


def test_llm_planning_refinement_success():
    agent = LLMPlanningRefinementAgent(FakeSuccessfulPlanningClient())

    result = agent.refine_plan(
        user_question="create a cleaning plan",
        deterministic_plan="Step 1: Check missing values.",
    )

    assert result.success
    assert not result.fallback_used
    assert result.source == "local_llm"


def test_llm_planning_refinement_fallback_when_unavailable():
    agent = LLMPlanningRefinementAgent(FakeUnavailablePlanningClient())

    result = agent.refine_plan(
        user_question="create a cleaning plan",
        deterministic_plan="Step 1: Check missing values.",
    )

    assert not result.success
    assert result.fallback_used
    assert result.source == "deterministic_fallback"
    assert "Step 1" in result.refined_plan


def test_llm_planning_refinement_fallback_when_empty():
    agent = LLMPlanningRefinementAgent(FakeEmptyPlanningClient())

    result = agent.refine_plan(
        user_question="create a cleaning plan",
        deterministic_plan="Step 1: Check missing values.",
    )

    assert not result.success
    assert result.fallback_used
    assert result.error == "Empty LLM planning refinement."