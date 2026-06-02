using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

namespace Hermes.Notifications.Services;

public class WebhookOutboundDispatcher
{
    private readonly HttpClient _httpClient;

    public WebhookOutboundDispatcher(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task DispatchInvoiceAsync(Guid invoiceId, string tenantId, object payload)
    {
        // Num cenário real, o destino dependeria do TenantId (ex: Tabela de Webhooks do cliente na BD)
        // Simulando a ponte B2B para o SAP/Sage
        var destinationUrl = "https://api.parceiro-b2b.com/v1/invoices/import";

        Console.WriteLine($"[Webhook] Disparando Fatura {invoiceId} do Tenant {tenantId} para o ERP Externo...");

        var response = await _httpClient.PostAsJsonAsync(destinationUrl, payload);
        
        // Se a API externa devolver 503 ou 500, o EnsureSuccessStatusCode() atira a exception.
        // A política do Polly configurada no Program.cs vai apanhar e fazer Retry/Circuit Breaking!
        response.EnsureSuccessStatusCode();

        Console.WriteLine($"[Webhook] Fatura {invoiceId} exportada com sucesso para o ERP!");
    }
}
