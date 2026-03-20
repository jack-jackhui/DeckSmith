"""Document processing module for PDF and Word document handling."""

import logging
from typing import List

import docx
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import CHUNK_OVERLAP, CHUNK_SIZE, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from vector_db import add_to_vector_db

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)


def check_file_size(file) -> None:
    """Check if file size is within allowed limits.

    Args:
        file: The uploaded file object.

    Raises:
        ValueError: If file exceeds the maximum allowed size.
    """
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File '{file.name}' exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB"
        )


def process_pdf(file) -> str:
    """Extract text content from a PDF file.

    Args:
        file: The PDF file object.

    Returns:
        The extracted text content.
    """
    check_file_size(file)

    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    logger.info("Processed PDF with %d pages", len(doc))
    return text


def process_docx(file) -> str:
    """Extract text content from a Word document.

    Args:
        file: The Word document file object.

    Returns:
        The extracted text content.
    """
    check_file_size(file)

    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"

    logger.info("Processed Word document with %d paragraphs", len(doc.paragraphs))
    return text


def chunk_text(text: str) -> List[str]:
    """Split text into chunks for vector storage.

    Args:
        text: The text to split.

    Returns:
        A list of text chunks.
    """
    if not text or not text.strip():
        return []

    chunks = text_splitter.split_text(text)
    logger.info("Split text into %d chunks", len(chunks))
    return chunks


def process_and_store_documents(uploaded_files: List) -> None:
    """Process uploaded documents and store them in the vector database.

    Args:
        uploaded_files: List of uploaded file objects.

    Raises:
        ValueError: If a file exceeds size limits or has unsupported format.
    """
    for file in uploaded_files:
        try:
            if file.type == "application/pdf":
                text = process_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = process_docx(file)
            else:
                logger.warning("Unsupported file type: %s", file.type)
                continue

            chunks = chunk_text(text)
            for chunk in chunks:
                add_to_vector_db(chunk, auto_save=False)

            from vector_db import save_index
            save_index()

            logger.info("Successfully processed and stored file: %s", file.name)

        except ValueError as e:
            logger.error("Validation error processing file %s: %s", file.name, e)
            raise
        except Exception as e:
            logger.error("Error processing file %s: %s", file.name, e)
            raise
