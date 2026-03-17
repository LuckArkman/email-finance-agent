import cv2
import numpy as np
import os
from PIL import Image

class ImageEnhancer:
    """
    Toolkit with isolated functions to improve the visual status of an image
    making features stand out before throwing it to the OCR model.
    """

    @staticmethod
    def rescale_image_dpi(image_path: str, scale_factor: float = 1.5) -> np.ndarray:
        """
        Increases or decreases actual image dimensions matrix (scaling).
        Better dimension helps ML algorithms lock onto font blocks.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        width = int(img.shape[1] * scale_factor)
        height = int(img.shape[0] * scale_factor)
        
        # INTER_CUBIC is excellent for zooming in typography
        resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
        return resized_img

    @staticmethod
    def apply_adaptive_threshold(img: np.ndarray) -> np.ndarray:
        """
        Converts to grayscale and applies OTSU binarization
        which calculates an optimal threshold value automatically.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Apply Gaussian Blur first to wash out background noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # OTSU binarization for crisp black & white contrast
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def remove_shadows(img: np.ndarray) -> np.ndarray:
        """
        Corrects bad lightning (shadows/corners) on phone-scanned documents
        by dilating the background and doing a subtraction.
        """
        rgb_planes = cv2.split(img)
        result_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(norm_img)
        
        shadow_removed = cv2.merge(result_planes)
        return shadow_removed

    @staticmethod
    def apply_morphological_transforms(thresh_img: np.ndarray) -> np.ndarray:
        """
        Applies dilation/erosion to close gaps in broken text fonts 
        or thin out overly bold typography.
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        # We perform a tiny dilation (thickening black lines/fonts assuming black text on white bg)
        # However, for threshold binary, text is often black (0) and bg is white (255)
        # If inverted, we would dilate. 
        # Here we just erode slightly to thin noise over standard binary:
        refined = cv2.erode(thresh_img, kernel, iterations=1)
        return refined


class CV2Pipeline:
    """
    Orchestration point. Takes a raw image from the Extractor
    and applies in sequence all necessary normalization steps 
    saving a highly optimized clean image for OCR.
    """
    
    def __init__(self, output_dir: str = "/tmp/clean_images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_image(self, image_path: str) -> str:
        """
        Executes the computer vision pipeline. Returns optimized image local path.
        """
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        out_filepath = os.path.join(self.output_dir, f"{name}_cv2.png")
        
        try:
            # 1. Start with rescaling/loading
            img = ImageEnhancer.rescale_image_dpi(image_path, scale_factor=1.2)
            
            # 2. Correct phone-scan/shadows
            light_img = ImageEnhancer.remove_shadows(img)
            
            # 3. Convert to grayscale and binarize
            thresh_img = ImageEnhancer.apply_adaptive_threshold(light_img)
            
            # 4. Filter morphological issues
            final_img = ImageEnhancer.apply_morphological_transforms(thresh_img)

            # Save the pure result
            cv2.imwrite(out_filepath, final_img)
            print(f"CV2 Pipeline finalized. Clean image saved at: {out_filepath}")
            return out_filepath

        except Exception as e:
            print(f"Error during CV2 pipeline for {image_path}: {e}")
            return image_path  # Returns original path if augmentation fails
