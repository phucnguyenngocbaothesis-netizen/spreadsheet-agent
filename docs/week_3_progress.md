# Week 3 Progress

## Sprint Goal

Week 3 focuses on implementing deterministic chart generation before adding LLM-based explanation.

The goal is to allow the system to route visualization requests to a ChartBuilderAgent and generate charts using Python.

## Pipeline After Week 3

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
DirectAnalysisAgent or ChartBuilderAgent
```

## Implemented Component

### ChartBuilderAgent

The ChartBuilderAgent performs two separate tasks:

```txt
User question + dataframe
    ↓
recommend_chart()
    ↓
ChartRecommendation
    ↓
build_chart()
    ↓
ChartResult
```

This separation makes the visualization pipeline easier to test, debug, and explain in the report.

## Supported Chart Types

| Data Pattern | Chart Type |
|---|---|
| One categorical column + one numeric column | Bar chart |
| One datetime column + one numeric column | Line chart |
| Two numeric columns | Scatter plot |
| One numeric column | Histogram |

## Example Questions

```txt
draw bar chart of revenue by product
show line chart of revenue over order date
show scatter plot of quantity and revenue
show histogram of revenue
show distribution of revenue
```

## ChartBuilderAgent Output

Each chart result includes:

```txt
figure
chart_type
x_column
y_column
chart_data
reason
```

The `chart_data` output is important because future EDA insight generation should explain charts using the exact dataframe values, not visual image inspection.

## Streamlit Integration

The UI now displays:

- Route result
- Chart metadata
- Rendered chart
- Chart data used for rendering

## Error Handling

Implemented readable errors for invalid chart requests:

- Histogram without numeric columns
- Scatter plot with fewer than two numeric columns
- Line chart without datetime or numeric columns
- Bar chart without categorical or numeric columns

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
50 passed
```

If the number is different, the important condition is that all tests pass.

## Week 3 Status

Completed:

- ChartBuilderAgent
- ChartRecommendation
- ChartResult
- Chart rendering
- Chart data output
- Visualization routing
- Chart error handling
- Unit tests

Next:

- EDAInsightAgent
- Data-grounded chart explanation
- Rule-based insight generation
- Optional LLM-assisted explanation later