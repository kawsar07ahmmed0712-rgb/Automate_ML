from __future__ import annotations

import pandas as pd

from audit_engine.adapters.rapidfuzz_adapter import detect_dirty_label_clusters
from audit_engine.core.config import AuditThresholds


def _safe_label_series(series: pd.Series) -> pd.Series:
    s = series.dropna().astype(str).str.strip()
    s = s[s != ""]
    return s


def build_categorical_signals(
    df: pd.DataFrame,
    profile_df: pd.DataFrame,
    semantic_df: pd.DataFrame,
    thresholds: AuditThresholds,
) -> pd.DataFrame:
    rows = []

    profile_map = profile_df.set_index("column").to_dict(orient="index")
    semantic_map = semantic_df.set_index("column").to_dict(orient="index")

    rare_threshold = thresholds.categorical.rare_threshold
    high_cardinality_threshold = thresholds.categorical.high_cardinality
    rare_label_burden_ratio = thresholds.categorical.rare_label_burden_ratio

    score_cutoff = thresholds.fuzzy.score_cutoff
    min_cluster_size = thresholds.fuzzy.min_cluster_size
    max_unique_values = thresholds.fuzzy.max_unique_values

    for col in df.columns:
        semantic_type = semantic_map.get(col, {}).get("semantic_type", "unknown")
        dtype = str(profile_map.get(col, {}).get("current_dtype", ""))

        categorical_family = semantic_type in {
            "categorical",
            "binary_flag",
            "numeric_discrete",
            "numeric_discrete_as_text",
        } or dtype == "object"

        if not categorical_family:
            continue

        s = _safe_label_series(df[col])
        unique_count = int(profile_map.get(col, {}).get("unique_count", 0))

        if s.empty:
            rows.append(
                {
                    "column": col,
                    "cardinality": unique_count,
                    "dominant_category_ratio": 0.0,
                    "rare_label_count": 0,
                    "rare_label_ratio": 0.0,
                    "high_cardinality_flag": False,
                    "rare_label_burden_flag": False,
                    "dirty_label_cluster_flag": False,
                    "dirty_label_cluster_count": 0,
                    "dirty_label_cluster_examples": "[]",
                    "encoding_hint": "review",
                }
            )
            continue

        vc = s.value_counts(normalize=True)
        dominant_ratio = float(vc.iloc[0]) if not vc.empty else 0.0
        rare_count = int((vc < rare_threshold).sum())
        rare_ratio = float(rare_count / len(vc)) if len(vc) else 0.0

        high_cardinality_flag = unique_count > high_cardinality_threshold
        rare_label_burden_flag = rare_ratio >= rare_label_burden_ratio and unique_count > 10

        fuzzy_result = detect_dirty_label_clusters(
            values=list(s.unique()),
            score_cutoff=score_cutoff,
            min_cluster_size=min_cluster_size,
            max_unique_values=max_unique_values,
        )

        if semantic_type == "binary_flag":
            encoding_hint = "binary_map"
        elif unique_count <= 10:
            encoding_hint = "one_hot"
        elif unique_count <= high_cardinality_threshold:
            encoding_hint = "one_hot_or_frequency_review"
        else:
            encoding_hint = "frequency_or_target_review"

        rows.append(
            {
                "column": col,
                "cardinality": unique_count,
                "dominant_category_ratio": round(dominant_ratio, 4),
                "rare_label_count": rare_count,
                "rare_label_ratio": round(rare_ratio, 4),
                "high_cardinality_flag": high_cardinality_flag,
                "rare_label_burden_flag": rare_label_burden_flag,
                "dirty_label_cluster_flag": bool(fuzzy_result["dirty_label_cluster_flag"]),
                "dirty_label_cluster_count": int(fuzzy_result["cluster_count"]),
                "dirty_label_cluster_examples": str(fuzzy_result["cluster_examples"]),
                "encoding_hint": encoding_hint,
            }
        )

    return pd.DataFrame(rows)