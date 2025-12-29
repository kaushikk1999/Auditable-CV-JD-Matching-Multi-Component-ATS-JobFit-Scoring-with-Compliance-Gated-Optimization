import sys
import json
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.storage import Storage
from modules.schemas import StructuredCV, ContactInfo, ExperienceEntry, EnhancedJD, KeywordTaxonomy

@pytest.fixture
def temp_processed_dir(tmp_path):
    """Create a temporary processed directory for testing."""
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    with patch('modules.storage.DATA_PROCESSED_DIR', processed_dir):
        yield processed_dir

def test_save_structured_cv(temp_processed_dir):
    """Test saving structured CV"""
    # Create a minimal structured CV
    cv = StructuredCV(
        contact_info=ContactInfo(full_name="John Doe", email="john@example.com"),
        experience=[
            ExperienceEntry(
                job_title="Developer",
                company_name="Tech Corp",
                start_date="2020",
                end_date="Present"
            )
        ]
    )
    
    filepath = Storage.save_structured_cv(cv)
    
    assert filepath.exists()
    assert filepath.name == "cv_structured.json"
    
    # Verify content
    data = json.loads(filepath.read_text())
    assert "structured_at" in data
    assert data["schema_version"] == "2.0"
    assert data["data"]["contact_info"]["full_name"] == "John Doe"

def test_load_structured_cv(temp_processed_dir):
    """Test loading structured CV"""
    # First save a CV
    cv = StructuredCV(
        contact_info=ContactInfo(full_name="Jane Smith"),
        experience=[
            ExperienceEntry(
                job_title="Engineer",
                company_name="Corp",
                start_date="2019",
                end_date="2021"
            )
        ]
    )
    Storage.save_structured_cv(cv)
    
    # Then load it
    loaded_cv = Storage.load_structured_cv()
    
    assert isinstance(loaded_cv, StructuredCV)
    assert loaded_cv.contact_info.full_name == "Jane Smith"
    assert len(loaded_cv.experience) == 1

def test_load_structured_cv_not_found(temp_processed_dir):
    """Test loading non-existent structured CV raises error"""
    with pytest.raises(FileNotFoundError, match="Structured CV not found"):
        Storage.load_structured_cv()

def test_save_enhanced_jd(temp_processed_dir):
    """Test saving enhanced JD"""
    # Create a minimal enhanced JD
    jd = EnhancedJD(
        job_title="Developer",
        company_name="Tech Inc",
        location="NYC",
        work_type="Full-time",
        experience_required="3 years",
        company_overview="A company",
        role_summary="Build stuff",
        key_responsibilities=["Code"],
        required_skills=["Python"],
        preferred_skills=[],
        education="BS",
        soft_skills=[],
        diversity_statement="We value diversity",
        recruiter_contact="hr@tech.com",
        ats_keywords=["Python"],
        keyword_taxonomy=KeywordTaxonomy(
            technical_skills=["Python"],
            tools_technologies=[],
            soft_skills=[],
            domain_knowledge=[],
            certifications=[]
        )
    )
    
    filepath = Storage.save_enhanced_jd(jd)
    
    assert filepath.exists()
    assert filepath.name == "jd_enhanced.json"
    
    # Verify content
    data = json.loads(filepath.read_text())
    assert "enhanced_at" in data
    assert data["schema_version"] == "2.0"
    assert data["data"]["job_title"] == "Developer"

def test_load_enhanced_jd(temp_processed_dir):
    """Test loading enhanced JD"""
    # First save a JD
    jd = EnhancedJD(
        job_title="Engineer",
        company_name="Corp",
        location="SF",
        work_type="Remote",
        experience_required="5 years",
        company_overview="overview",
        role_summary="summary",
        key_responsibilities=[],
        required_skills=[],
        preferred_skills=[],
        education="MS",
        soft_skills=[],
        diversity_statement="statement",
        recruiter_contact="contact",
        ats_keywords=[],
        keyword_taxonomy=KeywordTaxonomy()
    )
    Storage.save_enhanced_jd(jd)
    
    # Then load it
    loaded_jd = Storage.load_enhanced_jd()
    
    assert isinstance(loaded_jd, EnhancedJD)
    assert loaded_jd.job_title == "Engineer"
    assert loaded_jd.education == "MS"

def test_load_enhanced_jd_not_found(temp_processed_dir):
    """Test loading non-existent enhanced JD raises error"""
    with pytest.raises(FileNotFoundError, match="Enhanced JD not found"):
        Storage.load_enhanced_jd()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
