# Sprint 22: Hermes.Extraction: Extração em Massa de Line Items (Tabelas)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Extraction & IA
- **Objetivo da Sprint:** Processamento minucioso do detalhe da fatura linha a linha.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Ajuste de prompting avançado para compreender matrizes tabulares no texto OCR.
- C# records contendo `IEnumerable<LineItemExtracted>`.
- Validação C# pura assegurando que a soma dos itens (Qtd*Preço) corresponde ao total capturado.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- N/A

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `LineItemExtractionRule`\n- `MathValidator`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `ExtractionCompletedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
