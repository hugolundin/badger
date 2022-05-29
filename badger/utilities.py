import json
import asyncio
import hashlib
import netifaces

def checksum(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.md5(serialized.encode('utf-8')).hexdigest()

def ip_address() -> str:
    interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

class ThreadSafeEvent(asyncio.Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)