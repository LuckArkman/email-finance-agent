import httpx
from typing import Dict, Any, Optional
from app.config import BaseAPIConfig

class QuickBooksConnector:
    """
    Handles outbound synchronization of finalized invoices into QuickBooks Online.
    Converts internal InvoiceRecord data into QuickBooks Bill/Invoice entities.
    """
    def __init__(self):
        self.settings = BaseAPIConfig.get_settings()
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"
        # In production, these would be retrieved from a secure Token Store/Vault per Tenant
        self.access_token: Optional[str] = None

    async def sync_invoice_outbound(self, tenant_id: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Pushes a finalized invoice (Bill) to the user's QuickBooks account.
        """
        if not self.access_token:
            print(f"Skipping QuickBooks sync for tenant {tenant_id}: No Auth Token.")
            return False

        quickbooks_payload = {
            "VendorRef": {
                "name": invoice_data.get("vendor_name")
            },
            "Line": [
                {
                    "Amount": invoice_data.get("total_amount"),
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "name": "Accounts Payable"
                        }
                    }
                }
            ],
            "TxnDate": invoice_data.get("issue_date"),
            "DueDate": invoice_data.get("due_date")
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{tenant_id}/bill",
                    json=quickbooks_payload,
                    headers={"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"}
                )
                if response.status_code in [200, 201]:
                    print(f"Successfully synced Invoice to QuickBooks for tenant {tenant_id}")
                    return True
                else:
                    print(f"QuickBooks Sync Failed: {response.text}")
                    return False
            except Exception as e:
                print(f"Error connecting to QuickBooks: {e}")
                return False

class PlaidAPIClient:
    """
    Client to interact with Plaid API for Bank Statement verification 
    and transaction reconciliation.
    """
    def __init__(self):
        self.base_url = "https://production.plaid.com"
        self.client_id = "mock_client_id"
        self.secret = "mock_secret"

    async def verify_bank_statement(self, access_token: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetches bank transactions to verify if a payment was actually cleared.
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "client_id": self.client_id,
                "secret": self.secret,
                "access_token": access_token,
                "start_date": start_date,
                "end_date": end_date
            }
            try:
                response = await client.post(f"{self.base_url}/transactions/get", json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Plaid API Error: {e.response.text}")
                return {"error": "Failed to fetch bank data"}
            except Exception as e:
                print(f"Error connecting to Plaid: {e}")
                return {"error": "Connection failed"}
