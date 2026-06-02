Hermes Agent (Nous Research) — Setup Guide
==========================================

Este ficheiro documenta como instalar, configurar e correr o Hermes Agent
como substituto do backend Python para processamento de faturas por email.

## Pré-requisitos

- Linux, macOS, ou WSL2 (Windows nativo não suporta execute_code)
- Python 3.11+
- Ollama instalado localmente (ou credenciais do Nous Portal)
- httpx (`pip install httpx`) para os hooks de integração

## Instalação

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

## Configuração

1. Copiar o ficheiro de configuração:
```bash
cp hermes-agent/config.yaml ~/.hermes/config.yaml
```

2. Copiar as Skills:
```bash
cp -r hermes-agent/skills/invoice-extraction ~/.hermes/skills/
```

3. Copiar os Hooks:
```bash
cp -r hermes-agent/hooks/post-extraction ~/.hermes/hooks/
```

4. Configurar variáveis de ambiente (criar ficheiro .env):
```bash
cat > ~/.hermes/.env << EOF
# Email da caixa de faturas
FINANCE_EMAIL_ADDRESS=faturas@empresa.com
FINANCE_EMAIL_APP_PASSWORD=<google-app-password>
FINANCE_IMAP_HOST=imap.gmail.com
FINANCE_SMTP_HOST=smtp.gmail.com

# Hermes .NET Gateway
HERMES_DOTNET_GATEWAY_URL=http://localhost:5000
HERMES_DOTNET_API_KEY=<chave-secreta-partilhada>

# API Server do Hermes Agent
HERMES_API_SERVER_KEY=<chave-para-o-dotnet-consultar>

# MCP Server
HERMES_MCP_KEY=<chave-mcp>

# .NET Gateway lê esta variável
HERMES_AGENT_API_KEY=<chave-secreta-partilhada>
EOF
```

5. Instalar dependências Python dos hooks:
```bash
pip install httpx
```

## Executar

```bash
# Modo Gateway (monitorização contínua de email + API Server)
hermes gateway

# Verificar que o agente está a correr
curl http://localhost:8642/api/status \
  -H "Authorization: Bearer <HERMES_API_SERVER_KEY>"

# Testar o hook de startup
hermes hooks test gateway:startup
```

## Verificar Integração .NET

```bash
# Simular uma fatura enviada pelo Hermes Agent ao Gateway .NET
curl -X POST http://localhost:5000/api/hermes/invoices/ingest \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <HERMES_AGENT_API_KEY>" \
  -d '{
    "invoiceNumber": "INV-2026-001",
    "supplierName": "Fornecedor Teste Lda.",
    "totalAmount": 1230.00,
    "currency": "EUR",
    "validationStatus": "OK",
    "lineItems": [],
    "sourceEmail": "fornecedor@teste.com",
    "extractionTimestamp": "2026-06-01T22:00:00Z"
  }'
```

## Fluxo Completo

1. Email com fatura chega à caixa `faturas@empresa.com`
2. Hermes Agent deteta o email via IMAP polling (30s)
3. Skill `invoice-extraction` é carregada automaticamente
4. Agente lê o PDF/imagem com `vision_analyze`
5. Extrai JSON estruturado e valida matematicamente
6. POST para `http://localhost:5000/api/hermes/invoices/ingest`
7. Gateway .NET publica `InvoiceReceivedFromAgentEvent` no RabbitMQ
8. Hermes.Reconciliation processa a fatura
9. Hermes.Notifications alerta o frontend React via SignalR
10. Agente responde ao email do fornecedor com confirmação + trackingId
