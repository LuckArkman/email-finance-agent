using Hermes.Vector;
using MassTransit;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddDbContext<HermesDbContext>(options =>
{
    var connectionString = builder.Configuration["Database:ConnectionString"] 
        ?? "Host=localhost;Database=hermes_db;Username=postgres;Password=postgres";
        
    options.UseNpgsql(connectionString, o => 
    {
        o.UseVector(); // Extensão do pgvector
    });
});

builder.Services.AddHttpClient<EmbeddingService>(client =>
{
    client.BaseAddress = new System.Uri(builder.Configuration["Ollama:BaseUrl"] ?? "http://localhost:11434");
});

builder.Services.AddScoped<SearchQueryService>();

builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<VectorJobConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration["RabbitMQ:Host"] ?? "localhost", "/", h =>
        {
            h.Username(builder.Configuration["RabbitMQ:Username"] ?? "guest");
            h.Password(builder.Configuration["RabbitMQ:Password"] ?? "guest");
        });

        cfg.ReceiveEndpoint("vector-job-queue", e =>
        {
            e.ConfigureConsumer<VectorJobConsumer>(context);
        });
    });
});

var app = builder.Build();

app.UseRouting();
app.MapControllers();

app.Run();
