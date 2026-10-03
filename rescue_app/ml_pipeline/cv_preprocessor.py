import cv2
import numpy as np
import os

class OpenCVPreprocessor:
    """Handles image cleaning, resizing, color normalization and visual bounding annotations."""

    @staticmethod
    def load_and_preprocess(image_path, target_size=(640, 640)):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")
        
        # Read with OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Failed to decode image with OpenCV")

        original_h, original_w = image.shape[:2]

        # Enhance contrast with CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Bilateral filter for noise reduction while keeping edges sharp
        smoothed = cv2.bilateralFilter(enhanced, 5, 50, 50)

        return smoothed, (original_w, original_h)

    @staticmethod
    def draw_detections(image_path, detections, output_path):
        """Draws aesthetic bounding boxes with OpenCV."""
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        for det in detections:
            x1, y1, x2, y2 = det['box']
            label = det['label']
            conf = det['confidence']
            is_injury = det.get('is_injury', False)

            color = (0, 0, 230) if is_injury else (0, 200, 0) # Red for injury, Green for Animal
            
            # Box
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
            
            # Label banner
            text = f"{label} ({int(conf * 100)}%)"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img, (int(x1), max(0, int(y1) - 25)), (int(x1) + tw + 10, max(25, int(y1))), color, -1)
            cv2.putText(img, text, (int(x1) + 5, max(18, int(y1) - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        return output_path