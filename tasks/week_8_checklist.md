# Week 8 Checklist

## Sprint Goal

Prepare optional local LLM integration while keeping the system fully functional through deterministic fallback behavior.

## LocalLLMClient

- [x] Implement LocalLLMClient
- [x] Add LLMResponse dataclass
- [x] Add LLMStatus dataclass
- [x] Add Ollama availability check
- [x] Add local generation request
- [x] Add empty prompt handling
- [x] Add request error fallback
- [x] Add status metadata
- [x] Add unit tests

## Prompt Templates

- [x] Add EDA explanation prompt template
- [x] Add chart explanation prompt template
- [x] Add anti-hallucination instruction
- [x] Include deterministic result in prompt
- [x] Include dataset profile metadata in prompt
- [x] Add unit tests

## Streamlit Integration

- [x] Add optional LLM explanation toggle
- [x] Add local model name input
- [x] Add LLM status panel
- [x] Add fallback warning when LLM is unavailable
- [x] Add optional direct analysis explanation
- [x] Add optional EDA insight explanation
- [x] Add optional chart explanation

## Fallback Behavior

- [x] Deterministic output still works when LLM is disabled
- [x] Deterministic output still works when LLM server is unavailable
- [x] App does not crash when Ollama is not running
- [x] LLM failure displays warning instead of blocking output

## Testing

- [x] Test prompt building
- [x] Test empty prompt handling
- [x] Test unavailable local server fallback
- [x] Test generation request fallback
- [x] Test LLM status when unavailable
- [x] Test LLM status when available
- [x] Test prompt templates
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] Mandatory LLM inference
- [ ] LLM-based code generation
- [ ] LLM-based planning
- [ ] Ollama model management UI
- [ ] QLoRA fine-tuning
- [ ] GGUF conversion