from agents.fast_router import FastRouterAgent


def test_fast_router_direct_analysis_missing_values():
    router = FastRouterAgent()

    result = router.route("show missing values")

    assert result.route == "DIRECT_ANALYSIS"
    assert result.confidence > 0
    assert "missing" in result.matched_keywords


def test_fast_router_direct_analysis_columns():
    router = FastRouterAgent()

    result = router.route("show column names")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_visualization():
    router = FastRouterAgent()

    result = router.route("draw a bar chart of revenue by product")

    assert result.route == "VISUALIZATION"


def test_fast_router_codegen_sql():
    router = FastRouterAgent()

    result = router.route("write pandas code to group revenue by region")

    assert result.route == "CODEGEN_SQL"


def test_fast_router_planning():
    router = FastRouterAgent()

    result = router.route("give me an analysis plan for this dataset")

    assert result.route == "PLANNING"


def test_fast_router_personalization():
    router = FastRouterAgent()

    result = router.route("explain this for beginner")

    assert result.route == "PERSONALIZATION"


def test_fast_router_cleaning():
    router = FastRouterAgent()

    result = router.route("clean this dataset and convert types")

    assert result.route == "CLEANING"


def test_fast_router_unknown():
    router = FastRouterAgent()

    result = router.route("hello there")

    assert result.route == "UNKNOWN"
    assert result.confidence == 0.0


def test_fast_router_direct_analysis_numeric_summary():
    router = FastRouterAgent()

    result = router.route("show numeric summary")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_direct_analysis_categorical_summary():
    router = FastRouterAgent()

    result = router.route("show categorical summary")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_direct_analysis_unique_values():
    router = FastRouterAgent()

    result = router.route("show unique values")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_direct_analysis_sample_rows():
    router = FastRouterAgent()

    result = router.route("show sample rows")

    assert result.route == "DIRECT_ANALYSIS"

def test_fast_router_visualization_distribution():
    router = FastRouterAgent()

    result = router.route("show distribution of revenue")

    assert result.route == "VISUALIZATION"


def test_fast_router_visualization_draw():
    router = FastRouterAgent()

    result = router.route("draw revenue by product")

    assert result.route == "VISUALIZATION"

def test_fast_router_planning_visualization_workflow():
    router = FastRouterAgent()

    result = router.route("create a visualization workflow")

    assert result.route == "PLANNING"


def test_fast_router_planning_next_steps():
    router = FastRouterAgent()

    result = router.route("what should I do next")

    assert result.route == "PLANNING"

def test_fast_router_personalization_concise():
    router = FastRouterAgent()

    result = router.route("make it concise")

    assert result.route == "PERSONALIZATION"


def test_fast_router_personalization_simple():
    router = FastRouterAgent()

    result = router.route("make it simple for beginner")

    assert result.route == "PERSONALIZATION"

def test_fast_router_schema_aware_column_question():
    router = FastRouterAgent()

    profile = {
        "columns": ["input_values", "expected_route"],
    }

    result = router.route(
        "tell me about the input values",
        profile,
    )

    assert result.route == "DIRECT_ANALYSIS"
    assert "column:input_values" in result.matched_keywords


def test_fast_router_schema_aware_describe_column():
    router = FastRouterAgent()

    profile = {
        "columns": ["revenue", "region"],
    }

    result = router.route(
        "describe revenue",
        profile,
    )

    assert result.route == "DIRECT_ANALYSIS"

def test_fast_router_loads_keywords_from_json_config(tmp_path):
    config_path = tmp_path / "route_keywords.json"
    config_path.write_text(
        """
{
  "DIRECT_ANALYSIS": ["custom_missing_keyword"],
  "VISUALIZATION": ["custom_chart_keyword"],
  "EDA_INSIGHT": ["custom_insight_keyword"],
  "CODEGEN_SQL": ["custom_code_keyword"],
  "PLANNING": ["custom_plan_keyword"],
  "PERSONALIZATION": ["custom_personal_keyword"]
}
""",
        encoding="utf-8",
    )

    router = FastRouterAgent(keyword_config_path=str(config_path))

    result = router.route("custom_missing_keyword")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_falls_back_when_keyword_json_missing():
    router = FastRouterAgent(keyword_config_path="missing_config.json")

    result = router.route("show missing values")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_supports_vietnamese_keywords_from_default_json():
    router = FastRouterAgent()

    result = router.route("cho mình xem giá trị thiếu")

    assert result.route == "DIRECT_ANALYSIS"

def test_fast_router_vietnamese_missing_values():
    router = FastRouterAgent()

    result = router.route("cho mình xem giá trị thiếu")

    assert result.route == "DIRECT_ANALYSIS"


def test_fast_router_vietnamese_chart():
    router = FastRouterAgent()

    result = router.route("vẽ biểu đồ doanh thu theo khu vực")

    assert result.route == "VISUALIZATION"


def test_fast_router_vietnamese_plan():
    router = FastRouterAgent()

    result = router.route("tạo kế hoạch phân tích dữ liệu")

    assert result.route == "PLANNING"


def test_fast_router_vietnamese_schema_column_question():
    router = FastRouterAgent()

    profile = {
        "columns": ["gross_revenue", "region"],
    }

    result = router.route(
        "cho mình biết về gross revenue",
        profile,
    )

    assert result.route == "DIRECT_ANALYSIS"
    assert "column:gross_revenue" in result.matched_keywords