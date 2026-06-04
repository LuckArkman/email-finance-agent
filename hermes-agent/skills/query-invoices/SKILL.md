---
name: query-invoices
description: >
  Use this skill to answer questions about invoices, pending payments, payment proofs, and historical financial data located in the user's email or database.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables: []
tags:
  - finance
  - query
  - invoices
  - reports
---

## Overview

This skill allows you to retrieve information about invoices and proofs of payment. You have access to the `.NET` backend via MCP tools which you can call to query the database.

## Procedure

### Step 1 — Identify the Intent
Determine what the user is asking. For example:
- "Quais são as faturas pendentes?"
- "A fatura da EDP já foi paga?"
- "Mostra-me o histórico do fornecedor MEO."

### Step 2 — Query the Backend
Use the available MCP tools to fetch the required data:
- `get_pending_invoices()`: Retrieves a list of all invoices currently marked as pending.
- `get_supplier_history(supplier_name)`: Retrieves historical invoices and payment statuses for a given supplier.
- `search_database(query)`: If available, performs a semantic search across all indexed invoices and payment proofs.

### Step 3 — Format the Response
Present the data clearly to the user. Use Markdown tables, bullet points, and concise summaries. If a proof of payment is requested and found, mention the date of payment and the reference.

Example response:
"Encontrei 3 faturas pendentes:
1. **EDP Comercial** - 150.00€ (Vence a 2026-06-10)
2. **MEO** - 45.50€ (Vence a 2026-06-15)"
