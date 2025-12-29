import io
from pathlib import Path
from docx import Document
import pdfplumber

class CVParser:
    """Parses CV from .txt, .docx, or .pdf into clean text."""
    
    @staticmethod
    def parse_txt(file_content: bytes) -> str:
        """Parse plain text file."""
        return file_content.decode('utf-8', errors='ignore').strip()
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """Parse .docx file and extract text."""
        doc = Document(io.BytesIO(file_content))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Parse .pdf file and extract text."""
        text_chunks = []
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_chunks.append(text.strip())
        return "\n".join(text_chunks)
    
    @classmethod
    def parse(cls, file_content: bytes, file_extension: str) -> str:
        """
        Unified parser interface.
        
        Args:
            file_content: Raw file bytes
            file_extension: e.g., '.pdf', '.docx', '.txt'
        
        Returns:
            Clean text string
        """
        ext = file_extension.lower()
        
        if ext == ".txt":
            return cls.parse_txt(file_content)
        elif ext == ".docx":
            return cls.parse_docx(file_content)
        elif ext == ".pdf":
            return cls.parse_pdf(file_content)
        else:
            raise ValueError(f"Unsupported file format: {ext}")


class JDParser:
    """Placeholder for JD text normalization (no AI here, just cleaning)."""
    
    @staticmethod
    def clean_text(jd_text: str) -> str:
        """Basic cleaning: strip extra whitespace, normalize line breaks."""
        lines = [line.strip() for line in jd_text.split('\n') if line.strip()]
        return "\n".join(lines)
