# Sprint 17: Hermes.OCR: Visão Computacional (Deskewing e Enhancements)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.OCR
- **Objetivo da Sprint:** Antes da leitura, limpar ruído visual (ex: fotos pelo celular) das faturas, substituindo o pipeline OpenCV do Python.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Uso do Emgu CV ou ImageSharp para converter a imagem em Greyscale e aplicar Thresholding Otsu.
- Correção de rotação (Deskew) determinando ângulos base e rotacionando.
- Emissão temporária de imagens otimizadas para processamento OCR.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Emgu.CV / SixLabors.ImageSharp

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ImageEnhancementPipeline`\n- `DeskewProcessor`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
