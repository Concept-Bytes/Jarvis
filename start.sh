#!/usr/bin/env bash
set -e

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_key_here" ]; then
  echo ""
  echo "❌  ANTHROPIC_API_KEY not set."
  echo "    Edit .env and add your key from https://console.anthropic.com"
  echo ""
  exit 1
fi

PORT="${PORT:-5000}"
echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║  Jarvis  →  http://localhost:$PORT  ║"
echo "  ╚═══════════════════════════════════╝"
echo ""
python3 app.py
