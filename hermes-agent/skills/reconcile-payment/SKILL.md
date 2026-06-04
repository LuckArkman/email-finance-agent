---
name: reconcile-payment
description: >
  Use this skill when the user asks to reconcile a specific payment, register a proof of payment, or mark an invoice as paid.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables: []
tags:
  - finance
  - reconciliation
  - payments
---

## Overview

This skill helps the user reconcile payments against invoices. When the user provides a proof of payment (like an attachment or transaction ID), you should link it to the corresponding invoice.

## Procedure

### Step 1 — Identify the Invoice and Payment
Extract the payment amount, date, and any reference number from the user's message or uploaded proof of payment. Identify which pending invoice this payment corresponds to.

### Step 2 — Execute Reconciliation
Use the MCP tools:
- If automatically matching: `trigger_auto_reconciliation()` (if exposed via MCP).
- If manually matching: `update_invoice_status(invoice_id, status="paid")` (assuming such a tool is exposed).

### Step 3 — Confirm
Reply to the user confirming that the payment has been successfully reconciled against the invoice, citing the new status and remaining balance (if any).
