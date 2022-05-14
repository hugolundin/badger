import logging
log = logging.getLogger(__name__)

import socket
from result import Ok, Err
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy
from .providers import ConfigProvider

class Badger:
    def __init__(self):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.config = ConfigProvider('config.toml', self.callback)

    def __del__(self):
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()

    async def callback(self, mappings):
        self.mappings = mappings
        await self.stop()
        await self.run()

    async def run(self):
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

        match await self.proxy.run(self.mappings):
            case Ok(_):
                pass
            case Err(ret):
                log.error(f'Proxy returned {ret}')

    async def stop(self):
        self.proxy.stop()
        self.zeroconf.unregister_all_services()
