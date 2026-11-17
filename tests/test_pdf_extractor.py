
from unittest.mock import Mock

from PIL import Image, ImageDraw, ImageFont
import pytest

from app.services import pdf_extractor
from app.services.pdf_extractor import (
    PDFExtractionError,
    extract_pdf_text,
    extract_pdf_text_with_method,
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


def test_empty_page_text_is_handled(tmp_path, monkeypatch):
    """Handle a PDF page with no extractable native text."""
    pdf_file = tmp_path / "empty.pdf"
    pdf_file.write_bytes(b"%PDF-test")

    page = Mock()
    page.extract_text.return_value = None

    fake_reader = Mock()
    fake_reader.pages = [page]

    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda path: fake_reader,
    )

    result = extract_pdf_text(pdf_file)

    assert result == ""


def test_scanned_pdf_uses_ocr(tmp_path, monkeypatch):
    """A scanned PDF should be rendered and processed with OCR."""
    pdf_file = tmp_path / "scanned.pdf"

    # Create an image containing known text.
    image = Image.new("RGB", (1200, 400), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except OSError:
        font = ImageFont.load_default(size=48)

    draw.text(
        (50, 100),
        "OCR TEST 123",
        fill="black",
        font=font,
    )

    # Save the image as an image-only PDF.
    try:
        image.save(
            pdf_file,
            format="PDF",
            resolution=150.0,
        )
    finally:
        image.close()

    # Simulate a page without a native text layer.
    page = Mock()
    page.extract_text.return_value = None

    fake_reader = Mock()
    fake_reader.pages = [page]

    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda path: fake_reader,
    )

    # Mock OCR so the test focuses on PDF rendering and routing.
    monkeypatch.setattr(
        pdf_extractor,
        "extract_image_text",
        Mock(return_value="Recognized scanned text"),
    )

    extracted_text, method = extract_pdf_text_with_method(
        pdf_file,
        languages="eng",
    )

    assert extracted_text == "Recognized scanned text"
    assert method == "OCR"

