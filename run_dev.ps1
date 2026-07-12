# SQX Edge Pro - Desarrollo local
# Ejecutar desde la raíz del repositorio.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "No se encontró '$Name' en PATH. Instálalo y vuelve a ejecutar el script."
    }
}

Require-Command "python"
Require-Command "node"
Require-Command "npm"

$pythonVersion = (& python --version 2>&1)
$nodeVersion = (& node --version 2>&1)
Write-Host "Python: $pythonVersion"
Write-Host "Node:   $nodeVersion"

$venvPath = Join-Path $ProjectRoot "backend\.venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual Python..."
    & python -m venv $venvPath
}

Write-Host "Instalando dependencias Python..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e $ProjectRoot

if (-not (Test-Path (Join-Path $ProjectRoot "node_modules"))) {
    Write-Host "Instalando dependencias Electron..."
    & npm install
}

$env:PATH = "$(Join-Path $venvPath 'Scripts');$env:PATH"
Write-Host "Iniciando SQX Edge Pro..."
& npm run dev
