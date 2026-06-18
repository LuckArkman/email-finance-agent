$ErrorActionPreference = "Stop"

Write-Host "=== TESTE: WhatsApp Image Routing (Pipeline OCR) ==="
try {
    $tempFile = "$env:TEMP\fatura_whatsapp_teste.pdf"
    "Dummy PDF Content" | Out-File $tempFile -Encoding ascii

    # Create multipart form data using standard powershell features or .NET classes
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($tempFile)
    
    $bodyBytes = [System.Collections.Generic.List[byte]]::new()
    
    # 1. Source field
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("--$boundary`r`n"))
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("Content-Disposition: form-data; name=`"source`"`r`n`r`nwhatsapp`r`n"))
    
    # 2. Sender field
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("--$boundary`r`n"))
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("Content-Disposition: form-data; name=`"sender`"`r`n`r`n351912345678`r`n"))
    
    # 3. File
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("--$boundary`r`n"))
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("Content-Disposition: form-data; name=`"file`"; filename=`"fatura_whatsapp_teste.pdf`"`r`n"))
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("Content-Type: application/pdf`r`n`r`n"))
    $bodyBytes.AddRange($fileBytes)
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("`r`n"))
    
    # End boundary
    $bodyBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes("--$boundary--`r`n"))

    $request = [System.Net.HttpWebRequest]::Create("http://localhost:5000/api/hermes/documents/upload")
    $request.Method = "POST"
    $request.ContentType = "multipart/form-data; boundary=$boundary"
    
    $stream = $request.GetRequestStream()
    $stream.Write($bodyBytes.ToArray(), 0, $bodyBytes.Count)
    $stream.Close()
    
    $response = $request.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    $responseString = $reader.ReadToEnd()
    $reader.Close()
    
    Write-Host "Resposta do Servidor: " $responseString
} catch {
    Write-Host "WhatsApp Image Upload Error: $_"
}
