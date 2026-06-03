# Week 3 Checklist

## Sprint Goal

Implement the ChartBuilderAgent and enable the system to generate basic visualizations using deterministic Python logic.

## ChartBuilderAgent

- [x] Implement ChartBuilderAgent
- [x] Add ChartRecommendation dataclass
- [x] Add ChartResult dataclass
- [x] Separate chart recommendation from chart rendering
- [x] Return chart metadata
- [x] Return chart data used for rendering
- [x] Add unit tests

## Supported Charts

- [x] Bar chart
- [x] Line chart
- [x] Scatter plot
- [x] Histogram

## Chart Recommendation Rules

- [x] Categorical + numeric -> bar chart
- [x] Datetime + numeric -> line chart
- [x] Numeric + numeric -> scatter plot
- [x] One numeric column -> histogram

## Streamlit UI

- [x] Render matplotlib chart in Streamlit
- [x] Show chart type
- [x] Show selected x column
- [x] Show selected y column
- [x] Show recommendation reason
- [x] Show chart data

## Router Integration

- [x] Route chart requests to VISUALIZATION
- [x] Add keywords for chart, plot, visualize, graph
- [x] Add keywords for histogram, distribution, scatter, trend, draw
- [x] Add router tests

## Error Handling

- [x] Show clear error if histogram has no numeric column
- [x] Show clear error if scatter plot has fewer than two numeric columns
- [x] Show clear error if line chart lacks datetime or numeric columns
- [x] Show clear error if bar chart lacks categorical or numeric columns

## Testing

- [x] Add chart builder tests
- [x] Add chart recommendation tests
- [x] Add chart data output tests
- [x] Add chart error handling tests
- [x] Add visualization router tests
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] EDAInsightAgent
- [ ] LLM-based chart explanation
- [ ] CodegenSQLAgent
- [ ] PlanningAgent
- [ ] PersonalizationAgent
- [ ] Ollama integration
- [ ] QLoRA fine-tuning