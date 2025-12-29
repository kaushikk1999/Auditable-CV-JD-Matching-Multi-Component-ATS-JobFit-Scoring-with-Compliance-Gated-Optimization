
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.rewriting_engine import RewritingEngine
from modules.cv_structurer import CVStructurer
from modules.jd_analyzer import JDAnalyzer
from modules.storage import Storage
import json

# 1. Define Inputs
# 1. Define Inputs
CV_TEXT = """
KAUSHIK KARMAKAR
Email: john.doe@example.com | Phone: +1-555-0100
LinkedIn: linkedin.com/in/kaushik99 | GitHub: github.com/kaushikk1999
SUMMARY
Coding Educator focused holistic technology development children, creating next generation technology leaders. Instructed
500+ international students Python programming coding logic, achieving 4.9/5 satisfaction rating. Designed unique,
immersive holistic curriculum, sparking curiosity thirst learning young minds. Mentored students uncovering genius every
kid using interactive online teaching methods.
TECHNICAL SKILLS
Teaching & Pedagogy: Online Teaching, Mentoring, Curriculum Development, Student Engagement, Classroom
Management
Programming: Python (Core Concepts), Coding Logic, Software Subject Matter Expertise, Scratch, Java
EdTech Tools: Video Conferencing (Zoom/Meet), Gamified Learning Platforms, LMS, High-speed Internet Setup
Soft Skills: Excellent English, Confident & Presentable, Good Oratory Skills, Patience, Communication
PROFESSIONAL EXPERIENCE
1. Clevered | Machine Learning Coach internship | Sep 2024 – Present
● Conducted 100+ interactive online sessions, teaching Python concepts diverse student groups globally.
● Adapted instructional methods suit learning styles, ensuring 100% concept clarity via visual aids.
● Provided constructive feedback mentorship, helping learners succeed real-world projects building confidence.
2. Popat Technology | Data Science internship | Mar 2024 – Jul 2024
● Conceptualized 20+ lesson plans exercises, aligning educational standards holistic technology development.
● Simplified complex programming topics, increasing module completion rates 30% engaging content.
3. InternCareer | Data Analyst internship | Nov 2023
● Tracked 50+ student performance metrics, identifying improvement areas personalized guidance.
● Communicated progress updates parents, maintaining professional relationships transparent reporting.
4. Suvidha Foundation | Machine Learning Engineer internship | Oct 2023•
● Led 4 workshops introduction coding, engaging 60+ participants interactive demonstrations.
● Demonstrated best practices software development, instilling strong foundational habits young coders.
5. Mentored Minds | Data Analytics internship | Jul 2023 – Aug 2023
● Tutored 15 students coding fundamentals, improving logical thinking skills 20% through gamified practice.
● Customized learning paths individual students, ensuring personalized attention academic growth.
PROJECTS
Gamified Coding Curriculum & Learning App | Apr 2025 – Jul 2025
● Developed 1 interactive learning platform Python, revolutionize the education system modern tech.
● Created 10 mini-projects simulating real-world scenarios, boosting practical application 40% students.
● Integrated gamification elements, enhancing user retention 25% during beta testing phase.
● Authored comprehensive documentation guides, facilitating independent study capability learners.
EDUCATION
MTech, Data Science | Christ University, Bangalore | 2024 - 2026
Relevant Coursework: Machine Learning, Data Science, Python Programming, Statistical Modeling, Data Mining, Big Data
Analytics, NLP
CERTIFICATIONS
• Advanced Machine Learning Specialization (Coursera) – TensorFlow, Keras, Deployment Strategies
• Feature Engineering Techniques (Kaggle) – Transformation, Selection, Dimensionality Reduction
• Data Visualization Mastery (Kaggle) – Matplotlib, Seaborn, Interactive Dashboards
• Python for Data Science (Coursera) – pandas, NumPy, SciPy Libraries
"""

JD_TEXT = """
Technical Business Analyst
Altisource
Bengaluru, Karnataka
Job Description
Core Skills
Strong process mapping, requirement gathering, and documentation skills
Ability to translate business workflows into checklist logic, prompts, and system flows
Experience working with structured and unstructured data, especially documents and PDFs
Clear communicator who can partner with SMEs to design AI use cases
Skilled in evaluating business value, ROI, and operational impact
Ability to test AI outputs, validate logic paths, and support prompt tuning
Qualifications
Experience 2–5 years in BA or product role, ideally supporting tech or automation teams
Experience with automation or BPM projects; exposure to AI/LLM projects a plus
Worked with SMEs in operational environments (e.g., servicing, valuations, QC)
Defined requirements, test cases, and acceptance criteria for iterative software delivery
Familiarity with project tools (Jira, Confluence, Figma, or equivalents)
"""

print("🚀 Starting End-to-End Rewriting Test...")

# 2. Structure CV and JD (Phase 1 & 2)
print("Parsing CV and JD...")
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Monkeypatch model to Flash to avoid Pro safety triggers
import config.settings
config.settings.GEMINI_MODEL = "gemini-3-pro-preview"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

cv_structurer = CVStructurer(model)
jd_analyzer = JDAnalyzer(model)

# Simulate Phase 1 JD Extraction (Basic)
# Since we don't have the Phase 1 extractor imported, we'll do a quick extraction here or mock it
# Let's try to find the Phase 1 extractor. It's likely in `modules/parsers.py` or `app.py` logic.
# For this test, let's just create a basic JD dict manually or use a simple prompt.
basic_jd = {
    "job_title": "Technical Business Analyst",
    "company_name": "Altisource",
    "location": "Bengaluru, Karnataka",
    "work_type": "Full-time",
    "experience_required": "2-5 years",
    "company_overview": "Altisource is an integrated service provider...",
    "role_summary": "Technical Business Analyst supporting tech or automation teams.",
    "key_responsibilities": [
        "Process mapping, requirement gathering, and documentation",
        "Translate business workflows into checklist logic",
        "Partner with SMEs to design AI use cases",
        "Test AI outputs and validate logic paths"
    ],
    "required_skills": [
        "Process Mapping", "Requirement Gathering", "Documentation", 
        "Jira", "Figma", "Confluence", "AI/LLM", "BPM", 
        "Structured Data", "Unstructured Data", "PDFs"
    ],
    "preferred_skills": ["Automation", "Prompt Tuning"],
    "education": "Bachelor's degree",
    "soft_skills": ["Clear communicator", "Partner with SMEs"],
    "diversity_statement": "Equal opportunity employer",
    "recruiter_contact": "Not specified",
    "ats_keywords": [
        "Process Mapping", "Requirement Gathering", "Documentation", 
        "Jira", "Figma", "Confluence", "AI", "LLM", "BPM", 
        "Structured Data", "Unstructured Data", "PDFs", "Prompt Tuning",
        "Business Value", "ROI", "Operational Impact", "Test Cases", "Acceptance Criteria"
    ]
}

cv_structured = cv_structurer.parse(CV_TEXT)
jd_enhanced = jd_analyzer.enhance_jd(basic_jd, JD_TEXT)

# 3. Initialize Rewriting Engine (Phase 6)
print("Initializing Rewriting Engine (Aggressive Mode)...")
engine = RewritingEngine(
    max_iterations=5,      # Run up to 5 loops
    target_score=90.0,     # Target 90+
    temperature=0.3        # Low temp for precision
)

# 4. Run Optimization
print("Running Optimization Loop...")
result = engine.optimize_cv(
    cv_structured, jd_enhanced,
    CV_TEXT, JD_TEXT,
    rewrite_projects=True,
    rewrite_certificates=True
)

# 5. Output Results
final_scores = result["final_scores"]
ats_score = final_scores["ats_score"]
jobfit_score = final_scores["jobfit_score"]

print("\n" + "="*50)
print(f"FINAL RESULTS")
print("="*50)
print(f"ATS Score:    {ats_score:.1f} / 100")
print(f"JobFit Score: {jobfit_score:.1f} / 100")
print("-" * 30)

if ats_score >= 90 and jobfit_score >= 90:
    print("✅ SUCCESS: Both scores are 90+!")
else:
    print("❌ FAILURE: Scores did not reach 90+.")

print("\nValidation Report Summary:")
validation = result.get("validation_report", {})
violations = validation.get("violations", [])
if violations:
    print(f"⚠️ Found {len(violations)} violations (Aggressive Mode allowed them):")
    for v in violations[:5]:
        print(f"  - {v}")
else:
    print("✅ No violations found.")
