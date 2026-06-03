from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from agents.smart_loader import SmartLoaderAgent
from agents.generic_normalizer import GenericNormalizerAgent
from agents.dataset_profiler import DatasetProfilerAgent


@dataclass
class PipelineResult:
    dataframe: pd.DataFrame
    metadata: dict[str, Any]
    normalization_report: dict[str, Any]
    profile: dict[str, Any]


class SpreadsheetPipeline:
    """
    Week 2 pipeline:
    Uploaded file
        -> Smart Loader
        -> Generic Normalizer
        -> Dataset Profiler
        -> Return result
    """

    def __init__(self) -> None:
        self.smart_loader = SmartLoaderAgent()
        self.generic_normalizer = GenericNormalizerAgent()
        self.dataset_profiler = DatasetProfilerAgent()

    def run(self, uploaded_file) -> PipelineResult:
        loaded_dataset = self.smart_loader.load(uploaded_file)

        loaded_df = loaded_dataset.dataframe
        metadata = loaded_dataset.metadata

        normalized_dataset = self.generic_normalizer.normalize(loaded_df)

        normalized_df = normalized_dataset.dataframe
        normalization_report = normalized_dataset.report

        profile = self.dataset_profiler.profile(normalized_df)

        return PipelineResult(
            dataframe=normalized_df,
            metadata=metadata,
            normalization_report=normalization_report,
            profile=profile,
        )