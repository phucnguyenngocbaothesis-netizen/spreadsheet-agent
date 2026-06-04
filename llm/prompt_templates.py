from __future__ import annotations

from typing import Any


class PromptTemplates:
    """
    Week 8 v0.1:
    Prompt templates for optional LLM-assisted explanation.
    """

    @staticmethod
    def eda_explanation_prompt(
        user_question: str,
        deterministic_result: str,
        profile: dict[str, Any],
    ) -> str:
        return f"""
You are explaining spreadsheet analysis results.

User question:
{user_question}

Dataset shape:
Rows: {profile.get("shape", {}).get("rows")}
Columns: {profile.get("shape", {}).get("columns")}

Deterministic result:
{deterministic_result}

Task:
Explain the deterministic result clearly.
Do not invent numbers.
Only use the provided result and dataset profile.
""".strip()

    @staticmethod
    def chart_explanation_prompt(
        user_question: str,
        chart_metadata: dict[str, Any],
        chart_insights_markdown: str,
    ) -> str:
        return f"""
You are explaining a chart generated from spreadsheet data.

User question:
{user_question}

Chart metadata:
{chart_metadata}

Chart-grounded insights:
{chart_insights_markdown}

Task:
Explain what the chart shows.
Do not invent values.
Only use the chart metadata and chart-grounded insights.
""".strip()