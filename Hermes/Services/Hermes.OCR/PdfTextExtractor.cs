using System;
using System.Text;
using Microsoft.Extensions.Logging;
using UglyToad.PdfPig;
using UglyToad.PdfPig.DocumentLayoutAnalysis.TextExtractor;

namespace Hermes.OCR;

public class PdfTextExtractor
{
    private readonly ILogger<PdfTextExtractor> _logger;

    public PdfTextExtractor(ILogger<PdfTextExtractor> logger)
    {
        _logger = logger;
    }

    public string ExtractText(string pdfPath)
    {
        _logger.LogInformation($"Tentando extrair texto nativo de {pdfPath} usando PdfPig.");
        
        var sb = new StringBuilder();
        try
        {
            using var document = PdfDocument.Open(pdfPath);
            foreach (var page in document.GetPages())
            {
                var text = ContentOrderTextExtractor.GetText(page);
                sb.AppendLine(text);
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, $"Aviso: Falha ao ler o PDF {pdfPath}. Pode estar corrompido ou encriptado.");
        }

        return sb.ToString().Trim();
    }
}
