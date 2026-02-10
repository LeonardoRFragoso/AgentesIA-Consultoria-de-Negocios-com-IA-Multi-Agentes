# Script para rodar o backend em desenvolvimento com SQLite
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"
$env:DATABASE_URL = "sqlite:///./dev.db"
$env:JWT_SECRET_KEY = "dev-only-secret-key-change-in-production-minimum-32-chars"
$env:CORS_ORIGINS = '["http://localhost:3000","http://localhost:8501","http://localhost:8000"]'

Write-Host "Starting backend in development mode..." -ForegroundColor Green
Write-Host "Database: SQLite (dev.db)" -ForegroundColor Cyan
Write-Host "Environment: development" -ForegroundColor Cyan

python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
