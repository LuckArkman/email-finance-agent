using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;
using Dapper;
using Hermes.Analytics.Models;

namespace Hermes.Analytics;

public class DashboardKpisService
{
    private readonly IDbConnection _dbConnection;

    public DashboardKpisService(IDbConnection dbConnection)
    {
        _dbConnection = dbConnection;
    }

    public async Task<KpiSummary> GetKpisAsync()
    {
        const string sql = @"
            SELECT 
                SUM(""PendingInvoicesAmount"") AS TotalPending,
                SUM(""ReconciledInvoicesAmount"") AS TotalReconciled,
                SUM(""TotalReceiptsAmount"") - SUM(""PendingInvoicesAmount"") AS Balance
            FROM vw_daily_cashflow;
        ";

        var result = await _dbConnection.QueryFirstOrDefaultAsync<KpiSummary>(sql);
        return result ?? new KpiSummary();
    }

    public async Task<IEnumerable<DailyCashflow>> GetDailyCashflowAsync()
    {
        const string sql = @"
            SELECT * FROM vw_daily_cashflow
            ORDER BY ""Date"" DESC
            LIMIT 30;
        ";

        return await _dbConnection.QueryAsync<DailyCashflow>(sql);
    }

    public async Task RefreshMaterializedViewAsync()
    {
        await _dbConnection.ExecuteAsync("REFRESH MATERIALIZED VIEW vw_daily_cashflow;");
    }
}
