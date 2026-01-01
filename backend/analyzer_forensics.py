import cv2
import numpy as np
from config import Config
from PIL import Image, ImageChops
import io

class AnalyzerForensics:
    def analyze_ela(self, image_rgb: np.ndarray) -> bool:
        """
        Performs Error Level Analysis (ELA).
        
        How it works:
        JPEGs lose quality when saved. If you paste a high-quality object 
        into a low-quality image, they will have different "compression errors".
        This function highlights those differences.
        """
        # 1. Convert numpy array to a PIL Image object for saving simulation.
        original = Image.fromarray(image_rgb)
        
        # 2. Save this image to a "fake" file in memory (RAM) at 90% quality.
        # We simulate re-saving the image to see how it degrades.
        buffer = io.BytesIO()
        original.save(buffer, "JPEG", quality=90)
        
        # 3. Load that degraded image back.
        buffer.seek(0) # Go to start of file
        compressed = Image.open(buffer)
        
        # 4. Find the difference between Original and Compressed.
        # Logic: If part of the image was pasted in from a source with different quality,
        # it will react differently to compression than the background.
        diff = ImageChops.difference(original, compressed)
        
        # 5. Find the maximum difference value.
        # If the difference is huge, something suspicious happened.
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema]) # Get max value from channels
        
        # If max difference > Threshold, it might be edited.
        return max_diff > Config.ELA_FACTOR

    def analyze_lighting(self, image_rgb: np.ndarray) -> str:
        """
        Checks lighting consistency using the HSV color space.
        HSV = Hue (Color), Saturation (Intensity), Value (Brightness).
        """
        # 1. Convert RGB to HSV. We only care about 'V' (Brightness).
        hsv_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
        v_channel = hsv_image[:, :, 2] # Index 2 is Value.

        # 2. Calculate a Histogram (a count of how many bright vs dark pixels there are).
        # Range is 0 (black) to 255 (white).
        hist = cv2.calcHist([v_channel], [0], None, [256], [0, 256])

        # 3. Check for "Low Dynamic Range".
        # If pixels are only super bright or super dark, it's a bad or edited photo.
        # Simple Logic: Are most pixels stuck at the extremes?
        dark_pixels = np.sum(hist[0:20])
        bright_pixels = np.sum(hist[235:255])
        total_pixels = image_rgb.shape[0] * image_rgb.shape[1]

        if (dark_pixels + bright_pixels) / total_pixels > 0.8:
            return "Artificial/Bad Lighting"
        return "Natural Lighting"

    def detect_reflections(self, image_rgb: np.ndarray) -> bool:
        """
        Detects bright spots that look like camera flash reflections.
        """
        # 1. Convert to grayscale (black and white).
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        
        # 2. Threshold: Turn anything super bright (over 240) to pure white (255).
        _, bright_spots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        # 3. Count the bright pixels.
        count = cv2.countNonZero(bright_spots)
        
        # If we have a small cluster of super bright pixels, it's likely a flash/mirror.
        return count > 50 and count < 5000