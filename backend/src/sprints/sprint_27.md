# Sprint 27: API Layer: Endpoints de Autenticação Segura JWT

## 📌 Contexto Estratégico
- **Fase Arquitetural:** APIs REST e Integrações
- **Objetivo da Sprint:** Montar a proteção ao sistema via rotas JWT / Bearer tokens permitindo login e gerenciamento de permissão.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Integração PyJWT.
- [x] Rotas /login/access-token, hashing BCRYPT da senha.
- [x] Interceptors dependentes (get_current_active_user) do FastAPI.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Passlib, PyJWT

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `AuthHandler`\n- `SecurityDependencies`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `create_access_token()`\n- `verify_password()`\n- `get_current_user()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
