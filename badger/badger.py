import logging
log = logging.getLogger(__name__)

import socket, os
from result import Ok, Err
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy
from .providers import ConfigProvider, DockerProvider
from badger.providers import ConfigProvider
from .utilities import ip_address

class Badger:
    def __init__(self, config, docker):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.providers = []

        if os.path.exists(config):
            log.debug(f'Adding ConfigProvider for {config}.')
            self.providers.append(ConfigProvider(config, self.did_receive_mappings))

        if docker:
            log.debug(f'Docker enabled.')
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
                addresses=[socket.inet_aton(ip_address())],
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

        log.debug('Unregistering Zeroconf services')
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
        