# Sprint 19: Prompt Engineering: Cabeçalho de Invoice

## 📌 Contexto Estratégico
- **Fase Arquitetural:** OCR e Inteligência Artificial
- **Objetivo da Sprint:** Sintonizar os prompts instrucionais das IAs focando perfeitamente na identificação clara de Vendor, Date, Total e CNPJ.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Criação de prompt templates no Langchain focados em Headings.
- Mapeamento estrito de datetimes (tratar Mês/Dia vs Dia/Mês).
- Execução de evals e fine-tuning do prompt.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Langchain-core

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `PromptManager`\n- `HeaderExtractorService`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `build_header_prompt()`\n- `validate_date_formats()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
