# Sprint 13: Pré-processamento: Correção de Deskewing

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Pré-processamento Documental
- **Objetivo da Sprint:** Corrige rotações em faturas que foram escaneadas fisicamente ou tiradas através de celular.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Obtenção do ângulo dos blocos de texto.
- Rotação afim matemática da imagem em -ângulo detectado.
- Preenchimento de bordas (Background padding).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- OpenCV, Scikit-Image

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `DeskewProcessor`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `calculate_skew_angle()`\n- `rotate_image()`\n- `correct_document_perspective()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
