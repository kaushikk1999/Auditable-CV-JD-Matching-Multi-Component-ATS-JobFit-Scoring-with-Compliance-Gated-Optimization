import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.rewrite_validator import RewriteValidator
from modules.gemini_rewriter import GeminiRewriter

def test_constraint_validator():
    """Test that validator catches violations."""
    validator = RewriteValidator()
    
    # Test summary with stopwords
    original = "I am a software developer"
    rewritten = "I am responsible for developing software"
    
    is_valid, violations = validator.validate_summary(original, rewritten)
    
    assert not is_valid, "Should catch stopwords"
    assert any("stopword" in v.lower() for v in violations)
    print("✅ Validator catches stopwords")

def test_entity_preservation():
    """Test that entity changes are detected."""
    validator = RewriteValidator()
    
    original_cv = {
        "experience": [
            {
                "job_title": "Software Engineer",
                "company_name": "TechCorp",
                "start_date": "Jan 2020",
                "end_date": "Present"
            }
        ],
        "education": [
            {"degree": "BS Computer Science", "institution": "University"}
        ]
    }
    
    # Change job title
    rewritten_cv = {
        "experience": [
            {
                "job_title": "Senior Software Engineer",  # CHANGED
                "company_name": "TechCorp",
                "start_date": "Jan 2020",
                "end_date": "Present"
            }
        ],
        "education": [
            {"degree": "BS Computer Science", "institution": "University"}
        ]
    }
    
    is_valid, violations = validator.validate_no_entity_changes(original_cv, rewritten_cv)
    
    assert not is_valid, "Should detect job title change"
    assert any("job title" in v.lower() for v in violations)
    print("✅ Entity preservation validated")

def test_no_fabrication():
    """Test that skills validator catches fabricated skills."""
    validator = RewriteValidator()
    
    original_skills = [
        {"category_name": "Languages", "skills": ["Python", "Java"]}
    ]
    
    rewritten_skills = {
        "Languages": ["Python", "Java", "Rust", "Go"]  # Rust, Go not in original
    }
    
    experience = [
        {
            "job_title": "Python Developer",
            "bullets": [{"text": "Built Python applications"}]
        }
    ]
    
    is_valid, violations = validator.validate_skills(original_skills, rewritten_skills, experience)
    
    # Should flag Rust and Go as potential fabrications
    assert not is_valid or len(violations) > 0
    print(f"✅ Fabrication check: {len(violations)} potential issues found")

if __name__ == "__main__":
    test_constraint_validator()
    test_entity_preservation()
    test_no_fabrication()
    print("\n✅ All rewriting tests passed!")
