from llm.model_utils import ModelUtils


def test_model_utils_labels_lightweight_model():
    label = ModelUtils.get_model_label("qwen3:4b")

    assert label == "Lightweight"


def test_model_utils_labels_fine_tuned_model():
    label = ModelUtils.get_model_label("my-qwen3-ft-q4:latest")

    assert label == "Fine-tuned"


def test_model_utils_formats_and_extracts_model_option():
    option = ModelUtils.format_model_option("qwen3:4b")
    extracted = ModelUtils.extract_model_name(option)

    assert "qwen3:4b" in option
    assert extracted == "qwen3:4b"


def test_model_utils_recommends_qwen3_4b():
    recommendation = ModelUtils.get_model_recommendation("qwen3:4b")

    assert "fast local testing" in recommendation


def test_model_utils_sorts_models_by_priority():
    models = [
        "llama3.1:8b",
        "my-qwen3-ft-q4:latest",
        "qwen3:4b",
    ]

    sorted_models = ModelUtils.sort_models(models)

    assert sorted_models[0] == "qwen3:4b"
    assert sorted_models[1] == "my-qwen3-ft-q4:latest"