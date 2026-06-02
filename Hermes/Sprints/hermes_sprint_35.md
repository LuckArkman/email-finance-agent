# Sprint 35: Frontend (React): Componente AgentChat com SignalR Streaming

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Adaptação e Integração do Frontend
- **Objetivo da Sprint:** A experiência ChatGPT-like com RAG do Hermes será feita via streaming pelo SignalR permitindo fluidez fantástica.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Refazer a tela de AgentChat.
- Endpoint C# `IAsyncEnumerable<string>` streamado via SignalR.
- Atualização do estado de conversação caractere por caractere via React state append.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- React, Zustand

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `AgentChatComponent`\n- `ChatMessageList`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
