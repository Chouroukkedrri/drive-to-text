# Third-Party Licenses

This document lists the main third-party dependencies used by the Drive-to-Text project and their associated licenses.

Dependency versions are based on the project's Python environment. License information should be checked against the official package metadata and the versions actually distributed.

## 1. Main Python Dependencies

| Dependency | Installed Version | License |
|---|---|---|
| FastAPI | 0.162.7 | MIT |
| Uvicorn | 0.54.0 | BSD-3-Clause |
| Starlette | 1.10.0 | BSD-3-Clause |
| Jinja2 | 3.1.6 | BSD-3-Clause |
| pypdf | 7.1.0 | BSD-3-Clause |
| pypdfium2 | 5.15.2 | Apache-2.0 OR BSD-3-Clause |
| Pillow | 13.0.0 | HPND / Pillow license |
| pytesseract | 0.3.13 | Apache-2.0 |
| google-api-python-client | 2.202.0 | Apache-2.0 |
| google-auth | 2.62.2 | Apache-2.0 |
| python-dotenv | 1.2.4 | BSD-3-Clause |
| pytest | 9.2.0 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| python-multipart | 0.0.33 | Apache-2.0 |

## 2. OCR Engine

Drive-to-Text uses Tesseract OCR through the Python package `pytesseract`.

- **Tesseract OCR:** The OCR engine is installed separately from Python dependencies.
- **License:** Apache License 2.0.
- **Language data:** Tesseract language files, including French, English and Arabic, may have their own licensing and attribution requirements. Check the language-data distribution used on the target machine.

The `pytesseract` Python package is a wrapper; it is not the Tesseract OCR engine itself.

## 3. PDF Processing

The project uses `pypdf` for PDF text extraction and `pypdfium2` for PDF rendering where needed for OCR.

`pypdfium2` offers Apache-2.0 and BSD-3-Clause licensing options. Its bundled PDFium components and other distributed components may have additional license or notice requirements.

The project does not intentionally rely on PyMuPDF as an active dependency. If PyMuPDF is reintroduced, its AGPL-3.0 or commercial licensing terms must be reviewed before distribution.

## 4. License Compatibility and Commercial Use

The main dependencies listed above use permissive licenses. These generally permit commercial use, modification and redistribution, subject to their respective conditions.

In particular:

- **MIT:** Include the copyright and permission notices in copies or substantial portions of the software.
- **BSD-3-Clause:** Preserve the applicable copyright, conditions and disclaimer; do not use contributors' names to endorse derived products without permission.
- **Apache-2.0:** Preserve the required notices and comply with applicable license and patent provisions.
- **Pillow and pypdfium2:** Verify the license text and notices associated with the exact versions and distribution used.

The project's own MIT license does not replace or override the licenses of third-party components.

## 5. Official License References

- FastAPI: https://github.com/fastapi/fastapi
- Uvicorn: https://github.com/encode/uvicorn
- Starlette: https://github.com/encode/starlette
- Jinja2: https://github.com/pallets/jinja
- pypdf: https://github.com/py-pdf/pypdf
- pypdfium2: https://github.com/pypdfium2-team/pypdfium2
- Pillow: https://github.com/python-pillow/Pillow
- pytesseract: https://github.com/madmaze/pytesseract
- Google API Python Client: https://github.com/googleapis/google-api-python-client
- google-auth: https://github.com/googleapis/google-auth-library-python
- python-dotenv: https://github.com/theskumar/python-dotenv
- pytest: https://github.com/pytest-dev/pytest
- HTTPX: https://github.com/encode/httpx
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract

## 6. Scope and Verification

This inventory focuses on the principal dependencies declared in `requirements.txt` and the separately installed OCR engine.

It is not an exhaustive inventory of all transitive dependencies. Before publishing or distributing the project, verify the license metadata and required notices for the exact packages and bundled components used.

For reproducible installations, dependency versions should be pinned in `requirements.txt` and tested in a clean environment.
