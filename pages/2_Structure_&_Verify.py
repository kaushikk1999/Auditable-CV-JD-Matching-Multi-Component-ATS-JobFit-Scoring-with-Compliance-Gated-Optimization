import streamlit as st
from modules.cv_structurer import CVStructurer
from modules.jd_analyzer import JDAnalyzer
from modules.gemini_client import GeminiClient
from modules.storage import Storage
from modules.schemas import StructuredCV, EnhancedJD
import json

st.set_page_config(page_title="Phase 2: Structure & Verify", layout="wide")

st.title("📋 Phase 2: Structured Extraction & Verification")
st.markdown("**Day 2 Deliverable:** Parse CV/JD into structured sections and verify accuracy")

# Initialize session state
if "structured_cv" not in st.session_state:
    st.session_state.structured_cv = None
if "enhanced_jd" not in st.session_state:
    st.session_state.enhanced_jd = None

# Check Phase 1 completion
if "cv_text" not in st.session_state or not st.session_state.cv_text:
    st.error("⚠️ Please complete Phase 1 first (upload CV and JD)")
    st.stop()

if "jd_structure" not in st.session_state or not st.session_state.jd_structure:
    st.error("⚠️ Please complete Phase 1 first (extract JD structure)")
    st.stop()

# ===== PHASE 2 PROCESSING =====
st.header("🔄 Step 1: Extract Structured Sections")

col1, col2 = st.columns(2)

with col1:
    if st.button("🧠 Parse CV Structure", type="primary", use_container_width=True):
        with st.spinner("Extracting CV sections with Gemini..."):
            try:
                client = GeminiClient()
                structurer = CVStructurer(client.model)
                st.session_state.structured_cv = structurer.parse(st.session_state.cv_text)
                Storage.save_structured_cv(st.session_state.structured_cv)
                
                # Validation
                validation = structurer.validate_structure(st.session_state.structured_cv)
                if validation["valid"]:
                    st.success("✅ CV structure extracted successfully!")
                else:
                    st.warning("⚠️ CV parsed with issues:")
                    for issue in validation["issues"]:
                        st.error(f"- {issue}")
                
                # Show stats
                stats = validation["stats"]
                st.info(f"""
                **Extraction Stats:**
                - Experience entries: {stats['experience_count']}
                - Total bullets: {stats['total_bullets']}
                - Projects: {stats['project_count']}
                - Skill categories: {stats['skill_categories']}
                - Certifications: {stats['certifications']}
                """)
                
            except Exception as e:
                st.error(f"❌ CV parsing failed: {e}")

with col2:
    if st.button("🎯 Enhance JD Analysis", type="primary", use_container_width=True):
        with st.spinner("Building keyword taxonomy..."):
            try:
                client = GeminiClient()
                analyzer = JDAnalyzer(client.model)
                
                # Get Phase 1 JD data
                basic_jd = st.session_state.jd_structure
                st.session_state.enhanced_jd = analyzer.enhance_jd(
                    basic_jd, 
                    st.session_state.jd_text
                )
                Storage.save_enhanced_jd(st.session_state.enhanced_jd)
                
                st.success("✅ JD enhancement complete!")
                
                # Show taxonomy stats
                tax = st.session_state.enhanced_jd.keyword_taxonomy
                st.info(f"""
                **Keyword Taxonomy:**
                - Technical skills: {len(tax.technical_skills)}
- Tools/Tech: {len(tax.tools_technologies)}
                - Soft skills: {len(tax.soft_skills)}
                - Domain knowledge: {len(tax.domain_knowledge)}
                - Must-have reqs: {len(st.session_state.enhanced_jd.must_have_requirements)}
                - Nice-to-have reqs: {len(st.session_state.enhanced_jd.nice_to_have_requirements)}
                """)
                
            except Exception as e:
                st.error(f"❌ JD enhancement failed: {e}")

st.divider()

# ===== CV STRUCTURE EDITOR =====
if st.session_state.structured_cv:
    st.header("📝 Step 2: Review & Edit CV Structure")
    
    cv = st.session_state.structured_cv
    
    # Contact Info
    with st.expander("👤 Contact Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cv.contact_info.full_name = st.text_input("Full Name*", cv.contact_info.full_name)
            cv.contact_info.email = st.text_input("Email", cv.contact_info.email or "")
            cv.contact_info.phone = st.text_input("Phone", cv.contact_info.phone or "")
        with col2:
            cv.contact_info.linkedin = st.text_input("LinkedIn", cv.contact_info.linkedin or "")
            cv.contact_info.github = st.text_input("GitHub", cv.contact_info.github or "")
            cv.contact_info.location = st.text_input("Location", cv.contact_info.location or "")
    
    # Summary
    with st.expander("📄 Professional Summary", expanded=False):
        if cv.summary:
            cv.summary.text = st.text_area("Summary", cv.summary.text, height=100)
        else:
            st.info("No summary found in CV")
    
    # Skills
    with st.expander("🛠️ Skills", expanded=False):
        st.markdown("**Skill Categories**")
        for idx, skill_cat in enumerate(cv.skills):
            col1, col2 = st.columns([1, 3])
            with col1:
                cv.skills[idx].category_name = st.text_input(
                    f"Category {idx+1}", 
                    skill_cat.category_name,
                    key=f"skill_cat_{idx}"
                )
            with col2:
                skills_str = ", ".join(skill_cat.skills)
                new_skills = st.text_input(
                    f"Skills (comma-separated)",
                    skills_str,
                    key=f"skills_{idx}"
                )
                cv.skills[idx].skills = [s.strip() for s in new_skills.split(",") if s.strip()]
    
    # Experience
    with st.expander("💼 Professional Experience", expanded=False):
        for idx, exp in enumerate(cv.experience):
            st.markdown(f"### Experience {idx+1}")
            col1, col2 = st.columns(2)
            with col1:
                exp.job_title = st.text_input("Job Title*", exp.job_title, key=f"exp_title_{idx}")
                exp.company_name = st.text_input("Company*", exp.company_name, key=f"exp_company_{idx}")
            with col2:
                exp.start_date = st.text_input("Start Date", exp.start_date, key=f"exp_start_{idx}")
                exp.end_date = st.text_input("End Date", exp.end_date, key=f"exp_end_{idx}")
            
            st.markdown("**Bullets:**")
            for b_idx, bullet in enumerate(exp.bullets):
                exp.bullets[b_idx].text = st.text_area(
                    f"Bullet {b_idx+1}",
                    bullet.text,
                    height=60,
                    key=f"exp_{idx}_bullet_{b_idx}"
                )
            st.divider()
    
    # Projects
    with st.expander("🚀 Projects", expanded=False):
        if cv.projects:
            for idx, proj in enumerate(cv.projects):
                st.markdown(f"### Project {idx+1}")
                proj.project_name = st.text_input("Project Name*", proj.project_name, key=f"proj_name_{idx}")
                proj.description = st.text_area("Description", proj.description or "", key=f"proj_desc_{idx}")
                
                tech_str = ", ".join(proj.technologies)
                new_tech = st.text_input("Technologies", tech_str, key=f"proj_tech_{idx}")
                proj.technologies = [t.strip() for t in new_tech.split(",") if t.strip()]
                
                for b_idx, bullet in enumerate(proj.bullets):
                    proj.bullets[b_idx].text = st.text_area(
                        f"Bullet {b_idx+1}",
                        bullet.text,
                        height=60,
                        key=f"proj_{idx}_bullet_{b_idx}"
                    )
                st.divider()
        else:
            st.info("No projects found in CV")
    
    # Education
    with st.expander("🎓 Education", expanded=False):
        for idx, edu in enumerate(cv.education):
            col1, col2 = st.columns(2)
            with col1:
                edu.degree = st.text_input("Degree*", edu.degree, key=f"edu_degree_{idx}")
                edu.institution = st.text_input("Institution*", edu.institution, key=f"edu_inst_{idx}")
            with col2:
                edu.graduation_date = st.text_input("Graduation Date", edu.graduation_date or "", key=f"edu_grad_{idx}")
                edu.gpa = st.text_input("GPA", edu.gpa or "", key=f"edu_gpa_{idx}")
    
    # Certifications
    with st.expander("📜 Certifications", expanded=False):
        if cv.certifications:
            for idx, cert in enumerate(cv.certifications):
                col1, col2 = st.columns(2)
                with col1:
                    cert.name = st.text_input("Certification*", cert.name, key=f"cert_name_{idx}")
                    cert.issuer = st.text_input("Issuer*", cert.issuer, key=f"cert_issuer_{idx}")
                with col2:
                    cert.date_obtained = st.text_input("Date", cert.date_obtained or "", key=f"cert_date_{idx}")
        else:
            st.info("No certifications found in CV")
    
    # Save button
    st.divider()
    if st.button("💾 Save Structured CV", type="primary", use_container_width=True):
        try:
            Storage.save_structured_cv(st.session_state.structured_cv)
            st.success("✅ Structured CV saved successfully!")
        except Exception as e:
            st.error(f"❌ Save failed: {e}")

st.divider()

# ===== ENHANCED JD DISPLAY =====
if st.session_state.enhanced_jd:
    st.header("🎯 Step 3: Review Enhanced JD Analysis")
    
    jd = st.session_state.enhanced_jd
    
    # Keyword Taxonomy
    with st.expander("📊 Keyword Taxonomy", expanded=True):
        tax = jd.keyword_taxonomy
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Technical Skills**")
            st.write(", ".join(tax.technical_skills) if tax.technical_skills else "None")
            
            st.markdown("**Soft Skills**")
            st.write(", ".join(tax.soft_skills) if tax.soft_skills else "None")
            
            st.markdown("**Domain Knowledge**")
            st.write(", ".join(tax.domain_knowledge) if tax.domain_knowledge else "None")
        
        with col2:
            st.markdown("**Tools & Technologies**")
            st.write(", ".join(tax.tools_technologies) if tax.tools_technologies else "None")
            
            st.markdown("**Certifications**")
            st.write(", ".join(tax.certifications) if tax.certifications else "None")
    
    # Requirements
    with st.expander("✅ Must-Have Requirements", expanded=True):
        if jd.must_have_requirements:
            for req in jd.must_have_requirements:
                st.markdown(f"- **{req.text}**")
                st.caption(f"Keywords: {', '.join(req.keywords)}")
        else:
            st.info("No explicit must-have requirements identified")
    
    with st.expander("➕ Nice-to-Have Requirements", expanded=False):
        if jd.nice_to_have_requirements:
            for req in jd.nice_to_have_requirements:
                st.markdown(f"- {req.text}")
                st.caption(f"Keywords: {', '.join(req.keywords)}")
        else:
            st.info("No nice-to-have requirements identified")

# Footer
st.divider()
st.caption("Phase 2 Complete ✓ | Next: Keyword Gap Analysis (Phase 3)")
