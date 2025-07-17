from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class FunctionInfo:
    file_path: Path
    name: str
    class_name: Optional[str]
    start_lineno: int
    end_lineno: int
    is_async: bool
    decorator_count: int = 0

    # -------- derived -----------
    @property
    def line_count(self) -> int:
        return self.end_lineno - self.start_lineno + 1

    # -------- helpers -----------
    def human(self, root: Path) -> str:
        rel = self.file_path.relative_to(root)
        cls = f"{self.class_name}." if self.class_name else ""
        asnc = " (async)" if self.is_async else ""
        deco = f" [{self.decorator_count} deco]" if self.decorator_count else ""
        return f"{rel} :: {cls}{self.name} – {self.line_count} lines{asnc}{deco}"

    def __hash__(self) -> int:
        return hash((self.file_path, self.name, self.start_lineno))
