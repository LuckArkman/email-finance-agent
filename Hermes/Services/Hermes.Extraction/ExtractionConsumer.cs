using System;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Hermes.EventBus;
using Hermes.EventBus.Events;
using MassTransit;
using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class ExtractionConsumer : IConsumer<OcrCompletedEvent>
{
    private readonly ILogger<ExtractionConsumer> _logger;
    private readonly LlmClientFactory _llmFactory;
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly MathValidator _mathValidator;
    private readonly ConfidenceEvaluator _confidenceEvaluator;

    public ExtractionConsumer(
        ILogger<ExtractionConsumer> logger, 
        LlmClientFactory llmFactory, 
        IPublishEndpoint publishEndpoint,
        MathValidator mathValidator,
        ConfidenceEvaluator confidenceEvaluator)
    {
        _logger = logger;
        _llmFactory = llmFactory;
        _publishEndpoint = publishEndpoint;
        _mathValidator = mathValidator;
        _confidenceEvaluator = confidenceEvaluator;
    }

    public async Task Consume(ConsumeContext<OcrCompletedEvent> context)
    {
        var evt = context.Message;
        _logger.LogInformation($"Received OcrCompletedEvent for Document {evt.DocumentId} (Tenant: {evt.TenantId})");

        var prompt = PromptBuilder.BuildInvoiceExtractionPrompt();

        try
        {
            var llmClient = _llmFactory.CreateClient(LlmProvider.Mock);
            var rawJson = await llmClient.ExtractSemanticDataAsync(prompt, evt.RawText);
            
            _logger.LogDebug($"Raw JSON from LLM: {rawJson}");

            // 1. JSON Stripper (limpar backticks de markdown que os LLMs costumam adicionar)
            var cleanJson = StripMarkdown(rawJson);

            // 2. Deserialização Pydantic/Strict
            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
            var extractedModel = JsonSerializer.Deserialize<InvoiceExtractionModel>(cleanJson, options);

            if (extractedModel == null)
            {
                throw new InvalidOperationException("Desserialização falhou: JSON model é nulo.");
            }

            // 3. Conversão de Modelos e Validação Anti-Alucinação Matemática
            _mathValidator.ValidateTotal(extractedModel);

            DateTime? parsedDate = DateTime.TryParse(extractedModel.Date, out var date) ? date : null;
            var mappedItems = extractedModel.Items.Select(i => new InvoiceItemData(i.Description, i.Quantity, i.Price)).ToList();

            // 4. Confiança & Heurísticas
            bool requiresReview = _confidenceEvaluator.Evaluate(evt.MeanConfidence, extractedModel, evt.RawText);

            // 5. Publicar Evento de Fim de Esteira
            var completedEvent = new ExtractionCompletedEvent(
                evt.DocumentId,
                evt.TenantId,
                extractedModel.Vendor,
                extractedModel.Nif,
                parsedDate,
                extractedModel.Total,
                mappedItems,
                DateTime.UtcNow,
                requiresReview
            );

            await _publishEndpoint.Publish(completedEvent, context.CancellationToken);
            _logger.LogInformation($"Successfully published ExtractionCompletedEvent for Document {evt.DocumentId}. Data: Vendor={completedEvent.VendorName}, Total={completedEvent.TotalAmount}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Extraction pipeline failed for Document {evt.DocumentId}");
        }
    }

    private string StripMarkdown(string input)
    {
        if (string.IsNullOrWhiteSpace(input)) return input;
        var stripped = Regex.Replace(input, @"^```(json)?", "", RegexOptions.IgnoreCase | RegexOptions.Multiline);
        stripped = Regex.Replace(stripped, @"```$", "", RegexOptions.Multiline);
        return stripped.Trim();
    }
}
