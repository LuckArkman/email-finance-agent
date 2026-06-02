using System;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class LlmClientFactory
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<LlmClientFactory> _logger;

    public LlmClientFactory(IServiceProvider serviceProvider, ILogger<LlmClientFactory> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    public ILLMClient CreateClient(LlmProvider provider)
    {
        switch (provider)
        {
            case LlmProvider.SemanticKernel:
                _logger.LogInformation("Creating SemanticKernelClient (Azure OpenAI)");
                return _serviceProvider.GetRequiredService<SemanticKernelClient>();
            
            case LlmProvider.Ollama:
                _logger.LogInformation("Creating OllamaClient (Local Llama3)");
                return _serviceProvider.GetRequiredService<OllamaClient>();
            
            case LlmProvider.Mock:
            default:
                _logger.LogInformation("Creating MockLlmClient");
                return _serviceProvider.GetRequiredService<MockLlmClient>();
        }
    }
}
