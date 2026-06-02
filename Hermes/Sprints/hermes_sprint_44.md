# Sprint 44: Kubernetes K8s Manifestos e Horizontal Pod Autoscaling (HPA)

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** Deploy e Manutenção Final
- **Objetivo da Sprint:** Permitir a escala gigante da plataforma isolando pods de API dos pods de Processamento pesado (OCR).

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

- Atualizar diretório `/k8s/` com arquivos yaml dos novos contentores `.NET`.
- Configurar Keda ou HPA focado no tamanho da fila do RabbitMQ: Se subirem as mensagens OCR, sobe a quantidade de pods do Microsserviço Hermes.OCR.

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- Kubernetes Helm, Keda

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
- `N/A - Manifests Yaml`

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
- `N/A`

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
