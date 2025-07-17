from __future__ import annotations

import argparse
from pathlib import Path

from . import scanner
from .reporter import write_report


def main() -> None:
    ap = argparse.ArgumentParser(prog="deadcode", description="Static usage report")
    ap.add_argument("codebase", help="root directory of project")
    ap.add_argument(
        "-o",
        "--output",
        default="function_report.txt",
        help="path for generated report file",
    )
    ns = ap.parse_args()

    functions, refs = scanner.scan(ns.codebase)
    write_report(
        root=Path(ns.codebase).resolve(),
        functions=functions,
        ref_counts=refs,
        outfile=Path(ns.output),
    )
    print("✅ Report saved to", ns.output)


if __name__ == "__main__":  # pragma: no cover
    main()
