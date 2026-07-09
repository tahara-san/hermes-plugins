from hermes_planning_guards.out_of_scope_reminder import (
    PRE_VERIFY_MESSAGE,
    TRANSFORM_GUARD_NOTE,
    contains_issue_like_language,
    explicitly_says_no_issue_to_log,
    extract_issue_paths_from_tool_call,
    on_session_end,
    post_tool_call,
    pre_llm_call,
    pre_verify,
    reset_issue_tracking_state,
    transform_llm_output,
)


def setup_function():
    reset_issue_tracking_state()


def test_pre_llm_call_injects_context():
    result = pre_llm_call(session_id="s1", turn_id="t1")
    assert "context" in result
    assert "tasks/out-of-scope-issues" in result["context"]
    assert "Dependabot" in result["context"]


def test_contains_issue_like_language_uses_focused_trigger_set():
    assert contains_issue_like_language("Found a pre-existing bug")
    assert contains_issue_like_language("This is OUT-OF-SCOPE for now")
    assert contains_issue_like_language("Follow-up: simplify this later")
    assert contains_issue_like_language("This no-op looks suspicious")
    assert contains_issue_like_language("Skipped unrelated test")
    assert contains_issue_like_language("There is a code smell here")
    assert not contains_issue_like_language("Everything passed cleanly")
    assert not contains_issue_like_language("This unskipped setup is unrelated")


def test_explicit_no_issue_to_log_language_is_detected():
    assert explicitly_says_no_issue_to_log("There is no out-of-scope issue to log.")
    assert explicitly_says_no_issue_to_log("Skipped work is not an out-of-scope issue.")
    assert explicitly_says_no_issue_to_log(
        "Nothing to log under tasks/out-of-scope-issues for this follow-up note."
    )
    assert not explicitly_says_no_issue_to_log("There is an out-of-scope issue.")


def test_extract_issue_paths_from_write_file():
    paths = extract_issue_paths_from_tool_call(
        "write_file",
        {"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
    )
    assert paths == {"tasks/out-of-scope-issues/medium/20260709_bug.md"}


def test_extract_issue_paths_from_patch_replace_mode():
    paths = extract_issue_paths_from_tool_call(
        "patch",
        {"path": "tasks/out-of-scope-issues/low/20260709_cleanup.md"},
    )
    assert paths == {"tasks/out-of-scope-issues/low/20260709_cleanup.md"}


def test_extract_issue_paths_from_v4a_patch_targets():
    paths = extract_issue_paths_from_tool_call(
        "patch",
        {
            "mode": "patch",
            "patch": """*** Begin Patch
*** Add File: tasks/out-of-scope-issues/high/20260709_stale.md
+**Issue**
*** Update File: src/app.py
*** End Patch
""",
        },
    )
    assert paths == {"tasks/out-of-scope-issues/high/20260709_stale.md"}


def test_extract_issue_paths_from_terminal_command_text():
    paths = extract_issue_paths_from_tool_call(
        "terminal",
        {"command": "python scripts/write.py tasks/out-of-scope-issues/manual/20260709_item.md"},
    )
    assert "tasks/out-of-scope-issues/manual/20260709_item.md" in paths


def test_pre_verify_allows_clean_response():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert pre_verify(coding=True, final_response="Done; all checks passed.", session_id="s1") is None


def test_pre_verify_allows_after_issue_path_touch():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="ok",
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1") is None


def test_pre_verify_allows_changed_issue_path_without_observed_tool_call():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert (
        pre_verify(
            coding=True,
            final_response="Found a follow-up.",
            session_id="s1",
            changed_paths=["tasks/out-of-scope-issues/low/20260709_followup.md"],
        )
        is None
    )


def test_pre_verify_continues_when_issue_like_language_unlogged():
    pre_llm_call(session_id="s1", turn_id="t1")
    result = pre_verify(coding=True, final_response="There is a pre-existing issue.", session_id="s1")
    assert result == {"action": "continue", "message": PRE_VERIFY_MESSAGE}


def test_pre_verify_allows_explicit_no_issue_to_log_response():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert (
        pre_verify(
            coding=True,
            final_response="Skipped setup is not an out-of-scope issue.",
            session_id="s1",
        )
        is None
    )


def test_pre_verify_is_scoped_to_coding_and_first_attempt():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert pre_verify(coding=False, final_response="There is a code smell.", session_id="s1") is None
    assert pre_verify(coding=True, attempt=1, final_response="There is a code smell.", session_id="s1") is None


def test_transform_llm_output_appends_visible_fallback_when_unlogged():
    pre_llm_call(session_id="s1", turn_id="t1")
    response = transform_llm_output("Skipped a follow-up item.", session_id="s1")
    assert response == "Skipped a follow-up item." + TRANSFORM_GUARD_NOTE


def test_transform_llm_output_allows_explicit_no_issue_to_log_response():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert transform_llm_output(
        "Skipped setup is not an out-of-scope issue.",
        session_id="s1",
    ) is None


def test_transform_llm_output_leaves_logged_or_clean_output_unchanged():
    pre_llm_call(session_id="s1", turn_id="t1")
    assert transform_llm_output("Everything passed.", session_id="s1") is None
    post_tool_call(
        tool_name="patch",
        args={"path": "tasks/out-of-scope-issues/other/20260709_note.md"},
        status="ok",
        session_id="s1",
        turn_id="t1",
    )
    assert transform_llm_output("Skipped a follow-up item.", session_id="s1") is None


def test_failed_tool_status_does_not_count_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="blocked",
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_failed_status_string_does_not_count_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="failed",
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_error_result_without_status_does_not_count_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        result='{"error":"write failed"}',
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_nonzero_terminal_result_without_status_does_not_count_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="terminal",
        args={"command": "touch tasks/out-of-scope-issues/medium/20260709_bug.md"},
        result='{"output":"failed","exit_code":1,"error":null}',
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_empty_or_malformed_result_without_status_does_not_count_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    for result in ("", "not json"):
        post_tool_call(
            tool_name="write_file",
            args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
            result=result,
            session_id="s1",
            turn_id="t1",
        )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_no_clear_success_json_without_status_does_not_count_as_logged():
    for result in ('{}', '{"output":"wrote maybe"}', '{"success":null}'):
        reset_issue_tracking_state()
        pre_llm_call(session_id="s1", turn_id="t1")
        post_tool_call(
            tool_name="write_file",
            args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
            result=result,
            session_id="s1",
            turn_id="t1",
        )
        assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_write_file_success_result_without_status_counts_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        result='{"bytes_written":123,"resolved_path":"/repo/tasks/out-of-scope-issues/medium/20260709_bug.md"}',
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1") is None


def test_success_result_without_status_counts_as_logged():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        result='{"success":true}',
        session_id="s1",
        turn_id="t1",
    )
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1") is None


def test_repeated_pre_llm_call_same_turn_preserves_issue_touch():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="ok",
        session_id="s1",
        turn_id="t1",
    )
    pre_llm_call(session_id="s1", turn_id="t1")
    assert transform_llm_output("Found a pre-existing issue.", session_id="s1") is None


def test_repeated_pre_llm_call_without_turn_id_resets_issue_touch_safely():
    pre_llm_call(session_id="s1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="ok",
        session_id="s1",
    )
    pre_llm_call(session_id="s1")
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_new_turn_resets_previous_issue_touch():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="ok",
        session_id="s1",
        turn_id="t1",
    )
    pre_llm_call(session_id="s1", turn_id="t2")
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")


def test_on_session_end_clears_tracking_state():
    pre_llm_call(session_id="s1", turn_id="t1")
    post_tool_call(
        tool_name="write_file",
        args={"path": "tasks/out-of-scope-issues/medium/20260709_bug.md"},
        status="ok",
        session_id="s1",
        turn_id="t1",
    )
    on_session_end(session_id="s1")
    assert pre_verify(coding=True, final_response="Found a pre-existing issue.", session_id="s1")
