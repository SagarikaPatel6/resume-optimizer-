import pdfplumber
import docx

def parse_pdf(file) -> str:
    """Extract text from PDF."""
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def parse_docx(file) -> str:
    """Extract text from DOCX."""
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)
