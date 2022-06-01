import logging; log = logging.getLogger(__name__)  # fmt: skip

import json
import hashlib

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
