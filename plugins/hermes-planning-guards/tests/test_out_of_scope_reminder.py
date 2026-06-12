from hermes_planning_guards.out_of_scope_reminder import pre_llm_call


def test_pre_llm_call_injects_context():
    result = pre_llm_call()
    assert "context" in result
    assert "tasks/out-of-scope-issues" in result["context"]
    assert "Dependabot" in result["context"]
