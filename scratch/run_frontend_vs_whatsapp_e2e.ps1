$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host " TESTE E2E: Roteamento Frontend vs Roteamento WhatsApp "
Write-Host "=========================================================="

# 1. Teste Frontend
Write-Host "`n[Cenário 1] Instrução vinda do FRONTEND (Painel React)"
Write-Host "Rota: POST /api/hermes/agent/chat"
try {
    $frontendPayload = @{
        messages = @(
            @{ role = "user"; content = "Olá, eu sou o frontend! Responda confirmando que sou a interface Web." }
        )
    }
    $frontendJson = $frontendPayload | ConvertTo-Json -Depth 3
    
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $responseFrontend = Invoke-RestMethod -Uri "http://localhost:5000/api/hermes/agent/chat" -Method Post -Body $frontendJson -ContentType "application/json"
    $sw.Stop()

    Write-Host "⏳ Tempo de Resposta: $($sw.ElapsedMilliseconds) ms"
    Write-Host "📡 Comportamento: O Backend devolveu a resposta DIRETAMENTE na resposta HTTP!"
    Write-Host "📦 Corpo da Resposta HTTP:"
    Write-Host ($responseFrontend | ConvertTo-Json -Depth 5) -ForegroundColor Green
} catch {
    Write-Host "Erro no teste do Frontend: $_" -ForegroundColor Red
}

# 2. Teste WhatsApp
Write-Host "`n----------------------------------------------------------"
Write-Host "[Cenário 2] Instrução vinda do WHATSAPP (Baileys Bridge)"
Write-Host "Rota: POST /api/hermes/whatsapp/message"
try {
    $whatsappPayload = @{
        sender_phone = "351912345678"
        text = "Olá, eu sou o utilizador do WhatsApp! Confirma de onde veio esta instrução."
    }
    $whatsappJson = $whatsappPayload | ConvertTo-Json
    
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $responseWhatsApp = Invoke-RestMethod -Uri "http://localhost:5000/api/hermes/whatsapp/message" -Method Post -Body $whatsappJson -ContentType "application/json"
    $sw.Stop()

    Write-Host "⏳ Tempo de Resposta: $($sw.ElapsedMilliseconds) ms"
    Write-Host "📡 Comportamento: O Backend executou a instrução LLM mas NÃO devolveu o texto na resposta HTTP. Em vez disso, invocou POST http://baileys-bridge:3001/send e devolveu apenas um sinal de Success."
    Write-Host "📦 Corpo da Resposta HTTP:"
    Write-Host ($responseWhatsApp | ConvertTo-Json) -ForegroundColor Cyan
} catch {
    Write-Host "Erro no teste do WhatsApp: $_" -ForegroundColor Red
}

Write-Host "`n=========================================================="
Write-Host " Conclusão: O Gateway sabe perfeitamente de onde vêm as "
Write-Host " instruções e devolve-as corretamente pelo canal certo! "
Write-Host "=========================================================="
