from __future__ import annotations

from typing import Any


class PromptTemplates:
    """
    Week 10:
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
- Rows: {profile.get("shape", {}).get("rows")}
- Columns: {profile.get("shape", {}).get("columns")}

Deterministic result:
{deterministic_result}

Task:
Explain the deterministic result clearly.

Rules:
- Do not invent numbers.
- Do not add unsupported claims.
- Only use the deterministic result and dataset profile.
- Write complete sentences.
- Keep the answer concise.
- Use bullet points when listing columns or findings.
- End with one short conclusion.

Output format:
1. Main finding
2. Details
3. Short conclusion
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

Rules:
- Do not invent values.
- Do not add unsupported claims.
- Only use the chart metadata and chart-grounded insights.
- Write complete sentences.
- Keep the answer concise.
- Use bullet points for key observations.
- End with one short conclusion.

Output format:
1. Chart type and variables
2. Key observations
3. Short conclusion
""".strip()