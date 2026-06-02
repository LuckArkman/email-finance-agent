# Sprint 07: Segurança e Autenticação: Hermes.Identity e JWT

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Identity
- **Objetivo da Sprint:** Prover login seguro, geração de tokens JWT (Access e Refresh) e MFA, convertendo os scripts FastAPI/Passlib.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Migrar Password Hashing (Bcrypt) nativo ou PBKDF2/Identity.
- Criar rotas de Minimal APIs `/auth/login`, `/auth/register`.
- Geração de Claims Principal (Roles, Permissions) e assinatura assimétrica do JWT.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Microsoft.AspNetCore.Authentication.JwtBearer

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `AuthService`\n- `TokenGenerator`\n- `UserCredentials`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `UserLoggedInEvent`\n- `UserRegisteredEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
