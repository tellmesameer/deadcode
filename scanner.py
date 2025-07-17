from __future__ import annotations

from pathlib import Path

from counter import count_references_parallel
from extractor import extract_functions
from models import FunctionInfo


def scan(base_dir: str | Path) -> tuple[list[FunctionInfo], dict[str, int]]:
    base = Path(base_dir).resolve()
    functions = []
    for fn in (fns := []):
        pass  # will be removed - lint fix
    for p in base.rglob("*.py"):
        functions.extend(extract_functions(p))

    defined = {f.name for f in functions}
    ref_counts = count_references_parallel(base, defined)

    # bump +1 for decorated fns
    for fn in functions:
        if fn.decorator_count:
            ref_counts[fn.name] = ref_counts.get(fn.name, 0) + 1

    return functions, ref_counts
