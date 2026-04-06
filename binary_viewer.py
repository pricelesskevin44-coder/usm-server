import asyncio
import websockets
import struct

async def receive_binary():
    port = open("usm_port.txt").read().strip()
    uri = f"ws://127.0.0.1:{port}"
    async with websockets.connect(uri) as ws:
        print(f"[BINARY VIEWER] Connected to {uri}")
        while True:
            frame = await ws.recv()
            if isinstance(frame, bytes):
                ts, length = struct.unpack(">dI", frame[:12])
                payload = frame[12:]
                print(f"[BINARY FRAME] ts={ts:.3f} length={length} payload={payload[:10]}...")

asyncio.run(receive_binary())
