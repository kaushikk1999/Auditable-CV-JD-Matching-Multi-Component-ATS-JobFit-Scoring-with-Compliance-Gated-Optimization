
import os
import sys
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.units import inch

# Configuration
OUTPUT_FILENAME = "Project_Documentation.pdf"
MAX_FILE_SIZE_BYTES = 1024 * 50  # 50KB limit for full content inclusion to avoid massive PDF
INCLUDED_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.yaml', '.yml', 
    '.tex', '.mmd', '.sh', '.gitignore', '.rst'
}
EXCLUDED_DIRS = {
    '.git', '__pycache__', 'venv', '.venv', '.idea', '.vscode', 
    'node_modules', '.DS_Store', 'project_documentation_env'
}

def get_project_tree(root_dir):
    tree_str = ""
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            if f == ".DS_Store": continue
            tree_str += f"{subindent}{f}\n"
    return tree_str

def generate_pdf(root_dir):
    doc = SimpleDocTemplate(
        OUTPUT_FILENAME,
        pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = styles['Title']
    heading_style = styles['Heading1']
    subheading_style = styles['Heading2']
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=8,
        leading=10,
        fontName='Courier',
        backColor=colors.whitesmoke,
        borderPadding=5
    )
    
    # 1. Title Page
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("Project Documentation", title_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Root: {root_dir}", styles['Normal']))
    story.append(PageBreak())
    
    # 2. Project Structure
    story.append(Paragraph("1. Project Structure", heading_style))
    tree_view = get_project_tree(root_dir)
    story.append(Preformatted(tree_view, code_style))
    story.append(PageBreak())
    
    # 3. File Contents
    story.append(Paragraph("2. File Contents", heading_style))
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in sorted(files):
            if file == ".DS_Store": continue
            
            ext = os.path.splitext(file)[1].lower()
            if ext not in INCLUDED_EXTENSIONS and file not in ['Dockerfile', 'Procfile']:
                continue
                
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, root_dir)
            
            # Skip if file is too large
            try:
                if os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES:
                    story.append(Paragraph(f"File: {relpath} (Skipped - Too Large)", subheading_style))
                    story.append(Spacer(1, 10))
                    continue
            except OSError:
                continue

            # Read content
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {str(e)}"
            
            # Add to PDF
            story.append(Paragraph(f"File: {relpath}", subheading_style))
            
            # Handle potential XML/HTML tag conflicts in reportlab Paragraphs by escaping
            import html
            content_escaped = html.escape(content)
            
            # Split long content to avoid flowable errors
            if len(content_escaped) > 50000:
                content_escaped = content_escaped[:50000] + "\n... [Truncated for PDF limit] ..."

            story.append(Preformatted(content_escaped, code_style))
            story.append(Spacer(1, 20))
            
    # Build
    try:
        doc.build(story)
        print(f"SUCCESS: Generated {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"ERROR: Failed to generate PDF: {e}")

if __name__ == "__main__":
    generate_pdf(os.getcwd())
