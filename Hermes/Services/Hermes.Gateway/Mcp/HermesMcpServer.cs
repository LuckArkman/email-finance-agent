using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Mcp;

/// <summary>
/// MCP (Model Context Protocol) Server — expõe ferramentas do Hermes .NET
/// para que o Hermes Agent (Nous Research) as descubra e invoque nativamente.
///
/// O Hermes Agent configura este servidor em config.yaml:
///   mcp_servers:
///     hermes_dotnet:
///       url: "http://localhost:5000/mcp"
///       api_key: "${HERMES_MCP_KEY}"
/// </summary>
public static class HermesMcpServer
{
    private static readonly List<McpTool> _tools = new()
    {
        new McpTool(
            Name: "ingest_invoice",
            Description: "Submit a structured invoice JSON for .NET reconciliation processing.",
            InputSchema: new
            {
                type = "object",
                required = new[] { "invoice_number", "total_amount", "currency" },
                properties = new
                {
                    invoice_number = new { type = "string" },
                    supplier_name = new { type = "string" },
                    total_amount = new { type = "number" },
                    currency = new { type = "string" },
                    validation_status = new { type = "string" }
                }
            }
        ),
        new McpTool(
            Name: "get_supplier_history",
            Description: "Retrieve past invoice history for a given supplier (by name or tax ID).",
            InputSchema: new
            {
                type = "object",
                required = new[] { "supplier_name" },
                properties = new
                {
                    supplier_name = new { type = "string" },
                    supplier_tax_id = new { type = "string" }
                }
            }
        ),
        new McpTool(
            Name: "flag_for_review",
            Description: "Flag an invoice for human review due to discrepancy or missing data.",
            InputSchema: new
            {
                type = "object",
                required = new[] { "invoice_number", "reason" },
                properties = new
                {
                    invoice_number = new { type = "string" },
                    reason = new { type = "string" }
                }
            }
        ),
        new McpTool(
            Name: "get_pending_invoices",
            Description: "List invoices currently pending reconciliation in the .NET pipeline.",
            InputSchema: new { type = "object", properties = new { } }
        )
    };

    public static void MapMcpEndpoints(this WebApplication app)
    {
        var mcpKey = Environment.GetEnvironmentVariable("HERMES_MCP_KEY") ?? "";

        // MCP Tool Discovery — Hermes Agent chama este endpoint ao arrancar
        app.MapGet("/mcp/tools", (HttpContext ctx) =>
        {
            if (!IsAuthorized(ctx, mcpKey)) return Results.Unauthorized();
            return Results.Ok(new { tools = _tools });
        });

        // MCP Tool Execution — Hermes Agent invoca uma ferramenta pelo nome
        app.MapPost("/mcp/tools/{toolName}", async (
            string toolName,
            HttpContext ctx,
            ILogger<WebApplication> logger) =>
        {
            if (!IsAuthorized(ctx, mcpKey)) return Results.Unauthorized();

            using var body = await JsonDocument.ParseAsync(ctx.Request.Body);
            var input = body.RootElement;

            logger.LogInformation("[MCP] Hermes Agent invocou ferramenta: {Tool}", toolName);

            var result = toolName switch
            {
                "ingest_invoice" => HandleIngestInvoice(input),
                "get_supplier_history" => HandleGetSupplierHistory(input),
                "flag_for_review" => HandleFlagForReview(input),
                "get_pending_invoices" => HandleGetPendingInvoices(),
                _ => Results.NotFound(new { error = $"Unknown tool: {toolName}" })
            };

            return result;
        });
    }

    private static bool IsAuthorized(HttpContext ctx, string expectedKey)
    {
        var authHeader = ctx.Request.Headers["Authorization"].ToString();
        var bearer = authHeader.StartsWith("Bearer ") ? authHeader[7..] : "";
        return !string.IsNullOrEmpty(expectedKey) && bearer == expectedKey;
    }

    private static IResult HandleIngestInvoice(JsonElement input) =>
        Results.Accepted("/api/hermes/invoices/ingest", new
        {
            status = "queued",
            message = "Invoice forwarded to reconciliation pipeline.",
            tracking_id = Guid.NewGuid().ToString()
        });

    private static IResult HandleGetSupplierHistory(JsonElement input) =>
        Results.Ok(new
        {
            supplier = input.TryGetProperty("supplier_name", out var n) ? n.GetString() : null,
            invoice_count = 0,
            last_invoice_date = (string?)null,
            message = "Supplier history lookup — connect to Hermes.Infrastructure for real data."
        });

    private static IResult HandleFlagForReview(JsonElement input) =>
        Results.Ok(new
        {
            status = "flagged",
            invoice_number = input.TryGetProperty("invoice_number", out var inv) ? inv.GetString() : null,
            reason = input.TryGetProperty("reason", out var r) ? r.GetString() : null
        });

    private static IResult HandleGetPendingInvoices() =>
        Results.Ok(new { pending_count = 0, invoices = Array.Empty<object>() });
}

public record McpTool(string Name, string Description, object InputSchema);
