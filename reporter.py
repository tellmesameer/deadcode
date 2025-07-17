from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

from .models import FunctionInfo


def write_report(
    *,
    root: Path,
    functions: Iterable[FunctionInfo],
    ref_counts: Mapping[str, int],
    outfile: Path,
) -> None:
    grouped: dict[Path, list[FunctionInfo]] = defaultdict(list)
    file_totals: dict[Path, int] = defaultdict(int)

    for fn in functions:
        grouped[fn.file_path].append(fn)
        file_totals[fn.file_path] += fn.line_count

    with outfile.open("w", encoding="utf-8") as out:
        # -------- summary ----------
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

        # -------- usage ------------
        print("\n=========== STATIC REFERENCE COUNTS ===========\n", file=out)
        for name, cnt in sorted(ref_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{name}: {cnt} refs", file=out)
