"""Flet API compatibility checker.

Goal: Catch common runtime crashes (missing attributes, invalid kwargs) without launching the UI or building the .exe.

Usage:
  python flet_compat_check.py
  python flet_compat_check.py i18n_manager_modern.py

It parses the target Python file and validates:
- Attribute accesses like ft.something (existence)
- Calls like ft.Card(..., color=...) where kwargs don't exist for that control in the installed Flet version

Notes:
- This is a best-effort static checker. It covers the majority of Flet API mistakes that would crash at runtime.
- It only checks calls where the callee is a simple `ft.<Name>` reference.
"""

from __future__ import annotations

import ast
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class Issue:
    file: str
    line: int
    col: int
    kind: str
    message: str


def _get_ft_attr(ft_module: Any, name: str) -> tuple[bool, Optional[Any]]:
    try:
        return hasattr(ft_module, name), getattr(ft_module, name)
    except Exception:
        return False, None


def _callable_signature(obj: Any) -> Optional[inspect.Signature]:
    try:
        return inspect.signature(obj)
    except Exception:
        return None


def _allowed_kwargs(sig: inspect.Signature) -> set[str]:
    allowed: set[str] = set()
    for param in sig.parameters.values():
        if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            allowed.add(param.name)
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # accepts **kwargs, so we can't validate kwargs names
            return set()
    return allowed


class FletCompatVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, ft_module: Any):
        self.filename = filename
        self.ft = ft_module
        self.issues: list[Issue] = []

    def visit_Attribute(self, node: ast.Attribute):
        # Detect `ft.<attr>` usages.
        if isinstance(node.value, ast.Name) and node.value.id == "ft":
            exists, _ = _get_ft_attr(self.ft, node.attr)
            if not exists:
                self.issues.append(
                    Issue(
                        file=self.filename,
                        line=getattr(node, "lineno", 1),
                        col=getattr(node, "col_offset", 0),
                        kind="missing-attribute",
                        message=f"ft has no attribute '{node.attr}'",
                    )
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Validate calls like ft.Card(...)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "ft":
            ctrl_name = node.func.attr
            exists, obj = _get_ft_attr(self.ft, ctrl_name)
            if not exists or obj is None:
                self.issues.append(
                    Issue(
                        file=self.filename,
                        line=getattr(node, "lineno", 1),
                        col=getattr(node, "col_offset", 0),
                        kind="missing-control",
                        message=f"ft.{ctrl_name} is not available in this Flet version",
                    )
                )
                return

            sig = _callable_signature(obj)
            if sig is None:
                # Can't introspect; skip kw validation.
                return

            allowed = _allowed_kwargs(sig)
            if allowed == set():
                # Either **kwargs exists or signature not suitable; skip.
                return

            for kw in node.keywords:
                if kw.arg is None:
                    continue  # **kwargs
                if kw.arg not in allowed:
                    self.issues.append(
                        Issue(
                            file=self.filename,
                            line=getattr(kw, "lineno", getattr(node, "lineno", 1)),
                            col=getattr(kw, "col_offset", getattr(node, "col_offset", 0)),
                            kind="invalid-kwarg",
                            message=f"ft.{ctrl_name}() has no kwarg '{kw.arg}' (allowed: {', '.join(sorted(allowed))})",
                        )
                    )

        self.generic_visit(node)


def run_check(target: Path) -> list[Issue]:
    import flet as ft  # local import for the environment version

    code = target.read_text(encoding="utf-8")
    tree = ast.parse(code, filename=str(target))
    visitor = FletCompatVisitor(str(target), ft)
    visitor.visit(tree)
    return visitor.issues


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path(__file__).with_name("i18n_manager_modern.py")
    if not target.exists():
        print(f"Target not found: {target}")
        return 2

    try:
        import flet as ft
        print(f"Flet version: {getattr(ft, '__version__', 'unknown')}")
    except Exception as ex:
        print(f"Failed to import flet: {ex}")
        return 2

    issues = run_check(target)

    if not issues:
        print("OK: no obvious Flet API issues found.")
        return 0

    print(f"Found {len(issues)} issue(s):")
    for issue in issues:
        print(f"- {issue.kind}: {issue.file}:{issue.line}:{issue.col} - {issue.message}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
