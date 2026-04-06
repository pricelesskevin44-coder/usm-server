import asyncio
from .subscription_registry import SubscriptionRegistry
from .frame_pipeline import FramePipeline
from .binary_pipeline import BinaryPipeline
from .storage_engine import StorageEngine

class RoutingEngine:
    def __init__(self):
        self.registry = SubscriptionRegistry()
        self.storage = StorageEngine()
        self.json_pipeline = FramePipeline(storage=self.storage)
        self.binary_pipeline = BinaryPipeline(storage=self.storage)
        self.lock = asyncio.Lock()

    def subscribe(self, websocket, pattern):
        self.registry.subscribe(websocket, pattern)

    def unsubscribe(self, websocket):
        self.registry.unsubscribe(websocket)

    async def route_json(self, namespace, data):
        async with self.lock:
            frame_json = await self.json_pipeline.process_frame(namespace, data)
            subscribers = self.registry.match(namespace)
            for ws in subscribers:
                try:
                    await ws.send(frame_json)
                except Exception as e:
                    print(f"[ROUTING ERROR] {e}")

    async def route_binary(self, namespace, payload: bytes):
        async with self.lock:
            frame_bin = await self.binary_pipeline.process_frame(namespace, payload)
            subscribers = self.registry.match(namespace)
            for ws in subscribers:
                try:
                    await ws.send(frame_bin)
                except Exception as e:
                    print(f"[ROUTING ERROR] {e}")
