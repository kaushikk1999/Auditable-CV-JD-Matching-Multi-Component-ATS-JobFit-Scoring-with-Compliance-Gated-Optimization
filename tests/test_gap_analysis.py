
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.gap_analyzer import KeywordGapAnalyzer, ExperienceAligner
from modules.schemas import (
    StructuredCV, EnhancedJD, ContactInfo, ExperienceEntry, 
    ExperienceBullet, SkillCategory, KeywordTaxonomy
)

def test_gap_analysis():
    """Test keyword gap analysis."""
    # Create minimal CV
    cv = StructuredCV(
        contact_info=ContactInfo(full_name="Test User", email="test@example.com"),
        skills=[
            SkillCategory(category_name="Languages", skills=["Python", "JavaScript"])
        ],
        experience=[
            ExperienceEntry(
                job_title="Developer",
                company_name="TechCo",
                start_date="Jan 2020",
                end_date="Present",
                bullets=[
                    ExperienceBullet(text="Built scalable Python applications")
                ]
            )
        ]
    )
    
    # Create minimal JD
    jd = EnhancedJD(
        job_title="Senior Developer",
        company_name="NewCo",
        location="Remote",
        work_type="Full-time",
        experience_required="5 years",
        company_overview="Tech company",
        role_summary="Build systems",
        key_responsibilities=["Design APIs", "Mentor team"],
        required_skills=["Python", "AWS", "Docker"],
        preferred_skills=["Kubernetes"],
        education="BS",
        soft_skills=["Communication"],
        diversity_statement="",
        recruiter_contact="",
        ats_keywords=["Python", "AWS"],
        keyword_taxonomy=KeywordTaxonomy(
            technical_skills=["Python", "AWS"],
            tools_technologies=["Docker"],
            soft_skills=[],
            domain_knowledge=[],
            certifications=[]
        ),
        must_have_requirements=[],
        nice_to_have_requirements=[]
    )
    
    # Run analysis
    analyzer = KeywordGapAnalyzer()
    result = analyzer.analyze(cv, jd)
    
    # Assertions
    assert result.coverage_stats["overall_coverage"] > 0
    assert len(result.present_keywords) >= 1  # At least Python should match
    assert len(result.missing_keywords) >= 1  # AWS, Docker should be missing
    
    print("✅ Gap analysis test passed")
    print(f"   Present: {len(result.present_keywords)}, Missing: {len(result.missing_keywords)}")

if __name__ == "__main__":
    test_gap_analysis()
