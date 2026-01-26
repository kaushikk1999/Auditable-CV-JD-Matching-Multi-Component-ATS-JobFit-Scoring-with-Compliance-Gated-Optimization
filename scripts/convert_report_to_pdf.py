
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

# Config
INPUT_FILE = Path("/Users/kaushikkarmakar/.gemini/antigravity/brain/b880f5c0-074c-4fe3-92d0-1479565e3306/technical_implementation_report.md")
OUTPUT_FILE = Path("/Users/kaushikkarmakar/.gemini/antigravity/brain/b880f5c0-074c-4fe3-92d0-1479565e3306/Technical_Implementation_Report.pdf")

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, 'Technical Implementation Report - ATS CV Optimization', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def clean_text(text):
    """Remove markdown syntax and sanitize unicode for Latin-1"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
    
    # Replacements for common unicode chars
    replacements = {
        '\u201c': '"', '\u201d': '"',  # Smart quotes
        '\u2018': "'", '\u2019': "'",  # Smart single quotes
        '\u2013': '-', '\u2014': '-',  # Dashes
        '\u2026': '...',               # Ellipsis
        '\u00a0': ' ',                 # Non-breaking space
        '✓': '[X]', '✗': '[ ]',        # Checkmarks
        '═': '=', '─': '-', '━': '-',  # Box drawing chars
        '│': '|', '┃': '|',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    # Shorten long separators to avoid layout issues (e.g. 50 dashes -> 20 dashes)
    text = re.sub(r'-{20,}', '-'*20, text)
    text = re.sub(r'={20,}', '='*20, text)
    
    # Final safety mechanism: encode to latin-1, replacing errors
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(input_path, output_path):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    code_content = []
    in_table = False
    
    for line in lines:
        line_strip = line.strip()

        # Code Blocks
        if line_strip.startswith("```"):
            if in_code_block:
                # End of block
                pdf.set_font("courier", size=9)
                pdf.set_fill_color(240, 240, 240)
                # Print code block
                pdf.set_x(pdf.l_margin)  # Ensure X is valid
                for code_line in code_content:
                    # Sanitize code line too
                    safe_line = clean_text(code_line)
                    try:
                        pdf.multi_cell(pdf.epw, 5, safe_line, fill=True, border=0, align='L')
                    except Exception:
                        pdf.multi_cell(pdf.epw, 5, safe_line[:80] + "...", fill=True, border=0, align='L')
                pdf.ln(2)
                in_code_block = False
                code_content = []
                # Reset font
                pdf.set_font("helvetica", size=10)
            else:
                # Start of block
                in_code_block = True
            continue
        
        if in_code_block:
            code_content.append(line.rstrip())
            continue

        # Headers
        if line.startswith("# "):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 20)
            pdf.ln(5)
            pdf.multi_cell(0, 10, clean_text(line[2:].strip()), align='L')
            pdf.ln(2)
            pdf.set_font("helvetica", size=10)
            continue
        
        elif line.startswith("## "):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 16)
            pdf.ln(8)
            pdf.multi_cell(0, 10, clean_text(line[3:].strip()), align='L')
            pdf.ln(1)
            pdf.set_font("helvetica", size=10)
            continue

        elif line.startswith("### "):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 12)
            pdf.ln(5)
            pdf.multi_cell(0, 8, clean_text(line[4:].strip()), align='L')
            pdf.set_font("helvetica", size=10)
            continue
        
        elif line.startswith("#### "):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 11)
            pdf.ln(3)
            pdf.multi_cell(0, 6, clean_text(line[5:].strip()), align='L')
            pdf.set_font("helvetica", size=10)
            continue

        # Tables (Simple parser)
        if "|" in line and "-|-" not in line:
            # Table row
            if not in_table:
                # Potential start of table or just a line with pipe
                # Check next line for header separator
                pass 
            
            row_data = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if row_data:
                if not in_table:
                     # Check if it's a header (heuristic: line below is separator)
                     # For simplicity in this script, we'll just check if we are in a table flow
                     # But fpdf table context manager is best.
                     # We will collect rows and render later? No, complex.
                     # Let's use flexible table rendering
                     # Simplified: If line matches |...|...|, treat as table row
                     pass
        
        # Detect table separator line
        if "|-" in line:
            in_table = True
            continue 
            
        # If we see a table row
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
                
            cols = [c.strip() for c in line.strip().strip('|').split('|')]
            
            pdf.set_font("helvetica", size=9)
            col_width = pdf.epw / max(len(cols), 1)
            
            # Save current Y
            y_before = pdf.get_y()
            max_height = 0
            
            # Calculate max height first
            for col in cols:
                # Dry run for height
                lines_res = pdf.multi_cell(col_width, 5, clean_text(col), dry_run=True, output="LINES")
                h = len(lines_res) * 5
                if h > max_height:
                    max_height = h
            
            # Render
            for col in cols:
                pdf.set_xy(pdf.get_x(), y_before)
                pdf.multi_cell(col_width, 5, clean_text(col), border=1)
                # Move x
                pdf.set_xy(pdf.get_x() + col_width, y_before)
                
            # Move to next line
            pdf.set_xy(pdf.l_margin, y_before + max_height)
            pdf.set_font("helvetica", size=10)
            continue
        else:
            if in_table:
                in_table = False
                pdf.ln(2)

        # Bullet lists
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            pdf.set_x(15) 
            try:
                pdf.multi_cell(0, 5, "- " + clean_text(line.strip()[2:]))
            except Exception:
                pass
            continue
        
        # Generic text
        if line.strip():
            # Reset X to margin to be safe
            pdf.set_x(pdf.l_margin)
            
            # Check for bold starts
            is_bold = line.strip().startswith("**") and "**" in line.strip()[2:]
            
            try:
                if is_bold:
                    parts = line.strip().split("**")
                    if len(parts) >= 3:
                         pdf.set_font("helvetica", 'B', 10)
                         pdf.write(5, parts[1] + ": ")
                         pdf.set_font("helvetica", size=10)
                         pdf.write(5, clean_text("".join(parts[2:])))
                         pdf.ln()
                    else:
                        pdf.multi_cell(0, 5, clean_text(line))
                else:
                    pdf.multi_cell(0, 5, clean_text(line))
            except Exception as e:
                print(f"Skipping problematic line: {line.strip()[:20]}... Error: {e}")
            
    print(f"Generating PDF to: {output_path}")
    pdf.output(output_path)

if __name__ == "__main__":
    create_pdf(INPUT_FILE, OUTPUT_FILE)
