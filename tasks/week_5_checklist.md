# Week 5 Checklist

## Sprint Goal

Implement a rule-based CodegenSQLAgent that generates schema-grounded pandas and SQL templates without using an LLM.

## CodegenSQLAgent

- [x] Implement CodegenSQLAgent
- [x] Add CodegenResult dataclass
- [x] Add SchemaValidationResult dataclass
- [x] Generate pandas code
- [x] Generate SQL query
- [x] Add schema validation
- [x] Detect invalid mentioned columns
- [x] Add richer output metadata
- [x] Add unit tests

## Pandas Code Generation

- [x] Missing value summary
- [x] Numeric summary using `df.describe()`
- [x] Grouped aggregation using `groupby`
- [x] Data preview using `df.head()`
- [x] Fallback preview template

## SQL Query Generation

- [x] Missing value query using `CASE WHEN`
- [x] Grouped aggregation using `GROUP BY`
- [x] Preview query using `LIMIT 5`
- [x] Fallback SQL template

## Schema Validation

- [x] Validate existing columns
- [x] Detect invalid columns
- [x] Validate groupby categorical column
- [x] Validate groupby numeric column
- [x] Stop generation when requested columns do not exist

## Output Metadata

- [x] Add `generated_code_type`
- [x] Add `required_inputs`
- [x] Add `assumptions`
- [x] Add `warnings`
- [x] Display metadata in Streamlit

## Streamlit UI

- [x] Route code requests to `CODEGEN_SQL`
- [x] Show codegen metadata
- [x] Show generated pandas code
- [x] Show generated SQL query
- [x] Show schema warnings

## Testing

- [x] Add pandas codegen tests
- [x] Add SQL codegen tests
- [x] Add schema validation tests
- [x] Add invalid mentioned column tests
- [x] Add metadata tests
- [x] Run pytest successfully

## Not Implemented Yet

- [ ] LLM-based code generation
- [ ] Code execution sandbox
- [ ] SQL execution engine
- [ ] PlanningAgent
- [ ] PersonalizationAgent
- [ ] Ollama integration
- [ ] QLoRA fine-tuning