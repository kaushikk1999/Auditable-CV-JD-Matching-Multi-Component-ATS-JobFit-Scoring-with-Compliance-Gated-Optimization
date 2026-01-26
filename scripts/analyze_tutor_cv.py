"""
Comprehensive performance analysis for user's CV and Tutor JD.
Tests with fixed TF-IDF Cosine and education matching to show improvements.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.gemini_client import GeminiClient
from modules.cv_structurer import CVStructurer
from modules.jd_analyzer import JDAnalyzer
from modules.scoring_pipeline import ScoringPipeline
from modules.storage import Storage
import json

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
    print("="*100)
    print("COMPREHENSIVE PERFORMANCE ANALYSIS - TUTOR CV/JD")
    print("="*100)
    print()
    
    Storage.save_raw_cv(CV_TEXT)
    Storage.save_raw_jd(JD_TEXT)
    
    gemini = GeminiClient()
    
    # Phase 1: JD Extraction
    print("📄 PHASE 1: JD Extraction")
    print("-" * 100)
    jd_parsed = gemini.extract_jd_structure(JD_TEXT)
    print(f"✅ Job Title: {jd_parsed.get('job_title', 'N/A')}")
    print(f"✅ Required Skills: {jd_parsed.get('required_skills', [])[:5]}...")
    print()
    
    # Phase 2: CV Structuring
    print("🔧 PHASE 2: CV Structuring")
    print("-" * 100)
    structurer = CVStructurer(gemini.model)
    cv_structured = structurer.parse(CV_TEXT)
    print(f"✅ Experiences: {len(cv_structured.experience)}")
    print(f"✅ Skills Categories: {len(cv_structured.skills)}")
    print(f"✅ Education Entries: {len(cv_structured.education)}")
    print()
    
    # Phase 3: JD Enhancement
    print("🔍 PHASE 3: JD Enhancement")
    print("-" * 100)
    analyzer = JDAnalyzer(gemini.model)
    jd_enhanced = analyzer.enhance_jd(jd_parsed, JD_TEXT)
    print(f"✅ Required Skills: {len(jd_enhanced.required_skills)}")
    print(f"✅ Preferred Skills: {len(jd_enhanced.preferred_skills)}")
    print(f"✅ ATS Keywords: {len(jd_enhanced.ats_keywords)}")
    print()
    
    # Phase 5: Scoring (WITH FIXED TF-IDF Cosine!)
    print("📊 PHASE 5: INITIAL SCORING (With Fixed TF-IDF Cosine)")
    print("=" * 100)
    scorer = ScoringPipeline()
    initial_report = scorer.score_cv_jd_pair(
        cv_structured.model_dump(),
        jd_enhanced.model_dump(),
        CV_TEXT,
        JD_TEXT
    )
    
    print(f"\n🎯 INITIAL SCORES:")
    print(f"   ATS Score: {initial_report['ats_score']:.2f}")
    print(f"   JobFit Score: {initial_report['jobfit_score']:.2f}")
    print(f"   Combined: {(initial_report['ats_score'] + initial_report['jobfit_score']) / 2:.2f}")
    
    print(f"\n📊 ATS COMPONENTS (Out of 100):")
    for comp, score in initial_report['ats_components'].items():
        status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        print(f"   {status} {comp.replace('_', ' ').title():<25} {score:>6.2f}")
    
    print(f"\n💼 JOBFIT COMPONENTS (Out of 100):")
    for comp, score in initial_report['jobfit_components'].items():
        status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        print(f"   {status} {comp.replace('_', ' ').title():<25} {score:>6.2f}")
    
    print(f"\n🔍 ATS FEATURES:")
    features = initial_report.get('ats_features', {})
    print(f"   JD Keywords Count: {features.get('jd_keywords_count', 0)}")
    print(f"   CV Keywords Count: {features.get('cv_keywords_count', 0)}")
    print(f"   Exact Matches: {features.get('exact_matches', 0)}")
    
    if 'matched_jd_keyword_distribution' in features:
        print(f"\n   Matched JD Keywords by Section:")
        for section, count in features['matched_jd_keyword_distribution'].items():
            print(f"     - {section.capitalize()}: {count}")
    
    # Analysis
    print("\n" + "="*100)
    print("DETAILED ANALYSIS")
    print("="*100)
    
    print("\n🔴 MAJOR ISSUES:")
    issues = []
    
    ats_score = initial_report['ats_score']
    jobfit_score = initial_report['jobfit_score']
    ats_comps = initial_report['ats_components']
    jobfit_comps = initial_report['jobfit_components']
    
    if ats_comps['tfidf_cosine_similarity'] < 30:
        issues.append(f"   ❌ TF-IDF Cosine Similarity very low ({ats_comps['tfidf_cosine_similarity']:.1f}) - Weak semantic overlap")
    if ats_comps['lexical_coverage'] < 50:
        issues.append(f"   ❌ Lexical Coverage low ({ats_comps['lexical_coverage']:.1f}) - Missing key JD keywords")
    if jobfit_comps['skills_alignment'] < 50:
        issues.append(f"   ❌ Skills Alignment poor ({jobfit_comps['skills_alignment']:.1f}) - CV skills don't match JD requirements")
    if jobfit_comps['education_match'] < 50:
        issues.append(f"   ❌ Education Match low ({jobfit_comps['education_match']:.1f}) - Education mismatch")
    
    for issue in issues:
        print(issue)
    
    print("\n🟡 MODERATE CONCERNS:")
    if 50 <= jobfit_comps['experience_alignment'] < 70:
        print(f"   ⚠️ Experience Alignment moderate ({jobfit_comps['experience_alignment']:.1f}) - Some alignment but not strong")
    if 50 <= jobfit_comps['summary_similarity'] < 70:
        print(f"   ⚠️ Summary Similarity moderate ({jobfit_comps['summary_similarity']:.1f}) - Summary could be more targeted")
    
    print("\n🟢 STRENGTHS:")
    if ats_comps['section_distribution'] >= 70:
        print(f"   ✅ Section Distribution ({ats_comps['section_distribution']:.1f}) - Good keyword spread across sections")
    if jobfit_comps['experience_alignment'] >= 70:
        print(f"   ✅ Experience Alignment ({jobfit_comps['experience_alignment']:.1f}) - Experience bullets align well")
    if jobfit_comps['domain_relevance'] >= 70:
        print(f"   ✅ Domain Relevance ({jobfit_comps['domain_relevance']:.1f}) - Domain knowledge matches")
    
    # Gap Analysis
    print("\n" + "="*100)
    print("GAP ANALYSIS")
    print("="*100)
    
    print("\n📉 KEYWORD GAPS:")
    jd_kws = set(initial_report.get('ats_features', {}).get('jd_keywords_count', 0))
    exact_matches = initial_report.get('ats_features', {}).get('exact_matches', 0)
    
    print(f"   Total JD Keywords: {features.get('jd_keywords_count', 0)}")
    print(f"   Matched in CV: {exact_matches}")
    print(f"   Missing: {features.get('jd_keywords_count', 0) - exact_matches}")
    
    print("\n🎯 SPECIFIC RECOMMENDATIONS:")
    print("\n   To improve ATS Score:")
    print("   1. Add JD keywords: 'mathematics', 'science', 'tutoring', 'lesson planning'")
    print("   2. Mention 'grades 1-10' or 'primary/secondary education'")
    print("   3. Emphasize 'curriculum development' over 'coding curriculum'")
    print("   4. Add 'student assessment' and 'progress tracking'")
    
    print("\n   To improve JobFit Score:")
    print("   1. Tailor summary to tutoring (not just coding)")
    print("   2. Highlight math/science teaching if applicable")
    print("   3. Mention work with younger students (grades 1-10)")
    print("   4. Add 'parent communication' and 'personalized learning'")
    
    # Conclusion
    print("\n" + "="*100)
    print("VERDICT")
    print("="*100)
    
    combined = (ats_score + jobfit_score) / 2
    
    if combined >= 80:
        verdict = "✅ EXCELLENT MATCH - Highly likely to pass ATS"
    elif combined >= 65:
        verdict = "⚠️ GOOD MATCH - Likely to pass with minor improvements"
    elif combined >= 50:
        verdict = "⚠️ MODERATE MATCH - Needs improvement to pass ATS"
    else:
        verdict = "❌ POOR MATCH - Significant rewriting needed"
    
    print(f"\n{verdict}")
    print(f"\nCombined Score: {combined:.2f}/100")
    print(f"ATS Score: {ats_score:.2f}/100")
    print(f"JobFit Score: {jobfit_score:.2f}/100")
    
    print("\n📝 SUMMARY:")
    print(f"   The main issue is domain mismatch: Your CV focuses on 'coding/programming education'")
    print(f"   while the JD seeks a 'math/English/science tutor'. The technical skills overlap is low.")
    print(f"   Rewriting can help incorporate keywords, but the fundamental mismatch will limit scores.")
    
    return initial_report

if __name__ == "__main__":
    result = main()
