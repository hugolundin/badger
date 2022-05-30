import logging
log = logging.getLogger(__name__)

import socket, os
import toml
from result import Ok, Err

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy
from .utilities import ip_address

class Badger:
    def __init__(self, config, docker):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.providers = []

        if os.path.exists(config):
            log.debug(f'Adding ConfigProvider for {config}.')

            config = toml.load(config)
            for name, mapping in config.items():
                try:
                    host = mapping['host']
                    port = mapping['port']
                except KeyError:
                    continue
                
                self.mappings[name] = (host, port)

        if docker:
            log.debug(f'Docker enabled.')

            for container in self.client.containers.list():
                try:
                    name = container.labels['BADGER_NAME']
                    host = container.labels['BADGER_HOST']
                    port = container.labels['BADGER_PORT']
                    self.mappings[name] = (host, port)
                except KeyError:
                    continue

    async def run(self):
        for name, (host, port) in self.mappings.items():
            log.debug(f"[{name}] -> {host}:{port}")

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
