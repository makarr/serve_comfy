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


def update_error(request_id: uuid.UUID, error_msg: str) -> None:
    stmt = "UPDATE requests SET status = ?, error_msg = ? WHERE request_id = ?"
    with get_con(write=True) as con:
        con.execute(stmt, ("error", error_msg, request_id))


def select_request(request_id: uuid.UUID) -> str | None:
    stmt = "SELECT * FROM requests WHERE request_id = ? LIMIT 1"
    with get_con(write=False) as con:
        if res := con.execute(stmt, (request_id,)).fetchone():
            return res


def update_success(request_id: uuid.UUID, filename: str, url_name: str) -> None:
    stmt = """
    UPDATE requests 
    SET status = ?, filename = ?, url_name = ? 
    WHERE request_id = ?
    """
    with get_con(write=True) as con:
        con.execute(stmt, ("success", filename, url_name, request_id))


def select_filename(url_name: str) -> str | None:
    stmt = "SELECT filename FROM requests WHERE url_name = ? LIMIT 1"
    with get_con(write=False) as con:
        res = con.execute(stmt, (url_name,)).fetchone()
    if res:
        return res[0]