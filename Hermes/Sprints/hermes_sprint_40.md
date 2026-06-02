# Sprint 40: Resiliência a Falhas: Retry Policies e Circuit Breakers

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Segurança e Otimização
- **Objetivo da Sprint:** Impedir bloqueio do sistema se o serviço AI (Ollama/OpenAI) ou o IMAP ficarem indisponíveis momentaneamente.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Incorporar a framework Polly ao `HttpClient`.
- Configurar Circuit Breaker (Quebra se ocorrerem > 5 falhas seguidas).
- Exponential Backoff para leitura de email falhada.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Polly

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ResiliencePolicyConfiguration`\n- `HttpHandlers`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
