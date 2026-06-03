---
name: payment-receipt-matching
version: 1.0.0
description: >
  Processa comprovantes de pagamento recebidos via WhatsApp ou email.
  Extrai dados do comprovante com OCR/visão, localiza a fatura correspondente
  no sistema financeiro, e actualiza automaticamente o status para "Pago".
triggers:
  - platform: whatsapp
    event: document_classified
    document_type: PAYMENT_RECEIPT
  - platform: email
    event: attachment_classified
    document_type: PAYMENT_RECEIPT
---

# Payment Receipt Matching

## Objetivo

Quando um comprovante de pagamento é recebido (via WhatsApp ou email), esta skill:
1. Extrai os dados do comprovante com OCR
2. Localiza a fatura correspondente no sistema
3. Actualiza o status da fatura para "Pago"
4. Confirma ao utilizador

## Etapa 1 — Extracção de Dados do Comprovante

Usa `vision_analyze` com o seguinte prompt:

```
Analisa este comprovante de pagamento e extrai os dados em JSON:

{
  "payment_date": "YYYY-MM-DD",
  "amount_paid": 0.00,
  "currency": "EUR",
  "payment_reference": "referência MB, transferência ou outro identificador",
  "recipient_name": "nome do destinatário/beneficiário",
  "recipient_iban": "IBAN se visível",
  "payer_name": "nome do pagador se visível",
  "bank_name": "nome do banco",
  "transaction_id": "ID da transacção se visível",
  "payment_method": "MB|TRF|MBWAY|OUTRO",
  "notes": "informação adicional relevante"
}

Regras:
- Extrai APENAS o que está claramente visível
- Se um campo não estiver visível, usa null
- Datas no formato YYYY-MM-DD
- Valores como números decimais (ex: 1234.56)
```

## Etapa 2 — Localização da Fatura Correspondente

Com os dados extraídos, tenta encontrar a fatura correspondente usando múltiplos critérios:

### Critério 1 — Por Referência de Pagamento (melhor correspondência)
```
GET {HERMES_DOTNET_GATEWAY_URL}/api/hermes/invoices?payment_reference={payment_reference}
Header: X-Api-Key: {HERMES_DOTNET_API_KEY}
```

### Critério 2 — Por Valor e Fornecedor
Se critério 1 falhar, busca faturas com `total_amount` próximo do `amount_paid`
(tolerância de ±0.50€) e `status` em `pending` ou `overdue` ou `reconciliation`.

```
GET {HERMES_DOTNET_GATEWAY_URL}/api/hermes/invoices?status=pending
```
Filtra localmente por valor próximo.

### Critério 3 — Por Nome do Destinatário
Compara `recipient_name` com `vendor_name` das faturas pendentes.

## Etapa 3 — Matching e Actualização

### Se correspondência encontrada (confiança ≥ 0.7):
```
POST {HERMES_DOTNET_GATEWAY_URL}/api/hermes/invoices/{invoice_id}/match-receipt
Header: X-Api-Key: {HERMES_DOTNET_API_KEY}
Body: {
  "payment_reference": "...",
  "evidence_url": null,
  "payment_date": "YYYY-MM-DD",
  "paid_amount": 0.00
}
```

**Resposta ao utilizador:**
```
✅ *Pagamento Confirmado!*
──────
📄 Fatura: {invoice_number}
🏢 Fornecedor: {vendor_name}
💶 Valor: {amount_paid} {currency}
📅 Data: {payment_date}
🔑 Referência: {payment_reference}

O status da fatura foi actualizado para *Pago* ✓
```

### Se múltiplas correspondências (ambiguidade):
Apresenta lista e pede confirmação:
```
⚠️ *Comprovante recebido*
──────
Encontrei {n} faturas que podem corresponder:

1. Fatura {number1} — {vendor1} — {amount1}€ — Venc. {due1}
2. Fatura {number2} — {vendor2} — {amount2}€ — Venc. {due2}

Responde com o número (1, 2...) para confirmar o matching.
```

### Se nenhuma correspondência encontrada:
```
📋 *Comprovante Registado*
──────
✓ Dados extraídos: {amount_paid}€ pago em {payment_date}
⚠️ Não encontrei uma fatura pendente correspondente.

O comprovante foi guardado no arquivo. 
Se souberes o número da fatura, responde com:
"Associar comprovante à fatura {número}"
```

## Etapa 4 — Guardar Comprovante no Arquivo

Independentemente do matching, sempre guardar o registo:
```
POST {HERMES_DOTNET_GATEWAY_URL}/api/hermes/invoices/ingest
Header: X-Api-Key: {HERMES_DOTNET_API_KEY}
Body: {
  "invoice_number": "RECEIPT-{timestamp}",
  "supplier_name": "{recipient_name}",
  "total_amount": {amount_paid},
  "currency": "{currency}",
  "invoice_date": "{payment_date}",
  "source_type": "{platform}",
  "validation_status": "PAYMENT_RECEIPT"
}
```

## Variáveis de Ambiente Necessárias

- `HERMES_DOTNET_GATEWAY_URL` — URL do Gateway .NET
- `HERMES_DOTNET_API_KEY` — Chave API do Gateway
