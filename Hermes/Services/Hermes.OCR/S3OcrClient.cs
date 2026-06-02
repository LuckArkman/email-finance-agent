using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Amazon.S3;
using Amazon.S3.Transfer;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Hermes.OCR;

public class S3OcrClient
{
    private readonly ILogger<S3OcrClient> _logger;
    private readonly AmazonS3Client _s3Client;
    private readonly string _bucketName;

    public S3OcrClient(ILogger<S3OcrClient> logger, IConfiguration configuration)
    {
        _logger = logger;
        _bucketName = configuration["Storage:S3:BucketName"] ?? "hermes-documents";
        
        var accessKey = configuration["Storage:S3:AccessKey"];
        var secretKey = configuration["Storage:S3:SecretKey"];
        var serviceUrl = configuration["Storage:S3:ServiceUrl"]; 
        
        var config = new AmazonS3Config
        {
            UseHttp = serviceUrl?.StartsWith("http://") == true,
            ForcePathStyle = true 
        };

        if (!string.IsNullOrEmpty(serviceUrl))
        {
            config.ServiceURL = serviceUrl;
        }

        _s3Client = new AmazonS3Client(accessKey, secretKey, config);
    }

    public async Task DownloadFileAsync(string objectKey, string destinationPath, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation($"Downloading {_bucketName}/{objectKey} to {destinationPath}");

        try
        {
            using var fileTransferUtility = new TransferUtility(_s3Client);
            await fileTransferUtility.DownloadAsync(destinationPath, _bucketName, objectKey, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error downloading {objectKey} from S3");
            throw;
        }
    }

    public async Task<string> UploadFileAsync(string localFilePath, string objectKey, string mimeType, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation($"Uploading {localFilePath} to {_bucketName}/{objectKey}");

        try
        {
            using var fileTransferUtility = new TransferUtility(_s3Client);
            var uploadRequest = new TransferUtilityUploadRequest
            {
                FilePath = localFilePath,
                Key = objectKey,
                BucketName = _bucketName,
                ContentType = mimeType
            };

            await fileTransferUtility.UploadAsync(uploadRequest, cancellationToken);
            return objectKey;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error uploading {localFilePath} to S3");
            throw;
        }
    }
}
