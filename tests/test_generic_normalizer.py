import pandas as pd

from agents.generic_normalizer import GenericNormalizerAgent


def test_generic_normalizer_converts_numeric_strings():
    df = pd.DataFrame(
        {
            "revenue": ["1,200", "150", "300"],
            "quantity": ["3", "10", "5"],
        }
    )

    normalizer = GenericNormalizerAgent()
    normalized_dataset = normalizer.normalize(df)

    result = normalized_dataset.dataframe

    assert pd.api.types.is_numeric_dtype(result["revenue"])
    assert pd.api.types.is_numeric_dtype(result["quantity"])
    assert result["revenue"].iloc[0] == 1200
    assert result["quantity"].iloc[1] == 10


def test_generic_normalizer_converts_percentage_strings():
    df = pd.DataFrame(
        {
            "discount_rate": ["10%", "15%", "20%"],
        }
    )

    normalizer = GenericNormalizerAgent()
    normalized_dataset = normalizer.normalize(df)

    result = normalized_dataset.dataframe

    assert pd.api.types.is_numeric_dtype(result["discount_rate"])
    assert result["discount_rate"].iloc[0] == 0.10
    assert result["discount_rate"].iloc[1] == 0.15


def test_generic_normalizer_converts_date_strings():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        }
    )

    normalizer = GenericNormalizerAgent()
    normalized_dataset = normalizer.normalize(df)

    result = normalized_dataset.dataframe

    assert pd.api.types.is_datetime64_any_dtype(result["order_date"])


def test_generic_normalizer_keeps_text_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard"],
            "region": ["HCMC", "Hanoi", "Danang"],
        }
    )

    normalizer = GenericNormalizerAgent()
    normalized_dataset = normalizer.normalize(df)

    result = normalized_dataset.dataframe

    assert result["product"].dtype == "object" or str(result["product"].dtype) == "string"
    assert result["region"].dtype == "object" or str(result["region"].dtype) == "string"


def test_generic_normalizer_removes_empty_rows_and_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", None, "Mouse"],
            "empty_col": [None, None, None],
            "revenue": ["1200", None, "150"],
        }
    )

    normalizer = GenericNormalizerAgent()
    normalized_dataset = normalizer.normalize(df)

    result = normalized_dataset.dataframe

    assert "empty_col" not in result.columns
    assert result.shape[0] == 2