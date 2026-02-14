import importlib
import json
import os
import sqlite3
import threading
import urllib.parse
import ssl
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DB_URL = os.getenv("DATABASE_URL", "").strip()
DB_KIND = "postgres" if DB_URL.startswith("postgres") else "sqlite"

DB_LOCK = threading.Lock()
conn = None
cursor = None
_PG_CONNECT_KWARGS: dict = {}
pg8000 = None

def _sql(sql: str) -> str:
    if DB_KIND == "sqlite":
        return sql
    return sql.replace("?", "%s")

def _is_retryable_db_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "timeout",
        "timed out",
        "broken pipe",
        "connection reset",
        "connection is closed",
        "connection closed",
        "server closed",
        "network",
        "could not receive data",
        "connection refused",
        "interfaceerror",
        "temporary failure in name resolution",
        "nodename nor servname provided",
        "ssl",
        "eof occurred",
    )
    return any(marker in text for marker in markers)


def _open_postgres_connection():
    if pg8000 is None:
        raise RuntimeError("pg8000 is not available for postgres connection")
    return pg8000.connect(**_PG_CONNECT_KWARGS)


def _reconnect_postgres_locked():
    global conn, cursor
    if DB_KIND != "postgres":
        return
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass
    conn = _open_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET client_encoding TO 'UTF8'")
        conn.commit()
    except Exception:
        pass


def _execute(sql: str, params: tuple = ()):
    global conn, cursor
    query = _sql(sql)
    attempts = 0
    while True:
        try:
            cursor.execute(query, params)
            return
        except Exception as exc:
            if DB_KIND != "postgres" or not _is_retryable_db_error(exc):
                raise
            attempts += 1
            if attempts > 2:
                raise
            _reconnect_postgres_locked()

if DB_KIND == "postgres":
    try:
        pg8000 = importlib.import_module("pg8000")
    except ModuleNotFoundError:
        print("[db] warning: pg8000 is missing, fallback to sqlite")
        DB_KIND = "sqlite"

if DB_KIND == "postgres":
    parsed = urllib.parse.urlparse(DB_URL)
    db_user = urllib.parse.unquote(parsed.username or "")
    db_password = urllib.parse.unquote(parsed.password or "")
    db_host = parsed.hostname or "localhost"
    db_port = parsed.port or 5432
    db_name = (parsed.path or "").lstrip("/")
    query = urllib.parse.parse_qs(parsed.query or "")
    sslmode = (query.get("sslmode", ["require"])[0] or "require").lower()
    ssl_context = None
    if sslmode in {"disable", "allow"}:
        ssl_context = None
    elif sslmode in {"no-verify", "verify-none", "require", "prefer"}:
        ssl_context = ssl._create_unverified_context()
    else:
        ssl_context = ssl.create_default_context()

    connect_timeout = float(os.getenv("DB_CONNECT_TIMEOUT", "30"))
    _PG_CONNECT_KWARGS = {
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
        "database": db_name,
        "ssl_context": ssl_context,
        "timeout": connect_timeout,
    }
    print(f"[db] connecting postgres {db_host}:{db_port}/{db_name} (timeout {connect_timeout}s)", flush=True)
    try:
        conn = _open_postgres_connection()
        print(f"[db] postgres {db_host}:{db_port}/{db_name}")
    except Exception as exc:
        print(f"[db] warning: postgres connect failed ({exc}), fallback to sqlite")
        DB_KIND = "sqlite"

if DB_KIND == "sqlite":
    DB_PATH = Path(__file__).resolve().parent / "bot_database.db"
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    print(f"[db] sqlite {DB_PATH}")

cursor = conn.cursor()
if DB_KIND == "postgres":
    with DB_LOCK:
        try:
            cursor.execute("SET client_encoding TO 'UTF8'")
            conn.commit()
        except Exception:
            pass

with DB_LOCK:
    if DB_KIND == "postgres":
        _execute("""
        CREATE TABLE IF NOT EXISTS applications (
            user_id BIGINT PRIMARY KEY,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            last_state TEXT,
            last_apply_at TEXT,
            data_json TEXT,
            admin_message_id BIGINT,
            menu_message_id BIGINT,
            flow_message_id BIGINT,
            source TEXT
        )
        """)
    else:
        _execute("""
        CREATE TABLE IF NOT EXISTS applications (
            user_id INTEGER PRIMARY KEY,
            status TEXT
        )
        """)
    conn.commit()

with DB_LOCK:
    _execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()

with DB_LOCK:
    if DB_KIND == "postgres":
        _execute("""
        CREATE TABLE IF NOT EXISTS posted_messages (
            id BIGSERIAL PRIMARY KEY,
            created_at TEXT,
            updated_at TEXT,
            content_type TEXT,
            source_chat_id BIGINT,
            source_message_id BIGINT,
            source_preview TEXT,
            message_ids_json TEXT,
            texts_json TEXT,
            entities_json TEXT
        )
        """)
    else:
        _execute("""
        CREATE TABLE IF NOT EXISTS posted_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            updated_at TEXT,
            content_type TEXT,
            source_chat_id INTEGER,
            source_message_id INTEGER,
            source_preview TEXT,
            message_ids_json TEXT,
            texts_json TEXT,
            entities_json TEXT
        )
        """)
    conn.commit()

def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def _ensure_columns():
    with DB_LOCK:
        if DB_KIND == "sqlite":
            _execute("PRAGMA table_info(applications)")
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
            if "admin_message_id" not in cols:
                alter.append("ALTER TABLE applications ADD COLUMN admin_message_id INTEGER")
            if "menu_message_id" not in cols:
                alter.append("ALTER TABLE applications ADD COLUMN menu_message_id INTEGER")
            if "flow_message_id" not in cols:
                alter.append("ALTER TABLE applications ADD COLUMN flow_message_id INTEGER")
            if "source" not in cols:
                alter.append("ALTER TABLE applications ADD COLUMN source TEXT")
            for stmt in alter:
                _execute(stmt)
            if alter:
                conn.commit()
            return

        alter_statements = [
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS created_at TEXT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS updated_at TEXT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_state TEXT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_apply_at TEXT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS data_json TEXT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS admin_message_id BIGINT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS menu_message_id BIGINT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS flow_message_id BIGINT",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS source TEXT",
        ]
        try:
            for statement in alter_statements:
                _execute(statement)
            conn.commit()
        except Exception as err:
            if DB_KIND == "postgres" and _is_retryable_db_error(err):
                try:
                    _reconnect_postgres_locked()
                    for statement in alter_statements:
                        _execute(statement)
                    conn.commit()
                    return
                except Exception:
                    pass
            print(f"[db] warning: migration failed: {err}")

_ensure_columns()

def set_status(user_id: int, status: str):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET status = ?, updated_at = ? WHERE user_id = ?",
                (status, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, status, ts, ts)
            )
        conn.commit()

def set_last_state(user_id: int, last_state: str | None):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET last_state = ?, updated_at = ? WHERE user_id = ?",
                (last_state, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, last_state, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, last_state, ts, ts)
            )
        conn.commit()

def set_last_apply_at(user_id: int):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET last_apply_at = ?, updated_at = ? WHERE user_id = ?",
                (ts, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, last_apply_at, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, ts, ts, ts)
            )
        conn.commit()

def set_form_data(user_id: int, data: dict):
    ts = _now_ts()
    payload = json.dumps(data, ensure_ascii=False)
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET data_json = ?, updated_at = ? WHERE user_id = ?",
                (payload, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, data_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, payload, ts, ts)
            )
        conn.commit()

def save_web_application(user_id: int, data: dict, source: str | None = None, status: str = "pending"):
    ts = _now_ts()
    payload = json.dumps(data, ensure_ascii=False)
    with DB_LOCK:
        _execute(
            """
            INSERT INTO applications (
                user_id, status, created_at, updated_at, last_apply_at, data_json, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at,
                last_apply_at = excluded.last_apply_at,
                data_json = excluded.data_json,
                source = excluded.source
            """,
            (user_id, status, ts, ts, ts, payload, source)
        )
        conn.commit()

def set_admin_message_id(user_id: int, message_id: int | None):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET admin_message_id = ?, updated_at = ? WHERE user_id = ?",
                (message_id, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, admin_message_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, message_id, ts, ts)
            )
        conn.commit()

def get_admin_message_id(user_id: int) -> int | None:
    with DB_LOCK:
        _execute(
            "SELECT admin_message_id FROM applications WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

def set_menu_message_id(user_id: int, message_id: int | None):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET menu_message_id = ?, updated_at = ? WHERE user_id = ?",
                (message_id, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, menu_message_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, message_id, ts, ts)
            )
        conn.commit()

def set_source(user_id: int, source: str | None):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET source = ?, updated_at = ? WHERE user_id = ?",
                (source, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, source, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, source, ts, ts)
            )
        conn.commit()

def get_source(user_id: int) -> str | None:
    with DB_LOCK:
        _execute(
            "SELECT source FROM applications WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

def get_menu_message_id(user_id: int) -> int | None:
    with DB_LOCK:
        _execute(
            "SELECT menu_message_id FROM applications WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

def set_flow_message_id(user_id: int, message_id: int | None):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET flow_message_id = ?, updated_at = ? WHERE user_id = ?",
                (message_id, ts, user_id)
            )
        else:
            _execute(
                "INSERT INTO applications (user_id, flow_message_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, message_id, ts, ts)
            )
        conn.commit()

def get_flow_message_id(user_id: int) -> int | None:
    with DB_LOCK:
        _execute(
            "SELECT flow_message_id FROM applications WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

def get_admin_messages_for_archive(days: int) -> list[tuple[int, int]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with DB_LOCK:
        _execute(
            "SELECT user_id, admin_message_id FROM applications "
            "WHERE admin_message_id IS NOT NULL "
            "AND status IN ('accepted', 'rejected') "
            "AND updated_at < ?",
            (cutoff,)
        )
        return [(row[0], row[1]) for row in cursor.fetchall() if row[1] is not None]

def reset_all_data():
    with DB_LOCK:
        _execute("DELETE FROM applications")
        _execute("DELETE FROM settings")
        _execute("DELETE FROM posted_messages")
        conn.commit()
        if DB_KIND == "sqlite":
            try:
                _execute("VACUUM")
            except Exception:
                pass

def set_setting(key: str, value: str | None):
    with DB_LOCK:
        _execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()

def get_setting(key: str) -> str | None:
    with DB_LOCK:
        _execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]


SUPPORTED_LANGUAGES = {"ru", "en", "pt", "es"}
DEFAULT_LANGUAGE = "ru"


def _lang_setting_key(user_id: int) -> str:
    return f"user_lang:{int(user_id)}"


def set_user_language(user_id: int, language: str) -> None:
    lang = (language or "").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    set_setting(_lang_setting_key(user_id), lang)


def get_user_language(user_id: int) -> str:
    value = (get_setting(_lang_setting_key(user_id)) or "").strip().lower()
    if value in SUPPORTED_LANGUAGES:
        return value
    return DEFAULT_LANGUAGE


def has_user_language(user_id: int) -> bool:
    value = (get_setting(_lang_setting_key(user_id)) or "").strip().lower()
    return value in SUPPORTED_LANGUAGES

def list_applications(status: str | None = None) -> list[dict]:
    with DB_LOCK:
        if status:
            _execute(
                "SELECT user_id, status, updated_at FROM applications "
                "WHERE status = ? "
                "ORDER BY updated_at DESC",
                (status,)
            )
        else:
            _execute(
                "SELECT user_id, status, updated_at FROM applications "
                "WHERE status IN ('pending', 'accepted', 'rejected') "
                "ORDER BY updated_at DESC"
            )
        rows = cursor.fetchall()
        return [
            {"user_id": row[0], "status": row[1], "updated_at": row[2]}
            for row in rows
        ]


def list_applications_for_export() -> list[dict]:
    with DB_LOCK:
        _execute(
            "SELECT user_id, status, updated_at FROM applications "
            "ORDER BY "
            "CASE WHEN updated_at IS NULL OR updated_at = '' THEN 1 ELSE 0 END, "
            "updated_at DESC"
        )
        rows = cursor.fetchall()
        return [
            {"user_id": row[0], "status": row[1], "updated_at": row[2]}
            for row in rows
        ]

def clear_form_data(user_id: int):
    ts = _now_ts()
    with DB_LOCK:
        _execute(
            "SELECT 1 FROM applications WHERE user_id = ?",
            (user_id,)
        )
        exists = cursor.fetchone() is not None
        if exists:
            _execute(
                "UPDATE applications SET data_json = NULL, updated_at = ? WHERE user_id = ?",
                (ts, user_id)
            )
            conn.commit()

def get_form_data(user_id: int) -> dict | None:
    with DB_LOCK:
        _execute(
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
    with DB_LOCK:
        _execute(
            "SELECT status, last_apply_at, last_state, created_at, updated_at, admin_message_id, source "
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
            "admin_message_id": row[5],
            "source": row[6],
        }

def get_status(user_id: int) -> str | None:
    with DB_LOCK:
        _execute(
            "SELECT status FROM applications WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

def get_status_counts() -> dict:
    with DB_LOCK:
        _execute(
            "SELECT status, COUNT(*) FROM applications "
            "WHERE status IN ('new', 'pending', 'accepted', 'rejected') "
            "GROUP BY status"
        )
        rows = cursor.fetchall()
        counts = {"total": 0, "new": 0, "pending": 0, "accepted": 0, "rejected": 0}
        for status, count in rows:
            if status in counts:
                counts[status] = count
        counts["total"] = counts["pending"] + counts["accepted"] + counts["rejected"]
        return counts

def cleanup_old_form_data(days: int = 30):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with DB_LOCK:
        _execute(
            "UPDATE applications SET data_json = NULL "
            "WHERE data_json IS NOT NULL AND status = 'new' AND updated_at < ?",
            (cutoff,)
        )
        conn.commit()


def _json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _safe_json(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _post_preview(texts: dict | None) -> str:
    if not isinstance(texts, dict):
        return ""
    source = (
        texts.get("ru")
        or texts.get("en")
        or texts.get("pt")
        or texts.get("es")
        or ""
    )
    if not isinstance(source, str):
        source = str(source)
    compact = " ".join(source.split())
    return compact[:220]


def create_posted_message(
    content_type: str,
    source_chat_id: int | None,
    source_message_id: int | None,
    message_ids: dict,
    texts: dict,
    entities: dict | None = None,
) -> int:
    ts = _now_ts()
    preview = _post_preview(texts)
    message_ids_json = _json_text(message_ids or {})
    texts_json = _json_text(texts or {})
    entities_json = _json_text(entities or {})
    with DB_LOCK:
        if DB_KIND == "postgres":
            _execute(
                """
                INSERT INTO posted_messages (
                    created_at, updated_at, content_type,
                    source_chat_id, source_message_id, source_preview,
                    message_ids_json, texts_json, entities_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    ts,
                    ts,
                    content_type,
                    source_chat_id,
                    source_message_id,
                    preview,
                    message_ids_json,
                    texts_json,
                    entities_json,
                )
            )
            row = cursor.fetchone()
            conn.commit()
            return int(row[0]) if row else 0

        _execute(
            """
            INSERT INTO posted_messages (
                created_at, updated_at, content_type,
                source_chat_id, source_message_id, source_preview,
                message_ids_json, texts_json, entities_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                ts,
                content_type,
                source_chat_id,
                source_message_id,
                preview,
                message_ids_json,
                texts_json,
                entities_json,
            )
        )
        post_id = int(cursor.lastrowid or 0)
        conn.commit()
        return post_id


def get_posted_message(post_id: int) -> dict | None:
    with DB_LOCK:
        _execute(
            """
            SELECT id, created_at, updated_at, content_type,
                   source_chat_id, source_message_id, source_preview,
                   message_ids_json, texts_json, entities_json
            FROM posted_messages
            WHERE id = ?
            """,
            (post_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(row[0]),
            "created_at": row[1],
            "updated_at": row[2],
            "content_type": row[3],
            "source_chat_id": row[4],
            "source_message_id": row[5],
            "source_preview": row[6] or "",
            "message_ids": _safe_json(row[7], {}),
            "texts": _safe_json(row[8], {}),
            "entities": _safe_json(row[9], {}),
        }


def count_posted_messages() -> int:
    with DB_LOCK:
        _execute("SELECT COUNT(*) FROM posted_messages")
        row = cursor.fetchone()
        return int(row[0]) if row else 0


def list_posted_messages(limit: int = 20, offset: int = 0) -> list[dict]:
    with DB_LOCK:
        _execute(
            """
            SELECT id, created_at, updated_at, content_type,
                   source_chat_id, source_message_id, source_preview,
                   message_ids_json, texts_json, entities_json
            FROM posted_messages
            ORDER BY
                CASE WHEN created_at IS NULL OR created_at = '' THEN 1 ELSE 0 END,
                created_at DESC,
                id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        rows = cursor.fetchall()
        result: list[dict] = []
        for row in rows:
            result.append(
                {
                    "id": int(row[0]),
                    "created_at": row[1],
                    "updated_at": row[2],
                    "content_type": row[3],
                    "source_chat_id": row[4],
                    "source_message_id": row[5],
                    "source_preview": row[6] or "",
                    "message_ids": _safe_json(row[7], {}),
                    "texts": _safe_json(row[8], {}),
                    "entities": _safe_json(row[9], {}),
                }
            )
        return result


def update_posted_message(
    post_id: int,
    texts: dict | None = None,
    entities: dict | None = None,
    message_ids: dict | None = None,
) -> bool:
    current = get_posted_message(post_id)
    if not current:
        return False
    ts = _now_ts()
    new_texts = texts if texts is not None else current.get("texts", {})
    new_entities = entities if entities is not None else current.get("entities", {})
    new_message_ids = message_ids if message_ids is not None else current.get("message_ids", {})
    preview = _post_preview(new_texts)
    with DB_LOCK:
        _execute(
            """
            UPDATE posted_messages
            SET updated_at = ?,
                source_preview = ?,
                message_ids_json = ?,
                texts_json = ?,
                entities_json = ?
            WHERE id = ?
            """,
            (
                ts,
                preview,
                _json_text(new_message_ids or {}),
                _json_text(new_texts or {}),
                _json_text(new_entities or {}),
                post_id,
            )
        )
        conn.commit()
        return True


def delete_posted_message(post_id: int) -> None:
    with DB_LOCK:
        _execute("DELETE FROM posted_messages WHERE id = ?", (post_id,))
        conn.commit()
