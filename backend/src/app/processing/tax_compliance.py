import re
from typing import Optional, Dict, Any

class TaxBracketValidator:
    """
    Validates tax calculations to ensure compliance and avoid financial ingestion errors.
    """
    
    @staticmethod
    def verify_tax_math(subtotal: float, tax_amount: float, total: float, tolerance: float = 0.05) -> bool:
        """
        Extração percentual vs Bruto/Líquido matematicamente verificado no backend.
        Cross-checks if Subtotal + Tax == Total within an acceptable rounding tolerance.
        """
        expected_total = subtotal + tax_amount
        return abs(expected_total - total) <= tolerance


class TaxEngine:
    """
    Extracts and normalizes Tax identification numbers (CNPJ, CPF, VAT/VIES, EIN)
    from unstructured text for strict compliance tracking.
    """
    
    @staticmethod
    def extract_vat_number(ocr_text: str) -> Optional[str]:
        """
        Regex avançada para padrões VIES/CNPJ/EIN dependendo da localidade.
        """
        if not ocr_text:
            return None

        # 1. Brazil: CNPJ (14 digits, typically format XX.XXX.XXX/XXXX-XX)
        cnpj_pattern = r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'
        cnpjs = re.findall(cnpj_pattern, ocr_text)
        if cnpjs:
            return cnpjs[0] # Return the first valid CNPJ found

        # 2. Brazil: CPF (11 digits, typically format XXX.XXX.XXX-XX)
        cpf_pattern = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
        cpfs = re.findall(cpf_pattern, ocr_text)
        if cpfs:
            return cpfs[0]
            
        # 3. European VAT (VIES) Pattern: Starts with 2 letters country code, followed by 2-13 alphanumerics
        # Example: GB123456789, DE123456789, FR12345678901
        eu_vat_pattern = r'\b[A-Z]{2}[0-9A-Z]{2,13}\b'
        vats = re.findall(eu_vat_pattern, ocr_text)
        
        # Filter false positives out (we don't want standard capitalized words)
        valid_eu_prefixes = [
            "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", 
            "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", 
            "NL", "PL", "PT", "RO", "SE", "SI", "SK", "GB"
        ]
        
        for vat in vats:
            if vat[:2] in valid_eu_prefixes and any(char.isdigit() for char in vat):
                return vat
                
        # 4. US EIN (Employer Identification Number) format XX-XXXXXXX
        ein_pattern = r'\b\d{2}-\d{7}\b'
        eins = re.findall(ein_pattern, ocr_text)
        if eins:
            return eins[0]

        return None
