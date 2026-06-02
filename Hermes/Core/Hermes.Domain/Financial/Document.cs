using System;
using Hermes.Domain.Common;

namespace Hermes.Domain.Financial;

public class Document : BaseEntity
{
    public string OriginalFileName { get; private set; }
    public string S3Key { get; private set; }
    public long SizeInBytes { get; private set; }
    public string MimeType { get; private set; }
    public string StorageProvider { get; private set; } // e.g. "AWS_S3" or "MinIO"
    public string SourceMessageId { get; private set; }

    // Relação opcional de 1 para 1 com uma Fatura gerada a partir deste documento
    public Guid? InvoiceId { get; private set; }
    public Invoice? Invoice { get; private set; }

    protected Document() { } // EF Core

    public Document(string originalFileName, string s3Key, long sizeInBytes, string mimeType, string storageProvider, string sourceMessageId, Guid tenantId)
    {
        OriginalFileName = originalFileName;
        S3Key = s3Key;
        SizeInBytes = sizeInBytes;
        MimeType = mimeType;
        StorageProvider = storageProvider;
        SourceMessageId = sourceMessageId;
        TenantId = tenantId;
    }

    public void LinkToInvoice(Guid invoiceId)
    {
        InvoiceId = invoiceId;
    }
}
