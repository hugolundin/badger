import logging
log = logging.getLogger(__name__)

import toml
import docker

class DockerProvider:
    def __init__(self, callback):
        self.client = docker.from_env()
        self.callback = callback

    async def run(self):
        self.fetch()

    def fetch(self):
        mappings = {}

        for container in self.client.containers.list():
            try:
                name = container.labels['BADGER_NAME']
                host = container.labels['BADGER_HOST']
                port = container.labels['BADGER_PORT']
                mappings[name] = (host, port)
            except KeyError:
                continue
        
        self.callback(mappings)

class ConfigProvider:
    def __init__(self, path, callback):
        self.path = path
        self.callback = callback

    async def run(self):
        self.fetch()

    def fetch(self):
        mappings = {}

        try:
            config = toml.load(self.path)
            for name, mapping in config.items():
                try:
                    host = mapping['host']
                    port = mapping['port']
                except KeyError:
                    continue
                
                mappings[name] = (host, port)
        except FileNotFoundError:
            return

        self.callback(mappings)
