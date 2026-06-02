using System;
using System.Threading.Tasks;
using MassTransit;
using Microsoft.Extensions.Logging;
using Hermes.EventBus.Events;

namespace Hermes.Analytics.Consumers;

public class CacheInvalidatorConsumer : IConsumer<InvoiceReconciledEvent>
{
    private readonly RedisCacheService _cacheService;
    private readonly ILogger<CacheInvalidatorConsumer> _logger;

    public CacheInvalidatorConsumer(RedisCacheService cacheService, ILogger<CacheInvalidatorConsumer> logger)
    {
        _cacheService = cacheService;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<InvoiceReconciledEvent> context)
    {
        var tenantId = context.Message.TenantId;

        // Limpa a cache de KPIs e Cashflow Mensal para garantir dados frescos
        var kpiKey = $"analytics_kpi_{tenantId}";
        await _cacheService.RemoveAsync(kpiKey);

        _logger.LogInformation($"[Cache Evicted] Reconciliação concluída para Tenant {tenantId}. Cache de Analytics limpa.");
    }
}
