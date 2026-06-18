# Sprint 28: Módulo ReviewQueue: Filas Human-in-the-Loop

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Aplicações de Negócio Core
- **Objetivo da Sprint:** Intervenção manual para faturas confusas.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Captura de faturas marcadas com `FlagReviewRequired`.
- API CRUD (`GET /api/hermes/review`, `PUT /api/hermes/review/{id}`) exposta para a listagem visual no Frontend.
- Possibilidade de sobrescrever manualmente e gravar o log de alteração de auditoria.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- N/A

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ReviewController`\n- `AuditLogService`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `InvoiceManuallyReviewedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
