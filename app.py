import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="ATS CV Optimizer",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 ATS CV Optimizer")
st.markdown("### Research-Grade CV Optimization Pipeline")

st.markdown("""
Welcome to the ATS CV Optimizer. This application implements a 7-phase pipeline to optimize your CV for Applicant Tracking Systems (ATS) and specific Job Descriptions (JD).

**Pipeline Phases:**
1.  **Ingestion:** Upload CV and JD.
2.  **Structure & Verify:** Convert to structured JSON.
3.  **Gap Analysis:** Identify missing keywords.
4.  **Compliance Audit:** Check for buzzwords and formatting.
5.  **Scoring:** Compute ATS and Job-Compatibility scores.
6.  **Rewriting:** AI-powered optimization.
7.  **Final CV:** Export and delivery.

Use the sidebar to navigate through the phases.
""")

st.divider()

st.header("🛠 System Health Check")

# 1. Verify Directory Structure
st.subheader("1. Directory Structure")
required_dirs = ["pages", "modules", "config", "docs"]
missing_dirs = []

cols = st.columns(len(required_dirs))
for i, d in enumerate(required_dirs):
    path = Path(d)
    with cols[i]:
        if path.exists() and path.is_dir():
            st.success(f"✅ `{d}/`")
        else:
            st.error(f"❌ `{d}/`")
            missing_dirs.append(d)

if missing_dirs:
    st.warning(f"Missing directories: {', '.join(missing_dirs)}")

# 2. Verify Modules
st.subheader("2. Core Modules")
module_status = {}

try:
    import modules.parsers
    module_status["parsers"] = True
except ImportError as e:
    module_status["parsers"] = str(e)

try:
    import modules.scoring_pipeline
    module_status["scoring_pipeline"] = True
except ImportError as e:
    module_status["scoring_pipeline"] = str(e)

try:
    import modules.rewriting_engine
    module_status["rewriting_engine"] = True
except ImportError as e:
    module_status["rewriting_engine"] = str(e)

try:
    import modules.cv_assembler
    module_status["cv_assembler"] = True
except ImportError as e:
    module_status["cv_assembler"] = str(e)

try:
    import modules.exporters
    module_status["exporters"] = True
except ImportError as e:
    module_status["exporters"] = str(e)

cols_mod = st.columns(len(module_status))
for i, (mod, status) in enumerate(module_status.items()):
    with cols_mod[i]:
        if status is True:
            st.success(f"✅ `{mod}`")
        else:
            st.error(f"❌ `{mod}`")
            st.caption(status)

# 3. Verify Config & Docs
st.subheader("3. Configuration & Documentation")
config_files = [
    "config/scoring_config.yaml",
    "config/word_lists.py",
    "config/prompts.py",
    "docs/scoring_equations.md"
]

cols_conf = st.columns(len(config_files))
for i, f in enumerate(config_files):
    path = Path(f)
    with cols_conf[i]:
        if path.exists():
            st.success(f"✅ `{path.name}`")
        else:
            st.error(f"❌ `{path.name}`")

st.divider()
st.caption("ATS CV Optimizer v1.0 | System Ready")
