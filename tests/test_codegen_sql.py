from agents.codegen_sql import CodegenSQLAgent


def make_profile():
    return {
        "shape": {
            "rows": 5,
            "columns": 4,
        },
        "columns": ["product", "region", "revenue", "quantity"],
        "dtypes": {
            "product": "object",
            "region": "object",
            "revenue": "float64",
            "quantity": "int64",
        },
        "missing_values": {
            "product": 0,
            "region": 0,
            "revenue": 1,
            "quantity": 0,
        },
        "missing_percentage": {
            "product": 0.0,
            "region": 0.0,
            "revenue": 20.0,
            "quantity": 0.0,
        },
        "duplicate_rows": 1,
        "sample_rows": [],
        "numeric_summary": {},
        "categorical_summary": {},
    }


def test_codegen_generates_pandas_groupby():
    agent = CodegenSQLAgent()

    result = agent.generate("write pandas code to group revenue by region", make_profile())

    assert result.mode == "pandas"
    assert "groupby" in result.code
    assert "region" in result.code
    assert "revenue" in result.code


def test_codegen_generates_pandas_missing_values():
    agent = CodegenSQLAgent()

    result = agent.generate("write pandas code to show missing values", make_profile())

    assert result.mode == "pandas"
    assert "isna" in result.code
    assert "missing_percentage" in result.code


def test_codegen_generates_pandas_describe():
    agent = CodegenSQLAgent()

    result = agent.generate("write pandas code for numeric summary", make_profile())

    assert result.mode == "pandas"
    assert "describe" in result.code


def test_codegen_generates_sql_groupby():
    agent = CodegenSQLAgent()

    result = agent.generate("write SQL query to group revenue by region", make_profile())

    assert result.mode == "sql"
    assert "SELECT" in result.code
    assert "GROUP BY" in result.code
    assert '"region"' in result.code
    assert '"revenue"' in result.code


def test_codegen_generates_sql_missing_values():
    agent = CodegenSQLAgent()

    result = agent.generate("write SQL query to count missing values", make_profile())

    assert result.mode == "sql"
    assert "CASE WHEN" in result.code
    assert "IS NULL" in result.code


def test_codegen_fallback_pandas_preview():
    agent = CodegenSQLAgent()

    result = agent.generate("give me code", make_profile())

    assert result.mode == "pandas"
    assert "df.head" in result.code
    assert result.warnings


def test_codegen_fallback_sql_preview():
    agent = CodegenSQLAgent()

    result = agent.generate("give me sql", make_profile())

    assert result.mode == "sql"
    assert "SELECT *" in result.code
    assert "LIMIT 5" in result.code

def test_codegen_validates_existing_columns():
    agent = CodegenSQLAgent()

    validation = agent.validate_columns(
        requested_columns=["region", "revenue"],
        profile=make_profile(),
    )

    assert validation.is_valid
    assert validation.invalid_columns == []


def test_codegen_detects_invalid_columns():
    agent = CodegenSQLAgent()

    validation = agent.validate_columns(
        requested_columns=["region", "profit"],
        profile=make_profile(),
    )

    assert not validation.is_valid
    assert "profit" in validation.invalid_columns
    assert validation.warnings


def test_codegen_validates_groupby_request():
    agent = CodegenSQLAgent()

    validation = agent.validate_groupby_request(
        group_column="region",
        value_column="revenue",
        profile=make_profile(),
    )

    assert validation.is_valid


def test_codegen_rejects_groupby_with_wrong_column_types():
    agent = CodegenSQLAgent()

    validation = agent.validate_groupby_request(
        group_column="revenue",
        value_column="region",
        profile=make_profile(),
    )

    assert not validation.is_valid
    assert validation.warnings


def test_codegen_groupby_fails_when_no_numeric_column_exists():
    profile = make_profile()
    profile["dtypes"] = {
        "product": "object",
        "region": "object",
    }
    profile["columns"] = ["product", "region"]

    agent = CodegenSQLAgent()
    result = agent.generate("write pandas code to group by region", profile)

    assert result.mode == "pandas"
    assert "schema validation failed" in result.code
    assert result.warnings

def test_codegen_detects_invalid_mentioned_column_in_pandas_groupby():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write pandas code to group profit by region",
        make_profile(),
    )

    assert result.mode == "pandas"
    assert "requested columns were not found" in result.code

    warning_text = " ".join(result.warnings)
    assert "profit" in warning_text


def test_codegen_detects_invalid_mentioned_column_in_sql_groupby():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write SQL query to group profit by region",
        make_profile(),
    )

    assert result.mode == "sql"
    assert "requested columns were not found" in result.code

    warning_text = " ".join(result.warnings)
    assert "profit" in warning_text


def test_codegen_does_not_flag_valid_groupby_columns():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write pandas code to group revenue by region",
        make_profile(),
    )

    assert result.mode == "pandas"
    assert "groupby" in result.code
    assert not any("does not exist" in warning for warning in result.warnings)

def test_codegen_result_includes_metadata():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write pandas code to group revenue by region",
        make_profile(),
    )

    assert result.generated_code_type == "pandas_groupby_sum"
    assert "df" in result.required_inputs
    assert result.assumptions


def test_codegen_sql_result_includes_metadata():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write SQL query to group revenue by region",
        make_profile(),
    )

    assert result.generated_code_type == "sql_groupby_sum"
    assert "uploaded_table" in result.required_inputs
    assert result.assumptions


def test_codegen_invalid_column_result_includes_metadata():
    agent = CodegenSQLAgent()

    result = agent.generate(
        "write pandas code to group profit by region",
        make_profile(),
    )

    assert result.generated_code_type == "pandas_groupby_failed_invalid_columns"
    assert "df" in result.required_inputs
    assert result.assumptions
    assert result.warnings