# Sprint 21: Machine Learning: Cálculo e Sistema de Confidence Score

## 📌 Contexto Estratégico
- **Fase Arquitetural:** OCR e Inteligência Artificial
- **Objetivo da Sprint:** Toda IA deve fornecer índice de certeza. Limite aceitável antes de intervir humanamente.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Algoritmo para cruzar a probabilidade log-likeliehood do LLM / OCR em campos como Valor Pago.
- [x] Atribuição de score 0-100%.
- [x] Se <90%, flag: needs_manual_review = True.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- NumPy

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `ConfidenceEvaluator`\n- `ConfidenceMetrics`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `calculate_overall_confidence()`\n- `flag_low_metrics()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
