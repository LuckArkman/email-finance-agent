# Sprint 05: Integração do Banco Relacional: PostgreSQL + Entity Framework Core 9

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Fundação e Setup Arquitetural
- **Objetivo da Sprint:** Eliminar o SQLAlchemy e MongoDB; migrar toda a base lógica de entidades relacionais para EF Core.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Criação do DbContext global `HermesDbContext` com mapeamento fluente.
- Configuração inicial das strings de conexão.
- Criação do mecanismo inicial de Migrations (`dotnet ef migrations add Initial`).

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Microsoft.EntityFrameworkCore.PostgreSQL, Npgsql

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `HermesDbContext`\n- `BaseEntity`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
