import asyncio
import websockets

async def send_binary():
    port = open("usm_port.txt").read().strip()
    uri = f"ws://127.0.0.1:{port}"
    async with websockets.connect(uri) as ws:
        payload = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
        await ws.send(payload)
        print("Binary frame sent")

asyncio.run(send_binary())
