# Sprint 23: Machine Learning: NLP Email Intent Classifier

## 📌 Contexto Estratégico
- **Fase Arquitetural:** Categorização e Regras de Negócio
- **Objetivo da Sprint:** Classifica a mensagem (corpo textual) do email: É uma Fatura Nova? É um Comprovante? É Reclamação?

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

- Treinamento local de um SVC ou uso leve de LLM zero-shot no corpo do e-mail.
- Rotulação das categorias: AP, AR, Receipt, Non-Financial.
- Fluxo de descarte de spams (Mailing lists de newsletter).

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- Scikit-learn, NLTK

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
- `EmailIntentClassifier`\n- `IntentTypes(Enum)`

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
- `predict_intent()`\n- `tokenize_email_body()`

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
