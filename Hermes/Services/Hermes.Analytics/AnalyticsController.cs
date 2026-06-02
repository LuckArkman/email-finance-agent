using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace Hermes.Analytics;

[ApiController]
[Route("api/hermes/[controller]")]
public class AnalyticsController : ControllerBase
{
    private readonly DashboardKpisService _kpisService;

    public AnalyticsController(DashboardKpisService kpisService)
    {
        _kpisService = kpisService;
    }

    [HttpGet("kpis")]
    public async Task<IActionResult> GetKpis()
    {
        var kpis = await _kpisService.GetKpisAsync();
        return Ok(kpis);
    }

    [HttpGet("cashflow")]
    public async Task<IActionResult> GetDailyCashflow()
    {
        var cashflow = await _kpisService.GetDailyCashflowAsync();
        return Ok(cashflow);
    }

    [HttpPost("refresh")]
    public async Task<IActionResult> RefreshMaterializedView()
    {
        await _kpisService.RefreshMaterializedViewAsync();
        return Ok(new { message = "Materialized View refreshed successfully." });
    }
}
