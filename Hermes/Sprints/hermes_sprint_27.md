# Sprint 27: Hermes.Vector: API de Procura Semântica (Cosine Similarity)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Vector & RAG
- **Objetivo da Sprint:** Poder realizar procuras mágicas em C# com Queries Naturais.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Endpoint Minimal API `/api/hermes/search?q=luz da semana passada`.
- Geração de embedding da query `q`.
- LINQ com PgVector: `.OrderBy(x => x.Embedding.CosineDistance(queryEmbedding))`.
- Retorno ultra rápido graças ao índice HNSW do Postgres.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Pgvector EF LINQ

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `SemanticSearchController`\n- `SearchQueryService`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
