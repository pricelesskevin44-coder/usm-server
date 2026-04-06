#!/usr/bin/env python3
"""
USM Test Client — pure Python, no extra deps.
Usage:
  python test_client.py              # full round-trip test
  python test_client.py publish      # publish 5 frames
  python test_client.py view         # view stream (Ctrl-C to stop)
  python test_client.py api          # HTTP API endpoints
"""

import sys
import json
import time
import asyncio
import urllib.request

WS_HOST  = "localhost"
WS_PORT  = 8765
API_BASE = "http://localhost:8766"
NS       = "test/robot/alpha"

# ── HTTP API ─────────────────────────────────────────────────────

def test_api():
    print("\n=== HTTP API TEST ===")
    for ep in ["/info", "/namespaces", "/stats",
               f"/namespaces/{NS}/state"]:
        try:
            with urllib.request.urlopen(API_BASE + ep, timeout=3) as r:
                print(f"GET {ep} → {json.dumps(json.loads(r.read()), indent=2)}")
        except Exception as e:
            print(f"GET {ep} → {e}")

# ── Handshake ────────────────────────────────────────────────────

async def _handshake(ws, role, subscription=None):
    hs = {"frame_type": "handshake", "role": role, "version": 1}
    if subscription:
        hs["subscription"] = subscription
    await ws.send(json.dumps(hs))
    ack = json.loads(await ws.recv())
    print(f"[{role.upper()}] Handshake ack: {ack}")
    return ack

# ── Publisher ────────────────────────────────────────────────────

async def run_publisher(n_frames=5, delay=0.8):
    import websockets
    uri = f"ws://{WS_HOST}:{WS_PORT}/publish/{NS}"
    print(f"\n[PUBLISHER] Connecting → {uri}")
    async with websockets.connect(uri) as ws:
        await _handshake(ws, "publisher")
        for i in range(n_frames):
            frame = {
                "frame_type":  "state",
                "namespace":   NS,
                "json_state":  {
                    "x": round(i * 1.5, 2),
                    "y": round(i * 0.8, 2),
                    "speed": round(i * 0.3, 3),
                    "active": True,
                    "seq": i,
                },
                "binary_desc": {"present": False},
            }
            await ws.send(json.dumps(frame))
            print(f"[PUBLISHER] Sent frame {i+1}/{n_frames}  seq={i}")
            await asyncio.sleep(delay)
        # Stay connected briefly so server can flush
        await asyncio.sleep(1.0)
    print("[PUBLISHER] Done.")

# ── Viewer ───────────────────────────────────────────────────────

async def run_viewer(expect=5, timeout=30):
    import websockets
    uri = f"ws://{WS_HOST}:{WS_PORT}/view/#"
    print(f"\n[VIEWER] Connecting → {uri}")
    received = 0
    async with websockets.connect(uri) as ws:
        await _handshake(ws, "viewer", subscription="#")
        deadline = time.time() + timeout
        while received < expect and time.time() < deadline:
            try:
                raw  = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(raw)
                ft   = data.get('frame_type', 'state')
                if ft in ('heartbeat', 'handshake_ack'):
                    continue
                if ft == 'error':
                    print(f"[VIEWER] Server error: {data}")
                    continue
                ns   = data.get('namespace', '?')
                js   = data.get('json_state', {})
                harm = data.get('harmonics', {})
                temp = data.get('temporal', {})
                print(
                    f"[VIEWER]  frame {received+1} | ns={ns} | "
                    f"seq={js.get('seq','?')} | "
                    f"coherence={harm.get('coherence','?')} | "
                    f"delta={float(temp.get('delta', 0)):.4f}s"
                )
                received += 1
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[VIEWER] recv error: {e}")
                break
    print(f"[VIEWER] Done. Received {received}/{expect} frames.")
    return received

# ── Full round-trip ───────────────────────────────────────────────

async def run_full_test():
    print("\n╔══════════════════════════════════════╗")
    print("║  USM ROUND-TRIP TEST                ║")
    print("╚══════════════════════════════════════╝")
    print(f"\nTip: tail -f ~/usm_server/usm.log  (in another session)\n")

    viewer_task = asyncio.create_task(run_viewer(expect=5, timeout=30))
    await asyncio.sleep(0.5)   # viewer connects first
    pub_task    = asyncio.create_task(run_publisher(n_frames=5, delay=0.8))

    received, _ = await asyncio.gather(viewer_task, pub_task)

    await asyncio.sleep(0.5)
    test_api()

    if received == 5:
        print("\n✅  TEST PASSED — USM routing pipeline verified.")
    else:
        print(f"\n❌  TEST FAILED — {received}/5 frames received.")
        print("    Run:  tail -f ~/usm_server/usm.log")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if   mode == 'api':     test_api()
    elif mode == 'publish': asyncio.run(run_publisher())
    elif mode == 'view':    asyncio.run(run_viewer(expect=9999, timeout=3600))
    else:                   asyncio.run(run_full_test())
