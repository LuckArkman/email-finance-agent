using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MassTransit;

namespace Hermes.OCR;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = Host.CreateApplicationBuilder(args);

        builder.Services.AddSingleton<S3OcrClient>();
        builder.Services.AddSingleton<ImageEnhancementPipeline>();
        builder.Services.AddSingleton<DeskewProcessor>();
        builder.Services.AddSingleton<TesseractOcrEngine>();
        builder.Services.AddSingleton<PdfTextExtractor>();
        builder.Services.AddSingleton<DigitalPdfStrategy>();

        // Registar o Dispatcher como Singleton E como HostedService
        // O AddHostedService<T> aceita instâncias criadas na DI, ou podemos usar factory
        builder.Services.AddSingleton<JobDispatcher>();
        builder.Services.AddHostedService(provider => provider.GetRequiredService<JobDispatcher>());

        // Configuração do MassTransit
        builder.Services.AddMassTransit(x =>
        {
            x.AddConsumer<OcrJobConsumer>();

            x.UsingRabbitMq((context, cfg) =>
            {
                // TODO: Configurar URI de ligação real (RabbitMQ) vindo de config,
                // Usando localhost por default em ambiente de dev
                cfg.Host("localhost", "/", h => {
                    h.Username("guest");
                    h.Password("guest");
                });

                cfg.ReceiveEndpoint("ocr-job-queue", e =>
                {
                    e.ConfigureConsumer<OcrJobConsumer>(context);
                });
            });
        });

        var host = builder.Build();
        host.Run();
    }
}
