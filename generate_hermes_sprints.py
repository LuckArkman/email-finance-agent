import os
import json

base_dir = r"d:\email-finance-agent\Hermes\Sprints"
os.makedirs(base_dir, exist_ok=True)

sprints = [
    {
        "id": 1,
        "title": "Configuração da Solução Hermes e Projetos Base (.NET 9)",
        "phase": "Fundação e Setup Arquitetural",
        "objective": "Substituir a fundação FastAPI/Poetry por uma solução global em .NET 9 com suporte nativo a Minimal APIs e injeção de dependências robusta.",
        "processes": "- Criar arquivo `Hermes.sln` contendo as pastas lógicas (Services, Core, Infrastructure).\n- Gerar projeto `Hermes.Gateway` utilizando .NET 9 Minimal APIs.\n- Configurar EditorConfig e ferramentas padrão (SonarLint, dotnet format).\n- Estabelecer a esteira inicial no GitHub Actions para CI/CD do monorepo C#.",
        "libraries": ".NET 9 SDK, xUnit, Moq",
        "classes": ["Program.cs", "ServiceCollectionExtensions"],
        "events": ["N/A"]
    },
    {
        "id": 2,
        "title": "Desenvolvimento do Hermes.Gateway e Roteamento Ocelot/YARP",
        "phase": "Fundação e Setup Arquitetural",
        "objective": "Fornecer um ponto unificado de entrada e roteamento que substitui a gestão monolítica de rotas do FastAPI, garantindo Rate Limiting global.",
        "processes": "- Instalar e configurar YARP (Yet Another Reverse Proxy).\n- Definir rotas de fallback `api/hermes/*` redirecionando para os microsserviços do backend.\n- Adicionar middleware de Rate Limiting e proteções XSS e CSRF de borda.",
        "libraries": "YARP, ASP.NET Core Middleware",
        "classes": ["GatewayConfiguration", "RateLimitMiddleware"],
        "events": ["N/A"]
    },
    {
        "id": 3,
        "title": "Orquestração Assíncrona: Hermes.EventBus (RabbitMQ)",
        "phase": "Fundação e Setup Arquitetural",
        "objective": "Substituir o Celery e Redis-tasks por uma Arquitetura Orientada a Eventos (EDA) via mensageria robusta.",
        "processes": "- Instanciar a biblioteca MassTransit em integração com RabbitMQ.\n- Criar os contratos (C# Interfaces) para eventos vitais do sistema.\n- Construir a abstração `IEventBus` para publicações e assinaturas entre os microsserviços.",
        "libraries": "MassTransit, RabbitMQ",
        "classes": ["IEventBus", "RabbitMqEventBus", "IntegrationEvent"],
        "events": ["SystemStartedEvent"]
    },
    {
        "id": 4,
        "title": "Observabilidade e Telemetria: Serilog, OTel e Sentry",
        "phase": "Fundação e Setup Arquitetural",
        "objective": "Mover a camada de logging do appLogger Python para OpenTelemetry e Serilog no ecossistema C# para visibilidade centralizada.",
        "processes": "- Configuração do Serilog enriquecido com CorrelationIds.\n- Setup de Tracing via OpenTelemetry.\n- Integração com Prometheus para métricas e Sentry para captura de exceções globais.",
        "libraries": "Serilog, OpenTelemetry, Sentry.AspNetCore",
        "classes": ["TelemetryStartup", "ExceptionMiddleware"],
        "events": ["N/A"]
    },
    {
        "id": 5,
        "title": "Integração do Banco Relacional: PostgreSQL + Entity Framework Core 9",
        "phase": "Fundação e Setup Arquitetural",
        "objective": "Eliminar o SQLAlchemy e MongoDB; migrar toda a base lógica de entidades relacionais para EF Core.",
        "processes": "- Criação do DbContext global `HermesDbContext` com mapeamento fluente.\n- Configuração inicial das strings de conexão.\n- Criação do mecanismo inicial de Migrations (`dotnet ef migrations add Initial`).",
        "libraries": "Microsoft.EntityFrameworkCore.PostgreSQL, Npgsql",
        "classes": ["HermesDbContext", "BaseEntity"],
        "events": ["N/A"]
    },
    {
        "id": 6,
        "title": "Arquitetura Multi-Tenant: Isolamento e Identificadores Globais",
        "phase": "Módulo Hermes.Identity",
        "objective": "Garantir a total separação de dados dos clientes (Multi-Tenancy SaaS) injetando TenantId em cada Query e Entidade.",
        "processes": "- Adição do campo `TenantId` na classe `BaseEntity`.\n- Implementação de Global Query Filters no `HermesDbContext` para evitar fugas de dados.\n- Serviço `ITenantProvider` que extrai o ID do Tenant a partir de Headers ou Tokens JWT.",
        "libraries": "EF Core Global Filters",
        "classes": ["ITenantProvider", "TenantInterceptor", "TenantContext"],
        "events": ["TenantCreatedEvent"]
    },
    {
        "id": 7,
        "title": "Segurança e Autenticação: Hermes.Identity e JWT",
        "phase": "Módulo Hermes.Identity",
        "objective": "Prover login seguro, geração de tokens JWT (Access e Refresh) e MFA, convertendo os scripts FastAPI/Passlib.",
        "processes": "- Migrar Password Hashing (Bcrypt) nativo ou PBKDF2/Identity.\n- Criar rotas de Minimal APIs `/auth/login`, `/auth/register`.\n- Geração de Claims Principal (Roles, Permissions) e assinatura assimétrica do JWT.",
        "libraries": "Microsoft.AspNetCore.Authentication.JwtBearer",
        "classes": ["AuthService", "TokenGenerator", "UserCredentials"],
        "events": ["UserLoggedInEvent", "UserRegisteredEvent"]
    },
    {
        "id": 8,
        "title": "Modelagem de Permissões: Users, Roles e Subscriptions",
        "phase": "Módulo Hermes.Identity",
        "objective": "Centralizar a autorização de quem pode ver faturas ou alterar configurações usando políticas de Authorization do ASP.NET.",
        "processes": "- Criação das Entidades de Domínio `User`, `Role`, `Permission`.\n- Criação de Custom Authorization Policies (`RequireClaim(\"Permission\", \"Invoices.Write\")`).\n- Construção do Endpoint CRUD para gerir acessos dentro do tenant.",
        "libraries": "ASP.NET Core Authorization",
        "classes": ["RoleManager", "PermissionPolicyProvider"],
        "events": ["UserRoleUpdatedEvent"]
    },
    {
        "id": 9,
        "title": "Migração de Entidades Financeiras: Invoices e Items",
        "phase": "Modelo de Domínio Core",
        "objective": "Materializar a estrutura de Faturas, Itens de Fatura (Line Items), Fornecedores e Recibos na base relacional do PostgreSQL.",
        "processes": "- Mapeamento EF Core das classes `Invoice`, `InvoiceItem` e `Vendor`.\n- Configuração de relações Um-para-Muitos e restrições de *Foreign Key* on-delete-cascade.\n- Geração da Migration correspondente para atualizar a infraestrutura de dados.",
        "libraries": "EF Core Fluent API",
        "classes": ["Invoice", "InvoiceItem", "InvoiceConfiguration"],
        "events": ["InvoiceCreatedEvent"]
    },
    {
        "id": 10,
        "title": "Hermes.Email: Conexão IMAP Nativa C#",
        "phase": "Módulo Hermes.Email",
        "objective": "Substituir scripts `aioimaplib` Python por bibliotecas maduras em .NET (MailKit) para leitura segura de provedores externos.",
        "processes": "- Incorporar MailKit para leitura de IMAP/POP3 via SSL.\n- Construir Worker Service (BackgroundService) contínuo ouvindo caixas de correio.\n- Implementar processador que emite eventos ao receber mensagens não lidas.",
        "libraries": "MailKit, MimeKit",
        "classes": ["ImapListenerService", "EmailSyncJob"],
        "events": ["EmailReceivedEvent"]
    },
    {
        "id": 11,
        "title": "Hermes.Email: Integração Microsoft Graph API",
        "phase": "Módulo Hermes.Email",
        "objective": "Permitir onboarding corporativo OAuth com Microsoft 365/Outlook usando o SDK oficial em C#.",
        "processes": "- Implementar autenticação via `Microsoft.Identity.Client` (MSAL.NET).\n- Usar o SDK `Microsoft.Graph` para consultar `/me/messages` e inscrever Webhooks.\n- Capturar anexos de emails recebidos na nuvem corporativa.",
        "libraries": "Microsoft.Graph, Azure.Identity",
        "classes": ["GraphApiClient", "GraphWebhookReceiver"],
        "events": ["EmailReceivedEvent"]
    },
    {
        "id": 12,
        "title": "Hermes.Email: Ingestão Google Workspace (Gmail)",
        "phase": "Módulo Hermes.Email",
        "objective": "Trazer clientes G-Suite para a arquitetura com o Google.Apis em C# e Google Pub/Sub.",
        "processes": "- Setup de contas de serviço e credenciais GCP.\n- Criação de endpoints (Webhooks) para rececionar os push events do Gmail.\n- Conversão da base do Gmail Message para a abstração interna do sistema.",
        "libraries": "Google.Apis.Gmail.v1",
        "classes": ["GmailServiceFactory", "GmailPushHandler"],
        "events": ["EmailReceivedEvent"]
    },
    {
        "id": 13,
        "title": "Hermes.Email: Separação de Corpo, Metadados e Anexos",
        "phase": "Módulo Hermes.Email",
        "objective": "Ao receber um e-mail bruto, isolar PDFs vitais e descartar assinaturas de e-mail e ícones (Magic Bytes).",
        "processes": "- Lógica condicional percorrendo partições MIME.\n- Análise baseada em MimeKit para verificar `ContentType` e heurística de descarte (tamanho < 10kb).\n- Preparo e buffer do byte-array para o pipeline de armazenamento.",
        "libraries": "MimeKit",
        "classes": ["AttachmentFilter", "MimeMessageParser"],
        "events": ["AttachmentExtractedEvent"]
    },
    {
        "id": 14,
        "title": "Hermes.Documents: Armazenamento Blob (S3 e Local)",
        "phase": "Módulo Hermes.Documents",
        "objective": "Receber anexos do EventBus e salvar permanentemente em Block Storage ao invés do sistema de arquivos local.",
        "processes": "- Criação do Microsserviço `Hermes.Documents` que assina `AttachmentExtractedEvent`.\n- Upload em paralelo (Stream) para buckets Amazon S3 usando o SDK AWS .NET.\n- Gravação da Entidade de DB `Document` referenciando a S3 Key gerada.",
        "libraries": "AWSSDK.S3",
        "classes": ["DocumentStorageService", "S3BlobClient"],
        "events": ["DocumentStoredEvent"]
    },
    {
        "id": 15,
        "title": "Hermes.Documents: API de Upload Manual e Sanitização",
        "phase": "Módulo Hermes.Documents",
        "objective": "Disponibilizar endpoint de Minimal APIs para que o front-end (React) faça upload de faturas arrastadas (Drag&Drop).",
        "processes": "- Endpoint `POST /api/hermes/documents/upload`.\n- Validação do `IFormFile` e bloqueio de executáveis ou corrompidos via Magic Bytes verification.\n- Retorna o `DocumentId` e despoleta `DocumentStoredEvent`.",
        "libraries": "ASP.NET Core Http",
        "classes": ["UploadController", "FileSanitizer"],
        "events": ["DocumentStoredEvent"]
    },
    {
        "id": 16,
        "title": "Hermes.OCR: Motor de Despacho (Dispatcher) e Filas",
        "phase": "Módulo Hermes.OCR",
        "objective": "Orquestrar filas de OCR intensivas usando MassTransit Workers, absorvendo o trabalho do Celery Python.",
        "processes": "- Microsserviço `Hermes.OCR` com background workers assíduos no RabbitMQ consumindo `DocumentStoredEvent`.\n- Setup de paralelismo configurável via TPL (Task Parallel Library) `Parallel.ForEachAsync`.",
        "libraries": "MassTransit.RabbitMQ",
        "classes": ["OcrJobConsumer", "JobDispatcher"],
        "events": ["OcrStartedEvent", "OcrFailedEvent"]
    },
    {
        "id": 17,
        "title": "Hermes.OCR: Visão Computacional (Deskewing e Enhancements)",
        "phase": "Módulo Hermes.OCR",
        "objective": "Antes da leitura, limpar ruído visual (ex: fotos pelo celular) das faturas, substituindo o pipeline OpenCV do Python.",
        "processes": "- Uso do Emgu CV ou ImageSharp para converter a imagem em Greyscale e aplicar Thresholding Otsu.\n- Correção de rotação (Deskew) determinando ângulos base e rotacionando.\n- Emissão temporária de imagens otimizadas para processamento OCR.",
        "libraries": "Emgu.CV / SixLabors.ImageSharp",
        "classes": ["ImageEnhancementPipeline", "DeskewProcessor"],
        "events": ["N/A"]
    },
    {
        "id": 18,
        "title": "Hermes.OCR: Integração Tesseract nativa (.NET Wrapper)",
        "phase": "Módulo Hermes.OCR",
        "objective": "Extração de strings brutas de imagens e scans locais sem requisições caras a cloud.",
        "processes": "- Importação do TesseractEngine wrapper (.NET).\n- Processamento da imagem normalizada.\n- Retorno de Strings e confianças médias associadas.\n- Emissão de evento de finalização com a RawString.",
        "libraries": "Tesseract",
        "classes": ["TesseractOcrEngine", "OcrResult"],
        "events": ["OcrCompletedEvent"]
    },
    {
        "id": 19,
        "title": "Hermes.OCR: Parsing de PDFs nativos e Extração Textual",
        "phase": "Módulo Hermes.OCR",
        "objective": "Otimizar tempo e custo extraindo texto embutido em PDFs vetoriais eletrônicos (PDF/A) sem passar pela malha OCR.",
        "processes": "- Interceptar ficheiros PDF no `Hermes.OCR`.\n- Recurso a PdfPig (UglyToad) para verificar a presença de strings limpas.\n- Bypass do OCR visual se o arquivo for plenamente digital, disparando a conclusão instantânea.",
        "libraries": "UglyToad.PdfPig",
        "classes": ["PdfTextExtractor", "DigitalPdfStrategy"],
        "events": ["OcrCompletedEvent"]
    },
    {
        "id": 20,
        "title": "Hermes.Extraction: Pipeline de Integração RAG LLMs",
        "phase": "Módulo Hermes.Extraction & IA",
        "objective": "Substituir o LangChain em Python usando integrações semânticas em C# para conversar com LLMs na fase de Extração.",
        "processes": "- Consumir o `OcrCompletedEvent`.\n- Integrar bibliotecas oficiais do OpenAI SDK para C# ou Microsoft.SemanticKernel.\n- Definição da fachada de abstração de LLM (`ILLMClient`).",
        "libraries": "Microsoft.SemanticKernel, Azure.AI.OpenAI",
        "classes": ["ExtractionConsumer", "LlmClientFactory"],
        "events": ["N/A"]
    },
    {
        "id": 21,
        "title": "Hermes.Extraction: Prompt Engineering com Instructor .NET",
        "phase": "Módulo Hermes.Extraction & IA",
        "objective": "Modelagem determinística (Function Calling) convertendo texto caótico do OCR em um Record C# strongly-typed.",
        "processes": "- Traduzir os antigos schemas Pydantic do Python para Records do C# (ex: `public record InvoiceExtracted(...)`).\n- Aplicar Function Calling e System Prompts rígidos focando Data, Fornecedor, CNPJ/NIF e Montante Total.\n- Parsing validado do JSON de retorno.",
        "libraries": "System.Text.Json",
        "classes": ["PromptBuilder", "InvoiceExtractionModel"],
        "events": ["ExtractionCompletedEvent"]
    },
    {
        "id": 22,
        "title": "Hermes.Extraction: Extração em Massa de Line Items (Tabelas)",
        "phase": "Módulo Hermes.Extraction & IA",
        "objective": "Processamento minucioso do detalhe da fatura linha a linha.",
        "processes": "- Ajuste de prompting avançado para compreender matrizes tabulares no texto OCR.\n- C# records contendo `IEnumerable<LineItemExtracted>`.\n- Validação C# pura assegurando que a soma dos itens (Qtd*Preço) corresponde ao total capturado.",
        "libraries": "N/A",
        "classes": ["LineItemExtractionRule", "MathValidator"],
        "events": ["ExtractionCompletedEvent"]
    },
    {
        "id": 23,
        "title": "Hermes.Extraction: Confidence Score e Regras Heurísticas",
        "phase": "Módulo Hermes.Extraction & IA",
        "objective": "Migrar a análise Log-Likelihood e probabilidade de incerteza da IA.",
        "processes": "- Verificação de pontuação retornada pelo provedor de AI e casamento heurístico no C# (Regex do CNPJ cruza com o do LLM?).\n- Se confiança < 90%, associar *FlagReviewRequired* no evento emitido.",
        "libraries": "System.Text.RegularExpressions",
        "classes": ["ConfidenceEvaluator", "HeuristicMatcher"],
        "events": ["ExtractionCompletedEvent"]
    },
    {
        "id": 24,
        "title": "Hermes.AI: Conexão a Modelos Locais via Ollama",
        "phase": "Módulo Hermes.AI Core",
        "objective": "Garantir o processamento da IA corporativa On-Premises suportando o Llama3 localmente.",
        "processes": "- Cliente HTTP `HttpClient` parametrizado para contactar a API REST do Ollama hospedada internamente.\n- Parsing manual e robusto das respostas geradas pelo `llama3` local.",
        "libraries": "System.Net.Http",
        "classes": ["OllamaClient", "OllamaChatCompletion"],
        "events": ["N/A"]
    },
    {
        "id": 25,
        "title": "Módulo PgVector: Configuração da Base e Extensões",
        "phase": "Módulo Hermes.Vector & RAG",
        "objective": "Abandono sumário do ChromaDB. O PostgreSQL do Hermes assumirá o papel vetorial simultaneamente aos dados relacionais.",
        "processes": "- Ativação do script de DB `CREATE EXTENSION vector;`.\n- Incorporação do `Npgsql.EntityFrameworkCore.PostgreSQL.NodaTime` e suporte a vetor via `pgvector-dotnet`.\n- Criação do campo `public Vector Embedding { get; set; }` na tabela de Invoices.",
        "libraries": "Pgvector.EntityFrameworkCore",
        "classes": ["HermesDbContext", "VectorMigration"],
        "events": ["N/A"]
    },
    {
        "id": 26,
        "title": "Hermes.Vector: Geração de Embeddings com Nomic-Embed",
        "phase": "Módulo Hermes.Vector & RAG",
        "objective": "Geração das dimensões vetorizadas do texto das faturas a cada vez que a extração termina.",
        "processes": "- Escuta do `ExtractionCompletedEvent`.\n- Disparo à API Ollama (`/api/embeddings`) usando o modelo `nomic-embed-text` com payload do corpo do e-mail e itens da fatura.\n- Gravação das 768 dimensões resultantes na tabela do PostgreSQL conectada à fatura correspondente.",
        "libraries": "N/A",
        "classes": ["VectorJobConsumer", "EmbeddingService"],
        "events": ["VectorIndexedEvent"]
    },
    {
        "id": 27,
        "title": "Hermes.Vector: API de Procura Semântica (Cosine Similarity)",
        "phase": "Módulo Hermes.Vector & RAG",
        "objective": "Poder realizar procuras mágicas em C# com Queries Naturais.",
        "processes": "- Endpoint Minimal API `/api/hermes/search?q=luz da semana passada`.\n- Geração de embedding da query `q`.\n- LINQ com PgVector: `.OrderBy(x => x.Embedding.CosineDistance(queryEmbedding))`.\n- Retorno ultra rápido graças ao índice HNSW do Postgres.",
        "libraries": "Pgvector EF LINQ",
        "classes": ["SemanticSearchController", "SearchQueryService"],
        "events": ["N/A"]
    },
    {
        "id": 28,
        "title": "Módulo ReviewQueue: Filas Human-in-the-Loop",
        "phase": "Aplicações de Negócio Core",
        "objective": "Intervenção manual para faturas confusas.",
        "processes": "- Captura de faturas marcadas com `FlagReviewRequired`.\n- API CRUD (`GET /api/hermes/review`, `PUT /api/hermes/review/{id}`) exposta para a listagem visual no Frontend.\n- Possibilidade de sobrescrever manualmente e gravar o log de alteração de auditoria.",
        "libraries": "N/A",
        "classes": ["ReviewController", "AuditLogService"],
        "events": ["InvoiceManuallyReviewedEvent"]
    },
    {
        "id": 29,
        "title": "Hermes.Reconciliation: Motor de Conciliação Automático",
        "phase": "Aplicações de Negócio Core",
        "objective": "Lógica financeira pesada que cruza Comprovativos de Pagamentos com Faturas por pagar, dando baixa nas contas.",
        "processes": "- Ao inserir Comprovativo, iniciar serviço que cruza IBAN extraído, NIF da entidade, Data e Valor em tolerância (centavos) com a tabela Invoices (Status=Pending).\n- Alterar o Status para `Reconciled`.\n- Emissão de Evento `InvoiceReconciledEvent` no Bus de mensagens.",
        "libraries": "N/A",
        "classes": ["ReconciliationEngine", "ToleranceMatcher"],
        "events": ["InvoiceReconciledEvent"]
    },
    {
        "id": 30,
        "title": "Hermes.Analytics: Cálculos de Cashflow e Agregações SQL",
        "phase": "Aplicações de Negócio Core",
        "objective": "Alimentar os Dashboards gráficos de alto desempenho no React substituindo agregações em Python.",
        "processes": "- Endpoints HTTP para Agregação temporal usando EF Core Dapper ou SQL direto otimizado para totalizadores.\n- Views Materializadas no PostgreSQL (refrescadas por eventos diários) para evitar On-The-Fly calculos massivos em Big Data.",
        "libraries": "Dapper, EF Core Views",
        "classes": ["AnalyticsController", "DashboardKpisService"],
        "events": ["N/A"]
    },
    {
        "id": 31,
        "title": "Hermes.Notifications: Subscrições SignalR Base",
        "phase": "WebSockets & Eventos em Tempo Real",
        "objective": "Substituir de forma radical o primitivo WebSockets FastAPI por SignalR, a tecnologia padrão ouro de Tempo-real do .NET.",
        "processes": "- Implementação do `NotificationHub : Hub` centralizado no backend.\n- Configurar autenticação JWT para acesso às ligações Socket.\n- Grupos por Tenant: `Groups.AddToGroupAsync(Context.ConnectionId, user.TenantId)` impedindo envio de sockets de uma empresa para a outra.",
        "libraries": "Microsoft.AspNetCore.SignalR",
        "classes": ["NotificationHub", "SignalRAuthenticator"],
        "events": ["N/A"]
    },
    {
        "id": 32,
        "title": "Hermes.Notifications: Dispatcher Evento-para-Cliente",
        "phase": "WebSockets & Eventos em Tempo Real",
        "objective": "Ouvir o bus de eventos global (RabbitMQ) e retransmitir para o ecrã local React em frações de segundo.",
        "processes": "- Consumidor de Eventos como `ExtractionCompletedEvent` no `Hermes.Notifications`.\n- Injetar dependência `IHubContext<NotificationHub>`.\n- Enviar pacote JSON final: `.Clients.Group(tenantId).SendAsync(\"InvoiceProcessed\", invoiceData)`.",
        "libraries": "MassTransit, SignalR",
        "classes": ["EventToSocketBroadcaster"],
        "events": ["N/A"]
    },
    {
        "id": 33,
        "title": "Frontend (React): Migração de Rotas e Refatoração de Cliente HTTP",
        "phase": "Adaptação e Integração do Frontend",
        "objective": "Ajustar o React Vite existente para consumir `/api/hermes/*` substituindo chamadas legadas ao `/api/v1/` de Python.",
        "processes": "- Atualizar BaseURLs no Axios Interceptor.\n- Atualizar Tipagens do TypeScript baseadas nos novos Data Contracts (Records C#) de respostas que venham com novos formatos ou casing (CamelCase por omissão em System.Text.Json).",
        "libraries": "Axios, TypeScript",
        "classes": ["AxiosClient", "HttpServices"],
        "events": ["N/A"]
    },
    {
        "id": 34,
        "title": "Frontend (React): Substituição do Cliente WebSocket por SignalR",
        "phase": "Adaptação e Integração do Frontend",
        "objective": "A UI do Dashboard e Inbox que usa `new WebSocket()` precisa de ser migrada para usar o SignalR JS Client.",
        "processes": "- `npm install @microsoft/signalr`.\n- Criar `useSignalR` React Hook gerindo o ciclo de vida e reconnection automática.\n- Fazer o bind de escutas como `connection.on(\"InvoiceProcessed\", data => updateZustandStore(data))`.",
        "libraries": "@microsoft/signalr",
        "classes": ["useSignalR.ts", "SignalRStore"],
        "events": ["N/A"]
    },
    {
        "id": 35,
        "title": "Frontend (React): Componente AgentChat com SignalR Streaming",
        "phase": "Adaptação e Integração do Frontend",
        "objective": "A experiência ChatGPT-like com RAG do Hermes será feita via streaming pelo SignalR permitindo fluidez fantástica.",
        "processes": "- Refazer a tela de AgentChat.\n- Endpoint C# `IAsyncEnumerable<string>` streamado via SignalR.\n- Atualização do estado de conversação caractere por caractere via React state append.",
        "libraries": "React, Zustand",
        "classes": ["AgentChatComponent", "ChatMessageList"],
        "events": ["N/A"]
    },
    {
        "id": 36,
        "title": "Hermes.Agent: RAG e Construção de Agentes Autônomos",
        "phase": "Aplicações de Negócio Core & Chat",
        "objective": "O Cérebro da Operação. Recebe queries do React, pergunta ao vetor e constrói respostas conversacionais baseadas nas finanças da empresa.",
        "processes": "- Converter query para Embedding.\n- Pesquisa semântica no PgVector (Retrieval).\n- Injeção das Top 5 Faturas como Contexto (Augmented).\n- Chamada ao LLM (Ollama/OpenAI) pedindo resumo textual e enviando resposta Streamada (Generation).",
        "libraries": "Semantic Kernel / OpenAI SDK",
        "classes": ["RagOrchestrator", "AgentStreamService"],
        "events": ["N/A"]
    },
    {
        "id": 37,
        "title": "Migração de Testes Automatizados C# xUnit",
        "phase": "SecOps e Testes Contínuos",
        "objective": "Todo o PyTest vai para o caixote. Iniciar malha de proteção de testes Unitários focada em C#.",
        "processes": "- Criar projetos `Hermes.Tests.Unit` e `Hermes.Tests.Integration`.\n- Uso extensivo de Moq para simular dependências e EventBus (Sem ligar RabbitMQ local).\n- Testes de Controladores Minimal API usando TestServer in-memory.",
        "libraries": "xUnit, Moq, FluentAssertions",
        "classes": ["IntegrationTestFixture", "ServiceTests"],
        "events": ["N/A"]
    },
    {
        "id": 38,
        "title": "Performance Optimization: Caching Distribuído com Redis C#",
        "phase": "Segurança e Otimização",
        "objective": "Diminuir a carga do Postgres e processamento repetitivo de queries pesadas através da Cache nativa do .NET (IDistributedCache).",
        "processes": "- Integração de `StackExchange.Redis`.\n- Injectar `IDistributedCache` no Controller de Analytics.\n- Invalidação de chaves de cache (Eviction) reativa e baseada em eventos do EventBus (`InvoiceCreatedEvent` limpa a cache do Mês X).",
        "libraries": "StackExchange.Redis",
        "classes": ["RedisCacheService", "CacheInvalidatorConsumer"],
        "events": ["N/A"]
    },
    {
        "id": 39,
        "title": "Proteções de Endpoint: HSTS, Anti-CSRF e Data Protection",
        "phase": "Segurança e Otimização",
        "objective": "Garantir padrão OWASP Top 10 na plataforma.",
        "processes": "- Adição de HttpOnly, Secure flags nos Cookies (se forem usados para Refresh Token).\n- Injeção de Data Protection APIs do .NET para gerar keys temporárias seguras.",
        "libraries": "Microsoft.AspNetCore.DataProtection",
        "classes": ["SecurityConfiguration", "CorsSetup"],
        "events": ["N/A"]
    },
    {
        "id": 40,
        "title": "Resiliência a Falhas: Retry Policies e Circuit Breakers",
        "phase": "Segurança e Otimização",
        "objective": "Impedir bloqueio do sistema se o serviço AI (Ollama/OpenAI) ou o IMAP ficarem indisponíveis momentaneamente.",
        "processes": "- Incorporar a framework Polly ao `HttpClient`.\n- Configurar Circuit Breaker (Quebra se ocorrerem > 5 falhas seguidas).\n- Exponential Backoff para leitura de email falhada.",
        "libraries": "Polly",
        "classes": ["ResiliencePolicyConfiguration", "HttpHandlers"],
        "events": ["N/A"]
    },
    {
        "id": 41,
        "title": "Dockerização dos Microsserviços e Monorepo",
        "phase": "Deploy e Manutenção Final",
        "objective": "Substituir o Docker-compose Python, acomodando a buildização compilada de ambientes C#.",
        "processes": "- Escrever Multi-Stage Dockerfiles assentes em imagens .NET 9 Alpine / ASP.NET 9 (Publish Trimmed/AOT se aplicável para menor consumo de RAM).\n- Atualizar `docker-compose.yml` para lançar Serviços Hermes, RabbitMQ, PostgreSQL e Redis em orquestração limpa.",
        "libraries": "Docker",
        "classes": ["Dockerfile", "docker-compose.yml"],
        "events": ["N/A"]
    },
    {
        "id": 42,
        "title": "HealthChecks Nativos (.NET Health Checks)",
        "phase": "Deploy e Manutenção Final",
        "objective": "Permitir ao Docker e Kubernetes perceber o estado clínico dos Microsserviços Hermes.",
        "processes": "- Instalar `AspNetCore.HealthChecks.UI` e probes para Postgres, RabbitMQ e Redis.\n- Expor endpoint `/health/ready` e `/health/live` na board Gateway do Hermes.",
        "libraries": "AspNetCore.HealthChecks",
        "classes": ["HealthCheckConfiguration"],
        "events": ["N/A"]
    },
    {
        "id": 43,
        "title": "Integrações Webhooks de Terceiros e APIs Reversas",
        "phase": "Implantações B2B",
        "objective": "Permitir exportação direta das faturas para sistemas de gestão (SAP, Sage, QuickBooks).",
        "processes": "- Criar um Serviço Webhook Outbound que efetua `POST` externo assim que um documento alcança a fase Finalizada.\n- Registo dos endpoints de parceiros em tabela C# e tentativa com Polly de entrega garantida.",
        "libraries": "HttpClient",
        "classes": ["WebhookOutboundDispatcher"],
        "events": ["N/A"]
    },
    {
        "id": 44,
        "title": "Kubernetes K8s Manifestos e Horizontal Pod Autoscaling (HPA)",
        "phase": "Deploy e Manutenção Final",
        "objective": "Permitir a escala gigante da plataforma isolando pods de API dos pods de Processamento pesado (OCR).",
        "processes": "- Atualizar diretório `/k8s/` com arquivos yaml dos novos contentores `.NET`.\n- Configurar Keda ou HPA focado no tamanho da fila do RabbitMQ: Se subirem as mensagens OCR, sobe a quantidade de pods do Microsserviço Hermes.OCR.",
        "libraries": "Kubernetes Helm, Keda",
        "classes": ["N/A - Manifests Yaml"],
        "events": ["N/A"]
    },
    {
        "id": 45,
        "title": "Simulação End-To-End, Homologação B2B e Lançamento (V2.0 Hermes)",
        "phase": "Deploy e Manutenção Final",
        "objective": "Corte definitivo e transição do Monólito Python para a Cloud Distribuída Hermes .NET 9.",
        "processes": "- Congelar dependências e código Python. (Code Freeze V1).\n- Executar Playwright scripts para comprovar se a paridade de funções está 1:1.\n- Go-live produtivo para os clientes com acompanhamento dos Grafana Dashboards preenchidos pelo Serilog .NET.",
        "libraries": "N/A",
        "classes": ["N/A"],
        "events": ["N/A"]
    }
]

template = """# Sprint {id:02d}: {title}

## 📌 Contexto Estratégico e Arquitetural
- **Fase Hermes (.NET 9):** {phase}
- **Objetivo da Sprint:** {objective}

---

## ⚙️ Processos e Regras de Implementação (Migração Python -> C#)
Abaixo constam as diretrizes minuciosamente detalhadas desta Sprint:

{processes}

---

## 🛠️ Tecnologias e Bibliotecas C#
Os stacks obrigatórios para a execução no novo ecossistema:
- {libraries}

---

## 📦 Classes, Microsserviços e Contratos
O modelo de domínios ou estruturas C# sugeridas que precisam ser criadas ou referenciadas:
{classes_md}

---

## ⚡ Barramento de Eventos (EventBus/SignalR)
Eventos obrigatórios associados a esta entrega na arquitetura distribuída:
{events_md}

---
*Documento autogerado pelo arquiteto de IA - Plano de Implantação Hermes v2.0.*
"""

for s in sprints:
    classes_md = "\\n".join([f"- `{c}`" for c in s["classes"]])
    events_md = "\\n".join([f"- `{e}`" for e in s["events"]])
    processes_md = s["processes"]
    
    content = template.format(
        id=s["id"],
        title=s["title"],
        phase=s["phase"],
        objective=s["objective"],
        processes=processes_md,
        libraries=s["libraries"],
        classes_md=classes_md,
        events_md=events_md
    )
    
    filename = f"hermes_sprint_{s['id']:02d}.md"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Sucesso! {len(sprints)} sprints ricas e minuciosas foram geradas e salvas em {base_dir}")
