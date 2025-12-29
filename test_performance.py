"""
Test script to run CV and JD through the complete ATS CV Optimizer pipeline.
Tests scoring and rewriting performance with the updated 10-iteration, 80+ target logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.gemini_client import GeminiClient
from modules.cv_structurer import CVStructurer
from modules.jd_analyzer import JDAnalyzer
from modules.scoring_pipeline import ScoringPipeline
from modules.rewriting_engine import RewritingEngine
from modules.storage import Storage
import json

# Your CV content
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

# Job Description
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
    print("="*80)
    print("ATS CV OPTIMIZER - PERFORMANCE TEST")
    print("="*80)
    print()
    
    # Phase 1: Ingestion & Extraction
    print("📄 PHASE 1: Ingestion & JD Extraction")
    print("-" * 80)
    
    Storage.save_raw_cv(CV_TEXT)
    Storage.save_raw_jd(JD_TEXT)
    print("✅ Raw CV and JD saved")
    
    gemini = GeminiClient()
    jd_parsed = gemini.extract_jd_structure(JD_TEXT)
    Storage.save_parsed_jd(jd_parsed)
    print(f"✅ JD extracted - Job Title: {jd_parsed.get('job_title', 'N/A')}")
    print()
    
    # Phase 2: Structure & Verify
    print("🔧 PHASE 2: CV Structuring")
    print("-" * 80)
    
    structurer = CVStructurer(gemini.model)
    cv_structured = structurer.parse(CV_TEXT)
    Storage.save_structured_cv(cv_structured)
    print(f"✅ CV structured - {len(cv_structured.experience)} experience entries")
    print()
    
    # Phase 3: JD Enhancement
    print("🔍 PHASE 3: JD Enhancement")
    print("-" * 80)
    
    analyzer = JDAnalyzer(gemini.model)
    jd_enhanced = analyzer.enhance_jd(jd_parsed, JD_TEXT)
    Storage.save_enhanced_jd(jd_enhanced)
    print(f"✅ JD enhanced - {len(jd_enhanced.required_skills)} required skills")
    print()
    
    # Phase 5: Initial Scoring
    print("📊 PHASE 5: Initial Scoring")
    print("-" * 80)
    
    scorer = ScoringPipeline()
    initial_report = scorer.score_cv_jd_pair(
        cv_structured.model_dump(), 
        jd_enhanced.model_dump(),
        CV_TEXT,
        JD_TEXT
    )
    
    print(f"Initial ATS Score: {initial_report['ats_score']:.2f}")
    print(f"Initial JobFit Score: {initial_report['jobfit_score']:.2f}")
    print(f"  - Lexical Coverage: {initial_report['ats_components']['lexical_coverage']:.2f}")
    print(f"  - Skills Alignment: {initial_report['jobfit_components']['skills_alignment']:.2f}")
    print(f"  - Experience Alignment: {initial_report['jobfit_components']['experience_alignment']:.2f}")
    print()
    
    # Phase 6: Rewriting (10 iterations, 80+ target)
    print("✍️ PHASE 6: CV Rewriting (Max 10 iterations, Target: 80+)")
    print("-" * 80)
    
    engine = RewritingEngine(max_iterations=10, target_score=80.0)
    
    print("Starting rewriting iterations...")
    result = engine.optimize_cv(
        cv_structured,
        jd_enhanced,
        CV_TEXT,
        JD_TEXT,
        rewrite_projects=False,
        rewrite_certificates=False
    )
    
    print()
    print("="*80)
    print("REWRITING RESULTS")
    print("="*80)
    
    # Show iteration history
    print("\n📈 Iteration History:")
    print(f"{'Iter':<6} {'ATS Score':<12} {'JobFit Score':<14} {'Changes'}")
    print("-" * 80)
    
    for iteration in result['iterations']:
        iter_num = iteration['iteration']
        ats = iteration['ats_score']
        jobfit = iteration['jobfit_score']
        changes = iteration['changes'][:50]  # Truncate for display
        
        # Highlight if both scores exceed 80
        marker = "✅" if ats >= 80 and jobfit >= 80 else "  "
        print(f"{marker} {iter_num:<4} {ats:<12.2f} {jobfit:<14.2f} {changes}")
    
    print()
    print("="*80)
    print("FINAL SCORES")
    print("="*80)
    
    final_scores = result['final_scores']
    improvements = result['improvements']
    
    print(f"\n🎯 ATS Score: {final_scores['ats_score']:.2f} (+{improvements['ats_delta']:.2f})")
    print(f"💼 JobFit Score: {final_scores['jobfit_score']:.2f} (+{improvements['jobfit_delta']:.2f})")
    
    print(f"\n📊 ATS Components:")
    for comp, score in final_scores['ats_components'].items():
        print(f"  - {comp.replace('_', ' ').title()}: {score:.2f}")
    
    print(f"\n💼 JobFit Components:")
    for comp, score in final_scores['jobfit_components'].items():
        print(f"  - {comp.replace('_', ' ').title()}: {score:.2f}")
    
   # Success criteria
    print("\n" + "="*80)
    print("SUCCESS CRITERIA CHECK")
    print("="*80)
    
    ats_pass = final_scores['ats_score'] >= 80
    jobfit_pass = final_scores['jobfit_score'] >= 80
    
    print(f"ATS Score >= 80: {'✅ PASS' if ats_pass else '❌ FAIL'} ({final_scores['ats_score']:.2f})")
    print(f"JobFit Score >= 80: {'✅ PASS' if jobfit_pass else '❌ FAIL'} ({final_scores['jobfit_score']:.2f})")
    
    if ats_pass and jobfit_pass:
        print("\n🎉 SUCCESS! Both scores exceeded 80.")
    else:
        print("\n⚠️ Target not met. Scores below 80.")
    
    # Save final optimized CV
    Storage.save_optimized_cv(result['final_cv'])
    print(f"\n✅ Optimized CV saved to data/processed/cv_optimized.json")
    
    return result

if __name__ == "__main__":
    result = main()
