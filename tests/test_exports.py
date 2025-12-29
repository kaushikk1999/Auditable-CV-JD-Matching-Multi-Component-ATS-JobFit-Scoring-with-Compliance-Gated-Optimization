import sys
import unittest
import tempfile
import json
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.exporters import PDFExporter, DOCXExporter, HTMLExporter, JSONExporter
from modules.cv_assembler import CVAssembler
from tests.validation_utils import TestResult, check_file_exists, save_report

class TestExports(unittest.TestCase):
    
    def setUp(self):
        self.cv_text = """JOHN DOE
john@example.com | 555-1234

PROFESSIONAL SUMMARY
Software engineer with 5 years experience.

TECHNICAL SKILLS
Languages: Python, Java

PROFESSIONAL EXPERIENCE
Software Engineer | Tech Corp
2020 – Present
• Built scalable systems
"""
        self.cv_dict = {
            "contact_info": {"full_name": "John Doe"},
            "experience": [],
            "metadata": {"version": "1.0"}
        }
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_pdf_export(self):
        """Test PDF generation validity."""
        result = TestResult("EXP-01", "PDF Export")
        output_path = self.tmp_dir / "test.pdf"
        
        try:
            exporter = PDFExporter()
            exporter.export(self.cv_text, output_path)
            
            # 1. File exists and size > 0
            if not check_file_exists(output_path, min_size_bytes=100):
                raise AssertionError("PDF file missing or too small")
            result.add_detail(f"PDF created ({output_path.stat().st_size} bytes)")
            
            # 2. Basic Header Check (Sanity)
            with open(output_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    raise AssertionError("Invalid PDF header")
            result.add_detail("Valid PDF header detected")
            
            result.pass_test("PDF export valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), "tests/reports/exp_01_pdf.json")

    def test_docx_export(self):
        """Test DOCX generation validity."""
        result = TestResult("EXP-02", "DOCX Export")
        output_path = self.tmp_dir / "test.docx"
        
        try:
            exporter = DOCXExporter()
            exporter.export(self.cv_text, output_path)
            
            # 1. File exists and size > 0
            if not check_file_exists(output_path, min_size_bytes=1000):
                raise AssertionError("DOCX file missing or too small")
            result.add_detail(f"DOCX created ({output_path.stat().st_size} bytes)")
            
            # 2. Zip Signature Check (DOCX is a zip)
            with open(output_path, 'rb') as f:
                header = f.read(2)
                if header != b'PK':
                    raise AssertionError("Invalid DOCX (Zip) header")
            result.add_detail("Valid DOCX structure detected")
            
            result.pass_test("DOCX export valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), "tests/reports/exp_02_docx.json")

    def test_html_export(self):
        """Test HTML generation validity."""
        result = TestResult("EXP-03", "HTML Export")
        output_path = self.tmp_dir / "test.html"
        
        try:
            exporter = HTMLExporter()
            exporter.export(self.cv_text, output_path)
            
            # 1. File exists
            if not check_file_exists(output_path, min_size_bytes=50):
                raise AssertionError("HTML file missing or too small")
            
            # 2. Valid HTML structure
            content = output_path.read_text(encoding='utf-8')
            if "<!DOCTYPE html>" not in content and "<html>" not in content:
                raise AssertionError("Missing HTML doctype/tags")
            result.add_detail("Valid HTML tags found")
            
            # 3. Bootstrap check
            if "bootstrap" not in content.lower():
                raise AssertionError("Bootstrap styles not loaded")
            result.add_detail("Bootstrap reference found")
            
            result.pass_test("HTML export valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), "tests/reports/exp_03_html.json")

    def test_json_export(self):
        """Test JSON generation validity."""
        result = TestResult("EXP-04", "JSON Export")
        output_path = self.tmp_dir / "test.json"
        
        try:
            exporter = JSONExporter()
            exporter.export(self.cv_dict, output_path)
            
            # 1. File exists
            if not check_file_exists(output_path):
                raise AssertionError("JSON file missing")
            
            # 2. Parse and validate
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            if "cv" not in data:
                raise AssertionError("Missing 'cv' key in JSON")
            if "exported_at" not in data:
                raise AssertionError("Missing metadata in JSON")
                
            result.add_detail("JSON structure valid and reloadable")
            result.pass_test("JSON export valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), "tests/reports/exp_04_json.json")

    def test_txt_export(self):
        """Test TXT output (via Assembler)."""
        result = TestResult("EXP-05", "TXT Export")
        
        try:
            assembler = CVAssembler()
            text = assembler.to_text(self.cv_dict)
            
            if not text or len(text) == 0:
                raise AssertionError("TXT output empty")
            
            # Check for special chars (basic check)
            # Allow newlines, tabs, bullets, basic punctuation
            # This is a heuristic; mainly ensuring no binary garbage
            if "\0" in text:
                raise AssertionError("Binary null characters found in TXT")
                
            result.add_detail("TXT output generated and clean")
            result.pass_test("TXT export valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), "tests/reports/exp_05_txt.json")

if __name__ == "__main__":
    unittest.main()
