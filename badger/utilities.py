import json
import hashlib

def checksum(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.md5(serialized.encode('utf-8'))
