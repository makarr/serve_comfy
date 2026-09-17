import sqlite3
from datetime import datetime
from uuid import UUID
from typing import Optional

import msgspec

def adapt_uuid(uuid_obj: UUID) -> str:
    return uuid_obj.hex

def convert_uuid(value: Optional[bytes]) -> Optional[UUID]:
    if value is None:
        return None
    
    # If value is bytes, decode to string
    if isinstance(value, bytes):
        value = value.decode('utf-8')
        
    return UUID(hex=value)

def adapt_dict(dict_obj: dict) -> bytes:
    return msgspec.json.encode(dict_obj)

def convert_json(dict_bytes: bytes) -> dict:
    return msgspec.json.decode(dict_bytes)

def adapt_datetime(dt_obj: datetime) -> str:
    return dt_obj.isoformat()

def convert_datetime(dt_bytes: bytes) -> datetime:
    return datetime.fromisoformat(dt_bytes.decode('utf-8'))


def register_adapters():
    sqlite3.register_adapter(UUID, adapt_uuid)
    sqlite3.register_adapter(dict, adapt_dict)
    sqlite3.register_adapter(bool, int)
    sqlite3.register_adapter(datetime, adapt_datetime)
    
    sqlite3.register_converter("UUID", convert_uuid)
    sqlite3.register_converter("JSON", convert_json)    
    sqlite3.register_converter("BOOLEAN", lambda x: bool(int(x)))
    sqlite3.register_converter("TIMESTAMP", convert_datetime)