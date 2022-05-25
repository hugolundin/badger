import json
import hashlib
import netifaces

def checksum(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.md5(serialized.encode('utf-8')).hexdigest()

def ip_address() -> str:
    interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
