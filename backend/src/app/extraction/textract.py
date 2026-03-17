import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.config import BaseAPIConfig

class ExpenseDTO(BaseModel):
    """
    Standard DTO for an Invoice/Receipt outputted by Advanced Cloud Providers 
    (Like AWS Textract analyze_expense).
    """
    vendor_name: Optional[str] = None
    invoice_receipt_id: Optional[str] = None
    invoice_receipt_date: Optional[str] = None
    total: float = 0.0
    subtotal: float = 0.0
    tax: float = 0.0
    confidence_score: float = 0.0
    line_items: List[Dict[str, Any]] = []
    raw_json_response: Dict[str, Any]


class ExpenseParserAWS:
    """
    Helper to navigate the extremely complex blocks returned by AWS Textract 
    analyze_expense and map to our simplified internal ExpenseDTO.
    """
    @staticmethod
    def map_aws_blocks_to_dto(raw_response: Dict[str, Any]) -> ExpenseDTO:
        dto = ExpenseDTO(raw_json_response=raw_response)
        
        expense_documents = raw_response.get("ExpenseDocuments", [])
        if not expense_documents:
            return dto

        # Iterate only through the first document block for now
        doc = expense_documents[0]
        
        # Parse Summary Fields (Total, Tax, VendorName)
        summary_fields = doc.get("SummaryFields", [])
        
        total_confidence = 0.0
        fields_counted = 0
        
        # Basic mapping dictionary for Textract standard types
        for field in summary_fields:
            field_type = field.get("Type", {}).get("Text")
            value_obj = field.get("ValueDetection", {})
            value_text = value_obj.get("Text")
            confidence = value_obj.get("Confidence", 0.0)
            
            if field_type and value_text:
                total_confidence += confidence
                fields_counted += 1
                
                # Sanitize numeric fields aggressively
                def _parse_float(val: str) -> float:
                    try:
                        # removes currency symbols and spaces
                        clean_val = val.replace("$", "").replace("R", "").replace(" ", "").replace(",", ".")
                        return float(clean_val)
                    except ValueError:
                        return 0.0
                        
                if field_type == "VENDOR_NAME":
                    dto.vendor_name = value_text
                elif field_type == "INVOICE_RECEIPT_ID":
                    dto.invoice_receipt_id = value_text
                elif field_type == "INVOICE_RECEIPT_DATE":
                    dto.invoice_receipt_date = value_text
                elif field_type in ["TOTAL", "AMOUNT_DUE"]:
                    dto.total = _parse_float(value_text)
                elif field_type == "SUBTOTAL":
                    dto.subtotal = _parse_float(value_text)
                elif field_type == "TAX":
                    dto.tax = _parse_float(value_text)

        # Basic averaging confidence of detected summary fields
        if fields_counted > 0:
            dto.confidence_score = total_confidence / fields_counted
            
        return dto


class AWSTextractAdapter:
    """
    Integrates AWS Textract specifically targeting the AnalyzeExpense API
    which uses deep machine learning customized naturally for invoices and receipts.
    """
    def __init__(self):
        settings = BaseAPIConfig.get_settings()
        self.region = settings.aws_region
        
        # Using boto3 synchronous client. For real-time high-throughput, you'd wrap
        # this in an aioboto3 async context if needed, but we use ThreadPools in celery usually.
        self.client = boto3.client(
            'textract',
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
            region_name=self.region,
            config=boto3.session.Config(signature_version='s3v4')
        )

    def call_analyze_document(self, bucket_name: str, document_s3_key: str) -> Optional[ExpenseDTO]:
        """
        Calls Textract to process an invoice already uploaded to the S3 Bucket.
        Highly recommended flow over pushing bytes via network.
        """
        try:
            print(f"Calling AWS Textract AnalyzeExpense for s3://{bucket_name}/{document_s3_key}")
            response = self.client.analyze_expense(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': document_s3_key
                    }
                }
            )
            
            # Map the massive json response down
            return ExpenseParserAWS.map_aws_blocks_to_dto(response)
            
        except ClientError as e:
            print(f"Boto3 ClientError on Textract: {e}")
            return None
        except Exception as e:
            print(f"Generic error on Textract: {e}")
            return None
