import sys
from pathlib import Path

import streamlit as st
from core.language_utils import LanguageUtils

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from storage.sqlite_store import SQLiteStore

from agents.llm_explanation_agent import LLMExplanationAgent
from llm.model_utils import ModelUtils
from llm.local_llm_client import LocalLLMClient
from llm.prompt_templates import PromptTemplates
from agents.direct_analysis import DirectAnalysisAgent
from core.pipeline import SpreadsheetPipeline
from agents.fast_router import FastRouterAgent
from agents.chart_builder import ChartBuilderAgent
from agents.eda_insight import EDAInsightAgent
from agents.codegen_sql import CodegenSQLAgent
from agents.planning_agent import PlanningAgent
from agents.personalization_agent import PersonalizationAgent

pipeline = SpreadsheetPipeline()
direct_analysis_agent = DirectAnalysisAgent()
fast_router_agent = FastRouterAgent()
chart_builder_agent = ChartBuilderAgent()
eda_insight_agent = EDAInsightAgent()
codegen_sql_agent = CodegenSQLAgent()
planning_agent = PlanningAgent()
personalization_agent = PersonalizationAgent()
sqlite_store = SQLiteStore()

@st.cache_data(ttl=30)
def get_cached_llm_models() -> list[str]:
    client = LocalLLMClient()
    return client.list_models()

st.set_page_config(
    page_title="Spreadsheet Agent",
    layout="wide",
)

st.title("Spreadsheet Agent")

st.markdown(
    """
This prototype supports:
- CSV upload
- Excel upload
- Single-sheet reading
- Basic dataset profiling
- Deterministic direct answers without LLM
"""
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

st.sidebar.header("Recent Questions")

recent_history = sqlite_store.load_recent_chat_history(
    user_id=user_id,
    limit=5,
)

if not recent_history:
    st.sidebar.caption("No recent questions yet.")
else:
    for message in recent_history:
        st.sidebar.markdown(
            f"- `{message.route}`: {message.question}"
        )

if st.sidebar.button("Clear Chat History"):
    sqlite_store.clear_chat_history(user_id)
    st.sidebar.success("Chat history cleared.")
    st.rerun()

user_profile = personalization_agent.create_profile(
    role=user_role,
    technical_level=technical_level,
    response_style=response_style,
    preferred_format=preferred_format,
)
apply_personalization = st.sidebar.checkbox(
    "Apply personalization to text outputs",
    value=False,
)


def render_text_output(title: str, content: str) -> None:
    st.subheader(title)

    if not apply_personalization:
        st.markdown(content)
        return

    personalization_result = personalization_agent.personalize_response(
        content=content,
        profile=user_profile,
    )

    st.json(
        {
            "profile": personalization_agent.summarize_profile(user_profile),
            "applied_rules": personalization_result.applied_rules,
            "warnings": personalization_result.warnings,
        }
    )

    st.markdown(personalization_result.personalized_content)
 
def render_optional_llm_explanation(
    title: str,
    explanation_result,
) -> None:
    if not enable_llm_explanation:
        return

    st.subheader(title)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "LLM Success",
            "Yes" if explanation_result.success else "No",
        )

    with col2:
        st.metric(
            "Fallback Used",
            "Yes" if explanation_result.fallback_used else "No",
        )

    with col3:
        st.metric(
            "Model",
            explanation_result.model,
        )

    with st.expander("LLM Metadata"):
        st.json(
            {
                "success": explanation_result.success,
                "source": explanation_result.source,
                "model": explanation_result.model,
                "fallback_used": explanation_result.fallback_used,
                "prompt_type": explanation_result.prompt_type,
                "error": explanation_result.error,
            }
        )

    if explanation_result.warnings:
        st.warning("LLM warnings detected.")
        for warning in explanation_result.warnings:
            st.write(f"- {warning}")

    if explanation_result.fallback_used:
        st.warning(explanation_result.explanation)
        return

    st.markdown("### LLM Explanation")
    st.markdown(explanation_result.explanation)

st.sidebar.header("LLM Settings")

enable_llm_explanation = st.sidebar.checkbox(
    "Enable optional LLM explanation",
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


if enable_llm_explanation:
    llm_status = local_llm_client.get_status()
    llm_model_validation = local_llm_client.validate_model()

    st.sidebar.json(
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
else:
    llm_status = None

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
)
if uploaded_file is None:
    st.info("Upload a CSV or Excel file to start.")
    st.stop()

try:
    result = pipeline.run(uploaded_file)

    df = result.dataframe
    metadata = result.metadata
    normalization_report = result.normalization_report
    profile = result.profile

    st.success("File loaded successfully.")

    st.subheader("File Metadata")
    st.json(metadata)
    
    st.subheader("Normalization Report")
    st.json(normalization_report)

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", profile["shape"]["rows"])

    with col2:
        st.metric("Columns", profile["shape"]["columns"])

    with col3:
        st.metric("Duplicate Rows", profile["duplicate_rows"])

    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Column Data Types")
    st.json(profile["dtypes"])

    st.subheader("Missing Values")
    st.json(profile["missing_values"])

    st.subheader("Ask a Basic Question")

    question = st.text_input(
        "Example: show shape, show columns, show data types, missing values, duplicate rows"
    )

    if question:
        detected_language = LanguageUtils.detect_language(question)
        route_result = fast_router_agent.route(question, profile)
        answer_preview = ""

        st.subheader("Route Result")
        st.json(
            {
                "route": route_result.route,
                "confidence": route_result.confidence,
                "matched_keywords": route_result.matched_keywords,
                "reason": route_result.reason,
            }
        )

        if route_result.route == "DIRECT_ANALYSIS":
            answer = direct_analysis_agent.answer(
                question,
                profile,
                language=detected_language,
            )
            answer_preview = answer
            render_text_output("Direct Analysis Result", answer)

            llm_explanation_result = llm_explanation_agent.explain_eda_result_with_table_context(
                user_question=question,
                deterministic_result=answer,
                df=df,
                profile=profile,
            )

            render_optional_llm_explanation(
                title="Optional LLM Explanation",
                explanation_result=llm_explanation_result,
            )               

        elif route_result.route == "VISUALIZATION":
            try:
                chart_result = chart_builder_agent.build_chart(question, df)
                answer_preview = (
                    f"Created {chart_result.chart_type} chart with "
                    f"x={chart_result.x_column}, y={chart_result.y_column}."
                )
                st.subheader("Chart Result")
                st.json(
                    {
                        "chart_type": chart_result.chart_type,
                        "x_column": chart_result.x_column,
                        "y_column": chart_result.y_column,
                        "reason": chart_result.reason,
                    }
                )

                st.pyplot(chart_result.figure)
                
                st.subheader("Chart Data")
                st.dataframe(chart_result.chart_data, use_container_width=True)
                chart_insight_result = eda_insight_agent.generate_chart_insights(
                    chart_type=chart_result.chart_type,
                    chart_data=chart_result.chart_data,
                    x_column=chart_result.x_column,
                    y_column=chart_result.y_column,
                )

                chart_insight_markdown = eda_insight_agent.format_result_as_markdown(
                    chart_insight_result
                )

                render_text_output("Chart Insights", chart_insight_markdown)
                chart_metadata = {
                    "chart_type": chart_result.chart_type,
                    "x_column": chart_result.x_column,
                    "y_column": chart_result.y_column,
                    "reason": chart_result.reason,
                }

                llm_explanation_result = llm_explanation_agent.explain_chart_result(
                    user_question=question,
                    chart_metadata=chart_metadata,
                    chart_insights_markdown=chart_insight_markdown,
                )

                render_optional_llm_explanation(
                    title="Optional LLM Chart Explanation",
                    explanation_result=llm_explanation_result,
                )
            except Exception as chart_error:
                st.error("Failed to build chart.")
                st.error(str(chart_error))

        elif route_result.route == "EDA_INSIGHT":
            insight_result = eda_insight_agent.generate_insights(profile)
            insight_markdown = eda_insight_agent.format_result_as_markdown(insight_result)
            answer_preview = insight_markdown

            render_text_output("EDA Insights Results", insight_markdown)

            llm_explanation_result = llm_explanation_agent.explain_eda_result_with_table_context(
                user_question=question,
                deterministic_result=insight_markdown,
                df=df,
                profile=profile,
            )

            render_optional_llm_explanation(
                title="Optional LLM Insight Explanation",
                explanation_result=llm_explanation_result,
            )

        elif route_result.route == "CODEGEN_SQL":
            codegen_result = codegen_sql_agent.generate(question, profile)
            answer_preview = codegen_result.explanation

            st.subheader("Codegen / SQL Result")

            st.json(
                {
                    "mode": codegen_result.mode,
                    "generated_code_type": codegen_result.generated_code_type,
                    "explanation": codegen_result.explanation,
                    "required_inputs": codegen_result.required_inputs,
                    "assumptions": codegen_result.assumptions,
                    "warnings": codegen_result.warnings,
                }
            )

            language = "sql" if codegen_result.mode == "sql" else "python"
            st.code(codegen_result.code, language=language)

        elif route_result.route == "PLANNING":
            planning_result = planning_agent.create_plan(question, profile)
            planning_markdown = planning_agent.format_result_as_markdown(planning_result)
            answer_preview = planning_markdown

            render_text_output("Planning Result", planning_markdown)

            for step in planning_result.steps:
                with st.expander(f"Step {step.step_number}: {step.title}"):
                    st.write(step.description)
                    st.json(
                        {
                            "target_agent": step.target_agent,
                            "expected_output": step.expected_output,
                        }
                    )

        elif route_result.route == "PERSONALIZATION":
            base_content = (
                "This dataset has "
                f"{profile['shape']['rows']} rows and {profile['shape']['columns']} columns. "
                "The system can inspect missing values, duplicate rows, numeric summaries, "
                "categorical summaries, charts, EDA insights, code generation, and analysis plans."
            )

            personalization_result = personalization_agent.personalize_response(
                content=base_content,
                profile=user_profile,
            )
            answer_preview = personalization_result.personalized_content


            st.subheader("Personalization Result")

            st.json(
                {
                    "profile": personalization_agent.summarize_profile(user_profile),
                    "applied_rules": personalization_result.applied_rules,
                    "warnings": personalization_result.warnings,
                }
            )

            st.markdown(personalization_result.personalized_content)

        dataset_name = getattr(uploaded_file, "name", "uploaded_dataset")

        if answer_preview:
            sqlite_store.save_chat_message(
                user_id=user_id,
                dataset_name=dataset_name,
                question=question,
                route=route_result.route,
                answer_preview=answer_preview,
            )

        else:
            st.info(
                f"Route `{route_result.route}` detected, but this route is not implemented yet."
            )

    with st.expander("Full Dataset Profile"):
        st.json(profile)

except Exception as error:
    st.error("Failed to process file.")
    st.exception(error)