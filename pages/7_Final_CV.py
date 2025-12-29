import streamlit as st
from modules.cv_assembler import CVAssembler
from modules.exporters import PDFExporter, DOCXExporter, HTMLExporter, JSONExporter
from modules.compliance_checker import ComplianceAuditor
from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage
from pathlib import Path
import tempfile
import json

st.set_page_config(
    page_title="Phase 7: Final CV Delivery",
    layout="wide",
    page_icon="🎓"
)

st.title("🎓 Phase 7: Final Optimized CV Delivery")
st.markdown("**Day 7 Deliverable:** Professional CV export with ≥95 ATS + JobFit scores")

# Initialize
if "final_cv" not in st.session_state:
    st.session_state.final_cv = None
if "final_scores" not in st.session_state:
    st.session_state.final_scores = None

# Load data
try:
    optimized_cv = Storage.load_structured_cv("cv_optimized.json")
    original_cv = Storage.load_structured_cv("cv_structured.json")
    jd = Storage.load_enhanced_jd()
except FileNotFoundError as e:
    st.error(f"⚠️ Missing data: {e}. Please complete Phases 1-6 first.")
    st.stop()

# Convert to dicts
opt_dict = optimized_cv.model_dump() if hasattr(optimized_cv, 'model_dump') else optimized_cv
orig_dict = original_cv.model_dump() if hasattr(original_cv, 'model_dump') else original_cv
jd_dict = jd.model_dump() if hasattr(jd, 'model_dump') else jd

# ===== ASSEMBLY =====
st.header("🔧 Step 1: Assemble Final CV")

if st.button("▶️ Assemble & Validate", type="primary", use_container_width=True):
    with st.spinner("Assembling final CV..."):
        try:
            # Assemble
            assembler = CVAssembler()
            final_cv = assembler.assemble(opt_dict, orig_dict)
            final_cv_text = assembler.to_text(final_cv)
            
            st.session_state.final_cv = final_cv
            st.session_state.final_cv_text = final_cv_text
            
            # Run compliance audit
            auditor = ComplianceAuditor()
            bullets = []
            for exp in final_cv.get("experience", []):
                bullets.extend([b.get("text", "") for b in exp.get("bullets", [])])
            
            compliance_report = auditor.audit_cv_text(final_cv_text, bullets)
            st.session_state.compliance_report = compliance_report
            
            # Run final scoring
            scorer = ScoringPipeline()
            score_report = scorer.score_cv_jd_pair(
                final_cv, jd_dict, final_cv_text, ""
            )
            st.session_state.final_scores = score_report
            
            # Save
            Storage.save_structured_cv(final_cv, "cv_final.json")
            
            st.success("✅ Final CV assembled and validated!")
            
        except Exception as e:
            st.error(f"❌ Assembly failed: {e}")
            import traceback
            st.code(traceback.format_exc())

st.divider()

# ===== RESULTS DISPLAY =====
if st.session_state.final_scores:
    scores = st.session_state.final_scores
    compliance = st.session_state.compliance_report
    
    # Overall Status
    st.header("📊 Final Quality Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ats_score = scores["ats_score"]
        ats_color = "green" if ats_score >= 95 else "orange" if ats_score >= 85 else "red"
        st.markdown(f"### ATS Score")
        st.markdown(f"<h1 style='color: {ats_color};'>{ats_score:.1f}</h1>", unsafe_allow_html=True)
        if ats_score >= 95:
            st.success("✅ Excellent")
        elif ats_score >= 85:
            st.warning("⚠️ Strong")
        else:
            st.error("❌ Needs Work")
    
    with col2:
        jobfit_score = scores["jobfit_score"]
        jobfit_color = "green" if jobfit_score >= 95 else "orange" if jobfit_score >= 85 else "red"
        st.markdown(f"### Job-Compatibility")
        st.markdown(f"<h1 style='color: {jobfit_color};'>{jobfit_score:.1f}</h1>", unsafe_allow_html=True)
        if jobfit_score >= 95:
            st.success("✅ Excellent")
        elif jobfit_score >= 85:
            st.warning("⚠️ Strong")
        else:
            st.error("❌ Needs Work")
    
    with col3:
        compliance_status = compliance["overall_passed"]
        st.markdown(f"### Compliance")
        if compliance_status:
            st.markdown("<h1 style='color: green;'>✓</h1>", unsafe_allow_html=True)
            st.success("All Checks Passed")
        else:
            st.markdown("<h1 style='color: red;'>✗</h1>", unsafe_allow_html=True)
            st.error(f"{len(compliance['critical_violations'])} Violations")
    
    # Score Breakdown
    with st.expander("📈 Score Component Breakdown", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ATS Components")
            for component, score in scores["ats_components"].items():
                st.metric(
                    component.replace("_", " ").title(),
                    f"{score:.1f}%"
                )
        
        with col2:
            st.subheader("Job-Compatibility Components")
            for component, score in scores["jobfit_components"].items():
                st.metric(
                    component.replace("_", " ").title(),
                    f"{score:.1f}%"
                )
    
    # Compliance Details
    with st.expander("✅ Compliance Audit Report", expanded=not compliance_status):
        if compliance_status:
            st.success("✅ All compliance checks passed!")
        else:
            st.error("❌ Critical violations detected:")
            for violation in compliance["critical_violations"]:
                st.markdown(f"- **{violation}**")
        
        # Individual checks
        checks = compliance["checks"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Buzzword Audit**")
            st.caption(checks["buzzword_audit"]["status"])
            
            st.markdown("**Stopword Audit**")
            st.caption(checks["stopword_audit"]["status"])
            
            st.markdown("**Word Uniqueness**")
            st.caption(checks["word_uniqueness"]["status"])
        
        with col2:
            st.markdown("**Quantification Integrity**")
            st.caption(checks["quantification_integrity"]["status"])
            
            st.markdown("**Brevity Analysis**")
            st.caption(f"Word count: {checks['brevity_analysis']['word_count']}")
            
            st.markdown("**Bullet Density**")
            st.caption(f"Bullets: {checks['brevity_analysis']['bullet_count']}")
    
    st.divider()
    
    # CV Preview
    st.header("📄 Final CV Preview")
    
    if st.session_state.final_cv:
        cv_text = st.session_state.final_cv_text
        st.text_area(
            "Plain Text Preview",
            cv_text,
            height=600,
            help="ATS-friendly plain text format"
        )
    
    st.divider()
    
    # Export Section
    st.header("📥 Download Optimized CV")
    
    if st.session_state.final_cv and st.session_state.final_cv_text:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # PDF
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            exporter = PDFExporter()
                            exporter.export(st.session_state.final_cv_text, Path(tmp.name))
                            
                            with open(tmp.name, 'rb') as f:
                                st.download_button(
                                    "⬇️ Download PDF",
                                    f.read(),
                                    "optimized_cv.pdf",
                                    "application/pdf",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
        
        # DOCX
        with col2:
            if st.button("📝 DOCX", use_container_width=True):
                with st.spinner("Generating DOCX..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                            exporter = DOCXExporter()
                            exporter.export(st.session_state.final_cv_text, Path(tmp.name))
                            
                            with open(tmp.name, 'rb') as f:
                                st.download_button(
                                    "⬇️ Download DOCX",
                                    f.read(),
                                    "optimized_cv.docx",
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"DOCX generation failed: {e}")
        
        # TXT
        with col3:
            st.download_button(
                "📋 TXT",
                st.session_state.final_cv_text,
                "optimized_cv.txt",
                "text/plain",
                use_container_width=True
            )
        
        # JSON
        with col4:
            json_str = json.dumps(st.session_state.final_cv, indent=2)
            st.download_button(
                "💾 JSON",
                json_str,
                "optimized_cv.json",
                "application/json",
                use_container_width=True
            )
        
        # HTML
        with col5:
            if st.button("🌐 HTML", use_container_width=True):
                with st.spinner("Generating HTML..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                            exporter = HTMLExporter()
                            exporter.export(st.session_state.final_cv_text, Path(tmp.name))
                            
                            with open(tmp.name, 'r') as f:
                                st.download_button(
                                    "⬇️ Download HTML",
                                    f.read(),
                                    "optimized_cv.html",
                                    "text/html",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"HTML generation failed: {e}")
    
    st.divider()
    
    # Success Message
    if scores["ats_score"] >= 95 and scores["jobfit_score"] >= 95 and compliance_status:
        st.balloons()
        st.success("""
        🎉 **Congratulations!** Your CV has been successfully optimized!
        
        **Achievements:**
        - ✅ ATS Score ≥95: Excellent keyword alignment
        - ✅ Job-Compatibility ≥95: Strong role fit
        - ✅ All compliance checks passed
        
        Your optimized CV is ready for job applications!
        """)
    elif scores["ats_score"] >= 85 and scores["jobfit_score"] >= 85:
        st.info("""
        ✨ **Great work!** Your CV is well-optimized.
        
        While not at the 95+ threshold, your CV demonstrates:
        - Strong keyword alignment
        - Good job compatibility
        - Professional formatting
        
        Consider minor refinements to push scores higher.
        """)
    else:
        st.warning("""
        ⚠️ **Room for Improvement**
        
        Your CV has been optimized but hasn't reached the 95+ target.
        
        **Next steps:**
        - Review missing JD keywords in Phase 3 Gap Analysis
        - Consider re-running Phase 6 rewriting with different permissions
        - Manually refine bullets to add more JD-specific terms
        """)

# Footer
st.divider()
st.caption("🎓 Phase 7 Complete | ATS CV Optimizer v1.0 | 7-Day Pipeline Finished")
