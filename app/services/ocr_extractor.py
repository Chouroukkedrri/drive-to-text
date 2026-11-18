
from pathlib import Path
import re
import shutil

import pytesseract
from PIL import (
    Image,
    ImageEnhance,
    ImageOps,
    UnidentifiedImageError,
)


# Use Tesseract from PATH when available (Windows and Linux).
tesseract_executable = shutil.which("tesseract")

if tesseract_executable:
    pytesseract.pytesseract.tesseract_cmd = tesseract_executable
else:
    # Fallback for the standard Windows installation path.
    windows_tesseract = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_tesseract.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(
            windows_tesseract
        )

class OCRExtractionError(Exception):
    """Raised when text cannot be extracted from an image."""


def _prepare_images(image: Image.Image) -> list[Image.Image]:
    """Create image variants to improve OCR on difficult text."""

    # Normalize orientation and convert to grayscale.
    original = ImageOps.exif_transpose(image).convert("RGB")
    grayscale = ImageOps.grayscale(original)

    # Enlarge small images to improve character recognition.
    width, height = grayscale.size
    scale = max(1, min(4, 1800 // max(width, 1)))

    if scale > 1:
        grayscale = grayscale.resize(
            (width * scale, height * scale),
            Image.Resampling.LANCZOS,
        )

    # Improve contrast and create a black-and-white variant.
    contrast = ImageEnhance.Contrast(
        ImageOps.autocontrast(grayscale)
    ).enhance(1.8)

    threshold = contrast.point(
        lambda pixel: 255 if pixel > 160 else 0
    )

    return [original, grayscale, contrast, threshold]


def extract_image_text(
    file_path: str | Path,
    languages: str = "fra+eng",
) -> str:
    """Extract text using several OCR layouts and image variants."""

    path = Path(file_path)

    if not path.is_file():
        raise OCRExtractionError(
            f"Image file not found: {path.name}"
        )

    try:
        with Image.open(path) as source:
            variants = _prepare_images(source)

            # Try different layouts: block, sparse text, and
            # sparse text with orientation/script detection.
            page_modes = (6, 11, 12)
            best_text = ""

            for image in variants:
                for page_mode in page_modes:
                    text = pytesseract.image_to_string(
                        image,
                        lang=languages,
                        config=f"--oem 1 --psm {page_mode}",
                    ).strip()

                    if len(text) > len(best_text):
                        best_text = text

                    # Stop when a useful result is found.
                    if len(best_text) >= 3:
                        break

                if len(best_text) >= 3:
                    break

        # Remove a known artifact from some English OCR results.
        best_text = re.sub(
            r"(?m)^[ \t]*:[ \t]+(?=[A-Za-z])",
            "",
            best_text,
        )

        return best_text.strip()

    except (UnidentifiedImageError, OSError) as exc:
        raise OCRExtractionError(
            f"Could not open image {path.name}: {exc}"
        ) from exc

    except pytesseract.TesseractNotFoundError as exc:
        raise OCRExtractionError(
            "Tesseract was not found. Check its installation path."
        ) from exc

    except pytesseract.TesseractError as exc:
        raise OCRExtractionError(
            f"OCR failed for {path.name}: {exc}"
        ) from exc

