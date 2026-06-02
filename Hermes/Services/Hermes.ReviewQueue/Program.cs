using Hermes.ReviewQueue;
using MassTransit;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddDbContext<ReviewDbContext>(options =>
{
    var connectionString = builder.Configuration["Database:ConnectionString"] 
        ?? "Host=localhost;Database=hermes_db;Username=postgres;Password=postgres";
    options.UseNpgsql(connectionString);
});

builder.Services.AddScoped<AuditLogService>();

builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<ReviewQueueConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration["RabbitMQ:Host"] ?? "localhost", "/", h =>
        {
            h.Username(builder.Configuration["RabbitMQ:Username"] ?? "guest");
            h.Password(builder.Configuration["RabbitMQ:Password"] ?? "guest");
        });

        cfg.ReceiveEndpoint("review-queue", e =>
        {
            e.ConfigureConsumer<ReviewQueueConsumer>(context);
        });
    });
});

var app = builder.Build();

app.UseRouting();
app.MapControllers();

app.Run();
