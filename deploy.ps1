#!/usr/bin/env pwsh
<#
.SYNOPSIS
Quick deployment setup script for Credit Engine Full Stack
.DESCRIPTION
This script sets up and launches both backend API and frontend for development/production
.EXAMPLE
.\deploy.ps1 -Mode dev
.\deploy.ps1 -Mode docker
#>

param(
    [ValidateSet("dev", "docker", "test")]
    [string]$Mode = "dev"
)

Write-Host "=====================================" -ForegroundColor Green
Write-Host "Credit Engine Full Stack Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Colors for output
$InfoColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"

function Write-Step {
    param([string]$Message)
    Write-Host "➜ $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $SuccessColor
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ErrorColor
}

# Common checks
Write-Step "Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python found: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found. Please install Python 3.9+"
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Success "Node found: $nodeVersion, npm: $npmVersion"
} catch {
    Write-Error-Custom "Node.js not found. Please install Node 18+"
    exit 1
}

# Main deployment logic
switch ($Mode) {
    "dev" {
        Write-Host ""
        Write-Host "Starting in DEVELOPMENT mode" -ForegroundColor Yellow
        Write-Host ""

        # Check virtual environment
        if (-Not (Test-Path .\.venv)) {
            Write-Step "Creating Python virtual environment..."
            python -m venv .venv
            Write-Success "Virtual environment created"
        }

        # Activate venv
        Write-Step "Activating Python virtual environment..."
        & .\.venv\Scripts\Activate.ps1

        # Install Python dependencies
        Write-Step "Installing Python dependencies..."
        pip install -r credit_engine/requirements.txt -q
        Write-Success "Python dependencies installed"

        # Install frontend dependencies
        Write-Step "Installing frontend dependencies..."
        Set-Location frontend
        npm ci --quiet
        Set-Location ..
        Write-Success "Frontend dependencies installed"

        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "Running in Development Mode" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Backend will start at: http://localhost:5000" -ForegroundColor Cyan
        Write-Host "Frontend will start at: http://localhost:5173" -ForegroundColor Cyan
        Write-Host ""

        # Option to start services
        $startServices = Read-Host "Start services now? (yes/no)"
        if ($startServices -eq "yes") {
            Write-Host ""
            Write-Host "Starting services in new terminal windows..." -ForegroundColor Yellow
            Write-Host "If they don't open, run manually:" -ForegroundColor Yellow
            Write-Host "  Terminal 1: python api.py" -ForegroundColor Gray
            Write-Host "  Terminal 2: cd frontend && npm run dev" -ForegroundColor Gray
            Write-Host ""

            # Start backend in new window
            Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd $PWD; python api.py"
            
            # Start frontend in new window
            Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd $PWD\frontend; npm run dev"
            
            Write-Success "Services started in new windows"
            Write-Host "Press Ctrl+C in each window to stop" -ForegroundColor Yellow
        }
    }

    "docker" {
        Write-Host ""
        Write-Host "Starting in DOCKER mode (Production)" -ForegroundColor Yellow
        Write-Host ""

        # Check Docker
        try {
            $dockerVersion = docker --version
            Write-Success "Docker found: $dockerVersion"
        } catch {
            Write-Error-Custom "Docker not found. Please install Docker Desktop"
            exit 1
        }

        Write-Step "Building Docker images..."
        docker-compose build

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker images built successfully"
        } else {
            Write-Error-Custom "Failed to build Docker images"
            exit 1
        }

        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "Running in Docker Mode" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host ""

        Write-Host "Backend will be at: http://localhost:5000" -ForegroundColor Cyan
        Write-Host "Frontend will be at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""

        $startDocker = Read-Host "Start Docker containers? (yes/no)"
        if ($startDocker -eq "yes") {
            Write-Step "Starting Docker containers..."
            docker-compose up -d

            Start-Sleep -Seconds 3

            Write-Success "Containers started"
            Write-Host ""
            Write-Host "Container Status:" -ForegroundColor Cyan
            docker-compose ps
            Write-Host ""
            Write-Host "View logs: docker-compose logs -f" -ForegroundColor Gray
            Write-Host "Stop containers: docker-compose down" -ForegroundColor Gray
        }
    }

    "test" {
        Write-Host ""
        Write-Host "Starting in TEST mode" -ForegroundColor Yellow
        Write-Host ""

        Write-Step "Testing backend API..."
        $apiTest = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -ErrorAction SilentlyContinue
        
        if ($apiTest.status -eq "healthy") {
            Write-Success "Backend API is responding"
        } else {
            Write-Error-Custom "Backend API is not responding. Make sure it's running on port 5000"
        }

        Write-Step "Testing frontend..."
        try {
            $frontendTest = Invoke-WebRequest -Uri "http://localhost:3000" -ErrorAction SilentlyContinue
            Write-Success "Frontend is responding"
        } catch {
            Write-Error-Custom "Frontend is not responding. Make sure it's running on port 3000"
        }

        Write-Host ""
        Write-Host "Testing model loader..."
        python -c "from credit_engine.model_loader import load_production_model; loader = load_production_model(); print('✓ Model loaded successfully')"
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Deployment Setup Complete" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
