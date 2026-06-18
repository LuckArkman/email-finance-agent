# Sprint 16: Hermes.OCR: Motor de Despacho (Dispatcher) e Filas

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.OCR
- **Objetivo da Sprint:** Orquestrar filas de OCR intensivas usando MassTransit Workers, absorvendo o trabalho do Celery Python.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Microsserviço `Hermes.OCR` com background workers assíduos no RabbitMQ consumindo `DocumentStoredEvent`.
- Setup de paralelismo configurável via TPL (Task Parallel Library) `Parallel.ForEachAsync`.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- MassTransit.RabbitMQ

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `OcrJobConsumer`\n- `JobDispatcher`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `OcrStartedEvent`\n- `OcrFailedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
