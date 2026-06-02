# Sprint 38: Performance Optimization: Caching Distribuído com Redis C#

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Segurança e Otimização
- **Objetivo da Sprint:** Diminuir a carga do Postgres e processamento repetitivo de queries pesadas através da Cache nativa do .NET (IDistributedCache).

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Integração de `StackExchange.Redis`.
- Injectar `IDistributedCache` no Controller de Analytics.
- Invalidação de chaves de cache (Eviction) reativa e baseada em eventos do EventBus (`InvoiceCreatedEvent` limpa a cache do Mês X).

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- StackExchange.Redis

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `RedisCacheService`\n- `CacheInvalidatorConsumer`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
