using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Hermes.Extraction;

public class OllamaMessage
{
    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;
}

public class OllamaRequest
{
    [JsonPropertyName("model")]
    public string Model { get; set; } = "llama3";

    [JsonPropertyName("messages")]
    public List<OllamaMessage> Messages { get; set; } = new();

    [JsonPropertyName("stream")]
    public bool Stream { get; set; } = false;

    [JsonPropertyName("format")]
    public string Format { get; set; } = "json"; // Força o Output em formato JSON no Llama3!
}

public class OllamaResponse
{
    [JsonPropertyName("message")]
    public OllamaMessage? Message { get; set; }
}
