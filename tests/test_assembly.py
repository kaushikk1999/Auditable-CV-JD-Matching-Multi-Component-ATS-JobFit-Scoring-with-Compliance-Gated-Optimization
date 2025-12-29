import sys
import unittest
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.cv_assembler import CVAssembler
from tests.validation_utils import TestResult, normalize_string, normalize_bullet, save_report

class TestAssembly(unittest.TestCase):
    
    def setUp(self):
        self.assembler = CVAssembler()
        
        # Canonical Test Data
        self.original_cv = {
            "contact_info": {
                "full_name": "John Doe", 
                "email": "john@example.com",
                "phone": "555-0100",
                "location": "New York, NY"
            },
            "education": [
                {
                    "degree": "BS Computer Science", 
                    "institution": "University of Tech",
                    "graduation_date": "2018",
                    "gpa": "3.8"
                }
            ],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company_name": "Tech Corp",
                    "start_date": "2020",
                    "end_date": "Present",
                    "bullets": [{"text": "Original bullet 1"}]
                }
            ],
            "projects": [
                {"project_name": "Old Project", "bullets": [{"text": "Old details"}]}
            ],
            "certifications": [
                {"name": "Cert A", "issuer": "Issuer A"}
            ],
            "summary": {"text": "Original summary"}
        }
        
        self.optimized_cv = {
            "summary": {"text": "Optimized summary with keywords"},
            "skills": [
                {"category_name": "Core", "skills": ["Python", "AI"]}
            ],
            "experience": [
                {
                    "bullets": [{"text": "Optimized bullet 1 (Impact: 20%)"}]
                }
            ],
            # Projects rewritten
            "projects": [
                {"project_name": "Old Project", "bullets": [{"text": "Optimized project details"}]}
            ]
        }

    def test_entity_preservation(self):
        """Test strict preservation of education, titles, companies, dates, contact."""
        result = TestResult("ASM-01", "Entity Preservation")
        
        try:
            final_cv = self.assembler.assemble(self.optimized_cv, self.original_cv)
            
            # 1. Education
            self.assertEqual(final_cv["education"], self.original_cv["education"])
            result.add_detail("Education preserved exactly")
            
            # 2. Contact Info
            self.assertEqual(final_cv["contact_info"], self.original_cv["contact_info"])
            result.add_detail("Contact info preserved exactly")
            
            # 3. Experience Entities (Title, Company, Dates)
            orig_exp = self.original_cv["experience"][0]
            final_exp = final_cv["experience"][0]
            
            self.assertEqual(final_exp["job_title"], orig_exp["job_title"])
            self.assertEqual(final_exp["company_name"], orig_exp["company_name"])
            self.assertEqual(final_exp["start_date"], orig_exp["start_date"])
            self.assertEqual(final_exp["end_date"], orig_exp["end_date"])
            result.add_detail("Experience entities preserved")
            
            result.pass_test("All entities preserved correctly")
            
        except AssertionError as e:
            result.fail_test(f"Assertion failed: {str(e)}")
        except Exception as e:
            result.fail_test(f"Exception: {str(e)}")
            
        save_report(result.to_dict(), "tests/reports/asm_01_entity_preservation.json")

    def test_content_merging(self):
        """Test correct sourcing of rewritten vs original content."""
        result = TestResult("ASM-02", "Content Merging")
        
        try:
            final_cv = self.assembler.assemble(self.optimized_cv, self.original_cv)
            
            # 1. Summary (should be optimized)
            self.assertEqual(final_cv["summary"]["text"], self.optimized_cv["summary"]["text"])
            result.add_detail("Summary used from optimized")
            
            # 2. Experience Bullets (should be optimized)
            self.assertEqual(
                final_cv["experience"][0]["bullets"][0]["text"], 
                self.optimized_cv["experience"][0]["bullets"][0]["text"]
            )
            result.add_detail("Experience bullets used from optimized")
            
            # 3. Projects (should be optimized as provided)
            self.assertEqual(
                final_cv["projects"][0]["bullets"][0]["text"],
                self.optimized_cv["projects"][0]["bullets"][0]["text"]
            )
            result.add_detail("Projects used from optimized")
            
            # 4. Certifications (should be original as not in optimized)
            self.assertEqual(final_cv["certifications"], self.original_cv["certifications"])
            result.add_detail("Certifications fell back to original")
            
            result.pass_test("Content merging logic correct")
            
        except AssertionError as e:
            result.fail_test(f"Assertion failed: {str(e)}")
            
        save_report(result.to_dict(), "tests/reports/asm_02_content_merging.json")

    def test_text_conversion(self):
        """Test ATS-friendly text conversion rules."""
        result = TestResult("ASM-03", "Text Conversion")
        
        try:
            final_cv = self.assembler.assemble(self.optimized_cv, self.original_cv)
            text_output = self.assembler.to_text(final_cv)
            
            # 1. All sections present
            required_sections = [
                "JOHN DOE", "john@example.com", 
                "PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", 
                "PROFESSIONAL EXPERIENCE", "PROJECTS", 
                "EDUCATION", "CERTIFICATIONS"
            ]
            for sec in required_sections:
                if sec not in text_output:
                    raise AssertionError(f"Missing section/content: {sec}")
            result.add_detail("All sections present")
            
            # 2. Headers all caps (heuristic: check known headers)
            headers = ["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "PROFESSIONAL EXPERIENCE"]
            for h in headers:
                if h not in text_output:
                    raise AssertionError(f"Header not found or not caps: {h}")
            result.add_detail("Headers formatted correctly")
            
            # 3. Bullets with "•" prefix
            # Check if bullets exist and start with •
            bullet_lines = [line.strip() for line in text_output.split('\n') if "Optimized bullet" in line]
            for line in bullet_lines:
                if not line.startswith("•"):
                    raise AssertionError(f"Bullet missing prefix: {line}")
            result.add_detail("Bullets formatted with •")
            
            # 4. Contact info at top
            lines = [l.strip() for l in text_output.split('\n') if l.strip()]
            if "john@example.com" not in lines[1]: # Line 0 is Name, Line 1 Contact
                 # Allow for some variation, but it should be early
                 if text_output.find("john@example.com") > text_output.find("PROFESSIONAL SUMMARY"):
                     raise AssertionError("Contact info not at top")
            result.add_detail("Contact info at top")
            
            result.pass_test("Text conversion rules satisfied")
            
        except AssertionError as e:
            result.fail_test(f"Assertion failed: {str(e)}")
            
        save_report(result.to_dict(), "tests/reports/asm_03_text_conversion.json")

if __name__ == "__main__":
    unittest.main()
