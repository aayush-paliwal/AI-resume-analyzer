from docx import Document
from io import BytesIO
from pdfminer.high_level import extract_text



def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with BytesIO(file_bytes) as buffer:
            text = extract_text(buffer)
        return text.strip()
    except Exception as e:
        print(f"Failed to extract text from PDF: {str(e)}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        file_stream = BytesIO(file_bytes)
        doc = Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Failed to extract text from DOCX: {str(e)}")
        return ""


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise ValueError("Text file must be UTF-8 encoded.")


def extract_text_from_resume(filename: str, file_content: bytes) -> str:
    if not filename:
        raise ValueError("Filename cannot be empty")

    file_ext = filename.split('.')[-1].lower()

    if file_ext == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_ext == "docx":
        return extract_text_from_docx(file_content)
    elif file_ext == "txt":
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file type: .{file_ext}. Please upload PDF, DOCX, or TXT.")
