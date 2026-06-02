using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace Hermes.Vector;

[ApiController]
[Route("api/hermes/[controller]")]
public class SearchController : ControllerBase
{
    private readonly SearchQueryService _searchQueryService;

    public SearchController(SearchQueryService searchQueryService)
    {
        _searchQueryService = searchQueryService;
    }

    [HttpGet]
    public async Task<IActionResult> SemanticSearch([FromQuery] string q)
    {
        if (string.IsNullOrWhiteSpace(q))
        {
            return BadRequest(new { error = "O parâmetro 'q' é obrigatório." });
        }

        var results = await _searchQueryService.SearchInvoicesAsync(q, topK: 5);

        // Map para DTO anónimo para evitar serializar o Vector inteiro, que pode pesar o JSON
        var response = results.ConvertAll(i => new
        {
            i.Id,
            i.TenantId,
            i.DocumentId,
            i.Vendor,
            i.Nif,
            i.InvoiceDate,
            i.TotalAmount,
            i.CreatedAt
        });

        return Ok(response);
    }
}
