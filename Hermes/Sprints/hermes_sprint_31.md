# Sprint 31: Hermes.Notifications: Subscrições SignalR Base

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** WebSockets & Eventos em Tempo Real
- **Objetivo da Sprint:** Substituir de forma radical o primitivo WebSockets FastAPI por SignalR, a tecnologia padrão ouro de Tempo-real do .NET.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Implementação do `NotificationHub : Hub` centralizado no backend.
- Configurar autenticação JWT para acesso às ligações Socket.
- Grupos por Tenant: `Groups.AddToGroupAsync(Context.ConnectionId, user.TenantId)` impedindo envio de sockets de uma empresa para a outra.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Microsoft.AspNetCore.SignalR

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `NotificationHub`\n- `SignalRAuthenticator`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
