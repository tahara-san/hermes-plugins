"""Register hermes-planning-guards hooks."""
from __future__ import annotations

from .block_env_files import pre_tool_call
from .out_of_scope_reminder import (
    on_session_end,
    post_tool_call,
    pre_llm_call,
    pre_verify,
    transform_llm_output,
)


def register(ctx) -> None:
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_tool_call", post_tool_call)
    ctx.register_hook("pre_verify", pre_verify)
    ctx.register_hook("transform_llm_output", transform_llm_output)
    ctx.register_hook("on_session_end", on_session_end)
