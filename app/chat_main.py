from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.column_validation_agent import ColumnValidationAgent
from agents.prompt_quality_agent import PromptQualityAgent
from agents.chart_builder import ChartBuilderAgent
from agents.codegen_sql import CodegenSQLAgent
from agents.direct_analysis import DirectAnalysisAgent
from agents.eda_insight import EDAInsightAgent
from agents.fast_router import FastRouterAgent
from agents.llm_explanation_agent import LLMExplanationAgent
from agents.llm_router_fallback_agent import LLMRouterFallbackAgent
from agents.personalization_agent import PersonalizationAgent
from agents.planning_agent import PlanningAgent
from core.language_utils import LanguageUtils
from core.pipeline import SpreadsheetPipeline
from llm.local_llm_client import LocalLLMClient
from llm.model_utils import ModelUtils
from storage.sqlite_store import SQLiteStore


st.set_page_config(
    page_title="Spreadsheet Agent Chat",
    layout="wide",
)

pipeline = SpreadsheetPipeline()
direct_analysis_agent = DirectAnalysisAgent()
fast_router_agent = FastRouterAgent()
chart_builder_agent = ChartBuilderAgent()
eda_insight_agent = EDAInsightAgent()
codegen_sql_agent = CodegenSQLAgent()
planning_agent = PlanningAgent()
personalization_agent = PersonalizationAgent()
prompt_quality_agent = PromptQualityAgent()
sqlite_store = SQLiteStore()
column_validation_agent = ColumnValidationAgent()

@st.cache_data(ttl=30)
def get_cached_llm_models() -> list[str]:
    client = LocalLLMClient()
    return client.list_models()


def initialize_chat_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "dataset_loaded" not in st.session_state:
        st.session_state.dataset_loaded = False


def add_message(
    role: str,
    content: str,
    artifact: dict[str, Any] | None = None,
) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "artifact": artifact,
        }
    )


def render_message(message: dict[str, Any]) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        artifact = message.get("artifact")

        if not artifact:
            return

        artifact_type = artifact.get("type")

        if artifact_type == "chart":
            st.pyplot(artifact["figure"])

            with st.expander("Chart data"):
                st.dataframe(
                    artifact["chart_data"],
                    use_container_width=True,
                )

            with st.expander("Chart metadata"):
                st.json(artifact["metadata"])

        elif artifact_type == "code":
            st.code(
                artifact["code"],
                language=artifact.get("language", "python"),
            )

            with st.expander("Codegen metadata"):
                st.json(artifact["metadata"])

        elif artifact_type == "json":
            with st.expander(artifact.get("title", "Metadata")):
                st.json(artifact["data"])

        elif artifact_type == "planning_steps":
            for step in artifact["steps"]:
                with st.expander(f"Step {step.step_number}: {step.title}"):
                    st.write(step.description)
                    st.json(
                        {
                            "target_agent": step.target_agent,
                            "expected_output": step.expected_output,
                        }
                    )


def render_llm_explanation_if_enabled(
    enable_llm_explanation: bool,
    llm_explanation_result,
) -> str:
    if not enable_llm_explanation:
        return ""

    lines = [
        "",
        "---",
        "### Optional LLM Explanation",
        "",
        f"- LLM success: `{llm_explanation_result.success}`",
        f"- Fallback used: `{llm_explanation_result.fallback_used}`",
        f"- Model: `{llm_explanation_result.model}`",
        "",
    ]

    if llm_explanation_result.warnings:
        lines.append("Warnings:")
        for warning in llm_explanation_result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append(llm_explanation_result.explanation)

    return "\n".join(lines)


def build_sidebar():
    st.sidebar.title("Spreadsheet Agent")
    st.sidebar.caption("Upload a spreadsheet, ask questions, and inspect results.")

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
    )

    st.sidebar.header("User Profile")

    user_id = st.sidebar.text_input(
        "User ID",
        value="default_user",
    )

    stored_profile = sqlite_store.load_user_profile(user_id)

    default_role = stored_profile.role if stored_profile else "student"
    default_technical_level = (
        stored_profile.technical_level if stored_profile else "beginner"
    )
    default_response_style = (
        stored_profile.response_style if stored_profile else "balanced"
    )
    default_preferred_format = (
        stored_profile.preferred_format if stored_profile else "bullet"
    )

    technical_level_options = ["beginner", "intermediate", "advanced"]
    response_style_options = ["concise", "balanced", "detailed"]
    preferred_format_options = ["bullet", "paragraph", "step_by_step"]

    user_role = st.sidebar.text_input(
        "Role",
        value=default_role,
    )

    technical_level = st.sidebar.selectbox(
        "Technical level",
        options=technical_level_options,
        index=technical_level_options.index(default_technical_level)
        if default_technical_level in technical_level_options
        else 0,
    )

    response_style = st.sidebar.selectbox(
        "Response style",
        options=response_style_options,
        index=response_style_options.index(default_response_style)
        if default_response_style in response_style_options
        else 1,
    )

    preferred_format = st.sidebar.selectbox(
        "Preferred format",
        options=preferred_format_options,
        index=preferred_format_options.index(default_preferred_format)
        if default_preferred_format in preferred_format_options
        else 0,
    )

    if st.sidebar.button("Save User Profile"):
        sqlite_store.save_user_profile(
            user_id=user_id,
            role=user_role,
            technical_level=technical_level,
            response_style=response_style,
            preferred_format=preferred_format,
        )
        st.sidebar.success("User profile saved.")
        st.rerun()

    apply_personalization = st.sidebar.checkbox(
        "Apply personalization to text outputs",
        value=False,
    )

    st.sidebar.header("LLM Settings")

    enable_llm_explanation = st.sidebar.checkbox(
        "Enable optional LLM explanation",
        value=False,
    )

    enable_llm_route_fallback = st.sidebar.checkbox(
        "Enable optional LLM route fallback",
        value=False,
    )

    available_llm_models = get_cached_llm_models()
    available_llm_models = ModelUtils.sort_models(available_llm_models)

    if available_llm_models:
        model_options = [
            ModelUtils.format_model_option(model)
            for model in available_llm_models
        ]

        default_model = (
            "qwen3:4b"
            if "qwen3:4b" in available_llm_models
            else available_llm_models[0]
        )

        default_model_option = ModelUtils.format_model_option(default_model)
        default_model_index = model_options.index(default_model_option)

        selected_model_option = st.sidebar.selectbox(
            "Local LLM model",
            options=model_options,
            index=default_model_index,
        )

        llm_model_name = ModelUtils.extract_model_name(selected_model_option)

        st.sidebar.caption(
            ModelUtils.get_model_recommendation(llm_model_name)
        )
    else:
        llm_model_name = st.sidebar.text_input(
            "Local LLM model",
            value="llama3.1:8b",
        )

        st.sidebar.warning(
            "No local Ollama models detected. You can still type a model name manually."
        )

    local_llm_client = LocalLLMClient(model_name=llm_model_name)
    llm_explanation_agent = LLMExplanationAgent(local_llm_client)
    llm_router_fallback_agent = LLMRouterFallbackAgent(local_llm_client)

    if enable_llm_explanation or enable_llm_route_fallback:
        llm_status = local_llm_client.get_status()
        llm_model_validation = local_llm_client.validate_model()

        with st.sidebar.expander("LLM Status"):
            st.json(
                {
                    "available": llm_status.available,
                    "provider": llm_status.provider,
                    "model": llm_status.model,
                    "base_url": llm_status.base_url,
                    "status_message": llm_status.message,
                    "model_valid": llm_model_validation.is_valid,
                    "model_message": llm_model_validation.message,
                    "available_models": llm_model_validation.available_models,
                }
            )

    st.sidebar.header("Chat")

    if st.sidebar.button("New Chat"):
        st.session_state.messages = []
        st.rerun()
    st.sidebar.caption(
    "New Chat clears only the current visible chat session. Saved recent questions remain in SQLite."
    )

    recent_history = sqlite_store.load_recent_chat_history(
        user_id=user_id,
        limit=5,
    )

    with st.sidebar.expander("Recent Questions"):
        if not recent_history:
            st.caption("No recent questions yet.")
        else:
            for message in recent_history:
                st.markdown(f"- `{message.route}`: {message.question}")

    if st.sidebar.button("Clear Saved History"):
        sqlite_store.clear_chat_history(user_id)
        st.sidebar.success("Saved chat history cleared.")
        st.rerun()

    user_profile = personalization_agent.create_profile(
        role=user_role,
        technical_level=technical_level,
        response_style=response_style,
        preferred_format=preferred_format,
    )

    return {
        "uploaded_file": uploaded_file,
        "user_id": user_id,
        "user_profile": user_profile,
        "apply_personalization": apply_personalization,
        "enable_llm_explanation": enable_llm_explanation,
        "enable_llm_route_fallback": enable_llm_route_fallback,
        "llm_explanation_agent": llm_explanation_agent,
        "llm_router_fallback_agent": llm_router_fallback_agent,
    }


def personalize_if_enabled(
    content: str,
    user_profile,
    apply_personalization: bool,
) -> str:
    if not apply_personalization:
        return content

    result = personalization_agent.personalize_response(
        content=content,
        profile=user_profile,
    )

    return result.personalized_content


def process_question(
    question: str,
    df,
    profile: dict[str, Any],
    sidebar_state: dict[str, Any],
    uploaded_file_name: str,
) -> dict[str, Any]:
    
    prompt_quality_result = prompt_quality_agent.evaluate(question)

    if not prompt_quality_result.is_acceptable:
        content = prompt_quality_agent.format_result_as_markdown(
            prompt_quality_result
        )

        artifact = {
            "type": "json",
            "title": "Prompt quality metadata",
            "data": {
                "is_acceptable": prompt_quality_result.is_acceptable,
                "issue_type": prompt_quality_result.issue_type,
                "message": prompt_quality_result.message,
                "detected_intents": prompt_quality_result.detected_intents,
                "suggested_prompts": prompt_quality_result.suggested_prompts,
                "warnings": prompt_quality_result.warnings,
            },
        }

        sqlite_store.save_chat_message(
            user_id=sidebar_state["user_id"],
            dataset_name=uploaded_file_name,
            question=question,
            route="PROMPT_QUALITY_REJECTED",
            answer_preview=content,
        )

        return {
            "role": "assistant",
            "content": content,
            "artifact": artifact,
        }

    detected_language = LanguageUtils.detect_language(question)

    column_validation_result = column_validation_agent.validate_question_columns(
        question=question,
        available_columns=profile.get("columns", []),
    )

    if column_validation_result.has_missing_columns:
        content = column_validation_agent.format_result_as_markdown(
            column_validation_result
        )

        artifact = {
            "type": "json",
            "title": "Column validation metadata",
            "data": {
                "has_missing_columns": column_validation_result.has_missing_columns,
                "mentioned_columns": column_validation_result.mentioned_columns,
                "missing_columns": column_validation_result.missing_columns,
                "existing_columns": column_validation_result.existing_columns,
                "suggestions": column_validation_result.suggestions,
                "warnings": column_validation_result.warnings,
            },
        }

        sqlite_store.save_chat_message(
            user_id=sidebar_state["user_id"],
            dataset_name=uploaded_file_name,
            question=question,
            route="COLUMN_VALIDATION_REJECTED",
            answer_preview=content,
        )

        return {
            "role": "assistant",
            "content": content,
            "artifact": artifact,
        }

    route_result = fast_router_agent.route(question, profile)
    column_sensitive_routes = {
        "DIRECT_ANALYSIS",
        "VISUALIZATION",
        "CODEGEN_SQL",
    }

    if (
        route_result.route in column_sensitive_routes
        and column_validation_agent.should_validate_question_columns(
            question=question,
            route=route_result.route,
        )
    ):
        column_validation_result = column_validation_agent.validate_question_columns(
            question=question,
            available_columns=profile.get("columns", []),
        )

        if column_validation_result.has_missing_columns:
            content = column_validation_agent.format_result_as_markdown(
                column_validation_result
            )

            artifact = {
                "type": "json",
                "title": "Column validation metadata",
                "data": {
                    "has_missing_columns": column_validation_result.has_missing_columns,
                    "mentioned_columns": column_validation_result.mentioned_columns,
                    "missing_columns": column_validation_result.missing_columns,
                    "existing_columns": column_validation_result.existing_columns,
                    "suggestions": column_validation_result.suggestions,
                    "warnings": column_validation_result.warnings,
                },
            }

            sqlite_store.save_chat_message(
                user_id=sidebar_state["user_id"],
                dataset_name=uploaded_file_name,
                question=question,
                route="COLUMN_VALIDATION_REJECTED",
                answer_preview=content,
            )

            return {
                "role": "assistant",
                "content": content,
                "artifact": artifact,
            }


    llm_route_fallback_result = None

    if (
        route_result.route == "UNKNOWN"
        and sidebar_state["enable_llm_route_fallback"]
    ):
        llm_route_fallback_result = sidebar_state[
            "llm_router_fallback_agent"
        ].classify_unknown_route(
            user_question=question,
        )
        route_result = llm_route_fallback_result.route_result

    route_header = (
        f"**Route:** `{route_result.route}`  \n"
        f"**Confidence:** `{route_result.confidence}`  \n"
        f"**Reason:** {route_result.reason}"
    )

    artifact = {
        "type": "json",
        "title": "Route metadata",
        "data": {
            "route": route_result.route,
            "confidence": route_result.confidence,
            "matched_keywords": route_result.matched_keywords,
            "reason": route_result.reason,
            "llm_route_fallback": (
                {
                    "used_llm": llm_route_fallback_result.used_llm,
                    "raw_response": llm_route_fallback_result.raw_response,
                    "error": llm_route_fallback_result.error,
                    "warnings": llm_route_fallback_result.warnings,
                }
                if llm_route_fallback_result
                else None
            ),
        },
    }

    answer_preview = ""

    if route_result.route == "DIRECT_ANALYSIS":
        answer = direct_analysis_agent.answer(
            question,
            profile,
            language=detected_language,
        )

        answer = personalize_if_enabled(
            content=answer,
            user_profile=sidebar_state["user_profile"],
            apply_personalization=sidebar_state["apply_personalization"],
        )

        llm_extra = ""

        if sidebar_state["enable_llm_explanation"]:
            llm_result = sidebar_state[
                "llm_explanation_agent"
            ].explain_eda_result_with_table_context(
                user_question=question,
                deterministic_result=answer,
                df=df,
                profile=profile,
                language=detected_language,
            )

            llm_extra = render_llm_explanation_if_enabled(
                enable_llm_explanation=True,
                llm_explanation_result=llm_result,
            )

        content = f"{route_header}\n\n---\n\n{answer}{llm_extra}"
        answer_preview = answer

    elif route_result.route == "VISUALIZATION":
        try:
            chart_result = chart_builder_agent.build_chart(question, df)

            chart_insight_result = eda_insight_agent.generate_chart_insights(
                chart_type=chart_result.chart_type,
                chart_data=chart_result.chart_data,
                x_column=chart_result.x_column,
                y_column=chart_result.y_column,
            )

            chart_insight_markdown = eda_insight_agent.format_result_as_markdown(
                chart_insight_result
            )

            chart_insight_markdown = personalize_if_enabled(
                content=chart_insight_markdown,
                user_profile=sidebar_state["user_profile"],
                apply_personalization=sidebar_state["apply_personalization"],
            )

            llm_extra = ""

            if sidebar_state["enable_llm_explanation"]:
                chart_metadata = {
                    "chart_type": chart_result.chart_type,
                    "x_column": chart_result.x_column,
                    "y_column": chart_result.y_column,
                    "reason": chart_result.reason,
                }

                llm_result = sidebar_state[
                    "llm_explanation_agent"
                ].explain_chart_result(
                    user_question=question,
                    chart_metadata=chart_metadata,
                    chart_insights_markdown=chart_insight_markdown,
                    language=detected_language,
                )

                llm_extra = render_llm_explanation_if_enabled(
                    enable_llm_explanation=True,
                    llm_explanation_result=llm_result,
                )

            content = (
                f"{route_header}\n\n---\n\n"
                f"Created a `{chart_result.chart_type}` chart.\n\n"
                f"{chart_insight_markdown}"
                f"{llm_extra}"
            )

            artifact = {
                "type": "chart",
                "figure": chart_result.figure,
                "chart_data": chart_result.chart_data,
                "metadata": {
                    "chart_type": chart_result.chart_type,
                    "x_column": chart_result.x_column,
                    "y_column": chart_result.y_column,
                    "reason": chart_result.reason,
                },
            }

            answer_preview = content

        except Exception as chart_error:
            content = (
                f"{route_header}\n\n---\n\n"
                "I could not build a chart from this prompt.\n\n"
                "Please specify a chart type and valid dataset columns.\n\n"
                "Try one of these prompts:\n"
                "- draw bar chart of gross revenue by region\n"
                "- show histogram of profit\n"
                "- show line chart of gross revenue over order date\n"
                "- show scatter plot of shipping cost and profit\n\n"
                f"Error: `{chart_error}`"
            )

            artifact = {
                "type": "json",
                "title": "Chart error metadata",
                "data": {
                    "route": route_result.route,
                    "question": question,
                    "error": str(chart_error),
                    "suggested_prompts": [
                        "draw bar chart of gross revenue by region",
                        "show histogram of profit",
                        "show line chart of gross revenue over order date",
                        "show scatter plot of shipping cost and profit",
                    ],
                },
            }

            answer_preview = content

    elif route_result.route == "EDA_INSIGHT":
        insight_result = eda_insight_agent.generate_insights(profile)
        insight_markdown = eda_insight_agent.format_result_as_markdown(
            insight_result
        )

        insight_markdown = personalize_if_enabled(
            content=insight_markdown,
            user_profile=sidebar_state["user_profile"],
            apply_personalization=sidebar_state["apply_personalization"],
        )

        llm_extra = ""

        if sidebar_state["enable_llm_explanation"]:
            llm_result = sidebar_state[
                "llm_explanation_agent"
            ].explain_eda_result_with_table_context(
                user_question=question,
                deterministic_result=insight_markdown,
                df=df,
                profile=profile,
                language=detected_language,
            )

            llm_extra = render_llm_explanation_if_enabled(
                enable_llm_explanation=True,
                llm_explanation_result=llm_result,
            )

        content = f"{route_header}\n\n---\n\n{insight_markdown}{llm_extra}"
        answer_preview = insight_markdown

    elif route_result.route == "CODEGEN_SQL":
        codegen_result = codegen_sql_agent.generate(question, profile)

        content = (
            f"{route_header}\n\n---\n\n"
            f"{codegen_result.explanation}"
        )

        artifact = {
            "type": "code",
            "code": codegen_result.code,
            "language": "sql" if codegen_result.mode == "sql" else "python",
            "metadata": {
                "mode": codegen_result.mode,
                "generated_code_type": codegen_result.generated_code_type,
                "required_inputs": codegen_result.required_inputs,
                "assumptions": codegen_result.assumptions,
                "warnings": codegen_result.warnings,
            },
        }

        answer_preview = codegen_result.explanation

    elif route_result.route == "PLANNING":
        planning_result = planning_agent.create_plan(question, profile)
        planning_markdown = planning_agent.format_result_as_markdown(
            planning_result
        )

        planning_markdown = personalize_if_enabled(
            content=planning_markdown,
            user_profile=sidebar_state["user_profile"],
            apply_personalization=sidebar_state["apply_personalization"],
        )

        content = f"{route_header}\n\n---\n\n{planning_markdown}"

        artifact = {
            "type": "planning_steps",
            "steps": planning_result.steps,
        }

        answer_preview = planning_markdown

    elif route_result.route == "PERSONALIZATION":
        base_content = (
            "This dataset has "
            f"{profile['shape']['rows']} rows and {profile['shape']['columns']} columns. "
            "The system can inspect missing values, duplicate rows, numeric summaries, "
            "categorical summaries, charts, EDA insights, code generation, and analysis plans."
        )

        personalization_result = personalization_agent.personalize_response(
            content=base_content,
            profile=sidebar_state["user_profile"],
        )

        content = (
            f"{route_header}\n\n---\n\n"
            f"{personalization_result.personalized_content}"
        )

        artifact = {
            "type": "json",
            "title": "Personalization metadata",
            "data": {
                "profile": personalization_agent.summarize_profile(
                    sidebar_state["user_profile"]
                ),
                "applied_rules": personalization_result.applied_rules,
                "warnings": personalization_result.warnings,
            },
        }

        answer_preview = personalization_result.personalized_content

    else:
        content = (
            f"{route_header}\n\n---\n\n"
            "I could not route this request yet. Try asking about missing values, "
            "columns, charts, insights, pandas/SQL code, or analysis planning."
        )

        answer_preview = content

    if answer_preview:
        sqlite_store.save_chat_message(
            user_id=sidebar_state["user_id"],
            dataset_name=uploaded_file_name,
            question=question,
            route=route_result.route,
            answer_preview=answer_preview,
        )

    return {
        "role": "assistant",
        "content": content,
        "artifact": artifact,
    }


initialize_chat_state()

sidebar_state = build_sidebar()
uploaded_file = sidebar_state["uploaded_file"]

st.title("Spreadsheet Agent Chat")
st.caption(
    "Chat-based spreadsheet analysis using deterministic Python agents and optional local LLM explanations."
)

if uploaded_file is None:
    st.info("Upload a CSV or Excel file from the sidebar to start.")
    st.stop()

try:
    result = pipeline.run(uploaded_file)

    df = result.dataframe
    metadata = result.metadata
    normalization_report = result.normalization_report
    profile = result.profile

    with st.expander("Dataset overview", expanded=True):
        st.subheader("Dataset Status")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Rows", profile["shape"]["rows"])

        with col2:
            st.metric("Columns", profile["shape"]["columns"])

        with col3:
            st.metric("Duplicate rows", profile["duplicate_rows"])

        with col4:
            missing_total = sum(profile.get("missing_values", {}).values())
            st.metric("Missing values", missing_total)

        st.subheader("Preview")
        st.dataframe(df.head(20), use_container_width=True)

        with st.expander("Metadata", expanded=False):
            st.json(metadata)

        with st.expander("Normalization report", expanded=False):
            st.json(normalization_report)

        with st.expander("Full dataset profile", expanded=False):
            st.json(profile)

    with st.expander("Example prompts", expanded=False):
        st.markdown(
            """
    **Direct analysis**
    - `show missing values`
    - `tell me about gross revenue`

    **Visualization**
    - `draw bar chart of gross revenue by region`

    **Code generation**
    - `write pandas code to group gross revenue by region`

    **Vietnamese**
    - `cho mình xem giá trị thiếu`
    - `vẽ biểu đồ gross revenue theo region`

    **Prompt guard tests**
    - `help me`
    - `tell me about profit margin`
    """
        )

    for message in st.session_state.messages:
        render_message(message)

    user_question = st.chat_input(
        "Ask about missing values, columns, charts, insights, code, or planning..."
    )
    if user_question:
        add_message("user", user_question)

        assistant_message = process_question(
            question=user_question,
            df=df,
            profile=profile,
            sidebar_state=sidebar_state,
            uploaded_file_name=getattr(uploaded_file, "name", "uploaded_dataset"),
        )

        st.session_state.messages.append(assistant_message)

        st.rerun()

except Exception as error:
    st.error("Failed to process file.")
    st.exception(error)