"""
Better-matched test case: Software Engineer CV + JD with high keyword alignment.
This test verifies that the scoring and rewriting system can achieve 80+ scores.
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

# Well-matched CV (Software Engineer with Python, Django, AWS)
CV_TEXT = """
ALEX JOHNSON
Email: alex.johnson@email.com | Phone: +1-555-0123
LinkedIn: linkedin.com/in/alexjohnson | GitHub: github.com/alexjohnson

SUMMARY
Senior Software Engineer with 5+ years of experience building scalable web applications using Python and Django.
Expertise in cloud infrastructure (AWS), RESTful APIs, microservices architecture, and agile development.
Proven track record of delivering high-quality code and leading technical teams.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, TypeScript
Frameworks: Django, Flask, React, FastAPI
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD, Terraform
Databases: PostgreSQL, MySQL, MongoDB, Redis
Tools: Git, Jenkins, GitHub Actions, JIRA, Postman

PROFESSIONAL EXPERIENCE

Senior Software Engineer | Tech Solutions Inc | Jan 2021 - Present
• Designed and implemented RESTful APIs using Django and Python, serving 1M+ daily requests
• Built microservices architecture on AWS using Docker and Kubernetes, improving scalability by 300%
• Led migration from monolithic to microservices, reducing deployment time by 60%
• Mentored team of 4 junior developers in Python best practices and code reviews
• Implemented CI/CD pipelines using GitHub Actions and AWS CodePipeline

Software Engineer | Digital Innovations Co | Mar 2019 - Dec 2020
• Developed full-stack web applications using Django, React, and PostgreSQL
• Optimized database queries and implemented caching with Redis, reducing response time by 40%
• Collaborated with product team in agile sprints to deliver features on time
• Wrote comprehensive unit tests achieving 90% code coverage
• Deployed applications to AWS EC2 and managed infrastructure as code with Terraform

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2018
GPA: 3.8/4.0

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate (2022)
• Python Professional Certification (2020)
"""

# Well-matched JD (requires Python, Django, AWS - all present in CV)
JD_TEXT = """
Senior Software Engineer
Tech Corp - San Francisco, CA (Remote Available)

We are seeking an experienced Senior Software Engineer to join our growing engineering team. The ideal candidate will have strong expertise in Python, Django, and cloud technologies.

REQUIREMENTS:
Education: Bachelor's degree in Computer Science or related field (required)

Required Skills:
- Python Programming (5+ years experience)
- Django Framework
- RESTful API Design
- AWS Cloud Platform
- Docker and Kubernetes
- PostgreSQL or MySQL
- Git Version Control
- Agile Development

Preferred Skills:
- React or frontend frameworks
- CI/CD pipelines
- Microservices architecture
- MongoDB
- Terraform

KEY RESPONSIBILITIES:
- Design and develop scalable backend services using Python and Django
- Build and maintain RESTful APIs for web and mobile applications
- Deploy and manage applications on AWS cloud infrastructure
- Implement database schemas and optimize query performance
- Collaborate with cross-functional teams in agile environment
- Mentor junior engineers and conduct code reviews
- Write clean, testable, and well-documented code

JOB DETAILS:
- Location: Remote
- Experience: 5+ years
- Type: Full-time
- Salary: $120,000 - $180,000
"""

def main():
    print("="*80)
    print("WELL-MATCHED TEST: Software Engineer CV + JD")
    print("="*80)
    print()
    
    Storage.save_raw_cv(CV_TEXT)
    Storage.save_raw_jd(JD_TEXT)
    
    gemini = GeminiClient()
    
    # Phase 1
    print("📄 Phase 1: JD Extraction")
    jd_parsed = gemini.extract_jd_structure(JD_TEXT)
    print(f"✅ Job Title: {jd_parsed.get('job_title')}")
    
    # Phase 2
    print("\n🔧 Phase 2: CV Structuring")
    structurer = CVStructurer(gemini.model)
    cv_structured = structurer.parse(CV_TEXT)
    print(f"✅ {len(cv_structured.experience)} experiences, {len(cv_structured.skills)} skill categories")
    
    # Phase 3
    print("\n🔍 Phase 3: JD Enhancement")
    analyzer = JDAnalyzer(gemini.model)
    jd_enhanced = analyzer.enhance_jd(jd_parsed, JD_TEXT)
    print(f"✅ {len(jd_enhanced.required_skills)} required, {len(jd_enhanced.preferred_skills)} preferred skills")
    
    # Phase 5: Initial Scoring
    print("\n📊 Phase 5: Initial Scoring")
    print("-" * 80)
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
    
    print(f"\n📊 ATS Components:")
    for comp, score in initial_report['ats_components'].items():
        status = "✅" if score >= 70 else "⚠️"
        print(f"   {status} {comp.replace('_', ' ').title()}: {score:.2f}")
    
    print(f"\n💼 JobFit Components:")
    for comp, score in initial_report['jobfit_components'].items():
        status = "✅" if score >= 70 else "⚠️"
        print(f"   {status} {comp.replace('_', ' ').title()}: {score:.2f}")
    
    # Phase 6: Rewriting (with correct target)
    print("\n✍️ Phase 6: CV Rewriting")
    print("-" * 80)
    print("Starting rewriting with target: 80+...")
    
    engine = RewritingEngine(max_iterations=10, target_score=80.0)
    result = engine.optimize_cv(
        cv_structured,
        jd_enhanced,
        CV_TEXT,
        JD_TEXT
    )
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    final_scores = result['final_scores']
    improvements = result['improvements']
    
    print(f"\n🎯 ATS Score: {final_scores['ats_score']:.2f} ({improvements['ats_delta']:+.2f})")
    print(f"💼 JobFit Score: {final_scores['jobfit_score']:.2f} ({improvements['jobfit_delta']:+.2f})")
    
    print(f"\n✅ SUCCESS CRITERIA:")
    ats_pass = final_scores['ats_score'] >= 80
    jobfit_pass = final_scores['jobfit_score'] >= 80
    print(f"   ATS >= 80: {'✅ PASS' if ats_pass else '❌ FAIL'} ({final_scores['ats_score']:.2f})")
    print(f"   JobFit >= 80: {'✅ PASS' if jobfit_pass else '❌ FAIL'} ({final_scores['jobfit_score']:.2f})")
    
    if ats_pass and jobfit_pass:
        print("\n🎉 SUCCESS! Both scores exceeded 80!")
    else:
        print("\n⚠️ Needs improvement")
        
    print(f"\n📈 Iterations completed: {len(result['iterations']) - 1}")
    
    return result

if __name__ == "__main__":
    result = main()
