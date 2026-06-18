# Sprint 20: Hermes.Extraction: Pipeline de Integração RAG LLMs

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Extraction & IA
- **Objetivo da Sprint:** Substituir o LangChain em Python usando integrações semânticas em C# para conversar com LLMs na fase de Extração.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Consumir o `OcrCompletedEvent`.
- Integrar bibliotecas oficiais do OpenAI SDK para C# ou Microsoft.SemanticKernel.
- Definição da fachada de abstração de LLM (`ILLMClient`).

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Microsoft.SemanticKernel, Azure.AI.OpenAI

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ExtractionConsumer`\n- `LlmClientFactory`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
