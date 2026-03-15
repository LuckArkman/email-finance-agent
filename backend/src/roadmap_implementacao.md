# Roadmap Minucioso de Implementação e Desenvolvimento
**Projeto:** AI Email Finance Agent  
**Versão:** 1.0  
**Data:** Março de 2026

Este roadmap detalha minuciosamente a arquitetura, o planejamento de sprints e os marcos de implementação para o **AI Email Finance Agent**, baseando-se nas diretrizes do *Whitepaper v2*, melhores práticas ágeis para desenvolvimento de Inteligência Artificial e nas modernas abordagens de Processamento Inteligente de Documentos (IDP).

---

## 📅 Visão Geral e Estrutura do Repositório

Como primeira premissa arquitetural, foi estabelecido que o código-fonte principal que orquestra a ingestão de e-mails, processamento de documentos e a IA (o Back-end) será hospedado em um diretório isolado:
* **`backend/src/`**: Conterá os microsserviços em Python (FastAPI), filas do Celery, scripts de Integração LLM, rotinas de pré-processamento de OCR e conexão com bancos de dados.

O desenvolvimento será dividido em **5 Fases Principais**, organizadas em Sprints de 2 semanas cada.

---

## 🏗️ Fase 1: Descoberta, Planejamento e Fundação Arquitetural (Sprints 1 - 2)
**Objetivo Estratégico:** Estabelecer a infraestrutura de dados, definir o fluxo completo (end-to-end), projetar esquemas de banco e configurar o repositório principal no `backend/src/`.

**Tarefas e Entregáveis:**
1. **Configuração de Repositório e CI/CD:**
   * Inicialização da estrutura no diretório `backend/src/`.
   * Configuração de linting (Ruff/Black para Python), tipagem estática (MyPy) e suítes de teste (PyTest).
   * Configuração inicial dos containers Docker (Dockerfile para o FastAPI puro e para os workers do Celery).
   * Setup do GitHub Actions / GitLab CI para testes automatizados a cada *pull request*.
2. **Design e Provisionamento de Bancos de Dados:**
   * **PostgreSQL 16:** Modelagem das tabelas relacionais (User, Tenant, Invoice, Pagamentos, Categorias).
   * **MongoDB:** Modelagem das coleções flexíveis para armazenamento do JSON extraído pelas LLMs e histórico de OCR bruto.
   * **Redis:** Setup da infraestrutura de cache e message broker para rodar as filas assíncronas do Celery.
3. **Mapeamento de Regras e Tipologia de Documentos:**
   * Levantamento formal dos dados exatos a serem extraídos (ex: Nome do Fornecedor, Data de Vencimento, Valor do Imposto, IBAN, Total).
   * Estabelecimento de regras de validação primárias (ex: "A Data de Vencimento não pode ser anterior à Data de Emissão").

---

## 📨 Fase 2: PoC de Ingestão de E-mails e Pré-processamento (Sprints 3 - 4)
**Objetivo Estratégico:** Criar um "Mínimo Produto Viável" (MVP) em pipeline capaz de se conectar a um e-mail, ouvir mensagens e extrair anexos ou texto de forma limpa.

**Tarefas e Entregáveis:**
1. **Desenvolvimento do Ingestion Engine (`backend/src/ingestion/`):**
   * Implementação de rotinas de conexão via IMAP/SMTP (para e-mails genéricos).
   * Integração com Microsoft Graph API (para Outlook/O365) e Google Workspace via OAuth2.
   * Listener de Webhooks para notificações push ou pub/sub da chegada de mensagens.
2. **Classificador Inicial de Intenção do E-mail:**
   * Regras heurísticas e modelo leve de NLP para entender se o e-mail contém uma Nota Fiscal (Accounts Payable) ou um Comprovante de Pagamento.
3. **Módulo de Manipulação de Anexos (`backend/src/processing/`):**
   * Download seguro dos anexos. Filtros de segurança (rejeição automática de `.exe`, `.zip`) para mitigar vetores de ataque.
   * **Pipeline de Imagem (OpenCV/Pillow):** Alinhamento (deskewing) de PDFs/imagens, remoção de sombras, redução de ruído e normalização da resolução (DPI ótimo para OCR).

---

## 🧠 Fase 3: Motor de Inteligência Artificial e Extração (Sprints 5 - 7)
**Objetivo Estratégico:** Implementar a verdadeira mágica do agente - transformar bytes e pixels embaralhados em JSON estruturado e confiável.

**Tarefas e Entregáveis:**
1. **Pipeline de Extração OCR Base:**
   * Implementação inicial via EasyOCR / Tesseract.
   * Fallback em nuvem (AWS Textract ou Google Document AI) para documentos extremamente complexos (comprovantes amassados, notas manuscritas).
2. **Layout Parsing com Deep Learning:**
   * Utilização de modelos multimodais (como LayoutLMv3 ou Donut) para entender a *estrutura espacial* do documento (ex: diferenciar o cabeçalho de uma listagem tabular de itens).
3. **LLM para Contexto e Entendimento Semântico:**
   * Integração de LangChain com um modelo avançado de linguagem (GPT-4T ou Claude 3.5).
   * Desenvolvimento do *Schema Prompting*: instruir a IA a pegar o bloco de texto massivo do OCR e encaixar nas chaves estruturadas (VendorName, InvoiceDate, Taxes).
4. **Camada de Human-in-the-loop (HITL):**
   * Criação de limite de confiança (Confidence Score). Caso a IA tenha menos de 90% de certeza em um campo (ex: o valor total está manchado), enviar o evento para revisão humana antes do commit no PostgreSQL.

---

## ⚙️ Fase 4: Classificação Financeira e Workflow de Reconciliação (Sprints 8 - 10)
**Objetivo Estratégico:** O agente deve agora interpretar politicas financeiras, fazer matemática pesada e reconciliar automaticamente (Two-Way/Three-Way matching).

**Tarefas e Entregáveis:**
1. **Motor de Categorização de Gastos:**
   * IA baseada no contexto do e-mail e CNPJ/Nome do Fornecedor para auto-categorizar a despesa (ex: "AWS" -> `Software & IT`).
2. **Reconciliação e Pagamentos:**
   * Construção do algoritmo de *Matching*: A IA detecta um "Recibo de Pagamento", cruza o valor e a data com as "Faturas Pendentes" do PostgreSQL e marca a respectiva fatura como `PAID` (Paga).
3. **Motor de Tributação (Tax Engine - Foco em IVA/Impostos Locais):**
   * Extração de alíquotas fracionadas do corpo da nota fiscal.
   * Cálculo de retenções e criação de views no banco para relatórios fiscais em tempo real.

---

## 💻 Fase 5: Integração Externa, Escalabilidade e Dashboard (Sprints 11 - 13)
**Objetivo Estratégico:** Conectar o back-end ao mundo exterior (Web, ERPs) e empacotar a solução para ser consumida de forma corporativa e segura.

**Tarefas e Entregáveis:**
1. **APIs e WebSockets:**
   * Finalização dos endpoints REST no FastAPI para expor os dados ao front-end.
   * Server-Sent Events (SSE) ou WebSockets para atualizar o Front-end no momento exato em que a IA terminar de ler uma fatura enviada há 5 segundos.
2. **Integrações de ERPs e Bancos:**
   * Desenvolvimento de *Connectors* seguros, permitindo "empurrar" dados limpos diretamente para QuickBooks, SAP ou Xero.
   * Uso da Plaid ou de APIs de Open Banking para cruzar a fatura do sistema com a saída do extrato bancário.
3. **Endurecimento de Segurança (SecOps):**
   * Auditoria de Role-Based Access Control (RBAC). 
   * Teste de carga: simular a injeção simultânea de 50.000 e-mails para validar a capacidade do Kubernetes auto-escalar os pods do OCR / Celery e evitar engarrafamentos.
4. **Front-End / Dashboard:**
   * Implementação da interface do usuário (usando Vue 3 ou React 18, em repositório ou pasta separada).
   * Criação dos painéis de fluxo de caixa preditivo, painel de aprovação das reconciliações com erro na IA (HITL) e relatórios executivos.

---

## 🚀 Fase 6: Lançamento e Evolução Contínua (Sprints 14+)
* **Go-Live:** Implantação total no ambiente produtivo (Provisionando com Terraform em AWS/Azure).
* **Treinamento Contínuo de IA:** Reter feedback manual. Quando um humano corrige um campo lido errado pelo agente financeiro, retroalimentar o dataset de embeddings/finetuning para que a IA nunca cometa o mesmo erro duas vezes.
* **Módulos Futuros:** Previsão preditiva de quebra de fluxo de caixa via ML puro, e relatórios automatizados gerados nativamente por bots e enviados semanalmente.
