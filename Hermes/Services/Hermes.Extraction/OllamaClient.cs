using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class OllamaClient : ILLMClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OllamaClient> _logger;

    public OllamaClient(HttpClient httpClient, ILogger<OllamaClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<string> ExtractSemanticDataAsync(string prompt, string rawText)
    {
        _logger.LogInformation("Invoking Local LLM via Ollama API.");

        var requestDto = new OllamaRequest
        {
            Model = "llama3", // Model name configured in local Ollama instance
            Stream = false,
            Format = "json",
            Messages = new System.Collections.Generic.List<OllamaMessage>
            {
                new OllamaMessage { Role = "system", Content = prompt },
                new OllamaMessage { Role = "user", Content = rawText }
            }
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("/api/chat", requestDto);
            response.EnsureSuccessStatusCode();

            var ollamaResponse = await response.Content.ReadFromJsonAsync<OllamaResponse>();
            
            return ollamaResponse?.Message?.Content ?? string.Empty;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to communicate with Local Ollama Engine.");
            throw;
        }
    }
}
