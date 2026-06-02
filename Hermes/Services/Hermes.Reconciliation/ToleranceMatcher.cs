using System;

namespace Hermes.Reconciliation;

public class ToleranceMatcher
{
    private const decimal AllowedVariance = 0.05m; // 5 cêntimos de tolerância
    private const int AllowedDaysVariance = 3; // 3 dias de diferença

    public bool IsMatch(ReconcilableInvoice invoice, ReconcilableReceipt receipt)
    {
        // 1. Validar NIF
        if (!string.Equals(invoice.Nif, receipt.Nif, StringComparison.OrdinalIgnoreCase))
            return false;

        // 2. Validar Tolerância de Valor
        var diffAmount = Math.Abs(invoice.TotalAmount - receipt.Amount);
        if (diffAmount > AllowedVariance)
            return false;

        // 3. Validar Datas (se a fatura tiver data)
        if (invoice.InvoiceDate.HasValue)
        {
            var diffDays = Math.Abs((invoice.InvoiceDate.Value - receipt.PaymentDate).TotalDays);
            if (diffDays > AllowedDaysVariance)
                return false;
        }

        return true;
    }
}
