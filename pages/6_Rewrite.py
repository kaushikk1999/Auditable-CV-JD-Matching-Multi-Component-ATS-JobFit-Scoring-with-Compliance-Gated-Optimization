# pages/6_Rewrite.py
import streamlit as st
import traceback

from core.phase6_engine import generate_suggestions
from core.suggestions_models import RewriteSuggestionBundle
from modules.storage import Storage

def render_suggestions_tabs(bundle: RewriteSuggestionBundle) -> None:
    """Helper to render the tabs once we have a suggestion bundle."""
    # Tabs: Top Priorities, Summary, Experience Bullets, Skills, Cleanup
    tab_top, tab_summary, tab_exp, tab_skills, tab_cleanup = st.tabs(
        ["Top Priorities", "Summary", "Experience Bullets", "Skills", "Cleanup"]
    )

    # Initialize expand_all state if not present
    if "expand_all" not in st.session_state:
        st.session_state["expand_all"] = False

    def toggle_expand_all():
        st.session_state["expand_all"] = not st.session_state["expand_all"]
        
    # Add Expand All button in the sidebar or top area? The user asked for "a button called expand all"
    # To avoid layout issues, let's place it right before the content or in sidebar.
    # Placement: Right above the first tab content? or maybe global?
    # Since this function renders tabs, putting it outside/before tabs is better.
    # We will assume the button is rendered OUTSIDE this function or passed in?
    # BUT, the function renders existing tabs.
    # Let's add the button inside this function for now, or just use the state directly.
    # Actually, let's put the button right here.
    
    # We use a state variable for expanded checks
    is_expanded = st.session_state["expand_all"]


    with tab_top:
        st.subheader("Top Priorities")
        st.write(
            "Focus first on HIGH-impact suggestions in bullets and skills to move ATS "
            "and Job Compatibility towards the target."
        )
        
        # Simple prioritization view
        high_impact = []
        if bundle.bullets:
            high_impact.extend([b for b in bundle.bullets if b.impact == "HIGH"])
        if bundle.skills:
             high_impact.extend([s for s in bundle.skills if s.impact == "HIGH"])
             
        if not high_impact:
             st.info("No HIGH-impact suggestions found. Review other tabs for improvements.")
        else:
             for idx, item in enumerate(high_impact):
                 # Dynamic label construction based on suggestion type
                 label_prefix = ""
                 
                 # Check for BulletSuggestion attributes
                 if hasattr(item, "section") and hasattr(item, "role_index"):
                     section = getattr(item, "section", "experience").title()
                     role_idx = getattr(item, "role_index", 0) + 1
                     bullet_idx = getattr(item, "bullet_index", None)
                     
                     if bullet_idx is not None:
                         label_prefix = f"**{section} Role #{role_idx}, Bullet #{bullet_idx + 1}:** "
                     else:
                         label_prefix = f"**{section} Role #{role_idx} (New Bullet):** "
                 
                 # Check for SkillSuggestion attributes
                 elif hasattr(item, "to_add"):
                     added = ", ".join(getattr(item, "to_add", [])[:3])
                     if added:
                         label_prefix = f"**Skills (Add '{added}...'):** "
                     else:
                         label_prefix = "**Skills:** "
                 
                 # Check for Cleanup attributes
                 elif hasattr(item, "before"):
                     label_prefix = "**Cleanup:** "
                 
                 reason = getattr(item, "reason", "Improvement suggestion")
                 st.markdown(f"{idx+1}. {label_prefix}{reason}")

    with tab_summary:
        st.subheader("Summary suggestions")
        if not bundle.summary:
            st.info("No summary suggestions generated.")
        else:
            for idx, sug in enumerate(bundle.summary):
                with st.expander(f"[{sug.impact}] {sug.reason}", expanded=is_expanded):
                    if sug.before:
                        st.markdown("**Current summary (snippet):**")
                        st.write(sug.before)
                    st.markdown("**Suggested improved wording (example):**")
                    st.write(sug.after_example)
                    st.checkbox("✅ I applied this change", key=f"phase6_summary_{idx}")

    with tab_exp:
        st.subheader("Experience bullet suggestions")
        if not bundle.bullets:
            st.info("No experience bullet suggestions generated.")
        else:
            for idx, sug in enumerate(bundle.bullets):
                bullet_label = (
                    f"Role #{sug.role_index + 1}, "
                    f"{'new bullet' if sug.bullet_index is None else 'Bullet #' + str(sug.bullet_index + 1)}"
                )
                with st.expander(f"[{sug.impact}] {sug.reason} — {bullet_label}", expanded=is_expanded):
                    if sug.before:
                        st.markdown("**Current bullet:**")
                        st.write(sug.before)
                    else:
                        st.markdown("**This will be a new bullet to add.**")
                    st.markdown("**Suggested improved bullet (example):**")
                    st.write(sug.after_example)
                    st.checkbox("✅ I applied this change", key=f"phase6_bullet_{idx}")

    with tab_skills:
        st.subheader("Skill suggestions")
        if not bundle.skills:
            st.info("No skill suggestions generated.")
        else:
            for idx, sug in enumerate(bundle.skills):
                with st.expander(f"[{sug.impact}] {sug.reason}", expanded=is_expanded):
                    if sug.to_add:
                        st.markdown("**Consider adding:**")
                        st.write(", ".join(sug.to_add))
                    if sug.to_remove:
                        st.markdown("**Consider removing or de-emphasizing:**")
                        st.write(", ".join(sug.to_remove))
                    st.checkbox("✅ I applied this change", key=f"phase6_skill_{idx}")

    with tab_cleanup:
        st.subheader("Cleanup suggestions (buzzwords / stopwords)")
        if not bundle.cleanup:
            st.info("No cleanup suggestions generated.")
        else:
            for idx, sug in enumerate(bundle.cleanup):
                with st.expander(f"[{sug.impact}] {sug.reason}", expanded=is_expanded):
                    if sug.before:
                        st.markdown("**Original text:**")
                        st.write(sug.before)
                    st.markdown("**Cleaner example wording:**")
                    st.write(sug.after_example)
                    st.checkbox("✅ I applied this change", key=f"phase6_cleanup_{idx}")


def _load_debug_data():
    """Populates session_state with dummy data for testing."""
    st.session_state["cv_shell"] = {
        "summary": "Innovative data enthusiast.",
        "skills": ["Python", "Pandas"],
        "experience": [
            {
                "title": "ML Coach",
                "company": "Clevered",
                "dates": "2024",
                "bullets": ["I am a hard-working professional."],
            }
        ],
        "projects": [],
        "certificates": [],
    }
    st.session_state["mapping"] = {
        "present": ["python", "machine learning"],
        "missing_critical": [{"keyword": "SQL", "source": "jd"}],
        "missing_bonus": [],
        "irrelevant": [],
    }
    st.session_state["phase4_report"] = {
        "buzzwords": ["innovative"],
        "stopwords": ["and", "in", "for"],
        "duplicate_words": [],
        "duplicate_lines": [],
    }
    st.session_state["phase5_bundle"] = {
        "ats": {
            "score": 55.0,
            "components": {
                "coverage": {"value": 60.0},
                "quantified": {"value": 40.0},
                "uniqueness": {"value": 70.0},
                "buzzword": {"value": 80.0},
                "stopword": {"value": 75.0},
            },
        },
        "job_compatibility": {"score": 50.0},
        "scorecard": {},
    }
    st.session_state["jd_structured"] = {
        "title": "Data Scientist – Education",
        "must_have_skills": ["Python", "SQL", "Statistics"],
        "nice_to_have_skills": ["Cloud", "BigQuery"],
    }
    st.success("✅ Debug data loaded!")
    st.rerun()


def _try_recover_state() -> bool:
    """
    Attempts to recover missing session state from disk (via Storage).
    Returns True if enough data is recovered to proceed, False otherwise.
    """
    try:
        # 1. Recover CV Shell
        if "cv_shell" not in st.session_state:
            try:
                cv = Storage.load_structured_cv()
                st.session_state["cv_shell"] = cv.model_dump() if hasattr(cv, "model_dump") else cv
            except Exception:
                pass

        # 2. Recover JD
        if "jd_structured" not in st.session_state:
            try:
                jd = Storage.load_enhanced_jd()
                st.session_state["jd_structured"] = jd.model_dump() if hasattr(jd, "model_dump") else jd
            except Exception:
                pass

        # 3. Recover Phase 4 Report
        if "phase4_report" not in st.session_state:
            try:
                st.session_state["phase4_report"] = Storage.load_compliance_report()
            except Exception:
                pass

        # 4. Recover Mapping (from Analysis Report)
        if "mapping" not in st.session_state:
            try:
                analysis = Storage.load_analysis_report()
                gap = analysis.gap_analysis
                # Transform to 'mapping' structure expected by Phase 6
                # mapping = { "present": [], "missing_critical": [], "missing_bonus": [], "irrelevant": [] }
                present = [k.keyword for k in gap.present_keywords]
                
                missing_critical = []
                missing_bonus = []
                for k in gap.missing_keywords:
                    # heuristic: 'required' -> critical, else bonus
                    if k.jd_priority == "required":
                        missing_critical.append({"keyword": k.keyword, "source": "jd"})
                    else:
                        missing_bonus.append({"keyword": k.keyword, "source": "jd"})
                        
                st.session_state["mapping"] = {
                    "present": present,
                    "missing_critical": missing_critical,
                    "missing_bonus": missing_bonus,
                    "irrelevant": gap.irrelevant_keywords
                }
            except Exception:
                pass

        # 5. Recover Phase 5 Bundle (from Scoring Report)
        if "phase5_bundle" not in st.session_state:
            try:
                scoring = Storage.load_scoring_report()
                st.session_state["phase5_bundle"] = {
                    "ats": {
                        "score": scoring.get("ats_score", 0.0),
                        "components": scoring.get("ats_components", {})
                    },
                    "job_compatibility": {
                        "score": scoring.get("jobfit_score", 0.0),
                        "components": scoring.get("jobfit_components", {})
                    }
                }
            except Exception:
                pass
                
        # Final Verification
        required = ["cv_shell", "jd_structured", "phase4_report", "mapping", "phase5_bundle"]
        if all(k in st.session_state for k in required):
            return True
        return False

    except Exception as e:
        # Silent fail on recovery, let the main guards handle messaging
        # print(f"DEBUG: Recovery failed: {e}") 
        return False


def render_phase6():
    st.title("Phase 6 — Guided Rewrite Suggestions (No Auto-Edit)")

    # 0. Attempt Auto-Recovery if needed
    _try_recover_state()

    # 1. Gather required data from session_state
    phase5_bundle = st.session_state.get("phase5_bundle")
    mapping = st.session_state.get("mapping")
    cv_shell = st.session_state.get("cv_shell")
    phase4_report = st.session_state.get("phase4_report")
    jd_structured = st.session_state.get("jd_structured")

    # 2. Hard guard: Check if data is missing
    missing_keys = []
    if not phase5_bundle: missing_keys.append("phase5_bundle")
    if not mapping: missing_keys.append("mapping")
    if not cv_shell: missing_keys.append("cv_shell")
    if not phase4_report: missing_keys.append("phase4_report")
    if not jd_structured: missing_keys.append("jd_structured")

    if missing_keys:
        st.warning(f"Missing Phase data: {', '.join(missing_keys)}")
        st.info("You seem to have skipped previous phases (or data files are missing). Load debug data to test this page?")
        if st.button("🛠 Load Debug Data"):
            _load_debug_data()
        else:
            st.error("Cannot proceed without required data. Please complete Phases 2-5.")
            st.stop()
        return

    # 3. Display current context
    current_ats = float(phase5_bundle.get("ats", {}).get("score", 0.0))
    current_job = float(phase5_bundle.get("job_compatibility", {}).get("score", 0.0))
    target_min = 80.0

    st.markdown(f"**Current scores** — ATS: `{current_ats:.1f}` / Job Compatibility: `{current_job:.1f}`")
    st.markdown(f"**Target minimum** — both ≥ `{target_min}`")

    if current_ats >= target_min and current_job >= target_min:
        st.info(
            "Your CV already meets the minimum target. "
            "Suggestions below will focus on refinement and pushing higher."
        )

    # 4. Generate Button
    if st.button("✏️ Generate improvement suggestions", type="primary", use_container_width=True):
        with st.spinner("Analyzing gaps and drafting suggestions..."):
            try:
                bundle = generate_suggestions(
                    cv_shell=cv_shell,
                    mapping=mapping,
                    phase4_report=phase4_report,
                    phase5_bundle=phase5_bundle,
                    jd_structured=jd_structured,
                    target_min_score=target_min,
                )
                # Save to session_state
                st.session_state["phase6_suggestions"] = bundle
            except Exception as e:
                st.error(f"Error while generating suggestions: {e}")
                # Print full traceback to UI for debugging
                st.code(traceback.format_exc())
                # Stop execution here
                return

    # 5. Render Results
    bundle = st.session_state.get("phase6_suggestions")
    if bundle is None:
        st.info("Click **Generate improvement suggestions** to see prioritized suggestions.")
        return

    # Check for error signature
    if bundle.meta and bundle.meta.get("error") == "JSON_PARSE":
        st.error("⚠️ Failed to parse suggestions from the AI model.")
        with st.expander("Details (Raw Output)"):
            st.code(bundle.meta.get("raw_response", ""), language="text")
        st.warning("Please try clicking 'Generate' again. The model sometimes outputs invalid JSON.")
        return

    # Add Expand All Button
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("Expand All" if not st.session_state.get("expand_all") else "Collapse All"):
            st.session_state["expand_all"] = not st.session_state.get("expand_all", False)
            st.rerun()

    render_suggestions_tabs(bundle)


if __name__ == "__main__":
    render_phase6()
