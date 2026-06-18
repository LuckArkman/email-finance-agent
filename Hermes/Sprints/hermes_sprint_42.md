# Sprint 42: HealthChecks Nativos (.NET Health Checks)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Deploy e Manutenção Final
- **Objetivo da Sprint:** Permitir ao Docker e Kubernetes perceber o estado clínico dos Microsserviços Hermes.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Instalar `AspNetCore.HealthChecks.UI` e probes para Postgres, RabbitMQ e Redis.
- Expor endpoint `/health/ready` e `/health/live` na board Gateway do Hermes.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- AspNetCore.HealthChecks

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `HealthCheckConfiguration`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
