import time
import sqlite3
from config import settings
from database.db import get_connection

def execute_readonly(sql):
    started = time.perf_counter()
    conn = get_connection(readonly=True)
    deadline = settings.query_timeout_seconds
    conn.set_progress_handler(lambda: 1 if time.perf_counter() - started > deadline else 0, 1000)
    try:
        cursor = conn.execute(sql)
        columns = [d[0] for d in cursor.description or []]
        rows = cursor.fetchmany(settings.max_rows + 1)
        if len(rows) > settings.max_rows:
            rows = rows[:settings.max_rows]
        import pandas as pd
        df = pd.DataFrame([tuple(r) for r in rows], columns=columns)
        return df, time.perf_counter() - started
    except sqlite3.Error as exc:
        raise RuntimeError(str(exc)) from exc
    finally:
        conn.close()
