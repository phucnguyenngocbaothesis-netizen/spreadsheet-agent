# Week 6 Checklist

## Sprint Goal

Implement a rule-based PlanningAgent that creates multi-step analysis workflows and maps each step to existing system agents.

## PlanningAgent

- [x] Implement PlanningAgent
- [x] Add PlanStep dataclass
- [x] Add PlanningResult dataclass
- [x] Create general EDA plan
- [x] Create cleaning plan
- [x] Create visualization plan
- [x] Create codegen / SQL plan
- [x] Add planning metadata
- [x] Add markdown formatting
- [x] Add unit tests

## Supported Plan Types

- [x] General EDA plan
- [x] Cleaning / preprocessing plan
- [x] Visualization workflow
- [x] Codegen / SQL workflow

## Planning Metadata

- [x] Add `plan_type`
- [x] Add `estimated_difficulty`
- [x] Add `recommended_next_agent`
- [x] Add `assumptions`
- [x] Add `warnings`

## Agent Mapping

- [x] DatasetProfilerAgent
- [x] DirectAnalysisAgent
- [x] GenericNormalizerAgent
- [x] ChartBuilderAgent
- [x] EDAInsightAgent
- [x] CodegenSQLAgent
- [x] User review step

## Router Integration

- [x] Route planning requests to `PLANNING`
- [x] Add planning keywords
- [x] Prioritize workflow/plan requests over visualization route
- [x] Add router tests

## Streamlit UI

- [x] Display planning result
- [x] Render planning output as markdown
- [x] Show goal
- [x] Show plan type
- [x] Show estimated difficulty
- [x] Show recommended next agent
- [x] Show workflow steps

## Testing

- [x] Add PlanningAgent tests
- [x] Add planning metadata tests
- [x] Add planning markdown tests
- [x] Add planning router tests
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] LLM-assisted planning
- [ ] Executable workflow runner
- [ ] Automatic multi-agent execution
- [ ] PersonalizationAgent
- [ ] Ollama integration
- [ ] QLoRA fine-tuning