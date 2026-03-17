import numpy as np
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ConfidenceMetrics(BaseModel):
    """
    Data Transfer Object holding the granular probability calculations 
    for the AI/OCR predictions across key financial fields.
    """
    ocr_average_confidence: float = Field(default=100.0, description="Average OCR confidence (0-100)")
    llm_certainty_score: float = Field(default=100.0, description="Log-likelihood conversion to 0-100 scale")
    overall_confidence: float = Field(default=100.0, description="Weighted average of all available confidence streams")
    needs_manual_review: bool = Field(default=False, description="Flag indicating if human intervention is required")
    low_confidence_fields: List[str] = Field(default_factory=list, description="Specific fields that failed the threshold")


class ConfidenceEvaluator:
    """
    Calculus engine applying heuristic weighting to assess if an invoice
    was understood perfectly or if it needs to be flagged for an Accounts Payable
    analyst to review manually.
    """
    
    # Tolerance constraint - any average score below this needs human eyes
    ACCEPTABLE_THRESHOLD = 90.0

    @staticmethod
    def calculate_overall_confidence(
        ocr_boxes: List[Dict[str, Any]], 
        llm_extracted_data: Dict[str, Any],
        aws_textract_confidence: float = 0.0
    ) -> ConfidenceMetrics:
        """
        Algoritmo para cruzar a probabilidade e atribuir score final de 0-100%.
        
        Args:
            ocr_boxes: List of dictionaries predicting words and their OCR 'conf' (0-100) from Tesseract/EasyOCR.
            llm_extracted_data: The JSON output from Langchain/GPT-4.
            aws_textract_confidence: The AWS Textract confidence (if applicable).
        """
        metrics = ConfidenceMetrics()
        weights = []
        confidences = []

        # 1. Evaluate pure visual OCR confidence
        if ocr_boxes:
            valid_confs = [box.get('conf', 0) for box in ocr_boxes if isinstance(box.get('conf'), (int, float)) and box.get('conf', -1) > 0]
            if valid_confs:
                metrics.ocr_average_confidence = float(np.mean(valid_confs))
                confidences.append(metrics.ocr_average_confidence)
                weights.append(0.4) # OCR accounts for 40% of the decision
        elif aws_textract_confidence > 0:
            metrics.ocr_average_confidence = aws_textract_confidence
            confidences.append(aws_textract_confidence)
            weights.append(0.5) # Cloud OCR carries more weight

        # 2. Heuristic LLM Log-Likelihood mock / Penalty evaluation
        # Currently, OpenAI chat completion doesn't expose easy token logprobs without specific configs,
        # so we calculate a semantic penalty based on missing critical fields.
        llm_penalty = 0.0
        low_fields = []
        
        critical_fields = ['total_amount', 'issue_date', 'vendor_name']
        for field in critical_fields:
            if not llm_extracted_data.get(field):
                llm_penalty += 15.0 # High penalty for missing total or vendor
                low_fields.append(field)
                
        metrics.low_confidence_fields = low_fields
        metrics.llm_certainty_score = max(0.0, 100.0 - llm_penalty)
        
        # Add LLM metric
        confidences.append(metrics.llm_certainty_score)
        weights.append(0.6) # Semantic intelligence accounts for 60% of the structural confidence

        # 3. Final weighted Average
        if confidences:
            metrics.overall_confidence = float(np.average(confidences, weights=weights))
        else:
            metrics.overall_confidence = 0.0
            
        # 4. Trigger review flags
        metrics = ConfidenceEvaluator.flag_low_metrics(metrics)
        
        return metrics

    @staticmethod
    def flag_low_metrics(metrics: ConfidenceMetrics) -> ConfidenceMetrics:
        """
        Se <90%, flag: needs_manual_review = True.
        """
        # Hard threshold fallback
        if metrics.overall_confidence < ConfidenceEvaluator.ACCEPTABLE_THRESHOLD:
            metrics.needs_manual_review = True
            print(f"REVIEW REQUIRED: Confidence Score [{metrics.overall_confidence:.2f}%] is below {ConfidenceEvaluator.ACCEPTABLE_THRESHOLD}%.")
        
        # Absolute trigger: If the LLM failed to extract the total amount, it MUST be reviewed
        if "total_amount" in metrics.low_confidence_fields or "vendor_name" in metrics.low_confidence_fields:
            metrics.needs_manual_review = True
            print(f"REVIEW REQUIRED: Critical fields missing: {metrics.low_confidence_fields}")
            
        return metrics
