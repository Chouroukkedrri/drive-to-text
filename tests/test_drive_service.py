
import pytest

from app.services.drive_service import (
    DriveServiceError,
    extract_folder_id,
)


def test_extract_folder_id_from_standard_url():
    url = "https://drive.google.com/drive/folders/abc_123-XYZ"
    assert extract_folder_id(url) == "abc_123-XYZ"


def test_extract_folder_id_from_url_with_query():
    url = "https://drive.google.com/open?id=abc_123-XYZ"
    assert extract_folder_id(url) == "abc_123-XYZ"


def test_reject_invalid_domain():
    with pytest.raises(DriveServiceError):
        extract_folder_id("https://example.com/folders/abc123")


def test_reject_url_without_folder_id():
    with pytest.raises(DriveServiceError):
        extract_folder_id("https://drive.google.com/drive/my-drive")
