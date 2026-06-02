using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Hermes.Extraction;

public record InvoiceItemExtractionModel
{
    [JsonPropertyName("Description")]
    public string Description { get; init; } = string.Empty;

    [JsonPropertyName("Quantity")]
    public int Quantity { get; init; }

    [JsonPropertyName("Price")]
    public decimal Price { get; init; }
}

public record InvoiceExtractionModel
{
    [JsonPropertyName("Vendor")]
    public string Vendor { get; init; } = string.Empty;

    [JsonPropertyName("Nif")]
    public string Nif { get; init; } = string.Empty;

    [JsonPropertyName("Date")]
    public string Date { get; init; } = string.Empty;

    [JsonPropertyName("Total")]
    public decimal Total { get; init; }

    [JsonPropertyName("Items")]
    public List<InvoiceItemExtractionModel> Items { get; init; } = new();
}
