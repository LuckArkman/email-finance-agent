using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using System.Threading.Tasks;

namespace Hermes.OCR;

public class DeskewProcessor
{
    public async Task ApplyDeskewAsync(string sourcePath, string destinationPath)
    {
        using var image = await Image.LoadAsync(sourcePath);

        // Stub/Mock: Em ambiente produtivo, seria necessário extrair as Hough Lines para determinar o "skewAngle".
        // Para a migração, mantemos o esqueleto da rotação via ImageSharp, que aplica o Rotate com interpolação bicúbica
        float estimatedSkewAngle = 0.0f; // Ex: 1.5f graus

        if (estimatedSkewAngle != 0.0f)
        {
            image.Mutate(x => x.Rotate(estimatedSkewAngle, KnownResamplers.Bicubic));
        }

        await image.SaveAsPngAsync(destinationPath);
    }
}
