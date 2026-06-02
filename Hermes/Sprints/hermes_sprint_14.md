# Sprint 14: Hermes.Documents: Armazenamento Blob (S3 e Local)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Documents
- **Objetivo da Sprint:** Receber anexos do EventBus e salvar permanentemente em Block Storage ao invés do sistema de arquivos local.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Criação do Microsserviço `Hermes.Documents` que assina `AttachmentExtractedEvent`.
- Upload em paralelo (Stream) para buckets Amazon S3 usando o SDK AWS .NET.
- Gravação da Entidade de DB `Document` referenciando a S3 Key gerada.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- AWSSDK.S3

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `DocumentStorageService`\n- `S3BlobClient`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `DocumentStoredEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
