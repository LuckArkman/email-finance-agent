# Sprint 26: Motor Tax & Compliance: IVA / VAT Extractor

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Categorização e Regras de Negócio
- **Objetivo da Sprint:** Identificar precisamente tributos desmembrados (Europa - Imposto Adicionado) ou nos EUA para relatórios fiscais adequados.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Regex avançada para padrões VIES/CNPJ.
- [x] Extração percentual vs Bruto/Líquido matematicamente verificado no backend.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Python-Re

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `TaxEngine`\n- `TaxBracketValidator`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `extract_vat_number()`\n- `verify_tax_math()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
