

using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace Hermes.Email;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Background services & Jobs
        builder.Services.AddTransient<EmailSyncJob>();
        builder.Services.AddHostedService<ImapListenerService>();

        // Microsoft Graph Client
        builder.Services.AddSingleton<GraphApiClient>();

        // Gmail Client Factory
        builder.Services.AddSingleton<GmailServiceFactory>();

        // MIME Parsing & Filters
        builder.Services.AddSingleton<AttachmentFilter>();
        builder.Services.AddTransient<MimeMessageParser>();

        var app = builder.Build();

        // Webhook Receivers
        app.MapGraphWebhooks();
        app.MapGmailWebhooks();

        app.Run();
    }
}
