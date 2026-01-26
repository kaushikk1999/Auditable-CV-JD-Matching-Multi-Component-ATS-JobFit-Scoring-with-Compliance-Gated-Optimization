"""
Test Data Analytics Lecturer JD with current CV - Should score much higher!
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.keyword_engine import extract_target_keywords, select_top_keywords
from modules.evidence_mapper import build_evidence_map, get_allowed_keywords, get_needs_confirmation
from modules.scoring_pipeline import ScoringPipeline
from modules.gemini_client import GeminiClient

# Data Analytics Lecturer JD
jd_text = """
Job Title: Full-Time Data Analytics Lecturer

Key Responsibilities:
- Conduct lectures and training sessions on core and advanced data analytics topics
- Deliver content effectively in both English and Tamil
- Facilitate hands-on learning through real-time case studies, projects, and tools
- Monitor student progress, provide feedback, and support skill development

Requirements:
- Proven expertise in data analytics with proficiency in relevant tools and techniques
- Fluency in English and Tamil for effective communication
- Passion for teaching and mentoring learners
- Ability to work full-time and adapt to both online and offline training environments

Skills: Data analytics, Teaching, English, Tamil, Multilingual
"""

# Your CV
cv_text = """
KAUSHIK KARMAKAR

SUMMARY
Coding Educator focused holistic technology development children, creating next generation technology leaders. Instructed
500+ international students Python programming coding logic, achieving 4.9/5 satisfaction rating. Designed unique,
immersive holistic curriculum, sparking curiosity thirst learning young minds. Mentored students uncovering genius every
kid using interactive online teaching methods.

TECHNICAL SKILLS
Teaching & Pedagogy: Online Teaching, Mentoring, Curriculum Development, Student Engagement, Classroom Management
Programming: Python (Core Concepts), Coding Logic, Software Subject Matter Expertise, Scratch, Java
EdTech Tools: Video Conferencing (Zoom/Meet), Gamified Learning Platforms, LMS, High-speed Internet Setup
Soft Skills: Excellent English, Confident & Presentable, Good Oratory Skills, Patience, Communication

PROFESSIONAL EXPERIENCE
1. Clevered | Machine Learning Coach internship | Sep 2024 – Present
● Conducted 100+ interactive online sessions, teaching Python concepts diverse student groups globally.

2. Popat Technology | Data Science internship | Mar 2024 – Jul 2024
● Conceptualized 20+ lesson plans exercises, aligning educational standards holistic technology development.

EDUCATION
MTech, Data Science | Christ University, Bangalore | 2024 - 2026
Relevant Coursework: Machine Learning, Data Science, Python Programming, Statistical Modeling, Data Mining, Big Data Analytics, NLP

CERTIFICATIONS
• Advanced Machine Learning Specialization (Coursera)
• Feature Engineering Techniques (Kaggle)
• Data Visualization Mastery (Kaggle)
• Python for Data Science (Coursera)
"""

print("="*100)
print("DATA ANALYTICS LECTURER JD - MATCH ANALYSIS")
print("="*100)

# Extract keywords
print("\n1️⃣ EXTRACTING JD KEYWORDS...")
target_keywords = extract_target_keywords(jd_text)
top_keywords = select_top_keywords(target_keywords, n=20)

print(f"\nTop Keywords ({len(top_keywords)}):")
for kw in top_keywords[:10]:
    score = target_keywords.importance_scores.get(kw, 0)
    print(f"  - {kw} (importance: {score})")

# Build evidence map
print("\n2️⃣ CHECKING CV EVIDENCE...")
evidence_map = build_evidence_map(cv_text, top_keywords)

allowed = get_allowed_keywords(evidence_map, min_confidence=0.6)
needs_conf = get_needs_confirmation(evidence_map, target_keywords)

print(f"\n✅ Keywords WITH Evidence ({len(allowed)}):")
for kw in allowed:
    ev = evidence_map[kw]
    print(f"  - {kw} ({ev.evidence_type}, confidence={ev.confidence:.2f})")

print(f"\n⚠️ Keywords NEED Confirmation ({len(needs_conf)}):")
for kw in needs_conf[:5]:
    print(f"  - {kw}")

# Score
print("\n3️⃣ SCORING (Current System)...")
gemini = GeminiClient()

# Parse JD
jd_parsed = gemini.extract_jd_structure(jd_text)
print(f"\nParsed JD:")
print(f"  Title: {jd_parsed.get('job_title', 'N/A')}")
print(f"  Required Skills: {jd_parsed.get('required_skills', [])[:5]}")

# For scoring, we need structured CV - use a simplified version
cv_structured = {
    "summary": "Coding Educator with 500+ students taught",
    "skills": {
        "Teaching": ["Online Teaching", "Mentoring", "Curriculum Development"],
        "Programming": ["Python", "Data Science"],
        "Tools": ["Video Conferencing", "LMS"]
    },
    "experience": [
        {"company": "Clevered", "role": "Machine Learning Coach", "bullets": ["Taught Python to 100+ students"]},
        {"company": "Popat Technology", "role": "Data Science internship", "bullets": ["Created lesson plans"]}
    ],
    "education": [{"degree": "MTech Data Science", "institution": "Christ University"}]
}

scorer = ScoringPipeline()
scores = scorer.score_cv_jd_pair(cv_structured, jd_parsed, cv_text, jd_text)

print(f"\n📊 INITIAL SCORES:")
print(f"  ATS: {scores['ats_score']:.1f}")
print(f"  JobFit: {scores['jobfit_score']:.1f}")
print(f"  Combined: {(scores['ats_score'] + scores['jobfit_score'])/2:.1f}")

print("\n4️⃣ VERDICT:")
combined = (scores['ats_score'] + scores['jobfit_score'])/2
if combined >= 80:
    print("  ✅ EXCELLENT MATCH - Should easily reach 90+ with optimization")
elif combined >= 65:
    print("  ✅ GOOD MATCH - Can reach 80-90 with optimization")
elif combined >= 50:
    print("  ⚠️ MODERATE MATCH - Can reach 70-80 with optimization")
else:
    print("  ❌ POOR MATCH - Likely caps at 60-70")

print(f"\n  Evidence coverage: {len(allowed)}/{len(top_keywords)} keywords ({len(allowed)/len(top_keywords)*100:.0f}%)")
print(f"  This is a MUCH better match than math tutoring!")

print("\n" + "="*100)
