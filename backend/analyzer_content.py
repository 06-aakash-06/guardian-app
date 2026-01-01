# analyzer_content.py
import cv2
import pytesseract
import re
import numpy as np
from pyzbar.pyzbar import decode
from config import Config

class AnalyzerContent:
    def __init__(self):
        """
        Initialize the scanner tools.
        SWITCHED ENGINE: Using OpenCV instead of MediaPipe for 100% stability on Mac.
        """
        # Load OpenCV's built-in "Haar Cascade" Face Detector.
        # This model comes pre-installed with opencv-python.
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def analyze_faces(self, image_rgb: np.ndarray):
        """
        Detects faces using OpenCV.
        """
        height, width, _ = image_rgb.shape
        
        # 1. OpenCV needs Grayscale (Black & White) to find faces efficiently.
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        
        # 2. Run the detection.
        # scaleFactor=1.1: Look for faces at different zoom levels.
        # minNeighbors=5: strictness (higher = fewer false positives).
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        detections = []
        is_child_risk = False

        # 3. Process results
        for (x, y, w, h) in faces:
            # Check "Sharenting Risk" (Child Logic)
            # If face height is > 20% of image height, it's a close-up.
            if (h / height) > Config.FACE_SIZE_RATIO:
                is_child_risk = True
            
            # Note: OpenCV returns python integers, we ensure they are clean for the JSON format.
            detections.append({"type": "FACE", "box": (int(x), int(y), int(w), int(h))})
                
        return detections, is_child_risk

    def scan_text_pii(self, image_rgb: np.ndarray):
        """
        Uses OCR to read text and Regex to find sensitive patterns.
        """
        try:
            text_content = pytesseract.image_to_string(image_rgb)
        except Exception:
            # If Tesseract crashes/isn't found, return empty to keep app alive.
            return []
        
        findings = []
        
        # Email Regex
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content):
            findings.append("EMAIL_FOUND")
        # Phone Regex
        if re.search(r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', text_content):
            findings.append("PHONE_FOUND")
            
        return findings

    def scan_barcodes(self, image_rgb: np.ndarray):
        """
        Scans for QR codes and Barcodes.
        """
        barcodes = decode(image_rgb)
        barcode_list = []

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            barcode_list.append({"type": "BARCODE", "box": (x, y, w, h)})
            
        return barcode_list