from pathlib import Path
from modules.exporters import PDFExporter, DOCXExporter, HTMLExporter, JSONExporter
import os

def test_exporters():
    output_dir = Path("test_exports")
    output_dir.mkdir(exist_ok=True)
    
    cv_text = """JOHN DOE
john@example.com | 555-0123 | New York, NY
LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with a focus on backend systems.

TECHNICAL SKILLS
Languages: Python, Java, C++
Tools: Docker, Kubernetes, Git

PROFESSIONAL EXPERIENCE
SENIOR SOFTWARE ENGINEER | TECH CORP | NEW YORK, NY
2020 – Present
• Led migration of legacy monolith to microservices architecture.
• Improved system throughput by 50% through optimization.

SOFTWARE ENGINEER | STARTUP INC | SAN FRANCISCO, CA
2018 – 2020
• Developed RESTful APIs for mobile applications.
• Collaborated with cross-functional teams to deliver features.

EDUCATION
BS COMPUTER SCIENCE | UNIVERSITY OF TECHNOLOGY
Graduated: 2018
GPA: 3.8
"""

    cv_dict = {
        "contact_info": {"full_name": "John Doe"},
        "summary": {"text": "Experienced software engineer..."},
        "experience": []
    }

    # Test PDF
    print("Testing PDFExporter...")
    pdf_path = output_dir / "test_cv.pdf"
    PDFExporter().export(cv_text, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    print(f"PDF created: {pdf_path} ({pdf_path.stat().st_size} bytes)")

    # Test DOCX
    print("Testing DOCXExporter...")
    docx_path = output_dir / "test_cv.docx"
    DOCXExporter().export(cv_text, docx_path)
    assert docx_path.exists()
    assert docx_path.stat().st_size > 0
    print(f"DOCX created: {docx_path} ({docx_path.stat().st_size} bytes)")

    # Test HTML
    print("Testing HTMLExporter...")
    html_path = output_dir / "test_cv.html"
    HTMLExporter().export(cv_text, html_path)
    assert html_path.exists()
    assert html_path.stat().st_size > 0
    print(f"HTML created: {html_path} ({html_path.stat().st_size} bytes)")

    # Test JSON
    print("Testing JSONExporter...")
    json_path = output_dir / "test_cv.json"
    JSONExporter().export(cv_dict, json_path)
    assert json_path.exists()
    assert json_path.stat().st_size > 0
    print(f"JSON created: {json_path} ({json_path.stat().st_size} bytes)")

    print("\nAll smoke tests passed!")

if __name__ == "__main__":
    test_exporters()
