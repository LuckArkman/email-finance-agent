# Sprint 32: Hermes.Notifications: Dispatcher Evento-para-Cliente

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** WebSockets & Eventos em Tempo Real
- **Objetivo da Sprint:** Ouvir o bus de eventos global (RabbitMQ) e retransmitir para o ecrã local React em frações de segundo.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Consumidor de Eventos como `ExtractionCompletedEvent` no `Hermes.Notifications`.
- Injetar dependência `IHubContext<NotificationHub>`.
- Enviar pacote JSON final: `.Clients.Group(tenantId).SendAsync("InvoiceProcessed", invoiceData)`.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- MassTransit, SignalR

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `EventToSocketBroadcaster`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
