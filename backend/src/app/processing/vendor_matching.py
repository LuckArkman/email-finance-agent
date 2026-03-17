from thefuzz import fuzz, process
from typing import Optional, List, Dict, Tuple

class VendorMatcher:
    """
    Handles the normalization and string similarity (Fuzzy Matching) 
    between OCR-extracted vendor names and the canonical entities registered in the Database/ERP.
    Allows automated reconciliations despite typos ("Amazon" vs "Amazon Web Srvs").
    """
    def __init__(self, registered_vendors: List[str] = None):
        # Em produção, essa lista seria alimentada por uma Query no DB focando no Tenant_ID
        self.registered_vendors = registered_vendors if registered_vendors else [
            "Amazon Web Services", "Uber", "Apple", "Microsoft", "Google Ireland",
            "Contabilizei", "Ifood", "Airbnb", "Localiza"
        ]

    def fuzzy_match_vendor(self, extracted_vendor_name: str, threshold: int = 75) -> Optional[str]:
        """
        Calcula a Distância de Levenshtein (Token Sort) para associar as entidades.
        Retorna o Vendor Canonico mais provável, ou None se for um nome desconhecido/inédito.
        """
        if not extracted_vendor_name or not self.registered_vendors:
            return None
            
        # extractOne returns a tuple (best_match_string, score)
        best_match, score = process.extractOne(
            extracted_vendor_name, 
            self.registered_vendors, 
            scorer=fuzz.token_sort_ratio
        )
        
        if score >= threshold:
            print(f"Vendor Matched! OCR: '{extracted_vendor_name}' -> ERP: '{best_match}' (Score: {score}%)")
            return best_match
            
        print(f"Vendor NOT matched. Best was '{best_match}' with score {score}%. (Threshold: {threshold}%)")
        return None


class CategoryPredictor:
    """
    Heuristics/Statistical model to automatically map a matched Vendor into an 
    Accounting Chart of Accounts (Plano de Contas) Category.
    """
    def __init__(self):
        # Em produção, essas regras vêm de pesos ML ou Regras Customizadas do Usuário no PostgreSQL
        self.category_mapping: Dict[str, str] = {
            "Amazon Web Services": "Cloud Infrastructure",
            "Uber": "Travel & Transportation",
            "Ifood": "Meals & Entertainment",
            "Apple": "Software & Subscriptions",
            "Microsoft": "Software & Subscriptions",
            "Localiza": "Vehicle Expenses",
            "Airbnb": "Travel & Transportation",
        }

    def assign_default_category(self, canonical_vendor_name: str) -> str:
        """
        Atribui a categoria predefinida do Fornecedor para a fatura (Auto-Categorização).
        Caso o Fornecedor seja novo, cai no grupo generalista "Uncategorized".
        """
        if not canonical_vendor_name:
            return "Uncategorized"
            
        category = self.category_mapping.get(canonical_vendor_name)
        
        if category:
            print(f"Auto-categorized '{canonical_vendor_name}' as '{category}'")
            return category
            
        return "Uncategorized Expenses"
