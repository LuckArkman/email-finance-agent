using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Hermes.Infrastructure.Data;
using Hermes.Domain.Financial;

namespace Hermes.Gateway.Mcp;

/// <summary>
/// MCP (Model Context Protocol) Server — expõe ferramentas do Hermes .NET
/// para que o Hermes Agent (Nous Research) as descubra e invoque nativamente.
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
        ),
        new McpTool(
            Name: "search_knowledge_base",
            Description: "Search the vector database for relevant invoices and financial documents using semantic search.",
            InputSchema: new
            {
                type = "object",
                required = new[] { "query" },
                properties = new
                {
                    query = new { type = "string", description = "The search query (e.g. 'faturas pendentes da contoso', 'invoice for AWS')" }
                }
            }
        )
    };

    public static void MapMcpEndpoints(this WebApplication app)
    {
        var mcpKey = Environment.GetEnvironmentVariable("HERMES_MCP_KEY") ?? "";

        // MCP Tool Discovery
        app.MapGet("/mcp/tools", (HttpContext ctx) =>
        {
            if (!IsAuthorized(ctx, mcpKey)) return Results.Unauthorized();
            return Results.Ok(new { tools = _tools });
        });

        // MCP Tool Execution
        app.MapPost("/mcp/tools/{toolName}", async (
            string toolName,
            HttpContext ctx,
            ILogger<WebApplication> logger,
            HermesDbContext dbContext,
            IHttpClientFactory httpClientFactory) =>
        {
            if (!IsAuthorized(ctx, mcpKey)) return Results.Unauthorized();

            using var body = await JsonDocument.ParseAsync(ctx.Request.Body);
            var input = body.RootElement;

            logger.LogInformation("[MCP] Hermes Agent invocou ferramenta: {Tool}", toolName);

            var result = toolName switch
            {
                "ingest_invoice" => await HandleIngestInvoice(input, dbContext),
                "get_supplier_history" => await HandleGetSupplierHistory(input, dbContext),
                "flag_for_review" => await HandleFlagForReview(input, dbContext),
                "get_pending_invoices" => await HandleGetPendingInvoices(dbContext),
                "search_knowledge_base" => await HandleSearchKnowledgeBase(input, httpClientFactory, logger),
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

    private static async Task<IResult> HandleIngestInvoice(JsonElement input, HermesDbContext dbContext)
    {
        var invNum = input.TryGetProperty("invoice_number", out var inv) ? inv.GetString() : "UNKNOWN";
        var invoice = new Invoice
        {
            InvoiceNumber = invNum ?? "UNKNOWN",
            TotalAmount = input.TryGetProperty("total_amount", out var ta) ? (ta.ValueKind == JsonValueKind.Number ? ta.GetDecimal() : 0) : 0,
            Currency = input.TryGetProperty("currency", out var cur) ? cur.GetString() ?? "EUR" : "EUR",
            VendorName = input.TryGetProperty("supplier_name", out var sn) ? sn.GetString() : null,
            Status = InvoiceStatus.Draft,
            IssueDate = DateTime.UtcNow
        };

        dbContext.Invoices.Add(invoice);
        await dbContext.SaveChangesAsync();

        return Results.Accepted("/api/hermes/invoices/ingest", new
        {
            status = "queued",
            message = "Invoice saved to database and ready for pipeline.",
            tracking_id = invoice.Id.ToString()
        });
    }

    private static async Task<IResult> HandleGetSupplierHistory(JsonElement input, HermesDbContext dbContext)
    {
        var name = input.TryGetProperty("supplier_name", out var n) ? n.GetString()?.ToLower() : null;
        var taxId = input.TryGetProperty("supplier_tax_id", out var tid) ? tid.GetString()?.ToLower() : null;

        var query = dbContext.Invoices.AsQueryable();

        if (!string.IsNullOrEmpty(name))
        {
            query = query.Where(i => i.VendorName != null && i.VendorName.ToLower().Contains(name));
        }
        else if (!string.IsNullOrEmpty(taxId))
        {
            query = query.Where(i => i.VendorTaxId != null && i.VendorTaxId.ToLower() == taxId);
        }
        else
        {
            return Results.BadRequest(new { error = "Must provide supplier_name or supplier_tax_id." });
        }

        var invoices = await query
            .OrderByDescending(i => i.IssueDate)
            .Select(i => new
            {
                i.InvoiceNumber,
                i.TotalAmount,
                i.Currency,
                i.IssueDate,
                Status = i.Status.ToString()
            })
            .ToListAsync();

        return Results.Ok(new
        {
            supplier = name ?? taxId,
            invoice_count = invoices.Count,
            last_invoice_date = invoices.FirstOrDefault()?.IssueDate.ToString("yyyy-MM-dd"),
            history = invoices
        });
    }

    private static async Task<IResult> HandleFlagForReview(JsonElement input, HermesDbContext dbContext)
    {
        var invNum = input.TryGetProperty("invoice_number", out var inv) ? inv.GetString() : null;
        var reason = input.TryGetProperty("reason", out var r) ? r.GetString() : null;

        var invoice = await dbContext.Invoices.FirstOrDefaultAsync(i => i.InvoiceNumber == invNum);
        if (invoice != null)
        {
            invoice.Status = InvoiceStatus.ReviewRequired;
            // The reason can be logged or placed in a note if domain model supports it later.
            await dbContext.SaveChangesAsync();

            return Results.Ok(new
            {
                status = "flagged",
                invoice_number = invNum,
                reason = reason
            });
        }

        return Results.NotFound(new { error = "Invoice not found." });
    }

    private static async Task<IResult> HandleGetPendingInvoices(HermesDbContext dbContext)
    {
        var invoices = await dbContext.Invoices
            .Where(i => i.Status == InvoiceStatus.Pending)
            .Select(i => new
            {
                i.InvoiceNumber,
                i.VendorName,
                i.TotalAmount,
                i.Currency,
                i.DueDate,
                Status = i.Status.ToString()
            })
            .Take(5)
            .ToListAsync();

        return Results.Ok(new { pending_count = invoices.Count, invoices = invoices });
    }

    private static async Task<IResult> HandleSearchKnowledgeBase(JsonElement input, IHttpClientFactory httpClientFactory, ILogger logger)
    {
        var query = input.TryGetProperty("query", out var q) ? q.GetString() : null;
        if (string.IsNullOrWhiteSpace(query))
        {
            return Results.BadRequest(new { error = "Query is required for knowledge base search." });
        }

        try
        {
            var client = httpClientFactory.CreateClient();
            var response = await client.GetAsync($"http://hermes-vector:8080/api/hermes/Search?q={Uri.EscapeDataString(query)}");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return Results.Ok(new { results = JsonSerializer.Deserialize<JsonElement>(content) });
            }
            
            logger.LogWarning("[MCP] Falha na pesquisa vetorial. Status: {Status}", response.StatusCode);
            return Results.StatusCode((int)response.StatusCode);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "[MCP] Erro ao pesquisar no vector db.");
            return Results.Problem(detail: ex.Message);
        }
    }
}

public record McpTool(string Name, string Description, object InputSchema);
