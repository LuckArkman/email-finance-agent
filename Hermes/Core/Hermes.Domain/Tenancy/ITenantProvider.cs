namespace Hermes.Domain.Tenancy;

public interface ITenantProvider
{
    TenantContext GetCurrentTenant();
}
