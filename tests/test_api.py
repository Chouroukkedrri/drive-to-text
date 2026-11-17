
from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.services.drive_service import DriveServiceError


client = TestClient(main_module.app)

TEST_FOLDER_URL = (
    "https://drive.google.com/drive/folders/test-folder-id"
)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_files_returns_supported_files(monkeypatch):
    fake_files = [
        {
            "id": "pdf-123",
            "name": "sample.pdf",
            "mimeType": "application/pdf",
            "size": "1234",
        }
    ]

    monkeypatch.setattr(
        main_module,
        "list_folder_files",
        lambda folder_url: fake_files,
    )

    response = client.post(
        "/api/files",
        json={"folder_url": TEST_FOLDER_URL},
    )

    assert response.status_code == 200
    assert response.json()["files"] == [
        {
            "id": "pdf-123",
            "name": "sample.pdf",
            "mime_type": "application/pdf",
            "size": "1234",
        }
    ]


def test_list_files_reports_drive_error(monkeypatch):
    def fail_to_list(folder_url):
        raise DriveServiceError("Folder is inaccessible")

    monkeypatch.setattr(
        main_module,
        "list_folder_files",
        fail_to_list,
    )

    response = client.post(
        "/api/files",
        json={"folder_url": TEST_FOLDER_URL},
    )

    assert response.status_code == 400
    assert "inaccessible" in response.json()["detail"]


def test_extract_pdf_success(monkeypatch, tmp_path):
    fake_files = [
        {
            "id": "pdf-123",
            "name": "sample.pdf",
            "mimeType": "application/pdf",
        }
    ]

    monkeypatch.setattr(
        main_module,
        "list_folder_files",
        lambda folder_url: fake_files,
    )

    def fake_download(file_id, destination):
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake PDF content")
        return path

    monkeypatch.setattr(
        main_module,
        "download_drive_file",
        fake_download,
    )

    # The updated PDF extractor returns both the text and its method.
    monkeypatch.setattr(
        main_module,
        "extract_pdf_text_with_method",
        lambda path, languages="fra+eng": (
            "Texte extrait du PDF",
            "PDF parser",
        ),
    )

    response = client.post(
        "/api/extract",
        json={
            "folder_url": TEST_FOLDER_URL,
            "file_ids": ["pdf-123"],
        },
    )

    assert response.status_code == 200

    result = response.json()["results"][0]
    assert result["file_name"] == "sample.pdf"
    assert result["status"] == "success"
    assert result["text"] == "Texte extrait du PDF"
    assert result["method"] == "PDF parser"


def test_extraction_continues_when_one_file_fails(monkeypatch):
    fake_files = [
        {
            "id": "pdf-123",
            "name": "broken.pdf",
            "mimeType": "application/pdf",
        },
        {
            "id": "img-456",
            "name": "sample.png",
            "mimeType": "image/png",
        },
    ]

    monkeypatch.setattr(
        main_module,
        "list_folder_files",
        lambda folder_url: fake_files,
    )

    def fake_download(file_id, destination):
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake content")
        return path

    monkeypatch.setattr(
        main_module,
        "download_drive_file",
        fake_download,
    )

    # Simulate a PDF extraction failure.
    def fail_pdf(path, languages="fra+eng"):
        raise RuntimeError("Simulated PDF failure")

    monkeypatch.setattr(
        main_module,
        "extract_pdf_text_with_method",
        fail_pdf,
    )

    monkeypatch.setattr(
        main_module,
        "extract_image_text",
        lambda path, languages="fra+eng": "Texte reconnu",
    )

    response = client.post(
        "/api/extract",
        json={
            "folder_url": TEST_FOLDER_URL,
            "file_ids": ["pdf-123", "img-456"],
        },
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert len(results) == 2

    # The PDF fails, but processing continues with the image.
    assert results[0]["status"] == "error"
    assert "Simulated PDF failure" in results[0]["error"]

    assert results[1]["status"] == "success"
    assert results[1]["text"] == "Texte reconnu"
    assert results[1]["method"] == "OCR"


def test_extract_rejects_unknown_file_id(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "list_folder_files",
        lambda folder_url: [
            {
                "id": "pdf-123",
                "name": "sample.pdf",
                "mimeType": "application/pdf",
            }
        ],
    )

    response = client.post(
        "/api/extract",
        json={
            "folder_url": TEST_FOLDER_URL,
            "file_ids": ["unknown-id"],
        },
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"]

