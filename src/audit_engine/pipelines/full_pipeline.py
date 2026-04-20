from __future__ import annotations

import json
from pathlib import Path

from audit_engine.core.config import load_thresholds
from audit_engine.ingest.loader import load_dataframe
from audit_engine.profiling.column_profile import build_column_profiles
from audit_engine.signals.semantic_signals import infer_semantic_types
from audit_engine.signals.missingness_signals import build_missingness_signals
from audit_engine.signals.numeric_signals import build_numeric_signals
from audit_engine.signals.categorical_signals import build_categorical_signals
from audit_engine.signals.string_cleanliness_signals import build_string_cleanliness_signals
from audit_engine.signals.key_signals import build_key_signals
from audit_engine.signals.datetime_signals import build_datetime_signals
from audit_engine.signals.schema_signals import build_schema_signals
from audit_engine.reports.master_report_builder import build_master_report
from audit_engine.reports.summary_builder import build_summary
from audit_engine.rules.fe_rule_engine import build_fe_report
from audit_engine.adapters.pandera_adapter import run_pandera_checks
from audit_engine.adapters.ydata_adapter import generate_ydata_profile


def _apply_manual_overrides(
    semantic_df,
    target_col: str | None = None,
    date_col: str | None = None,
    id_col: str | None = None,
):
    out = semantic_df.copy()

    if target_col and target_col in out["column"].values:
        out.loc[out["column"] == target_col, "semantic_type"] = "target"
        out.loc[out["column"] == target_col, "semantic_confidence"] = 1.0
        out.loc[out["column"] == target_col, "semantic_review_flag"] = False

    if date_col and date_col in out["column"].values:
        out.loc[out["column"] == date_col, "semantic_type"] = "datetime"
        out.loc[out["column"] == date_col, "semantic_confidence"] = 1.0
        out.loc[out["column"] == date_col, "semantic_review_flag"] = False

    if id_col and id_col in out["column"].values:
        out.loc[out["column"] == id_col, "semantic_type"] = "identifier"
        out.loc[out["column"] == id_col, "semantic_confidence"] = 1.0
        out.loc[out["column"] == id_col, "semantic_review_flag"] = False

    return out


def run_full_pipeline(
    file_path: str,
    test_file_path: str | None = None,
    target_col: str | None = None,
    date_col: str | None = None,
    id_col: str | None = None,
    out_dir: str = "outputs",
    thresholds_path: str = "configs/thresholds.yaml",
):
    thresholds = load_thresholds(thresholds_path)

    df = load_dataframe(file_path)
    test_df = load_dataframe(test_file_path) if test_file_path else None

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_df = build_column_profiles(df)
    semantic_df = infer_semantic_types(df, profile_df)
    semantic_df = _apply_manual_overrides(
        semantic_df,
        target_col=target_col,
        date_col=date_col,
        id_col=id_col,
    )

    missing_df = build_missingness_signals(df, profile_df, thresholds)
    numeric_df = build_numeric_signals(df, semantic_df, thresholds)
    categorical_df = build_categorical_signals(df, profile_df, semantic_df, thresholds)
    string_clean_df = build_string_cleanliness_signals(df, profile_df)
    key_df = build_key_signals(profile_df, semantic_df)
    datetime_df = build_datetime_signals(df, profile_df, semantic_df, date_col=date_col)

    if test_df is not None:
        test_profile_df = build_column_profiles(test_df)
        test_semantic_df = infer_semantic_types(test_df, test_profile_df)
        test_semantic_df = _apply_manual_overrides(
            test_semantic_df,
            date_col=date_col,
            id_col=id_col,
        )
        schema_df = build_schema_signals(
            train_df=df,
            test_df=test_df,
            train_semantic_df=semantic_df,
            test_semantic_df=test_semantic_df,
        )
    else:
        schema_df = build_schema_signals(df)

    master_report = build_master_report(
        [
            profile_df,
            semantic_df,
            missing_df,
            numeric_df,
            categorical_df,
            string_clean_df,
            key_df,
            datetime_df,
            schema_df,
        ]
    )

    fe_report = build_fe_report(master_report, target_col=target_col)
    summary = build_summary(master_report, fe_report, output_path=output_dir / "summary.json")

    master_path = output_dir / "master_report.csv"
    fe_path = output_dir / "feature_engineering_report.csv"

    master_report.to_csv(master_path, index=False)
    fe_report.to_csv(fe_path, index=False)

    pandera_result = run_pandera_checks(df)
    (output_dir / "pandera_validation.json").write_text(
        json.dumps(pandera_result, indent=2, default=str),
        encoding="utf-8",
    )

    ydata_result = generate_ydata_profile(df, output_path=output_dir / "ydata_profile.html")
    (output_dir / "ydata_profile_status.json").write_text(
        json.dumps(ydata_result, indent=2, default=str),
        encoding="utf-8",
    )

    print("Audit complete")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    if test_df is not None:
        print(f"Schema comparison enabled with test file: {test_file_path}")
    print(f"Threshold config loaded from: {thresholds_path}")
    print(f"Master report saved: {master_path}")
    print(f"Feature engineering report saved: {fe_path}")
    print(f"Summary saved: {output_dir / 'summary.json'}")
    print(f"Pandera validation saved: {output_dir / 'pandera_validation.json'}")

    if ydata_result.get("ydata_profile_generated"):
        print(f"YData profile saved: {output_dir / 'ydata_profile.html'}")
    else:
        print("YData profile not generated")

    print(f"High priority FE columns: {summary.get('high_priority_fe_columns', 0)}")

    return {
        "master_report": master_report,
        "fe_report": fe_report,
        "summary": summary,
        "pandera_validation": pandera_result,
        "ydata_profile_status": ydata_result,
        "thresholds_used": thresholds.model_dump(),
    }


if __name__ == "__main__":
    run_full_pipeline("sample.csv")