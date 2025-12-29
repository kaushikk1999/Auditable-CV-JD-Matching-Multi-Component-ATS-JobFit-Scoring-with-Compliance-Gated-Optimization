"""
Perform Ablation Study on ATS & JobFit Scoring Components.

This script:
1. Parses the default Tutor CV and JD (same as analyze_tutor_cv.py).
2. Runs the base scoring with full weights.
3. Iteratively sets each component's weight to 0.0 and re-runs scoring.
4. Outputs the results as JSON for visualization.
"""
import sys
import json
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.gemini_client import GeminiClient
from modules.cv_structurer import CVStructurer
from modules.jd_analyzer import JDAnalyzer
from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage

# User's CV (Coding Educator)
CV_TEXT = """
KAUSHIK KARMAKAR

Email: john.doe@example.com | Phone: +1-555-0100
LinkedIn: linkedin.com/in/kaushik99 | GitHub: github.com/kaushikk1999

SUMMARY

Coding Educator focused holistic technology development children, creating next generation technology leaders. Instructed
500+ personalized students Python programming coding logic, achieving 4.9/5 satisfaction rating. Designed unique,
interactive learning experiences via gamification, teaching young minds turning young minds into coding game every
kid using interactive online teaching methods.

TECHNICAL SKILLS

Teaching & Pedagogy: Online Teaching, Mentoring, Curriculum Development, Student Engagement, Classroom
Management

Programming: Python (Core Concepts), Coding Logic, Software Subject Matter Expertise, Scratch, Java

EdTech Tools: Video Conferencing (Zoom/Meet), Gamified Learning Platforms, LMS, High-speed Internet Setup

Soft Skills: Excellent English, Confident & Presentable, Good Oratory Skills, Patience, Communication

PROFESSIONAL EXPERIENCE

1. Clevered | Machine Learning Coach internship | Sep 2024 – Present
• Conducted 100+ interactive online sessions, teaching Python concepts diverse student groups globally.
• Adapted instructional methods, gamification styles, ensuring 100% concept clarity via visual aids.
• Provided constructive feedback mentorship, helping learners succeed real-world projects building confidence.

2. Papar Technology | Data Science internship | Mar 2024 – Jul 2024
• Conceptualized 20+ lesson plans exercises, aligning educational standards holistic technology development.
• Simplified complex programming topics, increasing module completion rates 30% engaging content.

3. InternCareer | Data Analyst internship | Nov 2023
• Tracked 50+ student performance metrics, identifying improvement areas personalized guidance.
• Communicated progress updates parents, maintaining professional relationships transparent reporting.

4. Sanvidha Foundation | Machine Learning Engineer internship | Oct 2023
• Led 4 workshops introduction coding, engaging 60+ participants interactive demonstrations.
• Demonstrated best practices software development, instilling strong foundational habits young coders.

5. Mentored Minds | Data Analytics internship | Jul 2023 – Aug 2023
"""

# Tutor JD
JD_TEXT = """
Online Tutor
Class dunia - Remote

We are seeking a qualified and enthusiastic female tutor to teach mathematics, English, and science to Australian students in grades 1 to 10. The ideal candidate should be a graduate with a strong command of English and a passion for educating young learners.

REQUIREMENTS:
- Skills: Math (required), Tutoring, Teaching experience, Lesson planning, Experience working with students
- Education: Bachelor's degree (required)
- Languages: English (required)
- Experience: Teaching: 1 year (Preferred), total work: 1 year (Preferred)

JOB DETAILS:
- Job Types: Full-time, Part-time, Permanent, Fresher, Freelance
- Contract length: 6 months
- Pay: ₹2,000.00 - ₹4,000.00 per month
- Work Location: Remote

KEY RESPONSIBILITIES:
- Teach mathematics, English, and science to students grades 1-10
- Create engaging lesson plans
- Provide personalized tutoring and guidance
- Assess student progress and provide feedback
- Work with Australian students (online teaching)
"""

def main():
    print("Initializing Gemini and Parsing Documents (this may take a moment)...", file=sys.stderr)
    
    gemini = GeminiClient()
    
    # Parse JD
    jd_parsed = gemini.extract_jd_structure(JD_TEXT)
    analyzer = JDAnalyzer(gemini.model)
    jd_enhanced = analyzer.enhance_jd(jd_parsed, JD_TEXT)
    
    # Parse CV
    structurer = CVStructurer(gemini.model)
    cv_structured = structurer.parse(CV_TEXT)
    
    scorer = ScoringPipeline()
    
    # 1. Base Score (All weights active)
    base_report = scorer.score_cv_jd_pair(
        cv_structured.model_dump(),
        jd_enhanced.model_dump(),
        CV_TEXT,
        JD_TEXT
    )
    
    base_ats = base_report['ats_score']
    base_jobfit = base_report['jobfit_score']
    
    results = {
        "baseline": {
            "ats_score": base_ats,
            "jobfit_score": base_jobfit
        },
        "ablations": []
    }
    
    # Helper to get default weights (deep copy to avoid mutation issues)
    default_config = copy.deepcopy(scorer.feature_extractor.config)
    
    # 2. ATS Ablations
    ats_components = [
        "lexical_coverage", "fuzzy_coverage", "tfidf_relevance", 
        "tfidf_cosine_similarity", "section_distribution"
    ]
    
    for comp in ats_components:
        # Reset to defaults
        scorer.feature_extractor.config.ats_weights = copy.deepcopy(default_config.ats_weights)
        
        # Set specific weight to 0
        setattr(scorer.feature_extractor.config.ats_weights, comp, 0.0)
        
        # Re-score
        report = scorer.score_cv_jd_pair(
            cv_structured.model_dump(),
            jd_enhanced.model_dump(),
            CV_TEXT,
            JD_TEXT
        )
        
        # NOTE: When we set a weight to 0, the total POSSIBLE score decreases if we don't re-normalize.
        # However, "Ablation" usually means "Performance without X".
        # If the system expects weights to sum to 1.0, setting one to 0 makes the max score < 100.
        # We want to see the *drop* in the final score. 
        # So recording the raw score is correct for "How much does this component contribute?"
        
        results["ablations"].append({
            "type": "ATM",
            "removed_component": comp,
            "score": report["ats_score"],
            "delta": base_ats - report["ats_score"]
        })

    # 3. JobFit Ablations
    jobfit_components = [
        "summary_similarity", "experience_alignment", "skills_alignment",
        "education_match", "domain_relevance"
    ]
    
    for comp in jobfit_components:
        # Reset to defaults
        scorer.feature_extractor.config.jobfit_weights = copy.deepcopy(default_config.jobfit_weights)
        
        # Set specific weight to 0
        setattr(scorer.feature_extractor.config.jobfit_weights, comp, 0.0)
        
        # Re-score
        report = scorer.score_cv_jd_pair(
            cv_structured.model_dump(),
            jd_enhanced.model_dump(),
            CV_TEXT,
            JD_TEXT
        )
        
        results["ablations"].append({
            "type": "JobFit",
            "removed_component": comp,
            "score": report["jobfit_score"],
            "delta": base_jobfit - report["jobfit_score"]
        })

    # Output JSON to stdout
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
