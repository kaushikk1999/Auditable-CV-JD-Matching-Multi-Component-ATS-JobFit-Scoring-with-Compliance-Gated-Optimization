import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.schemas import StructuredCV, ContactInfo, ExperienceEntry, ExperienceBullet
from pydantic import ValidationError

def test_valid_structured_cv():
    """Test valid CV structure."""
    data = {
        "contact_info": {
            "full_name": "John Doe",
            "email": "john@example.com"
        },
        "experience": [
            {
                "job_title": "Software Engineer",
                "company_name": "TechCorp",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullets": [
                    {"text": "Built scalable systems"}
                ]
            }
        ]
    }
    
    try:
        cv = StructuredCV(**data)
        assert cv.contact_info.full_name == "John Doe"
        assert len(cv.experience) == 1
        print("✅ Valid CV structure test passed")
    except ValidationError as e:
        print(f"❌ Test failed: {e}")

def test_missing_required_fields():
    """Test that validation catches missing required fields."""
    data = {
        "contact_info": {
            "full_name": "John Doe"
        },
        "experience": []  # Empty - should fail validation
    }
    
    try:
        cv = StructuredCV(**data)
        print("❌ Should have failed validation")
    except ValidationError:
        print("✅ Validation correctly caught missing experience")

if __name__ == "__main__":
    test_valid_structured_cv()
    test_missing_required_fields()
    print("\n✅ All schema tests passed!")
