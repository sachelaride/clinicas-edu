import os
from pathlib import Path
import shutil
from typing import Optional
import uuid

from app.core.config import settings

class FileStorageService:
    def __init__(self):
        self.base_upload_dir = Path(settings.BASE_UPLOAD_DIR)
        self._ensure_base_upload_dir_exists()

    def _ensure_base_upload_dir_exists(self):
        """Ensures the base upload directory exists."""
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_clinic_dir(self, clinic_name: str) -> Path:
        """Returns the path for a specific clinic's directory."""
        clinic_dir = self.base_upload_dir / clinic_name.replace(" ", "_")
        clinic_dir.mkdir(exist_ok=True)
        return clinic_dir

    def _get_next_folder_path(self, base_path: Path, prefix: str) -> Path:
        """
        Determines the next folder path based on the 400-document limit.
        e.g., prontuarios/0001, prontuarios/0002
        """
        current_folder_index = 1
        while True:
            folder_name = f"{prefix}{current_folder_index:04d}"
            folder_path = base_path / folder_name
            
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                return folder_path
            
            # Count files in the current folder
            file_count = len(list(folder_path.iterdir()))
            if file_count < 400:
                return folder_path
            
            current_folder_index += 1

    def save_prontuario_file(self, clinic_name: str, file_content: bytes, file_extension: str) -> str:
        """
        Saves a prontuario file to the clinic's prontuarios directory.
        Returns the relative path to the saved file.
        """
        clinic_dir = self._get_clinic_dir(clinic_name)
        prontuarios_base_path = clinic_dir / "prontuarios"
        prontuarios_base_path.mkdir(exist_ok=True)

        target_folder = self._get_next_folder_path(prontuarios_base_path, "prontuario_")
        
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = target_folder / file_name
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path.relative_to(self.base_upload_dir))

    def save_documento_file(self, clinic_name: str, file_content: bytes, file_extension: str) -> str:
        """
        Saves a document file to the clinic's documents directory.
        Returns the relative path to the saved file.
        """
        clinic_dir = self._get_clinic_dir(clinic_name)
        documentos_base_path = clinic_dir / "documentos"
        documentos_base_path.mkdir(exist_ok=True)

        target_folder = self._get_next_folder_path(documentos_base_path, "documento_")
        
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = target_folder / file_name
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path.relative_to(self.base_upload_dir))

    def delete_file(self, relative_file_path: str):
        """Deletes a file given its relative path from the base upload directory."""
        file_path = self.base_upload_dir / relative_file_path
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            # Optionally, clean up empty folders
            self._cleanup_empty_folders(file_path.parent)

    def _cleanup_empty_folders(self, path: Path):
        """Recursively deletes empty parent folders."""
        while path != self.base_upload_dir and not any(path.iterdir()):
            try:
                path.rmdir()
                path = path.parent
            except OSError: # Folder might not be empty or other error
                break

# Instantiate the service
file_storage_service = FileStorageService()