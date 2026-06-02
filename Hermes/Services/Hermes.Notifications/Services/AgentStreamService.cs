using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;

namespace Hermes.Notifications.Services;

public class ChatMessageDto
{
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}

public interface IAgentStreamService
{
    IAsyncEnumerable<string> StreamChatAsync(IEnumerable<ChatMessageDto> messages, CancellationToken cancellationToken = default);
}

public class AgentStreamService : IAgentStreamService
{
    // Em produção, injetaríamos Kernel (Semantic Kernel), Dapper (PgVector) e ILogger.
    public async IAsyncEnumerable<string> StreamChatAsync(IEnumerable<ChatMessageDto> messages, [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        // SIMULAÇÃO DO PIPELINE RAG:
        // 1. Converter última message.Content para Embedding Vetorial.
        // 2. Consulta PgVector (Retrieval) usando Dapper: SELECT id, texto FROM faturas ORDER BY embedding <-> @vector LIMIT 5
        // 3. Adicionar contexto às mensagens.
        // 4. Executar Prompt no LLM via Semantic Kernel de forma streamada.

        var dummyResponse = " Olá! [RAG Ativado] Analisei as suas finanças. O vetor das Top 5 faturas mais semelhantes indica que não tem pagamentos pendentes à Vodafone este mês. O seu saldo livre atual é de 4.500€. Como posso ajudar mais?";
        var chunks = dummyResponse.Split(' ');

        foreach (var chunk in chunks)
        {
            cancellationToken.ThrowIfCancellationRequested();

            // Simula o atraso de "pensamento" (Token Generation) da IA
            await Task.Delay(Random.Shared.Next(50, 150), cancellationToken);
            
            yield return chunk + " ";
        }
    }
}
