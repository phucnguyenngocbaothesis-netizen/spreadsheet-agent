# Week 7 Progress

## Sprint Goal

Week 7 focuses on adding rule-based personalization.

The system now adapts text outputs based on a manually configured user profile.

No LLM is used in Week 7.

## Pipeline After Week 7

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
DirectAnalysisAgent / ChartBuilderAgent / EDAInsightAgent / CodegenSQLAgent / PlanningAgent / PersonalizationAgent
```

## Implemented Component

### PersonalizationAgent

The PersonalizationAgent modifies text output based on user preferences.

Each profile contains:

```txt
role
technical_level
response_style
preferred_format
```

Each personalization result contains:

```txt
original_content
personalized_content
profile
applied_rules
warnings
```

## Supported User Profile Options

### Technical Level

| Value | Behavior |
|---|---|
| beginner | Adds beginner-friendly explanation |
| intermediate | Adds moderate explanation |
| advanced | Adds technical explanation |

### Response Style

| Value | Behavior |
|---|---|
| concise | Limits output length |
| balanced | Keeps normal output |
| detailed | Adds extra note |

### Preferred Format

| Value | Behavior |
|---|---|
| bullet | Keeps bullet-style output |
| paragraph | Converts output into paragraph style |
| step_by_step | Adds step-by-step framing |

## Streamlit Integration

The sidebar now includes:

```txt
Role
Technical level
Response style
Preferred format
Apply personalization to text outputs
```

When personalization is enabled, the system applies the selected profile to supported text outputs.

## Supported Personalized Outputs

- Direct analysis result
- EDA insight result
- Chart insights
- Planning result
- Standalone personalization response

## Example Questions

```txt
explain this for beginner
make it concise
make it technical and detailed
show missing values
find insights
create a visualization workflow
```

## Example Personalized Output

```txt
Beginner-friendly explanation:

The dataset has 5 rows and 4 columns.

In simple terms, this result helps you understand the dataset without needing advanced statistics.
```

## Why This Is Useful

Personalization improves usability for different user types.

A beginner user may need simpler explanations, while a technical user may prefer compact or detailed outputs with more analytical wording.

This supports the report goal of lightweight personalization without adding runtime-heavy user modeling.

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
107 passed
```

If the number is different, the important condition is that all tests pass.

## Week 7 Status

Completed:

- PersonalizationAgent
- Manual user profile
- Sidebar profile controls
- Personalized text rendering
- Standalone personalization route
- Router integration
- Unit tests

Next:

- LLM/Ollama integration preparation
- LLM client wrapper
- Optional EDA insight explanation through local model
- Prompt templates