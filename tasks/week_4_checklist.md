# Week 4 Checklist

## Sprint Goal

Implement EDAInsightAgent to generate rule-based dataset insights and chart-grounded insights without using an LLM.

## EDAInsightAgent

- [x] Implement EDAInsightAgent
- [x] Add Insight dataclass
- [x] Add EDAInsightResult dataclass
- [x] Generate dataset-level insights
- [x] Generate chart-grounded insights
- [x] Add severity levels
- [x] Add recommendations
- [x] Add markdown formatting
- [x] Add unit tests

## Dataset-Level Insights

- [x] Dataset overview
- [x] Missing value insights
- [x] Duplicate row insights
- [x] Numeric range insights
- [x] Categorical top-value insights

## Chart-Grounded Insights

- [x] Bar chart highest category
- [x] Bar chart lowest category
- [x] Line chart trend direction
- [x] Histogram distribution summary
- [x] Scatter plot correlation insight

## Severity Rules

- [x] Missing values below 20% -> info
- [x] Missing values from 20% to below 50% -> warning
- [x] Missing values 50% or above -> critical
- [x] Duplicate rows from 10% to below 50% -> warning
- [x] Duplicate rows 50% or above -> critical
- [x] Strong scatter correlation -> warning

## Streamlit UI

- [x] Show EDA insight result
- [x] Show chart insights after visualization
- [x] Render insights as markdown
- [x] Show recommendation and evidence

## Testing

- [x] Add EDA insight tests
- [x] Add chart insight tests
- [x] Add markdown formatting tests
- [x] Add severity rule tests
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] LLM-assisted insight explanation
- [ ] CodegenSQLAgent
- [ ] PlanningAgent
- [ ] PersonalizationAgent
- [ ] Ollama integration
- [ ] QLoRA fine-tuning