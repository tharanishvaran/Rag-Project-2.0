import os
from flask import current_app


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md', 'pptx'}


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has an allowed extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS



def get_upload_path(stored_filename: str) -> str:
    """Get absolute upload path for a stored filename."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return os.path.join(upload_folder, stored_filename)


def safe_delete_file(file_path: str) -> bool:
    """Safely delete a file, returning True if deleted, False if not found."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False
    return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes is None:
        return 'Unknown'
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
