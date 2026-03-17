# Sprint 28: API Layer: Políticas Multi-Tenancy (B2B)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** APIs REST e Integrações
- **Objetivo da Sprint:** Confinar a visibilidade de dados: a visualização de faturas pela empresa A não enxerga a empresa B.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Adição do tenant_id global nas sessões usando context_vars ou restrição no `get_current_user`.
- [x] Testes RLS (Row Level Security).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Contextvars (Built-in)

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `TenantSecurityMiddleware`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `get_current_tenant()`\n- `filter_by_tenant()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
