import logging
log = logging.getLogger(__name__)

import toml, asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

class DockerProvider:
    pass

class ConfigProvider:
    def __init__(self, config, callback):
        self.path = Path(__file__).with_name(config).resolve()
        self.callback = callback
        self.observer = Observer()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

    async def run(self):
        event_handler = RegexMatchingEventHandler(str(self.path))
        event_handler.on_any_event = self.on_any_event
        self.observer.schedule(event_handler, self.path.parents[0])
        self.observer.start()
        await asyncio.Event().wait()

    def on_any_event(self, event):
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
            pass
        finally:
            self.callback(mappings)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(mappings):
        print(mappings)

    config = ConfigProvider('config.toml', callback)
    loop.run_until_complete(config.run())
