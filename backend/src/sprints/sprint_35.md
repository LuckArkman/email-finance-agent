# Sprint 35: Front-end: State Management e Contexto Auth

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Front-end SPA Setup
- **Objetivo da Sprint:** Centralizar login, permissões de rotas no Route Guard, e reatividade global da plataforma.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Setup de Store (Redux ou Pinia).
- [x] Construção do service camada de Rede (Axios Wrapper com Interceptors pro Token JWT).
- [x] Tela de Autenticação / Forgot Password completas.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Axios, Pinia/Redux Toolkit, Vue Router/React Router

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `AuthStore`\n- `HttpInterceptor`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `login()`\n- `logout()`\n- `validateJwtOnRoute()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
