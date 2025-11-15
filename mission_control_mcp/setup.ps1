# MissionControlMCP Setup Script for Windows PowerShell
# Run this script to set up the MCP server

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         MissionControlMCP Installation Script           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Parse version
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "⚠️  Warning: Python 3.11+ is recommended" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

# Install dependencies
try {
    pip install -q -r requirements.txt
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Running verification tests..." -ForegroundColor Yellow
Write-Host ""

# Run tests
try {
    python test_server.py
} catch {
    Write-Host ""
    Write-Host "⚠️  Some tests may have failed (this is OK if optional dependencies are missing)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✓ Installation Complete!" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Test the server:" -ForegroundColor White
Write-Host "   python test_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the MCP server:" -ForegroundColor White
Write-Host "   uvx mcp dev mcp_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Integrate with Claude Desktop:" -ForegroundColor White
Write-Host "   See README.md for configuration details" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Read the documentation:" -ForegroundColor White
Write-Host "   README.md - User guide" -ForegroundColor Gray
Write-Host "   HACKATHON_SUBMISSION.md - Submission details" -ForegroundColor Gray
Write-Host ""

Write-Host "Happy automating! 🚀" -ForegroundColor Cyan
Write-Host ""
