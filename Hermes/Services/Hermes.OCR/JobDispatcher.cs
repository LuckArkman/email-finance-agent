using System;
using System.IO;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Hermes.EventBus;

using MassTransit;

namespace Hermes.OCR;

public record OcrJobContext(DocumentStoredEvent EventData);

public class JobDispatcher : BackgroundService
{
    private readonly Channel<OcrJobContext> _channel;
    private readonly ILogger<JobDispatcher> _logger;
    private readonly S3OcrClient _s3Client;
    private readonly ImageEnhancementPipeline _enhancer;
    private readonly DeskewProcessor _deskewer;
    private readonly TesseractOcrEngine _ocrEngine;
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly DigitalPdfStrategy _pdfStrategy;

    public JobDispatcher(
        ILogger<JobDispatcher> logger, 
        S3OcrClient s3Client,
        ImageEnhancementPipeline enhancer,
        DeskewProcessor deskewer,
        TesseractOcrEngine ocrEngine,
        IPublishEndpoint publishEndpoint,
        DigitalPdfStrategy pdfStrategy)
    {
        _logger = logger;
        _s3Client = s3Client;
        _enhancer = enhancer;
        _deskewer = deskewer;
        _ocrEngine = ocrEngine;
        _publishEndpoint = publishEndpoint;
        _pdfStrategy = pdfStrategy;

        _channel = Channel.CreateBounded<OcrJobContext>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.Wait
        });
    }

    public async ValueTask EnqueueJobAsync(OcrJobContext jobContext, CancellationToken cancellationToken)
    {
        await _channel.Writer.WriteAsync(jobContext, cancellationToken);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("JobDispatcher is starting.");

        var options = new ParallelOptions
        {
            MaxDegreeOfParallelism = 4,
            CancellationToken = stoppingToken
        };

        try
        {
            await Parallel.ForEachAsync(_channel.Reader.ReadAllAsync(stoppingToken), options, async (job, token) =>
            {
                await ProcessJobAsync(job, token);
            });
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("JobDispatcher is stopping.");
        }
    }

    private async Task ProcessJobAsync(OcrJobContext job, CancellationToken token)
    {
        _logger.LogInformation($"Starting OCR processing for Document {job.EventData.DocumentId} (Tenant: {job.EventData.TenantId})");
        
        var evt = job.EventData;
        var tempFolder = Path.Combine(Path.GetTempPath(), "hermes_ocr", evt.DocumentId.ToString());
        Directory.CreateDirectory(tempFolder);

        var localRawPath = Path.Combine(tempFolder, "raw_" + evt.OriginalFileName);
        var enhancedPath = Path.Combine(tempFolder, "enhanced.png");
        var deskewedPath = Path.Combine(tempFolder, "deskewed.png");

        try
        {
            // 1. Descarregar o documento base do S3
            await _s3Client.DownloadFileAsync(evt.S3Key, localRawPath, token);

            // Novo passo: 1.5. Estratégia de Bypass (Digital PDFs)
            if (_pdfStrategy.TryBypassOcr(localRawPath, evt.OriginalFileName, out var nativeText))
            {
                // Dispara o evento e aborta todo o fluxo visual (poupança massiva de CPU)
                var bypassEvent = new OcrCompletedEvent(evt.DocumentId, evt.TenantId, nativeText, 1.0f, DateTime.UtcNow);
                await _publishEndpoint.Publish(bypassEvent, token);
                
                _logger.LogInformation($"Successfully bypassed OCR for Document {evt.DocumentId} using PdfPig.");
                return; // <-- Saída imediata da função!
            }

            // 2. Realce de Imagem (Grayscale + Thresholding)
            await _enhancer.EnhanceImageAsync(localRawPath, enhancedPath);

            // 3. Deskew (Endireitar a fatura)
            await _deskewer.ApplyDeskewAsync(enhancedPath, deskewedPath);

            // 4. Upload da versão otimizada de volta para o S3
            var enhancedS3Key = evt.S3Key.Replace(Path.GetFileName(evt.S3Key), "optimized.png");
            await _s3Client.UploadFileAsync(deskewedPath, enhancedS3Key, "image/png", token);
            
            _logger.LogInformation($"Successfully optimized Document {evt.DocumentId}. New S3 Key: {enhancedS3Key}");

            // 5. Tesseract OCR (Processar a imagem optimizada em disco)
            var ocrResult = await _ocrEngine.ProcessImageAsync(deskewedPath);

            // 6. Publicar evento final da Sprint 18
            var completedEvent = new OcrCompletedEvent(
                evt.DocumentId,
                evt.TenantId,
                ocrResult.RawText,
                ocrResult.Confidence,
                DateTime.UtcNow
            );

            await _publishEndpoint.Publish(completedEvent, token);
            _logger.LogInformation($"Dispatched OcrCompletedEvent for Document {evt.DocumentId}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed OCR processing for Document {job.EventData.DocumentId}");
        }
        finally
        {
            // Limpeza
            if (Directory.Exists(tempFolder))
            {
                Directory.Delete(tempFolder, true);
            }
        }
    }
}
