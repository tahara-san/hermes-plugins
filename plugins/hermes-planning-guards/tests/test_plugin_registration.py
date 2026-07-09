import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FakeContext:
    def __init__(self):
        self.hooks = []

    def register_hook(self, name, callback):
        self.hooks.append((name, callback))


def load_directory_plugin_root():
    """Simulate Hermes directory-plugin loading of root __init__.py."""
    parent = "hermes_plugins_test"
    if parent not in sys.modules:
        ns_pkg = types.ModuleType(parent)
        ns_pkg.__path__ = []
        ns_pkg.__package__ = parent
        sys.modules[parent] = ns_pkg
    module_name = f"{parent}.hermes_planning_guards"
    spec = importlib.util.spec_from_file_location(
        module_name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    module.__package__ = module_name
    module.__path__ = [str(ROOT)]
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_directory_plugin_root_init_exports_register():
    module = load_directory_plugin_root()
    assert hasattr(module, "register")


def test_register_wires_expected_hooks():
    module = load_directory_plugin_root()
    ctx = FakeContext()
    module.register(ctx)
    names = [name for name, _ in ctx.hooks]
    assert names == [
        "pre_tool_call",
        "pre_llm_call",
        "post_tool_call",
        "pre_verify",
        "transform_llm_output",
        "on_session_end",
    ]
