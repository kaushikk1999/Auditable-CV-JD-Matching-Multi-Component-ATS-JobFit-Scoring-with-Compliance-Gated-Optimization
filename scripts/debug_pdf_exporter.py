from fpdf import FPDF

def test_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    
    text = "Hello World"
    pdf.multi_cell(0, 5, txt=text)
    print("Success")

if __name__ == "__main__":
    test_pdf()
