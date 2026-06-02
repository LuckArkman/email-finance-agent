using System.Threading.Tasks;
using MassTransit;
using Microsoft.Extensions.Logging;
using Hermes.EventBus;

namespace Hermes.OCR;

public class OcrJobConsumer : IConsumer<DocumentStoredEvent>
{
    private readonly JobDispatcher _jobDispatcher;
    private readonly ILogger<OcrJobConsumer> _logger;

    public OcrJobConsumer(JobDispatcher jobDispatcher, ILogger<OcrJobConsumer> logger)
    {
        _jobDispatcher = jobDispatcher;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<DocumentStoredEvent> context)
    {
        _logger.LogInformation($"Received DocumentStoredEvent for DocumentId: {context.Message.DocumentId}");

        // Publicar OcrStartedEvent logo antes de colocar na fila interna para que o sistema saiba que chegou no OCR
        await context.Publish(new OcrStartedEvent(
            context.Message.DocumentId,
            context.Message.TenantId,
            System.DateTime.UtcNow
        ), context.CancellationToken);

        // Enviar para a pipeline paralela baseada em Channels
        await _jobDispatcher.EnqueueJobAsync(new OcrJobContext(context.Message), context.CancellationToken);
    }
}
