import re
import logging

class ObfuscatorService:
    """
    Service for masking PII (Personally Identifiable Information) in logs and UI.
    Supports masking IBANs, Emails, and sensitive IDs.
    """
    
    @staticmethod
    def mask_email(email: str) -> str:
        if not email or "@" not in email:
            return email
        name, domain = email.split("@")
        return f"{name[0]}***@{domain}"

    @staticmethod
    def mask_iban(iban: str) -> str:
        if not iban:
            return iban
        # Show only first 4 and last 4
        return f"{iban[:4]}{'*' * (len(iban)-8)}{iban[-4:]}"

    @staticmethod
    def mask_dict(data: dict, keys_to_mask: list = ["password", "token", "iban", "email"]) -> dict:
        """Recursively mask sensitive keys in a dictionary."""
        masked = data.copy()
        for k, v in masked.items():
            if isinstance(v, dict):
                masked[k] = ObfuscatorService.mask_dict(v, keys_to_mask)
            elif k.lower() in keys_to_mask:
                if k.lower() == "email":
                    masked[k] = ObfuscatorService.mask_email(str(v))
                elif k.lower() == "iban":
                    masked[k] = ObfuscatorService.mask_iban(str(v))
                else:
                    masked[k] = "********"
        return masked

class SensitiveDataFilter(logging.Filter):
    """Logging filter to automatically mask sensitive data in log records."""
    def filter(self, record):
        if isinstance(record.msg, dict):
            record.msg = str(ObfuscatorService.mask_dict(record.msg))
        elif isinstance(record.msg, str):
            # Simple regex for generic email masking in strings
            record.msg = re.sub(r'[\w\.-]+@[\w\.-]+', '***@***.***', record.msg)
        return True
