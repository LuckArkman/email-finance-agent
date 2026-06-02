using System;
using Hermes.Domain.Tenancy;
using Microsoft.AspNetCore.Http;

namespace Hermes.Infrastructure.Tenancy;

public class HttpTenantProvider : ITenantProvider
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private const string TenantHeaderName = "X-Tenant-ID";

    public HttpTenantProvider(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public TenantContext GetCurrentTenant()
    {
        var context = _httpContextAccessor.HttpContext;
        if (context != null && context.Request.Headers.TryGetValue(TenantHeaderName, out var tenantValues))
        {
            var tenantIdString = tenantValues.ToString();
            if (Guid.TryParse(tenantIdString, out var tenantId))
            {
                return new TenantContext { TenantId = tenantId };
            }
        }

        // Se não existir Tenant no cabeçalho ou o contexto for nulo (p. ex: Background Services),
        // devolve Empty em vez de crachar, o EF Core lidará com a inserção e bloqueará caso o campo
        // seja obrigatório no SaveChanges se faltar um Tenant.
        return new TenantContext { TenantId = Guid.Empty };
    }
}
