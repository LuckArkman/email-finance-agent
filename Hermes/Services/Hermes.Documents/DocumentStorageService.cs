using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Hermes.EventBus;
using Hermes.Infrastructure.Data;
using Hermes.Domain.Financial;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace Hermes.Documents;

public class DocumentStorageService : BackgroundService
{
    private readonly ILogger<DocumentStorageService> _logger;
    private readonly S3BlobClient _s3Client;
    private readonly IServiceProvider _serviceProvider;

    public DocumentStorageService(ILogger<DocumentStorageService> logger, S3BlobClient s3Client, IServiceProvider serviceProvider)
    {
        _logger = logger;
        _s3Client = s3Client;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("DocumentStorageService is starting.");

        // Simulação do EventBus Listener para o Evento "AttachmentExtractedEvent"
        // TODO: Mapear via MassTransit Consumer. Aqui simulamos o processamento abstrato.
        
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(1000, stoppingToken);
        }
    }

    // Método que será chamado pelo consumidor real (MassTransit IConsumer) quando receber a mensagem
    public async Task ProcessExtractedAttachmentAsync(AttachmentExtractedEvent evt, CancellationToken cancellationToken)
    {
        _logger.LogInformation($"Receiving Extracted Attachment: {evt.FileName} (from message {evt.MessageId})");

        var dateFolder = DateTime.UtcNow.ToString("yyyy/MM/dd");
        var s3Key = $"invoices/{dateFolder}/{evt.MessageId}/{evt.FileName}";

        try
        {
            // Upload to S3/MinIO
            await _s3Client.UploadFileAsync(evt.StoragePath, s3Key, evt.MimeType, cancellationToken);

            // Gravar Entity de Base de Dados
            using (var scope = _serviceProvider.CreateScope())
            {
                var dbContext = scope.ServiceProvider.GetRequiredService<HermesDbContext>();
                
                // Em cenário real o TenantId vem no Header/Message; assumimos Guid default para simplificar.
                var tenantId = Guid.Parse("00000000-0000-0000-0000-000000000001");
                
                var document = new Document(
                    evt.FileName, 
                    s3Key, 
                    evt.SizeInBytes, 
                    evt.MimeType, 
                    _s3Client.StorageProviderName, 
                    evt.MessageId, 
                    tenantId);
                
                dbContext.Set<Document>().Add(document);
                await dbContext.SaveChangesAsync(cancellationToken);
                
                _logger.LogInformation($"Document Entity saved to DB with Id: {document.Id}");

                // TODO: Publicar DocumentStoredEvent
                // var storedEvent = new DocumentStoredEvent(evt.MessageId, document.Id, evt.FileName, s3Key, evt.SizeInBytes, evt.MimeType, document.StorageProvider);
                // _eventBus.Publish(storedEvent);
            }

            // Limpar ficheiro local após upload
            if (File.Exists(evt.StoragePath))
            {
                File.Delete(evt.StoragePath);
                _logger.LogInformation($"Deleted temporary local file {evt.StoragePath}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to process attachment {evt.FileName}");
        }
    }
}
