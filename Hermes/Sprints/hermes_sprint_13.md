# Sprint 13: Hermes.Email: Separação de Corpo, Metadados e Anexos

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Email
- **Objetivo da Sprint:** Ao receber um e-mail bruto, isolar PDFs vitais e descartar assinaturas de e-mail e ícones (Magic Bytes).

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Lógica condicional percorrendo partições MIME.
- Análise baseada em MimeKit para verificar `ContentType` e heurística de descarte (tamanho < 10kb).
- Preparo e buffer do byte-array para o pipeline de armazenamento.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- MimeKit

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `AttachmentFilter`\n- `MimeMessageParser`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `AttachmentExtractedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
