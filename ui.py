from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from .scanner import scan
from .reporter import write_report

st.title("Dead-Code Static Report")

codebase = st.text_input("Project root (folder)", value=".")
run = st.button("Run")

if run:
    with st.spinner("Scanning…"):
        funcs, refs = scan(codebase)
        tmp = Path(tempfile.gettempdir()) / "function_report.txt"
        write_report(root=Path(codebase).resolve(), functions=funcs, ref_counts=refs, outfile=tmp)
    st.success("Done!")
    st.download_button("Download report", tmp.read_bytes(), file_name="function_report.txt")
