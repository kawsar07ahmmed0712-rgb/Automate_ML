from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class MissingConfig(BaseModel):
    low: float = 5
    high: float = 30
    severe: float = 60
    extreme_drop: float = 85
    indicator_min: float = 5
    indicator_max: float = 60


class NumericConfig(BaseModel):
    outlier_high_pct: float = 5
    skew_moderate: float = 1
    skew_severe: float = 2
    zero_heavy_pct: float = 80


class CategoricalConfig(BaseModel):
    rare_threshold: float = 0.01
    high_cardinality: int = 50
    rare_label_burden_ratio: float = 0.30


class FuzzyConfig(BaseModel):
    score_cutoff: int = 92
    min_cluster_size: int = 2
    max_unique_values: int = 150


class AuditThresholds(BaseModel):
    missing: MissingConfig = Field(default_factory=MissingConfig)
    numeric: NumericConfig = Field(default_factory=NumericConfig)
    categorical: CategoricalConfig = Field(default_factory=CategoricalConfig)
    fuzzy: FuzzyConfig = Field(default_factory=FuzzyConfig)


def load_thresholds(path: str | Path | None = None) -> AuditThresholds:
    if path is None:
        return AuditThresholds()

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Threshold config not found: {path}")

    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AuditThresholds(**data)