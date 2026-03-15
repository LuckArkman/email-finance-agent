# Sprint 22: Workflows Inteligentes: HITL Dispatcher

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Categorização e Regras de Negócio
- **Objetivo da Sprint:** Gestor inteligente de envio. Documentos marcados como duvidosos pela IA vão para a Inbox de Revisores Humanos.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Criação da Entidade HumanReviewQueue.
- Serviço que isola o doc processado mantendo pendente no sistema financeiro.
- Envio de alerta WebSocket notificando os administradores.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- FastAPI, PostgreSQL

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `HumanReviewService`\n- `ReviewQueueModel`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `dispatch_to_review()`\n- `approve_document_manually()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
