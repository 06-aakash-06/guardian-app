import cv2
import numpy as np
import os
from PIL import Image

def load_image_safe(path: str) -> np.ndarray:
    """
    Loads an image from the computer disk into memory.
    
    Args:
        path (str): The location of the file (e.g., "C:/photos/me.jpg").
        
    Returns:
        np.ndarray: A matrix of numbers representing the pixels (RGB format).
    """
    # 1. Check if the file actually exists.
    if not os.path.exists(path):
        raise FileNotFoundError(f"Error: The file at {path} was not found.")

    # 2. Read the image using OpenCV.
    # OpenCV reads images in 'BGR' (Blue-Green-Red) order by default.
    image_bgr = cv2.imread(path)

    if image_bgr is None:
        raise ValueError("Error: This file is not a valid image.")

    # 3. Convert BGR to RGB (Red-Green-Blue).
    # Most AI libraries (like MediaPipe) expect Red to be first.
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    return image_rgb

def save_image_safe(image_rgb: np.ndarray, original_path: str, suffix: str) -> str:
    """
    Saves the processed image back to disk.
    
    Why use Pillow (Image.fromarray) instead of OpenCV (cv2.imwrite)?
    OpenCV sometimes copies old metadata. Pillow creates a fresh file structure,
    stripping hidden data automatically.
    """
    # 1. Create a new filename (e.g., "photo.jpg" -> "photo_safe.jpg")
    base, ext = os.path.splitext(original_path)
    new_path = f"{base}{suffix}{ext}"

    # 2. Convert the number matrix back into a picture object.
    pil_image = Image.fromarray(image_rgb)

    # 3. Save it. We don't attach any 'exif' data, so it's clean.
    pil_image.save(new_path)
    
    return new_path