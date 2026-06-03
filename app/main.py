from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from agents.direct_analysis import DirectAnalysisAgent
from core.pipeline import SpreadsheetPipeline
from agents.fast_router import FastRouterAgent
from agents.chart_builder import ChartBuilderAgent
from agents.eda_insight import EDAInsightAgent
from agents.codegen_sql import CodegenSQLAgent
from agents.planning_agent import PlanningAgent

st.set_page_config(
    page_title="Spreadsheet Agent - Week 1",
    layout="wide",
)

st.title("Spreadsheet Agent - Week 1 Prototype")

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

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
)

pipeline = SpreadsheetPipeline()
direct_analysis_agent = DirectAnalysisAgent()
fast_router_agent = FastRouterAgent()
chart_builder_agent = ChartBuilderAgent()
eda_insight_agent = EDAInsightAgent()
codegen_sql_agent = CodegenSQLAgent()
planning_agent = PlanningAgent()

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
        route_result = fast_router_agent.route(question)

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
            answer = direct_analysis_agent.answer(question, profile)
            st.markdown(answer)
        elif route_result.route == "VISUALIZATION":
            try:
                chart_result = chart_builder_agent.build_chart(question, df)

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

                st.subheader("Chart Insights")
                st.markdown(eda_insight_agent.format_result_as_markdown(chart_insight_result))

            except Exception as chart_error:
                st.error("Failed to build chart.")
                st.error(str(chart_error))

        elif route_result.route == "EDA_INSIGHT":
            insight_result = eda_insight_agent.generate_insights(profile)

            st.subheader("EDA Insight Result")
            st.markdown(eda_insight_agent.format_result_as_markdown(insight_result))

        elif route_result.route == "CODEGEN_SQL":
            codegen_result = codegen_sql_agent.generate(question, profile)

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

            st.subheader("Planning Result")
            st.markdown(planning_agent.format_result_as_markdown(planning_result))

            for step in planning_result.steps:
                with st.expander(f"Step {step.step_number}: {step.title}"):
                    st.write(step.description)
                    st.json(
                        {
                            "target_agent": step.target_agent,
                            "expected_output": step.expected_output,
                        }
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