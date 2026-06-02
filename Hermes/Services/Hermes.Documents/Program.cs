using Microsoft.AspNetCore.Builder;
using Hermes.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Hermes.Domain.Tenancy;

namespace Hermes.Documents;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Configuração de BD (partilhada)
        builder.Services.AddDbContext<HermesDbContext>(options =>
            options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
        
        // Mock do Tenant Provider
        builder.Services.AddSingleton<ITenantProvider, MockTenantProvider>();

        // AWS S3 / MinIO e Serviço de Upload
        builder.Services.AddSingleton<S3BlobClient>();
        builder.Services.AddHostedService<DocumentStorageService>();

        var app = builder.Build();

        // Endpoints Web
        app.MapUploadEndpoints();

        app.Run();
    }
}

public class MockTenantProvider : ITenantProvider
{
    public TenantContext GetCurrentTenant() => new TenantContext { TenantId = System.Guid.Parse("00000000-0000-0000-0000-000000000001") };
}
