    from audit_engine.signals.semantic_signals import infer_semantic_types

    def test_module_import():
        assert callable(infer_semantic_types)
    
