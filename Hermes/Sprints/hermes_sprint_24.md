# Sprint 24: Hermes.AI: Conexão a Modelos Locais via Ollama

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.AI Core
- **Objetivo da Sprint:** Garantir o processamento da IA corporativa On-Premises suportando o Llama3 localmente.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Cliente HTTP `HttpClient` parametrizado para contactar a API REST do Ollama hospedada internamente.
- Parsing manual e robusto das respostas geradas pelo `llama3` local.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- System.Net.Http

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `OllamaClient`\n- `OllamaChatCompletion`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
