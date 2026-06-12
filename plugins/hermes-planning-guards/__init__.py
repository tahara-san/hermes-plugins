"""Directory-plugin shim for Hermes plugin discovery.

Hermes directory plugins require plugin.yaml and a root __init__.py with
register(ctx). The implementation lives in the hermes_planning_guards package
so it also works as a pip/entry-point plugin.
"""

try:
    # Hermes loads directory plugins as package namespaces, so this is the
    # normal runtime path.
    from .hermes_planning_guards import register
except ImportError:  # pragma: no cover - pytest/importlib direct-file fallback
    # Test runners may import this file as a bare __init__ module because the
    # plugin directory name contains hyphens and is not a regular Python package.
    import sys
    from pathlib import Path

    plugin_dir = str(Path(__file__).resolve().parent)
    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)
    from hermes_planning_guards import register

__all__ = ["register"]
