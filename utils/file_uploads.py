import os
import uuid
from werkzeug.utils import secure_filename


def _allowed_image(filename, allowed_extensions):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def save_image_file(file_storage, upload_root, subfolder, allowed_extensions):
    """Save an uploaded image under static/uploads/<subfolder> and return relative path."""
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None, None

    filename = secure_filename(file_storage.filename)
    if not _allowed_image(filename, allowed_extensions):
        return None, 'Formato no permitido. Usa JPG, JPEG, PNG o WEBP.'

    extension = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{extension}"

    destination_dir = os.path.join(upload_root, subfolder)
    os.makedirs(destination_dir, exist_ok=True)

    absolute_path = os.path.join(destination_dir, unique_name)
    file_storage.save(absolute_path)

    # Return path relative to static/ so url_for('static', filename=...) works.
    return os.path.join('uploads', subfolder, unique_name).replace('\\', '/'), None


def delete_image_file(static_root, relative_path):
    if not relative_path:
        return
    absolute_path = os.path.join(static_root, relative_path)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)
