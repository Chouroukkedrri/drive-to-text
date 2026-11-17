
from app.services.drive_service import (
    DriveServiceError,
    list_folder_files,
)

FOLDER_URL = "https://drive.google.com/drive/folders/11MtWGee3UFBHLVsVxb8L0GoPR0CFVf1a?usp=sharing"


def main():
    print("=== Début du test Google Drive ===", flush=True)

    try:
        print("Recherche des fichiers...", flush=True)
        files = list_folder_files(FOLDER_URL)

        print(f"Connexion réussie : {len(files)} fichier(s) trouvé(s).")

        for file in files:
            print(f"- {file.get('name')} ({file.get('mimeType')})")

        if not files:
            print("Aucun PDF ou fichier image compatible trouvé.")

    except DriveServiceError as exc:
        print(f"Erreur Google Drive : {exc}", flush=True)
if __name__ == "__main__":
    main()
