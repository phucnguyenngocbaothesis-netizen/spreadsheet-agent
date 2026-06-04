from llm.local_llm_client import LocalLLMClient, LLMResponse


def test_local_llm_client_builds_prompt_with_system_prompt():
    client = LocalLLMClient()

    prompt = client._build_prompt(
        prompt="Explain missing values.",
        system_prompt="Be concise.",
    )

    assert "System instruction" in prompt
    assert "Be concise" in prompt
    assert "Explain missing values" in prompt


def test_local_llm_client_builds_prompt_without_system_prompt():
    client = LocalLLMClient()

    prompt = client._build_prompt(
        prompt="Explain missing values.",
        system_prompt=None,
    )

    assert prompt == "Explain missing values."


def test_local_llm_client_handles_empty_prompt():
    client = LocalLLMClient()

    response = client.generate("")

    assert isinstance(response, LLMResponse)
    assert not response.success
    assert response.error == "Empty prompt received."


def test_local_llm_client_returns_false_when_unavailable(monkeypatch):
    client = LocalLLMClient()

    def mock_get(*args, **kwargs):
        raise Exception("Connection failed")

    monkeypatch.setattr("requests.get", mock_get)

    assert not client.is_available()

def test_local_llm_client_generate_handles_request_error(monkeypatch):
    client = LocalLLMClient()

    def mock_post(*args, **kwargs):
        raise Exception("Connection failed")

    monkeypatch.setattr("requests.post", mock_post)

    response = client.generate("Explain this result.")

    assert not response.success
    assert response.error
    assert response.content == ""

def test_local_llm_client_status_when_unavailable(monkeypatch):
    client = LocalLLMClient(model_name="test-model")

    def mock_get(*args, **kwargs):
        raise Exception("Connection failed")

    monkeypatch.setattr("requests.get", mock_get)

    status = client.get_status()

    assert not status.available
    assert status.provider == "local_ollama"
    assert status.model == "test-model"
    assert "fallback" in status.message.lower()


def test_local_llm_client_status_when_available(monkeypatch):
    client = LocalLLMClient(model_name="test-model")

    class MockResponse:
        status_code = 200

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    status = client.get_status()

    assert status.available
    assert status.provider == "local_ollama"
    assert status.model == "test-model"
    assert "available" in status.message.lower()

def test_local_llm_client_list_models_when_available(monkeypatch):
    client = LocalLLMClient()

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "models": [
                    {"name": "llama3.1:8b"},
                    {"name": "qwen2.5:3b"},
                ]
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    models = client.list_models()

    assert "llama3.1:8b" in models
    assert "qwen2.5:3b" in models


def test_local_llm_client_list_models_when_unavailable(monkeypatch):
    client = LocalLLMClient()

    def mock_get(*args, **kwargs):
        raise Exception("Connection failed")

    monkeypatch.setattr("requests.get", mock_get)

    models = client.list_models()

    assert models == []


def test_local_llm_client_validate_model_success(monkeypatch):
    client = LocalLLMClient(model_name="llama3.1:8b")

    def mock_list_models():
        return ["llama3.1:8b", "qwen2.5:3b"]

    monkeypatch.setattr(client, "list_models", mock_list_models)

    result = client.validate_model()

    assert result.is_valid
    assert result.requested_model == "llama3.1:8b"
    assert "llama3.1:8b" in result.available_models


def test_local_llm_client_validate_model_failure(monkeypatch):
    client = LocalLLMClient(model_name="missing-model")

    def mock_list_models():
        return ["llama3.1:8b", "qwen2.5:3b"]

    monkeypatch.setattr(client, "list_models", mock_list_models)

    result = client.validate_model()

    assert not result.is_valid
    assert result.requested_model == "missing-model"
    assert result.available_models
    assert "not found" in result.message


def test_local_llm_client_validate_model_no_models(monkeypatch):
    client = LocalLLMClient(model_name="llama3.1:8b")

    def mock_list_models():
        return []

    monkeypatch.setattr(client, "list_models", mock_list_models)

    result = client.validate_model()

    assert not result.is_valid
    assert result.available_models == []
    assert "No local models" in result.message