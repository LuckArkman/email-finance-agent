using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

namespace Hermes.Extraction;

public class SemanticKernelClient : ILLMClient
{
    private readonly ILogger<SemanticKernelClient> _logger;
    private readonly IChatCompletionService _chatService;
    private readonly Kernel _kernel;

    public SemanticKernelClient(ILogger<SemanticKernelClient> logger, Kernel kernel)
    {
        _logger = logger;
        _kernel = kernel;
        _chatService = _kernel.GetRequiredService<IChatCompletionService>();
    }

    public async Task<string> ExtractSemanticDataAsync(string prompt, string rawText)
    {
        _logger.LogInformation("Invoking LLM via Semantic Kernel.");
        
        var chatHistory = new ChatHistory(prompt);
        chatHistory.AddUserMessage(rawText);

        try
        {
            var response = await _chatService.GetChatMessageContentAsync(chatHistory, kernel: _kernel);
            return response.Content ?? string.Empty;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to communicate with LLM.");
            throw;
        }
    }
}
