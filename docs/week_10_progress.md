# Week 10 Progress

## Sprint Goal

Week 10 focuses on improving optional LLM explanations.

The deterministic agents remain the source of truth. The LLM is only used to explain deterministic outputs.

## Pipeline After Week 10

```txt
Uploaded CSV/XLSX
    ↓
Deterministic agents
    ↓
Deterministic result
    ↓
Optional LLMExplanationAgent
    ↓
LLM explanation or deterministic fallback
```

## Implemented Component

### LLMExplanationAgent

The LLMExplanationAgent wraps local LLM explanation behavior in a structured agent.

It supports:

```txt
explain_eda_result()
explain_chart_result()
```

Each explanation result contains:

```txt
success
explanation
source
model
fallback_used
error
prompt_type
warnings
```

## Supported Explanation Types

| Deterministic Output | Optional LLM Explanation |
|---|---|
| DirectAnalysisAgent result | EDA explanation |
| EDAInsightAgent result | EDA insight explanation |
| ChartBuilderAgent + chart insights | Chart explanation |

## Grounding Policy

The LLM is not allowed to invent new values.

Prompt rules include:

```txt
Do not invent numbers.
Do not add unsupported claims.
Only use the deterministic result and dataset profile.
Write complete sentences.
Keep the answer concise.
```

## Quality Checks

The system adds warnings if the explanation appears problematic.

Current checks:

```txt
empty output
too short
too long
possibly incomplete or cut off
```

These checks do not block the explanation. They only add warning metadata.

## Streamlit Integration

The UI now displays:

```txt
LLM Success
Fallback Used
Model
LLM Metadata
LLM Warnings
LLM Explanation
```

The deterministic output is still shown before the LLM output.

## Example

User asks:

```txt
show missing values
```

The system first returns deterministic output:

```txt
revenue: 1 missing values (25.0%)
```

Then, if LLM is enabled and available, it returns a grounded explanation using the selected local model.

## Fallback Behavior

If the LLM fails:

```txt
Deterministic output remains visible.
The LLM section shows fallback metadata.
The app does not crash.
```

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
133 passed
```

The exact number may differ if more tests were added. The important condition is that all tests pass.

## Week 10 Status

Completed:

- LLMExplanationAgent
- Structured explanation result
- Prompt refinement
- Explanation quality warnings
- Streamlit formatting
- Fallback-safe explanation layer
- Unit tests

Next:

- Week 11: Evaluation framework
- Routing evaluation
- Normalization evaluation
- Chart recommendation evaluation
- Codegen validation evaluation
- LLM fallback evaluation