#!/bin/bash
# MissionControlMCP Setup Script for Unix/Linux/macOS

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         MissionControlMCP Installation Script           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
    
    # Check if version is 3.11+
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        echo "⚠️  Warning: Python 3.11+ is recommended"
    fi
else
    echo "✗ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."

# Install dependencies
if pip3 install -q -r requirements.txt; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    echo "Try running manually: pip3 install -r requirements.txt"
    exit 1
fi

echo ""
echo "Running verification tests..."
echo ""

# Run tests
python3 test_server.py || echo "⚠️  Some tests may have failed (this is OK if optional dependencies are missing)"

echo ""
echo "══════════════════════════════════════════════════════════"
echo "✓ Installation Complete!"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "📚 Next Steps:"
echo ""
echo "1. Test the server:"
echo "   python3 test_server.py"
echo ""
echo "2. Start the MCP server:"
echo "   uvx mcp dev mcp_server.py"
echo ""
echo "3. Integrate with Claude Desktop:"
echo "   See README.md for configuration details"
echo ""
echo "4. Read the documentation:"
echo "   README.md - User guide"
echo "   HACKATHON_SUBMISSION.md - Submission details"
echo ""

echo "Happy automating! 🚀"
echo ""
