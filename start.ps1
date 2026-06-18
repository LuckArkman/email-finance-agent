param (
    [switch]$ForceGPU,
    [switch]$ForceCPU
)

Write-Host "Inicializando o Hermes Agent Ecosystem..." -ForegroundColor Cyan

# Verifica a presenca da placa NVIDIA via nvidia-smi
$hasGpu = $false
if ($ForceGPU) {
    $hasGpu = $true
} elseif ($ForceCPU) {
    $hasGpu = $false
} else {
    try {
        $nvidiaSmi = Get-Command "nvidia-smi" -ErrorAction SilentlyContinue
        if ($nvidiaSmi) {
            $output = nvidia-smi 2>&1
            if ($LASTEXITCODE -eq 0) {
                $hasGpu = $true
            }
        }
    } catch {
        $hasGpu = $false
    }
}

$overrideFile = "docker-compose.override.yml"

if ($hasGpu) {
    Write-Host "Placa NVIDIA detectada! Ativando aceleracao via CUDA (GPU)." -ForegroundColor Green
    $overrideContent = @"
services:
  qwen-engine:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
"@
    Set-Content -Path $overrideFile -Value $overrideContent
} else {
    Write-Host "Nenhuma placa NVIDIA detectada. O sistema rodara em modo CPU." -ForegroundColor Yellow
    if (Test-Path $overrideFile) {
        Remove-Item $overrideFile -Force
    }
}

Write-Host "Subindo os containers do Docker Compose..." -ForegroundColor Cyan
docker compose up -d

Write-Host "Verificacao de GPU e inicializacao concluidas com sucesso!" -ForegroundColor Green
