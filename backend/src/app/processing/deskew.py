import cv2
import numpy as np
import os
from skimage.transform import hough_line, hough_line_peaks
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu

class DeskewProcessor:
    """
    Handles deskewing (skew correction) of scanned images or photos,
    ensuring that skewed lines are horizontally aligned for the OCR engine.
    """
    def __init__(self, output_dir: str = "/tmp/deskewed_images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def calculate_skew_angle(image: np.ndarray) -> float:
        """
        Calculates the angle of text blocks using probabilistic Hough Transform or skimage.
        """
        # Convert to grayscale via skimage if colored
        if len(image.shape) == 3:
            gray = rgb2gray(image)
        else:
            gray = image

        # Apply threshold to binarize (background 0, text 1)
        thresh_val = threshold_otsu(gray)
        binary = gray < thresh_val

        # Hough Transform to detect lines
        tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
        h, theta, d = hough_line(binary, theta=tested_angles)

        # Get peak lines
        _, angles, _ = hough_line_peaks(h, theta, d)

        if len(angles) == 0:
            return 0.0

        # Calculate median angle
        # Most lines in text are horizontal (angle ~ 90 degrees or -90 in polar coords relative to vertical)
        # In skimage, theta = 0 is horizontal line.
        # We need to compute the skew difference from 0 or pi/2
        angles = np.rad2deg(angles)
        
        # We find the dominant angle. Text lines are usually horizontal, meaning theta is near 90 or -90.
        # So deviation from 90 is the skew.
        skew_angles = []
        for angle in angles:
            if 45 < angle <= 90:
                skew_angles.append(angle - 90)
            elif -90 <= angle < -45:
                skew_angles.append(angle + 90)
            elif -45 <= angle <= 45:
                skew_angles.append(angle)

        if not skew_angles:
            return 0.0
            
        return float(np.median(skew_angles))

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotates the image by the given angle (Affine Transformation), padding the background.
        """
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        # Get the rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new image dimensions to fit the rotated image
        abs_cos = abs(M[0, 0])
        abs_sin = abs(M[0, 1])

        new_w = int(h * abs_sin + w * abs_cos)
        new_h = int(h * abs_cos + w * abs_sin)

        # Adjust the rotation matrix to take into account translation
        M[0, 2] += new_w / 2 - center[0]
        M[1, 2] += new_h / 2 - center[1]

        # Preenchimento de bordas (Background padding) with white color
        bg_color = (255, 255, 255) if len(image.shape) == 3 else 255
        rotated = cv2.warpAffine(
            image, M, (new_w, new_h),
            flags=cv2.INTER_CUBIC, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=bg_color
        )
        
        return rotated

    def correct_document_perspective(self, image_path: str) -> str:
        """
        Main pipeline method to read, deskew, and save the corrected perspective image.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        angle = self.calculate_skew_angle(image)
        
        # If angle is minimal, we don't skew
        if abs(angle) < 0.5:
            print(f"Angle {angle:.2f} is minimal. Skipping deskew for {image_path}")
            return image_path
            
        print(f"Deskewing {image_path} with angle {angle:.2f} degrees")
        deskewed_image = self.rotate_image(image, angle)

        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        out_filepath = os.path.join(self.output_dir, f"{name}_deskewed{ext}")
        
        cv2.imwrite(out_filepath, deskewed_image)
        return out_filepath
