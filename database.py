import json
import sqlite3
from datetime import datetime, timezone, timedelta

conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    user_id INTEGER PRIMARY KEY,
    status TEXT
)
""")
conn.commit()

def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def _ensure_columns():
    cursor.execute("PRAGMA table_info(applications)")
    cols = {row[1] for row in cursor.fetchall()}
    alter = []
    if "created_at" not in cols:
        alter.append("ALTER TABLE applications ADD COLUMN created_at TEXT")
    if "updated_at" not in cols:
        alter.append("ALTER TABLE applications ADD COLUMN updated_at TEXT")
    if "last_state" not in cols:
        alter.append("ALTER TABLE applications ADD COLUMN last_state TEXT")
    if "last_apply_at" not in cols:
        alter.append("ALTER TABLE applications ADD COLUMN last_apply_at TEXT")
    if "data_json" not in cols:
        alter.append("ALTER TABLE applications ADD COLUMN data_json TEXT")
    for stmt in alter:
        cursor.execute(stmt)
    if alter:
        conn.commit()

_ensure_columns()

def set_status(user_id: int, status: str):
    ts = _now_ts()
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id = ?",
        (user_id,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute(
            "UPDATE applications SET status = ?, updated_at = ? WHERE user_id = ?",
            (status, ts, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO applications (user_id, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, status, ts, ts)
        )
    conn.commit()

def set_last_state(user_id: int, last_state: str):
    ts = _now_ts()
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id = ?",
        (user_id,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute(
            "UPDATE applications SET last_state = ?, updated_at = ? WHERE user_id = ?",
            (last_state, ts, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO applications (user_id, last_state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, last_state, ts, ts)
        )
    conn.commit()

def set_last_apply_at(user_id: int):
    ts = _now_ts()
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id = ?",
        (user_id,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute(
            "UPDATE applications SET last_apply_at = ?, updated_at = ? WHERE user_id = ?",
            (ts, ts, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO applications (user_id, last_apply_at, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, ts, ts, ts)
        )
    conn.commit()

def set_form_data(user_id: int, data: dict):
    ts = _now_ts()
    payload = json.dumps(data, ensure_ascii=False)
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id = ?",
        (user_id,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute(
            "UPDATE applications SET data_json = ?, updated_at = ? WHERE user_id = ?",
            (payload, ts, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO applications (user_id, data_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, payload, ts, ts)
        )
    conn.commit()

def clear_form_data(user_id: int):
    ts = _now_ts()
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id = ?",
        (user_id,)
    )
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute(
            "UPDATE applications SET data_json = NULL, updated_at = ? WHERE user_id = ?",
            (ts, user_id)
        )
        conn.commit()

def get_form_data(user_id: int) -> dict | None:
    cursor.execute(
        "SELECT data_json FROM applications WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if not row or not row[0]:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None


def get_application(user_id: int) -> dict | None:
    cursor.execute(
        "SELECT status, last_apply_at, last_state, created_at, updated_at "
        "FROM applications WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "status": row[0],
        "last_apply_at": row[1],
        "last_state": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }

def get_status(user_id: int) -> str | None:
    cursor.execute(
        "SELECT status FROM applications WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        return None
    return row[0]

def get_status_counts() -> dict:
    cursor.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status"
    )
    rows = cursor.fetchall()
    counts = {"total": 0, "new": 0, "pending": 0, "accepted": 0, "rejected": 0}
    for status, count in rows:
        if status is None:
            continue
        counts["total"] += count
        if status in counts:
            counts[status] = count
    return counts

def cleanup_old_form_data(days: int = 30):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cursor.execute(
        "UPDATE applications SET data_json = NULL "
        "WHERE data_json IS NOT NULL AND status = 'new' AND updated_at < ?",
        (cutoff,)
    )
    conn.commit()
