
from unittest.mock import patch

import pytest
from PIL import Image

from app.services.ocr_extractor import (
    OCRExtractionError,
    extract_image_text,
)


def test_extract_text_from_image(tmp_path):
    """Test OCR extraction and text cleaning using mocked OCR."""
    image_file = tmp_path / "sample.png"
    Image.new("RGB", (200, 100), "white").save(image_file)

    with patch(
        "app.services.ocr_extractor.pytesseract.image_to_string",
        return_value="  Hello World  ",
    ) as mock_ocr:
        result = extract_image_text(image_file)

    assert result == "Hello World"
    assert mock_ocr.call_count >= 1

    first_call = mock_ocr.call_args_list[0]
    assert first_call.kwargs["lang"] == "fra+eng"
    assert first_call.kwargs["config"].startswith("--oem 1 --psm ")


def test_missing_image_raises_error(tmp_path):
    """A missing image should raise OCRExtractionError."""
    missing_file = tmp_path / "missing.png"

    with pytest.raises(
        OCRExtractionError,
        match="not found",
    ):
        extract_image_text(missing_file)


def test_invalid_image_raises_error(tmp_path):
    """An invalid image should raise OCRExtractionError."""
    image_file = tmp_path / "invalid.png"
    image_file.write_bytes(b"not a real image")

    with pytest.raises(
        OCRExtractionError,
        match="Could not open image",
    ):
        extract_image_text(image_file)


