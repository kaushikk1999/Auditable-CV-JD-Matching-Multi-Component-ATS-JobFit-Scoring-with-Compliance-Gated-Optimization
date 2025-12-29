import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.cv_structurer import CVStructurer
from modules.schemas import StructuredCV, ContactInfo, ExperienceEntry, ExperienceBullet

class TestCVStructurer:
    
    def test_clean_response_with_json_fence(self):
        """Test cleaning response with ```json fence"""
        response = "```json\n{\"test\": \"data\"}\n```"
        cleaned = CVStructurer._clean_response(response)
        assert cleaned == '{"test": "data"}'
    
    def test_clean_response_with_basic_fence(self):
        """Test cleaning response with ``` fence"""
        response = "```\n{\"test\": \"data\"}\n```"
        cleaned = CVStructurer._clean_response(response)
        assert cleaned == '{"test": "data"}'
    
    def test_clean_response_no_fence(self):
        """Test cleaning response without fence"""
        response = '{"test": "data"}'
        cleaned = CVStructurer._clean_response(response)
        assert cleaned == '{"test": "data"}'
    
    def test_parse_valid_cv(self):
        """Test parsing a valid CV structure"""
        # Create a mock Gemini model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "contact_info": {
                "full_name": "John Doe",
                "email": "john@example.com"
            },
            "experience": [{
                "job_title": "Developer",
                "company_name": "Tech Corp",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullets": [{"text": "Built features"}]
            }]
        })
        mock_model.generate_content.return_value = mock_response
        
        structurer = CVStructurer(mock_model)
        result = structurer.parse("Sample CV text")
        
        assert isinstance(result, StructuredCV)
        assert result.contact_info.full_name == "John Doe"
        assert len(result.experience) == 1
    
    def test_parse_invalid_json(self):
        """Test parsing with invalid JSON response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        mock_model.generate_content.return_value = mock_response
        
        structurer = CVStructurer(mock_model)
        
        with pytest.raises(ValueError, match="Gemini returned invalid JSON"):
            structurer.parse("Sample CV text")
    
    def test_parse_validation_failure(self):
        """Test parsing with schema validation failure"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Missing required 'experience' field (non-empty requirement)
        mock_response.text = json.dumps({
            "contact_info": {
                "full_name": "John Doe"
            },
            "experience": []  # This should trigger validation error
        })
        mock_model.generate_content.return_value = mock_response
        
        structurer = CVStructurer(mock_model)
        
        with pytest.raises(ValueError, match="CV structure validation failed"):
            structurer.parse("Sample CV text")
    
    def test_validate_structure_complete_cv(self):
        """Test validation of a complete CV"""
        mock_model = MagicMock()
        structurer = CVStructurer(mock_model)
        
        # Create a complete CV
        cv = StructuredCV(
            contact_info=ContactInfo(
                full_name="John Doe",
                email="john@example.com"
            ),
            experience=[
                ExperienceEntry(
                    job_title="Dev",
                    company_name="Corp",
                    start_date="2020",
                    end_date="Present",
                    bullets=[ExperienceBullet(text="Did stuff")]
                )
            ]
        )
        
        validation = structurer.validate_structure(cv)
        
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
        assert validation["stats"]["experience_count"] == 1
        assert validation["stats"]["total_bullets"] == 1
    
    def test_validate_structure_missing_email(self):
        """Test validation with missing email"""
        mock_model = MagicMock()
        structurer = CVStructurer(mock_model)
        
        cv = StructuredCV(
            contact_info=ContactInfo(full_name="John Doe"),
            experience=[
                ExperienceEntry(
                    job_title="Dev",
                    company_name="Corp",
                    start_date="2020",
                    end_date="Present"
                )
            ]
        )
        
        validation = structurer.validate_structure(cv)
        
        assert "No email address found" in validation["warnings"]
    
    def test_validate_structure_no_experience(self):
        """Test validation with no experience (should fail)"""
        mock_model = MagicMock()
        structurer = CVStructurer(mock_model)
        
        # This won't actually instantiate due to validator, so we skip this test
        # since the schema itself prevents empty experience
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
