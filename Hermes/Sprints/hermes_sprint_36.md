# Sprint 36: Hermes.Agent: RAG e Construção de Agentes Autônomos

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Aplicações de Negócio Core & Chat
- **Objetivo da Sprint:** O Cérebro da Operação. Recebe queries do React, pergunta ao vetor e constrói respostas conversacionais baseadas nas finanças da empresa.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Converter query para Embedding.
- Pesquisa semântica no PgVector (Retrieval).
- Injeção das Top 5 Faturas como Contexto (Augmented).
- Chamada ao LLM (Ollama/OpenAI) pedindo resumo textual e enviando resposta Streamada (Generation).

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Semantic Kernel / OpenAI SDK

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `RagOrchestrator`\n- `AgentStreamService`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
