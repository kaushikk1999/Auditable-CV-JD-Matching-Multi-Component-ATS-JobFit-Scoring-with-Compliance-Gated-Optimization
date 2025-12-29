import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.jd_analyzer import JDAnalyzer
from modules.schemas import EnhancedJD, KeywordTaxonomy, RequirementLevel

class TestJDAnalyzer:
    
    def test_clean_response_with_json_fence(self):
        """Test cleaning response with ```json fence"""
        response = "```json\n{\"test\": \"data\"}\n```"
        cleaned = JDAnalyzer._clean_response(response)
        assert cleaned == '{"test": "data"}'
    
    def test_clean_response_no_fence(self):
        """Test cleaning response without fence"""
        response = '{"test": "data"}'
        cleaned = JDAnalyzer._clean_response(response)
        assert cleaned == '{"test": "data"}'
    
    def test_extract_taxonomy_valid_json(self):
        """Test extracting taxonomy with valid Gemini response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "keyword_taxonomy": {
                "technical_skills": ["Python"],
                "tools_technologies": ["Docker"],
                "soft_skills": ["Communication"],
                "domain_knowledge": ["Finance"],
                "certifications": []
            },
            "must_have_requirements": [{
                "text": "Python required",
                "is_required": True,
                "keywords": ["Python"]
            }],
            "nice_to_have_requirements": []
        })
        mock_model.generate_content.return_value = mock_response
        
        analyzer = JDAnalyzer(mock_model)
        result = analyzer._extract_taxonomy("Sample JD")
        
        assert "keyword_taxonomy" in result
        assert result["keyword_taxonomy"]["technical_skills"] == ["Python"]
    
    def test_extract_taxonomy_invalid_json_fallback(self):
        """Test that invalid JSON returns fallback taxonomy"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        mock_model.generate_content.return_value = mock_response
        
        analyzer = JDAnalyzer(mock_model)
        result = analyzer._extract_taxonomy("Sample JD")
        
        # Should return empty fallback
        assert result["keyword_taxonomy"]["technical_skills"] == []
        assert result["must_have_requirements"] == []
        assert result["nice_to_have_requirements"] == []
    
    def test_enhance_jd_success(self):
        """Test successful JD enhancement"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "keyword_taxonomy": {
                "technical_skills": ["Python"],
                "tools_technologies": [],
                "soft_skills": [],
                "domain_knowledge": [],
                "certifications": []
            },
            "must_have_requirements": [],
            "nice_to_have_requirements": []
        })
        mock_model.generate_content.return_value = mock_response
        
        analyzer = JDAnalyzer(mock_model)
        
        # Phase 1 basic JD
        basic_jd = {
            "job_title": "Developer",
            "company_name": "Tech Corp",
            "location": "Remote",
            "work_type": "Full-time",
            "experience_required": "3 years",
            "company_overview": "A tech company",
            "role_summary": "Build things",
            "key_responsibilities": ["Code"],
            "required_skills": ["Python"],
            "preferred_skills": [],
            "education": "BS",
            "soft_skills": [],
            "diversity_statement": "We value diversity",
            "recruiter_contact": "hr@tech.com",
            "ats_keywords": ["Python", "Developer"]
        }
        
        enhanced = analyzer.enhance_jd(basic_jd, "Sample JD text")
        
        assert isinstance(enhanced, EnhancedJD)
        assert enhanced.job_title == "Developer"
        assert enhanced.keyword_taxonomy.technical_skills == ["Python"]
    
    def test_get_all_keywords_deduplication(self):
        """Test that get_all_keywords removes duplicates case-insensitively"""
        mock_model = MagicMock()
        analyzer = JDAnalyzer(mock_model)
        
        # Create an enhanced JD with duplicate keywords
        enhanced_jd = EnhancedJD(
            job_title="Dev",
            company_name="Corp",
            location="NYC",
            work_type="Full",
            experience_required="3",
            company_overview="overview",
            role_summary="summary",
            key_responsibilities=[],
            required_skills=["Python"],
            preferred_skills=[],
            education="BS",
            soft_skills=[],
            diversity_statement="statement",
            recruiter_contact="contact",
            ats_keywords=["Python", "AWS", "docker"],  # lowercase docker
            keyword_taxonomy=KeywordTaxonomy(
                technical_skills=["python", "Java"],  # lowercase python (duplicate)
                tools_technologies=["Docker", "Kubernetes"],  # capitalized Docker (duplicate)
                soft_skills=[],
                domain_knowledge=[],
                certifications=[]
            )
        )
        
        keywords = analyzer.get_all_keywords(enhanced_jd)
        
        # Should have Python (first occurrence), Java, Docker (first occurrence), Kubernetes, AWS
        # All duplicates removed case-insensitively
        assert len(keywords) == 5
        # Check that first occurrence is preserved
        assert "python" in keywords  # from technical_skills (first occurrence)
        assert "Python" not in keywords  # from required_skills or ats_keywords (duplicate)
        assert "Docker" in keywords  # from tools_technologies (first occurrence)
        assert "docker" not in keywords  # from ats_keywords (duplicate)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
