    from audit_engine.reports.master_report_builder import build_master_report
    from audit_engine.reports.fe_report_builder import build_fe_report

    def test_imports():
        assert callable(build_master_report)
        assert callable(build_fe_report)
    
