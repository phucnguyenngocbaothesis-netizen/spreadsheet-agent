# Week 1 Demo Evidence

## Sprint Goal

Build the first working spreadsheet analysis pipeline that can upload a CSV/Excel file, load it into a dataframe, generate a compact dataset profile, and answer basic deterministic questions without using an LLM.

## Implemented Components

### 1. SmartLoaderAgent

Implemented features:

- Load CSV files
- Load Excel files
- Support single-sheet Excel files
- Detect likely header row
- Remove fully empty rows and columns
- Clean column names
- Restore basic numeric types

### 2. DatasetProfilerAgent

Implemented features:

- Detect dataset shape
- List column names
- Detect pandas data types
- Count missing values
- Calculate missing percentages
- Count duplicate rows
- Extract sample rows

### 3. DirectAnalysisAgent

Implemented features:

- Answer dataset shape questions
- Answer column name questions
- Answer data type questions
- Answer missing value questions
- Answer duplicate row questions

## Demo Dataset

File used:

```txt
data_samples/messy_header_sales.csv