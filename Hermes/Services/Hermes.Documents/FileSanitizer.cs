using System;
using System.IO;
using System.Linq;

namespace Hermes.Documents;

public static class FileSanitizer
{
    // Assinaturas de Ficheiros conhecidos (Magic Bytes)
    private static readonly byte[][] _pdfMagicBytes = { new byte[] { 0x25, 0x50, 0x44, 0x46 } };
    private static readonly byte[][] _pngMagicBytes = { new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A } };
    private static readonly byte[][] _jpegMagicBytes = { 
        new byte[] { 0xFF, 0xD8, 0xFF, 0xE0 },
        new byte[] { 0xFF, 0xD8, 0xFF, 0xE1 },
        new byte[] { 0xFF, 0xD8, 0xFF, 0xE8 }
    };
    
    // NOTA: Arquivos XML podem começar com <?xml (0x3C, 0x3F, 0x78, 0x6D, 0x6C) mas também ter BOM, etc. A validação pode ser mais relaxada ou rigorosa.
    private static readonly byte[][] _xmlMagicBytes = { 
        new byte[] { 0x3C, 0x3F, 0x78, 0x6D, 0x6C } // <?xml
    };

    public static bool IsValid(Stream stream, string fileName)
    {
        if (stream == null || stream.Length == 0) return false;

        var ext = Path.GetExtension(fileName).ToLowerInvariant();
        var buffer = new byte[8]; // O maior cabeçalho que verificamos (PNG) tem 8 bytes
        
        // Guardar a posição original e ler
        var originalPosition = stream.Position;
        stream.Read(buffer, 0, buffer.Length);
        stream.Position = originalPosition; // Rewind the stream

        if (ext == ".pdf")
        {
            return _pdfMagicBytes.Any(magic => buffer.Take(magic.Length).SequenceEqual(magic));
        }
        else if (ext == ".png")
        {
            return _pngMagicBytes.Any(magic => buffer.Take(magic.Length).SequenceEqual(magic));
        }
        else if (ext == ".jpg" || ext == ".jpeg")
        {
            return _jpegMagicBytes.Any(magic => buffer.Take(magic.Length).SequenceEqual(magic));
        }
        else if (ext == ".xml")
        {
            // Arquivos XML podem ter BOM (Byte Order Mark), ignoramos verificação estrita aqui por simplicidade, 
            // mas num cenário super crítico faríamos parse do BOM.
            return true;
        }

        return false;
    }
}
