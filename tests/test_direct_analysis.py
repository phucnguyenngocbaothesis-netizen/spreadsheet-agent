from agents.direct_analysis import DirectAnalysisAgent


def make_profile():
    return {
        "shape": {
            "rows": 5,
            "columns": 3,
        },
        "columns": ["product", "region", "revenue"],
        "dtypes": {
            "product": "object",
            "region": "object",
            "revenue": "int64",
        },
        "missing_values": {
            "product": 0,
            "region": 1,
            "revenue": 2,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 20.0,
            "revenue": 40.0,
        },
        "duplicate_rows": 1,
        "sample_rows": [
            {
                "product": "Laptop",
                "region": "HCMC",
                "revenue": 1200,
            }
        ],
        "numeric_summary": {
            "revenue": {
                "count": 3,
                "mean": 550.0,
                "median": 300.0,
                "std": 567.89,
                "min": 150.0,
                "max": 1200.0,
            }
        },
        "categorical_summary": {
            "product": {
                "unique_count": 2,
                "top_values": {
                    "Laptop": 2,
                    "Mouse": 1,
                },
            },
            "region": {
                "unique_count": 2,
                "top_values": {
                    "HCMC": 2,
                    "Hanoi": 1,
                },
            },
        },
    }

def test_answer_shape():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show shape", make_profile())

    assert "5 rows" in answer
    assert "3 columns" in answer


def test_answer_columns():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show columns", make_profile())

    assert "product" in answer
    assert "region" in answer
    assert "revenue" in answer


def test_answer_missing_values():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show missing values", make_profile())

    assert "region" in answer
    assert "revenue" in answer
    assert "40.0%" in answer


def test_answer_duplicates():
    agent = DirectAnalysisAgent()
    answer = agent.answer("duplicate rows", make_profile())

    assert "1 duplicate rows" in answer

def test_answer_numeric_summary():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show numeric summary", make_profile())

    assert "revenue" in answer
    assert "Mean" in answer
    assert "Max" in answer


def test_answer_categorical_summary():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show categorical summary", make_profile())

    assert "product" in answer
    assert "Laptop" in answer
    assert "Unique values" in answer


def test_answer_sample_rows():
    agent = DirectAnalysisAgent()
    answer = agent.answer("show sample rows", make_profile())

    assert "Laptop" in answer
    assert "HCMC" in answer

def test_answer_column_summary_for_numeric_column():
    agent = DirectAnalysisAgent()

    profile = make_profile()

    answer = agent.answer("tell me about revenue", profile)

    assert "Column summary" in answer
    assert "revenue" in answer
    assert "numeric" in answer
    assert "Mean" in answer or "Mean:" in answer


def test_answer_column_summary_with_spaces_matches_underscore_column():
    agent = DirectAnalysisAgent()

    profile = {
        "shape": {
            "rows": 3,
            "columns": 1,
        },
        "columns": ["input_values"],
        "dtypes": {
            "input_values": "object",
        },
        "missing_values": {
            "input_values": 0,
        },
        "missing_percentage": {
            "input_values": 0.0,
        },
        "duplicate_rows": 0,
        "sample_rows": [
            {"input_values": "show missing values"},
            {"input_values": "draw chart"},
        ],
        "numeric_summary": {},
        "categorical_summary": {
            "input_values": {
                "unique_count": 2,
                "top_values": {
                    "show missing values": 1,
                    "draw chart": 1,
                },
            }
        },
    }

    answer = agent.answer("tell me about the input values", profile)

    assert "Column summary" in answer
    assert "input_values" in answer
    assert "categorical" in answer
    assert "show missing values" in answer