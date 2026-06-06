# Defense Prompt Bank

## Purpose

This document lists prompt types that may appear during project defense and explains how the system handles them.

The goal is not to support every possible natural language prompt perfectly, but to make the system robust against common spreadsheet analysis requests, vague prompts, multi-intent prompts, invalid-column prompts, unsupported requests, and bilingual English/Vietnamese inputs.

---

## 1. Prompts the system handles well

### Direct analysis

```txt
show shape
show columns
show data types
show missing values
show duplicate rows
show numeric summary
show categorical summary
show sample rows
```

Vietnamese examples:

```txt
cho mình xem kích thước dataset
cho mình xem tên cột
cho mình xem kiểu dữ liệu
cho mình xem giá trị thiếu
cho mình xem dòng trùng lặp
```

Expected behavior:

```txt
Route: DIRECT_ANALYSIS
Agent: DirectAnalysisAgent
LLM: Not required
```

---

## 2. Schema-aware column questions

```txt
tell me about gross revenue
describe region
tell me about discount rate
tell me about profit
```

Vietnamese examples:

```txt
cho mình biết về gross revenue
cho mình biết về region
mô tả discount rate
```

Expected behavior:

```txt
Route: DIRECT_ANALYSIS
Reason: schema-aware column question
Agent: DirectAnalysisAgent
```

The router checks whether the mentioned column exists in the dataset profile.

---

## 3. Visualization prompts

```txt
draw bar chart of gross revenue by region
show histogram of profit
show line chart of gross revenue over order date
show scatter plot of shipping cost and profit
```

Vietnamese examples:

```txt
vẽ biểu đồ gross revenue theo region
vẽ phân phối của profit
vẽ scatter plot giữa shipping cost và profit
```

Expected behavior:

```txt
Route: VISUALIZATION
Agent: ChartBuilderAgent
LLM: Optional explanation only
```

If chart generation fails, the app returns a safe fallback message and suggested chart prompts.

---

## 4. Codegen / SQL prompts

```txt
write pandas code to group gross revenue by region
write pandas code to show missing values
write SQL query to group gross revenue by region
```

Vietnamese examples:

```txt
viết code pandas để nhóm gross revenue theo region
viết SQL query để nhóm gross revenue theo region
```

Expected behavior:

```txt
Route: CODEGEN_SQL
Agent: CodegenSQLAgent
Validation: schema validation before code generation
```

The system should not invent missing columns.

---

## 5. Planning prompts

```txt
create a cleaning plan
create an analysis plan
create a visualization workflow
what should I do next with this dataset?
```

Vietnamese examples:

```txt
tạo kế hoạch làm sạch dữ liệu
tạo kế hoạch phân tích dữ liệu
mình nên làm gì tiếp với dataset này?
```

Expected behavior:

```txt
Route: PLANNING
Agent: PlanningAgent
```

The system creates a step-by-step workflow.

---

## 6. Insight prompts

```txt
find insights in this dataset
analyze this dataset
find trends in this dataset
what patterns do you see?
```

Vietnamese examples:

```txt
tìm insight trong dataset này
phân tích dataset này
tìm xu hướng trong dữ liệu
```

Expected behavior:

```txt
Route: EDA_INSIGHT
Agent: EDAInsightAgent
```

The system provides deterministic insight based on the dataset profile.

---

## 7. Vague prompts

Examples:

```txt
help me
can you help me
tell me something
do something
```

Expected behavior:

```txt
Rejected by PromptQualityAgent
Reason: vague_prompt
```

The system suggests clearer prompts such as:

```txt
show missing values
tell me about gross revenue
draw bar chart of gross revenue by region
find insights in this dataset
create a cleaning plan
```

---

## 8. Multi-intent prompts

Examples:

```txt
show missing values and draw a chart
show missing values, write code, and create a cleaning plan
```

Vietnamese examples:

```txt
cho mình xem giá trị thiếu và vẽ biểu đồ doanh thu
kiểm tra missing rồi viết code pandas luôn
```

Expected behavior:

```txt
Rejected by PromptQualityAgent
Reason: multi_intent_prompt
```

Current prototype asks the user to run one task at a time.

Future work:

```txt
MultiIntentAgent
- split prompt into sub-tasks
- route each sub-task
- combine outputs
```

---

## 9. Unsupported prompts

Examples:

```txt
train a model to predict revenue
build a full dashboard
export cleaned Excel
forecast next month sales
```

Expected behavior:

```txt
Rejected by PromptQualityAgent
Reason: unsupported_request
```

The system explains that this is outside the current prototype scope and suggests alternatives:

```txt
create a data cleaning plan
create an analysis plan
write pandas code to prepare the dataset
show numeric summary
```

---

## 10. Invalid-column prompts

Examples:

```txt
tell me about profit margin
draw chart of net income by country
write pandas code to group customer satisfaction by month
```

Expected behavior:

```txt
Rejected by ColumnValidationAgent
Reason: mentioned columns do not exist in the dataset
```

The system suggests similar available columns when possible.

---

## 11. Prompt stress evaluation

The system includes a prompt stress evaluation set covering:

```txt
vague prompts
multi-intent prompts
unsupported prompts
invalid-column prompts
Vietnamese prompts
schema-aware prompts
visualization prompts
codegen prompts
planning prompts
insight prompts
```

Latest result:

```txt
Total cases: 25
Correct cases: 25
Incorrect cases: 0
Accuracy: 1.0
```

This means the system handled all designed stress-test prompts correctly.

It does not mean the system can handle every possible natural language prompt.

---

## 12. Safe fallback policy

The system follows this principle:

```txt
Python computes.
LLM explains.
```

If the LLM fails:

```txt
- deterministic output remains valid
- retry once if the LLM returns an empty response
- fallback to deterministic explanation
- do not recursively call agents
- do not invent numbers
```

---

## 13. Suggested defense answer

If asked how the system handles strange prompts:

```txt
The system uses a prompt quality guard before routing. It rejects vague, unsupported, or multi-intent prompts and suggests clearer alternatives. If the prompt is valid, the FastRouterAgent routes it to the correct deterministic agent. If a prompt mentions columns that do not exist, the ColumnValidationAgent catches it and suggests similar available columns. Optional LLM fallback is used only for route classification or explanation, not for deterministic computation.
```

---

## 14. Current limitations

The current prototype does not fully implement:

```txt
full multi-intent execution
full Power BI-style dashboard builder
model training
forecasting
export cleaned dataset
semantic vector memory
large-scale external benchmarks
```

These are listed as future work.