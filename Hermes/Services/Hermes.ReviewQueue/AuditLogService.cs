using System.Threading.Tasks;

namespace Hermes.ReviewQueue;

public class AuditLogService
{
    private readonly ReviewDbContext _dbContext;

    public AuditLogService(ReviewDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task LogActionAsync(System.Guid pendingReviewId, string action, string details, string user)
    {
        var log = new AuditLog
        {
            PendingReviewId = pendingReviewId,
            Action = action,
            Details = details,
            User = user
        };

        _dbContext.AuditLogs.Add(log);
        await _dbContext.SaveChangesAsync();
    }
}
