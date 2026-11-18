# Drive-to-Text — Document Extraction POC

A lightweight, self-hostable web application that retrieves PDFs and images from a public Google Drive folder, extracts their text using the appropriate processing pipeline, and displays and exports the results as JSON.

**Technical assessment:** DI Xpertia — TA-2026-01
**Status:** Proof of concept with Docker support and automated tests.

## 1. Project Overview

Drive-to-Text demonstrates the initial stage of a document intelligence pipeline: retrieving documents from a shared folder, selecting files, extracting their text, and inspecting the results.

The application supports:

- Public Google Drive folder retrieval.
- PDF and image listing and selection.
- Native PDF text extraction.
- Automatic OCR fallback for scanned PDFs without usable text.
- OCR for PNG, JPG, and JPEG images.
- Per-document results and error handling.
- JSON export.
- Docker-based execution.
- Automated tests for the API, Drive integration, PDF extraction, and OCR.

The project is designed as a small proof of concept rather than a production document-processing platform.

## 2. Features

### Google Drive Integration

- Accepts a public Google Drive folder URL.
- Retrieves supported documents.
- Displays file metadata, including name, MIME type, and size when available.
- Handles invalid links, inaccessible folders, and retrieval errors.
- Validates selected file IDs before processing.

Only publicly accessible folders are in scope. Google OAuth authentication is not required.

### Document Selection and Batch Processing

- Select individual documents.
- Select all available documents.
- Display the number of selected files.
- Process multiple documents in one request.
- Handle errors independently so one failed document does not stop the remaining batch.

### PDF and Image Text Extraction

The application selects the extraction method according to the document type.

| Input          | Processing method                                        |
| -------------- | -------------------------------------------------------- |
| Text-based PDF | Native PDF text extraction                               |
| Scanned PDF    | Render pages and use OCR when usable text is unavailable |
| PNG, JPG, JPEG | OCR with Tesseract                                       |

The PDF pipeline uses `pypdf` for native text extraction and `pypdfium2` for PDF rendering. Image OCR uses `pytesseract`, Tesseract OCR, and Pillow.

OCR language data for English, French, and Arabic is installed in the Docker image. The application’s supported language choices must match the configuration exposed by the API and interface.

### Results and JSON Export

- Display extracted text for each document.
- Report the extraction method.
- Display successful, empty, or failed extraction results.
- Preserve document-specific error information.
- Export extraction results as JSON.

The exact status values and their presentation should remain consistent between the backend and frontend.

## 3. Architecture

The application uses a lightweight architecture with a FastAPI backend and an HTML/CSS/JavaScript frontend.

```text
Public Google Drive folder
          |
          v
    Drive service
          |
          v
   Supported files
          |
          v
  File selection / batch
          |
          v
   Extraction routing
       /       \
      v         v
 PDF parser   Image OCR
      |         ^
      |         |
      +---- Scanned PDF
          |
          v
 Per-file results and errors
          |
          v
   Web interface / JSON
```

### Main components

- `app/main.py`: FastAPI routes, request validation, extraction orchestration, and response generation.
- `app/services/drive_service.py`: public Google Drive folder listing and file downloads.
- `app/services/pdf_extractor.py`: native PDF text extraction and scanned-PDF OCR fallback.
- `app/services/ocr_extractor.py`: image preprocessing and OCR.
- `app/templates/index.html`: main web interface and frontend interactions.
- `app/static/css/style.css`: interface styling.
- `tests/`: automated tests for API endpoints, Drive integration, PDF processing, and OCR.
- `samples/`: sample documents and example extraction output.

This separation keeps external document retrieval, text extraction, API handling, and presentation independently testable.

## 4. Technology Stack

| Technology               | Purpose                                |
| ------------------------ | -------------------------------------- |
| Python                   | Main programming language              |
| FastAPI                  | Backend API                            |
| Uvicorn                  | ASGI application server                |
| Jinja2                   | HTML template rendering                |
| HTML, CSS, JavaScript    | Web interface                          |
| pypdf                    | Native PDF text extraction             |
| pypdfium2                | PDF rendering for scanned-document OCR |
| Tesseract OCR            | Open-source OCR engine                 |
| pytesseract              | Python interface to Tesseract          |
| Pillow                   | Image processing                       |
| Google API Python Client | Google Drive integration               |
| pytest                   | Automated testing                      |
| Docker                   | Reproducible application environment   |
| Docker Compose           | Application build and startup          |

### Design decisions

FastAPI provides a lightweight Python backend with request validation and testable endpoints. A server-rendered HTML interface avoids introducing a separate frontend build pipeline.

The extraction pipeline uses local, open-source PDF and OCR tools instead of requiring a paid document-processing API. Docker packages the Python dependencies and Tesseract language data into a reproducible environment.

## 5. Requirements

### Option A — Run locally on Windows

- Python 3.13 or a compatible Python version.
- Git.
- Tesseract OCR.
- The required Tesseract language data.
- Internet access for public Google Drive retrieval.

### Option B — Run with Docker

- Docker Desktop or another Docker Engine installation.
- Docker Compose.
- Internet access for the initial image build and public Google Drive retrieval.

**Docker is the recommended option** because it installs the system-level OCR dependencies and Python packages in a consistent environment.

## 6. Run with Docker Compose

Run these commands from the project root.

### Step 1 — Build the image

```powershell
docker compose build
```

### Step 2 — Start the application

```powershell
docker compose up
```

### Step 3 — Open the application

- Web interface: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

The application server listens on `0.0.0.0:8000` inside the container. Docker maps the container port to port `8000` on the host, so use `127.0.0.1:8000` in your browser.

### Step 4 — Stop the application

Press `Ctrl+C` in the terminal running `docker compose up`.

To stop and remove the Compose containers and network, run:

```powershell
docker compose down
```

To run the automated tests inside a temporary container:

```powershell
docker compose run --rm app python -m pytest -v
```

To view application logs:

```powershell
docker compose logs
```

## 7. Run Locally on Windows

### Step 1 — Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2 — Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3 — Configure Tesseract

Install Tesseract OCR and ensure that its executable is available through `PATH` or the standard Windows installation path.

Verify the installation:

```powershell
tesseract --version
tesseract --list-langs
```

### Step 4 — Configure environment variables

Create a local `.env` file from `.env.example` if the application requires configuration values.

For Google Drive API access, provide the required `GOOGLE_API_KEY` when applicable. Never commit secrets or private configuration to the repository.

### Step 5 — Start the application

```powershell
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## 8. How to Use the Application

1. Open the web interface.
2. Paste the URL of a publicly accessible Google Drive folder.
3. Retrieve the supported PDFs and images.
4. Select individual files or select all.
5. Choose an available OCR language if that control is provided by the current interface.
6. Start the extraction batch.
7. Inspect each document’s extracted text, method, status, and any error message.
8. Export the results as JSON.

Documents that require authentication are outside the scope of this proof of concept.

## 9. API Endpoints

### `GET /`

Displays the main web interface.

### `GET /health`

Checks application availability.

Expected response:

```json
{
  "status": "ok"
}
```

### `POST /api/files`

Retrieves supported files from a public Google Drive folder.

Example request:

```json
{
  "folder_url": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
}
```

### `POST /api/extract`

Processes selected documents and returns per-file extraction results.

Example request:

```json
{
  "folder_url": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID",
  "file_ids": ["FILE_ID_1", "FILE_ID_2"],
  "ocr_language": "fra+eng"
}
```

The accepted language values and request fields must match the implementation in `app/main.py`.

## 10. Example JSON Output

A successful result may have the following structure:

```json
{
  "file_id": "example_file_id",
  "file_name": "document.pdf",
  "mime_type": "application/pdf",
  "method": "PDF parser",
  "status": "success",
  "text": "Extracted document text."
}
```

A failed result may have the following structure:

```json
{
  "file_id": "example_file_id",
  "file_name": "corrupted_document.pdf",
  "mime_type": "application/pdf",
  "method": "Not determined",
  "status": "error",
  "text": "",
  "error": "Error description"
}
```

These examples illustrate the intended response structure. The actual output depends on the document and the implementation.

The file `samples/sample_output.json` should contain a real result produced by running the application against a test Drive folder. It should not contain placeholder data presented as an actual test result.

## 11. Automated Testing

The project includes tests for:

- Health and API endpoints.
- File listing and Drive-related errors.
- Extraction success and per-file failure handling.
- Google Drive folder URL validation.
- OCR success and invalid or missing images.
- Multipage PDFs, empty pages, missing PDFs, and scanned-PDF OCR fallback.

Run the suite locally:

```powershell
python -m pytest -v
```

Run the suite in Docker:

```powershell
docker compose run --rm app python -m pytest -v
```

The latest verified run reported 17 passing tests in both environments. Tests should be rerun after the final code changes.

## 12. Configuration and Security

- Keep `.env` out of version control.
- Commit `.env.example` without real credentials.
- Do not include API keys, private documents, or confidential extraction results in the public repository.
- Validate file IDs against the requested folder.
- Sanitize filenames used for temporary downloads.
- Remove temporary files after processing.
- Restrict the application to public Drive folders unless authentication is explicitly added.
- Avoid including sensitive information in logs or error responses.

The Docker image installs Tesseract and the English, French, and Arabic language data. The application’s selected language must correspond to the OCR configuration used for each request.

## 13. Limitations

This project is a proof of concept and has not been presented as a production deployment.

Known limitations include:

- Only publicly accessible Google Drive folders are supported.
- OCR quality depends on image resolution, orientation, language, and document quality.
- Large or malformed files may fail during retrieval or extraction.
- Processing large batches synchronously can affect responsiveness.
- Tesseract language data must be available for the requested OCR language.
- External Drive access requires a valid configuration and network connectivity.

If asynchronous processing and live progress reporting are not implemented, the application should not be described as providing real-time progress. These capabilities require separate implementation and testing.

## 14. Licensing

The repository includes:

- `LICENSE`: the licence selected for this project.
- `LICENSES.md`: a dependency licence inventory.

Before submission, verify the actual versions and licences of the main dependencies, whether they can be used in closed-source commercial products, and whether attribution or additional notices are required.

Do not claim that all dependencies have been verified for commercial compatibility until the licence review is complete.

## 15. Git and Repository Conventions

The project follows the assessment’s preference for Conventional Commits and feature branches.

Examples of commit messages:

```text
feat(drive): list supported files from public folders
feat(ocr): add image text extraction
fix(pdf): handle scanned PDFs without usable text
test(extraction): cover PDF and OCR routing
build(docker): add Docker Compose support
docs(readme): document setup and Docker usage
```

Use small, focused commits that explain the evolution of the project. Keep virtual environments, caches, generated files, and secrets out of Git.

The public GitHub repository should include the application source, tests, README, `.gitignore`, `.env.example`, `LICENSE`, `LICENSES.md`, and a genuine sample JSON output.

## 16. Bonus Features and Project Status

| Assessment item                            | Current evidence                                                |
| ------------------------------------------ | --------------------------------------------------------------- |
| Scanned-PDF OCR fallback                   | Automated test passes                                           |
| Docker / Docker Compose                    | Image built; application starts; Docker tests pass              |
| Automated tests                            | 17 tests pass in the latest reported runs                       |
| OCR language selection                     | Verify supported choices and end-to-end behavior                |
| Asynchronous processing with live progress | Requires implementation and verification if not already present |

The next engineering milestone is to verify the OCR language-selection flow, implement and test asynchronous processing with live progress if it is still missing, generate the final sample JSON output, and complete the dependency licence review.

## 17. Final Deliverables Checklist

- [ ] Public GitHub repository.
- [ ] README with architecture, setup, execution, limitations, and next steps.
- [ ] `LICENSE` and verified `LICENSES.md`.
- [ ] `.env.example` without secrets.
- [ ] Real `samples/sample_output.json` generated from a test Drive folder.
- [ ] Automated tests passing locally and in Docker.
- [ ] Dockerfile and Compose configuration.
- [ ] Clean Git history with Conventional Commits and feature branches.
- [ ] Optional demonstration video, no longer than two minutes.

**Assessment:** DI Xpertia — TA-2026-01
**Project:** Drive-to-Text Document Extraction POC
**Stack:** Python, FastAPI, Google Drive API, PDF extraction, Tesseract OCR, pytest, Docker, and Docker Compose.
