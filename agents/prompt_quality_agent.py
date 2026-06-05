from __future__ import annotations

from dataclasses import dataclass


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
    Week 11 v1.6:
    Rule-based prompt quality checker.

    This agent detects vague, unsupported, or multi-intent prompts before routing.
    It does not use an LLM.
    """

    def evaluate(self, user_question: str) -> PromptQualityResult:
        question = user_question.lower().strip()

        if not question:
            return self._bad_prompt(
                issue_type="empty_prompt",
                message="Your prompt is empty. Please ask a spreadsheet analysis question.",
                suggested_prompts=self._default_suggestions(),
            )

        if self._is_vague_prompt(question):
            return self._bad_prompt(
                issue_type="vague_prompt",
                message="Your prompt is too broad. Please ask for a specific spreadsheet task.",
                suggested_prompts=self._default_suggestions(),
            )

        unsupported_issue = self._detect_unsupported_request(question)

        if unsupported_issue is not None:
            return self._bad_prompt(
                issue_type="unsupported_request",
                message=unsupported_issue,
                suggested_prompts=[
                    "create a data cleaning plan",
                    "create an analysis plan",
                    "write pandas code to prepare the dataset",
                    "show numeric summary",
                ],
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

    def _is_vague_prompt(self, question: str) -> bool:
        vague_prompts = [
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
        ]

        return question in vague_prompts

    def _detect_unsupported_request(self, question: str) -> str | None:
        unsupported_patterns = [
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
        ]

        for pattern in unsupported_patterns:
            if pattern in question:
                return (
                    "This request is outside the current prototype scope. "
                    "The app can create a plan or generate helper code, but it does not "
                    "train models, build full dashboards, or export cleaned files yet."
                )

        return None

    def _detect_intents(self, question: str) -> list[str]:
        intent_keywords = {
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
        }

        detected = []

        for intent, keywords in intent_keywords.items():
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

    def _default_suggestions(self) -> list[str]:
        return [
            "show missing values",
            "tell me about gross revenue",
            "draw bar chart of gross revenue by region",
            "find insights in this dataset",
            "write pandas code to group gross revenue by region",
            "create a cleaning plan",
        ]

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