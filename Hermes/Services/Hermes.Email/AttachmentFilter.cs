using System;
using MimeKit;

namespace Hermes.Email;

public class AttachmentFilter
{
    private const long ImageSizeThreshold = 10 * 1024; // 10 KB

    public bool IsValidAttachment(MimePart attachment)
    {
        if (attachment == null) return false;

        var mimeType = attachment.ContentType.MimeType.ToLowerInvariant();
        var size = attachment.Content?.Stream?.Length ?? 0;

        // Sempre aceitar PDFs e XMLs, independentemente do tamanho (faturas eletrónicas ou recibos de texto simples)
        if (mimeType == "application/pdf" || mimeType == "application/xml" || mimeType == "text/xml")
        {
            return true;
        }

        // Se for imagem, filtrar assinaturas e ícones minúsculos (Magic Bytes Heuristics)
        if (mimeType.StartsWith("image/"))
        {
            return size >= ImageSizeThreshold;
        }

        // Outros documentos genéricos (ex: Word, Excel) são aceites, embora possamos afinar esta heurística mais tarde
        if (mimeType.StartsWith("application/"))
        {
            return true;
        }

        // Ficheiros não identificados ou texto solto podem ser lixo
        return false;
    }
}
