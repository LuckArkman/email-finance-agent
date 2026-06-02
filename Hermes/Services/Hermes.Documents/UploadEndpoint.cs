using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Hermes.Infrastructure.Data;
using Hermes.Domain.Financial;
using Hermes.Domain.Tenancy;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Builder;

namespace Hermes.Documents;

public static class UploadEndpoint
{
    public static void MapUploadEndpoints(this Microsoft.AspNetCore.Routing.IEndpointRouteBuilder routes)
    {
        routes.MapPost("/api/hermes/documents/upload", async (
            HttpContext context,
            IFormFile file,
            [FromServices] S3BlobClient s3Client,
            [FromServices] HermesDbContext dbContext,
            [FromServices] ITenantProvider tenantProvider,
            ILogger<Program> logger) =>
        {
            if (file == null || file.Length == 0)
            {
                return Results.BadRequest("No file uploaded.");
            }

            using var stream = file.OpenReadStream();

            if (!FileSanitizer.IsValid(stream, file.FileName))
            {
                logger.LogWarning($"Blocked invalid file upload attempt: {file.FileName}");
                return Results.BadRequest("File format is invalid or corrupted. Only PDF, PNG, JPG, and XML are allowed.");
            }

            // Extract TenantId (em ambiente real o ITenantProvider trataria dos claims no HTTP Context, 
            // mas podemos ler de headers forçados pelo gateway para garantir)
            var tenantId = tenantProvider.GetCurrentTenant().TenantId;
            if (context.Request.Headers.TryGetValue("X-Tenant-Id", out var headerVal) && Guid.TryParse(headerVal, out var tid))
            {
                tenantId = tid;
            }

            var messageId = $"MANUAL_{Guid.NewGuid()}";
            var safeName = string.Concat(file.FileName.Split(Path.GetInvalidFileNameChars()));
            var dateFolder = DateTime.UtcNow.ToString("yyyy/MM/dd");
            var s3Key = $"invoices/{dateFolder}/{messageId}/{safeName}";

            try
            {
                var tempPath = Path.Combine(Path.GetTempPath(), safeName);
                
                // Gravar temporariamente para fazer upload S3 (poderíamos usar direto a stream mas o S3 BlobClient já recebe path)
                using (var tempStream = File.Create(tempPath))
                {
                    stream.Position = 0; // Rewind
                    await stream.CopyToAsync(tempStream);
                }

                await s3Client.UploadFileAsync(tempPath, s3Key, file.ContentType);

                var document = new Document(
                    safeName, 
                    s3Key, 
                    file.Length, 
                    file.ContentType, 
                    s3Client.StorageProviderName, 
                    messageId, 
                    tenantId);

                dbContext.Set<Document>().Add(document);
                await dbContext.SaveChangesAsync();

                // TODO: Publicar DocumentStoredEvent para o MassTransit

                if (File.Exists(tempPath))
                {
                    File.Delete(tempPath);
                }

                return Results.Created($"/api/hermes/documents/{document.Id}", new { DocumentId = document.Id });
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Failed to upload manual document.");
                return Results.StatusCode(StatusCodes.Status500InternalServerError);
            }
        }).DisableAntiforgery(); // Disable AntiForgery for API upload endpoints
    }
}
