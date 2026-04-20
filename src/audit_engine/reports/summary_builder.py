from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def build_summary(
    master_df: pd.DataFrame,
    fe_df: pd.DataFrame,
    output_path: str | Path | None = None,
) -> dict:
    summary = {
        "column_count": int(len(master_df)),
        "high_severity_columns": int((master_df["severity"] == "high").sum()) if "severity" in master_df.columns else 0,
        "medium_severity_columns": int((master_df["severity"] == "medium").sum()) if "severity" in master_df.columns else 0,
        "low_severity_columns": int((master_df["severity"] == "low").sum()) if "severity" in master_df.columns else 0,
        "average_quality_score": round(float(master_df["quality_score"].mean()), 2) if "quality_score" in master_df.columns and not master_df.empty else 0.0,
        "columns_with_missingness": int((master_df["missing_pct"] > 0).sum()) if "missing_pct" in master_df.columns else 0,
        "high_missingness_columns": int(master_df.get("high_missingness_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "high_missingness_flag" in master_df.columns else 0,
        "severe_missingness_columns": int(master_df.get("severe_missingness_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "severe_missingness_flag" in master_df.columns else 0,
        "high_cardinality_columns": int(master_df.get("high_cardinality_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "high_cardinality_flag" in master_df.columns else 0,
        "rare_label_burden_columns": int(master_df.get("rare_label_burden_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "rare_label_burden_flag" in master_df.columns else 0,
        "high_outlier_columns": int(master_df.get("high_outlier_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "high_outlier_flag" in master_df.columns else 0,
        "severe_skew_columns": int(master_df.get("severe_skew_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "severe_skew_flag" in master_df.columns else 0,
        "identifier_like_columns": int(master_df.get("id_like_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "id_like_flag" in master_df.columns else 0,
        "datetime_columns": int(master_df.get("datetime_flag", pd.Series(dtype=bool)).fillna(False).sum()) if "datetime_flag" in master_df.columns else 0,
        "text_cleaning_columns": int(fe_df.get("text_cleaning_needed", pd.Series(dtype=bool)).fillna(False).sum()) if "text_cleaning_needed" in fe_df.columns else 0,
        "high_priority_fe_columns": int((fe_df["priority"] == "high").sum()) if "priority" in fe_df.columns else 0,
        "medium_priority_fe_columns": int((fe_df["priority"] == "medium").sum()) if "priority" in fe_df.columns else 0,
        "drop_candidate_columns": int((fe_df["keep_drop_review"] == "drop").sum()) if "keep_drop_review" in fe_df.columns else 0,
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    return summary