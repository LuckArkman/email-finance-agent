# Sprint 15: Hermes.Documents: API de Upload Manual e Sanitização

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Documents
- **Objetivo da Sprint:** Disponibilizar endpoint de Minimal APIs para que o front-end (React) faça upload de faturas arrastadas (Drag&Drop).

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Endpoint `POST /api/hermes/documents/upload`.
- Validação do `IFormFile` e bloqueio de executáveis ou corrompidos via Magic Bytes verification.
- Retorna o `DocumentId` e despoleta `DocumentStoredEvent`.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- ASP.NET Core Http

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `UploadController`\n- `FileSanitizer`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `DocumentStoredEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
