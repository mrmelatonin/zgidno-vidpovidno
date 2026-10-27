<#
.SYNOPSIS
    Автоматичне встановлення скіла 'zgidno-vidpovidno' для Antigravity.
#>
$ErrorActionPreference = "Stop"

$TargetDir = "$HOME\.gemini\config\skills\zgidno-vidpovidno"
Write-Host "Встановлення скіла 'zgidno-vidpovidno'..." -ForegroundColor Cyan
Write-Host "Цільова папка: $TargetDir" -ForegroundColor DarkGray

if (-not (Test-Path "$HOME\.gemini\config\skills")) {
    New-Item -ItemType Directory -Force -Path "$HOME\.gemini\config\skills" | Out-Null
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    if (Test-Path "$TargetDir\.git") {
        Write-Host "Оновлення існуючого репозиторію через git pull..." -ForegroundColor Yellow
        git -C $TargetDir pull
    } else {
        if (Test-Path $TargetDir) {
            Remove-Item -Recurse -Force $TargetDir
        }
        git clone https://github.com/mrmelatonin/zgidno-vidpovidno.git $TargetDir
    }
} else {
    Write-Host "Git не знайдено, завантаження архіву з GitHub..." -ForegroundColor Yellow
    $ZipPath = "$env:TEMP\zgidno-vidpovidno.zip"
    $ExtractPath = "$env:TEMP\zgidno-extracted"
    Invoke-WebRequest -Uri "https://github.com/mrmelatonin/zgidno-vidpovidno/archive/refs/heads/main.zip" -OutFile $ZipPath
    if (Test-Path $ExtractPath) { Remove-Item -Recurse -Force $ExtractPath }
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
    if (Test-Path $TargetDir) { Remove-Item -Recurse -Force $TargetDir }
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Copy-Item -Recurse -Force "$ExtractPath\zgidno-vidpovidno-main\*" $TargetDir
    Remove-Item -Recurse -Force $ExtractPath, $ZipPath -ErrorAction SilentlyContinue
}

Write-Host "`n[+] Скіл 'zgidno-vidpovidno' успішно встановлено!" -ForegroundColor Green
Write-Host "Тепер він автоматично доступний усім агентам Antigravity на вашому комп'ютері.`n" -ForegroundColor Green
