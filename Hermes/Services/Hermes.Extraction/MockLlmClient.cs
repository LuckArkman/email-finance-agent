using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class MockLlmClient : ILLMClient
{
    private readonly ILogger<MockLlmClient> _logger;

    public MockLlmClient(ILogger<MockLlmClient> logger)
    {
        _logger = logger;
    }

    public async Task<string> ExtractSemanticDataAsync(string prompt, string rawText)
    {
        _logger.LogInformation("Using MockLlmClient to simulate semantic extraction (Bypass OpenAI API).");
        await Task.Delay(1000); // Simulate network latency

        // Retorna um JSON estático estruturado perfeito (como seria de esperar do LLM real)
        return """
        {
            "Vendor": "TechSupplier Inc.",
            "Nif": "500000000",
            "Date": "2026-06-01",
            "Total": 249.99,
            "Items": [
                {
                    "Description": "Monitor 24 inch",
                    "Quantity": 1,
                    "Price": 199.99
                },
                {
                    "Description": "Keyboard",
                    "Quantity": 1,
                    "Price": 50.00
                }
            ]
        }
        """;
    }
}
