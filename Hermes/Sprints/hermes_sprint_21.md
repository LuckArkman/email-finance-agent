# Sprint 21: Hermes.Extraction: Prompt Engineering com Instructor .NET

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Extraction & IA
- **Objetivo da Sprint:** Modelagem determinística (Function Calling) convertendo texto caótico do OCR em um Record C# strongly-typed.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Traduzir os antigos schemas Pydantic do Python para Records do C# (ex: `public record InvoiceExtracted(...)`).
- Aplicar Function Calling e System Prompts rígidos focando Data, Fornecedor, CNPJ/NIF e Montante Total.
- Parsing validado do JSON de retorno.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- System.Text.Json

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `PromptBuilder`\n- `InvoiceExtractionModel`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `ExtractionCompletedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
