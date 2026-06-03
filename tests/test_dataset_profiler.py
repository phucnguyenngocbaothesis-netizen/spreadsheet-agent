import pandas as pd

from agents.dataset_profiler import DatasetProfilerAgent


def test_dataset_profiler_shape():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert profile["shape"]["rows"] == 3
    assert profile["shape"]["columns"] == 2


def test_dataset_profiler_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse"],
            "revenue": [1200, 150],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert profile["columns"] == ["product", "revenue"]


def test_dataset_profiler_missing_values():
    df = pd.DataFrame(
        {
            "product": ["Laptop", None, "Keyboard"],
            "revenue": [1200, None, 300],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert profile["missing_values"]["product"] == 1
    assert profile["missing_values"]["revenue"] == 1


def test_dataset_profiler_duplicate_rows():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Laptop"],
            "revenue": [1200, 150, 1200],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert profile["duplicate_rows"] == 1

def test_dataset_profiler_numeric_summary():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "revenue": [1200, 150, 300],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert "revenue" in profile["numeric_summary"]
    assert profile["numeric_summary"]["revenue"]["count"] == 3
    assert profile["numeric_summary"]["revenue"]["min"] == 150
    assert profile["numeric_summary"]["revenue"]["max"] == 1200


def test_dataset_profiler_categorical_summary():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Laptop"],
            "region": ["HCMC", "Hanoi", "HCMC"],
        }
    )

    profiler = DatasetProfilerAgent()
    profile = profiler.profile(df)

    assert "product" in profile["categorical_summary"]
    assert profile["categorical_summary"]["product"]["unique_count"] == 2
    assert profile["categorical_summary"]["product"]["top_values"]["Laptop"] == 2