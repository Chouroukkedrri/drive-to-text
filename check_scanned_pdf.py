
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont

from app.services.pdf_extractor import extract_pdf_text_with_method


def main():
    """Create an image-only PDF and test the real OCR pipeline."""

    with TemporaryDirectory(
        prefix="drive_to_text_check_"
    ) as temp_dir:
        pdf_path = Path(temp_dir) / "scanned_test.pdf"

        # Create an image containing text.
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

        draw.text(
            (50, 200),
            "Believe in yourself.",
            fill="black",
            font=font,
        )

        # Save the image as a PDF without a native text layer.
        try:
            image.save(
                pdf_path,
                format="PDF",
                resolution=150.0,
            )
        finally:
            image.close()

        print(f"Test PDF created: {pdf_path.name}")

        # Test the real PDFium -> image -> Tesseract pipeline.
        extracted_text, method = extract_pdf_text_with_method(
            pdf_path,
            languages="eng",
        )

        print(f"Extraction method: {method}")
        print("\n--- Extracted text ---")
        print(extracted_text)

        if "OCR TEST 123" not in extracted_text:
            raise SystemExit(
                "FAILED: expected text was not recognized."
            )

        if method != "OCR":
            raise SystemExit(
                f"FAILED: expected OCR, received {method}."
            )

        print("\nSUCCESS: Real OCR test passed!")


if __name__ == "__main__":
    main()
