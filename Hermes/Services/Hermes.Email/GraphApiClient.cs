using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Graph;
using Microsoft.Graph.Models;

namespace Hermes.Email;

public class GraphApiClient
{
    private readonly ILogger<GraphApiClient> _logger;
    private readonly IConfiguration _configuration;
    private readonly GraphServiceClient _graphClient;

    public GraphApiClient(ILogger<GraphApiClient> logger, IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;

        var tenantId = _configuration["Graph:TenantId"];
        var clientId = _configuration["Graph:ClientId"];
        var clientSecret = _configuration["Graph:ClientSecret"];

        // ClientCredentials Flow for Daemon Background Services (Application Permissions)
        var options = new ClientSecretCredentialOptions
        {
            AuthorityHost = AzureAuthorityHosts.AzurePublicCloud,
        };

        var clientSecretCredential = new ClientSecretCredential(tenantId, clientId, clientSecret, options);
        var scopes = new[] { "https://graph.microsoft.com/.default" };

        _graphClient = new GraphServiceClient(clientSecretCredential, scopes);
    }

    public async Task ProcessUnreadEmailsAsync(string targetUserId, CancellationToken cancellationToken)
    {
        try
        {
            // /users/{id}/messages?$filter=isRead eq false
            var messages = await _graphClient.Users[targetUserId].Messages.GetAsync(requestConfiguration =>
            {
                requestConfiguration.QueryParameters.Filter = "isRead eq false";
                requestConfiguration.QueryParameters.Expand = new[] { "attachments" };
            }, cancellationToken);

            if (messages?.Value == null) return;

            foreach (var message in messages.Value)
            {
                _logger.LogInformation($"Processing Graph Message: {message.Subject} from {message.From?.EmailAddress?.Address}");
                
                // Process attachments
                if (message.HasAttachments == true && message.Attachments != null)
                {
                    foreach (var attachment in message.Attachments)
                    {
                        if (attachment is FileAttachment fileAttachment)
                        {
                            var tempPath = Path.Combine(Path.GetTempPath(), $"{message.Id}_{fileAttachment.Name}");
                            if (fileAttachment.ContentBytes != null)
                            {
                                await File.WriteAllBytesAsync(tempPath, fileAttachment.ContentBytes, cancellationToken);
                            }
                        }
                    }
                }

                // TODO: Publicar no EventBus (Publish(new EmailReceivedEvent(...)))

                // Mark as read
                var updateMessage = new Message { IsRead = true };
                await _graphClient.Users[targetUserId].Messages[message.Id].PatchAsync(updateMessage, cancellationToken: cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing Graph emails");
        }
    }
}
