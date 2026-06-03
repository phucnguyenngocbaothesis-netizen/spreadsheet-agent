# Week 2 Progress

## Sprint Goal

Improve the spreadsheet pipeline by adding data normalization, rule-based routing, stronger direct analysis, and integration tests without using an LLM.

## Pipeline After Week 2

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
DirectAnalysisAgent or future agents
```

## Implemented Components

### 1. GenericNormalizerAgent

The normalizer converts common spreadsheet string formats into usable dataframe types.

Implemented conversions:

```txt
"1,200"       -> 1200
"15%"         -> 0.15
"2026-01-01"  -> datetime
""            -> missing value
```

Implemented features:

- Standardize column names
- Replace empty strings with missing values
- Remove fully empty rows and columns
- Convert numeric strings to numbers
- Convert percentage strings to decimal numbers
- Convert date-like strings to datetime
- Keep text columns unchanged

### 2. FastRouterAgent

The router classifies user questions into execution routes.

Current routes:

```txt
DIRECT_ANALYSIS
VISUALIZATION
CODEGEN_SQL
PLANNING
PERSONALIZATION
CLEANING
EDA_INSIGHT
UNKNOWN
```

Example routes:

```txt
show missing values                  -> DIRECT_ANALYSIS
show numeric summary                 -> DIRECT_ANALYSIS
draw a bar chart                     -> VISUALIZATION
write pandas code                    -> CODEGEN_SQL
give me an analysis plan             -> PLANNING
explain this for beginner            -> PERSONALIZATION
clean this dataset                   -> CLEANING
find insights                        -> EDA_INSIGHT
```

### 3. DatasetProfilerAgent Upgrade

The profiler now generates:

- Shape
- Column names
- Data types
- Missing values
- Missing percentages
- Duplicate row count
- Sample rows
- Numeric summary
- Categorical summary
- Top categorical values

### 4. DirectAnalysisAgent Upgrade

The direct analysis agent now answers:

```txt
show shape
show columns
show data types
show missing values
duplicate rows
show numeric summary
show categorical summary
show unique values
show sample rows
```

### 5. Pipeline Integration Tests

Added integration tests for:

- Messy CSV header detection
- Mixed data type normalization
- Numeric summary generation
- Categorical summary generation
- Duplicate row detection

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
35 passed
```

## Week 2 Status

Completed:

- GenericNormalizerAgent
- FastRouterAgent
- Improved DatasetProfilerAgent
- Improved DirectAnalysisAgent
- Streamlit route display
- Unit tests
- Integration tests

Not implemented yet:

- ChartBuilderAgent
- EDAInsightAgent with LLM
- CodegenSQLAgent
- PlanningAgent
- PersonalizationAgent
- Ollama integration
- QLoRA fine-tuning