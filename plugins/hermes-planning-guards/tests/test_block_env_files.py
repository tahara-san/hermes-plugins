from hermes_planning_guards.block_env_files import is_blocked_basename, pre_tool_call


def test_blocks_env_file_read():
    result = pre_tool_call("read_file", {"path": ".env"})
    assert result is not None
    assert result["action"] == "block"


def test_allows_env_sample():
    assert pre_tool_call("read_file", {"path": ".env.sample"}) is None


def test_allows_env_example():
    assert pre_tool_call("read_file", {"path": ".env.example"}) is None
    assert pre_tool_call("terminal", {"command": "cat .env.example"}) is None


def test_allows_env_source_file():
    assert is_blocked_basename(".env.ts") is False
    assert pre_tool_call("read_file", {"path": "src/.env.config.ts"}) is None


def test_blocks_terminal_reference():
    result = pre_tool_call("terminal", {"command": "cat .env.local"})
    assert result is not None
    assert "terminal command" in result["message"]


def test_blocks_patch_target():
    patch = """*** Begin Patch\n*** Update File: .env\n@@\n-OLD\n+NEW\n*** End Patch\n"""
    result = pre_tool_call("patch", {"mode": "patch", "patch": patch})
    assert result is not None
    assert "patch target" in result["message"]
