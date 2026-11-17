
# Standard library
import io
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Third-party libraries
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
load_dotenv()


class DriveServiceError(Exception):
    """Raised when a Google Drive folder cannot be accessed."""


def extract_folder_id(folder_url: str) -> str:
    """Extract the folder ID from a Google Drive URL."""
    parsed_url = urlparse(folder_url.strip())

    if parsed_url.hostname not in {
        "drive.google.com",
        "www.drive.google.com",
    }:
        raise DriveServiceError("Please provide a valid Google Drive URL.")

    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", parsed_url.path)

    if match:
        return match.group(1)

    folder_ids = parse_qs(parsed_url.query).get("id", [])

    if folder_ids and re.fullmatch(r"[a-zA-Z0-9_-]+", folder_ids[0]):
        return folder_ids[0]

    raise DriveServiceError(
        "Folder ID not found. Copy the URL of the actual Drive folder."
    )


def list_folder_files(folder_url: str) -> list[dict]:
    """List PDF and image files in an accessible Google Drive folder."""
    folder_id = extract_folder_id(folder_url)
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise DriveServiceError(
            "GOOGLE_API_KEY is missing. Check the .env file."
        )

    try:
        service = build(
            "drive",
            "v3",
            developerKey=api_key,
            cache_discovery=False,
        )

        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=100,
            fields="files(id, name, mimeType, webViewLink, size)",
        ).execute()

        supported_types = {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/tiff",
            "image/bmp",
        }

        return [
            file
            for file in response.get("files", [])
            if file.get("mimeType") in supported_types
        ]

    except HttpError as exc:
        status = getattr(exc.resp, "status", "unknown")
        content = getattr(exc, "content", b"")

        if isinstance(content, bytes):
            details = content.decode("utf-8", errors="replace")
        else:
            details = str(content)

        details = details.replace(api_key, "[API_KEY_HIDDEN]")

        raise DriveServiceError(
            f"Google Drive HTTP error {status}: {details}"
        ) from exc

    except Exception as exc:
        details = str(exc) or "No additional details."
        details = details.replace(api_key, "[API_KEY_HIDDEN]")

        raise DriveServiceError(
            f"Technical error {type(exc).__name__}: {details}"
        ) from exc

def download_drive_file(
    file_id: str,
    destination: str | Path,
) -> Path:
    """Download a publicly accessible Google Drive file."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise DriveServiceError(
            "GOOGLE_API_KEY is missing. Check the .env file."
        )

    target = Path(destination)

    try:
        service = build(
            "drive",
            "v3",
            developerKey=api_key,
            cache_discovery=False,
        )

        request = service.files().get_media(fileId=file_id)
        target.parent.mkdir(parents=True, exist_ok=True)

        with io.BytesIO() as output:
            downloader = MediaIoBaseDownload(output, request)
            done = False

            while not done:
                _, done = downloader.next_chunk()

            target.write_bytes(output.getvalue())

        return target

    except HttpError as exc:
        raise DriveServiceError(
            f"Could not download Google Drive file: {exc}"
        ) from exc
    except Exception as exc:
        raise DriveServiceError(
            f"Download failed ({type(exc).__name__}): {exc}"
        ) from exc
