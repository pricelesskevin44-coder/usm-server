#!/data/data/com.termux/files/usr/bin/bash
PID_FILE="$HOME/usm_server/usm.pid"
echo "=== USM STATUS ==="
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Server : RUNNING (PID $PID)"
  else
    echo "Server : DEAD (stale PID file)"
  fi
else
  echo "Server : STOPPED"
fi

echo ""
echo "--- API /info ---"
curl -s http://localhost:8766/info 2>/dev/null || echo "(API not reachable)"
echo ""
echo "--- API /stats ---"
curl -s http://localhost:8766/stats 2>/dev/null || echo "(API not reachable)"
echo ""
