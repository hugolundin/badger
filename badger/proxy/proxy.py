import logging
log = logging.getLogger(__name__)

import json
import asyncio
from pathlib import Path
from result import Result, Ok, Err

class Proxy:
    def __init__(self, port=80, script='handler.py', quiet=True):
        self.port = port
        self.script = Path(__file__).with_name(script).resolve()
        self.quiet = quiet

    async def run(self, mappings) -> Result[None, int]:
        
        # Encode twice in order to escape double-quotes.
        data = json.dumps(json.dumps([
            {'name': name, 'host': host, 'port': port} for name, (host, port) in mappings.items()
        ]))

        self.process = await asyncio.create_subprocess_shell(
            f'mitmdump -p {self.port} -s {self.script} {"--quiet" if self.quiet else ""} --set mappings={data}'
        )

        log.debug(f'Started {self.process.pid}')
        stdout, stderr = await self.process.communicate()
        log.debug(f'{stdout} {stderr}')

        match self.process.returncode:
            case 0:
                return Ok()
            case code:
                return Err(code)

    async def stop(self):
        await self.process.terminate()

    async def restart(self, mappings):
        await self.stop()
        await self.run(mappings)
