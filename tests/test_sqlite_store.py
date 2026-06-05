from storage.sqlite_store import SQLiteStore


def test_sqlite_store_saves_and_loads_user_profile(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    store.save_user_profile(
        user_id="test_user",
        role="student",
        technical_level="beginner",
        response_style="balanced",
        preferred_format="bullet",
    )

    profile = store.load_user_profile("test_user")

    assert profile is not None
    assert profile.user_id == "test_user"
    assert profile.role == "student"
    assert profile.technical_level == "beginner"


def test_sqlite_store_updates_user_profile(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    store.save_user_profile(
        user_id="test_user",
        role="student",
        technical_level="beginner",
        response_style="balanced",
        preferred_format="bullet",
    )

    store.save_user_profile(
        user_id="test_user",
        role="analyst",
        technical_level="advanced",
        response_style="detailed",
        preferred_format="step_by_step",
    )

    profile = store.load_user_profile("test_user")

    assert profile is not None
    assert profile.role == "analyst"
    assert profile.technical_level == "advanced"
    assert profile.response_style == "detailed"


def test_sqlite_store_saves_chat_history(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    store.save_chat_message(
        user_id="test_user",
        dataset_name="sales.csv",
        question="show missing values",
        route="DIRECT_ANALYSIS",
        answer_preview="Missing value summary.",
    )

    history = store.load_recent_chat_history("test_user")

    assert len(history) == 1
    assert history[0].question == "show missing values"
    assert history[0].route == "DIRECT_ANALYSIS"


def test_sqlite_store_limits_chat_history(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    for index in range(5):
        store.save_chat_message(
            user_id="test_user",
            dataset_name="sales.csv",
            question=f"question {index}",
            route="DIRECT_ANALYSIS",
            answer_preview="answer",
        )

    history = store.load_recent_chat_history("test_user", limit=3)

    assert len(history) == 3
    assert history[0].question == "question 4"


def test_sqlite_store_clears_chat_history(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    store.save_chat_message(
        user_id="test_user",
        dataset_name="sales.csv",
        question="show missing values",
        route="DIRECT_ANALYSIS",
        answer_preview="answer",
    )

    store.clear_chat_history("test_user")

    history = store.load_recent_chat_history("test_user")

    assert history == []


def test_sqlite_store_summarizes_memory(tmp_path):
    db_path = tmp_path / "test_memory.db"
    store = SQLiteStore(db_path=str(db_path))

    store.save_user_profile(
        user_id="test_user",
        role="student",
        technical_level="beginner",
        response_style="balanced",
        preferred_format="bullet",
    )

    store.save_chat_message(
        user_id="test_user",
        dataset_name="sales.csv",
        question="show missing values",
        route="DIRECT_ANALYSIS",
        answer_preview="answer",
    )

    summary = store.summarize_memory("test_user")

    assert summary["has_profile"]
    assert summary["recent_chat_count"] == 1
    assert "show missing values" in summary["recent_questions"]