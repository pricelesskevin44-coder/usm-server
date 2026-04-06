"""
ws/server — WebSocket server entry point (websockets >= 12).

URL routing:
  ws://host:8765/publish/<namespace>   → publisher
  ws://host:8765/view/<pattern>        → viewer (pattern can use * and #)
  ws://host:8765/                      → viewer with subscription=#
"""

import asyncio
import websockets
from ws.handshake   import perform_handshake
from ws.connections import conns
from utils.logging  import logger

async def handler(websocket):
    # Get request path (websockets >= 12 API)
    try:
        path = websocket.request.path
    except AttributeError:
        try:
            path = websocket.path
        except AttributeError:
            path = '/'

    path = path or '/'

    # Perform protocol handshake (version negotiation)
    hs = await perform_handshake(websocket)
    if not hs:
        return

    # Resolve role + namespace/subscription from URL path
    if path.startswith('/publish/'):
        ns = path[len('/publish/'):].strip('/')
        if ns:
            hs['namespace'] = ns
        hs.setdefault('role', 'publisher')

    elif path.startswith('/view/'):
        sub = path[len('/view/'):].strip('/')
        if sub:
            hs['subscription'] = sub
        hs.setdefault('role', 'viewer')

    role = hs.get('role', 'viewer')

    if role == 'publisher':
        # Must have a namespace
        if not hs.get('namespace'):
            logger.warn("publisher_no_namespace", client_id=hs.get('id'))
            hs['namespace'] = 'default'
        await conns.handle_publisher(websocket, hs)
    else:
        hs.setdefault('subscription', '#')
        await conns.handle_viewer(websocket, hs)

def run(host: str = "0.0.0.0", port: int = 8765):
    logger.info("usm_ws_start", host=host, port=port)

    async def _serve():
        async with websockets.serve(handler, host, port):
            logger.info("usm_ws_ready", url=f"ws://{host}:{port}")
            await asyncio.Future()   # run forever

    asyncio.run(_serve())
