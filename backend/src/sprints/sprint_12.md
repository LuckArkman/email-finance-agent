# Sprint 12: Pré-processamento: Visão Computacional (Image Normalization)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Pré-processamento Documental
- **Objetivo da Sprint:** Melhorar a qualidade visual do documento antes de entrar no motor OCR para aumentar acurácia.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Conversão para Grayscale.
- [x] Binarização adaptativa OTSU.
- [x] Morphological transforms (Dilatar e Erodar fontes fracas).
- [x] Salvar nova imagem consolidada.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- OpenCV (cv2), Pillow (PIL), NumPy

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `ImageEnhancer`\n- `CV2Pipeline`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `apply_adaptive_threshold()`\n- `rescale_image_dpi()`\n- `remove_shadows()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
