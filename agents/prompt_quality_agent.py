from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PromptQualityResult:
    is_acceptable: bool
    issue_type: str | None
    message: str
    suggested_prompts: list[str]
    detected_intents: list[str]
    warnings: list[str]


class PromptQualityAgent:
    """
    Rule-based prompt quality checker.

    Logic stays in Python.
    Patterns and keywords can be loaded from JSON config.
    """

    DEFAULT_CONFIG_PATH = "config/prompt_quality_patterns.json"

    def __init__(
        self,
        config_path: str | None = None,
    ) -> None:
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config(self.config_path)

        self.vague_prompts = self.config["vague_prompts"]
        self.unsupported_patterns = self.config["unsupported_patterns"]
        self.intent_keywords = self.config["intent_keywords"]
        self.default_suggestions = self.config["default_suggestions"]
        self.unsupported_suggestions = self.config["unsupported_suggestions"]

    def evaluate(self, user_question: str) -> PromptQualityResult:
        question = str(user_question).lower().strip()

        if not question:
            return self._bad_prompt(
                issue_type="empty_prompt",
                message="Your prompt is empty. Please ask a spreadsheet analysis question.",
                suggested_prompts=self.default_suggestions,
            )

        if self._is_vague_prompt(question):
            return self._bad_prompt(
                issue_type="vague_prompt",
                message="Your prompt is too broad. Please ask for a specific spreadsheet task.",
                suggested_prompts=self.default_suggestions,
            )

        unsupported_issue = self._detect_unsupported_request(question)

        if unsupported_issue is not None:
            return self._bad_prompt(
                issue_type="unsupported_request",
                message=unsupported_issue,
                suggested_prompts=self.unsupported_suggestions,
            )

        detected_intents = self._detect_intents(question)

        if len(detected_intents) > 1:
            return self._bad_prompt(
                issue_type="multi_intent_prompt",
                message=(
                    "Your prompt contains multiple tasks. "
                    "Please run one task at a time, or ask for a planning workflow."
                ),
                suggested_prompts=[
                    "show missing values",
                    "draw bar chart of gross revenue by region",
                    "write pandas code to group gross revenue by region",
                    "create an analysis plan",
                ],
                detected_intents=detected_intents,
            )

        return PromptQualityResult(
            is_acceptable=True,
            issue_type=None,
            message="Prompt is acceptable.",
            suggested_prompts=[],
            detected_intents=detected_intents,
            warnings=[],
        )

    def _load_config(self, config_path: str) -> dict[str, Any]:
        path = Path(config_path)

        if not path.exists():
            return self._get_default_config()

        try:
            with path.open("r", encoding="utf-8") as file:
                loaded_config = json.load(file)

            return self._validate_config(loaded_config)

        except (json.JSONDecodeError, OSError, TypeError):
            return self._get_default_config()

    def _validate_config(self, loaded_config: dict[str, Any]) -> dict[str, Any]:
        default_config = self._get_default_config()

        validated = default_config.copy()

        for key in [
            "vague_prompts",
            "unsupported_patterns",
            "default_suggestions",
            "unsupported_suggestions",
        ]:
            value = loaded_config.get(key)

            if isinstance(value, list):
                validated[key] = [
                    str(item).lower().strip()
                    for item in value
                    if str(item).strip()
                ]

        intent_keywords = loaded_config.get("intent_keywords")

        if isinstance(intent_keywords, dict):
            validated_intents: dict[str, list[str]] = {}

            for intent, keywords in intent_keywords.items():
                if not isinstance(keywords, list):
                    continue

                validated_intents[str(intent)] = [
                    str(keyword).lower().strip()
                    for keyword in keywords
                    if str(keyword).strip()
                ]

            if validated_intents:
                validated["intent_keywords"] = validated_intents

        return validated

    def _get_default_config(self) -> dict[str, Any]:
        return {
            "vague_prompts": [
                "help",
                "help me",
                "can you help me",
                "tell me something",
                "give me something",
                "what can you do",
                "what should i ask",
                "do something",
                "analyze it",
                "look at this",
                "xem giúp mình",
                "giúp mình",
                "làm gì đó",
                "nói gì đó",
            ],
            "unsupported_patterns": [
                "train a model",
                "fit a model",
                "build a classifier",
                "build a regression model",
                "forecast next month",
                "predict next month",
                "predict next quarter",
                "cluster customers",
                "create full dashboard",
                "build a dashboard",
                "power bi",
                "tableau",
                "drag and drop",
                "export cleaned excel",
                "download cleaned file",
                "save cleaned dataset",
            ],
            "intent_keywords": {
                "DIRECT_ANALYSIS": [
                    "shape",
                    "columns",
                    "data types",
                    "missing",
                    "duplicate",
                    "numeric summary",
                    "categorical summary",
                    "sample rows",
                    "giá trị thiếu",
                    "dòng trùng",
                    "kiểu dữ liệu",
                    "tên cột",
                ],
                "VISUALIZATION": [
                    "chart",
                    "plot",
                    "visualize",
                    "histogram",
                    "scatter",
                    "bar chart",
                    "line chart",
                    "draw",
                    "vẽ",
                    "biểu đồ",
                ],
                "EDA_INSIGHT": [
                    "insight",
                    "analyze",
                    "trend",
                    "pattern",
                    "eda",
                    "phân tích",
                    "xu hướng",
                    "nhận xét",
                ],
                "CODEGEN_SQL": [
                    "code",
                    "pandas",
                    "sql",
                    "query",
                    "write code",
                    "viết code",
                    "truy vấn",
                ],
                "PLANNING": [
                    "plan",
                    "workflow",
                    "steps",
                    "roadmap",
                    "process",
                    "kế hoạch",
                    "quy trình",
                    "các bước",
                ],
                "PERSONALIZATION": [
                    "beginner",
                    "simple",
                    "technical",
                    "concise",
                    "detailed",
                    "đơn giản",
                    "ngắn gọn",
                    "chi tiết",
                ],
            },
            "default_suggestions": [
                "show missing values",
                "tell me about gross revenue",
                "draw bar chart of gross revenue by region",
                "find insights in this dataset",
                "write pandas code to group gross revenue by region",
                "create a cleaning plan",
            ],
            "unsupported_suggestions": [
                "create a data cleaning plan",
                "create an analysis plan",
                "write pandas code to prepare the dataset",
                "show numeric summary",
            ],
        }

    def _is_vague_prompt(self, question: str) -> bool:
        return question in self.vague_prompts

    def _detect_unsupported_request(self, question: str) -> str | None:
        for pattern in self.unsupported_patterns:
            if pattern in question:
                return (
                    "This request is outside the current prototype scope. "
                    "The app can create a plan or generate helper code, but it does not "
                    "train models, build full dashboards, or export cleaned files yet."
                )

        return None

    def _detect_intents(self, question: str) -> list[str]:
        detected = []

        for intent, keywords in self.intent_keywords.items():
            if any(keyword in question for keyword in keywords):
                detected.append(intent)

        return detected

    def _bad_prompt(
        self,
        issue_type: str,
        message: str,
        suggested_prompts: list[str],
        detected_intents: list[str] | None = None,
    ) -> PromptQualityResult:
        return PromptQualityResult(
            is_acceptable=False,
            issue_type=issue_type,
            message=message,
            suggested_prompts=suggested_prompts,
            detected_intents=detected_intents or [],
            warnings=[message],
        )

    def format_result_as_markdown(
        self,
        result: PromptQualityResult,
    ) -> str:
        if result.is_acceptable:
            return "Prompt is acceptable."

        lines = [
            "I could not process this prompt reliably.",
            "",
            f"Reason: {result.message}",
            "",
        ]

        if result.detected_intents:
            lines.append("Detected multiple possible intents:")
            for intent in result.detected_intents:
                lines.append(f"- `{intent}`")
            lines.append("")

        if result.suggested_prompts:
            lines.append("Try one of these prompts instead:")
            for prompt in result.suggested_prompts:
                lines.append(f"- `{prompt}`")

        return "\n".join(lines)