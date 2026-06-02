using System;

namespace Hermes.Analytics.Models;

public class DailyCashflow
{
    public DateTime Date { get; set; }
    public decimal PendingInvoicesAmount { get; set; }
    public decimal ReconciledInvoicesAmount { get; set; }
    public decimal TotalReceiptsAmount { get; set; }
}

public class KpiSummary
{
    public decimal TotalPending { get; set; }
    public decimal TotalReconciled { get; set; }
    public decimal Balance { get; set; }
}
