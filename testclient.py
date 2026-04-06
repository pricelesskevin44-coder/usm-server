import asyncio
import websockets
import json

async def viewer():
    port = open("usm_port.txt").read().strip()
    uri = f"ws://127.0.0.1:{port}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "subscribe", "pattern": "#"}))
        count = 0
        while count < 5:
            msg = await ws.recv()
            frame = json.loads(msg)
            print("[VIEWER]", frame)
            count += 1

async def publisher():
    port = open("usm_port.txt").read().strip()
    uri = f"ws://127.0.0.1:{port}"
    async with websockets.connect(uri) as ws:
        for i in range(5):
            await ws.send(json.dumps({
                "type": "publish",
                "namespace": "test/channel",
                "data": {"value": i}
            }))
            await asyncio.sleep(0.1)

async def main():
    await asyncio.gather(viewer(), publisher())

asyncio.run(main())
