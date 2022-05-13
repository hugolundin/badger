import logging
log = logging.getLogger(__name__)

import socket
from result import Ok, Err
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy

class Badger:
    def __init__(self):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)

    def __del__(self):
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()

    async def run(self):
        await self.register_mappings()

        match await self.proxy.run(self.mappings):
            case Ok(_):
                pass
            case Err(ret):
                log.error(f'Proxy returned {ret}')

    async def register_mappings(self):
        for name, _ in self.mappings.items():
            service = ServiceInfo(
                '_http._tcp.local.',
                f'{name}._http._tcp.local.',
                addresses=[socket.inet_aton('10.0.0.52')],
                port=80,
                properties={},
                server=f'{name}.local',
            )

            self.zeroconf.register_service(service)
