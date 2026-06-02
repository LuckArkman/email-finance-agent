using System;
using System.Linq;
using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class MathValidator
{
    private readonly ILogger<MathValidator> _logger;
    private const decimal AllowedDiscrepancy = 1.0m; // Tolerância máxima de 1 unidade monetária (ex: 1 Euro) por causa de IVAs no total

    public MathValidator(ILogger<MathValidator> logger)
    {
        _logger = logger;
    }

    public void ValidateTotal(InvoiceExtractionModel model)
    {
        if (model == null || model.Items == null || !model.Items.Any())
        {
            _logger.LogInformation("No items found. Skipping math validation.");
            return;
        }

        decimal calculatedTotal = model.Items.Sum(item => item.Quantity * item.Price);
        decimal discrepancy = Math.Abs(calculatedTotal - model.Total);

        if (discrepancy > AllowedDiscrepancy)
        {
            _logger.LogWarning(
                $"[MATH DISCREPANCY DETECTED] The extracted Total ({model.Total}) does not match the sum of Line Items ({calculatedTotal}). " +
                $"Difference: {discrepancy}. This could be an LLM Hallucination or a tax inclusion issue."
            );
            // Em vez de atirar excepção, deixamos fluir (Soft-Fail policy) para que um utilizador reveja.
        }
        else
        {
            _logger.LogInformation($"Math validation passed! Calculated: {calculatedTotal} | Extracted: {model.Total}");
        }
    }
}
