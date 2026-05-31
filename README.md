# AI Email Finance Agent — Documentação Completa do Projeto

Este documento serve como a referência primária, exaustiva e minuciosa para todo o ecossistema do **AI Email Finance Agent**. Cobre a totalidade da arquitetura, funcionamento dos componentes, roteamento da API, payloads e a interligação com as interfaces gráficas (Frontend).

---

## 1. Visão Geral da Arquitetura

O sistema é desenhado em torno de uma arquitetura baseada em micro-serviços executados em contentores Docker, garantindo escalabilidade, resiliência e a capacidade de realizar processos assíncronos pesados (como OCR e Extração LLM) sem bloquear a interface do utilizador.

### 1.1 Stack Tecnológico Principal
- **Backend**: FastAPI (Python 3.12)
- **Mensageria & Tarefas em Background**: Celery + Redis
- **Bases de Dados**: 
  - PostgreSQL (Dados Estruturados: utilizadores, faturas, line items, logs).
  - MongoDB (Dados Não-Estruturados: emails raw e históricos de extração).
  - ChromaDB (Banco Vetorial para busca semântica em linguagem natural).
- **Inteligência Artificial**: Ollama (Llama 3 e nomic-embed-text) operando localmente, fallback para OpenAI.
- **Frontend**: React.js (Vite), Tailwind CSS, Framer Motion (animações), Zustand (gestão de estado global).

---

## 2. Componentes Internos do Backend

O backend (`app/`) está estruturado de forma modular:

* **`app/extraction/` (Cérebro da IA)**: 
  * Contém clientes para LLMs (`LLMExtractorClient`), promtping dinâmico baseado em RAG e avaliação de confiança (`ConfidenceEvaluator`).
  * Processa Extração de Cabeçalhos, Identificação de *Line Items* e análise espacial (OCR → Textract/EasyOCR/Tesseract).
* **`app/tasks/` (Processamento Assíncrono)**:
  * `email_tasks.py`: Orquestra a sincronização de contas (Gmail/Outlook IMAP e Graph API), efetua o parsing de anexos físicos e do corpo do e-mail, e inicia a delegação de tarefas de OCR.
  * `ocr_tasks.py`: Recebe ficheiros, aplica deskewing (limpeza da imagem), envia para OCR, depois para o LLM Llama3 para extração Pydantic. Se a extração for válida, indexa automaticamente no ChromaDB.
* **`app/services/`**: Lógica de negócio agnóstica de rotas.
  * `vector_store.py`: Abstração sobre o ChromaDB e Ollama Embeddings, lidando com reindexações e procuras de similaridade por coseno.
  * `whatsapp_service.py`: Emissão de mensagens pelo WhatsApp Baileys Bridge.
* **`app/telemetry.py`**: Gestor central de observabilidade (Sentry, Prometheus) e logs blindados (ocultação de PII).
* **`app/security.py` & `app/tenant.py`**: Garantem o isolamento arquitetónico Multi-Tenant. Cada pedido à API passa por middlewares que injetam o `tenant_id` no contexto global, evitando o cruzamento acidental de dados entre empresas.

---

## 3. Descrição Minuciosa das Rotas da API (Backend)

Todos os endpoints estão alojados sob o prefixo `/api/v1/`. Eles são protegidos por tokens JWT (JSON Web Tokens) e limitadores de tráfego (Rate Limiting).

### 3.1. Autenticação e Conta (`/auth`)

* **`POST /auth/login`**
  * **Parâmetros**: `OAuth2PasswordRequestForm` (username, password).
  * **Funcionamento**: Verifica o bcrypt hash da password. Se válido, gera tokens de acesso.
  * **Payload de Retorno**: `{"access_token": "jwt...", "token_type": "bearer", "user": {...}}`

* **`POST /auth/register`**
  * **Parâmetros**: `email`, `password`, `company_name`, `full_name`.
  * **Funcionamento**: Cria um novo `User` e gera o seu isolamento via um novo `tenant_id`. Inicia as definições padrão (WebhookConfig, etc).

### 3.2. Gestão de Faturas (`/invoices`)

* **`GET /invoices`**
  * **Parâmetros**: Paginação (`skip`, `limit`), Filtros (`status`, `vendor`, `date_from`, `date_to`).
  * **Funcionamento**: Pesquisa na base PostgreSQL pelas faturas filtrando pelo `tenant_id` do request. Retorna a lista acompanhada do somatório total da query (útil para totalizadores).
  * **Payload**: `{"data": [{InvoiceRecord}], "total_count": int, "aggregated_sum": float}`

* **`GET /invoices/{id}`**
  * **Parâmetros**: `id` da fatura na path.
  * **Funcionamento**: Retorna os detalhes minuciosos (incluindo array de `items` / LineItems) de uma fatura específica.

* **`PUT /invoices/{id}/status`**
  * **Parâmetros**: `status` ("pending", "paid", "review_required", "reconciled").
  * **Funcionamento**: Altera o estado do documento. Desencadeia eventos via WebSocket para atualizar os ecrãs dos utilizadores instantaneamente.

### 3.3. Caixa de Entrada e Documentos (`/documents` & `/emails`)

* **`POST /documents/upload`**
  * **Parâmetros**: `file` (UploadFile multipart/form-data).
  * **Funcionamento**: Valida MimeTypes (PDF, PNG, JPG). Grava o ficheiro na pasta `/tmp/uploads`, cria um `InvoiceRecord` genérico com o status "processing" e despacha o Celery Task (`enqueue_ocr_job`). Retorna o ID da tarefa.
  * **Payload**: `{"task_id": "uuid", "invoice_id": "uuid", "status": "processing"}`

* **`GET /emails/sync`**
  * **Parâmetros**: Nenhum explícito (usa os tokens guardados na DB para a conta conectada).
  * **Funcionamento**: Despoleta o `sync_tenant_emails_task` via Celery, que vai ao provedor de email da empresa, descarrega novos emails, isola os anexos, grava no MongoDB e desencadeia OCRs em massa.

### 3.4. Busca Semântica Avançada (`/search`)

* **`GET /search`**
  * **Parâmetros**: `q` (query de texto natural), `limit`, `status`, `document_type`.
  * **Funcionamento**: Converte a string `q` para vetores de 768 dimensões com Ollama, efetua similaridade de coseno no ChromaDB, filtra por metadados de status e retorna os resumos textuais rankeados.
  * **Payload**: `{"query": str, "total_results": int, "results": [{"invoice_id": str, "score": float, "snippet": str, "metadata": dict}]}`

* **`POST /search/reindex`**
  * **Funcionamento**: Endpoint administrativo. Lê todo o histórico do PostgreSQL para um Tenant e re-vetoriza forçadamente para dentro do ChromaDB.

### 3.5. Reconciliação Bancária (`/reconciliation`)

* **`POST /reconciliation/auto-match`**
  * **Funcionamento**: Vasculha recibos de pagamento (`PAYMENT_RECEIPT`) pendentes e cruza IBANs, Valores e Referências com Faturas Pendentes (`ACCOUNTS_PAYABLE`). Havendo correspondência exata, gera pares e liquida as faturas.

### 3.6. Comunicação Real-time (`/ws`)

* **`WebSocket /ws/{token}`**
  * **Funcionamento**: Abre uma ligação TCP bidirecional e segura. Escuta um canal Redis local. Quando processos em background de OCR acabam, emitem eventos (`{"type": "INVOICE_PROCESSED", "id": "..."}`) empurrados diretamente para os browsers.

---

## 4. Arquitetura e Vistas do Frontend (React/Vite)

O Frontend é desenvolvido em React e usa o conceito de *Single Page Application* (SPA), com navegação roteada por React Router DOM. Cada ecrã foca-se na eficiência operacional e riqueza visual (Micro-animações e Framer Motion).

### 4.1. Dashboard (`Dashboard.tsx`)
A primeira página após o login.
* **Dados**: Interroga `GET /api/v1/analytics/kpis` e `GET /api/v1/analytics/charts`.
* **Fluxo**: Ao carregar, o Zustand verifica a sessão. O ecrã mostra de imediato contadores de faturas pendentes, valores a pagamento, e gráficos de evolução temporal. Integra *WebSockets* para que os contadores pisquem e mudem de valor sem necessitar de refresh se um email acabar de chegar.

### 4.2. Caixa de Entrada (`InvoicesInbox.tsx` e `UniversalInbox.tsx`)
* **Propósito**: Onde chegam os emails e os resultados diretos do OCR.
* **Integração Backend**: Efetua chamadas a `GET /invoices` com filtro de datas e status "pending".
* **Interatividade**: Dispõe de um componente Modal (`DocumentViewerModal.tsx`) que intercepta o clique do utilizador numa fatura, pede o binário (blob) do documento ao endpoint seguro (`GET /api/v1/documents/view/{path}`) e apresenta o PDF nativamente ou a imagem.

### 4.3. Agenda de Pagamentos (`PaymentsAgenda.tsx`)
* **Propósito**: Ferramenta central de tesouraria. Apresenta um calendário.
* **Interatividade**: Os dias são preenchidos com *badges* coloridas que representam faturas a vencer, pendentes ou pagas. Ao selecionar o mês, a página chama o backend pedindo faturas do mês selecionado; ao selecionar o dia, a lista direita detalha quais pagamentos devem sair naquele momento. Resumos estatísticos mensais no painel lateral ajudam a gerir o fluxo de caixa.

### 4.4. Fila de Revisão Humana (`ReviewQueue.tsx`)
* **Fluxo**: Ocasionalmente, o Llama3 ou OCR terão níveis de "Confidence Score" abaixo de 90%. Esses documentos vão parar a esta fila.
* **Ação**: O utilizador pode visualizar a foto do lado esquerdo, e o parsing extraído do lado direito num formulário (fornecedor, valor total, nif). O utilizador corrige os valores errados e clica em "Submeter Correção", desencadeando um `PUT /api/v1/review/{id}/resolve`. O LLM é treinado retrospectivamente com estas correções.

### 4.5. Configurações de Conexões (`EmailLinking.tsx` & `Settings.tsx`)
* **Objetivo**: Ecrã onde a empresa emparelha as suas caixas de correio.
* **Mecanismo OAUTH**: Clicar em "Conectar Gmail" remete o utilizador para a landing page da Google passando a Redirect URI do nosso backend. Quando o login na Google é aceite, o utilizador regressa a `/api/v1/emails/callback/google` onde o backend troca o Auth Code pelos Tokens definitivos (Refresh/Access Token) que são guardados no PostgreSQL encriptados, redirecionando o browser de volta à dashboard com sucesso.

### 4.6. Conversar com IA (`AgentChat.tsx`)
* **Fluxo**: Representa um Chatbot (ChatGPT-like). Permite à gestão fazer perguntas como *"Quanto gastei em luz?"*.
* **Integração**: Chama a rota `/api/v1/chat`. Com a nova funcionalidade vetorial implementada, os prompts do utilizador são transformados em queries ao banco vetorial ChromaDB de onde os metadados são retirados. O agente LLM usa esses resultados para montar a resposta natural entregue à UI via streaming (SSE).

---

## 5. Fluxo de Integração Holístico (O Ciclo de Vida de um Email)

Para compreender como todas as peças funcionam em sintonia perfeita, aqui está o ciclo de vida completo:

1. **Chegada (Cron/Sync)**: O Celery Task do Backend acorda, liga-se ao servidor IMAP da conta ligada do utilizador e deteta um novo email de "no-reply@edp.pt".
2. **Ingestão (MongoDB)**: O corpo é processado e o PDF em anexo é salvo em `/tmp/email_attachments`. Um registo "cru" vai para o Mongo.
3. **Fila de Execução (Celery/Redis)**: A rota interna insere uma tarefa na fila de OCR (`enqueue_ocr_job`).
4. **Extração (AI)**: O `celery_worker` apanha o documento, converte a imagem e roda o Tesseract. A string crua de letras é enviada ao Llama 3 sob um Prompt rigoroso para extração em JSON (`PydanticOutputParser`).
5. **Classificação Vetorial (ChromaDB)**: Havendo sucesso, o texto extraído vai ao Ollama ser condensado em *embeddings* e indexado num `VectorStore`.
6. **Armazenamento de Negócio (PostgreSQL)**: Um novo `InvoiceRecord` entra na tabela.
7. **Notificação Real-time (WebSockets)**: O Redis emite um PUB/SUB `invoice_processed`. O `main.py` de FastAPI apanha a notificação e empurra para a ligação TCP/WebSocket do browser.
8. **UI Response (React)**: No browser do utilizador, que estava com o `Dashboard.tsx` aberto, ouve-se o "ding", o contador salta de 5 faturas para 6 e uma notificação *toast* aparece "Nova fatura da EDP pronta!". Tudo sem refrescar a página.
9. **Resolução Contabilística**: O utilizador clica na fatura, agenda o pagamento no seu banco e através da página `InvoicesInbox.tsx`, altera o Status para *Pago*. O ciclo encerra-se.

---

### Notas de Segurança
- As comunicações front/back assumem origens pre-definidas de CORS.
- Todo o tráfego a partir dos views de React está englobado pelo middleware de intercepção JWT do Axios, o qual renova silenciosamente os tokens se expirados recorrendo a `/auth/refresh`.
- Nenhum acesso de ficheiros ocorre na raiz de sistema: a visualização de faturas (anexos) requer endpoints validados pela sessão.
