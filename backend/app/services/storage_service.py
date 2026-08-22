import os
import shutil
import logging
from abc import ABC, abstractmethod
from flask import current_app

logger = logging.getLogger(__name__)

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseStorageService(ABC):
    """Abstract Base Class for Document Storage Services."""

    @abstractmethod
    def save_file(self, file_obj, target_filename: str) -> str:
        """Save file object to storage and return destination path/URL."""
        pass

    @abstractmethod
    def get_file_path(self, target_filename: str) -> str:
        """Retrieve local filesystem path or URL for document processing."""
        pass

    @abstractmethod
    def delete_file(self, target_filename: str) -> bool:
        """Delete stored file."""
        pass


class LocalStorageService(BaseStorageService):
    """Local Filesystem Storage Service implementation."""

    def __init__(self, upload_folder: str = None):
        self._upload_folder = upload_folder

    def _get_upload_dir(self) -> str:
        if self._upload_folder:
            folder = self._upload_folder
        elif current_app:
            folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        else:
            folder = os.getenv('UPLOAD_FOLDER', 'uploads')

        if not os.path.isabs(folder):
            folder = os.path.join(_BACKEND_ROOT, folder)
        folder = os.path.normpath(folder)
        os.makedirs(folder, exist_ok=True)
        return folder

    def save_file(self, file_obj, target_filename: str) -> str:
        upload_dir = self._get_upload_dir()
        file_path = os.path.join(upload_dir, target_filename)
        
        if hasattr(file_obj, 'save'):
            file_obj.save(file_path)
        elif isinstance(file_obj, (bytes, bytearray)):
            with open(file_path, 'wb') as f:
                f.write(file_obj)
        else:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_obj, f)

        logger.info(f"Saved file {target_filename} to local storage at: {file_path}")
        return file_path

    def get_file_path(self, target_filename: str) -> str:
        upload_dir = self._get_upload_dir()
        return os.path.join(upload_dir, target_filename)

    def delete_file(self, target_filename: str) -> bool:
        file_path = self.get_file_path(target_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted local file: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete local file {file_path}: {e}")
                return False
        return False


def get_storage_service() -> BaseStorageService:
    """Factory function for instantiating configured StorageService."""
    storage_driver = os.getenv('STORAGE_DRIVER', 'local').lower()
    if storage_driver == 'local':
        return LocalStorageService()
    return LocalStorageService()
