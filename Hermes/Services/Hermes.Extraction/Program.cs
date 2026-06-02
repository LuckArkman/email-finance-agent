using MassTransit;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.SemanticKernel;

namespace Hermes.Extraction;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = Host.CreateApplicationBuilder(args);

        // 1. LLM / Semantic Kernel Setup
        builder.Services.AddSingleton<MockLlmClient>();
        
        // Exemplo de como se regista o Semantic Kernel real (a ser usado em Produção)
        var kernelBuilder = builder.Services.AddKernel();
        // Em produção fariamos: kernelBuilder.AddAzureOpenAIChatCompletion(...)
        builder.Services.AddSingleton<SemanticKernelClient>();
        
        builder.Services.AddHttpClient<OllamaClient>(client =>
        {
            client.BaseAddress = new System.Uri(builder.Configuration["Ollama:BaseUrl"] ?? "http://localhost:11434");
        })
        .AddPolicyHandler(Hermes.Extraction.Extensions.ResiliencePolicyConfiguration.GetRetryPolicy())
        .AddPolicyHandler(Hermes.Extraction.Extensions.ResiliencePolicyConfiguration.GetCircuitBreakerPolicy());
        
        builder.Services.AddSingleton<LlmClientFactory>();
        builder.Services.AddSingleton<MathValidator>();
        builder.Services.AddSingleton<HeuristicMatcher>();
        builder.Services.AddSingleton<ConfidenceEvaluator>();

        // 2. MassTransit Setup
        builder.Services.AddMassTransit(x =>
        {
            x.AddConsumer<ExtractionConsumer>();

            x.UsingRabbitMq((context, cfg) =>
            {
                cfg.Host(builder.Configuration["EventBus:Host"] ?? "localhost", "/", h =>
                {
                    h.Username(builder.Configuration["EventBus:Username"] ?? "guest");
                    h.Password(builder.Configuration["EventBus:Password"] ?? "guest");
                });

                cfg.ReceiveEndpoint("hermes-extraction-queue", e =>
                {
                    e.ConfigureConsumer<ExtractionConsumer>(context);
                });
            });
        });

        var host = builder.Build();
        host.Run();
    }
}
