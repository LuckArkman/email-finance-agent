using System;
using System.Threading.Tasks;
using Hermes.EventBus;
using Hermes.EventBus.Events;
using MassTransit;
using Microsoft.Extensions.Logging;

namespace Hermes.Vector;

public class VectorJobConsumer : IConsumer<ExtractionCompletedEvent>
{
    private readonly ILogger<VectorJobConsumer> _logger;
    private readonly EmbeddingService _embeddingService;
    private readonly HermesDbContext _dbContext;
    private readonly IPublishEndpoint _publishEndpoint;

    public VectorJobConsumer(
        ILogger<VectorJobConsumer> logger, 
        EmbeddingService embeddingService, 
        HermesDbContext dbContext,
        IPublishEndpoint publishEndpoint)
    {
        _logger = logger;
        _embeddingService = embeddingService;
        _dbContext = dbContext;
        _publishEndpoint = publishEndpoint;
    }

    public async Task Consume(ConsumeContext<ExtractionCompletedEvent> context)
    {
        var evt = context.Message;
        _logger.LogInformation($"Received ExtractionCompletedEvent for Document {evt.DocumentId}. Preparing vectorization.");

        try
        {
            // 1. Build the text prompt
            var prompt = _embeddingService.BuildDocumentPrompt(evt);

            // 2. Generate vector from Ollama
            var vectorArray = await _embeddingService.GenerateEmbeddingsAsync(prompt);
            if (vectorArray == null || vectorArray.Length == 0)
            {
                throw new InvalidOperationException("Embedding generated was empty.");
            }

            // 3. Save to database
            var entity = new InvoiceEntity
            {
                TenantId = evt.TenantId,
                DocumentId = evt.DocumentId,
                Vendor = evt.VendorName,
                Nif = evt.Nif,
                InvoiceDate = evt.InvoiceDate,
                TotalAmount = evt.TotalAmount,
                Embedding = new Pgvector.Vector(vectorArray)
            };

            _dbContext.Invoices.Add(entity);
            await _dbContext.SaveChangesAsync(context.CancellationToken);

            _logger.LogInformation($"Successfully saved InvoiceEntity and {vectorArray.Length}-dimensional vector for Document {evt.DocumentId}.");

            // 4. Publish Indexed Event
            await _publishEndpoint.Publish(new VectorIndexedEvent(
                evt.DocumentId,
                evt.TenantId,
                entity.Id,
                vectorArray.Length,
                DateTime.UtcNow
            ), context.CancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to index document {evt.DocumentId}");
        }
    }
}
