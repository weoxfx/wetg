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
pip install -r "$INSTALL_DIR/requirements.txt" --break-system-packages -q 2>/dev/null \
    || pip3 install -r "$INSTALL_DIR/requirements.txt" -q

# Determine writable bin directory
if [ -d "$PREFIX/bin" ]; then
    # Termux
    BIN_DIR="$PREFIX/bin"
elif [ -w "/usr/local/bin" ]; then
    BIN_DIR="/usr/local/bin"
else
    # Replit / restricted systems — use ~/.local/bin
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

# Create wetg command
cat > "$BIN_DIR/wetg" << EOF
#!/bin/bash
python3 "$INSTALL_DIR/wetg.py" "\$@"
EOF
chmod +x "$BIN_DIR/wetg"

# Add ~/.local/bin to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
    export PATH="$BIN_DIR:$PATH"
    echo "📌 Added $BIN_DIR to PATH"
fi

echo ""
echo "✅ WETG installed! Usage:"
echo "   wetg new mybot.wetg"
echo "   wetg run mybot.wetg"
echo "   wetg mybot.wetg"
echo ""
echo "💡 If 'wetg' is not found, run:  source ~/.bashrc"
