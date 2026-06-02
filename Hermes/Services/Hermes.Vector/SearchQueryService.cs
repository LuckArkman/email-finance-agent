using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Pgvector.EntityFrameworkCore;

namespace Hermes.Vector;

public class SearchQueryService
{
    private readonly HermesDbContext _dbContext;
    private readonly EmbeddingService _embeddingService;

    public SearchQueryService(HermesDbContext dbContext, EmbeddingService embeddingService)
    {
        _dbContext = dbContext;
        _embeddingService = embeddingService;
    }

    public async Task<List<InvoiceEntity>> SearchInvoicesAsync(string query, int topK = 5)
    {
        // 1. Gerar o embedding da Query em linguagem natural
        var queryVectorArray = await _embeddingService.GenerateEmbeddingsAsync(query);
        
        if (queryVectorArray == null || queryVectorArray.Length == 0)
        {
            return new List<InvoiceEntity>();
        }

        var queryVector = new Pgvector.Vector(queryVectorArray);

        // 2. Procurar na BD usando Cosine Distance (vetores com menor distância são mais similares)
        var results = await _dbContext.Invoices
            .Where(i => i.Embedding != null)
            .OrderBy(i => i.Embedding!.CosineDistance(queryVector))
            .Take(topK)
            .ToListAsync();

        return results;
    }
}
