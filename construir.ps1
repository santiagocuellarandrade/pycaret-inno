# Construye la app en Windows: ejecutable (PyInstaller) -> instalador (Inno Setup).
#
# Antes: ejecuta el cuaderno notebooks\entrenamiento_pycaret.ipynb para exportar el modelo.
#
# Uso (PowerShell, desde la raíz del proyecto):
#     powershell -ExecutionPolicy Bypass -File construir.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "modelo\modelo_iris.pkl")) {
    Write-Host "Falta modelo\modelo_iris.pkl: ejecuta primero el cuaderno notebooks\entrenamiento_pycaret.ipynb" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "assets\icono.ico")) {
    Write-Host "Falta assets\icono.ico (lo necesitan el .exe y el instalador)." -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/2] Creando el ejecutable con PyInstaller..." -ForegroundColor Cyan
uv run pyinstaller ClasificadorDesertor.spec --noconfirm
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n[2/2] Creando el instalador con Inno Setup..." -ForegroundColor Cyan
$iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    Write-Host "No encontré Inno Setup 6. Instálalo desde https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "o abre instalador\ClasificadorDesertor.iss y presiona Compile." -ForegroundColor Yellow
    exit 1
}
& $iscc "instalador\ClasificadorDesertor.iss"
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`nListo: instalador\salida\" -ForegroundColor Green
