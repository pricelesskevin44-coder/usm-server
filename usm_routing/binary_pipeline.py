import asyncio
import time
import struct

class BinaryPipeline:
    def __init__(self, storage=None):
        self.storage = storage
        self.lock = asyncio.Lock()

    async def process_frame(self, namespace: str, payload: bytes):
        async with self.lock:
            ts = time.time()
            header = struct.pack('>dI', ts, len(payload))
            frame = header + payload
            if self.storage:
                await self.storage.write_binary(namespace, frame)
            return frame
