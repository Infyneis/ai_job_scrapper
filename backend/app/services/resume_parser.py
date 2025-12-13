from pathlib import Path
import PyPDF2
from docx import Document
import io


def extract_text_from_pdf(file_content: bytes) -> str:
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return text.strip()


def extract_text_from_docx(file_content: bytes) -> str:
    text = ""
    try:
        doc = Document(io.BytesIO(file_content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
    return text.strip()


def extract_resume_text(filename: str, file_content: bytes) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_content)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_content)
    elif ext == ".txt":
        return file_content.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file format: {ext}")
