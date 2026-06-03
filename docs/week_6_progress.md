# Week 6 Progress

## Sprint Goal

Week 6 focuses on adding a rule-based PlanningAgent.

The goal is to turn high-level user requests into structured workflow plans that map to existing agents in the system.

No LLM is used in Week 6.

## Pipeline After Week 6

```txt
Uploaded CSV/XLSX
    ↓
SmartLoaderAgent
    ↓
GenericNormalizerAgent
    ↓
DatasetProfilerAgent
    ↓
FastRouterAgent
    ↓
DirectAnalysisAgent / ChartBuilderAgent / EDAInsightAgent / CodegenSQLAgent / PlanningAgent
```

## Implemented Component

### PlanningAgent

The PlanningAgent creates multi-step workflows for dataset analysis.

Each plan contains:

```txt
goal
plan_type
estimated_difficulty
recommended_next_agent
steps
assumptions
warnings
```

Each step contains:

```txt
step_number
title
description
target_agent
expected_output
```

## Supported Plan Types

| User Request | Plan Type | Recommended Next Agent |
|---|---|---|
| give me an analysis plan | general_eda | EDAInsightAgent |
| create a cleaning plan | cleaning | DirectAnalysisAgent |
| create a visualization workflow | visualization | ChartBuilderAgent |
| create a pandas code workflow | codegen_sql | CodegenSQLAgent |

## Example Questions

```txt
give me an analysis plan
what should I do next?
create a cleaning plan
create a visualization workflow
create a pandas code workflow
create a SQL workflow
```

## Example Planning Output

```txt
Goal: General exploratory data analysis workflow.
Plan type: general_eda
Estimated difficulty: medium
Recommended next agent: EDAInsightAgent
```

Example steps:

```txt
1. Validate loaded dataset -> DatasetProfilerAgent
2. Check data quality -> DirectAnalysisAgent
3. Generate EDA insights -> EDAInsightAgent
4. Create visualizations -> ChartBuilderAgent
5. Generate reusable analysis code -> CodegenSQLAgent
```

## Why This Is Useful

The PlanningAgent connects the existing deterministic agents into a coherent workflow.

Instead of only answering one request, the system can now explain what should happen next and which agent should handle each step.

This supports the multi-agent design in the report while keeping the implementation lightweight and testable.

## Router Update

The FastRouterAgent now prioritizes planning requests when the user asks for:

```txt
plan
workflow
steps
next steps
roadmap
process
pipeline
```

This prevents requests like:

```txt
create a visualization workflow
```

from being incorrectly routed to `VISUALIZATION`.

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
95 passed
```

If the number is different, the important condition is that all tests pass.

## Week 6 Status

Completed:

- PlanningAgent
- PlanStep
- PlanningResult
- General EDA plan
- Cleaning plan
- Visualization plan
- Codegen / SQL plan
- Planning metadata
- Markdown formatting
- Streamlit integration
- Router priority update
- Unit tests

Next:

- PersonalizationAgent
- User profile schema
- Response style adaptation
- Technical-depth adaptation