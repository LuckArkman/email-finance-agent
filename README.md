# LuckArkman - Email Finance Agent (v1.0.0)

🚀 **Agente de IA para Automação Financeira: Extração de Faturas via E-mail.**

Este projeto implementa uma solução completa de Human-in-the-Loop (HITL) para processamento de faturas, utilizando IA para extração de dados e uma interface premium para auditoria e gestão.

## 🏗️ Arquitetura do Sistema

### Backend (FastAPI + Celery + MongoDB)
- **Extração Inteligente**: OCR com Tesseract/EasyOCR e processamento de linguagem natural com GPT-4o.
- **Async Workflow**: Redis + Celery para processamento de documentos pesados em background.
- **Multitenancy**: Isolamento de dados por Tenant e autenticação JWT rigorosa.
- **Segurança**: Ofuscação de PII, Rate Limiting (SlowAPI) e Criptografia S3 AES-256.

### Frontend (React + Vite + Tailwind + Framer Motion)
- **Inbox Inteligente**: Gestão de faturas com status em tempo real.
- **Split Viewer**: Auditoria de PDFs lado a lado com formulários de extração (HITL).
- **Dashboard Analítico**: Gráficos de Cashflow e métricas de acurácia via WebSockets.
- **Settings**: Gestão de webhooks de saída para Zapier e ERPs.

## 🚀 Como Executar em Produção

### Pré-requisitos
- Docker & Docker Compose
- Cluster Kubernetes (recomendado para escala)
- Chaves de API: OpenAI, AWS S3, Sentry (opcional)

### Deploy via Docker Compose
```bash
docker-compose --profile production up -d
```

### Deploy via Kubernetes
1. Configure as chaves no `k8s/secrets.yaml`.
2. Aplique os manifestos:
```bash
kubectl apply -f k8s/
```

## 🧪 Testes e Qualidade
- **E2E**: Executado via Playwright (`npm run test:e2e`).
- **Load**: Validado via Locust para 1000+ invoices/min.
- **Sentry**: Monitoramento de erros em tempo real integrado.

## 📄 Documentação Técnica
- [Guia de Handover RC1](file:///C:/Users/MPLopes/.gemini/antigravity/brain/f6a9c627-d511-481b-b4a4-d5c722912fde/handover_rc1.md)
- [Relatório de Stress Test](file:///C:/Users/MPLopes/.gemini/antigravity/brain/f6a9c627-d511-481b-b4a4-d5c722912fde/stress_test_report.md)

---
*Desenvolvido por Antigravity AI para o projeto LuckArkman.*
