import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.services.drive_service import (
    DriveServiceError,
    download_drive_file,
    list_folder_files,
)
from app.services.pdf_extractor import (
    extract_pdf_text_with_method,
)
from app.services.ocr_extractor import extract_image_text


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Drive-to-Text")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# --------------------------------------------------
# Favicon
# --------------------------------------------------

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Serve the application favicon."""
    favicon_path = BASE_DIR / "static" / "favicon.svg"

    return FileResponse(
        favicon_path,
        media_type="image/svg+xml",
    )


# --------------------------------------------------
# Request models
# --------------------------------------------------

class FolderRequest(BaseModel):
    folder_url: str


class ExtractionRequest(FolderRequest):
    file_ids: list[str]
    ocr_language: Literal[
        "eng",
        "fra",
        "ara",
        "fra+eng",
    ] = "fra+eng"


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def safe_filename(filename: str) -> str:
    """Create a safe local filename for a temporary download."""
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", filename)
    return cleaned.strip(" .") or "document"


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request, folder_url: str = ""):
    """Display the page and optionally list Drive files."""

    files = []
    drive_error = None
    searched = bool(folder_url.strip())

    if searched:
        try:
            files = list_folder_files(folder_url.strip())
        except DriveServiceError as exc:
            drive_error = str(exc)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "folder_url": folder_url,
            "files": files,
            "drive_error": drive_error,
            "searched": searched,
        },
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    """Check whether the API is running."""
    return {"status": "ok"}


# --------------------------------------------------
# Google Drive file listing
# --------------------------------------------------

@app.post("/api/files")
def get_drive_files(payload: FolderRequest):
    """List supported files in a public Google Drive folder."""

    folder_url = payload.folder_url.strip()

    if not folder_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a Google Drive folder URL.",
        )

    try:
        files = list_folder_files(folder_url)

    except DriveServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "files": [
            {
                "id": file["id"],
                "name": file.get("name", "Unnamed file"),
                "mime_type": file.get("mimeType", ""),
                "size": file.get("size"),
            }
            for file in files
        ]
    }


# --------------------------------------------------
# Document extraction
# --------------------------------------------------

@app.post("/api/extract")
def extract_selected_files(payload: ExtractionRequest):
    """
    Download selected files and extract their text.

    Each file is processed independently so that a failure
    in one document does not stop the remaining documents.
    """

    folder_url = payload.folder_url.strip()
    requested_ids = list(dict.fromkeys(payload.file_ids))

    if not folder_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a Google Drive folder URL.",
        )

    if not requested_ids:
        raise HTTPException(
            status_code=400,
            detail="Select at least one document.",
        )

    # Retrieve files from Google Drive.
    try:
        available_files = list_folder_files(folder_url)

    except DriveServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    files_by_id = {
        file["id"]: file
        for file in available_files
        if file.get("id")
    }

    # Validate the requested file IDs.
    missing_ids = [
        file_id
        for file_id in requested_ids
        if file_id not in files_by_id
    ]

    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=(
                "Some selected files were not found in this folder. "
                "List the folder files again and retry."
            ),
        )

    selected_files = [
        files_by_id[file_id]
        for file_id in requested_ids
    ]

    results = []

    # Temporary downloads are removed automatically afterward.
    with TemporaryDirectory(
        prefix="drive_to_text_"
    ) as temp_dir:

        for index, file in enumerate(
            selected_files,
            start=1,
        ):
            file_id = file["id"]
            file_name = file.get("name", "Unnamed file")
            mime_type = file.get("mimeType", "")

            destination = (
                Path(temp_dir)
                / f"{index}_{safe_filename(file_name)}"
            )

            method = "Not determined"

            try:
                # Download the document from Google Drive.
                local_path = download_drive_file(
                    file_id,
                    destination,
                )

                # Extract text and identify the method used.
                if mime_type == "application/pdf":
                    (
                        extracted_text,
                        method,
                    ) = extract_pdf_text_with_method(
                        local_path,
                        languages=payload.ocr_language,
                    )

                elif mime_type.startswith("image/"):
                    method = "OCR"

                    extracted_text = extract_image_text(
                        local_path,
                        languages=payload.ocr_language,
                    )

                else:
                    method = "Not applicable"

                    raise ValueError(
                        f"Unsupported file type: {mime_type}"
                    )

                # Add the result to the JSON response.
                results.append(
                    {
                        "file_id": file_id,
                        "file_name": file_name,
                        "mime_type": mime_type,
                        "method": method,
                        "status": (
                            "success"
                            if extracted_text.strip()
                            else "empty"
                        ),
                        "text": extracted_text,
                    }
                )

            except Exception as exc:
                # Record the failure and continue with other files.
                results.append(
                    {
                        "file_id": file_id,
                        "file_name": file_name,
                        "mime_type": mime_type,
                        "method": method,
                        "status": "error",
                        "text": "",
                        "error": str(exc),
                    }
                )

    return {"results": results}