from typing import Dict, Any, Tuple
import pandas as pd

class ThreeWayMatchRule:
    """
    Business Rules constraints for Reconciliations.
    """
    def __init__(self, tolerance_cents: int = 5):
        # Allow differences in cents (e.g., due to rounding discrepancies in ERPs vs PDFs)
        self.tolerance_val = tolerance_cents / 100.0

    def check_tolerance(self, amount1: float, amount2: float) -> bool:
        """
        Validação matemática de desvios e tolerâncias (Centavos).
        """
        return abs(amount1 - amount2) <= self.tolerance_val


class ReconciliationEngine:
    """
    Three-Way Matching Engine:
    Validates if PO (Purchase Order) == Invoice (OCR) == Receipt (Bank Payment)
    """
    def __init__(self):
        self.rules = ThreeWayMatchRule(tolerance_cents=10) # 10 cents tolerance

    def compare_po_with_invoice(self, po_data: Dict[str, Any], invoice_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Algoritmo analítico de reconciliação cruzando os documentos 
        focando em Purchase Order Number e Total Amounts.
        """
        # 1. Matching Entities directly
        invoice_po_number = str(invoice_data.get("po_number", "")).strip()
        system_po_number = str(po_data.get("po_number", "")).strip()
        
        if not invoice_po_number or not system_po_number:
            return False, "Missing PO Number on one of the documents."
            
        if invoice_po_number != system_po_number:
            return False, f"PO Mismatch: Invoice says {invoice_po_number}, System says {system_po_number}"

        # 2. Matching Amounts
        invoice_total = float(invoice_data.get("total_amount", 0.0))
        po_total = float(po_data.get("total_amount", 0.0))
        
        if not self.rules.check_tolerance(invoice_total, po_total):
            return False, f"Amount Discrepancy: Invoice Total {invoice_total} != PO Total {po_total}"
            
        # Optional: Checking Vendor alignment using our previous NLP
        # We assume vendor was already matched in VendorMatcher step.

        return True, "Perfect Match"
