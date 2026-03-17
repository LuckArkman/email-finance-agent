import os
import fitz  # PyMuPDF
from typing import Dict, Any, List, Optional

class PDFMetadataExtractor:
    """
    Handles extraction of native PDF metadata avoiding heavy OCR if unnecessary.
    """
    
    @staticmethod
    def get_pdf_metadata(filepath: str) -> Dict[str, Any]:
        """Extracts native metadata (CreationDate, Creator, Producer, Title) from a PDF file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")
            
        metadata = {}
        try:
            with fitz.open(filepath) as pdf:
                metadata = pdf.metadata
                metadata['page_count'] = len(pdf)
                metadata['is_encrypted'] = pdf.is_encrypted
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
            
        return metadata


class DocumentSplitter:
    """
    Responsible for breaking down large PDF documents into manageable chunks
    or even isolating the invoice pages from the long terms of service pages.
    """
    
    def __init__(self, output_dir: str = "/tmp/split_pdfs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_pdf_pages(self, filepath: str, start_page: int, end_page: int) -> Optional[str]:
        """
        Splits a specific range of pages into a new PDF document.
        Both start_page and end_page are 0-indexed.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")

        base_name = os.path.basename(filepath)
        name, ext = os.path.splitext(base_name)
        out_filename = f"{name}_p{start_page}_to_{end_page}{ext}"
        out_filepath = os.path.join(self.output_dir, out_filename)

        try:
            with fitz.open(filepath) as src_pdf:
                # Ensure bounds
                total_pages = len(src_pdf)
                start_page = max(0, min(start_page, total_pages - 1))
                end_page = max(start_page, min(end_page, total_pages - 1))

                doc_slice = fitz.open()
                doc_slice.insert_pdf(src_pdf, from_page=start_page, to_page=end_page)
                doc_slice.save(out_filepath)
                doc_slice.close()
                
            print(f"Split PDF saved to: {out_filepath}")
            return out_filepath
        except Exception as e:
            print(f"Error splitting PDF {filepath}: {e}")
            return None

    def convert_pdf_to_images(self, filepath: str, dpi: int = 300) -> List[str]:
        """
        Converts all pages of a PDF into high resolution PNG images for OCR algorithms.
        Returns a list of temporary file paths.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")

        base_name = os.path.basename(filepath)
        name, _ = os.path.splitext(base_name)
        img_paths = []

        try:
            with fitz.open(filepath) as pdf:
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    # We define a Matrix for scaling (DPI)
                    # Default DPI of PyMuPDF is 72. 300/72 = ~4.16
                    zoom = dpi / 72.0
                    mat = fitz.Matrix(zoom, zoom)
                    
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    out_img_name = f"{name}_page_{page_num + 1}.png"
                    out_img_path = os.path.join(self.output_dir, out_img_name)
                    
                    pix.save(out_img_path)
                    img_paths.append(out_img_path)
                    
            print(f"Converted {len(img_paths)} pages to images.")
            return img_paths
            
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
