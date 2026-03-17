import os
import magic
import base64
from typing import List, Dict, Any

class FileSanitizer:
    """
    Handling the cleansing of extracted attachments.
    Eliminates tracking pixels, linked in icons, or completely irrelevant small blobs
    that would just spam the OCR endpoints.
    """
    MIN_SIZE_BYTES = 5 * 1024 # Drop anything smaller than 5KB (usually signatures/icons)

    @staticmethod
    def identify_mime_type(file_bytes: bytes) -> str:
        """Identify using magic bytes, safer than using extension headers."""
        return magic.from_buffer(file_bytes, mime=True)
    
    @staticmethod
    def filter_tracking_pixels(file_bytes: bytes) -> bool:
        """Returns True if the file looks relevant, False if it resembles a tracking payload/icon."""
        if len(file_bytes) < FileSanitizer.MIN_SIZE_BYTES:
            return False
        
        mime = FileSanitizer.identify_mime_type(file_bytes)
        allowed_mimes = ["application/pdf", "image/jpeg", "image/png", "image/tiff"]
        
        if mime not in allowed_mimes:
            return False
            
        return True


class AttachmentParser:
    """
    Extracts raw files from multi-part MIME structured strings (like those obtained from email).
    """

    def __init__(self, temp_storage_path: str = "/tmp/invoice_attachments"):
        self.temp_storage_path = temp_storage_path
        os.makedirs(self.temp_storage_path, exist_ok=True)

    def extract_attachments(self, email_parts: List[Any], message_id: str) -> List[str]:
        """
        Parses over standard email message walk() parts and extracts valid attachments.
        Returns a list of local temporary file paths.
        """
        extracted_paths = []

        for part in email_parts:
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()
            if not file_name:
                continue

            raw_payload = part.get_payload(decode=True)
            if not raw_payload:
                continue

            # Pass through our Sanitizer rules
            if not FileSanitizer.filter_tracking_pixels(raw_payload):
                print(f"Skipping attachment {file_name}: Failed sanitizer check (Too small or invalid mime type).")
                continue

            safename = f"{message_id}_{file_name.replace(' ', '_')}"
            local_path = os.path.join(self.temp_storage_path, safename)
            
            with open(local_path, "wb") as f:
                f.write(raw_payload)
            
            extracted_paths.append(local_path)
            print(f"Attachment stored temporarily at: {local_path}")

        return extracted_paths
