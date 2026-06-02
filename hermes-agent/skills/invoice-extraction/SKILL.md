---
name: invoice-extraction
description: >
  Use this skill whenever an email contains an attached or linked financial document
  such as an invoice, receipt, purchase order, or billing statement (PDF, PNG, JPG,
  or plain text). Extracts all structured financial data and forwards it to the
  Hermes .NET processing pipeline for validation and reconciliation.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables:
  - HERMES_DOTNET_GATEWAY_URL
  - HERMES_DOTNET_API_KEY
tags:
  - finance
  - invoices
  - extraction
  - b2b
---

## Overview

This skill transforms an unstructured financial document (email attachment or inline
content) into a validated JSON payload and delivers it to the Hermes .NET 9
microservice pipeline for mathematical reconciliation, storage, and B2B export.

## Procedure

### Step 1 — Identify the Document
- Check the email for PDF, PNG, JPG, or TIFF attachments.
- If there is a link to a document in the email body, use `web_extract` to fetch it.
- If the email body itself contains an invoice (plain text / HTML table), parse it directly.
- If no document is found, reply to the sender asking for the attachment and STOP.

### Step 2 — Read the Document Content
- For **images or scanned PDFs**: use `vision_analyze` to perform OCR and extract text.
- For **text-based PDFs**: use the `read_file` tool or `web_extract` if it is a URL.
- For **multi-page PDFs**: process ALL pages before extracting totals.
- Collect the raw text in its entirety before proceeding.

### Step 3 — Extract Structured Data
From the raw text, build a JSON object with EXACTLY these fields:

```json
{
  "supplier_name": "string or null",
  "supplier_tax_id": "string or null",
  "supplier_address": "string or null",
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "purchase_order_ref": "string or null",
  "line_items": [
    {
      "description": "string",
      "quantity": 0.0,
      "unit_price": 0.0,
      "total": 0.0
    }
  ],
  "subtotal": 0.0,
  "tax_rate": 0.0,
  "tax_amount": 0.0,
  "total_amount": 0.0,
  "currency": "EUR",
  "payment_method": "string or null",
  "bank_iban": "string or null",
  "notes": "string or null",
  "source_email": "sender@domain.com",
  "extraction_timestamp": "ISO-8601 UTC"
}
```

**Rules — NEVER break these:**
- Do NOT invent data. If a field is absent from the document, set it to `null`.
- Do NOT guess numeric values. Copy them exactly as printed.
- Dates MUST be in `YYYY-MM-DD` format. Convert if the document uses DD/MM/YYYY or MM-DD-YYYY.
- Amounts MUST be plain floats (no currency symbols, no thousands separators).
- `currency` must be the 3-letter ISO 4217 code (EUR, USD, GBP, BRL...).

### Step 4 — Validate Mathematics
Run the following checks:
1. Sum all `line_items[].total` → compare to `subtotal`.
   - If difference > 0.02 → set `validation_status: "LINE_ITEMS_DISCREPANCY"`
2. Calculate `subtotal * tax_rate / 100` → compare to `tax_amount`.
   - If difference > 0.02 → set `validation_status: "TAX_DISCREPANCY"`
3. Calculate `subtotal + tax_amount` → compare to `total_amount`.
   - If difference > 0.02 → set `validation_status: "TOTAL_DISCREPANCY"`
4. If all checks pass → set `validation_status: "OK"`

Add `validation_status` and `validation_notes` (describe discrepancy if any) to the JSON.

### Step 5 — POST to Hermes .NET Gateway
Use `execute_code` to deliver the payload:

```python
import os, httpx, json

payload = { ... }  # the JSON built in Steps 3 & 4

gateway_url = os.environ["HERMES_DOTNET_GATEWAY_URL"]
api_key = os.environ["HERMES_DOTNET_API_KEY"]

response = httpx.post(
    f"{gateway_url}/api/hermes/invoices/ingest",
    json=payload,
    headers={
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    },
    timeout=30.0
)
response.raise_for_status()
result = response.json()
print(f"Invoice accepted. Tracking ID: {result.get('trackingId')}")
```

### Step 6 — Reply to Sender
Send a brief, professional reply to the original email confirming receipt:

> "Dear [Supplier Name], thank you for invoice [invoice_number].
> We have received and registered your document. Our team will process
> it within [due_date or '3 business days']. Reference: [trackingId]."

## Error Handling

| Error | Action |
|---|---|
| Document unreadable / corrupt | Reply asking for a re-send. Log the issue. |
| Missing mandatory fields (`invoice_number`, `total_amount`) | Set `validation_status: "INCOMPLETE"` and still POST — let .NET decide |
| Network error posting to .NET | Retry twice with 5s delay. If still failing, save to memory and alert via email. |
| `.NET` returns non-2xx | Log the response body. Do NOT reply to sender until resolved. |

## Pitfalls

- Scanned PDFs may have OCR errors in numbers — double-check totals.
- Some suppliers omit tax lines (0% VAT) — `tax_amount` should be 0.0, NOT null.
- Multi-currency invoices: use the currency of the `total_amount` line.
- Proforma invoices are NOT payable — set `notes: "PROFORMA"` and flag accordingly.
- Credit notes have NEGATIVE totals — preserve the negative sign.
