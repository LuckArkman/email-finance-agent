# Sprint 30: Hermes.Analytics: Cálculos de Cashflow e Agregações SQL

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Aplicações de Negócio Core
- **Objetivo da Sprint:** Alimentar os Dashboards gráficos de alto desempenho no React substituindo agregações em Python.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Endpoints HTTP para Agregação temporal usando EF Core Dapper ou SQL direto otimizado para totalizadores.
- Views Materializadas no PostgreSQL (refrescadas por eventos diários) para evitar On-The-Fly calculos massivos em Big Data.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Dapper, EF Core Views

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `AnalyticsController`\n- `DashboardKpisService`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
