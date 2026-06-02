using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using MimeKit;
using Microsoft.Extensions.Logging;

namespace Hermes.Email;

public class MimeMessageParser
{
    private readonly ILogger<MimeMessageParser> _logger;
    private readonly AttachmentFilter _attachmentFilter;

    public MimeMessageParser(ILogger<MimeMessageParser> logger, AttachmentFilter attachmentFilter)
    {
        _logger = logger;
        _attachmentFilter = attachmentFilter;
    }

    public async Task ParseAndExtractAsync(Stream emlStream, string messageId, CancellationToken cancellationToken)
    {
        try
        {
            var message = await MimeMessage.LoadAsync(emlStream, cancellationToken);
            _logger.LogInformation($"Parsing email: {message.Subject} (MessageId: {messageId})");

            var attachments = new List<MimePart>();

            // Iterar sobre todas as partes do email
            foreach (var bodyPart in message.BodyParts)
            {
                if (bodyPart is MimePart mimePart && mimePart.IsAttachment)
                {
                    attachments.Add(mimePart);
                }
                else if (bodyPart is MimePart inlinePart && !string.IsNullOrEmpty(inlinePart.FileName))
                {
                    // Tratar ficheiros inline com nomes como anexos também (ex: imagens ou PDFs arrastados)
                    attachments.Add(inlinePart);
                }
            }

            foreach (var attachment in attachments)
            {
                if (_attachmentFilter.IsValidAttachment(attachment))
                {
                    _logger.LogInformation($"Attachment Validated: {attachment.FileName} ({attachment.ContentType.MimeType})");

                    var safeName = string.Concat(attachment.FileName.Split(Path.GetInvalidFileNameChars()));
                    var tempPath = Path.Combine(Path.GetTempPath(), $"{messageId}_{safeName}");

                    using (var stream = File.Create(tempPath))
                    {
                        if (attachment.Content != null)
                        {
                            await attachment.Content.DecodeToAsync(stream, cancellationToken);
                        }
                    }

                    var fileInfo = new FileInfo(tempPath);
                    
                    // TODO: Publicar AttachmentExtractedEvent(messageId, safeName, attachment.ContentType.MimeType, fileInfo.Length, tempPath)
                }
                else
                {
                    _logger.LogDebug($"Attachment Discarded: {attachment.FileName} ({attachment.ContentType.MimeType})");
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to parse EML stream for MessageId: {messageId}");
        }
    }
}
