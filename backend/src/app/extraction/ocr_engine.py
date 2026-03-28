import os
import pytesseract
import easyocr
import asyncio
from typing import Dict, Any, List

class PytesseractAdapter:
    """
    Wrapper for Tesseract engine configurations to guarantee
    good parsing of Portuguese and numerical data.
    """
    def __init__(self, lang: str = 'por+eng'):
        self.lang = lang
        # psm 6 = block of text. psm 3 = fully automatic page segmentation, but no OSD.
        # oem 3 = Default engine mode
        self.config = f"--oem 3 --psm 4 -l {self.lang}"
        # Make sure the Tesseract binary is accessible in environment path in prod.

    def extract_text(self, image_path: str) -> str:
        """Synchronous wrapper for pure string text extraction."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        return pytesseract.image_to_string(image_path, config=self.config)

    def get_data_boxes(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Returns verbose data containing text blocks, bounding boxes, and confidence.
        Useful for downstream NLP routing.
        """
        data = pytesseract.image_to_data(image_path, config=self.config, output_type=pytesseract.Output.DICT)
        boxes = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 10:  # Valid confidence only
                boxes.append({
                    "text": data['text'][i],
                    "x": data['left'][i],
                    "y": data['top'][i],
                    "w": data['width'][i],
                    "h": data['height'][i],
                    "conf": data['conf'][i]
                })
        return boxes


class EasyOCRAdapter:
    """
    Wrapper for EasyOCR, preferred when documents have complex backgrounds 
    or when Tesseract fails horribly.
    Uses GPU if available.
    """
    def __init__(self, langs: List[str] = ['pt', 'en']):
        # Warning: This loads Heavy ML Models into memory.
        # Typically initialized once at worker start.
        self.reader = easyocr.Reader(langs, gpu=True) # Change to True if Cuda is there

    def extract_text(self, image_path: str) -> str:
        # EasyOCR returns a list of tuples (bbox, text, prob)
        results = self.reader.readtext(image_path)
        text_content = " ".join([res[1] for res in results])
        return text_content


class LocalOCREngine:
    """
    The orchestrator determining which OCR Engine to run for initial string extraction
    before pushing raw strings to the Cloud APIs or NLP layers.
    """
    def __init__(self, engine_type: str = "tesseract"):
        self.engine_type = engine_type
        if engine_type == "tesseract":
            self.adapter = PytesseractAdapter()
        elif engine_type == "easyocr":
            self.adapter = EasyOCRAdapter()
        else:
            raise ValueError(f"Unknown OCR type: {engine_type}")

    async def extract_text_content(self, image_path: str) -> str:
        """Assíncrona para extração de String text evitando travas no backend. Suporta PDF e Imagens."""
        loop = asyncio.get_event_loop()
        
        # Support PDF by converting pages to images
        if image_path.lower().endswith(".pdf"):
            print(f"Detectado PDF. Convertendo para imagens para OCR: {image_path}")
            from app.processing.pdf_utils import DocumentSplitter
            splitter = DocumentSplitter()
            # Converte PDF para lista de caminhos de imagens PNG
            image_paths = await loop.run_in_executor(None, splitter.convert_pdf_to_images, image_path)
            
            # Executa OCR em cada página sequencialmente (ou paralelo se preferir)
            all_text = []
            for img_p in image_paths:
                page_text = await loop.run_in_executor(None, self.adapter.extract_text, img_p)
                all_text.append(page_text)
                # Opcional: remover imagem temporária após OCR
                os.remove(img_p)
            
            return "\n--- NOVA PÁGINA PDF ---\n".join(all_text)
            
        # Standard Image processing
        raw_text = await loop.run_in_executor(None, self.adapter.extract_text, image_path)
        return raw_text
        
    async def get_image_data_boxes(self, image_path: str) -> List[Dict[str, Any]]:
        """Used heavily if utilizing coordinate-based ML logic or mapping stamps."""
        if self.engine_type != "tesseract":
             raise NotImplementedError("Boxes implementation focused on Tesseract currently.")
             
        loop = asyncio.get_event_loop()
        boxes = await loop.run_in_executor(None, self.adapter.get_data_boxes, image_path)
        return boxes
