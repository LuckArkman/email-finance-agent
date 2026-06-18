# Sprint 06: Arquitetura Multi-Tenant: Isolamento e Identificadores Globais

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Identity
- **Objetivo da Sprint:** Garantir a total separação de dados dos clientes (Multi-Tenancy SaaS) injetando TenantId em cada Query e Entidade.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Adição do campo `TenantId` na classe `BaseEntity`.
- Implementação de Global Query Filters no `HermesDbContext` para evitar fugas de dados.
- Serviço `ITenantProvider` que extrai o ID do Tenant a partir de Headers ou Tokens JWT.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- EF Core Global Filters

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ITenantProvider`\n- `TenantInterceptor`\n- `TenantContext`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `TenantCreatedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
