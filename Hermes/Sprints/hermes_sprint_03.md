# Sprint 03: Orquestração Assíncrona: Hermes.EventBus (RabbitMQ)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Fundação e Setup Arquitetural
- **Objetivo da Sprint:** Substituir o Celery e Redis-tasks por uma Arquitetura Orientada a Eventos (EDA) via mensageria robusta.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Instanciar a biblioteca MassTransit em integração com RabbitMQ.
- Criar os contratos (C# Interfaces) para eventos vitais do sistema.
- Construir a abstração `IEventBus` para publicações e assinaturas entre os microsserviços.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- MassTransit, RabbitMQ

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `IEventBus`\n- `RabbitMqEventBus`\n- `IntegrationEvent`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `SystemStartedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
