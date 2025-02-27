import fitz  # PyMuPDF
import docx


from app.utils.aws_utils import download_resume_from_s3, get_file_extension_from_s3_url

from fastapi import UploadFile

def extract_text_from_pdf(file: UploadFile):
    """Extracts text from a PDF while maintaining sections."""
    text = []
    doc = fitz.open(stream=file.file.read(), filetype="pdf")

    for page in doc:
        text.append(page.get_text("text"))  # Extracts text while keeping formatting

    return "\n".join(text)

def extract_text_from_docx(file: UploadFile):
    """Extracts text from a DOCX file while maintaining structure."""
    text = []
    doc = docx.Document(file.file)

    for para in doc.paragraphs:
        text.append(para.text)  # Maintains paragraph order

    return "\n".join(text)

def extract_resume_text(file: UploadFile):
    """Detects file type and extracts text accordingly."""
    try:
        if file.filename.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            return extract_text_from_docx(file)
        elif file.filename.endswith(".txt"):
            return file.file.read().decode("utf-8")
        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT are allowed.")
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

#todo: if not used delete it
def get_resume_text_from_s3(s3_url: str):
    """
    Downloads a resume from S3, extracts its file extension, and retrieves text.

    :param s3_url: The S3 URL of the resume.
    :return: Extracted text content of the resume.
    """
    try:
        # ✅ Step 1: Download resume file from S3
        resume_file = download_resume_from_s3(s3_url)

        # ✅ Step 2: Get file extension
        resume_file_ext = get_file_extension_from_s3_url(s3_url)

        # ✅ Step 3: Extract text from the resume
        resume_text = extract_resume_text(resume_file, resume_file_ext)

        return resume_text

    except Exception as e:
        raise Exception(f"Error processing resume from S3: {str(e)}")