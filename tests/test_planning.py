from agents.planning_agent import PlanningAgent


def make_profile():
    return {
        "shape": {
            "rows": 5,
            "columns": 4,
        },
        "columns": ["product", "region", "revenue", "order_date"],
        "dtypes": {
            "product": "object",
            "region": "object",
            "revenue": "float64",
            "order_date": "datetime64[ns]",
        },
        "missing_values": {
            "product": 0,
            "region": 0,
            "revenue": 1,
            "order_date": 0,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 0.0,
            "revenue": 20.0,
            "order_date": 0.0,
        },
        "duplicate_rows": 1,
    }


def test_planning_agent_creates_general_eda_plan():
    agent = PlanningAgent()

    result = agent.create_plan("give me an analysis plan", make_profile())

    assert result.goal
    assert len(result.steps) >= 3
    assert any(step.target_agent == "EDAInsightAgent" for step in result.steps)


def test_planning_agent_creates_cleaning_plan():
    agent = PlanningAgent()

    result = agent.create_plan("create a cleaning plan", make_profile())

    assert "cleaning" in result.goal.lower()
    assert any(step.target_agent == "GenericNormalizerAgent" for step in result.steps)
    assert result.warnings


def test_planning_agent_creates_visualization_plan():
    agent = PlanningAgent()

    result = agent.create_plan("create a visualization workflow", make_profile())

    assert "visualization" in result.goal.lower()
    assert any(step.target_agent == "ChartBuilderAgent" for step in result.steps)


def test_planning_agent_creates_codegen_plan():
    agent = PlanningAgent()

    result = agent.create_plan("create a pandas code workflow", make_profile())

    assert "code generation" in result.goal.lower()
    assert any(step.target_agent == "CodegenSQLAgent" for step in result.steps)


def test_planning_agent_steps_have_required_fields():
    agent = PlanningAgent()

    result = agent.create_plan("what should I do next", make_profile())

    for index, step in enumerate(result.steps, start=1):
        assert step.step_number == index
        assert step.title
        assert step.description
        assert step.target_agent
        assert step.expected_output

def test_planning_agent_formats_result_as_markdown():
    agent = PlanningAgent()

    result = agent.create_plan("give me an analysis plan", make_profile())
    markdown = agent.format_result_as_markdown(result)

    assert "## Planning Result" in markdown
    assert "Goal" in markdown
    assert "Workflow Steps" in markdown
    assert "Target agent" in markdown


def test_planning_agent_formats_warnings():
    agent = PlanningAgent()

    result = agent.create_plan("create a cleaning plan", make_profile())
    markdown = agent.format_result_as_markdown(result)

    assert "Warnings" in markdown
    assert "missing values" in markdown or "Duplicate rows" in markdown

def test_planning_agent_general_plan_metadata():
    agent = PlanningAgent()

    result = agent.create_plan("give me an analysis plan", make_profile())

    assert result.plan_type == "general_eda"
    assert result.estimated_difficulty
    assert result.recommended_next_agent == "EDAInsightAgent"


def test_planning_agent_cleaning_plan_metadata():
    agent = PlanningAgent()

    result = agent.create_plan("create a cleaning plan", make_profile())

    assert result.plan_type == "cleaning"
    assert result.recommended_next_agent == "DirectAnalysisAgent"


def test_planning_agent_visualization_plan_metadata():
    agent = PlanningAgent()

    result = agent.create_plan("create a visualization workflow", make_profile())

    assert result.plan_type == "visualization"
    assert result.recommended_next_agent == "ChartBuilderAgent"


def test_planning_agent_codegen_plan_metadata():
    agent = PlanningAgent()

    result = agent.create_plan("create a pandas code workflow", make_profile())

    assert result.plan_type == "codegen_sql"
    assert result.recommended_next_agent == "CodegenSQLAgent"


def test_planning_agent_markdown_includes_metadata():
    agent = PlanningAgent()

    result = agent.create_plan("give me an analysis plan", make_profile())
    markdown = agent.format_result_as_markdown(result)

    assert "Plan type" in markdown
    assert "Estimated difficulty" in markdown
    assert "Recommended next agent" in markdown