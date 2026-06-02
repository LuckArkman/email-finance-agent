# Sprint 25: Módulo PgVector: Configuração da Base e Extensões

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Vector & RAG
- **Objetivo da Sprint:** Abandono sumário do ChromaDB. O PostgreSQL do Hermes assumirá o papel vetorial simultaneamente aos dados relacionais.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Ativação do script de DB `CREATE EXTENSION vector;`.
- Incorporação do `Npgsql.EntityFrameworkCore.PostgreSQL.NodaTime` e suporte a vetor via `pgvector-dotnet`.
- Criação do campo `public Vector Embedding { get; set; }` na tabela de Invoices.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Pgvector.EntityFrameworkCore

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `HermesDbContext`\n- `VectorMigration`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
