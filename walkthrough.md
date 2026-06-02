# Walkthrough das Últimas Implementações

Abaixo encontra-se um resumo exaustivo de todas as configurações, integrações e correções efetuadas para migrar a arquitetura para o novo gateway em .NET e corrigir os erros de inicialização que impediam o arranque correto dos serviços.

## 1. Implementação do Hermes Gateway (.NET)
- **Criação do Serviço Gateway:** Configurado o serviço `hermes_gateway` utilizando .NET 9.0 para servir como o ponto central de entrada e roteamento.
- **Integração com YARP (Reverse Proxy):** Configurado o YARP para encaminhar pedidos internamente, substituindo o antigo backend em Python.
- **SignalR (WebSockets):** Foram removidas referências antigas no binário para prevenir crashes no arranque onde era chamado um `MapHub` sem o registo prévio do `AddSignalR`.
- **Correção de ENTRYPOINT Docker:** Resolvido o erro em que o Docker tentava executar literalmente `${SERVICE_NAME}.dll` (as variáveis `ARG` não são expandidas em arrays JSON de ENTRYPOINT). O `Dockerfile` foi reescrito para utilizar `ENV` e a forma shell do comando `ENTRYPOINT ["sh", "-c", "exec dotnet $SERVICE_DLL"]`.
- **Resolução de Warnings NuGet:** Atualizada a versão do pacote `Microsoft.Extensions.Http.Resilience` para `9.1.0` para resolver problemas de resolução e dependências em loop.

## 2. Configuração do Frontend e Integração
- **Atualização de Variáveis e Chamadas API:** O frontend foi modificado para utilizar a variável de ambiente correta (ou encaminhamento no Nginx) apontando para a API .NET.
- **Correção Nginx Crítico:**
  > [!WARNING]
  > O serviço `hermes_frontend` estava a falhar o arranque com `emerg: host not found in upstream "backend"`. A configuração do `nginx.conf` ainda apontava para `http://backend:8000`. Foi corrigido para `proxy_pass http://hermes-gateway:8080` de modo a respeitar a nova arquitetura .NET e as rotas `/api/`.
- **Force Rebuild:** O container `hermes_frontend` foi totalmente reconstruído com cache limpa, passando agora a estar 100% Up e saudável.

## 3. Configurações Globais (.env) e Hermes Agent
- **Inicialização de Variáveis de Ambiente:** O sistema estava com warnings no docker-compose indicando a falta de chaves cruciais, o que impedia o arranque de hooks e plugins do `hermes_agent` (ex: `[post-extraction] HERMES_DOTNET_GATEWAY_URL não configurados` e erros da chave do `Api_Server`).
- **Resolução:** O ficheiro modelo `.env.example` foi copiado para `.env` no root do projeto de modo a garantir que todos os containers têm valores por defeito e não entram em crash durante o script de inicialização.

## 4. Estado Atual e Próximos Passos (Requer Atenção)
> [!CAUTION]
> Neste momento o Gateway, Redis, RabbitMQ, Postgres, Identity e Frontend estão a executar e **Saudáveis**.
>
> Contudo, existem vários serviços .NET subsidiários que estão a sofrer de **Segmentation Faults (Exit Code 139)** contínuos no arranque. Serviços como:
> - `hermes_analytics`
> - `hermes_extraction`
> - `hermes_notifications`
> - `hermes_reconciliation`
> - `hermes_review_queue`
> - `hermes_vector`
>
> Este erro `139` é muito comum em imagens `alpine` com .NET 9 caso haja referências a bibliotecas C/C++ não compatíveis com `musl libc` (como clientes nativos GRPC, ou SQL). Será necessário rever as dependências nativas destes microserviços ou alterar a imagem base de `alpine` para `bookworm-slim` / `jammy-chiseled` nestes componentes específicos.

Validem as funcionalidades principais no Frontend através do Gateway e digam-me se pretendem que investigue e aplique as correções para os serviços subsidiários em *crash-loop*.
