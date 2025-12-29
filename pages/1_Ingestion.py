import streamlit as st
from pathlib import Path
from modules.parsers import CVParser, JDParser
from modules.gemini_client import GeminiClient
from modules.storage import Storage

st.set_page_config(
    page_title="Phase 1: Ingestion",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding-top: 2rem;
    }
    
    /* Typography */
    h1 {
        color: #1e3a8a;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #2563eb;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        margin-top: 2rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #4b5563;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    /* Cards */
    .stCard {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    /* Text Areas */
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        font-family: 'Courier New', monospace;
    }
    
    /* Success/Info Messages */
    .stSuccess {
        background-color: #dcfce7;
        color: #166534;
        border-radius: 8px;
    }
    .stInfo {
        background-color: #eff6ff;
        color: #1e40af;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Title Section
with st.container():
    st.title("Phase 1: Ingestion")
    st.markdown("""
    <div style='background-color: #eff6ff; padding: 1rem; border-radius: 8px; border-left: 5px solid #2563eb; margin-bottom: 2rem;'>
        <p style='margin:0; color: #1e40af; font-size: 1.1rem;'>
            <strong>Ingestion & Extraction</strong><br>
            Upload your CV and Job Description to extract structured data using Gemini AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Check for config/docs status
col_status, _ = st.columns([1, 2])
with col_status:
    with st.expander("System Status", expanded=False):
        config_files = ["config/scoring_config.yaml", "config/word_lists.py", "config/prompts.py"]
        docs_files = ["docs/scoring_equations.md"]
        
        all_configs = all(Path(f).exists() for f in config_files)
        all_docs = all(Path(f).exists() for f in docs_files)
        
        if all_configs:
            st.success("✅ Config files present")
        else:
            st.error("❌ Missing config files")
            
        if all_docs:
            st.success("✅ Documentation present")
        else:
            st.error("❌ Missing documentation")

# Initialize session state
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "jd_structure" not in st.session_state:
    st.session_state.jd_structure = {}

# === Main Content Layout ===
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("## 📤 Step 1: Your CV")
    
    tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Upload CV (.txt, .docx, .pdf)",
            type=["txt", "docx", "pdf"],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file:
            file_extension = Path(uploaded_file.name).suffix
            try:
                cv_bytes = uploaded_file.read()
                st.session_state.cv_text = CVParser.parse(cv_bytes, file_extension)
                st.success(f"✅ Successfully parsed **{uploaded_file.name}**")
            except Exception as e:
                st.error(f"❌ Parse error: {e}")

    with tab2:
        manual_cv = st.text_area(
            "Paste CV Content",
            height=300,
            placeholder="Copy and paste your full CV text here...",
            key="manual_cv_input"
        )
        if manual_cv.strip():
            st.session_state.cv_text = manual_cv.strip()
            st.success("✅ CV text captured")

    # Show parsed CV preview
    if st.session_state.cv_text:
        with st.expander("👀 Preview Extracted CV Text"):
            st.text_area("Raw Text", st.session_state.cv_text, height=200, disabled=True)

with col_right:
    st.markdown("## 📋 Step 2: Job Description")
    
    jd_input = st.text_area(
        "Paste the full Job Description",
        height=400,
        placeholder="Paste the complete job posting here (responsibilities, requirements, etc.)...",
        help="The more detail you provide, the better the extraction."
    )
    
    if jd_input.strip():
        st.session_state.jd_text = JDParser.clean_text(jd_input)
        st.success(f"✅ JD captured ({len(st.session_state.jd_text)} chars)")

# === Action Section ===
st.markdown("---")
col_action_1, col_action_2, col_action_3 = st.columns([1, 2, 1])

with col_action_2:
    parse_btn = st.button(
        "🚀 Parse & Extract Data", 
        type="primary", 
        use_container_width=True,
        disabled=not (st.session_state.cv_text and st.session_state.jd_text)
    )

if parse_btn:
    with st.status("🤖 Processing...", expanded=True) as status:
        st.write("💾 Saving raw inputs...")
        Storage.save_raw_cv(st.session_state.cv_text)
        Storage.save_raw_jd(st.session_state.jd_text)
        
        st.write("🧠 Analyzing with Gemini AI...")
        try:
            client = GeminiClient()
            st.session_state.jd_structure = client.extract_jd_structure(st.session_state.jd_text)
            Storage.save_parsed_jd(st.session_state.jd_structure)
            status.update(label="✅ Extraction Complete!", state="complete", expanded=False)
            st.rerun()
        except Exception as e:
            status.update(label="❌ Extraction Failed", state="error")
            st.error(f"Error details: {e}")

# === Results Section ===
if st.session_state.jd_structure:
    st.markdown("## 📊 Step 3: Structured Analysis")
    data = st.session_state.jd_structure
    
    # Top Level Info Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Job Title", data.get('job_title', 'N/A'))
    with col2:
        st.metric("Company", data.get('company_name', 'N/A'))
    with col3:
        st.metric("Location", data.get('location', 'N/A'))
    with col4:
        st.metric("Experience", data.get('experience_required', 'N/A'))

    st.markdown("### 🏢 Company & Role")
    with st.container():
        st.markdown(f"""
        <div class="stCard">
            <p><strong>Overview:</strong> {data.get('company_overview', 'Not specified')}</p>
            <p><strong>Role Summary:</strong> {data.get('role_summary', 'Not specified')}</p>
            <p><strong>Work Type:</strong> {data.get('work_type', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    col_resp, col_skills = st.columns([1, 1])
    
    with col_resp:
        st.markdown("### 🔑 Key Responsibilities")
        responsibilities = data.get('key_responsibilities', [])
        if responsibilities:
            for resp in responsibilities:
                st.info(f"• {resp}")
        else:
            st.write("Not specified")

    with col_skills:
        st.markdown("### 🛠 Skills Required")
        required = data.get('required_skills', [])
        if required:
            st.markdown("**Hard Skills:**")
            st.markdown(" ".join([f"`{skill}`" for skill in required]))
        
        st.markdown("**Preferred / Bonus:**")
        preferred = data.get('preferred_skills', [])
        if preferred:
             st.markdown(" ".join([f"`{skill}`" for skill in preferred]))
        else:
            st.write("None specified")

    st.markdown("### 🧠 Soft Skills & Culture")
    col_soft, col_div = st.columns(2)
    with col_soft:
        soft = data.get('soft_skills', [])
        if soft:
            st.success(" • ".join(soft))
        else:
            st.write("Not specified")
            
    with col_div:
        st.markdown(f"**Diversity Statement:** {data.get('diversity_statement', 'Not specified')}")

    st.markdown("### 🎯 ATS Keywords")
    keywords = data.get('ats_keywords', [])
    if keywords:
        st.markdown("""
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 10px; border: 1px solid #bae6fd;">
            """ + " • ".join([f"<b>{k}</b>" for k in keywords]) + """
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎓 Education & Contact")
    col_edu, col_contact = st.columns(2)
    with col_edu:
        st.markdown(f"**Education:** {data.get('education', 'Not specified')}")
    with col_contact:
        st.markdown(f"**Recruiter:** {data.get('recruiter_contact', 'Not specified')}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.8rem;'>"
    "ATS CV Optimizer • Phase 1 • Powered by Gemini AI"
    "</div>", 
    unsafe_allow_html=True
)

st.divider()
st.markdown("### 🔄 Next Steps")
if st.session_state.get("jd_structure"):
    st.info("✅ Phase 1 complete! Proceed to **Phase 2: Structure & Verify** using the sidebar.")
