# Sprint 29: API Layer: Crud Invoices e Endereçamento REST

## 📌 Contexto Estratégico
- **Fase Arquitetural:** APIs REST e Integrações
- **Objetivo da Sprint:** Fornecer as rotas expostas para o Frontend consumir visualmente as Invoices, listar faturas vencidas, e atualizá-las.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Controllers GET /invoices, POST /invoices/manual, GET /invoices/{id}.
- [x] Parâmetros Fastapi (Paginação, sorting, filtro de datas).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- FastAPI

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `InvoiceController`\n- `InvoiceResponseSchema`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `read_invoices()`\n- `update_invoice_status()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
