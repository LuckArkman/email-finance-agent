# Walkthrough Completo: Integração, Docker e Estabilização .NET 9

Este documento resume de forma detalhada todas as implementações, refatorações e correções realizadas nas últimas iterações do projeto Hermes, focando na integração completa do ecossistema e na estabilização do ambiente Docker.

---

## 1. Integração React ↔ .NET Gateway ↔ Hermes Agent

Estabelecemos um fluxo de comunicação unidirecional e seguro onde o Frontend (React) comunica exclusivamente com o Gateway (.NET), que por sua vez atua como um proxy seguro para o Hermes Agent (Python).

### Backend .NET (`Hermes.Gateway`)
- **[NOVO] `HermesAgentClient.cs`**: Criado um `HttpClient` tipado dedicado a encapsular as chamadas REST para a API do Hermes Agent (porta `8642`).
  - Implementa resiliência nativa com `AddStandardResilienceHandler()` (Circuit Breaker e Retry automáticos).
  - Encapsula chamadas como `GetStatusAsync()`, `GetSessionsAsync()`, e `ChatAsync()`.
- **[NOVO] `AgentProxyController.cs`**: Um novo Controller exposto para o React, contendo endpoints como `/api/hermes/agent/status` e `/api/hermes/agent/chat`. Ele garante que credenciais e lógica de negócio permaneçam ocultas do cliente.
- **Configuração**: Adicionada a secção `HermesAgent` no `appsettings.json` para definir o `BaseUrl` e a `ApiKey` de comunicação inter-serviços.

### Frontend React
- **[MODIFICADO] `services/api.ts`**: Reestruturado para incluir o namespace `agentApi`. Todas as chamadas para o agente de IA agora apontam para o endpoint `/api/hermes/agent/...` do .NET Gateway.
- **[MODIFICADO] `AgentChat.tsx`**: A interface de chat foi completamente ligada à API real:
  - **Status ao Vivo**: Polling do estado do agente (Online/Offline) e do modelo em uso.
  - **Histórico**: Recuperação das últimas sessões de chat através da API.
  - **Interação REST**: Substituição de WebSockets (SignalR) temporariamente por chamadas REST puras via POST para simplificar a infraestrutura atual e garantir estabilidade imediata.

---

## 2. Orquestração com Docker Compose

O ficheiro `docker-compose.yml` foi completamente reescrito para abranger todo o ecossistema (12 serviços), garantindo isolamento de rede, ordem de arranque correta e healthchecks adequados.

### Novos Serviços Adicionados
- **`ollama`**: Serviço de IA local. Faz o pull automático do modelo `hermes3:8b` no arranque, essencial para o motor do agente.
- **`hermes-agent`**: O motor autónomo Python (Nous Research). Mapeia volumes locais para manter estado (`/root/.hermes`) e expõe a porta `8642` para o Gateway.
- **Todos os Microsserviços .NET**: `gateway`, `identity`, `extraction`, `reconciliation`, `notifications`, `analytics`, `vector`, `review-queue`. Todos compilados a partir de um Dockerfile centralizado.

### Melhorias na Infraestrutura
- **Rede Privada**: Todos os serviços comunicam de forma segura através da rede bridge `hermes-net`.
- **Healthchecks**: Implementados healthchecks rigorosos em *todos* os serviços. O `depends_on` agora usa a diretiva `condition: service_healthy` (ex: o `gateway` só arranca depois do `postgres` e `rabbitmq` estarem saudáveis).
- **Variáveis de Ambiente (.env)**: Criado um `.env.example` consolidando chaves críticas como `JWT_SECRET`, configurações de e-mail IMAP/SMTP e chaves de API (`HERMES_API_SERVER_KEY`).

---

## 3. Resolução de Conflitos de Build (.NET 9)

Durante a fase de compilação da infraestrutura Docker, deparamo-nos com falhas severas que foram sistematicamente diagnosticadas e resolvidas:

### Conflitos de Versão (.NET 9 vs .NET 10)
- **Problema**: O `Dockerfile` base utilizava imagens do SDK e Runtime do **.NET 9**. Contudo, vários ficheiros `.csproj` (como `Hermes.Analytics`, `Hermes.Vector`) estavam a definir `<TargetFramework>net10.0</TargetFramework>` ou referenciando pacotes na versão `10.x` (ex: `Microsoft.EntityFrameworkCore.Design 10.0.8`).
- **Solução**: 
  - Fizemos um *downgrade* em massa do `<TargetFramework>` para `net9.0` em todos os projetos de forma a alinhar com as imagens base.
  - Substituímos globalmente os pacotes problemáticos. Exemplo: pacotes da Microsoft e Npgsql na versão `10.x` foram alterados para `9.x` compatíveis (ex: `Npgsql.EntityFrameworkCore.PostgreSQL 9.0.4`, `Microsoft.Extensions.Http.Resilience 9.1.0`).

### Bug Crítico no Dockerfile (`ENTRYPOINT`)
- **Problema**: Os contentores .NET entravam em *crash loop* imediato. O `ENTRYPOINT ["dotnet", "${SERVICE_NAME}.dll"]` estava no formato JSON array, formato no qual o Docker **não expande variáveis de ambiente** ou `ARG`s em tempo de execução. O contentor tentava executar literalmente o ficheiro chamado `${SERVICE_NAME}.dll`.
- **Solução**:
  - Modificámos o `Dockerfile` para transpor o `ARG` para um `ENV` durante a transição do build.
  - Usámos a *shell form* no `ENTRYPOINT`:
    ```dockerfile
    ENV SERVICE_DLL="${SERVICE_NAME}.dll"
    ENTRYPOINT ["sh", "-c", "exec dotnet $SERVICE_DLL"]
    ```
  - Isto forçou uma reconstrução total sem cache (`--no-cache`) de todos os 7 microsserviços, resolvendo definitivamente o erro.

---

## Estado Atual do Sistema
✅ A solução completa compila localmente sem nenhum erro ou aviso de versão.
✅ Todos os contentores (12 no total) estão no estado **Up / Healthy** no Docker Compose.
✅ O Gateway responde na porta `:5000` e o Frontend React na `:5173`, prontos para uso e testes end-to-end.
