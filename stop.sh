#!/data/data/com.termux/files/usr/bin/bash
PID_FILE="$HOME/usm_server/usm.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "[USM] Not running (no PID file)"
  exit 0
fi
PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  rm -f "$PID_FILE"
  echo "[USM] Stopped (PID $PID)"
else
  echo "[USM] Was not running"
  rm -f "$PID_FILE"
fi
