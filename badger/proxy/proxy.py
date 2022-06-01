import logging; log = logging.getLogger(__name__)  # fmt: skip

import json
import asyncio
import logging
from pathlib import Path

from result import Ok, Err, Result


class Proxy:
    def __init__(self, port=80, script="handler.py", quiet=True):
        self.port = port
        self.script = Path(__file__).with_name(script).resolve()
        self.quiet = quiet

    async def run(self, mappings) -> Result[None, int]:

        # Encode twice in order to escape double-quotes.
        data = json.dumps(
            json.dumps(
                [
                    {"name": name, "host": host, "port": port}
                    for name, (host, port) in mappings.items()
                ]
            )
        )

        process = await asyncio.create_subprocess_shell(
            f'mitmdump -p {self.port} -s {self.script} {"--quiet" if self.quiet else ""} --set mappings={data}'
        )

        log.debug(f"Started {process.pid}")

        try:
            stdout, stderr = await process.communicate()
            log.debug(f"{stdout} {stderr}")

            match process.returncode:
                case 0:
                    return Ok()
                case code:
                    return Err(code)
        except asyncio.CancelledError:
            return Ok()
