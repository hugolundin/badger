import logging

from badger.providers import ConfigProvider
log = logging.getLogger(__name__)

import socket
import asyncio
from pathlib import Path
from result import Ok, Err
from os.path import exists
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy
from .providers import ConfigProvider, DockerProvider

class Badger:
    def __init__(self, config):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.providers = []

        path = Path(__file__).with_name(config).resolve()
        if exists(path):
            self.providers.append(ConfigProvider(path, self.did_receive_mappings))

        self.providers.append(DockerProvider(self.did_receive_mappings))

    def did_receive_mappings(self, mappings):
        self.mappings.update(mappings)

    async def run(self):
        for provider in self.providers:
            await provider.run()

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

        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
