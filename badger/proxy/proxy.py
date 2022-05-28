import logging
log = logging.getLogger(__name__)

import json
import asyncio
from pathlib import Path
from result import Result, Ok, Err

class Proxy:
    def __init__(self, port=8000, script='handler.py', quiet=True):
        self.port = port
        self.script = Path(__file__).with_name(script).resolve()
        self.quiet = quiet
        self.event = asyncio.Event()

    async def run(self, mappings) -> Result[None, int]:
        
        # Encode twice in order to escape double-quotes.
        data = json.dumps(json.dumps([
            {'name': name, 'host': host, 'port': port} for name, (host, port) in mappings.items()
        ]))

        process = await asyncio.create_subprocess_shell(
            f'mitmdump -p {self.port} -s {self.script} {"--quiet" if self.quiet else ""} --set mappings={data}'
        )

        log.debug(f'Started {process.pid}')

        try:
            while True:
                await asyncio.wait([process.communicate(), self.event.wait()], return_when=asyncio.FIRST_COMPLETED)

                if self.event.is_set():
                    self.event.clear()
                    continue

                match process.returncode:
                    case 0:
                        return Ok()
                    case code:
                        return Err(code)

        except asyncio.CancelledError:
            return Ok()
