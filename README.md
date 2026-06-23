# Hermes — AI Email Finance Agent B2B
**Documentação Completa da Arquitetura, Recursos, Ferramentas e Bibliotecas**

Este documento serve como a referência primária, exaustiva e técnica para todo o ecossistema do **Hermes**, uma plataforma inteligente B2B arquitetada para a automação total de processos financeiros, captura e reconciliação de faturas via e-mail e interação proativa com os administradores por WhatsApp.

O sistema baseia-se numa arquitetura híbrida de ponta, interligando microsserviços corporativos rígidos e escaláveis em **.NET 9 (C#)** com a maleabilidade, inovação algorítmica e capacidade cognitiva de um motor de Agente Autônomo em **Python 3.12**, apoiado por Modelos de Linguagem de Larga Escala (LLM) que correm 100% localmente.

---

## 1. Visão Geral e Paradigma

A aplicação afasta-se de monolitos tradicionais em favor de uma **Arquitetura Orientada a Eventos (Event-Driven Architecture)**, potenciando alta concorrência. Operações pesadas como OCR (Reconhecimento Ótico de Caracteres), inferência LLM de biliões de parâmetros ou vetorização semântica de milhares de e-mails ocorrem em background, perfeitamente orquestradas, sem bloquear as rotas RESTful da interface do utilizador.

A plataforma foca-se na **privacidade absoluta (Local AI)**. Todos os documentos financeiros não cruzam as fronteiras do servidor, sendo analisados localmente por motores *Open-Weights*.

---

## 2. Stack Tecnológico, Pacotes e Bibliotecas

### 2.1. Core Services & Backend Corporativo (.NET 9)
A espinha dorsal de regras de negócio, persistência estruturada e roteamento é garantida por um ecossistema C# (.NET 9):
* **ASP.NET Core (Web API)**: Fornece os endpoints REST de alta performance, protegidos por tokens JWT (JSON Web Tokens).
* **YARP (Yet Another Reverse Proxy)**: Atua dentro do serviço de Gateway, canalizando tráfego de entrada em segurança para os sub-serviços adequados.
* **Entity Framework Core 9 (EF Core)**: ORM robusto gerindo os modelos de dados e a migração de esquemas com o banco relacional de forma tipificada.
* **MassTransit (com RabbitMQ)**: Biblioteca de abstração e orquestração de mensageria (Pub/Sub e filas) para garantir que microserviços comunicam entre si sem dependências síncronas pesadas.
* **Microsoft Semantic Kernel**: Integra-se ativamente no serviço de Extração (.NET) facilitando orquestrações ricas com LLMs (chain-of-thought, elaboração de prompts) em C#.

### 2.2. Inteligência Artificial e Agente Autônomo (Python 3.12)
O coração cognitivo do projeto, lidando com lógica inferencial imprevisível:
* **Hermes Agent (Nous Research)**: Framework assíncrona avançada de Agentes de IA baseada em Python. Mantém a memória contextual em conversas pelo WhatsApp, avalia eixos de intenção de mensagens de entrada (Intent Classification) e invoca dinamicamente ferramentas de extração a partir da diretoria interna (`skills/`).
* **Model Context Protocol (MCP)**: Utilizado para unificar e escalar ferramentas. O `.NET Gateway` expõe os próprios *endpoints* corporativos no formato de MCP Server, permitindo ao Agente Python solicitar dados estruturados de faturas diretamente à rede .NET em linguagem natural.
* **Ollama**: Motor de virtualização de modelos LLM. Gira localmente os pesos quânticos, mantendo-os em memória.
* **FastAPI + Uvicorn**: Hospeda internamente o servidor API local para o *Hermes Agent* e também o Microsserviço Independente de Processamento de Áudio (`hermes-audio`).

### 2.3. Mensageria, Caching e Bases de Dados
* **PostgreSQL (com extensão pgvector)**: Central de persistência. Substitui bases de dados vetoriais dedicadas (como ChromaDB ou Pinecone) consolidando num único local as tabelas relacionais de *Invoices/Users* e o *Vector Space* dos embeddings documentais (facilitando RAG — Retrieval-Augmented Generation).
* **RabbitMQ**: Broker AMQP robusto e escalável onde se formam as filas de processamento (`review_queue`, `extraction_queue`, `notification_queue`).
* **Redis**: Cache ultrarrápida In-Memory usada fundamentalmente para rate-limiting, gestão de sessões WebSocket em realtime e agregação temporária dos KPIs de *Analytics*.

### 2.4. LLMs Locais (Arquitetura Dual-Model)
Para mitigar os longos tempos de geração nos modelos imensos (12 biliões), optou-se por um despachante dual na família **Qwen 2.5**:
* **Qwen 2.5: 1.5B (Rápido)**: Modelo ultraleve operando tarefas de front-line como "Decisão de Rota de Conversa", "Classificação de Intenção do WhatsApp" e "Classificação de Spam". Resulta em inferências em frações de segundo.
* **Qwen 2.5: 12B (Preciso)**: Modelo principal, ativado perante hardware suportado (GPU), especializado na Extração Analítica Complexa de JSON (NIF, IBAN, Valores Totais, e dezenas de itens de linha cruzados de uma fatura de múltiplas páginas).

### 2.5. Frontend / Web UI
* **React 18 + Vite**: O motor ultra-veloz de desenvolvimento e transpilação moderna para a SPA corporativa servida em instâncias de Nginx na porta 5173.
* **Tailwind CSS & Framer Motion**: Estilização imersiva baseada em utilitários e sistema declarativo de animações (microinterações) focado numa experiência Glassmorphism Premium.
* **Zustand**: Gestor de estado global super leve (em substituição do Redux) encarregue da sincronização reativa dos KPIs do painel de administração e da tesouraria global.

### 2.6. Integrações de Interface Físicas
* **Baileys (Node.js/TypeScript)**: Biblioteca fulcral baseada em Sockets WSS usada pelo Microsserviço `baileys-bridge`. Simula um dispositivo WhatsApp Web na perfeição, injetando as mensagens vindas da rede móvel diretamente no Agente e reenviando textos de volta para as conversas do utilizador.

---

## 3. Microsserviços e Separação de Responsabilidades (CQRS)

A robustez atinge-se dividindo os processadores operacionais e analíticos na seguinte grelha de contentores independentes:

1. **`hermes-gateway` (Porta 5000)**: Ponto de entrada de tráfego. Avalia Rate Limits, proxy reverso, e centraliza o contrato de MCP unificado do Backend para o Cérebro de IA Python.
2. **`hermes-identity`**: Autenticador. Emite Tokens JWT, gere a persistência e validação da segurança das senhas e chaves API das integrações externas.
3. **`hermes-extraction`**: Operário Pesado. Consome PDFs cruos do RabbitMQ. Aplica as rotinas de Parsing ou envia recortes fotográficos com *Vision Models* via Ollama, consolidando no final um objeto C# fortificado antes de gravar.
4. **`hermes-reconciliation`**: Assina as filas "Bancárias". Consome comprovativos emitidos via PDF e interseta (*Auto-Match*) faturas passadas (analisando IBANs e saldos em falta) e marca registos de conciliação final.
5. **`hermes-notifications`**: Sistema emissor proativo. Ouve a flag "Fatura Paga" para disparar payloads REST corporativos (Webhooks) para o software nativo da empresa-cliente (Sage, PHC, SAP).
6. **`hermes-analytics`**: Centraliza os fluxos transacionais, somando totais monetários aglomerados em caches Redis de modo a manter a página de Dashboard sempre a zero milissegundos de tempo de load.
7. **`hermes-vector`**: Inteligência RAG acoplada. Vetoriza fragmentos de qualquer email/fatura nova no formato dimensional do `pgvector`, tornando magicamente possível inquirir ao Agente pelo WhatsApp: *"Podes mostrar-me em que gastamos 300€ num restaurante a semana passada?"*
8. **`hermes-review-queue`**: Onde opera a verificação Humana (Human-in-the-Loop). Se o *Confidence Score* de extração for medíocre (< 90%), o documento é resgatado do automatismo e estaciona numa UI para conferência humana de revisão.
9. **`hermes-audio`**: Transcrição fonética (STT - Speech-To-Text) convertendo mensagens de áudio atiradas ao WhatsApp num texto literal para o processamento limpo do *Hermes Agent*.

---

## 4. O Fluxo Orgânico da Informação (Exemplo de Ciclo de Vida)

Para compreender como a complexidade flui como uma orquestra, basta seguir o cenário principal:

1. **A Captura Inicial**: O fornecedor remete um e-mail com anexo, ou em alternativa, o Administrador fotografa a fatura com o seu smartphone e partilha o ficheiro por WhatsApp para o contacto do *Bot* do Hermes.
2. **Interseção no Bridge**: O script WSS (`baileys-bridge`) capta instantaneamente o Base64 do PDF da foto de WhatsApp e envia para o `hermes-agent`. A IA avalia a Intenção (*Intent Classification*) da foto e reconhece: *"É uma submissão de nova fatura."*
3. **Colocação no Message Broker**: O ficheiro é enviado via POST para a Gateway `hermes-gateway` que descarrega rapidamente na fila RabbitMQ sob o evento `Document.Received`. A Gateway responde 200 OK liberta a ligação do WhatsApp.
4. **Pipeline de Inferência**: O `hermes-extraction` nota o alerta na fila. Retira a imagem, chama o Semantic Kernel, extrai chaves-valores num esquema fixo e verifica se tudo cruza.
5. **Classificação Vetorial e CQRS**: Com o parsing bem-sucedido, o modelo vetorial (`hermes-vector`) regista a nova fatura dimensionalmente no banco de dados da tesouraria do PostgreSQL. Dispara o evento cimeiro `Invoice.Processed`.
6. **Live Update Global**: 
    - O ecrã Frontend React, via SignalR/WebSocket, pisca em tempo-real na mesa do CFO mostrando: "Fatura de Restaurante - 30.50€ aguarda pagamento." 
    - Em simultâneo, o *Hermes Agent* escreve de volta na conversa do WhatsApp do administrador a notificação: *"A fatura que enviou foi extraída e arquivada com sucesso com um valor de 30,50€!"*

---

## 5. Deployment e Setup Básico

Toda a infraestrutura densa está contida dentro de receitas e layers limpas num macro orquestrador de Contentores Docker.

### 5.1. Pré-Requisitos
- **Docker Engine + Compose** (V2+).
- Variáveis seguras declaradas no `.env` (ex: passwords, chaves JWT secretas, etc).
- Para ativar o modelo superior (qwen2.5:12b), requer GPU NVIDIA com Cuda compatível e flag no docker: `PULL_LARGE_MODEL=true`.

### 5.2. Compilação Universal Num Só Passo
```bash
docker compose up -d --build
```
> Com este comando simples, o motor encarrega-se de compilar as DLLs do C#, executar as buils de Node, levantar a bridge do WhatsApp, configurar as Skills de Python, baixar os modelos localmente e gerir a ordem saudável de *Healthchecks* no background.

### 5.3. Emparelhamento Interativo WhatsApp
Uma vez o sistema online, o sub-serviço do Hermes fica com a sessão virgem pendente. Deve aceder aos terminais TTY do contentor na linha de comandos para capturar o código QR fotográfico oficial:
```bash
docker exec -it hermes_agent hermes whatsapp
```
Leia esse QR com a câmara do WhatsApp no "Dispositivo Físico do Bot". A sessão persistirá localmente nos volumes mapeados (`auth_sessions`), reatando nativamente em futuros reinícios de servidor.
