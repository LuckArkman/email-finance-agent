using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using MailKit;
using MailKit.Net.Imap;
using MailKit.Search;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Hermes.Email;

public class EmailSyncJob
{
    private readonly ILogger<EmailSyncJob> _logger;
    private readonly IConfiguration _configuration;

    public EmailSyncJob(ILogger<EmailSyncJob> logger, IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
    }

    public async Task ProcessUnreadEmailsAsync(CancellationToken cancellationToken)
    {
        var host = _configuration["Imap:Host"] ?? "imap.gmail.com";
        var port = int.Parse(_configuration["Imap:Port"] ?? "993");
        var useSsl = bool.Parse(_configuration["Imap:UseSsl"] ?? "true");
        var username = _configuration["Imap:Username"];
        var password = _configuration["Imap:Password"];

        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
        {
            _logger.LogWarning("IMAP credentials not configured. Skipping sync.");
            return;
        }

        using var client = new ImapClient();
        try
        {
            await client.ConnectAsync(host, port, useSsl, cancellationToken);
            await client.AuthenticateAsync(username, password, cancellationToken);

            var inbox = client.Inbox;
            await inbox.OpenAsync(FolderAccess.ReadWrite, cancellationToken);

            var uids = await inbox.SearchAsync(SearchQuery.NotSeen, cancellationToken);
            _logger.LogInformation($"Found {uids.Count} unread emails.");

            foreach (var uid in uids)
            {
                var message = await inbox.GetMessageAsync(uid, cancellationToken);
                
                _logger.LogInformation($"Processing message: {message.Subject} from {message.From}");

                var subject = message.Subject ?? "NoSubject";
                var safeSubject = string.Concat(subject.Split(Path.GetInvalidFileNameChars()));
                var fileName = $"{uid}_{safeSubject}.eml";
                var tempPath = Path.Combine(Path.GetTempPath(), fileName);
                
                await message.WriteToAsync(tempPath, cancellationToken);

                // TODO: Publicar o evento no EventBus (Publish(new EmailReceivedEvent(...)))

                // Marcar como lido
                await inbox.AddFlagsAsync(uid, MessageFlags.Seen, true, cancellationToken);
            }

            await client.DisconnectAsync(true, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing unread emails.");
        }
    }
}
