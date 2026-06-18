---
name: whatsapp-intent-classifier
version: 1.0.0
description: >
  Classifica TODAS as mensagens recebidas via WhatsApp antes de qualquer processamento.
  Determina se a mensagem é: (1) um documento financeiro para OCR, (2) um comprovante
  de pagamento, ou (3) uma consulta textual ao agente. NUNCA processa uma mensagem
  como fatura sem passar por esta classificação primeiro.
triggers:
  - platform: whatsapp
    event: message_received
    priority: 10   # Executado ANTES de qualquer outra skill
---

# WhatsApp Intent Classifier

## Objetivo

Esta skill é a **primeira etapa** do pipeline WhatsApp. Classifica a intenção da
mensagem recebida e encaminha para o handler correcto.

**REGRA FUNDAMENTAL:** Nenhuma mensagem WhatsApp deve ser processada como fatura
sem antes passar por esta classificação.

## Etapa 1 — Identificar Tipo de Mensagem

Verifica o tipo de mensagem recebida:

- **Mensagem de texto simples** → vai para Etapa 2 (classificação de intenção textual)
- **Imagem (JPEG/PNG/WEBP)** → vai para Etapa 3 (classificação de documento visual)
- **PDF/Documento** → vai para Etapa 3 (classificação de documento)
- **Áudio/Vídeo** → responde que apenas aceita texto, imagens e PDFs
- **Sticker/GIF** → ignora silenciosamente

## Etapa 2 — Classificação de Intenção Textual

Para mensagens de texto, analisa o conteúdo e classifica em:

### QUERY — Consulta ao Agente
Exemplos de padrões que indicam consulta:
- "Qual é o total das faturas pendentes?"
- "Tenho faturas vencidas?"
- "Quando vence a fatura da [empresa]?"
- "Mostra-me as faturas deste mês"
- "Qual o meu saldo em aberto?"
- "Quais faturas estão em conciliação?"
- "Resumo financeiro"
- Qualquer pergunta ou solicitação de informação

**Acção:** Encaminhar directamente para o modelo LLM com contexto do banco vectorial.
O agente consulta o RAG e responde com base nos dados reais das faturas.

### UNKNOWN — Mensagem Não Reconhecida
Para mensagens que não se enquadram em nenhuma categoria.

**Acção:** Responder ao utilizador:
```
⚕️ *Hermes Finance*
──────
Olá! Posso ajudar-te com:
📄 *Documentos* — Envia uma foto ou PDF de uma fatura ou comprovante
🔍 *Consultas* — Pergunta sobre faturas, valores ou vencimentos

O que precisas?
```

## Etapa 3 — Classificação de Documento Visual (OCR Prévio)

Para imagens e PDFs, executa análise visual preliminar com `vision_analyze`:

### Prompt de Classificação Visual:
```
Analisa esta imagem/documento e classifica-o numa das seguintes categorias:

1. INVOICE — Se for uma fatura, boleto, nota fiscal ou conta a pagar
   Sinais: número de fatura, dados do fornecedor, valor a pagar, data de vencimento, NIF

2. PAYMENT_RECEIPT — Se for um comprovante de pagamento
   Sinais: "comprovante de pagamento", "transferência efectuada", "pago em", 
   carimbo de "PAGO", extracto bancário com pagamento, recibo

3. OTHER_FINANCIAL — Outro documento financeiro
   Sinais: extracto bancário, declaração fiscal, contrato

4. NON_FINANCIAL — Não é um documento financeiro
   Sinais: foto pessoal, screenshot, documento não financeiro

Responde APENAS com o JSON:
{
  "document_type": "INVOICE|PAYMENT_RECEIPT|OTHER_FINANCIAL|NON_FINANCIAL",
  "confidence": 0.0-1.0,
  "key_fields_detected": ["campo1", "campo2"],
  "reasoning": "explicação breve em português"
}
```

### Acção por Tipo Detectado:

**INVOICE (confiança ≥ 0.6):**
→ Activa skill `invoice-extraction` para processar a fatura
→ Responde: "Recebi o seu documento. A iniciar a tarefa de extração e OCR..."

**INVOICE (confiança < 0.6):**
→ Activa skill `invoice-extraction` com flag `low_confidence=true`
→ Responde: "⚠️ Documento pouco legível. A tentar extrair dados..."

**PAYMENT_RECEIPT:**
→ Activa skill `payment-receipt-matching`
→ Responde: "✅ Comprovante recebido! A fazer matching com faturas pendentes..."

**OTHER_FINANCIAL:**
→ Guarda documento com categoria `other_financial`
→ Responde: "📋 Documento financeiro registado no arquivo."

**NON_FINANCIAL:**
→ Não processa
→ Responde: "ℹ️ Este documento não parece ser uma fatura ou comprovante. Envia uma imagem de uma fatura ou comprovante de pagamento."

## Etapa 4 — Resposta de Erro / Fallback

Se `vision_analyze` falhar:
```
⚕️ *Hermes Finance*
──────
⚠️ Não consegui analisar a imagem. Certifica-te que:
• A imagem está bem iluminada e nítida
• O documento está completo e visível
• Não há reflexos ou sombras a cobrir o texto

Tenta novamente com uma foto melhor.
```

## Variáveis de Ambiente Necessárias

- `HERMES_DOTNET_GATEWAY_URL` — URL do Gateway .NET
- `HERMES_DOTNET_API_KEY` — Chave API do Gateway
- `WHATSAPP_ENABLED` — Deve ser "true"
