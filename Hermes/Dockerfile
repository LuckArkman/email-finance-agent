# ── Build Stage ──────────────────────────────────────────────
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG SERVICE_NAME
WORKDIR /src

# Copiar a solução inteira
COPY ["Hermes.slnx", "."]
COPY ["Core/", "Core/"]
COPY ["Infrastructure/", "Infrastructure/"]
COPY ["Services/", "Services/"]

# Restaurar dependências
RUN dotnet restore "Services/${SERVICE_NAME}/${SERVICE_NAME}.csproj"

# Build e Publish
RUN dotnet publish "Services/${SERVICE_NAME}/${SERVICE_NAME}.csproj" \
    -c Release -o /app/publish /p:UseAppHost=false

# ── Runtime Stage ─────────────────────────────────────────────
FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine AS final
ARG SERVICE_NAME

# Passar SERVICE_NAME como ENV para ficar disponível em runtime
ENV SERVICE_DLL="${SERVICE_NAME}.dll"

WORKDIR /app
COPY --from=build /app/publish .

# Expor porta 8080 padrão do .NET 9
EXPOSE 8080

# Shell form: expande $SERVICE_DLL corretamente em runtime
ENTRYPOINT ["sh", "-c", "exec dotnet $SERVICE_DLL"]
