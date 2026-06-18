# Sprint 26: Hermes.Vector: Geração de Embeddings com Nomic-Embed

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Vector & RAG
- **Objetivo da Sprint:** Geração das dimensões vetorizadas do texto das faturas a cada vez que a extração termina.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Escuta do `ExtractionCompletedEvent`.
- Disparo à API Ollama (`/api/embeddings`) usando o modelo `nomic-embed-text` com payload do corpo do e-mail e itens da fatura.
- Gravação das 768 dimensões resultantes na tabela do PostgreSQL conectada à fatura correspondente.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- N/A

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `VectorJobConsumer`\n- `EmbeddingService`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `VectorIndexedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
