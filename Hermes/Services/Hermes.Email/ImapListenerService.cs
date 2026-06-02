using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Email;

public class ImapListenerService : BackgroundService
{
    private readonly ILogger<ImapListenerService> _logger;
    private readonly IServiceProvider _serviceProvider;

    public ImapListenerService(ILogger<ImapListenerService> logger, IServiceProvider serviceProvider)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("IMAP Listener Service starting...");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var syncJob = scope.ServiceProvider.GetRequiredService<EmailSyncJob>();

                _logger.LogInformation("Checking for new emails...");
                await syncJob.ProcessUnreadEmailsAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred during email sync cycle.");
            }

            // Polling interval - 10 segundos
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
}
