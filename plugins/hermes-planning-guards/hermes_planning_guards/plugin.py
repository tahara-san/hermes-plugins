"""Register hermes-planning-guards hooks."""
from __future__ import annotations

from .block_env_files import pre_tool_call
from .out_of_scope_reminder import pre_llm_call


def register(ctx) -> None:
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("pre_llm_call", pre_llm_call)
