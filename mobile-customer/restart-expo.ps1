# Script para reiniciar Expo correctamente
# Ejecutar desde: c:\Users\godoy\Desktop\quickgo\mobile-customer

Write-Host "🔄 Reiniciando Expo..." -ForegroundColor Cyan

# 1. Detener procesos de Expo
Write-Host "`n1️⃣ Deteniendo procesos de Expo..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*expo*"} | Stop-Process -Force
Start-Sleep -Seconds 2

# 2. Limpiar caché
Write-Host "`n2️⃣ Limpiando caché..." -ForegroundColor Yellow
if (Test-Path ".expo") {
    Remove-Item -Recurse -Force ".expo"
    Write-Host "✅ Caché .expo eliminada" -ForegroundColor Green
}

# 3. Verificar que el backend esté corriendo
Write-Host "`n3️⃣ Verificando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/restaurants/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend respondiendo correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend no responde. Asegúrate de que Docker esté corriendo:" -ForegroundColor Red
    Write-Host "   cd .." -ForegroundColor Gray
    Write-Host "   docker-compose up -d" -ForegroundColor Gray
    exit 1
}

# 4. Verificar configuración de API
Write-Host "`n4️⃣ Verificando configuración..." -ForegroundColor Yellow
$apiConfig = Get-Content "src\api\index.ts" | Select-String "const API_URL"
Write-Host "   $apiConfig" -ForegroundColor Gray

# 5. Iniciar Expo
Write-Host "`n5️⃣ Iniciando Expo..." -ForegroundColor Yellow
Write-Host "   Presiona 'w' para abrir en navegador" -ForegroundColor Cyan
Write-Host "   Presiona 'r' para recargar" -ForegroundColor Cyan
Write-Host ""
npx expo start --clear

