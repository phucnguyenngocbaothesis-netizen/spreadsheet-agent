# Week 5 Progress

## Sprint Goal

Week 5 focuses on adding a schema-grounded CodegenSQLAgent.

The goal is to generate simple pandas and SQL code templates from the uploaded dataset profile without using an LLM.

## Pipeline After Week 5

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
DirectAnalysisAgent / ChartBuilderAgent / EDAInsightAgent / CodegenSQLAgent
```

## Implemented Component

### CodegenSQLAgent

The CodegenSQLAgent generates rule-based code templates for common spreadsheet analysis requests.

It supports:

- pandas code generation
- SQL query generation
- schema validation
- invalid mentioned column detection
- structured codegen metadata

## Supported Pandas Requests

```txt
write pandas code to show missing values
write pandas code for numeric summary
write pandas code to group revenue by region
give me pandas preview code
```

Example output:

```python
grouped = df.groupby("region", as_index=False)["revenue"].sum()
grouped = grouped.sort_values("revenue", ascending=False)
grouped
```

## Supported SQL Requests

```txt
write SQL query to count missing values
write SQL query to group revenue by region
give me SQL preview query
```

Example output:

```sql
SELECT
    "region",
    SUM("revenue") AS "total_revenue"
FROM uploaded_table
GROUP BY "region"
ORDER BY "total_revenue" DESC;
```

## Schema Validation

The agent validates whether requested columns exist in the dataset schema.

Valid request:

```txt
write pandas code to group revenue by region
```

Result:

```txt
Generated pandas groupby code.
No warnings.
```

Invalid request:

```txt
write pandas code to group profit by region
```

Result:

```txt
Code generation stopped.
Warning: The requested column `profit` does not exist in the dataset.
```

## Codegen Result Metadata

Each generated result includes:

```txt
mode
generated_code_type
explanation
required_inputs
assumptions
warnings
code
```

This makes the output easier to inspect, test, and present in the report.

## Why This Is Still Rule-Based

This version does not use an LLM. It intentionally generates safe templates from known schema information.

This follows the project principle:

```txt
Python computes. LLM explains later.
```

Later, an LLM can be added to generate more flexible code, but only after schema validation and safety checks are already in place.

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
81 passed
```

If the number is different, the important condition is that all tests pass.

## Week 5 Status

Completed:

- CodegenSQLAgent
- Pandas code generation
- SQL query generation
- Schema validation
- Invalid mentioned column detection
- Rich codegen metadata
- Streamlit integration
- Unit tests

Next:

- PlanningAgent
- Multi-step workflow planning
- Route planning requests
- Map planning steps to existing agents