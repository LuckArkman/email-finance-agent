import os
import json

base_dir = r"d:\email-finance-agent\sprints"
os.makedirs(base_dir, exist_ok=True)

sprints = [
    {
        "id": 1,
        "title": "Setup Base do Back-end e Esteira CI/CD",
        "phase": "Fundação Arquitetural",
        "objective": "Iniciar o projeto FastAPI, gerenciar dependências e configurar pipeline de testes automatizados.",
        "processes": "- Inicialização do Poetry.\n- Configuração de Linters (Ruff, Black, Mypy).\n- Definição do Entrypoint FastAPI.\n- Criação de Action no GitHub para rodar pytest em PRs.",
        "libraries": "FastAPI, Uvicorn, Poetry, Pytest, Ruff",
        "classes": ["BaseAPIConfig", "EnvironmentSettings(BaseSettings)"],
        "functions": ["create_fastapi_app()", "app_health_status()"]
    },
    {
        "id": 2,
        "title": "Dockerização do Ambiente Back-end",
        "phase": "Fundação Arquitetural",
        "objective": "Criar imagens containerizadas leves para rodar o backend de forma agnóstica em qualquer OS.",
        "processes": "- Criação do Dockerfile multi-stage usando Python 3.12-slim.\n- Definição do arquivo docker-compose.yml.\n- Scripts entrypoint e wait-for-it.\n- Mapeamento de volumes locais.",
        "libraries": "Docker, Docker Compose",
        "classes": ["N/A - Foco Infra"],
        "functions": ["entrypoint.sh", "start-reload.sh"]
    },
    {
        "id": 3,
        "title": "Modelagem de Banco Relacional (PostgreSQL)",
        "phase": "Fundação Arquitetural",
        "objective": "Estruturar o ORM e tabelas principais que irão governar o sistema Multi-Tenant e acessos.",
        "processes": "- Setup SQLAlchemy 2.0 (Models Base).\n- Configuração assíncrona com Asyncpg.\n- Criação de tabelas: Users, Tenants (Workspaces), Invoices, Payments.\n- Setup do Alembic e Migration Inicial.",
        "libraries": "SQLAlchemy, Alembic, AsyncPg",
        "classes": ["BaseModel", "Tenant", "User", "InvoiceRecord", "Transaction"],
        "functions": ["get_async_session()", "run_migrations_offline()"]
    },
    {
        "id": 4,
        "title": "Setup do Banco Documental (MongoDB)",
        "phase": "Fundação Arquitetural",
        "objective": "Habilitar armazenamento NoSQL para reter payloads brutos de emails e JSONs flexíveis da IA.",
        "processes": "- Configuração do driver MotorMotor client.\n- Modelagem de schemata Pydantic (validação).\n- Conexão e injeção de dependência no FastAPI.\n- Adição do Mongo no compose local.",
        "libraries": "Motor, PyMongo, Pydantic",
        "classes": ["AsyncMongoManager", "RawEmailModel", "AIResultPayload"],
        "functions": ["init_mongo_client()", "insert_raw_email_document()"]
    },
    {
        "id": 5,
        "title": "Filas e Workflows Assíncronos (Redis + Celery)",
        "phase": "Fundação Arquitetural",
        "objective": "Desacoplar o processamento longo (como OCR) do loop do servidor HTTP, provendo resiliência.",
        "processes": "- Subida do container Redis.\n- Inicialização do Celery Worker.\n- Definição de Tasks Abstratas de tentativa/retry.\n- Roteamento de filas secundárias (e.g., ai_queue, general_queue).",
        "libraries": "Celery, Redis-py",
        "classes": ["CeleryManager", "OCRTaskHandler"],
        "functions": ["create_celery_app()", "enqueue_ocr_job()", "check_task_status()"]
    },
    {
        "id": 6,
        "title": "Motor de Ingestão: Serviço IMAP Padrão",
        "phase": "Ingestão e Conectividade",
        "objective": "Acessar caixas de e-mail de usuários e monitorar a chegada de faturas via IMAP padrão.",
        "processes": "- Conexão SSL via imaplib.\n- Autenticação e loop de idle (IMAP IDLE) ou polling.\n- Decodificação de headers (Remetente, Assunto).\n- Conversão para formato interno DTO.",
        "libraries": "imaplib, email.parser, aioimaplib",
        "classes": ["IMAPConnectionManager", "EmailMessageDTO"],
        "functions": ["login_imap()", "fetch_unseen_emails()", "parse_email_headers()"]
    },
    {
        "id": 7,
        "title": "Ingestão: Microsoft Graph API (Office 365)",
        "phase": "Ingestão e Conectividade",
        "objective": "Garantir acesso OAuth2 a clientes Enterprise que utilizam corporações Outlook/Microsoft.",
        "processes": "- Geração de Tokens via MSAL.\n- Requisições GET para o endpoint /me/messages.\n- Criação de Webhooks (Subscriptions) no Graph API para notificações em tempo real.",
        "libraries": "Msal, Httpx",
        "classes": ["MSGraphClient", "OAuthTokenHandler", "GraphWebhookManager"],
        "functions": ["acquire_token_silent()", "subscribe_to_inbox()", "refresh_access_token()"]
    },
    {
        "id": 8,
        "title": "Ingestão: Google Workspace API (Gmail)",
        "phase": "Ingestão e Conectividade",
        "objective": "Implementar protocolo do Google para leitura segura de provedores G-Suite.",
        "processes": "- Setup de Credenciais GCP (Service Account ou User Auth).\n- Uso do google-api-python-client.\n- Integração com Google Pub/Sub para push notifications de chegada de emails.",
        "libraries": "google-api-python-client, google-auth",
        "classes": ["GmailAPIClient", "GooglePubSubListener"],
        "functions": ["build_gmail_service()", "list_messages()", "download_message_raw()"]
    },
    {
        "id": 9,
        "title": "Ingestão: Listener Webhooks para ERPs e Portais",
        "phase": "Ingestão e Conectividade",
        "objective": "Habilitar entradas via API, permitindo que outros sistemas deem 'push' em faturas.",
        "processes": "- Criação de endpoint genérico /api/v1/ingest/webhook.\n- Validação de assinaturas (HMAC).\n- Sanitização de payload entrante.\n- Encaminhamento do documento para fila de processamento.",
        "libraries": "FastAPI, hmac, hashlib",
        "classes": ["WebhookAuthenticator", "IncomingWebhookSchema"],
        "functions": ["verify_hmac_signature()", "handle_stripe_event()", "process_generic_webhook()"]
    },
    {
        "id": 10,
        "title": "Processamento: Parsing e Separação de Anexos",
        "phase": "Ingestão e Conectividade",
        "objective": "Extrair as faturas contidas dentro de mensagens (PDFs, JPEGs) descartando assinaturas inúteis.",
        "processes": "- Varredura de partes MIME da mensagem.\n- Download e identificação de file signature (Magic bytes).\n- Remoção de blobs irrelevantes (imagens de rodapé, linkedin icons).\n- Escrita dos arquivos brutos no S3 ou Temp storage.",
        "libraries": "python-magic, base64",
        "classes": ["AttachmentParser", "FileSanitizer"],
        "functions": ["extract_attachments()", "identify_mime_type()", "filter_tracking_pixels()"]
    },
    {
        "id": 11,
        "title": "Pré-processamento: Extração de Metadados e Ghostscript",
        "phase": "Pré-processamento Documental",
        "objective": "Interpretar arquivos PDF de forma limpa garantindo fatiamento apropriado de múltiplas páginas.",
        "processes": "- Load do arquivo binário.\n- Splitting do arquivo em caso de PDFs longos (ex: page 1 a 3 = invoice, 4 a 10 = termos).\n- Parsing de metadados nativos via PyMuPDF.",
        "libraries": "PyMuPDF (fitz)",
        "classes": ["PDFMetadataExtractor", "DocumentSplitter"],
        "functions": ["extract_pdf_pages()", "get_pdf_metadata()", "convert_pdf_to_images()"]
    },
    {
        "id": 12,
        "title": "Pré-processamento: Visão Computacional (Image Normalization)",
        "phase": "Pré-processamento Documental",
        "objective": "Melhorar a qualidade visual do documento antes de entrar no motor OCR para aumentar acurácia.",
        "processes": "- Conversão para Grayscale.\n- Binarização adaptativa OTSU.\n- Morphological transforms (Dilatar e Erodar fontes fracas).\n- Salvar nova imagem consolidada.",
        "libraries": "OpenCV (cv2), Pillow (PIL), NumPy",
        "classes": ["ImageEnhancer", "CV2Pipeline"],
        "functions": ["apply_adaptive_threshold()", "rescale_image_dpi()", "remove_shadows()"]
    },
    {
        "id": 13,
        "title": "Pré-processamento: Correção de Deskewing",
        "phase": "Pré-processamento Documental",
        "objective": "Corrige rotações em faturas que foram escaneadas fisicamente ou tiradas através de celular.",
        "processes": "- Obtenção do ângulo dos blocos de texto.\n- Rotação afim matemática da imagem em -ângulo detectado.\n- Preenchimento de bordas (Background padding).",
        "libraries": "OpenCV, Scikit-Image",
        "classes": ["DeskewProcessor"],
        "functions": ["calculate_skew_angle()", "rotate_image()", "correct_document_perspective()"]
    },
    {
        "id": 14,
        "title": "Armazenamento em Nuvem Raw/Processed (AWS S3)",
        "phase": "Pré-processamento Documental",
        "objective": "Upload dos arquivos processados para o bucket, preparando-os para o OCR sem lotar disco local.",
        "processes": "- Setup do conector boto3.\n- Geração de Pre-Signed URLs.\n- Upload do RAW file e Upload do Processed file.\n- Atualização do path no PostgreSQL Database.",
        "libraries": "boto3",
        "classes": ["S3BucketManager"],
        "functions": ["upload_file_to_s3()", "generate_presigned_url()", "delete_blob_s3()"]
    },
    {
        "id": 15,
        "title": "Extração Híbrida: Setup de Engine Tesseract/EasyOCR",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Implementar uma camada inicial local de reconhecimento ótico para não onerar APIs externas em arquivos simples.",
        "processes": "- Inicialização psm configurations no Tesseract.\n- Chamada assíncrona para extração de String text (Text string pura).\n- Export do OCR bruto para a coleção MongoDB correspondente.",
        "libraries": "Pytesseract, EasyOCR",
        "classes": ["LocalOCREngine", "PytesseractAdapter"],
        "functions": ["extract_text_content()", "get_image_data_boxes()"]
    },
    {
        "id": 16,
        "title": "Integração OCR Avançado em Nuvem (AWS Textract)",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Utilizar IA profunda nativa para documentos complexos e faturas amolecidas de difícil leitura.",
        "processes": "- Integração de boto3 para client do textract.\n- Chamada à API `analyze_expense`.\n- Parsing de Key-Value pairs que o Amazon retorna nativo.\n- Redução / Transformação em DTO padronizado.",
        "libraries": "Boto3",
        "classes": ["AWSTextractAdapter", "ExpenseParserAWS"],
        "functions": ["call_analyze_document()", "map_aws_blocks_to_dto()"]
    },
    {
        "id": 17,
        "title": "Parser de Layouts Espaciais (LayoutLMv3 Integration)",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Adotar um modelo multimodal para entender posições e tabelas. (Ex: a palavra $15 está à direita de Hamburguer).",
        "processes": "- Carregamento e inferência com modelo open-source Transformers via HuggingFace.\n- Identificação de Bound-boxes de itens vs Cabeçalho.\n- Geração de árvore estrutural semântica do documento.",
        "libraries": "Transformers, Torch, HuggingFace Hub",
        "classes": ["LayoutModelPipeline", "SpatialTreeGenerator"],
        "functions": ["load_layout_model()", "predict_visual_elements()", "combine_boxes_and_text()"]
    },
    {
        "id": 18,
        "title": "Integração LLM e Cadeia Semântica (LangChain)",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Conectar o projeto a modelos gigantes (GPT-4T / Claude) para realizar RAG e extração profunda dos blocos de texto.",
        "processes": "- Definição do conector LLM via LangChain (ChatOpenAI).\n- Definição do output_parser com Pydantic.\n- Tratativa de rate-limits no disparo.",
        "libraries": "Langchain, OpenAI, Instructor",
        "classes": ["LLMExtractorClient", "InvoiceOutputSchema(BaseModel)"],
        "functions": ["invoke_llm_chain()", "format_prompt()"]
    },
    {
        "id": 19,
        "title": "Prompt Engineering: Cabeçalho de Invoice",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Sintonizar os prompts instrucionais das IAs focando perfeitamente na identificação clara de Vendor, Date, Total e CNPJ.",
        "processes": "- Criação de prompt templates no Langchain focados em Headings.\n- Mapeamento estrito de datetimes (tratar Mês/Dia vs Dia/Mês).\n- Execução de evals e fine-tuning do prompt.",
        "libraries": "Langchain-core",
        "classes": ["PromptManager", "HeaderExtractorService"],
        "functions": ["build_header_prompt()", "validate_date_formats()"]
    },
    {
        "id": 20,
        "title": "Prompt Engineering: Extração de Linhas/Tabelas (Line Items)",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Isolar e entender tabelas e grids para extrair cada item que foi comprado com suas taxas individuais (Table extraction).",
        "processes": "- Identificação de array de itens da compra.\n- Parsing the Table layout para o LLM.\n- Garantia de fechamento de sum: Soma dos (ValorUnitário*Qtd) deve igualar ao total do item.",
        "libraries": "Pydantic",
        "classes": ["LineItemExtractor", "LineItemSchema"],
        "functions": ["extract_line_items()", "validate_mathematical_sum()"]
    },
    {
        "id": 21,
        "title": "Machine Learning: Cálculo e Sistema de Confidence Score",
        "phase": "OCR e Inteligência Artificial",
        "objective": "Toda IA deve fornecer índice de certeza. Limite aceitável antes de intervir humanamente.",
        "processes": "- Algoritmo para cruzar a probabilidade log-likeliehood do LLM / OCR em campos como Valor Pago.\n- Atribuição de score 0-100%.\n- Se <90%, flag: needs_manual_review = True.",
        "libraries": "NumPy",
        "classes": ["ConfidenceEvaluator", "ConfidenceMetrics"],
        "functions": ["calculate_overall_confidence()", "flag_low_metrics()"]
    },
    {
        "id": 22,
        "title": "Workflows Inteligentes: HITL Dispatcher",
        "phase": "Categorização e Regras de Negócio",
        "objective": "Gestor inteligente de envio. Documentos marcados como duvidosos pela IA vão para a Inbox de Revisores Humanos.",
        "processes": "- Criação da Entidade HumanReviewQueue.\n- Serviço que isola o doc processado mantendo pendente no sistema financeiro.\n- Envio de alerta WebSocket notificando os administradores.",
        "libraries": "FastAPI, PostgreSQL",
        "classes": ["HumanReviewService", "ReviewQueueModel"],
        "functions": ["dispatch_to_review()", "approve_document_manually()"]
    },
    {
        "id": 23,
        "title": "Machine Learning: NLP Email Intent Classifier",
        "phase": "Categorização e Regras de Negócio",
        "objective": "Classifica a mensagem (corpo textual) do email: É uma Fatura Nova? É um Comprovante? É Reclamação?",
        "processes": "- Treinamento local de um SVC ou uso leve de LLM zero-shot no corpo do e-mail.\n- Rotulação das categorias: AP, AR, Receipt, Non-Financial.\n- Fluxo de descarte de spams (Mailing lists de newsletter).",
        "libraries": "Scikit-learn, NLTK",
        "classes": ["EmailIntentClassifier", "IntentTypes(Enum)"],
        "functions": ["predict_intent()", "tokenize_email_body()"]
    },
    {
        "id": 24,
        "title": "Regras de Negócio: Entity Matching (Vendor e Chart of Accounts)",
        "phase": "Categorização e Regras de Negócio",
        "objective": "Associar nomes de empresas lidas no PDF para as empresas previamente cadastradas no DB através de aproximação Fuzzy.",
        "processes": "- Instanciação do thefuzz para comparar strings (ex: 'Amazon Web Srvs' -> 'Amazon').\n- Auto categorização utilizando dados estatísticos anteriores (Ex: Vendor 'Uber' -> Travel).",
        "libraries": "TheFuzz, Levenshtein",
        "classes": ["VendorMatcher", "CategoryPredictor"],
        "functions": ["fuzzy_match_vendor()", "assign_default_category()"]
    },
    {
        "id": 25,
        "title": "Motor de Automação Contábil: Matching Three-Way",
        "phase": "Categorização e Regras de Negócio",
        "objective": "Conciliar Purchase Order (Ordem de Compra), Invoice e Receipt/Boleto.",
        "processes": "- Algoritmo analítico de reconciliação cruzando os 3 documentos via PO Number e Amount.\n- Validação matemática de desvios e tolerâncias (Centavos).",
        "libraries": "Pandas",
        "classes": ["ReconciliationEngine", "ThreeWayMatchRule"],
        "functions": ["compare_po_with_invoice()", "check_tolerance()"]
    },
    {
        "id": 26,
        "title": "Motor Tax & Compliance: IVA / VAT Extractor",
        "phase": "Categorização e Regras de Negócio",
        "objective": "Identificar precisamente tributos desmembrados (Europa - Imposto Adicionado) ou nos EUA para relatórios fiscais adequados.",
        "processes": "- Regex avançada para padrões VIES/CNPJ.\n- Extração percentual vs Bruto/Líquido matematicamente verificado no backend.",
        "libraries": "Python-Re",
        "classes": ["TaxEngine", "TaxBracketValidator"],
        "functions": ["extract_vat_number()", "verify_tax_math()"]
    },
    {
        "id": 27,
        "title": "API Layer: Endpoints de Autenticação Segura JWT",
        "phase": "APIs REST e Integrações",
        "objective": "Montar a proteção ao sistema via rotas JWT / Bearer tokens permitindo login e gerenciamento de permissão.",
        "processes": "- Integração PyJWT.\n- Rotas /login/access-token, hashing BCRYPT da senha.\n- Interceptors dependentes (get_current_active_user) do FastAPI.",
        "libraries": "Passlib, PyJWT",
        "classes": ["AuthHandler", "SecurityDependencies"],
        "functions": ["create_access_token()", "verify_password()", "get_current_user()"]
    },
    {
        "id": 28,
        "title": "API Layer: Políticas Multi-Tenancy (B2B)",
        "phase": "APIs REST e Integrações",
        "objective": "Confinar a visibilidade de dados: a visualização de faturas pela empresa A não enxerga a empresa B.",
        "processes": "- Adição do tenant_id global nas sessões usando context_vars ou restrição no `get_current_user`.\n- Testes RLS (Row Level Security).",
        "libraries": "Contextvars (Built-in)",
        "classes": ["TenantSecurityMiddleware"],
        "functions": ["get_current_tenant()", "filter_by_tenant()"]
    },
    {
        "id": 29,
        "title": "API Layer: Crud Invoices e Endereçamento REST",
        "phase": "APIs REST e Integrações",
        "objective": "Fornecer as rotas expostas para o Frontend consumir visualmente as Invoices, listar faturas vencidas, e atualizá-las.",
        "processes": "- Controllers GET /invoices, POST /invoices/manual, GET /invoices/{id}.\n- Parâmetros Fastapi (Paginação, sorting, filtro de datas).",
        "libraries": "FastAPI",
        "classes": ["InvoiceController", "InvoiceResponseSchema"],
        "functions": ["read_invoices()", "update_invoice_status()"]
    },
    {
        "id": 30,
        "title": "API Layer: Módulo de Analytics e Agragadores Financeiros",
        "phase": "APIs REST e Integrações",
        "objective": "Oferecer rotas performáticas que sumarizam as faturas para gerar os gráficos de fluxo de caixa da tela incial.",
        "processes": "- Views em PostgreSQL + Queries de grupamento (GROUP BY Month).\n- Endpoint /analytics/cashflow.\n- Cache da Query complexa no Redis para velocidade 0ms.",
        "libraries": "SQLAlchemy",
        "classes": ["AnalyticsService"],
        "functions": ["get_cashflow_summary()", "get_spend_by_vendor_chart()"]
    },
    {
        "id": 31,
        "title": "Real Time Communications: WebSockets e Server-Sent Events",
        "phase": "APIs REST e Integrações",
        "objective": "Push vivo na tela dos contadores enquanto o back-end e IA vão digerindo processamentos pendentes de faturas assíncronas.",
        "processes": "- Habilitar FastApi Websocket endpoint /ws/tenant_id.\n- Escutar o canal do Redis (Pub/Sub).\n- Disparo Broadcasting do evento JSON.",
        "libraries": "Redis PubSub, FastAPI WebSockets",
        "classes": ["ConnectionManagerSocket", "EventBroadcaster"],
        "functions": ["connect_ws()", "broadcast_ocr_finished()"]
    },
    {
        "id": 32,
        "title": "Integrações ERP: Conector Plaid / QuickBooks",
        "phase": "APIs REST e Integrações",
        "objective": "Configurar conector de saída. Quando fatura é dada como 'PAID', informar fisicamente o fluxo do Software Contábil do cliente.",
        "processes": "- Módulo Client Connector com HTTPx.\n- Auth Token sync e webhook receiver do ERP da ponta.\n- Push da Entity contábil convertida.",
        "libraries": "Httpx",
        "classes": ["QuickBooksConnector", "PlaidAPIClient"],
        "functions": ["sync_invoice_outbound()", "verify_bank_statement()"]
    },
    {
        "id": 33,
        "title": "Setup do Repositório do Frontend: Vite + Vue3/React",
        "phase": "Front-end SPA Setup",
        "objective": "Construir a estrutura base em Javascript/TypeScript provendendo compilação rápida HMR e robustez estática.",
        "processes": "- `npm create vite@latest` local (Vue/React).\n- Configuração do tsconfig.\n- Setup inicial da árvore `src/components`, `src/views`, `src/store`.",
        "libraries": "Vite, TypeScript, Vue3 ou React18",
        "classes": ["N/A - Componentes UI"],
        "functions": ["main.ts", "App.vue / App.tsx"]
    },
    {
        "id": 34,
        "title": "Front-end: Arquitetura Core e Design System Tailwind",
        "phase": "Front-end SPA Setup",
        "objective": "Aplicar estética corporativa, Dark mode e estilizações Premium utilizando TailwindCSS customizado nos Tokens.",
        "processes": "- Instalação de utilitários Tailwind.\n- Criação do ThemeConfig. Glassmorphism Utilities.\n- Definição do Layout principal com Topbar e Left Sidebar dinâmica.",
        "libraries": "TailwindCSS, HeroIcons, Framer Motion",
        "classes": ["NavBarComponent", "SidebarComponent", "LayoutBase"],
        "functions": ["toggleSidebar()", "toggleDarkMode()"]
    },
    {
        "id": 35,
        "title": "Front-end: State Management e Contexto Auth",
        "phase": "Front-end SPA Setup",
        "objective": "Centralizar login, permissões de rotas no Route Guard, e reatividade global da plataforma.",
        "processes": "- Setup de Store (Redux ou Pinia).\n- Construção do service camada de Rede (Axios Wrapper com Interceptors pro Token JWT).\n- Tela de Autenticação / Forgot Password completas.",
        "libraries": "Axios, Pinia/Redux Toolkit, Vue Router/React Router",
        "classes": ["AuthStore", "HttpInterceptor"],
        "functions": ["login()", "logout()", "validateJwtOnRoute()"]
    },
    {
        "id": 36,
        "title": "Front-end: UI Tela de Inbox - Hub de Correspondências",
        "phase": "Front-end Módulos Visuais",
        "objective": "Interface vital reproduzindo a UX de um email tradicional focado em finanças, permitindo leitura das extrações em lote.",
        "processes": "- Criação da Tabela Complexa de Datatable.\n- Ordenação, Paginação, Botões contextuais de status de faturas (Pendentes, Processadas, Recusadas).",
        "libraries": "TanStack Table / Element Plus",
        "classes": ["InvoiceInboxView", "DataGridComponent"],
        "functions": ["fetchInvoicesPagination()", "massProcessAction()"]
    },
    {
        "id": 37,
        "title": "Front-end: Document Viewers Interativos (Split Screen)",
        "phase": "Front-end Módulos Visuais",
        "objective": "Na esquerda o Preview perfeito do PDF faturado nativo; na direita os campos editáveis extraídos pela IA LangChain.",
        "processes": "- Integração de Viewer PDF Canvas.\n- Sincronização e Highlights entre campo Extraído (Forms na direita) vs Bound-Box da Imagem original (esquerda).",
        "libraries": "React-PDF / PDFjs-dist",
        "classes": ["SplitViewerComponent", "DocumentCanvasPreview", "ExtractionFormsUI"],
        "functions": ["renderPdfPage()", "onFieldFocusHighlightBox()"]
    },
    {
        "id": 38,
        "title": "Front-end: Human-in-the-loop Resolution Center",
        "phase": "Front-end Módulos Visuais",
        "objective": "Queue para os operadores resolverem todos alertas da Confidence score baixa de um e-mail / fatura borrados.",
        "processes": "- Visualização estilo Modal para revisão ultra rápida.\n- Aceite (Submit) e disparo de Put Method que atualizará base do Banco de Dados e disparar aprendizado contínuo (Retrain/Prompt Adjust).",
        "libraries": "Axios, Formik/VeeValidate",
        "classes": ["HitlWorkqueue", "ReviewModal"],
        "functions": ["loadNextInQueue()", "approveManualOverride()"]
    },
    {
        "id": 39,
        "title": "Front-end: Painel Analítico Interativo (Dashboard)",
        "phase": "Front-end Módulos Visuais",
        "objective": "Renderizar gráficos em real-time acoplados ao Redis consumindo métricas que embasarão CEO/CFO nas tomadas de decisões.",
        "processes": "- Chamadas as rotas do backend AnalyticsService.\n- Gráficos Lineares, Bar Charts e Widgets informativos.\n- Atualizações fluidas via Socket connection.",
        "libraries": "Chart.js / Recharts",
        "classes": ["DashboardMainView", "CashflowLineChart", "StatusMetricCards"],
        "functions": ["mountDashboard()", "updateGraphViaSocket()"]
    },
    {
        "id": 40,
        "title": "Front-end: Painéis de Relatórios, Filtros e CSV Exports",
        "phase": "Front-end Módulos Visuais",
        "objective": "Permitir ao contador gerar listagens tributárias das atividades trimestrais (Tax generation).",
        "processes": "- UI de Filtros avançados com múltiplos Inputs (Dates, Fornecedor array, Categoria).\n- Download programático do Arquivo CSV construído através de Blobs de resposta da API.",
        "libraries": "File-saver",
        "classes": ["ReportsModule", "AdvancedFiltersSidebar"],
        "functions": ["triggerReportDownload()", "formatQueryString()"]
    },
    {
        "id": 41,
        "title": "SecOps: Auditorias, Rate limiting e Hardening",
        "phase": "SecOps e Testes Contínuos",
        "objective": "Preparar o software contra abusos OWASP (Layer 7 API protection)",
        "processes": "- Middleware FastAPI com Token Bucket strategy (Slowapi).\n- Ocultação (Data obfuscation) dos painéis e PII logs gravados pelo AppLogger.\n- Criptografia dos dados S3 AES-256 Enabled Server Side.",
        "libraries": "SlowAPI",
        "classes": ["RateLimitMiddleware", "ObfuscatorService"],
        "functions": ["limit_ip_requests()", "mask_iban_numbers()"]
    },
    {
        "id": 42,
        "title": "Testes de Integração Frontend/Backend (Playwright)",
        "phase": "SecOps e Testes Contínuos",
        "objective": "Garantir a ausência de Regressões durante todo o WorkFlow E2E de simulação.",
        "processes": "- Setup de Playwright configurado via headless browser.\n- Execução de Simulação E2E: Disparo de Email -> Backend recebe -> OCR Processa -> WebSocket atualiza Front -> Aparece no Dashboard.",
        "libraries": "Playwright",
        "classes": ["TestE2EWorkflow"],
        "functions": ["test_complete_invoice_pipeline()"]
    },
    {
        "id": 43,
        "title": "Stress & Load Testing - Gargalo Celery e OCR",
        "phase": "SecOps e Testes Contínuos",
        "objective": "Descobrir o limite onde o Celery vai engargalar (1000 Invoices min). Identificar Profiling e Custo AWS/OpenAI.",
        "processes": "- Script Locust para floodar Webhooks paralelos com PDFs densos(>10MB).\n- Analise do comportamento de Redis e Memória e latência API.",
        "libraries": "Locust",
        "classes": ["StressTestRunner"],
        "functions": ["simulate_heavy_load()"]
    },
    {
        "id": 44,
        "title": "Go-Live Preparation: HPA Kubernetes Infra",
        "phase": "Deploy e Manutenção Final",
        "objective": "Garantir tolerância e escala horizontal com implantação no Kubernetes e Helm.",
        "processes": "- Escrever Manifestos Deployment.yaml, Service.yaml.\n- Horizontal Pod Autoscaler associado ao tamanho da fila Celery/Redis via metricas customizadas.\n- CI/CD Deploy Stage Integrado.",
        "libraries": "Kubernetes CLI, Helm",
        "classes": ["N/A - Config"],
        "functions": ["N/A"]
    },
    {
        "id": 45,
        "title": "Monitoramento de APMs contínuo (MLOps/Sentry)",
        "phase": "Deploy e Manutenção Final",
        "objective": "Dar observabilidade de ponta a ponta sobre vazamento de memória e acurácia modelo das predições de IA da versão prod.",
        "processes": "- Integração do Datadog e Sentry para logs de Exceção.\n- Grafana para visualizar dashboard de Erros e Throughput das Invoices processadas.",
        "libraries": "Sentry, Prometheus/Grafana",
        "classes": ["TelemetryManager"],
        "functions": ["capture_exception_sentry()", "push_metric()"]
    },
    {
        "id": 46,
        "title": "Review Formal e Code Freeze",
        "phase": "Deploy e Manutenção Final",
        "objective": "Gatilho de transição entre build principal beta para RC1 (Release Candidate 1).",
        "processes": "- Validação de todas Branches (Merge main).\n- Homologação final UAT (User Acceptance Testing) com stakeholders base.",
        "libraries": "N/A",
        "classes": ["N/A"],
        "functions": ["N/A"]
    },
    {
        "id": 47,
        "title": "Integrações Finais ERPs Auxiliares e Webhooks Inversos",
        "phase": "Deploy e Manutenção Final",
        "objective": "Finalizações de Connectors secundários criados com parcerias na Nuvem.",
        "processes": "- Finalização SDK de integração via API Rest customizável com Zapier / Make.com / PowerAutomate.",
        "libraries": "FastAPI",
        "classes": ["WebhookOutbound"],
        "functions": ["emit_trigger_workflow()"]
    },
    {
        "id": 48,
        "title": "Lançamento Oficial à Prod! V1.0",
        "phase": "Deploy e Manutenção Final",
        "objective": "Disparo inicial do Produto e passagem de conhecimento da equipe do Projeto.",
        "processes": "- Ativação real de Domínios, SSL Lets Encrypt Prod.\n- Operação Inicial com Hand-Off documentado.",
        "libraries": "N/A",
        "classes": ["N/A"],
        "functions": ["N/A"]
    }
]

template = """# Sprint {id:02d}: {title}

## 📌 Contexto Estratégico
- **Fase Arquitetural:** {phase}
- **Objetivo da Sprint:** {objective}

---

## ⚙️ Processos e Regras de Implementação
Abaixo constam as entregas minuciosamente detalhadas desta Sprint:

{processes}

---

## 🛠️ Tecnologias e Bibliotecas Associadas
Os stacks e ecossistemas obrigatórios para a execução:
- {libraries}

---

## 📦 Classes e Entidades Principais
O modelo de domínios ou estruturas sugeridas que precisam ser criadas ou referenciadas:
{classes_md}

---

## ⚡ Funções e Métodos Sistêmicos Críticos
Funções obrigatórias para orquestração interna e manipulação dos fluxos de dados / lógicos:
{functions_md}

---
*Documento autogerado pelo processo automatizado de arquitetura - Inteligência Artificial.*
"""

for s in sprints:
    classes_md = "\\n".join([f"- `{c}`" for c in s["classes"]])
    functions_md = "\\n".join([f"- `{f}`" for f in s["functions"]])
    processes_md = s["processes"]
    
    content = template.format(
        id=s["id"],
        title=s["title"],
        phase=s["phase"],
        objective=s["objective"],
        processes=processes_md,
        libraries=s["libraries"],
        classes_md=classes_md,
        functions_md=functions_md
    )
    
    filename = f"sprint_{s['id']:02d}.md"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Sucesso! {len(sprints)} sprints detalhadas foram salvas e compiladas no diretorio {base_dir}")
