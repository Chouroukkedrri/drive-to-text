
from unittest.mock import Mock

import pytest

from app.services import pdf_extractor
from app.services.pdf_extractor import (
    PDFExtractionError,
    extract_pdf_text,
)


def test_extract_text_from_multiple_pages(tmp_path, monkeypatch):
    """Extract text from multiple native PDF pages."""
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-test")

    first_page = Mock()
    first_page.extract_text.return_value = "Hello from page one"

    second_page = Mock()
    second_page.extract_text.return_value = "Hello from page two"

    fake_reader = Mock()
    fake_reader.pages = [first_page, second_page]

    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda path: fake_reader,
    )

    result = extract_pdf_text(pdf_file)

    assert result == (
        "Hello from page one\n\n"
        "Hello from page two"
    )


def test_missing_pdf_raises_error(tmp_path):
    """A missing PDF should raise PDFExtractionError."""
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(
        PDFExtractionError,
        match="not found",
    ):
        extract_pdf_text(missing_file)


