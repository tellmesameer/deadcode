from __future__ import annotations

import ast
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from pathlib import Path
from typing import Iterable


class _RefVisitor(ast.NodeVisitor):
    def __init__(self, valid: set[str]) -> None:
        self.valid = valid
        self.refs: Counter[str] = Counter()

    def visit_Call(self, node: ast.Call) -> None:
        self._maybe(node.func)
        for arg in node.args:
            self._maybe(arg)
        for kw in node.keywords:
            self._maybe(kw.value)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._maybe(node)
        self.generic_visit(node)

    def _maybe(self, node: ast.AST | None) -> None:
        name = self._extract(node)
        if name in self.valid:
            self.refs[name] += 1

    @staticmethod
    def _extract(node: ast.AST | None) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None


def _count_in_file(path: Path, valid: set[str]) -> Counter[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return Counter()
    v = _RefVisitor(valid)
    v.visit(tree)
    return v.refs


def _iter_py(base: Path) -> Iterable[Path]:
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".py"):
                yield Path(root) / f


# ----------------------------------------------------------------------
def count_references_parallel(base: Path, valid: set[str]) -> Counter[str]:
    total: Counter[str] = Counter()
    with ThreadPoolExecutor() as pool:
        for c in pool.map(_count_in_file, _iter_py(base), repeat(valid)):
            total.update(c)
    return total
