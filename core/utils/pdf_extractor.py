"""
PDF and text extraction utilities.
Handles PDF, DOCX, and plain text files.
"""

import io
import pdfplumber


def extract_text_from_pdf(file_obj):
    """
    Extract text from a PDF file object.
    Returns cleaned text string.
    """
    text = ""
    try:
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {str(e)}")
    return text.strip()


def extract_text_from_file(file_obj, filename=""):
    """
    Auto-detect file type and extract text.
    Supports PDF, DOCX, and plain TXT.
    """
    filename = filename.lower()

    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    elif filename.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file_obj)
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX text: {str(e)}")
    else:
        # Try as plain text
        try:
            content = file_obj.read()
            return content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")


def extract_text_from_string(text_content):
    """Return clean text if already a string."""
    return text_content.strip() if text_content else ""
