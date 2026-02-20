#!/bin/bash

set -e

REPO="https://github.com/weoxfx/wetg"
INSTALL_DIR="$HOME/.wetg"

echo "🔥 Installing WETG..."

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Updating existing install..."
    git -C "$INSTALL_DIR" pull
else
    echo "📦 Cloning repo..."
    git clone "$REPO" "$INSTALL_DIR"
fi

# Install dependencies
echo "📥 Installing requirements..."
pip install -r "$INSTALL_DIR/requirements.txt" --break-system-packages -q

# Create wetg command
WETG_BIN="$INSTALL_DIR/wetg_run.sh"
cat > "$WETG_BIN" << 'EOF'
#!/bin/bash
python3 "$HOME/.wetg/wetg.py" "$@"
EOF
chmod +x "$WETG_BIN"

# Add to PATH based on environment
if [ -d "$PREFIX/bin" ]; then
    # Termux
    cp "$WETG_BIN" "$PREFIX/bin/wetg"
    echo "✅ Installed to Termux PATH"
elif [ -w "/usr/local/bin" ]; then
    cp "$WETG_BIN" "/usr/local/bin/wetg"
    echo "✅ Installed to /usr/local/bin"
else
    sudo cp "$WETG_BIN" "/usr/local/bin/wetg"
    echo "✅ Installed to /usr/local/bin (sudo)"
fi

echo ""
echo "✅ WETG installed! Usage:"
echo "   wetg new mybot.wetg"
echo "   wetg run mybot.wetg"
echo "   wetg mybot.wetg"
