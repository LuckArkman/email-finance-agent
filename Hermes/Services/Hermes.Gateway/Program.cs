using Hermes.Gateway.Extensions;
using Hermes.Gateway.Mcp;
using Hermes.Gateway.Middlewares;
using Hermes.Infrastructure.Extensions;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Http.Resilience;
using Microsoft.AspNetCore.Http;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Add Observability (Serilog, OTel, Sentry)
builder.AddHermesTelemetry();

// Add Database
builder.Services.AddHermesDatabase(builder.Configuration);

// Add Gateway Configurations and YARP
builder.Services.AddHermesGateway(builder.Configuration);

// Add Security and Rate Limiting
builder.Services.AddHermesRateLimiter();
builder.Services.AddGatewayServices();

// Add Security Config
builder.Services.AddHermesSecurity();

// Add Health Checks
builder.Services.AddHermesHealthChecks(builder.Configuration);

// Add MVC Controllers (InvoiceIngestController, AgentProxyController, etc.)
builder.Services.AddControllers();

// Add HermesAgentClient — typed HttpClient para o Hermes Agent (Nous Research)
var hermesAgentUrl = builder.Configuration["HermesAgent:BaseUrl"] ?? "http://localhost:8642";
var hermesAgentKey = builder.Configuration["HermesAgent:ApiKey"] ?? "";
builder.Services.AddHttpClient<Hermes.Gateway.Services.HermesAgentClient>(client =>
{
    client.BaseAddress = new Uri(hermesAgentUrl);
    client.DefaultRequestHeaders.Add("Authorization", $"Bearer {hermesAgentKey}");
    client.Timeout = TimeSpan.FromSeconds(60);
})
.AddStandardResilienceHandler();

var app = builder.Build();

// Setup Telemetry Middlewares
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ExceptionMiddleware>();

// Configure Security Headers Middlewares (Anti-XSS, NoSniff, HSTS, CORS)
app.UseHermesSecurity(app.Environment.IsDevelopment());

// Use Prometheus endpoint
app.MapPrometheusScrapingEndpoint();

// Use Rate Limiting
app.UseRateLimiter();

// Map Controllers (InvoiceIngestController — recebe payloads do Hermes Agent)
app.MapControllers();

// Map MCP Server (Hermes Agent descobre ferramentas .NET via MCP)
app.MapMcpEndpoints();

// Map YARP Reverse Proxy
app.MapReverseProxy();

// Map Health Checks Endpoints
app.UseHermesHealthChecks();

app.Run();

public partial class Program { }