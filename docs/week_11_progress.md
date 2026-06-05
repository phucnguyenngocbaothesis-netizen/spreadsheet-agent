# Week 11 Progress

## Sprint Goal

Week 11 focuses on evaluation, routing robustness, prompt quality handling, bilingual input support, and lightweight persistent memory.

The system now includes component-level evaluation and stronger input handling before moving into Week 12 UI/demo polishing.

## Implemented Components

### Evaluation Framework

The project now includes evaluation scripts for:

```txt
routing
normalization
chart recommendation
codegen validation
prompt quality
combined evaluation summary
```

Evaluation outputs are saved into:

```txt
evaluation/outputs/
```

The combined runner is:

```cmd
python evaluation\run_all_evaluations.py
```

## Router Improvements

The router now supports:

```txt
rule-based keyword routing
schema-aware column routing
JSON-configurable route keywords
Vietnamese keyword routing
optional LLM route fallback
```

Routing keywords are stored in:

```txt
config/route_keywords.json
```

This makes the router easier to extend without modifying Python logic.

## Schema-Aware Routing

The router can now handle natural column questions such as:

```txt
tell me about region
describe gross revenue
cho mình biết về gross revenue
```

If the mentioned column exists in the dataset profile, the route becomes:

```txt
DIRECT_ANALYSIS
```

## Prompt Quality Guard

The PromptQualityAgent detects problematic prompts before routing.

It handles:

```txt
empty prompts
vague prompts
multi-intent prompts
unsupported requests
```

Examples:

```txt
help me
show missing values and draw chart
train a model to predict revenue
```

Instead of routing these directly, the app returns a safer clarification message and suggested prompts.

## Bilingual Support

The system now supports basic English/Vietnamese input.

Implemented:

```txt
LanguageUtils
Vietnamese router keywords
Vietnamese DirectAnalysis outputs
language-aware LLM explanation prompts
```

Example Vietnamese prompts:

```txt
cho mình xem giá trị thiếu
cho mình xem tên cột
cho mình biết về gross revenue
vẽ biểu đồ gross revenue theo region
```

## Query-Aware Table Context

The TableContextAgent selects relevant table columns based on the user question.

It supports:

```txt
column relevance scoring
selected columns
dropped columns
sample rows
compact context formatting
```

This context is used to ground optional LLM explanations.

## Persistent Memory

The system now uses SQLite for lightweight persistent memory.

Stored data:

```txt
user profile
recent questions
route history
answer preview
```

This is not a vector database. Semantic vector memory is left as future work.

## Chat-Style UI

A temporary ChatGPT-style UI was added:

```cmd
streamlit run app\chat_main.py
```

It supports:

```txt
scrollable chat history in the current session
sidebar upload/settings/profile
chat_input
assistant/user message bubbles
chart/code/planning artifacts inside messages
```

The old app remains available:

```cmd
streamlit run app\main.py
```

## Evaluation Command

Run:

```cmd
pytest
python evaluation\run_all_evaluations.py
```

Expected output should include evaluation rows similar to:

```txt
routing
normalization
chart_recommendation
codegen_validation
prompt_quality
```

The exact number of cases may differ as evaluation cases are expanded.

## Week 11 Status

Completed:

```txt
Evaluation framework
Schema-aware routing
JSON router config
Bilingual routing
Language-aware LLM explanations
Query-aware table context
SQLite persistent memory
Prompt quality guard
Temporary chat-style UI
```

Next:

```txt
Week 12: UI polish + demo evidence
```