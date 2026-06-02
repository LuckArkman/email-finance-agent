using HealthChecks.UI.Client;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Gateway.Extensions;

public static class HealthCheckConfiguration
{
    public static IServiceCollection AddHermesHealthChecks(this IServiceCollection services, IConfiguration configuration)
    {
        var dbConn = configuration["Database:ConnectionString"] ?? "Host=localhost;Database=hermes_db;Username=postgres;Password=postgres";
        var rabbitConn = $"amqp://{configuration["EventBus:Username"] ?? "guest"}:{configuration["EventBus:Password"] ?? "guest"}@{configuration["EventBus:Host"] ?? "localhost"}:5672";
        var redisConn = configuration["ConnectionStrings:Redis"] ?? "localhost:6379";

        services.AddHealthChecks()
            // Liveness (O API está UP?)
            .AddCheck("Self", () => Microsoft.Extensions.Diagnostics.HealthChecks.HealthCheckResult.Healthy(), tags: new[] { "live" })
            // Readiness (Dependências estão UP?)
            .AddNpgSql(dbConn, name: "PostgreSQL", tags: new[] { "ready", "db" })
            // .AddRabbitMQ(rabbitConn, name: "RabbitMQ", tags: new[] { "ready", "queue" })
            .AddRedis(redisConn, name: "Redis", tags: new[] { "ready", "cache" });

        return services;
    }

    public static IApplicationBuilder UseHermesHealthChecks(this IApplicationBuilder app)
    {
        // Resposta imediata Liveness
        app.UseHealthChecks("/health/live", new HealthCheckOptions
        {
            Predicate = r => r.Tags.Contains("live")
        });

        // Resposta profunda Readiness com UI amigável em JSON (Para o Docker/K8s ler)
        app.UseHealthChecks("/health/ready", new HealthCheckOptions
        {
            Predicate = r => r.Tags.Contains("ready"),
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
        });

        return app;
    }
}
