using Hermes.Domain.Tenancy;
using Hermes.Infrastructure.Data;
using Hermes.Infrastructure.Tenancy;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Infrastructure.Extensions;

public static class DatabaseConfiguration
{
    public static IServiceCollection AddHermesDatabase(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddSingleton<Microsoft.AspNetCore.Http.IHttpContextAccessor, Microsoft.AspNetCore.Http.HttpContextAccessor>();
        services.AddScoped<ITenantProvider, HttpTenantProvider>();

        var connectionString = configuration.GetConnectionString("DefaultConnection");

        services.AddDbContext<HermesDbContext>(options =>
        {
            options.UseNpgsql(connectionString);
            options.ConfigureWarnings(w => w.Ignore(Microsoft.EntityFrameworkCore.Diagnostics.RelationalEventId.PendingModelChangesWarning));
        });

        return services;
    }
}
