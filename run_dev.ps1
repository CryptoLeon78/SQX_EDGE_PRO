$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$VenvPath = Join-Path $BackendDir ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "No se encontró '$Name' en PATH. Instálalo y vuelve a ejecutar el script."
    }
}

Require-Command "python"
Require-Command "node"
Require-Command "npm"

Write-Host "Python: $(& python --version 2>&1)"
Write-Host "Node:   $(& node --version 2>&1)"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creando entorno virtual Python..."
    & python -m venv $VenvPath
}

Write-Host "Instalando FastAPI, Uvicorn y Pydantic..."
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install `
    "fastapi>=0.115,<1.0" `
    "uvicorn[standard]>=0.30,<1.0" `
    "pydantic>=2.8,<3.0"

if (-not (Test-Path (Join-Path $ProjectRoot "node_modules"))) {
    Write-Host "Instalando Electron..."
    & npm install
}

$env:PATH = "$(Join-Path $VenvPath 'Scripts');$env:PATH"

Write-Host "Iniciando SQX Edge Pro..."
& npm run dev
