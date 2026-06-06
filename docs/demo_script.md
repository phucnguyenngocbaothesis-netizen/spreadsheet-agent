# Demo Script

## Purpose

This document defines a stable demonstration flow for the spreadsheet agent prototype.

The demo should show:

- File upload
- Dataset profiling
- Direct deterministic analysis
- Schema-aware routing
- Visualization
- Code generation
- Planning
- Bilingual input
- Prompt quality guard
- Column validation guard
- Optional local LLM explanation and fallback
- Evaluation evidence

---

## App Command

Run the chat-style UI:

```cmd
streamlit run app\chat_main.py


Demo Dataset

Recommended dataset:

advanced_messy_sales_dataset.csv

This dataset contains:

messy header / metadata rows
mixed date formats
numeric strings
percentage strings
missing values
duplicate rows
negative profit values
categorical and numeric columns
Demo Flow
1. Upload dataset

Upload the demo dataset from the sidebar.

Expected:

Dataset overview appears
Rows / columns / duplicate rows are shown
Preview is visible
Full profile is available in expander
2. Direct deterministic analysis

Prompt:

show missing values

Expected:

Route: DIRECT_ANALYSIS
Missing value summary
No LLM required
3. Schema-aware column question

Prompt:

tell me about gross revenue

Expected:

Route: DIRECT_ANALYSIS
Reason: schema-aware column question
Column summary for gross_revenue
4. Visualization

Prompt:

draw bar chart of gross revenue by region

Expected:

Route: VISUALIZATION
Chart is rendered in chat
Chart data and metadata are available
5. Code generation

Prompt:

write pandas code to group gross revenue by region

Expected:

Route: CODEGEN_SQL
Generated pandas code
Schema validation passed
6. Planning

Prompt:

create a cleaning plan

Expected:

Route: PLANNING
Step-by-step workflow
Planning artifact shown in chat
7. Vietnamese input

Prompt:

cho mình xem giá trị thiếu

Expected:

Route: DIRECT_ANALYSIS
Vietnamese direct analysis output

Prompt:

vẽ biểu đồ gross revenue theo region

Expected:

Route: VISUALIZATION
Chart is generated
8. Prompt quality guard

Prompt:

help me

Expected:

Rejected by PromptQualityAgent
Reason: vague_prompt
Suggested prompts are shown

Prompt:

show missing values and draw bar chart of gross revenue by region

Expected:

Rejected by PromptQualityAgent
Reason: multi_intent_prompt
System asks user to run one task at a time
9. Column validation guard

Prompt:

tell me about profit margin

Expected:

Rejected by ColumnValidationAgent
Missing column detected
Similar available columns suggested
10. Optional LLM explanation

Enable:

Enable optional LLM explanation

Prompt:

tell me about gross revenue

Expected:

Deterministic result appears first
Optional LLM explanation appears below
If LLM fails, deterministic fallback explanation is shown
Evaluation Evidence

Run:

pytest
python evaluation\run_all_evaluations.py

Important evidence:

pytest passes
routing evaluation passes
prompt quality evaluation passes
prompt stress evaluation reaches 1.0 accuracy on designed test set
latency / LLM call reduction evaluation runs
Screenshots to Capture

Capture these screenshots for report/demo evidence:

Chat-style UI after uploading dataset
Dataset overview expander
show missing values
tell me about gross revenue
draw bar chart of gross revenue by region
write pandas code to group gross revenue by region
Vietnamese prompt: cho mình xem giá trị thiếu
Prompt quality rejection: help me
Multi-intent rejection
Invalid-column rejection
Optional LLM fallback metadata
Evaluation terminal output
Defense Explanation

The system follows this principle:

Python computes.
LLM explains.

The deterministic agents compute factual outputs such as missing values, data types, numeric summaries, charts, and schema validation.

The local LLM is only used for optional explanation or fallback routing. If the LLM fails, the deterministic result remains valid.

Known Limitations

Current prototype does not fully support:

full multi-intent execution
full dashboard builder
model training
forecasting
export cleaned datasets
vector database semantic memory
large-scale external benchmarks