using System;
using System.Net.Http;
using Polly;
using Polly.Extensions.Http;

namespace Hermes.Extraction.Extensions;

public static class ResiliencePolicyConfiguration
{
    public static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .WaitAndRetryAsync(3, retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)), 
                onRetry: (outcome, timespan, retryAttempt, context) =>
                {
                    // Em produção, deve-se usar ILogger. Aqui usamos Console genérico por simplicidade.
                    Console.WriteLine($"[Polly] Delaying for {timespan.TotalSeconds} seconds, then making retry {retryAttempt}");
                });
    }

    public static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30),
                onBreak: (outcome, timespan) =>
                {
                    Console.WriteLine($"[Polly] Circuit Broken! Waiting {timespan.TotalSeconds} seconds.");
                },
                onReset: () =>
                {
                    Console.WriteLine("[Polly] Circuit Reset! Traffic is flowing again.");
                },
                onHalfOpen: () =>
                {
                    Console.WriteLine("[Polly] Circuit Half-Open! Testing the waters...");
                });
    }
}
