# Sprint 34: Frontend (React): Substituição do Cliente WebSocket por SignalR

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Adaptação e Integração do Frontend
- **Objetivo da Sprint:** A UI do Dashboard e Inbox que usa `new WebSocket()` precisa de ser migrada para usar o SignalR JS Client.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- `npm install @microsoft/signalr`.
- Criar `useSignalR` React Hook gerindo o ciclo de vida e reconnection automática.
- Fazer o bind de escutas como `connection.on("InvoiceProcessed", data => updateZustandStore(data))`.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- @microsoft/signalr

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `useSignalR.ts`\n- `SignalRStore`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
