"""
auth.py — Single shared account authentication.

Default credentials: username=BIT, password=11223344
Password can be changed via the UI (stored in SQLite).
Sessions are server-side tokens stored in SQLite.
"""

import sqlite3
import hashlib
import secrets
from pathlib import Path
from helpers import BASE_DIR, logger

DB_PATH = BASE_DIR / "auth.db"

DEFAULT_USERNAME = "BIT"
DEFAULT_PASSWORD = "11223344"


def _conn():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id        INTEGER PRIMARY KEY CHECK (id = 1),
                username  TEXT NOT NULL DEFAULT 'BIT',
                pass_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        existing = db.execute("SELECT COUNT(*) FROM credentials").fetchone()[0]
        if existing == 0:
            db.execute(
                "INSERT INTO credentials (id, username, pass_hash) VALUES (1, ?, ?)",
                (DEFAULT_USERNAME, _hash(DEFAULT_PASSWORD))
            )
        db.commit()
    logger.info("Auth DB ready.")


def _hash(password: str) -> str:
    salt = "bw_static_salt_v1"
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _get_creds():
    with _conn() as db:
        return db.execute("SELECT username, pass_hash FROM credentials WHERE id=1").fetchone()


def login_user(username: str, password: str) -> dict:
    creds = _get_creds()
    if not creds:
        return {"ok": False, "error": "Auth not initialised."}
    if username.strip().upper() != creds["username"].upper():
        return {"ok": False, "error": "Incorrect username or password."}
    if _hash(password) != creds["pass_hash"]:
        return {"ok": False, "error": "Incorrect username or password."}
    token = secrets.token_hex(32)
    with _conn() as db:
        db.execute("INSERT INTO sessions (token) VALUES (?)", (token,))
        db.commit()
    logger.info("Login successful.")
    return {"ok": True, "token": token, "user": {"name": "Admin", "username": creds["username"]}}


def get_user_by_token(token: str):
    if not token:
        return None
    with _conn() as db:
        row = db.execute("SELECT token FROM sessions WHERE token=?", (token,)).fetchone()
    if not row:
        return None
    creds = _get_creds()
    return {"name": "Admin", "username": creds["username"] if creds else "BIT"}


def logout_user(token: str):
    if not token:
        return
    with _conn() as db:
        db.execute("DELETE FROM sessions WHERE token=?", (token,))
        db.commit()


def change_password(old_password: str, new_password: str) -> dict:
    creds = _get_creds()
    if not creds:
        return {"ok": False, "error": "Auth not initialised."}
    if _hash(old_password) != creds["pass_hash"]:
        return {"ok": False, "error": "Current password is incorrect."}
    if len(new_password) < 8:
        return {"ok": False, "error": "New password must be at least 8 characters."}
    with _conn() as db:
        db.execute("UPDATE credentials SET pass_hash=? WHERE id=1", (_hash(new_password),))
        db.execute("DELETE FROM sessions")   # force re-login after password change
        db.commit()
    logger.info("Password changed. All sessions invalidated.")
    return {"ok": True}
