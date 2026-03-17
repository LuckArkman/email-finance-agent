# Sprint 31: Real Time Communications: WebSockets e Server-Sent Events

## 📌 Contexto Estratégico
- **Fase Arquitetural:** APIs REST e Integrações
- **Objetivo da Sprint:** Push vivo na tela dos contadores enquanto o back-end e IA vão digerindo processamentos pendentes de faturas assíncronas.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Habilitar FastApi Websocket endpoint /ws/tenant_id.
- [x] Escutar o canal do Redis (Pub/Sub).
- [x] Disparo Broadcasting do evento JSON.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Redis PubSub, FastAPI WebSockets

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `ConnectionManagerSocket`\n- `EventBroadcaster`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `connect_ws()`\n- `broadcast_ocr_finished()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
