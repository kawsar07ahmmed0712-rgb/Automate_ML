from __future__ import annotations

from functools import reduce

import pandas as pd


def _merge_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    valid_frames = [df for df in frames if df is not None and not df.empty]
    if not valid_frames:
        return pd.DataFrame()

    return reduce(
        lambda left, right: left.merge(right, on="column", how="outer"),
        valid_frames,
    )


def _assign_severity(master_df: pd.DataFrame) -> pd.DataFrame:
    out = master_df.copy()

    severity = []
    for _, row in out.iterrows():
        score = 0

        if bool(row.get("drop_candidate_extreme_missing", False)):
            score += 3
        elif bool(row.get("severe_missingness_flag", False)):
            score += 3
        elif bool(row.get("high_missingness_flag", False)):
            score += 2

        if bool(row.get("high_outlier_flag", False)):
            score += 1
        if bool(row.get("severe_skew_flag", False)):
            score += 1
        if bool(row.get("high_cardinality_flag", False)):
            score += 1
        if bool(row.get("rare_label_burden_flag", False)):
            score += 1
        if bool(row.get("special_character_flag", False)):
            score += 1
        if bool(row.get("case_inconsistency_flag", False)):
            score += 1
        if bool(row.get("possible_primary_key_flag", False)):
            score += 1

        if score >= 5:
            severity.append("high")
        elif score >= 2:
            severity.append("medium")
        else:
            severity.append("low")

    out["severity"] = severity
    return out


def _assign_quality_score(master_df: pd.DataFrame) -> pd.DataFrame:
    out = master_df.copy()
    scores = []

    for _, row in out.iterrows():
        score = 100.0

        score -= min(float(row.get("missing_pct", 0) or 0) * 0.20, 25)
        score -= min(float(row.get("outlier_pct_iqr", 0) or 0) * 0.50, 15)
        score -= 8 if bool(row.get("high_cardinality_flag", False)) else 0
        score -= 6 if bool(row.get("rare_label_burden_flag", False)) else 0
        score -= 5 if bool(row.get("special_character_flag", False)) else 0
        score -= 5 if bool(row.get("case_inconsistency_flag", False)) else 0
        score -= 5 if bool(row.get("empty_string_issue_flag", False)) else 0
        score -= 4 if bool(row.get("whitespace_issue_flag", False)) else 0
        score -= 4 if bool(row.get("mixed_null_tokens_flag", False)) else 0

        scores.append(round(max(score, 0), 2))

    out["quality_score"] = scores
    return out


def build_master_report(frames: list[pd.DataFrame]) -> pd.DataFrame:
    master_df = _merge_frames(frames)

    if master_df.empty:
        return master_df

    # boolean columns fill
    bool_like_cols = [col for col in master_df.columns if col.endswith("_flag")]
    for col in bool_like_cols:
        master_df[col] = master_df[col].fillna(False)

    master_df = _assign_severity(master_df)
    master_df = _assign_quality_score(master_df)

    preferred_cols = [
        "column",
        "current_dtype",
        "semantic_type",
        "semantic_confidence",
        "severity",
        "quality_score",
        "missing_count",
        "missing_pct",
        "unique_count",
        "unique_ratio",
        "cardinality",
        "outlier_pct_iqr",
        "skewness",
        "zero_pct",
    ]

    existing_preferred = [c for c in preferred_cols if c in master_df.columns]
    remaining = [c for c in master_df.columns if c not in existing_preferred]

    return master_df[existing_preferred + remaining]