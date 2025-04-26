import io
import logging

import fitz  # PyMuPDF
import docx


from fastapi import UploadFile

from app.utils.aws_utils import download_resume_from_s3_key
from app.utils.utils import get_file_extension_from_s3_key

logger = logging.getLogger("app")


def extract_text_from_pdf(
    file: UploadFile | io.BytesIO,
    *,
    filename: str | None = None
) -> str:
    """Extracts text from a PDF.  Accepts either an UploadFile or a BytesIO."""
    name = filename or getattr(file, "filename", "bytes-resume.pdf")
    logger.info(f"📄 Extracting text from PDF file: {name}")
    try:
        # if it's an UploadFile, read from .file; otherwise assume it's BytesIO
        data = file.file.read() if hasattr(file, "file") else file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        pages = [page.get_text("text") for page in doc]
        return "\n".join(pages)
    except Exception as e:
        logger.error(f"❌ Failed to extract text from PDF: {e}", exc_info=True)
        raise

def extract_text_from_docx(
    file: UploadFile | io.BytesIO,
    *,
    filename: str | None = None
) -> str:
    """Extracts text from a DOCX.  Accepts either an UploadFile or a BytesIO."""
    name = filename or getattr(file, "filename", "bytes-resume.docx")
    logger.info(f"📄 Extracting text from DOCX file: {name}")
    try:
        # wrap BytesIO in a file‐like object accepted by python‐docx
        stream = file.file if hasattr(file, "file") else file
        doc = docx.Document(stream)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        logger.error(f"❌ Failed to extract text from DOCX: {e}", exc_info=True)
        raise


def extract_resume_text(file: UploadFile):
    """Detects file type and extracts text accordingly."""
    logger.info(
        f"🔍 Detecting format and extracting resume text for file: {file.filename}"
    )
    try:
        if file.filename.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            return extract_text_from_docx(file)
        elif file.filename.endswith(".txt"):
            logger.info("📃 Extracting text from plain text file")
            return file.file.read().decode("utf-8")
        else:
            raise ValueError(
                "Unsupported file format. Only PDF, DOCX, and TXT are allowed."
            )
    except Exception as e:
        logger.error(f"❌ Failed to extract resume text: {str(e)}", exc_info=True)
        raise Exception(f"Error extracting resume text: {str(e)}")


def extract_resume_text_from_bytes(file_bytes: io.BytesIO, extension: str) -> str:
    """
    Given a BytesIO and its extension, routes to the appropriate extractor.
    """
    logger.info(f"🔍 Extracting resume text from bytes (.{extension})")
    try:
        if extension == "pdf":
            return extract_text_from_pdf(file_bytes, filename=f"resume.{extension}")
        elif extension == "docx":
            return extract_text_from_docx(file_bytes, filename=f"resume.{extension}")
        elif extension in ("txt", "text"):
            return file_bytes.read().decode("utf-8")
        else:
            raise ValueError(f"Unsupported extension: .{extension}")
    except Exception:
        logger.error("❌ Failed to extract text from bytes", exc_info=True)
        raise


def get_resume_text_from_s3_key(s3_key: str):
    """
    Downloads a resume from S3, extracts its file extension, and retrieves text.

    :param s3_key: The S3 key of the resume.
    :return: Extracted text content of the resume.
    """
    logger.info(f"📥 Fetching and extracting resume text from S3 key: {s3_key}")
    try:
        resume_file = download_resume_from_s3_key(s3_key)
        resume_file_ext = get_file_extension_from_s3_key(s3_key)
        resume_text = extract_resume_text_from_bytes(resume_file, resume_file_ext)
        logger.info("✅ Successfully extracted resume text from S3")
        return resume_text
    except Exception as e:
        logger.error(f"❌ Error processing resume from S3: {str(e)}", exc_info=True)
        raise Exception(f"Error processing resume from S3: {str(e)}")
