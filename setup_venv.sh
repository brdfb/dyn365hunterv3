#!/bin/bash
# Setup Python virtual environment for local development

set -e

echo "🐍 Setting up Python virtual environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    echo "   Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_CMD="python3"
echo "✅ Found $(python3 --version)"

# Check if venv already exists
if [ -d ".venv" ] || [ -d "venv" ]; then
    # Remove Windows venv if exists (Scripts/ indicates Windows venv)
    if [ -d ".venv/Scripts" ]; then
        echo "⚠️  Windows venv detected, removing..."
        rm -rf .venv venv
    else
        echo "ℹ️  Virtual environment already exists"
        echo "   To recreate, delete .venv or venv directory first"
        exit 0
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if ! $PYTHON_CMD -m venv .venv 2>/dev/null; then
    echo "⚠️  venv module not available"
    
    # Check if we're on Debian/Ubuntu
    if command -v apt &> /dev/null; then
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
        echo "📦 Installing python3-venv package..."
        echo "   Run: sudo apt install python${PYTHON_VERSION}-venv"
        echo ""
        echo "   Or install manually:"
        echo "   sudo apt update"
        echo "   sudo apt install python3-venv"
        exit 1
    else
        echo "❌ venv module not available and package manager not found"
        echo "   Please install python3-venv manually"
        exit 1
    fi
fi

# Activate virtual environment (for dependency installation)
echo "🔌 Preparing virtual environment..."
# Note: We don't actually activate in the script, just prepare it
# User needs to activate manually after script completes

# Upgrade pip (use python -m pip for better compatibility)
echo "⬆️  Upgrading pip..."
if [ -f ".venv/bin/python" ]; then
    # Linux/Mac/WSL
    .venv/bin/python -m pip install --upgrade pip --quiet
elif [ -f ".venv/Scripts/python.exe" ]; then
    # Windows
    .venv/Scripts/python.exe -m pip install --upgrade pip --quiet
else
    echo "⚠️  Could not find Python in venv, skipping pip upgrade"
fi

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    if [ -f ".venv/bin/pip" ]; then
        # Linux/Mac/WSL
        .venv/bin/pip install -r requirements.txt --quiet
    elif [ -f ".venv/Scripts/pip.exe" ]; then
        # Windows
        .venv/Scripts/pip.exe install -r requirements.txt --quiet
    else
        echo "⚠️  Could not find pip in venv, trying activated environment..."
        pip install -r requirements.txt --quiet
    fi
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping dependency installation"
fi

echo ""
echo "🎉 Virtual environment setup complete!"
echo ""
if [ -f ".venv/bin/activate" ]; then
    echo "📋 To activate the virtual environment (Linux/Mac/WSL):"
    echo "   source .venv/bin/activate"
elif [ -f ".venv/Scripts/activate" ]; then
    echo "📋 To activate the virtual environment (Windows):"
    echo "   Git Bash:     source .venv/Scripts/activate"
    echo "   CMD:          .venv\\Scripts\\activate.bat"
    echo "   PowerShell:   .venv\\Scripts\\Activate.ps1"
fi
echo ""
echo "📝 To deactivate: deactivate"
echo ""

