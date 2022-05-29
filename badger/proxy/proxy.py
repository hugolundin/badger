import logging
log = logging.getLogger(__name__)

import json
import asyncio
from pathlib import Path
from result import Result, Ok, Err

from ..utilities import ThreadSafeEvent

class Proxy:
    def __init__(self, port=80, script='handler.py', quiet=True):
        self.port = port
        self.script = Path(__file__).with_name(script).resolve()
        self.quiet = quiet
        self.event = ThreadSafeEvent()
        self.mappings = None

    def restart(self, mappings):
        self.event.set()
        self.mappings = mappings

    async def run(self, mappings) -> Result[None, int]:
        self.event.clear()
        self.mappings = mappings

        try:
            while True:
                self.event.clear()

                # Encode twice in order to escape double-quotes.
                data = json.dumps(json.dumps([
                    {'name': name, 'host': host, 'port': port} for name, (host, port) in self.mappings.items()
                ]))
                
                process = await asyncio.create_subprocess_shell(
                    f'mitmdump -p {self.port} -s {self.script} {"--quiet" if self.quiet else ""} --set mappings={data}'
                )

                log.debug(f'Started {process.pid}')
                
                await asyncio.wait([
                    asyncio.create_task(process.communicate()),
                    asyncio.create_task(self.event.wait())
                ], return_when=asyncio.FIRST_COMPLETED)

                if self.event.is_set():
                    log.debug('Reloading proxy...')
                    process.kill()
                    continue
                
                match process.returncode:
                    case 0:
                        return Ok()
                    case code:
                        return Err(code)

        except asyncio.CancelledError:
            return Ok()
