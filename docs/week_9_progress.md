# Week 9 Progress

## Sprint Goal

Week 9 focuses on validating Ollama runtime integration and improving local model selection.

The system can now detect available local Ollama models, validate the selected model, and show user-friendly model labels in Streamlit.

## Pipeline After Week 9

```txt
Uploaded CSV/XLSX
    ↓
Deterministic agents
    ↓
Optional LLM explanation layer
    ↓
Ollama availability check
    ↓
Model validation
    ↓
LLM explanation or deterministic fallback
```

## Implemented Components

### ModelValidationResult

The system now validates whether the selected model exists locally.

Each validation result contains:

```txt
is_valid
requested_model
available_models
message
```

### ModelUtils

The ModelUtils helper provides:

```txt
get_model_label()
get_model_recommendation()
format_model_option()
extract_model_name()
sort_models()
```

## Local Models Detected

The current Ollama setup includes:

```txt
my-qwen3-ft-q4:latest
my-qwen3-ft:latest
qwen3:4b
qwen3-8b-ctx2k:latest
qwen2.5:7b
qwen25-7b-ctx2k:latest
qwen3:8b
deepseek-r1:7b
llama3.1:8b
```

## Recommended Testing Order

```txt
qwen3:4b
my-qwen3-ft-q4:latest
qwen3:8b
llama3.1:8b
```

Rationale:

- `qwen3:4b` is lightweight and fast for local testing.
- `my-qwen3-ft-q4:latest` is useful for testing fine-tuned quantized behavior.
- `qwen3:8b` gives stronger output quality.
- `llama3.1:8b` is useful as a stable baseline.

## Streamlit Update

The sidebar now shows local models as readable dropdown options, for example:

```txt
qwen3:4b — Lightweight — Recommended for fast local testing.
my-qwen3-ft-q4:latest — Fine-tuned — Recommended for testing fine-tuned quantized behavior.
qwen3:8b — Balanced — Good balance between quality and speed.
```

## Fallback Behavior

The app still follows this policy:

```txt
If the LLM is unavailable, show deterministic output.
If the selected model is invalid, show warning.
Do not block rule-based agents.
Do not crash the app.
```

## Test Result

Command:

```cmd
pytest
```

Expected result:

```txt
126 passed
```

The exact number may differ if additional tests were added. The important condition is that all tests pass.

## Week 9 Status

Completed:

- Ollama model listing
- Model validation
- Cached model dropdown
- Model labels
- Model recommendations
- Streamlit LLM model selection
- Unit tests

Next:

- Week 10: LLM explanation refinement
- Prompt template improvements
- LLM response formatting
- Optional explanation quality checks