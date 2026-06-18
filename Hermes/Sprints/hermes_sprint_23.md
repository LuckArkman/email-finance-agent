# Sprint 23: Hermes.Extraction: Confidence Score e Regras Heurísticas

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Módulo Hermes.Extraction & IA
- **Objetivo da Sprint:** Migrar a análise Log-Likelihood e probabilidade de incerteza da IA.

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Verificação de pontuação retornada pelo provedor de AI e casamento heurístico no C# (Regex do CNPJ cruza com o do LLM?).
- Se confiança < 90%, associar *FlagReviewRequired* no evento emitido.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- System.Text.RegularExpressions

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `ConfidenceEvaluator`\n- `HeuristicMatcher`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `ExtractionCompletedEvent`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
