using Microsoft.Extensions.Logging;

namespace Hermes.OCR;

public class DigitalPdfStrategy
{
    private readonly PdfTextExtractor _extractor;
    private readonly ILogger<DigitalPdfStrategy> _logger;

    // Threshold heurístico: se extrairmos mais de 100 caracteres, é um Digital PDF
    private const int DigitalTextThreshold = 100;

    public DigitalPdfStrategy(PdfTextExtractor extractor, ILogger<DigitalPdfStrategy> logger)
    {
        _extractor = extractor;
        _logger = logger;
    }

    /// <summary>
    /// Tenta extrair texto do ficheiro. Retorna true se for um PDF nativo/digital com texto legível suficiente.
    /// </summary>
    public bool TryBypassOcr(string localFilePath, string originalFileName, out string extractedText)
    {
        extractedText = string.Empty;

        // 1. Verificar se a extensão é PDF (case-insensitive)
        if (!originalFileName.EndsWith(".pdf", System.StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }

        // 2. Extrair o texto bruto usando PdfPig
        var rawText = _extractor.ExtractText(localFilePath);

        // 3. Aplicar a Heurística
        if (rawText.Length > DigitalTextThreshold)
        {
            _logger.LogInformation($"[BYPASS OCR] Ficheiro {originalFileName} é um Digital PDF nativo. ({rawText.Length} caracteres extraídos).");
            extractedText = rawText;
            return true;
        }

        _logger.LogInformation($"Ficheiro {originalFileName} é PDF mas não parece nativo (apenas {rawText.Length} chars). Reencaminhando para o Tesseract...");
        return false;
    }
}
