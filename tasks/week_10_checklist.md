# Week 10 Checklist

## Sprint Goal

Refine optional LLM explanations while keeping deterministic outputs as the source of truth.

## LLMExplanationAgent

- [x] Implement LLMExplanationAgent
- [x] Add LLMExplanationResult dataclass
- [x] Explain direct analysis results
- [x] Explain EDA insight results
- [x] Explain chart-grounded insights
- [x] Use deterministic output as grounding context
- [x] Add fallback when LLM is unavailable
- [x] Add fallback when selected model is invalid
- [x] Add fallback when generation fails
- [x] Add unit tests

## Prompt Refinement

- [x] Improve EDA explanation prompt
- [x] Improve chart explanation prompt
- [x] Add anti-hallucination rules
- [x] Require complete sentences
- [x] Require concise output
- [x] Add structured output format
- [x] Add prompt template tests

## Explanation Quality Checks

- [x] Detect empty LLM output
- [x] Detect overly short explanation
- [x] Detect overly long explanation
- [x] Detect possibly incomplete/cut-off explanation
- [x] Add quality warning tests

## Streamlit UI

- [x] Show LLM success metric
- [x] Show fallback-used metric
- [x] Show selected model metric
- [x] Show metadata in expander
- [x] Show warnings separately
- [x] Show explanation under clear heading
- [x] Keep deterministic result visible first

## Fallback Policy

- [x] Deterministic output is always shown first
- [x] LLM explanation is optional
- [x] LLM failure does not block app output
- [x] Invalid model does not crash app
- [x] Unavailable Ollama server does not crash app

## Testing

- [x] Add unavailable-server tests
- [x] Add invalid-model tests
- [x] Add successful-generation tests
- [x] Add failed-generation tests
- [x] Add chart-explanation tests
- [x] Add response-quality warning tests
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] LLM answer scoring
- [ ] LLM response comparison across models
- [ ] LLM-based code generation
- [ ] LLM-based planning
- [ ] Fine-tuning pipeline
- [ ] Human evaluation form