from __future__ import annotations

import ast
from pathlib import Path
from typing import List

from models import FunctionInfo


class _FunctionGatherer(ast.NodeVisitor):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.fns: List[FunctionInfo] = []
        self.class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: D401,E501
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._add(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._add(node, is_async=True)

    def _add(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        *,
        is_async: bool,
    ) -> None:
        self.fns.append(
            FunctionInfo(
                file_path=self.file_path,
                name=node.name,
                class_name=".".join(self.class_stack) or None,
                start_lineno=node.lineno,
                end_lineno=node.end_lineno,
                is_async=is_async,
                decorator_count=len(node.decorator_list),
            )
        )
        self.generic_visit(node)


# ----------------------------------------------------------------------
def extract_functions(path: Path) -> list[FunctionInfo]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []
    visitor = _FunctionGatherer(path)
    visitor.visit(tree)
    return visitor.fns
