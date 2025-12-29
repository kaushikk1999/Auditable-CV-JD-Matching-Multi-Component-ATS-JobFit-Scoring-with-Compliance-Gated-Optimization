import streamlit as st
from modules.compliance_checker import ComplianceAuditor
from modules.storage import Storage
from modules.schemas import StructuredCV
import json

st.set_page_config(page_title="Phase 4: Compliance Audit", layout="wide")

st.title("🔍 Phase 4: Compliance Audit & Rule Enforcement")
st.markdown("**Day 4 Deliverable:** Pre-rewrite compliance check against ATS optimization rules")

# Initialize
if "compliance_report" not in st.session_state:
    st.session_state.compliance_report = None

auditor = ComplianceAuditor()

# Load CV
try:
    cv = Storage.load_structured_cv()
except FileNotFoundError:
    st.error("⚠️ Please complete Phase 1-3 first (structured CV not found)")
    st.stop()

# ===== CONFIGURATION =====
st.header("⚙️ Step 1: Audit Configuration")

col1, col2, col3 = st.columns(3)
with col1:
    enforce_buzzwords = st.checkbox("Enforce Buzzword Ban", value=True)
with col2:
    enforce_stopwords = st.checkbox("Enforce Stopword Ban", value=True)
with col3:
    enforce_uniqueness = st.checkbox("Enforce Word Uniqueness", value=True)

st.divider()

# ===== AUDIT EXECUTION =====
st.header("🚀 Step 2: Run Compliance Audit")

# Reconstruct CV text from structured data
def structured_cv_to_text(cv: StructuredCV) -> str:
    """Convert structured CV back to plain text for auditing."""
    sections = []
    
    # Contact
    sections.append(f"{cv.contact_info.full_name}\n{cv.contact_info.email}")
    
    # Summary
    if cv.summary:
        sections.append(f"\nSUMMARY\n{cv.summary.text}")
    
    # Skills
    if cv.skills:
        skills_text = "\nSKILLS\n"
        for cat in cv.skills:
            skills_text += f"{cat.category_name}: {', '.join(cat.skills)}\n"
        sections.append(skills_text)
    
    # Experience
    if cv.experience:
        exp_text = "\nEXPERIENCE\n"
        for exp in cv.experience:
            exp_text += f"{exp.job_title} | {exp.company_name} | {exp.start_date} - {exp.end_date}\n"
            for bullet in exp.bullets:
                exp_text += f"• {bullet.text}\n"
        sections.append(exp_text)
    
    # Projects
    if cv.projects:
        proj_text = "\nPROJECTS\n"
        for proj in cv.projects:
            proj_text += f"{proj.project_name}\n"
            for bullet in proj.bullets:
                proj_text += f"• {bullet.text}\n"
        sections.append(proj_text)
    
    # Education
    if cv.education:
        edu_text = "\nEDUCATION\n"
        for edu in cv.education:
            edu_text += f"{edu.degree}, {edu.institution}\n"
        sections.append(edu_text)
    
    return "\n".join(sections)

# Extract bullets
def extract_bullets(cv: StructuredCV) -> list:
    """Extract all bullet points from CV."""
    bullets = []
    if cv.experience:
        for exp in cv.experience:
            bullets.extend([b.text for b in exp.bullets])
    if cv.projects:
        for proj in cv.projects:
            bullets.extend([b.text for b in proj.bullets])
    return bullets

cv_text = structured_cv_to_text(cv)
bullets = extract_bullets(cv)

if st.button("▶️ Run Audit", type="primary", use_container_width=True):
    with st.spinner("Running compliance checks..."):
        # Run audit
        report = auditor.audit_cv_text(cv_text, bullets)
        st.session_state.compliance_report = report
        
        # Save report
        Storage.save_compliance_report(report)
        
        if report["overall_passed"]:
            st.success("✅ All critical compliance checks passed!")
        else:
            st.error("❌ COMPLIANCE BREACH DETECTED - See violations below")

st.divider()

# ===== DISPLAY RESULTS =====
if st.session_state.compliance_report:
    report = st.session_state.compliance_report
    
    # Overall Status
    st.header("📊 Audit Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_icon = "✅" if report["overall_passed"] else "❌"
        st.metric("Overall Status", f"{status_icon} {'PASS' if report['overall_passed'] else 'FAIL'}")
    
    with col2:
        st.metric("Critical Violations", len(report["critical_violations"]))
    
    with col3:
        st.metric("Warnings", len(report["warnings"]))
    
    st.divider()
    
    # Detailed Check Results
    st.header("🔍 Detailed Check Results")
    
    checks = report["checks"]
    
    # 1. Buzzword Audit
    with st.expander("1️⃣ Buzzword Audit", expanded=not checks["buzzword_audit"]["passed"]):
        buzz = checks["buzzword_audit"]
        if buzz["passed"]:
            st.success(f"✅ {buzz['status']} - No banned jargon detected")
        else:
            st.error(f"❌ {buzz['status']} - {buzz['violation_count']} violations found")
            st.markdown("**Banned Terms Detected:**")
            st.write(", ".join(buzz["violations"][:20]))
            if buzz["violation_count"] > 20:
                st.caption(f"...and {buzz['violation_count'] - 20} more")
    
    # 2. Stopword Audit
    with st.expander("2️⃣ Stopword Audit", expanded=not checks["stopword_audit"]["passed"]):
        stop = checks["stopword_audit"]
        if stop["passed"]:
            st.success(f"✅ {stop['status']} - Zero filler words")
        else:
            st.error(f"❌ {stop['status']} - {stop['violation_count']} stopwords found")
            st.markdown("**Stopwords Detected:**")
            violation_freq = {}
            for word in stop["violations"]:
                violation_freq[word] = cv_text.lower().count(word)
            
            # Sort by frequency
            sorted_violations = sorted(violation_freq.items(), key=lambda x: x[1], reverse=True)
            
            import pandas as pd
            df = pd.DataFrame(sorted_violations[:20], columns=["Stopword", "Frequency"])
            st.dataframe(df, use_container_width=True)
    
    # 3. Word Uniqueness
    with st.expander("3️⃣ Word Uniqueness Report", expanded=not checks["word_uniqueness"]["passed"]):
        uniq = checks["word_uniqueness"]
        if uniq["passed"]:
            st.success(f"✅ {uniq['status']} - Every word used only once")
        else:
            st.error(f"❌ {uniq['status']} - {uniq['violation_count']} words repeated")
            st.markdown(f"**Total duplicate instances:** {uniq['total_duplicate_instances']}")
            
            # Sort duplicates by frequency
            sorted_dups = sorted(uniq["duplicates"].items(), key=lambda x: x[1], reverse=True)
            
            import pandas as pd
            df = pd.DataFrame(sorted_dups[:30], columns=["Word", "Occurrences"])
            st.dataframe(df, use_container_width=True, height=400)
    
    # 4. Duplicate Terms
    with st.expander("4️⃣ Duplicate Term Check"):
        dup = checks["duplicate_terms"]
        if dup["passed"]:
            st.success(f"✅ {dup['status']}")
        else:
            st.warning(f"⚠️ {dup['status']} - {dup['violation_count']} repeated phrases")
            if dup["duplicate_phrases"]:
                st.write(", ".join(dup["duplicate_phrases"]))
    
    # 5. Quantification Integrity
    with st.expander("5️⃣ Quantification Integrity Audit", expanded=True):
        quant = checks["quantification_integrity"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Compliance Rate", f"{quant['compliance_rate']:.1%}")
        with col2:
            st.metric("Quantified Bullets", f"{len(quant['compliant_bullets'])}/{quant['total_bullets']}")
        
        if not quant["passed"]:
            st.warning(f"⚠️ {quant['status']}")
            st.markdown("**Non-compliant bullets:**")
            for idx in quant["non_compliant_bullets"][:10]:
                if idx < len(bullets):
                    st.caption(f"Bullet {idx+1}: {bullets[idx][:100]}...")
        else:
            st.success(f"✅ {quant['status']}")
    
    # 6. Brevity Analysis
    with st.expander("6️⃣ Brevity & Word Count Analysis"):
        brev = checks["brevity_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Word Count**")
            st.metric("Current", brev["word_count"])
            st.caption(f"Target: {brev['word_count_target']}")
            if brev["word_count_status"] == "WITHIN_RANGE":
                st.success("✅ Within target range")
            else:
                diff = brev["word_count"] - 425  # Mid-point
                st.warning(f"⚠️ {abs(diff)} words {'over' if diff > 0 else 'under'} target")
        
        with col2:
            st.markdown("**Bullet Count**")
            st.metric("Current", brev["bullet_count"])
            st.caption(f"Target: {brev['bullet_count_target']}")
            if brev["bullet_count_status"] == "BULLET_COUNT_OK":
                st.success("✅ Optimal density")
            else:
                st.warning(f"⚠️ Adjust bullet count")
    
    st.divider()
    
    # Recommendations
    st.header("💡 Recommendations")
    
    if report["overall_passed"]:
        st.success("CV passes all critical compliance checks. Ready for Phase 5 scoring.")
    else:
        st.error("**Critical violations must be fixed before proceeding to rewriting (Phase 6):**")
        for violation in report["critical_violations"]:
            st.markdown(f"- Fix **{violation}** violations")
    
    if report["warnings"]:
        st.warning("**Recommended improvements:**")
        for warning in report["warnings"]:
            st.markdown(f"- Address **{warning}** issues")
    
    # Download Report
    st.divider()
    report_json = json.dumps(report, indent=2)
    st.download_button(
        "📥 Download Full Audit Report (JSON)",
        report_json,
        "compliance_audit_report.json",
        "application/json"
    )

# Footer
st.divider()
st.caption("Phase 4 Complete ✓ | Next: Formal ATS Scoring (Phase 5)")
