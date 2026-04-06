#!/data/data/com.termux/files/usr/bin/bash
BASE="$HOME/usm_server"
PID_FILE="$BASE/usm.pid"
LOG_FILE="$BASE/usm.log"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "[USM] Already running (PID $PID)"
    exit 0
  fi
fi

cd "$BASE"
export PYTHONPATH="$BASE:$PYTHONPATH"

nohup python main.py config.json >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
sleep 1

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  echo "[USM] Started (PID $PID)"
  echo "[USM] Log:  tail -f $LOG_FILE"
  echo "[USM] WS  → ws://localhost:8765"
  echo "[USM] API → http://localhost:8766/info"
else
  echo "[USM] ERROR: Server failed to start. Check $LOG_FILE"
  tail -20 "$LOG_FILE"
fi
