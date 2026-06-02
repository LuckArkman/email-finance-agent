using System.Threading.Tasks;

namespace Hermes.Extraction;

public interface ILLMClient
{
    Task<string> ExtractSemanticDataAsync(string prompt, string rawText);
}
