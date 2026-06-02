using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using SixLabors.ImageSharp.PixelFormats;
using System.IO;
using System.Threading.Tasks;

namespace Hermes.OCR;

public class ImageEnhancementPipeline
{
    public async Task EnhanceImageAsync(string sourcePath, string destinationPath)
    {
        // Carrega a imagem nativamente usando ImageSharp 
        // (cross-platform, não precisa de binários OpenCV)
        using var image = await Image.LoadAsync<Rgba32>(sourcePath);

        image.Mutate(x => x
            .Grayscale() // 1. Grayscale para remover ruído de cores (bom para faturas amarrotadas ou fotografadas)
            .BinaryThreshold(0.5f) // 2. Binarização simples para reforçar os contornos das letras a preto e fundo a branco
        );

        // Salvar a imagem processada (png para compressão lossless)
        await image.SaveAsPngAsync(destinationPath);
    }
}
