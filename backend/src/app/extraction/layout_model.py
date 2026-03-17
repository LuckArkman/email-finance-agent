import os
import torch
from typing import Dict, Any, List, Tuple
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image

class SpatialTreeGenerator:
    """
    Helper object to reconstruct visual bounding boxes 
    into a structured hierarchical tree.
    """
    @staticmethod
    def combine_boxes_and_text(words: List[str], boxes: List[List[int]], predictions: List[str]) -> Dict[str, Any]:
        """
        Geração de árvore estrutural semântica do documento.
        Links recognized words, their physical layout blocks, and the sequence labeling 
        prediction (like HEADER, DATE, TOTAL).
        """
        document_tree = {
            "headers": [],
            "line_items": [],
            "summaries": [],
            "other": []
        }
        
        # A rudimentary post-processing of the spatial elements to cluster them
        for word, box, label in zip(words, boxes, predictions):
            element = {"text": word, "bbox": box, "label": label}
            
            # This is a mocked layout routing based on standard BIO tagging 
            # (assuming model outputs tags like B-HEADER, I-HEADER, B-ANSWER etc)
            if "HEADER" in label.upper() or "TITLE" in label.upper() or "COMPANY" in label.upper():
                document_tree["headers"].append(element)
            elif "ITEM" in label.upper() or "DESC" in label.upper():
                document_tree["line_items"].append(element)
            elif "TOTAL" in label.upper() or "TAX" in label.upper() or "DATE" in label.upper():
                document_tree["summaries"].append(element)
            else:
                if word.strip():  # Skip empty characters
                    document_tree["other"].append(element)
                    
        return document_tree

class LayoutModelPipeline:
    """
    Orchestrates the open-source HuggingFace Transformers logic 
    dedicated to the LayoutLMv3 Document Understanding Model.
    """
    def __init__(self, model_name: str = "microsoft/layoutlmv3-base"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.processor = None
        self.model = None

    def load_layout_model(self) -> None:
        """
        Loads the massive torch weights into VRAM. 
        Should only be called once globally for the worker to avoid memory leaks.
        """
        if self.processor is None or self.model is None:
            print(f"Loading LayoutLMv3 model: {self.model_name} onto {self.device}")
            # The processor bridges images/text -> tensors
            self.processor = LayoutLMv3Processor.from_pretrained(self.model_name, apply_ocr=True)
            # The token classification architecture defines spatial understanding
            self.model = LayoutLMv3ForTokenClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval() # Setting for inference
            print("LayoutLMv3 successfully loaded.")

    def predict_visual_elements(self, image_path: str) -> Dict[str, Any]:
        """
        Receives an image, performs multimodal inference 
        (combining Image visual features + OCR embedded text).
        """
        if not self.model or not self.processor:
            self.load_layout_model()
            
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        try:
            image = Image.open(image_path).convert("RGB")
            
            # Since apply_ocr=True, processor internally calls Tesseract to get bounding boxes 
            # and words, then passes them to the LayoutLM architecture.
            encoding = self.processor(image, return_tensors="pt")
            
            # Move to target device
            pixel_values = encoding['pixel_values'].to(self.device)
            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)
            bbox = encoding['bbox'].to(self.device)
            
            # Perform inference
            with torch.no_grad():
                outputs = self.model(
                    input_ids=input_ids,
                    bbox=bbox,
                    attention_mask=attention_mask,
                    pixel_values=pixel_values
                )
            
            # Logits correspond to probability of each tag
            logits = outputs.logits
            predictions_idx = logits.argmax(-1).squeeze().tolist()
            
            # In a trained model, id2label maps integers to BIO tags like "B-TOTAL"
            # Here we map to default label strings if untrained, or use model dict
            labels = [self.model.config.id2label[p] for p in predictions_idx]
            
            # Reconstruct original words based on input_ids via tokenizer
            words = self.processor.tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
            original_bboxes = bbox.squeeze().tolist()
            
            # Re-assemble the fragmented spatial logic back into a JSON
            semantic_tree = SpatialTreeGenerator.combine_boxes_and_text(words, original_bboxes, labels)
            
            return {
                "status": "success",
                "extracted_tree": semantic_tree
            }
            
        except Exception as e:
            print(f"LayoutLM Inference Error on {image_path}: {e}")
            return {"status": "error", "message": str(e), "extracted_tree": {}}
