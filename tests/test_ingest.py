    from audit_engine.ingest.loader import load_dataframe

    def test_module_import():
        assert callable(load_dataframe)
    
