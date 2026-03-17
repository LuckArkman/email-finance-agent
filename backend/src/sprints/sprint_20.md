# Sprint 20: Prompt Engineering: Extração de Linhas/Tabelas (Line Items)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** OCR e Inteligência Artificial
- **Objetivo da Sprint:** Isolar e entender tabelas e grids para extrair cada item que foi comprado com suas taxas individuais (Table extraction).

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Identificação de array de itens da compra.
- [x] Parsing the Table layout para o LLM.
- [x] Garantia de fechamento de sum: Soma dos (ValorUnitário*Qtd) deve igualar ao total do item.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Pydantic

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `LineItemExtractor`\n- `LineItemSchema`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `extract_line_items()`\n- `validate_mathematical_sum()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
