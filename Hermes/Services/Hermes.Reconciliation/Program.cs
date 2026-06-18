using Hermes.Reconciliation;
using MassTransit;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddDbContext<ReconciliationDbContext>(options =>
{
    var connectionString = builder.Configuration["Database:ConnectionString"] 
        ?? "Host=localhost;Database=hermes_db;Username=postgres;Password=postgres";
    options.UseNpgsql(connectionString);
});

builder.Services.AddScoped<ToleranceMatcher>();
builder.Services.AddScoped<ReconciliationEngine>();

builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<InvoiceReadyConsumer>();
    x.AddConsumer<ReceiptReadyConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration["RabbitMQ:Host"] ?? "localhost", "/", h =>
        {
            h.Username(builder.Configuration["RabbitMQ:Username"] ?? "guest");
            h.Password(builder.Configuration["RabbitMQ:Password"] ?? "guest");
        });

        cfg.ReceiveEndpoint("reconciliation-invoices", e =>
        {
            e.ConfigureConsumer<InvoiceReadyConsumer>(context);
        });

        cfg.ReceiveEndpoint("reconciliation-receipts", e =>
        {
            e.ConfigureConsumer<ReceiptReadyConsumer>(context);
        });
    });
});

var host = builder.Build();
host.Run();
