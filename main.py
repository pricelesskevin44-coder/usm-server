import asyncio
import json
import websockets
from usm_routing.routing_engine import RoutingEngine

router = RoutingEngine()
CLIENT_ID = 0

def next_client_id():
    global CLIENT_ID
    CLIENT_ID += 1
    return CLIENT_ID

async def handle_connection(websocket):
    client_id = next_client_id()
    print(f"[CONNECT] Client {client_id}")
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                namespace = "binary/channel"
                await router.route_binary(namespace, message)
            else:
                msg = json.loads(message)
                t = msg.get("type")
                if t == "handshake":
                    await websocket.send(json.dumps({
                        "type": "handshakeack",
                        "client_id": client_id
                    }))
                elif t == "subscribe":
                    pattern = msg.get("pattern", "#")
                    router.subscribe(websocket, pattern)
                elif t == "publish":
                    namespace = msg.get("namespace")
                    data = msg.get("data")
                    await router.route_json(namespace, data)
    finally:
        router.unsubscribe(websocket)
        print(f"[DISCONNECT] Client {client_id}")

async def start_server():
    for port in range(8765, 8800):
        try:
            server = await websockets.serve(handle_connection, "127.0.0.1", port)
            print(f"[USM-WS] Running on ws://127.0.0.1:{port}")
            with open("usm_port.txt", "w") as f:
                f.write(str(port))
            return server, port
        except OSError:
            continue
    raise RuntimeError("No free ports available")

async def main():
    server, port = await start_server()
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
