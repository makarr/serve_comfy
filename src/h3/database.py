import uuid

from src.common.database.connection import get_con

def insert_prompt_id(request_id: uuid.UUID, prompt_id: str) -> None:
    stmt = "INSERT INTO requests (request_id, status, prompt_id) VALUES (?, ?, ?)"
    with get_con(write=True) as con:
        con.execute(stmt, (request_id, "processing", prompt_id))


def insert_error(request_id: uuid.UUID, error_msg: str) -> None:
    stmt = "INSERT INTO requests (request_id, status, error_msg) VALUES (?, ?, ?)"
    with get_con(write=True) as con:
        con.execute(stmt, (request_id, "error", error_msg))


def select_status(request_id: uuid.UUID) -> str | None:
    stmt = "SELECT status FROM requests WHERE request_id = ? LIMIT 1"
    with get_con(write=False) as con:
        res = con.execute(stmt, (request_id,)).fetchone()
    if res:
        return res[0]