import logging
log = logging.getLogger(__name__)

import asyncio
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy

class Badger:
    def __init__(self):
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.All)

    async def run(self):
        await asyncio.Event().wait()
