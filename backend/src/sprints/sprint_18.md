# Sprint 18: Integração LLM e Cadeia Semântica (LangChain)

## 📌 Contexto Estratégico
- **Fase Arquitetural:** OCR e Inteligência Artificial
- **Objetivo da Sprint:** Conectar o projeto a modelos gigantes (GPT-4T / Claude) para realizar RAG e extração profunda dos blocos de texto.

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- [x] Definição do conector LLM via LangChain (ChatOpenAI).
- [x] Definição do output_parser com Pydantic.
- [x] Tratativa de rate-limits no disparo.

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Langchain, OpenAI, Instructor

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `LLMExtractorClient`\n- `InvoiceOutputSchema(BaseModel)`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `invoke_llm_chain()`\n- `format_prompt()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
