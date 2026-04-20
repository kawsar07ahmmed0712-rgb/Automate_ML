    from pathlib import Path
    import sys

    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.rules.fe_rule_engine import build_fe_actions
    from audit_engine.reports.fe_report_builder import build_fe_report
    from audit_engine.reports.csv_exporter import export_csv

    def run_fe_pipeline(file_path: str | None = None):
        if file_path is None:
            if len(sys.argv) < 2:
                print("Usage: python scripts/run_fe_report.py <csv_file>")
                return
            file_path = sys.argv[1]

        master_df = run_master_report(file_path)
        fe_df = build_fe_actions(master_df)
        fe_df = build_fe_report(fe_df)

        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "feature_engineering_report.csv"
        export_csv(fe_df, out_path)

        print(f"Feature engineering report saved to: {out_path}")
        return fe_df

    def run_fe_report(file_path: str | None = None):
        return run_fe_pipeline(file_path)
    
