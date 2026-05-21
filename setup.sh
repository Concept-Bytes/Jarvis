#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════╗"
echo "║        Jarvis Setup Script       ║"
echo "╚══════════════════════════════════╝"
echo ""

# ── Check Python ────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌  Python3 not found."
  echo "    On Termux:  pkg install python"
  echo "    On Debian:  sudo apt install python3 python3-pip"
  exit 1
fi

PY=$(python3 --version)
echo "✔  $PY found"

# ── Create .env ─────────────────────────────────────────
if [ ! -f .env ]; then
  cat > .env <<'ENV'
# Get your key at https://console.anthropic.com
ANTHROPIC_API_KEY=your_key_here

# Optional: Spotify integration
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_USERNAME=

# Server port (default 5000)
PORT=5000
ENV
  echo "✔  Created .env  →  edit it and set ANTHROPIC_API_KEY before starting"
else
  echo "✔  .env already exists"
fi

# ── Create directories ───────────────────────────────────
mkdir -p images static/icons templates
echo "✔  Directories ready"

# ── Install core dependencies (no compilation needed) ────
echo ""
echo "Installing core dependencies…"
pip3 install flask anthropic
echo "✔  Core dependencies installed (flask, anthropic)"

# ── Install optional tool dependencies ───────────────────
echo ""
echo "Installing optional tool dependencies…"
pip3 install python-weather spotipy || echo "⚠  python-weather/spotipy failed — weather & Spotify tools won't work (chat still works fine)"
pip3 install icrawler || echo "⚠  icrawler failed — image search won't work (chat still works fine)"
echo "✔  Optional tools done"

# ── Termux:Boot auto-start (runs only inside Termux) ────
if command -v termux-setup-storage &>/dev/null 2>&1; then
  BOOT_DIR="$HOME/.termux/boot"
  mkdir -p "$BOOT_DIR"
  SCRIPT="$BOOT_DIR/start-jarvis.sh"
  JARVIS_DIR="$(pwd)"
  cat > "$SCRIPT" <<BOOT
#!/data/data/com.termux/files/usr/bin/bash
cd $JARVIS_DIR
source .env 2>/dev/null || true
export ANTHROPIC_API_KEY
python3 app.py >> jarvis.log 2>&1 &
BOOT
  chmod +x "$SCRIPT"
  echo "✔  Termux:Boot script created → Jarvis will start automatically on reboot"
fi

echo ""
echo "══════════════════════════════════════════"
echo "  Setup complete! Next steps:"
echo ""
echo "  1.  Edit .env and paste your API key"
echo "      (get one at https://console.anthropic.com)"
echo ""
echo "  2.  Start Jarvis:"
echo "      ./start.sh"
echo ""
echo "  3.  Open Chrome and go to:"
echo "      http://localhost:5000"
echo ""
echo "  4.  To install as a home-screen app:"
echo "      Chrome menu → 'Add to Home screen'"
echo "══════════════════════════════════════════"
echo ""
