# Sprint 15: Extração Híbrida: Setup de Engine Tesseract/EasyOCR

## 📌 Contexto Estratégico
- **Fase Arquitetural:** OCR e Inteligência Artificial
- **Objetivo da Sprint:** Implementar uma camada inicial local de reconhecimento ótico para não onerar APIs externas em arquivos simples.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Inicialização psm configurations no Tesseract.
- Chamada assíncrona para extração de String text (Text string pura).
- Export do OCR bruto para a coleção MongoDB correspondente.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Pytesseract, EasyOCR

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `LocalOCREngine`\n- `PytesseractAdapter`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `extract_text_content()`\n- `get_image_data_boxes()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
