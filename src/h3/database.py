import uuid

from src.common.database.connection import get_con

def insert_request(request_id: uuid.UUID) -> None:
    stmt = "INSERT INTO requests (request_id, status) VALUES (?, ?)"
    with get_con(write=True) as con:
        con.execute(stmt, (request_id, "processing"))

def select_status(request_id: uuid.UUID) -> str | None:
    stmt = "SELECT status FROM requests WHERE request_id = ? LIMIT 1"
    with get_con(write=False) as con:
        res = con.execute(stmt, (request_id,)).fetchone()
    if res:
        return res[0]