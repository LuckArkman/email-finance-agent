using System.Text.RegularExpressions;

namespace Hermes.Extraction;

public class HeuristicMatcher
{
    public bool DoesNifMatchRawText(string extractedNif, string rawText)
    {
        if (string.IsNullOrWhiteSpace(extractedNif) || string.IsNullOrWhiteSpace(rawText))
        {
            return false;
        }

        // Removemos espaços ou formatação extra (pontos, hífens) do NIF extraído
        var cleanExtractedNif = Regex.Replace(extractedNif, @"[^\d]", "");
        
        // Removemos espaços e formatações parecidas no RawText inteiro
        var cleanRawText = Regex.Replace(rawText, @"[^\d]", "");

        // Se o NIF extraído ainda tiver caracteres (ex: NIF válido) e estiver contido nos dígitos puros do OCR
        if (cleanExtractedNif.Length >= 5 && cleanRawText.Contains(cleanExtractedNif))
        {
            return true;
        }

        return false;
    }
}
