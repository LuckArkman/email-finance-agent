using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Serilog;

namespace Hermes.Gateway.Extensions;

public static class TelemetryStartup
{
    public static void AddHermesTelemetry(this WebApplicationBuilder builder)
    {
        // Serilog setup
        builder.Host.UseSerilog((context, config) =>
        {
            config.ReadFrom.Configuration(context.Configuration)
                  .Enrich.FromLogContext()
                  .Enrich.WithCorrelationIdHeader("X-Correlation-ID")
                  .WriteTo.Console();
        });

        // Sentry setup
        builder.WebHost.UseSentry(o =>
        {
            // Dummy DSN for demonstration, ideally from config
            o.Dsn = "https://examplePublicKey@o0.ingest.sentry.io/0";
            o.TracesSampleRate = 1.0;
        });

        // OpenTelemetry setup
        builder.Services.AddOpenTelemetry()
            .WithTracing(tracing =>
            {
                tracing.AddAspNetCoreInstrumentation()
                       .AddHttpClientInstrumentation();
            })
            .WithMetrics(metrics =>
            {
                metrics.AddAspNetCoreInstrumentation()
                       .AddHttpClientInstrumentation()
                       .AddPrometheusExporter();
            });
    }
}
