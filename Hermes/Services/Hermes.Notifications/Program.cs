using Hermes.Notifications;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using System.Threading.Tasks;
using MassTransit;
using Polly;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSignalR();
builder.Services.AddScoped<Hermes.Notifications.Services.IAgentStreamService, Hermes.Notifications.Services.AgentStreamService>();

// Webhook Outbound Dispatcher + Polly
builder.Services.AddHttpClient<Hermes.Notifications.Services.WebhookOutboundDispatcher>()
    .AddTransientHttpErrorPolicy(policy => policy.WaitAndRetryAsync(3, _ => System.TimeSpan.FromSeconds(2)))
    .AddTransientHttpErrorPolicy(policy => policy.CircuitBreakerAsync(5, System.TimeSpan.FromSeconds(30)));

// MassTransit & RabbitMQ Setup
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<Hermes.Notifications.Consumers.ExtractionCompletedConsumer>();
    x.AddConsumer<Hermes.Notifications.Consumers.InvoiceReconciledConsumer>();
    x.AddConsumer<Hermes.Notifications.Consumers.InvoiceFinalizedConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration["RabbitMQ:Host"] ?? "localhost", "/", h =>
        {
            h.Username(builder.Configuration["RabbitMQ:Username"] ?? "guest");
            h.Password(builder.Configuration["RabbitMQ:Password"] ?? "guest");
        });

        cfg.ConfigureEndpoints(context);
    });
});

// Configurar JWT Bearer com suporte para Query String (WebSockets)
var jwtKey = builder.Configuration["Jwt:Key"] ?? "HermesSuperSecretKeyForDevelopmentOnly123!";
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };

        // Intercetar Query String para SignalR
        options.Events = new JwtBearerEvents
        {
            OnMessageReceived = context =>
            {
                var accessToken = context.Request.Query["access_token"];

                // Se o pedido for para o Hub de notificações
                var path = context.HttpContext.Request.Path;
                if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hub/notifications"))
                {
                    context.Token = accessToken;
                }
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization();

builder.Services.AddCors(options =>
{
    options.AddPolicy("SignalRPolicy", builder =>
    {
        builder.SetIsOriginAllowed(_ => true) // Em produção, colocar domínios específicos
               .AllowAnyMethod()
               .AllowAnyHeader()
               .AllowCredentials();
    });
});

var app = builder.Build();

app.UseRouting();

app.UseCors("SignalRPolicy");

app.UseAuthentication();
app.UseAuthorization();

app.MapHub<NotificationHub>("/hub/notifications");

app.Run();
public partial class Program { }
