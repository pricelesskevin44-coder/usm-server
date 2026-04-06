import asyncio
import json
import time

class FramePipeline:
    def __init__(self, storage=None):
        self.storage = storage
        self.lock = asyncio.Lock()

    async def process_frame(self, namespace, data):
        async with self.lock:
            frame = {
                "type": "frame",
                "namespace": namespace,
                "data": data,
                "timestamp": time.time()
            }
            if self.storage:
                await self.storage.write(namespace, frame)
            return json.dumps(frame)
