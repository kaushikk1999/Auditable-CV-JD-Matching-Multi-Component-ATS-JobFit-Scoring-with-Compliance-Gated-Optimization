from fpdf import FPDF

def test_pdf_detailed():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    
    cv_text = """JOHN DOE
john@example.com | 555-0123 | New York, NY
LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with a focus on backend systems.
"""
    lines = cv_text.split('\n')
    
    for i, line in enumerate(lines):
        print(f"Processing line {i}: '{line}'")
        if not line.strip():
            pdf.ln(5)
            continue
        
        if line.isupper() and len(line) < 50:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 6, txt=line, ln=True)
            pdf.set_font("Arial", size=11)
        else:
            print(f"Before multi_cell: x={pdf.get_x()}, epw={pdf.epw}")
            pdf.multi_cell(0, 5, txt=line)
            
    print("Success")

if __name__ == "__main__":
    test_pdf_detailed()
