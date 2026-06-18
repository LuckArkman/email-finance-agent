# Sprint 02: Desenvolvimento do Hermes.Gateway e Roteamento Ocelot/YARP

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Fundação e Setup Arquitetural
- **Objetivo da Sprint:** Fornecer um ponto unificado de entrada e roteamento que substitui a gestão monolítica de rotas do FastAPI, garantindo Rate Limiting global.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Instalar e configurar YARP (Yet Another Reverse Proxy).
- Definir rotas de fallback `api/hermes/*` redirecionando para os microsserviços do backend.
- Adicionar middleware de Rate Limiting e proteções XSS e CSRF de borda.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- YARP, ASP.NET Core Middleware

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `GatewayConfiguration`\n- `RateLimitMiddleware`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
