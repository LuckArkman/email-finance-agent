# Sprint 24: Regras de Negócio: Entity Matching (Vendor e Chart of Accounts)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Categorização e Regras de Negócio
- **Objetivo da Sprint:** Associar nomes de empresas lidas no PDF para as empresas previamente cadastradas no DB através de aproximação Fuzzy.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Instanciação do thefuzz para comparar strings (ex: 'Amazon Web Srvs' -> 'Amazon').
- [x] Auto categorização utilizando dados estatísticos anteriores (Ex: Vendor 'Uber' -> Travel).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- TheFuzz, Levenshtein

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `VendorMatcher`\n- `CategoryPredictor`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `fuzzy_match_vendor()`\n- `assign_default_category()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
