# Sprint 29: Hermes.Reconciliation: Motor de Conciliação Automático

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Aplicações de Negócio Core
- **Objetivo da Sprint:** Lógica financeira pesada que cruza Comprovativos de Pagamentos com Faturas por pagar, dando baixa nas contas.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Ao inserir Comprovativo, iniciar serviço que cruza IBAN extraído, NIF da entidade, Data e Valor em tolerância (centavos) com a tabela Invoices (Status=Pending).
- Alterar o Status para `Reconciled`.
- Emissão de Evento `InvoiceReconciledEvent` no Bus de mensagens.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- N/A

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ReconciliationEngine`\n- `ToleranceMatcher`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `InvoiceReconciledEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
