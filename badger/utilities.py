import logging; log = logging.getLogger(__name__)  # fmt: skip

import json
import asyncio
import hashlib
from signal import SIGINT, SIGTERM

import netifaces


def checksum(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()


def ip_address() -> str:
    interface = netifaces.gateways()["default"][netifaces.AF_INET][1]
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]


def parse_mappings(mappings) -> dict:
    result = {}

    for mapping in mappings:
        name, address = mapping.split("@")
        host, port = address.split(":")
        result[name] = (host, port)

    return result


def exec(fn):
    def cancel_tasks():
        for t in asyncio.all_tasks():
            t.cancel()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for s in [SIGINT, SIGTERM]:
        loop.add_signal_handler(s, cancel_tasks)

    try:
        loop.run_until_complete(fn)
    except asyncio.exceptions.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
