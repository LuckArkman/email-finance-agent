using System.Text.Json;
using System.Threading.Tasks;
using Hermes.EventBus;
using MassTransit;
using Microsoft.Extensions.Logging;

namespace Hermes.ReviewQueue;

public class ReviewQueueConsumer : IConsumer<ExtractionCompletedEvent>
{
    private readonly ReviewDbContext _dbContext;
    private readonly ILogger<ReviewQueueConsumer> _logger;

    public ReviewQueueConsumer(ReviewDbContext dbContext, ILogger<ReviewQueueConsumer> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<ExtractionCompletedEvent> context)
    {
        var evt = context.Message;

        if (!evt.RequiresReview)
        {
            _logger.LogInformation($"Document {evt.DocumentId} does not require review. Skipping.");
            return;
        }

        _logger.LogWarning($"Document {evt.DocumentId} flagged for manual review! Moving to Quarantine.");

        var rawPayload = JsonSerializer.Serialize(evt);

        var pending = new PendingReview
        {
            TenantId = evt.TenantId,
            DocumentId = evt.DocumentId,
            RawJsonPayload = rawPayload,
            IsResolved = false
        };

        _dbContext.PendingReviews.Add(pending);
        await _dbContext.SaveChangesAsync();
    }
}
