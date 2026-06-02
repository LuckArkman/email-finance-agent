using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Gateway.Extensions;

public static class SecurityConfiguration
{
    public static IServiceCollection AddHermesSecurity(this IServiceCollection services)
    {
        // Política rigorosa de CORS
        services.AddCors(options =>
        {
            options.AddPolicy("StrictCorsPolicy", builder =>
            {
                builder.WithOrigins("http://localhost:5173", "https://hermes.empresa.com")
                       .AllowAnyMethod()
                       .AllowAnyHeader()
                       .AllowCredentials() // Obrigatório para Cookies HTTP-Only ou Autenticação avançada
                       .SetPreflightMaxAge(TimeSpan.FromMinutes(10));
            });
        });

        // Força HSTS com validade de 365 dias
        services.AddHsts(options =>
        {
            options.Preload = true;
            options.IncludeSubDomains = true;
            options.MaxAge = TimeSpan.FromDays(365);
        });

        return services;
    }

    public static IApplicationBuilder UseHermesSecurity(this IApplicationBuilder app, bool isDevelopment)
    {
        // Se estivermos em produção, exigimos a criptografia HTTP extrema
        if (!isDevelopment)
        {
            app.UseHsts();
            app.UseHttpsRedirection();
        }

        app.UseCors("StrictCorsPolicy");

        // Headers adicionais anti-CSRF / anti-XSS
        app.Use(async (context, next) =>
        {
            context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
            context.Response.Headers.Append("X-Frame-Options", "DENY");
            context.Response.Headers.Append("X-XSS-Protection", "1; mode=block");
            await next();
        });

        return app;
    }
}
