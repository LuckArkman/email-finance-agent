# Sprint 33: Frontend (React): Migração de Rotas e Refatoração de Cliente HTTP

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Adaptação e Integração do Frontend
- **Objetivo da Sprint:** Ajustar o React Vite existente para consumir `/api/hermes/*` substituindo chamadas legadas ao `/api/v1/` de Python.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Atualizar BaseURLs no Axios Interceptor.
- Atualizar Tipagens do TypeScript baseadas nos novos Data Contracts (Records C#) de respostas que venham com novos formatos ou casing (CamelCase por omissão em System.Text.Json).

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Axios, TypeScript

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `AxiosClient`\n- `HttpServices`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
