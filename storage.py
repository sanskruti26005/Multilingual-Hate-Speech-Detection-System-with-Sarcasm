# storage.py
import os
from PIL import Image
from datetime import datetime
import shutil

UPLOAD_FOLDER = "uploaded_images"
THUMBNAIL_FOLDER = "thumbnails"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

def _timestamp_filename(suffix=".png"):
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f") + suffix

def save_pil_image(img):
    """Save a PIL Image object to uploads and return path."""
    filename = _timestamp_filename(".png")
    path = os.path.join(UPLOAD_FOLDER, filename)
    img.save(path)
    return path

def save_image_file(file_path):
    """Copy an existing image file into uploads and return new path."""
    ext = os.path.splitext(file_path)[1] or ".png"
    filename = _timestamp_filename(ext)
    dst = os.path.join(UPLOAD_FOLDER, filename)
    shutil.copyfile(file_path, dst)
    return dst

def make_thumbnail(img, size=(180, 120)):
    """Create thumbnail from a PIL image object and return path."""
    thumb = img.copy()
    thumb.thumbnail(size)
    filename = _timestamp_filename("_thumb.png")
    path = os.path.join(THUMBNAIL_FOLDER, filename)
    thumb.save(path)
    return path

def make_thumbnail_from_path(image_path, size=(180, 120)):
    img = Image.open(image_path).convert("RGB")
    return make_thumbnail(img, size=size)  