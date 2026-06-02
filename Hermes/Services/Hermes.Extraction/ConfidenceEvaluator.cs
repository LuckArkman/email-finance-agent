using Microsoft.Extensions.Logging;

namespace Hermes.Extraction;

public class ConfidenceEvaluator
{
    private readonly ILogger<ConfidenceEvaluator> _logger;
    private readonly HeuristicMatcher _matcher;

    private const float MinimumOcrConfidenceThreshold = 0.90f; // 90%

    public ConfidenceEvaluator(ILogger<ConfidenceEvaluator> logger, HeuristicMatcher matcher)
    {
        _logger = logger;
        _matcher = matcher;
    }

    public bool Evaluate(float ocrConfidence, InvoiceExtractionModel extractedModel, string rawText)
    {
        bool requiresReview = false;

        // 1. Ocr Confidence
        if (ocrConfidence < MinimumOcrConfidenceThreshold)
        {
            _logger.LogWarning($"[CONFIDENCE WARNING] OCR Mean Confidence ({ocrConfidence:P2}) is below threshold ({MinimumOcrConfidenceThreshold:P2}). Flagging for review.");
            requiresReview = true;
        }

        // 2. Heuristics (Ex: NIF Matching)
        bool nifMatches = _matcher.DoesNifMatchRawText(extractedModel.Nif, rawText);
        if (!nifMatches)
        {
            _logger.LogWarning($"[HEURISTIC WARNING] Extracted NIF/CNPJ '{extractedModel.Nif}' was not clearly found in the OCR RawText. Possible hallucination. Flagging for review.");
            requiresReview = true;
        }

        if (!requiresReview)
        {
            _logger.LogInformation("Confidence Evaluator: Passed all checks. (Green light)");
        }

        return requiresReview;
    }
}
