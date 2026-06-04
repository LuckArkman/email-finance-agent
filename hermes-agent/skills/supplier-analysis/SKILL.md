---
name: supplier-analysis
description: >
  Use this skill to analyze data, history, and trends related to a specific supplier.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables: []
tags:
  - finance
  - suppliers
  - analysis
  - history
---

## Overview

This skill allows you to retrieve historical data about a specific supplier and identify trends such as average invoice value, total paid, or frequent payment delays.

## Procedure

### Step 1 — Identify the Supplier
Extract the name or VAT number of the supplier from the user's message.
Example: "Mostra-me o histórico da Vodafone." -> Supplier: Vodafone.

### Step 2 — Fetch Supplier Data
Use the MCP tools:
- `get_supplier_history(supplier_name)`: To fetch all recorded transactions, invoices, and payments for that supplier.

### Step 3 — Analyze and Summarize
Calculate useful metrics based on the history:
- Total amount billed by the supplier over time.
- Number of invoices.
- Average time to pay.
- Outstanding balance.

### Step 4 — Formulate Response
Provide the analysis to the user in a clear format.

Example:
"**Análise de Fornecedor: Vodafone**
- **Faturas Registadas:** 12
- **Total Gasto:** 1,250.00€
- **Saldo Pendente:** 0.00€
- **Média Mensal:** ~104.16€"
