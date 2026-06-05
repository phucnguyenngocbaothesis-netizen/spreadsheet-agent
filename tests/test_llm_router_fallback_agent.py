from agents.llm_router_fallback_agent import LLMRouterFallbackAgent
from llm.local_llm_client import LLMResponse


class FakeUnavailableClient:
    model_name = "fake-model"

    def get_status(self):
        class Status:
            available = False
            message = "LLM unavailable."

        return Status()

    def validate_model(self):
        raise AssertionError("validate_model should not be called.")

    def generate(self, *args, **kwargs):
        raise AssertionError("generate should not be called.")


class FakeInvalidModelClient:
    model_name = "missing-model"

    def get_status(self):
        class Status:
            available = True
            message = "LLM available."

        return Status()

    def validate_model(self):
        class Validation:
            is_valid = False
            message = "Model not found."

        return Validation()

    def generate(self, *args, **kwargs):
        raise AssertionError("generate should not be called.")


class FakeSuccessfulRouteClient:
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
            content="VISUALIZATION",
            model=self.model_name,
            provider="local_ollama",
        )


class FakeInvalidRouteResponseClient:
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
            content="I think this is about something else.",
            model=self.model_name,
            provider="local_ollama",
        )


class FakeFailedGenerationClient:
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
            success=False,
            content="",
            model=self.model_name,
            provider="local_ollama",
            error="Generation failed.",
        )


def test_llm_router_fallback_skips_when_llm_unavailable():
    agent = LLMRouterFallbackAgent(FakeUnavailableClient())

    result = agent.classify_unknown_route("make a visual breakdown")

    assert not result.used_llm
    assert result.route_result.route == "UNKNOWN"
    assert result.warnings


def test_llm_router_fallback_skips_when_model_invalid():
    agent = LLMRouterFallbackAgent(FakeInvalidModelClient())

    result = agent.classify_unknown_route("make a visual breakdown")

    assert not result.used_llm
    assert result.route_result.route == "UNKNOWN"
    assert "Model not found" in result.error


def test_llm_router_fallback_returns_valid_route():
    agent = LLMRouterFallbackAgent(FakeSuccessfulRouteClient())

    result = agent.classify_unknown_route("make a visual breakdown")

    assert result.used_llm
    assert result.route_result.route == "VISUALIZATION"
    assert "llm_route_fallback" in result.route_result.matched_keywords


def test_llm_router_fallback_returns_unknown_for_invalid_route_response():
    agent = LLMRouterFallbackAgent(FakeInvalidRouteResponseClient())

    result = agent.classify_unknown_route("unrelated request")

    assert result.used_llm
    assert result.route_result.route == "UNKNOWN"


def test_llm_router_fallback_handles_generation_failure():
    agent = LLMRouterFallbackAgent(FakeFailedGenerationClient())

    result = agent.classify_unknown_route("make a visual breakdown")

    assert not result.used_llm
    assert result.route_result.route == "UNKNOWN"
    assert "Generation failed" in result.error


def test_llm_router_fallback_parses_route_inside_sentence():
    agent = LLMRouterFallbackAgent(FakeSuccessfulRouteClient())

    route = agent._parse_route("The best route is CODEGEN_SQL.")

    assert route == "CODEGEN_SQL"