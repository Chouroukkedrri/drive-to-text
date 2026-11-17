
from pathlib import Path
from tempfile import TemporaryDirectory

import pypdfium2 as pdfium
from pypdf import PdfReader

from app.services.ocr_extractor import extract_image_text


class PDFExtractionError(Exception):
    """Raised when text cannot be extracted from a PDF."""


def extract_pdf_text_with_method(
    file_path: str | Path,
    languages: str = "fra+eng",
) -> tuple[str, str]:
    """
    Extract text from a PDF and report the method used.

    Returns:
        A tuple containing:
        - extracted_text: the extracted document text
        - method: PDF parser, OCR, or PDF parser + OCR

    Raises:
        PDFExtractionError: If the PDF cannot be processed.
    """
    path = Path(file_path)

    if not path.is_file():
        raise PDFExtractionError(
            f"PDF file not found: {path.name}"
        )

    try:
        # 1. Extract text directly from the PDF.
        reader = PdfReader(str(path))

        page_texts = [
            (page.extract_text() or "").strip()
            for page in reader.pages
        ]

        # Identify pages without extractable text.
        pages_needing_ocr = [
            index
            for index, text in enumerate(page_texts)
            if not text
        ]

        # If every page has native text, no OCR is needed.
        if not pages_needing_ocr:
            extracted_text = "\n\n".join(page_texts).strip()
            return extracted_text, "PDF parser"

        # Count pages that already contain native text.
        native_text_pages = sum(
            bool(text) for text in page_texts
        )

        # 2. Open the PDF with PDFium for page rendering.
        try:
            document = pdfium.PdfDocument(str(path))
        except Exception:
            # Preserve the native extraction result if PDFium
            # cannot render this document.
            extracted_text = "\n\n".join(page_texts).strip()
            return extracted_text, "PDF parser"

        try:
            # Temporary images are removed automatically.
            with TemporaryDirectory(
                prefix="drive_to_text_"
            ) as temp_dir:
                temp_path = Path(temp_dir)

                # 3. Render and OCR each page without native text.
                for index in pages_needing_ocr:
                    if index >= len(document):
                        raise PDFExtractionError(
                            f"Could not access page {index + 1} "
                            f"of {path.name}."
                        )

                    image_path = (
                        temp_path / f"page_{index + 1}.png"
                    )

                    try:
                        # Open the page and render it as an image.
                        page = document[index]

                        try:
                            bitmap = page.render(scale=2)

                            try:
                                image = bitmap.to_pil()

                                try:
                                    image.save(
                                        str(image_path),
                                        format="PNG",
                                    )
                                finally:
                                    image.close()

                            finally:
                                bitmap.close()

                        finally:
                            page.close()

                        # Recognize text from the rendered page.
                        page_texts[index] = extract_image_text(
                            image_path,
                            languages=languages,
                        ).strip()

                    except PDFExtractionError:
                        raise

                    except Exception as exc:
                        raise PDFExtractionError(
                            f"Could not process page "
                            f"{index + 1} of {path.name}: {exc}"
                        ) from exc

        finally:
            # Release the PDFium document resources.
            document.close()

        # 4. Combine text from native and scanned pages.
        extracted_text = "\n\n".join(page_texts).strip()

        if native_text_pages > 0:
            method = "PDF parser + OCR"
        else:
            method = "OCR"

        return extracted_text, method

    except PDFExtractionError:
        raise

    except Exception as exc:
        raise PDFExtractionError(
            f"Could not extract text from {path.name}: {exc}"
        ) from exc


def extract_pdf_text(
    file_path: str | Path,
    languages: str = "fra+eng",
) -> str:
    """
    Extract text from a PDF and return only the text.

    This wrapper preserves compatibility with callers that
    expect extract_pdf_text() to return a string.
    """
    extracted_text, _method = extract_pdf_text_with_method(
        file_path,
        languages=languages,
    )

    return extracted_text
