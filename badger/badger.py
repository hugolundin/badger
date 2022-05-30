import logging
from multiprocessing.sharedctypes import Value
log = logging.getLogger(__name__)

import socket, os
import toml
import pathlib, docker
from result import Ok, Err

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from .proxy import Proxy
from .utilities import ip_address

class Badger:
    def __init__(self, config, enable_docker):
        self.mappings = {}
        self.proxy = Proxy()
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.providers = []
        self.config = {}

        if config:
            path = pathlib.Path(__file__).parent.with_name(config).resolve()
            if os.path.exists(path):
                self.config = toml.load(path)
            else:
                log.warning(f'BADGER_CONFIG_PATH ({path}) was not found.')

        # TODO: Add format validation.
        for name, address in self.config.get('mappings', {}).items():
            self.mappings[name] = address.split(':')

        if self.config.get('docker', True):
            if enable_docker:
                log.debug(f'Docker enabled.')

                try:
                    for container in docker.from_env().containers.list():
                        try:
                            name = container.labels['BADGER_NAME']
                            host = container.labels['BADGER_HOST']
                            port = container.labels['BADGER_PORT']
                            self.mappings[name] = (host, port)
                        except KeyError:
                            continue
                except docker.errors.DockerException:
                    log.warning('Unable to connect to Docker.')

    async def run(self):
        for name, (host, port) in self.mappings.items():
            log.debug(f"{name} -> {host}:{port}")

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
