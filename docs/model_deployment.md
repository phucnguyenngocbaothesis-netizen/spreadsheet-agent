# Local LLM Deployment Evidence

## Purpose

This project uses a hybrid architecture where deterministic Python agents compute spreadsheet results, while a local LLM is used only for optional explanation and fallback routing.

The LLM does not replace deterministic computation.

## Local Inference Backend

The prototype uses:

```txt
Ollama
Local model inference
No external API required

Available Local Models

The local machine currently has Ollama models available through:

ollama list

Example models may include:

qwen3:4b
qwen3:8b
qwen2.5:7b
llama3.1:8b
my-qwen3-ft-q4:latest

The exact list depends on the deployment machine.

Application Integration

The app connects to Ollama through:

llm/local_llm_client.py

Main responsibilities:

- Check whether Ollama is available
- List local models
- Validate selected model
- Generate optional explanations
- Handle LLM failures safely
Streamlit Model Selection

The UI supports local model selection in the sidebar.

If Ollama is unavailable or the selected model is invalid, the app falls back to deterministic outputs.

LLM Usage Policy

The system follows this rule:

Python computes.
LLM explains.

The LLM is used for:

- Optional EDA explanation
- Optional chart explanation
- Optional route fallback for UNKNOWN prompts

The LLM is not used as the source of truth for:

- Missing value counts
- Numeric summaries
- Duplicate rows
- Chart aggregation
- Schema validation
- Column validation
Safe Fallback Behavior

If the LLM fails, returns an empty response, or is unavailable:

- The app keeps the deterministic result
- The UI shows fallback metadata
- The system does not crash
- The LLM retry is limited to one attempt

Example fallback flow:

Deterministic result generated
→ LLM explanation requested
→ LLM returns empty response
→ Retry once with shorter prompt
→ If retry fails, show deterministic fallback explanation
Why Local LLM

Local LLM deployment helps with:

- Offline operation
- Lower privacy risk
- Lower external API dependency
- Better control over model selection
- Compatibility with lightweight deployment
Limitation

The current prototype does not require the LLM to succeed. Some small local models may return short or empty explanations. This is handled through deterministic fallback logic.

Future Work

Possible future improvements:

- Use a fine-tuned Qwen model as the default explanation model
- Add model quality comparison
- Add latency comparison between models
- Add prompt-level retry strategy by route type
- Add GGUF deployment documentation if needed

---

# 3. Tạo file `docs/evaluation_summary.md`

```md
# Evaluation Summary

## Purpose

The evaluation framework tests whether the spreadsheet agent behaves correctly across routing, normalization, chart recommendation, code generation, prompt quality, prompt stress, and latency/LLM-call reduction.

## Evaluation Commands

Run all unit tests:

```cmd
pytest

Run all evaluation scripts:

python evaluation\run_all_evaluations.py
Evaluation Modules

The project includes:

routing evaluation
normalization evaluation
chart recommendation evaluation
codegen validation evaluation
prompt quality evaluation
prompt stress evaluation
latency and LLM call reduction evaluation
Prompt Stress Evaluation

Prompt stress evaluation tests the system against:

- vague prompts
- multi-intent prompts
- unsupported prompts
- invalid-column prompts
- Vietnamese prompts
- mixed routing cases
- schema-aware column prompts

Latest result:

Total cases: 25
Correct cases: 25
Incorrect cases: 0
Accuracy: 1.0

This means the system handled all designed prompt stress cases correctly. It does not mean the system can handle every possible prompt perfectly.

LLM Call Reduction

The hybrid architecture avoids unnecessary LLM calls by using:

- rule-based routing
- deterministic Python agents
- schema-aware routing
- prompt quality guard
- column validation

The LLM is called only when optional explanation or route fallback is enabled.

Interpretation

The evaluation results support the main design claim:

A lightweight hybrid spreadsheet agent can handle many spreadsheet analysis tasks using deterministic Python agents, while using local LLMs only when helpful.
Limitations

The current evaluation does not yet include:

- full external benchmarks such as Spider, DS-1000, or TableBench
- large-scale real user studies
- full semantic vector memory evaluation
- full dashboard interaction evaluation

These are listed as future work.


---

# 4. Update README thêm docs links

Thêm vào `README.md`:

```md
## Documentation

Additional documentation:

```txt
docs/week_11_progress.md
docs/model_deployment.md
docs/evaluation_summary.md

These files summarize the evaluation framework, local LLM deployment, prompt robustness, and Week 11/12 progress.