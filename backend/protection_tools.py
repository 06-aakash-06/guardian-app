# protection_tools.py
import cv2
import numpy as np

class ProtectionTools:
    
    def generate_preview(self, image_rgb: np.ndarray, detections):
        """
        Creates a temporary image with numbered boxes drawn on it.
        This helps the user decide which faces to blur (ID: 0, ID: 1, etc).
        """
        # Create a copy so we don't draw on the actual image being processed
        preview_img = image_rgb.copy()
        
        for i, item in enumerate(detections):
            x, y, w, h = item['box']
            label = f"ID:{i} ({item['type']})"
            
            # 1. Draw a Green Box
            cv2.rectangle(preview_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 2. Draw the ID Number above the box
            cv2.putText(preview_img, label, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
        return preview_img

    def cloak_face(self, image_rgb: np.ndarray, face_box):
        """
        Applies 'Adversarial Noise' to confuse AI, but keeps face visible to humans.
        """
        x, y, w, h = face_box
        roi = image_rgb[y:y+h, x:x+w] 

        noise = np.random.normal(0, 25, roi.shape).astype('uint8')
        cloaked_face = cv2.add(roi, noise) 

        image_rgb[y:y+h, x:x+w] = cloaked_face
        return image_rgb

    def smart_redact(self, image_rgb: np.ndarray, detections_to_blur):
        """
        Redacts ONLY the specific items passed in the list.
        """
        for item in detections_to_blur:
            x, y, w, h = item['box']
            
            if item['type'] == 'FACE':
                # Gaussian Blur (Frosted Glass effect)
                roi = image_rgb[y:y+h, x:x+w]
                # Dynamic kernel size based on face size (smoother blur)
                ksize = (w // 2) | 1 # Ensure it's an odd number
                blur = cv2.GaussianBlur(roi, (ksize, ksize), 30)
                image_rgb[y:y+h, x:x+w] = blur
                
            elif item['type'] == 'BARCODE':
                # Black Box
                cv2.rectangle(image_rgb, (x, y), (x+w, y+h), (0, 0, 0), -1)
        
        return image_rgb