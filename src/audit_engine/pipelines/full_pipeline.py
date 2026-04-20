    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.pipelines.fe_pipeline import run_fe_pipeline

    def run_full_pipeline(file_path: str | None = None):
        master_df = run_master_report(file_path)
        fe_df = run_fe_pipeline(file_path)
        return {"master_report": master_df, "fe_report": fe_df}

    def run_full_audit(file_path: str | None = None):
        return run_full_pipeline(file_path)
    
