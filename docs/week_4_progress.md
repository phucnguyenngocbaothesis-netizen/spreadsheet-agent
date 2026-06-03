# Week 4 Progress

## Sprint Goal

Week 4 focuses on adding rule-based EDA insight generation before introducing LLM-based explanation.

The system now generates insights from:

1. Dataset profile
2. Chart data

No LLM is used in Week 4.

## Pipeline After Week 4

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
DirectAnalysisAgent / ChartBuilderAgent / EDAInsightAgent
```

## Implemented Component

### EDAInsightAgent

The EDAInsightAgent generates rule-based analytical comments from structured data.

Main outputs:

```txt
summary
insights
severity
recommendation
evidence
```

## Dataset-Level Insights

The agent can detect:

- Dataset shape
- Missing values
- Duplicate rows
- Numeric ranges
- Most common categorical values

Example:

```txt
[WARNING] Missing values in `revenue`

The column `revenue` has 1 missing values (20.0%).

Recommendation:
Investigate why `revenue` has missing values. Depending on the analysis goal, consider imputation, row removal, or keeping missingness as a separate signal.
```

## Chart-Grounded Insights

The agent can also explain chart data directly.

| Chart Type | Insight |
|---|---|
| Bar chart | Highest and lowest category |
| Line chart | Trend direction |
| Histogram | Distribution range and mean |
| Scatter plot | Correlation between two numeric columns |

## Why Chart-Grounded Insight Matters

The system does not inspect the chart image. Instead, it explains the exact dataframe used to render the chart.

This follows the project principle:

```txt
Python computes. LLM explains later.
```

For now, Python both computes and generates simple rule-based explanation.

## Severity Rules

| Condition | Severity |
|---|---|
| Missing values < 20% | info |
| Missing values >= 20% and < 50% | warning |
| Missing values >= 50% | critical |
| Duplicate rows >= 10% and < 50% | warning |
| Duplicate rows >= 50% | critical |
| Strong scatter correlation | warning |

## Streamlit Integration

The UI now supports:

- `find insights`
- `analyze this dataset`
- chart request followed by chart-grounded insights

Example questions:

```txt
find insights
analyze this dataset
draw bar chart of revenue by product
show histogram of revenue
show scatter plot of quantity and revenue
```

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
63 passed
```

If the number is different, the important condition is that all tests pass.

## Week 4 Status

Completed:

- EDAInsightAgent
- Dataset-level rule-based insights
- Chart-grounded insights
- Severity rules
- Recommendations
- Markdown formatting
- Streamlit integration
- Unit tests

Next:

- CodegenSQLAgent skeleton
- Safe pandas code generation
- SQL query generation
- Schema-grounded code validation