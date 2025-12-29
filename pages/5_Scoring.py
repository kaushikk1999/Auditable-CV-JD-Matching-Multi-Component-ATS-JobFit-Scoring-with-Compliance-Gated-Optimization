import json
import streamlit as st
import plotly.graph_objects as go

from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage
from modules.baselines import BaselineCalculator

st.set_page_config(page_title="Phase 5: Scoring", layout="wide", page_icon="📊")

st.title("📊 Phase 5: ATS & Job-Compatibility Scoring")
st.markdown("**Day 5 Deliverable:** Formal scoring with component breakdown")

COMPONENT_LABELS = {
    "lexical_coverage": "Lexical Coverage",
    "fuzzy_coverage": "Fuzzy Coverage",
    "tfidf_relevance": "TF-IDF Relevance",
    "tfidf_cosine_similarity": "TF-IDF Cosine Similarity",
    "section_distribution": "Section Distribution",
    "summary_similarity": "Summary Similarity",
    "experience_alignment": "Experience Alignment",
    "skills_alignment": "Skills Alignment",
    "education_match": "Education Match",
    "domain_relevance": "Domain Relevance",
}

# ---------- Helpers ----------

COMPONENT_LABELS = {
    "lexical_coverage": "Lexical Coverage",
    "fuzzy_coverage": "Fuzzy Coverage",
    "tfidf_relevance": "TF-IDF Relevance",
    "tfidf_cosine_similarity": "TF-IDF Cosine Similarity",
    "section_distribution": "Section Distribution",
    "summary_similarity": "Summary Similarity",
    "experience_alignment": "Experience Alignment",
    "skills_alignment": "Skills Alignment",
    "education_match": "Education Match",
    "domain_relevance": "Domain Relevance",
}

def to_dict(model_or_dict):
    """Pydantic v2: model_dump(); v1: dict(); else pass-through."""
    if model_or_dict is None:
        return {}
    if hasattr(model_or_dict, "model_dump"):
        return model_or_dict.model_dump()
    if hasattr(model_or_dict, "dict"):
        return model_or_dict.dict()
    return dict(model_or_dict) if isinstance(model_or_dict, dict) else {}

def normalize_jd_education_fields(jd: dict) -> dict:
    """
    Option A alignment: ensure JD dict contains BOTH:
      - education_required_text
      - education_preferred_text

    If your extractor still outputs a single `education` field, we map it to required_text
    and leave preferred_text empty unless we can find an obvious preferred field.
    """
    jd = dict(jd or {})

    # Required
    if not isinstance(jd.get("education_required_text"), str):
        jd["education_required_text"] = ""
    if not jd["education_required_text"].strip():
        for k in (
            "education_required",
            "required_education",
            "education_requirement",
            "education_required_level_text",
            "education",  # legacy single-field
        ):
            v = jd.get(k)
            if isinstance(v, str) and v.strip():
                jd["education_required_text"] = v.strip()
                break

    # Preferred
    if not isinstance(jd.get("education_preferred_text"), str):
        jd["education_preferred_text"] = ""
    if not jd["education_preferred_text"].strip():
        for k in (
            "education_preferred",
            "preferred_education",
            "education_preference",
            "preferred_degree",
            "preferred_qualification",
        ):
            v = jd.get(k)
            if isinstance(v, str) and v.strip():
                jd["education_preferred_text"] = v.strip()
                break

    return jd

def safe_band_text(band: str | None) -> str:
    if not band:
        return "N/A"
    return str(band).upper()

# ---------- Initialize session ----------
if "scoring_report" not in st.session_state:
    st.session_state.scoring_report = None

# ---------- Load CV and JD ----------
try:
    cv_structured = Storage.load_structured_cv()
    jd_enhanced = Storage.load_enhanced_jd()
    cv_raw = Storage.load_raw_cv() if hasattr(Storage, "load_raw_cv") else ""
    jd_raw = Storage.load_raw_jd() if hasattr(Storage, "load_raw_jd") else ""
except FileNotFoundError:
    st.error("⚠️ Please complete Phases 1–4 first")
    st.stop()

cv_dict = to_dict(cv_structured)
jd_dict = normalize_jd_education_fields(to_dict(jd_enhanced))

# ---------- Education Match (Spec) inputs ----------
st.header("🎓 Education Match Inputs (Spec Mode)")
with st.expander("View / edit JD education required & preferred fields", expanded=False):
    st.caption(
        "Option A alignment: scoring uses BOTH required and preferred education text. "
        "If your JD extractor only produced a single `education` field, it has been mapped to `education_required_text`."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        edu_required = st.text_area(
            "JD — Education (Required)",
            value=jd_dict.get("education_required_text", ""),
            height=120,
            help="Examples: 'Bachelor’s degree in CS', 'Master’s required', 'BS required'. Leave empty if JD has no requirement.",
        )
    with col_b:
        edu_preferred = st.text_area(
            "JD — Education (Preferred)",
            value=jd_dict.get("education_preferred_text", ""),
            height=120,
            help="Examples: 'Master’s preferred', 'PhD preferred'. Leave empty if not mentioned.",
        )

    jd_dict["education_required_text"] = (edu_required or "").strip()
    jd_dict["education_preferred_text"] = (edu_preferred or "").strip()

st.divider()

# ===== SCORING EXECUTION =====
st.header("🚀 Step 1: Compute Scores")

if st.button("▶️ Run Scoring Pipeline", type="primary", use_container_width=True):
    with st.spinner("Computing ATS and Job-Compatibility scores..."):
        try:
            pipeline = ScoringPipeline()
            report = pipeline.score_cv_jd_pair(cv_dict, jd_dict, cv_raw, jd_raw)

            st.session_state.scoring_report = report

            # --- BASELINES (FOR PAPER) ---
            try:
                # Reuse feature_extractor from pipeline for efficiency
                baseline_calc = BaselineCalculator(pipeline.feature_extractor)
                
                # Compute
                jaccard_res = baseline_calc.compute_jaccard(cv_raw, jd_raw)
                embedding_sim = baseline_calc.compute_embedding_similarity(cv_raw, jd_raw)
                
                st.session_state["baselines"] = {
                     "jaccard": jaccard_res,
                     "embedding_sim": embedding_sim
                }
            except Exception as e:
                import logging
                logging.error(f"Baseline calc failed: {e}")
                st.session_state["baselines"] = {}
            
            # --- BRIDGE FOR PHASE 6 ---
            # Phase 6 expects specific keys that might not be set if we just jumped here.
            # We reconstruct/load them into session_state to ensure continuity.
            
            st.session_state["phase5_bundle"] = {
                "ats": {
                    "score": report.get("ats_score", 0.0),
                    "components": report.get("ats_components", {})
                },
                "job_compatibility": {
                    "score": report.get("jobfit_score", 0.0),
                    # map components if available
                    "components": report.get("jobfit_components", {})
                }
            }

            # Ensure baseline objects are in session if not already
            if "cv_shell" not in st.session_state:
                st.session_state["cv_shell"] = cv_dict
            if "jd_structured" not in st.session_state:
                st.session_state["jd_structured"] = jd_dict
            
            # Load other missing pieces via Storage if possible
            if "mapping" not in st.session_state and hasattr(Storage, "load_mapping"):
                try:
                    st.session_state["mapping"] = Storage.load_mapping()
                except:
                    pass
            
            if "phase4_report" not in st.session_state and hasattr(Storage, "load_compliance_report"):
                try:
                    st.session_state["phase4_report"] = Storage.load_compliance_report()
                except:
                    pass

            if hasattr(Storage, "save_scoring_report"):
                Storage.save_scoring_report(report)

            st.success("✅ Scoring complete! Phase 6 data prepared.")
        except Exception as e:
            st.error(f"❌ Scoring failed: {e}")
            import traceback
            st.code(traceback.format_exc())

st.divider()

# ===== DISPLAY RESULTS =====
if st.session_state.scoring_report:
    report = st.session_state.scoring_report or {}

    ats_score = float(report.get("ats_score", 0.0))
    jobfit_score = float(report.get("jobfit_score", 0.0))
    interpretation = report.get("interpretation", {}) or {}

    # Overall Scores
    st.header("📈 Overall Scores")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ATS Score")
        fig_ats = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=ats_score,
                title={"text": "ATS Score"},
                delta={"reference": 75, "increasing": {"color": "green"}},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 75], "color": "lightblue"},
                        {"range": [75, 90], "color": "lightgreen"},
                        {"range": [90, 100], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            )
        )
        fig_ats.update_layout(height=300)
        st.plotly_chart(fig_ats, use_container_width=True)

        st.caption(f"**Band:** {safe_band_text(interpretation.get('ats_band'))}")

    with col2:
        st.subheader("Job-Compatibility Score")
        fig_jobfit = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=jobfit_score,
                title={"text": "Job-Compatibility Score"},
                delta={"reference": 75, "increasing": {"color": 'green'}},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkorange"},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 75], "color": "lightyellow"},
                        {"range": [75, 90], "color": "lightgreen"},
                        {"range": [90, 100], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            )
        )
        fig_jobfit.update_layout(height=300)
        st.plotly_chart(fig_jobfit, use_container_width=True)

        st.caption(f"**Band:** {safe_band_text(interpretation.get('jobfit_band'))}")

    st.divider()

    # Component Breakdowns
    st.header("🔍 Score Component Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ATS Components")
        ats_comp = report.get("ats_components", {}) or {}
        if not ats_comp:
            st.info("No ATS component breakdown found in report.")
        else:
            for component, score in ats_comp.items():
                try:
                    s = float(score)
                except Exception:
                    s = score
                label = COMPONENT_LABELS.get(component, component.replace("_", " ").title())
                st.metric(
                    label,
                    f"{s:.3f}" if isinstance(s, float) else str(s),
                    help="Contribution to overall ATS score",
                )

    with col2:
        st.subheader("Job-Compatibility Components")
        jobfit_comp = report.get("jobfit_components", {}) or {}
        if not jobfit_comp:
            st.info("No JobFit component breakdown found in report.")
        else:
            for component, score in jobfit_comp.items():
                try:
                    s = float(score)
                except Exception:
                    s = score
                label = COMPONENT_LABELS.get(component, component.replace("_", " ").title())
                st.metric(
                    label,
                    f"{s:.3f}" if isinstance(s, float) else str(s),
                    help="Contribution to overall Job-Compatibility score",
                )

    st.divider()

    # Interpretation & Feedback
    st.header("💡 Interpretation & Recommendations")

    feedback = (interpretation.get("feedback") or []) if isinstance(interpretation, dict) else []
    if not feedback:
        st.info("No feedback items found in report interpretation.")
    else:
        for feedback_item in feedback:
            st.info(str(feedback_item))

    # Feature Details
    with st.expander("📊 Raw Features & Statistics"):
        st.json(report.get("ats_features", {}))

    st.divider()

    st.divider()

    # ===== ABLATION STUDY =====
    st.header("🧪 Ablation Study (Component Impact)")
    st.caption("How much does each component contribute to the final score? (Calculated by removing one component at a time)")

    ab_col1, ab_col2 = st.columns(2)

    with ab_col1:
        st.subheader("ATS Score Ablation")
        ats_ab = report.get("ats_ablation", [])
        if ats_ab:
            st.dataframe(
                ats_ab,
                column_config={
                    "component_removed": "Component Removed",
                    "score_drop": st.column_config.NumberColumn("Drop (%)", format="%.2f"),
                    "score_without_component": st.column_config.NumberColumn("Score w/o (%)", format="%.2f"),
                    "weight_percent": st.column_config.NumberColumn("Weight (%)", format="%.1f"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No ablation data available for ATS score.")

    with ab_col2:
        st.subheader("JobFit Score Ablation")
        fit_ab = report.get("jobfit_ablation", [])
        if fit_ab:
            st.dataframe(
                fit_ab,
                column_config={
                    "component_removed": "Component Removed",
                    "score_drop": st.column_config.NumberColumn("Drop (%)", format="%.2f"),
                    "score_without_component": st.column_config.NumberColumn("Score w/o (%)", format="%.2f"),
                    "weight_percent": st.column_config.NumberColumn("Weight (%)", format="%.1f"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No ablation data available for JobFit score.")
            
    st.divider()

    # ===== BASELINES (FOR PAPER) =====
    st.header("🔬 Baselines (for paper)")
    
    baselines = st.session_state.get("baselines", {})
    if not baselines:
         st.info("Run scoring pipeline to generate baselines.")
    else:
        jaccard = baselines.get("jaccard", {})
        embedding_score = baselines.get("embedding_sim")

        b_col1, b_col2 = st.columns(2)
        
        with b_col1:
            st.subheader("1. Keyword Overlap (Jaccard)")
            j_score = jaccard.get("jaccard_index", 0.0)
            j_pct_cv = jaccard.get("overlap_percent_cv", 0.0)
            
            st.metric("Jaccard Index", f"{j_score:.4f}")
            st.caption(f"Overlap: **{jaccard.get('intersection_count', 0)}** tokens")
            st.progress(j_score, text=f"Index: {j_score:.2f}")
            
            st.write(f"**Coverage (CV):** {j_pct_cv:.1%}")
            
            with st.expander("See matched tokens (Top 10)"):
                st.write(", ".join(jaccard.get("overlap_tokens", [])))
                
        with b_col2:
            st.subheader("2. Embedding Similarity")
            if embedding_score is None:
                st.warning("Embedding similarity unavailable (check API key/config).")
            else:
                st.metric("Cosine Similarity", f"{embedding_score:.4f}")
                # Clamp for progress bar just in case
                disp_score = max(0.0, min(1.0, embedding_score))
                st.progress(disp_score, text=f"Cosine: {embedding_score:.4f}")
                st.caption("Based on sentence-transformers embeddings of full text.")

        # Optional: Correlation vs Human Labels
        # Check for evaluation.csv or similar in data/
        import os
        import pandas as pd
        
        # Heuristic path check
        eval_path = "data/evaluation.csv" 
        if os.path.exists(eval_path):
            st.subheader("3. Correlation vs Human Labels")
            try:
                df = pd.read_csv(eval_path)
                required_cols = ["HumanFit", "JobFit", "KeywordOverlap", "EmbeddingSim"]
                # Only if columns exist
                if set(["HumanFit"]).issubset(df.columns):
                     st.dataframe(df.head())
                     st.info("Correlation analysis would go here if full dataset available.")
            except Exception:
                pass

    # Download
    report_json = json.dumps(report, indent=2)
    st.download_button(
        "📥 Download Scoring Report (JSON)",
        report_json,
        "scoring_report.json",
        "application/json",
    )

# Footer
st.divider()
st.caption("Phase 5 Complete ✓ | Next: CV Rewriting Engine (Phase 6)")
