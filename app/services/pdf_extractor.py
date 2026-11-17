
from pathlib import Path

from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Raised when text cannot be extracted from a PDF."""


def extract_pdf_text(file_path: str | Path) -> str:
    """
    Extract native text from a PDF file.

    Raises:
        PDFExtractionError: If the file is missing or cannot be read.
    """
    path = Path(file_path)

    if not path.is_file():
        raise PDFExtractionError(
            f"PDF file not found: {path.name}"
        )

    try:
        reader = PdfReader(str(path))
        page_texts = [
            page.extract_text()
            for page in reader.pages
        ]
        return "\n\n".join(
            text for text in page_texts if text
        ).strip()

    except Exception as exc:
        raise PDFExtractionError(
            f"Could not extract text from {path.name}: {exc}"
        ) from exc
