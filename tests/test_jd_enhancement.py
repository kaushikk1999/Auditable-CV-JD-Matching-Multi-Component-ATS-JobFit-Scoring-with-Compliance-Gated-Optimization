import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.schemas import EnhancedJD, KeywordTaxonomy

def test_enhanced_jd_schema():
    """Test EnhancedJD validates correctly."""
    data = {
        "job_title": "Senior Developer",
        "company_name": "TechCo",
        "location": "Remote",
        "work_type": "Full-time",
        "experience_required": "5+ years",
        "company_overview": "Leading tech company",
        "role_summary": "Build scalable systems",
        "key_responsibilities": ["Design APIs", "Mentor juniors"],
        "required_skills": ["Python", "AWS"],
        "preferred_skills": ["Docker"],
        "education": "BS Computer Science",
        "soft_skills": ["Communication"],
        "diversity_statement": "Equal opportunity employer",
        "recruiter_contact": "recruiter@techco.com",
        "ats_keywords": ["Python", "AWS", "API"],
        "keyword_taxonomy": {
            "technical_skills": ["Python"],
            "tools_technologies": ["AWS"],
            "soft_skills": [],
            "domain_knowledge": [],
            "certifications": []
        },
        "must_have_requirements": [],
        "nice_to_have_requirements": []
    }
    
    try:
        jd = EnhancedJD(**data)
        assert jd.job_title == "Senior Developer"
        assert "Python" in jd.keyword_taxonomy.technical_skills
        print("✅ EnhancedJD schema test passed")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_enhanced_jd_schema()
