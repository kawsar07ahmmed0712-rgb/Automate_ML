    from audit_engine.rules.fe_rule_engine import build_fe_actions

    def test_module_import():
        assert callable(build_fe_actions)
    
