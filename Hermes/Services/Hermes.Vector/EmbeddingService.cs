using System;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Hermes.EventBus;
using Hermes.EventBus.Events;

namespace Hermes.Vector;

public class OllamaEmbeddingRequest
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = "nomic-embed-text";

    [JsonPropertyName("prompt")]
    public string Prompt { get; set; } = string.Empty;
}

public class OllamaEmbeddingResponse
{
    [JsonPropertyName("embedding")]
    public float[] Embedding { get; set; } = Array.Empty<float>();
}

public class EmbeddingService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<EmbeddingService> _logger;

    public EmbeddingService(HttpClient httpClient, ILogger<EmbeddingService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public string BuildDocumentPrompt(ExtractionCompletedEvent evt)
    {
        var itemsStr = string.Join(", ", evt.Items.Select(i => $"{i.Quantity}x {i.Description}"));
        return $"Invoice from {evt.VendorName}, NIF: {evt.Nif}, Date: {evt.InvoiceDate?.ToString("yyyy-MM-dd")}, Total: {evt.TotalAmount}. Items: {itemsStr}";
    }

    public async Task<float[]> GenerateEmbeddingsAsync(string prompt)
    {
        _logger.LogInformation("Generating embeddings via Ollama (nomic-embed-text).");

        var request = new OllamaEmbeddingRequest { Prompt = prompt };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("/api/embeddings", request);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<OllamaEmbeddingResponse>();
            return result?.Embedding ?? Array.Empty<float>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate embeddings via Ollama.");
            throw;
        }
    }
}
