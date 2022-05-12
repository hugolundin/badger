import logging
log = logging.getLogger(__name__)

import json
import asyncio
from result import Result, Ok, Err

class Proxy:
    def __init__(self):
        pass

    async def run(self, mappings) -> Result[None, None]:
        serialized = json.dumps([
            {'name': name, 'host': host, 'port': port} for name, (host, port) in mappings.items()
        ])

        process = await asyncio.create_subprocess_shell(
            f'mitmdump -p 80 -s handler.py --quiet --set mappings={serialized}',
            shell=True
        )

        log.debug(f'Started {process.pid}')

        stdout, stderr = await process.communicate()

        log.debug(f'{stdout} {stderr}')

        match process.returncode:
            case 0:
                return Ok()
            case code:
                return Err(code)
