using Hermes.Analytics;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using System.Data;
using Npgsql;

using Hermes.Analytics.Consumers;
using MassTransit;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

var connectionString = builder.Configuration["Database:ConnectionString"] 
    ?? "Host=localhost;Database=hermes_db;Username=postgres;Password=postgres";

// Caching Configurations
builder.Services.AddDistributedMemoryCache(); // Fallback
// builder.Services.AddStackExchangeRedisCache(options => { options.Configuration = "localhost:6379"; });
builder.Services.AddScoped<Hermes.Analytics.RedisCacheService>();

// MassTransit setup for cache invalidation
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<CacheInvalidatorConsumer>();
    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration["RabbitMQ:Host"] ?? "localhost", "/", h =>
        {
            h.Username(builder.Configuration["RabbitMQ:Username"] ?? "guest");
            h.Password(builder.Configuration["RabbitMQ:Password"] ?? "guest");
        });
        cfg.ConfigureEndpoints(context);
    });
});

builder.Services.AddDbContext<AnalyticsDbContext>(options =>
{
    options.UseNpgsql(connectionString);
});

builder.Services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
builder.Services.AddScoped<DashboardKpisService>();

var app = builder.Build();

app.UseRouting();
app.MapControllers();

app.Run();
