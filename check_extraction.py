
from pathlib import Path
import re

from app.services.drive_service import (
    DriveServiceError,
    list_folder_files,
    download_drive_file,
)
from app.services.pdf_extractor import (
    PDFExtractionError,
    extract_pdf_text,
)
from app.services.ocr_extractor import (
    OCRExtractionError,
    extract_image_text,
)

# Remplace cette valeur par la même URL qui a déjà fonctionné
# dans ton fichier check_drive.py.
FOLDER_URL = "https://drive.google.com/drive/folders/11MtWGee3UFBHLVsVxb8L0GoPR0CFVf1a?usp=sharing"

DOWNLOAD_DIR = Path("downloads")


def safe_filename(filename: str) -> str:
    """Create a safe local filename."""
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", filename)
    return cleaned.strip(" .") or "downloaded_file"


def main():
    print("=== Test téléchargement et extraction ===")

    try:
        files = list_folder_files(FOLDER_URL)
    except DriveServiceError as exc:
        print(f"Erreur lors de la récupération des fichiers : {exc}")
        return

    if not files:
        print("Aucun fichier PDF ou image trouvé.")
        return

    print(f"{len(files)} fichier(s) trouvé(s).\n")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for file in files:
        name = file.get("name", "fichier_inconnu")
        file_id = file.get("id")
        mime_type = file.get("mimeType", "")

        print(f"--- Fichier : {name} ---")

        if not file_id:
            print("Erreur : identifiant du fichier absent.\n")
            continue

        destination = DOWNLOAD_DIR / (
            f"{file_id}_{safe_filename(name)}"
        )

        try:
            # 1. Télécharger le fichier
            local_path = download_drive_file(
                file_id,
                destination,
            )
            print(f"Téléchargement réussi : {local_path}")

            # 2. Extraire le texte selon le type du fichier
            if mime_type == "application/pdf":
                text = extract_pdf_text(local_path)
            elif mime_type.startswith("image/"):
                text = extract_image_text(
                    local_path,
                    languages="fra+eng",
                )
            else:
                print(f"Type non pris en charge : {mime_type}\n")
                continue

            # 3. Afficher le résultat
            if text.strip():
                print("Texte extrait :")
                print(text[:1200])

                if len(text) > 1200:
                    print("... Texte tronqué à l'écran.")
            else:
                print(
                    "Aucun texte détecté. "
                    "Le PDF est peut-être numérisé ou l'image "
                    "ne contient peut-être pas de texte lisible."
                )

        except (
            DriveServiceError,
            PDFExtractionError,
            OCRExtractionError,
        ) as exc:
            print(f"Erreur pour ce fichier : {exc}")

        print()


if __name__ == "__main__":
    main()
