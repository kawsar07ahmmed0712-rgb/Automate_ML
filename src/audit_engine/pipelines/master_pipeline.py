    from pathlib import Path
    import sys

    from audit_engine.ingest.loader import load_dataframe
    from audit_engine.profiling.column_profile import build_column_profiles
    from audit_engine.profiling.parse_profile import build_parse_profile
    from audit_engine.profiling.string_profile import build_string_profile
    from audit_engine.signals.dtype_signals import build_dtype_signals
    from audit_engine.signals.semantic_signals import infer_semantic_types
    from audit_engine.signals.key_signals import build_key_signals
    from audit_engine.signals.missingness_signals import build_missingness_signals
    from audit_engine.signals.categorical_signals import build_categorical_signals
    from audit_engine.signals.numeric_signals import build_numeric_signals
    from audit_engine.signals.datetime_signals import build_datetime_signals
    from audit_engine.signals.string_cleanliness_signals import build_string_cleanliness_signals
    from audit_engine.reports.master_report_builder import build_master_report
    from audit_engine.reports.csv_exporter import export_csv

    def run_master_report(file_path: str | None = None):
        if file_path is None:
            if len(sys.argv) < 2:
                print("Usage: python scripts/run_master_report.py <csv_file>")
                return
            file_path = sys.argv[1]

        df = load_dataframe(file_path)

        profile_df = build_column_profiles(df)
        parse_df = build_parse_profile(df)
        string_df = build_string_profile(df)

        frames = [
            profile_df,
            build_dtype_signals(df, parse_df),
            infer_semantic_types(df, profile_df),
            build_key_signals(profile_df),
            build_missingness_signals(profile_df),
            build_categorical_signals(df, profile_df),
            build_numeric_signals(df),
            build_datetime_signals(df),
            build_string_cleanliness_signals(string_df),
        ]

        master_df = build_master_report(frames)

        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "master_report.csv"
        export_csv(master_df, out_path)

        print(f"Master report saved to: {out_path}")
        return master_df
    
