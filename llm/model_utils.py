from __future__ import annotations


class ModelUtils:
    """
    Week 9 v0.3:
    Utilities for displaying and recommending local LLM models.
    """

    @staticmethod
    def get_model_label(model_name: str) -> str:
        name = model_name.lower()

        if "ft" in name or "fine" in name:
            return "Fine-tuned"

        if "q4" in name or "quant" in name:
            return "Quantized"

        if "4b" in name:
            return "Lightweight"

        if "7b" in name or "8b" in name:
            return "Balanced"

        if "deepseek" in name:
            return "Reasoning"

        return "Local model"

    @staticmethod
    def get_model_recommendation(model_name: str) -> str:
        name = model_name.lower()

        if "qwen3:4b" in name:
            return "Recommended for fast local testing."

        if "my-qwen3-ft-q4" in name:
            return "Recommended for testing fine-tuned quantized behavior."

        if "qwen3:8b" in name or "llama3.1:8b" in name:
            return "Good balance between quality and speed."

        if "my-qwen3-ft:latest" in name:
            return "Fine-tuned model, but may be slower and heavier."

        if "deepseek" in name:
            return "Useful for reasoning-style responses, but may be verbose."

        return "General local model."

    @staticmethod
    def format_model_option(model_name: str) -> str:
        label = ModelUtils.get_model_label(model_name)
        recommendation = ModelUtils.get_model_recommendation(model_name)

        return f"{model_name} — {label} — {recommendation}"

    @staticmethod
    def extract_model_name(model_option: str) -> str:
        return model_option.split(" — ")[0].strip()

    @staticmethod
    def sort_models(models: list[str]) -> list[str]:
        priority = [
            "qwen3:4b",
            "my-qwen3-ft-q4:latest",
            "qwen3:8b",
            "llama3.1:8b",
            "qwen2.5:7b",
            "deepseek-r1:7b",
            "my-qwen3-ft:latest",
        ]

        priority_index = {
            model: index
            for index, model in enumerate(priority)
        }

        return sorted(
            models,
            key=lambda model: priority_index.get(model, 999),
        )