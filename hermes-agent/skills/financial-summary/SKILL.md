---
name: financial-summary
description: >
  Use this skill to generate financial summaries, calculate totals, and present business metrics to the user.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables: []
tags:
  - finance
  - metrics
  - reports
  - summary
---

## Overview

This skill allows you to summarize the user's financial status by calculating totals across invoices, identifying overdue payments, or generating specific time-range reports.

## Procedure

### Step 1 — Define the Scope
Understand the time frame and context the user is asking for:
- "Resumo do mês atual"
- "Qual o total pago este ano?"
- "Mostra o total de faturas por pagar"

### Step 2 — Fetch Data
Use the available MCP tools to get the raw data:
- `get_pending_invoices()`: To get all unpaid amounts.
- `search_database()` or specific backend metrics APIs to retrieve historical metrics.

### Step 3 — Calculate
Sum the values, categorize them by status (Paid vs Pending), and identify any critical anomalies (e.g., highly overdue invoices).

### Step 4 — Present the Summary
Respond with a clear, concise summary.

Example:
"**Resumo Financeiro - Junho 2026**
- Total Faturado: 10,500.00€
- Total Pendente: 3,200.00€
- Total Pago: 7,300.00€

**Atenção:** Existe 1 fatura expirada no valor de 450.00€."
