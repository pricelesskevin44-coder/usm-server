import asyncio
import os
import json
from collections import deque
import aiofiles

class StorageEngine:
    def __init__(self, path=None, retention=3600):
        self.path = os.path.expanduser("~/usm_storage") if path is None else path
        self.retention = retention
        self.memory = {}
        self.lock = asyncio.Lock()
        os.makedirs(self.path, exist_ok=True)

    async def write(self, namespace, frame):
        async with self.lock:
            if namespace not in self.memory:
                self.memory[namespace] = deque()
            self.memory[namespace].append(frame)
            # Cleanup old frames
            now = frame.get("timestamp", 0)
            while self.memory[namespace] and now - self.memory[namespace][0].get("timestamp",0) > self.retention:
                self.memory[namespace].popleft()
            # Write to disk
            filename = os.path.join(self.path, namespace.replace("/", "_")+".log")
            async with aiofiles.open(filename, mode='a') as f:
                await f.write(json.dumps(frame) + "\n")

    async def write_binary(self, namespace, frame: bytes):
        async with self.lock:
            filename = os.path.join(self.path, namespace.replace("/", "_")+".bin")
            async with aiofiles.open(filename, 'ab') as f:
                await f.write(frame)

    async def read(self, namespace):
        async with self.lock:
            return list(self.memory.get(namespace, []))
