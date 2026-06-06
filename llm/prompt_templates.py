from __future__ import annotations

from typing import Any



class PromptTemplates:
    """
    Week 10:
    Prompt templates for optional LLM-assisted explanation.
    """

    @staticmethod
    def get_response_language_instruction(language: str) -> str:
        if language == "vi":
            return "Respond in Vietnamese."

        return "Respond in English."

    @staticmethod
    def planning_refinement_prompt(
        user_question: str,
        deterministic_plan: str,
        language: str = "en",
    ) -> str:
        response_language_instruction = (
            PromptTemplates.get_response_language_instruction(language)
        )

        return f"""
    You are refining a deterministic spreadsheet analysis plan.

    User question:
    {user_question}

    Deterministic plan:
    {deterministic_plan}

    Response language:
    {response_language_instruction}

    Task:
    Rewrite the plan so it is clearer, easier to follow, and more useful for a spreadsheet analysis workflow.

    Rules:
    - Do not create a completely new plan.
    - Do not remove important steps from the deterministic plan.
    - Do not invent dataset columns.
    - Do not invent results.
    - Keep the original workflow intent.
    - Keep the plan concise.
    - Use numbered steps.
    - Add short explanations only when useful.

    Output format:
    1. Refined workflow
    2. Why these steps matter
    3. Short conclusion
    """.strip()

    @staticmethod
    def eda_explanation_prompt(
        user_question: str,
        deterministic_result: str,
        profile: dict[str, Any],
        language: str = "en",
    ) -> str:
        response_language_instruction = PromptTemplates.get_response_language_instruction(
            language
        )
        return f"""
You are explaining spreadsheet analysis results.

User question:
{user_question}

Dataset shape:
- Rows: {profile.get("shape", {}).get("rows")}
- Columns: {profile.get("shape", {}).get("columns")}

Deterministic result:
{deterministic_result}

Response language:
{response_language_instruction}

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
        language: str = "en",
    ) -> str:
        response_language_instruction = PromptTemplates.get_response_language_instruction(
            language
        )
        return f"""
You are explaining a chart generated from spreadsheet data.

User question:
{user_question}

Chart metadata:
{chart_metadata}

Chart-grounded insights:
{chart_insights_markdown}

Response language:
{response_language_instruction}

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
    
    @staticmethod
    def eda_explanation_with_table_context_prompt(
        user_question: str,
        deterministic_result: str,
        table_context_markdown: str,
        language: str = "en",
    ) -> str:
        response_language_instruction = PromptTemplates.get_response_language_instruction(
            language
        )
        return f"""
    You are explaining spreadsheet analysis results.

    User question:
    {user_question}

    Deterministic result:
    {deterministic_result}

    Query-aware table context:
    {table_context_markdown}

    Response language:
    {response_language_instruction}

    Task:
    Explain the deterministic result clearly using the selected table context.

    Rules:
    - Do not invent numbers.
    - Do not add unsupported claims.
    - Only use the deterministic result and query-aware table context.
    - Write complete sentences.
    - Keep the answer concise.
    - Use bullet points when listing columns or findings.
    - End with one short conclusion.

    Output format:
    1. Main finding
    2. Relevant table context
    3. Short conclusion
    """.strip()