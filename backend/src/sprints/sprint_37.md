# Sprint 37: Front-end: Document Viewers Interativos (Split Screen)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Front-end Módulos Visuais
- **Objetivo da Sprint:** Na esquerda o Preview perfeito do PDF faturado nativo; na direita os campos editáveis extraídos pela IA LangChain.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Integração de Viewer PDF Canvas.
- [x] Sincronização e Highlights entre campo Extraído (Forms na direita) vs Bound-Box da Imagem original (esquerda).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- React-PDF / PDFjs-dist

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `SplitViewerComponent`\n- `DocumentCanvasPreview`\n- `ExtractionFormsUI`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `renderPdfPage()`\n- `onFieldFocusHighlightBox()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
