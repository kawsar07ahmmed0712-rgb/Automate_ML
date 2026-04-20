    from audit_engine.profiling.column_profile import build_column_profiles

    def test_module_import():
        assert callable(build_column_profiles)
    
