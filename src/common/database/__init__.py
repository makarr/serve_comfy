from .adapters import register_adapters
from .connection import get_con

register_adapters()

init_script = """
CREATE TABLE IF NOT EXISTS requests (
    request_id  UUID UNIQUE NOT NULL,
    status      TEXT,
    error_msg   TEXT,
    prompt_id   TEXT
);
"""

with get_con(write=True) as con:
    con.executescript(init_script)