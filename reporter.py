from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

from models import FunctionInfo


def _project_line_total(files: set[Path]) -> int:
    """Return the total number of physical lines across all *.py files."""
    total = 0
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8", errors="ignore") as fh:
                for _ in fh:
                    total += 1
        except OSError:
            continue
    return total


def write_report(
    *,
    root: Path,
    functions: Iterable[FunctionInfo],
    ref_counts: Mapping[str, int],
    outfile: Path,
) -> None:
    """Write the text report to *outfile*."""
    functions = list(functions)  # allow multiple passes
    py_files: set[Path] = {fn.file_path for fn in functions}

    # ───────────────────────────────── summary numbers ────────────────────────────
    total_func_lines = sum(fn.line_count for fn in functions)
    total_project_lines = _project_line_total(py_files)

    # ───────────────────────────────── group by file ──────────────────────────────
    grouped: dict[Path, list[FunctionInfo]] = defaultdict(list)
    file_totals: dict[Path, int] = defaultdict(int)

    for fn in functions:
        grouped[fn.file_path].append(fn)
        file_totals[fn.file_path] += fn.line_count

    # ───────────────────────────────── write report ───────────────────────────────
    with outfile.open("w", encoding="utf-8") as out:
        # global summary -----------------------------------------------------------
        print(
            "\n=================== GLOBAL SUMMARY ===================\n",
            file=out,
        )
        print(f"Python files scanned : {len(py_files)}", file=out)
        print(f"Function definitions  : {len(functions)}", file=out)
        print(f"Lines inside funcs    : {total_func_lines}", file=out)
        print(f"Total code lines      : {total_project_lines}", file=out)
        unref = sum(1 for fn in functions if ref_counts.get(fn.name, 0) == 0)
        print(f"Un-referenced funcs   : {unref}", file=out)

        # per-file view ------------------------------------------------------------
        print(
            "\n=========== FUNCTION SUMMARY "
            "(sorted by total function lines) ===========\n",
            file=out,
        )
        for file_path, _ in sorted(
            file_totals.items(), key=lambda x: x[1], reverse=True
        ):
            rel = file_path.relative_to(root)
            print(f"\n📄 {rel}", file=out)
            print("-" * (len(str(rel)) + 4), file=out)
            for fn in sorted(
                grouped[file_path], key=lambda f: f.line_count, reverse=True
            ):
                print("  •", fn.human(root), file=out)

        # static usage counts ------------------------------------------------------
        print(
            "\n=========== STATIC REFERENCE COUNTS (all functions) ===========\n",
            file=out,
        )
        all_names = {fn.name for fn in functions}
        for name in sorted(
            all_names, key=lambda n: (ref_counts.get(n, 0), n), reverse=True
        ):
            print(f"{name}: {ref_counts.get(name, 0)} refs", file=out)
