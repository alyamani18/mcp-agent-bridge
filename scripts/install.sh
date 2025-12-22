#!/bin/bash
# Install MCP Agent Bridge
# Author: Wojciech Wiesner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Installing MCP Agent Bridge..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp config/example.env .env
    echo "Please edit .env with your configuration"
fi

# Create log directory
echo "Creating log directory..."
sudo mkdir -p /var/log/mcp-agent-bridge
sudo chown $USER:$USER /var/log/mcp-agent-bridge

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Agent Zero token"
echo "2. Run: ./scripts/start_all.sh"
echo ""
echo "For systemd installation:"
echo "  sudo cp config/systemd/*.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now codex-mcp-proxy claude-mcp-proxy"
