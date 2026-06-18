# Sprint 18: Hermes.OCR: Integração Tesseract nativa (.NET Wrapper)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.OCR
- **Objetivo da Sprint:** Extração de strings brutas de imagens e scans locais sem requisições caras a cloud.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Importação do TesseractEngine wrapper (.NET).
- Processamento da imagem normalizada.
- Retorno de Strings e confianças médias associadas.
- Emissão de evento de finalização com a RawString.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Tesseract

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `TesseractOcrEngine`\n- `OcrResult`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `OcrCompletedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
