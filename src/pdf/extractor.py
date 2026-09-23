import re
from dataclasses import dataclass
from typing import List

import fitz


@dataclass
class PDFExtractionResult:
    """
    Stores the result of PDF text extraction.
    """

    success: bool
    text: str
    page_count: int
    character_count: int
    word_count: int
    message: str


def validate_pdf_file(file_bytes: bytes) -> tuple[bool, str]:
    """
    Validate that the uploaded file appears to be a PDF.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded file.

    Returns
    -------
    tuple[bool, str]
        Validation status and message.
    """

    if not file_bytes:
        return False, "The uploaded file is empty."

    # Standard PDF files normally begin with %PDF.
    if not file_bytes.startswith(b"%PDF"):
        return False, "The uploaded file does not appear to be a valid PDF."

    return True, "PDF file validation successful."


def normalize_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving useful line structure.

    Parameters
    ----------
    text:
        Raw text extracted from the PDF.

    Returns
    -------
    str
        Normalized text.
    """

    if not text:
        return ""

    # Normalize different newline formats.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces and tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces immediately before a newline.
    text = re.sub(r" +\n", "\n", text)

    # Reduce excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> PDFExtractionResult:
    """
    Extract text from all pages of a PDF using PyMuPDF.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded PDF.

    Returns
    -------
    PDFExtractionResult
        Structured extraction result.
    """

    is_valid, validation_message = validate_pdf_file(file_bytes)

    if not is_valid:
        return PDFExtractionResult(
            success=False,
            text="",
            page_count=0,
            character_count=0,
            word_count=0,
            message=validation_message,
        )

    document = None

    try:
        document = fitz.open(
            stream=file_bytes,
            filetype="pdf",
        )

        # Check for password protection.
        if document.needs_pass:
            return PDFExtractionResult(
                success=False,
                text="",
                page_count=document.page_count,
                character_count=0,
                word_count=0,
                message=(
                    "This PDF is password protected. "
                    "Please upload an unlocked PDF."
                ),
            )

        page_count = document.page_count

        if page_count == 0:
            return PDFExtractionResult(
                success=False,
                text="",
                page_count=0,
                character_count=0,
                word_count=0,
                message="The PDF contains no pages.",
            )

        extracted_pages: List[str] = []

        for page_number in range(page_count):
            page = document.load_page(page_number)

            page_text = page.get_text(
                "text",
                sort=True,
            )

            page_text = normalize_text(page_text)

            if page_text:
                extracted_pages.append(
                    f"--- Page {page_number + 1} ---\n{page_text}"
                )
            else:
                extracted_pages.append(
                    f"--- Page {page_number + 1} ---\n[No selectable text found]"
                )

        combined_text = "\n\n".join(extracted_pages)
        normalized_text = normalize_text(combined_text)

        # Remove page markers temporarily when calculating content.
        content_only = re.sub(
            r"--- Page \d+ ---",
            "",
            normalized_text,
        ).strip()

        character_count = len(content_only)
        word_count = len(
            re.findall(r"\b[\w+#.-]+\b", content_only)
        )

        if character_count == 0:
            return PDFExtractionResult(
                success=False,
                text=normalized_text,
                page_count=page_count,
                character_count=0,
                word_count=0,
                message=(
                    "The PDF was opened successfully, but no selectable "
                    "text was found. It may be a scanned/image-only PDF."
                ),
            )

        return PDFExtractionResult(
            success=True,
            text=normalized_text,
            page_count=page_count,
            character_count=character_count,
            word_count=word_count,
            message=(
                f"Successfully extracted text from {page_count} "
                f"page{'s' if page_count != 1 else ''}."
            ),
        )

    except fitz.FileDataError:
        return PDFExtractionResult(
            success=False,
            text="",
            page_count=0,
            character_count=0,
            word_count=0,
            message=(
                "PyMuPDF could not open this file as a valid PDF. "
                "The file may be corrupted or incorrectly formatted."
            ),
        )

    except Exception as exc:
        return PDFExtractionResult(
            success=False,
            text="",
            page_count=0,
            character_count=0,
            word_count=0,
            message=f"Unexpected PDF extraction error: {exc}",
        )

    finally:
        if document is not None:
            document.close()