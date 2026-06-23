using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Services;

/// <summary>
/// Typed HTTP client para comunicar com o Hermes Agent (Nous Research).
/// Encapsula as chamadas à API REST do agente (porta 8642 por padrão).
/// Configurado no Program.cs com Polly resilience (retry + circuit breaker).
/// </summary>
public class HermesAgentClient
{
    private readonly HttpClient _http;
    private readonly ILogger<HermesAgentClient> _logger;

    public HermesAgentClient(HttpClient http, ILogger<HermesAgentClient> logger)
    {
        _http = http;
        _logger = logger;
    }

    // ----------------------------------------------------------------
    // Status do Agente
    // ----------------------------------------------------------------

    public async Task<AgentStatusResponse?> GetStatusAsync()
    {
        try
        {
            var healthResp = await _http.GetAsync("/health");
            if (healthResp.IsSuccessStatusCode)
            {
                return new AgentStatusResponse("1.0", true, 0, "qwen:12b", "ollama");
            }
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogWarning("[HermesAgentClient] GetStatus falhou: {Msg}", ex.Message);
            return null;
        }
    }

    // ----------------------------------------------------------------
    // Sessões
    // ----------------------------------------------------------------

    /// <summary>GET /api/sessions — lista as sessões recentes com metadados.</summary>
    public async Task<List<AgentSession>?> GetSessionsAsync()
    {
        try
        {
            var result = await _http.GetFromJsonAsync<AgentSessionsResponse>("/api/sessions");
            return result?.Sessions;
        }
        catch (Exception ex)
        {
            _logger.LogWarning("[HermesAgentClient] GetSessions falhou: {Msg}", ex.Message);
            return null;
        }
    }

    // ----------------------------------------------------------------
    // Chat / Inferência (OpenAI-compatible)
    // ----------------------------------------------------------------

    /// <summary>
    /// POST /v1/chat/completions — envia mensagens ao agente e recebe resposta.
    /// Compatível com o formato OpenAI Chat Completions.
    /// </summary>
    public async Task<string?> ChatAsync(List<ChatMessage> messages, string model = "hermes-agent")
    {
        var requestBody = new
        {
            model,
            messages = messages.ConvertAll(m => new { role = m.Role, content = m.Content }),
            stream = false
        };

        try
        {
            var json = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _http.PostAsync("/v1/chat/completions", content);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<ChatCompletionResponse>();
            return result?.Choices?[0]?.Message?.Content;
        }
        catch (Exception ex)
        {
            _logger.LogError("[HermesAgentClient] Chat falhou: {Msg}", ex.Message);
            return null;
        }
    }

    // ----------------------------------------------------------------
    // Processamento Manual de Documentos
    // ----------------------------------------------------------------

    /// <summary>
    /// Envia uma instrução ao agente para processar um documento específico.
    /// Útil quando o frontend faz upload de um PDF para processamento imediato.
    /// </summary>
    public async Task<string?> TriggerDocumentProcessingAsync(string documentPath, string sourceEmail)
    {
        var prompt = $"Process the invoice document at path '{documentPath}' " +
                     $"received from '{sourceEmail}'. " +
                     $"Use the invoice-extraction skill to extract and submit it to the .NET pipeline.";

        return await ChatAsync(new List<ChatMessage>
        {
            new("user", prompt)
        });
    }
}

// ----------------------------------------------------------------
// DTOs — respostas do Hermes Agent API
// ----------------------------------------------------------------

public record AgentStatusResponse(
    string Version,
    bool GatewayRunning,
    int ActiveSessions,
    string Model,
    string Provider
);

public record AgentSessionsResponse(List<AgentSession> Sessions);

public record AgentSession(
    string SessionId,
    string Platform,
    DateTime CreatedAt,
    int MessageCount,
    int TokensUsed
);

public record ChatMessage(string Role, string Content);

public record ChatCompletionResponse(
    string Id,
    List<ChatChoice> Choices
);

public record ChatChoice(int Index, ChatChoiceMessage Message);
public record ChatChoiceMessage(string Role, string Content);
