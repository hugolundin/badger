import logging
log = logging.getLogger(__name__)

import toml
import docker
import asyncio
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from .utilities import checksum

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
        self.observer = Observer()
        self.identifier = None

    async def run(self):
        await self.fetch()
        event_handler = RegexMatchingEventHandler(str(self.path))
        event_handler.on_any_event = self.on_any_event
        self.observer.schedule(event_handler, self.path.parent)
        self.observer.start()
        await asyncio.Event().wait()

    def on_any_event(self, _):
        asyncio.run(self.fetch())

    async def fetch(self):
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
        except (FileNotFoundError, toml.TomlDecodeError):
            return

        identifier = checksum(mappings)
        if identifier != self.identifier:
            self.identifier = identifier
            await self.callback(mappings)
