# Sprint 19: Hermes.OCR: Parsing de PDFs nativos e Extração Textual

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.OCR
- **Objetivo da Sprint:** Otimizar tempo e custo extraindo texto embutido em PDFs vetoriais eletrônicos (PDF/A) sem passar pela malha OCR.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Interceptar ficheiros PDF no `Hermes.OCR`.
- Recurso a PdfPig (UglyToad) para verificar a presença de strings limpas.
- Bypass do OCR visual se o arquivo for plenamente digital, disparando a conclusão instantânea.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- UglyToad.PdfPig

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `PdfTextExtractor`\n- `DigitalPdfStrategy`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `OcrCompletedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
