using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Hermes.Analytics.Migrations
{
    /// <inheritdoc />
    public partial class InitialAnalyticsMigration : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                CREATE MATERIALIZED VIEW vw_daily_cashflow AS
                WITH DateSeries AS (
                    SELECT generate_series(
                        COALESCE((SELECT MIN(""CreatedAt"") FROM ""Invoices""), current_date - interval '30 days'),
                        current_date,
                        '1 day'::interval
                    )::date AS ""Date""
                )
                SELECT 
                    ds.""Date"",
                    COALESCE(SUM(i.""TotalAmount"") FILTER (WHERE i.""IsReconciled"" = false), 0) AS ""PendingInvoicesAmount"",
                    COALESCE(SUM(i.""TotalAmount"") FILTER (WHERE i.""IsReconciled"" = true), 0) AS ""ReconciledInvoicesAmount"",
                    COALESCE(SUM(r.""Amount""), 0) AS ""TotalReceiptsAmount""
                FROM DateSeries ds
                LEFT JOIN ""Invoices"" i ON i.""CreatedAt""::date = ds.""Date""
                LEFT JOIN ""Receipts"" r ON r.""CreatedAt""::date = ds.""Date""
                GROUP BY ds.""Date"";
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("DROP MATERIALIZED VIEW IF EXISTS vw_daily_cashflow;");
        }
    }
}
