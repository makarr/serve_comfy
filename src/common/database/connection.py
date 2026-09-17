import sqlite3
from contextlib import contextmanager
from typing import Generator

from src.config.constants import DB_PATH

@contextmanager
def get_con(
    write: bool = False
) -> Generator[sqlite3.Connection, None, None]:
    try:
        con = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
        yield con
    except sqlite3.Error as e:
        raise e
    finally:
        if write:
            con.commit()
        con.close()