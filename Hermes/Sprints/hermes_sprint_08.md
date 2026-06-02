# Sprint 08: Modelagem de Permissões: Users, Roles e Subscriptions

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Identity
- **Objetivo da Sprint:** Centralizar a autorização de quem pode ver faturas ou alterar configurações usando políticas de Authorization do ASP.NET.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Criação das Entidades de Domínio `User`, `Role`, `Permission`.
- Criação de Custom Authorization Policies (`RequireClaim("Permission", "Invoices.Write")`).
- Construção do Endpoint CRUD para gerir acessos dentro do tenant.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- ASP.NET Core Authorization

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `RoleManager`\n- `PermissionPolicyProvider`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `UserRoleUpdatedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
