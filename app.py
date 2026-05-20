import argparse
from contextlib import contextmanager
import csv
import json
import math
import mimetypes
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.parse
import uuid
import webbrowser
import zipfile
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_NAME = "智能文件复习系统 2.0 WebUI"
APP_VERSION = "2.7.0"
SCHEMA_VERSION = 3
DEFAULT_PORT = 8765
WEBVIEW_WINDOW = None


def user_documents_dir() -> Path:
    return Path.home() / "Documents"


DEFAULT_APP_DIR = user_documents_dir() / "LiFileReviewer2"
PROFILE_POINTER_PATH = DEFAULT_APP_DIR / "profile_location.json"


def fs_path(path: str | Path) -> str:
    value = str(Path(path).expanduser())
    if platform.system() != "Windows":
        return value
    absolute = os.path.abspath(value)
    if absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute.lstrip("\\")
    return "\\\\?\\" + absolute


def user_path(path: str | Path) -> str:
    value = str(path)
    if value.startswith("\\\\?\\UNC\\"):
        return "\\\\" + value[8:]
    if value.startswith("\\\\?\\"):
        return value[4:]
    return value


def path_exists(path: str | Path) -> bool:
    return os.path.exists(fs_path(path))


def path_is_file(path: str | Path) -> bool:
    return os.path.isfile(fs_path(path))


def path_is_dir(path: str | Path) -> bool:
    return os.path.isdir(fs_path(path))


def path_stat(path: str | Path):
    return os.stat(fs_path(path))


def ensure_dir(path: str | Path) -> None:
    os.makedirs(fs_path(path), exist_ok=True)


def read_text_file(path: str | Path) -> str:
    with open(fs_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def write_text_file(path: str | Path, content: str) -> None:
    ensure_dir(Path(path).parent)
    with open(fs_path(path), "w", encoding="utf-8") as handle:
        handle.write(content)


def copy_file(src: str | Path, dst: str | Path) -> None:
    ensure_dir(Path(dst).parent)
    shutil.copy2(fs_path(src), fs_path(dst))


def unlink_file(path: str | Path) -> None:
    os.unlink(fs_path(path))


def resolve_profile_dir() -> Path:
    env_path = os.environ.get("LI_FILE_REVIEWER_PROFILE")
    if env_path:
        return Path(env_path).expanduser().resolve()
    try:
        if path_exists(PROFILE_POINTER_PATH):
            payload = json.loads(read_text_file(PROFILE_POINTER_PATH))
            app_dir = payload.get("app_dir")
            if app_dir:
                return Path(app_dir).expanduser().resolve()
    except Exception:
        pass
    return DEFAULT_APP_DIR


def set_app_dir(path: str | Path) -> None:
    global APP_DIR, CONFIG_PATH, DB_PATH, LOG_PATH, BACKUP_DIR, PLUGINS_DIR, DEFAULT_NOTES_DIR, EXPORT_DIR
    APP_DIR = Path(path).expanduser().resolve()
    CONFIG_PATH = APP_DIR / "config.json"
    DB_PATH = APP_DIR / "review_data.sqlite"
    LOG_PATH = APP_DIR / "app.log"
    BACKUP_DIR = APP_DIR / "backups"
    PLUGINS_DIR = APP_DIR / "plugins"
    DEFAULT_NOTES_DIR = APP_DIR / "notes"
    EXPORT_DIR = APP_DIR / "exports"


set_app_dir(resolve_profile_dir())


DEFAULT_CONFIG = {
    "app_name": APP_NAME,
    "version": APP_VERSION,
    "library_roots": [],
    "scan_extensions": [
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
        ".txt", ".md", ".html", ".htm", ".rtf", ".epub",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",
        ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".mp3", ".wav", ".m4a",
    ],
    "ignore_dirs": [
        ".git", ".svn", ".hg", "__pycache__", "node_modules", ".obsidian",
        ".trash", "$RECYCLE.BIN", "System Volume Information",
    ],
    "follow_hidden_dirs": False,
    "scheduler": {
        "algorithm": "FSRS-Lite",
        "desired_retention": 0.90,
        "max_reviews_per_day": 120,
        "max_new_per_day": 40,
        "new_item_due_immediately": True,
    },
    "review": {
        "auto_open_file": False,
        "external_open_on_review_start": False,
        "show_preview": True,
        "default_rating": 2,
    },
    "notes": {
        "storage_dir": "",
        "default_extension": ".md",
        "open_local_note_after_create": False,
    },
    "exports": {
        "default_dir": "",
    },
    "reminders": {
        "enabled": True,
        "time": "20:30",
        "repeat_minutes": 90,
        "browser_notifications": True,
    },
    "ui": {
        "language": "zh-CN",
        "theme": "light",
        "density": "comfortable",
        "accent": "#2563eb",
        "surface": "#ffffff",
        "background": "#f4f6f8",
        "text": "#172033",
        "sidebar": "#111827",
        "custom_css": "",
    },
    "maintenance": {
        "auto_backup_before_migration": True,
        "keep_backup_count": 30,
    },
    "plugins": {
        "enabled": True,
        "auto_load": False,
        "installed": [],
    },
}


RATING_LABELS = {
    0: "忘记",
    1: "困难",
    2: "良好",
    3: "简单",
}


def ensure_app_dirs() -> None:
    ensure_dir(APP_DIR)
    ensure_dir(BACKUP_DIR)
    ensure_dir(PLUGINS_DIR)
    ensure_dir(DEFAULT_NOTES_DIR)
    ensure_dir(EXPORT_DIR)
    manifest_path = PLUGINS_DIR / "README.md"
    if not path_exists(manifest_path):
        write_text_file(
            manifest_path,
            "# Plugins\n\n"
            "Put future plugin folders here. Each plugin can provide a `plugin.json` manifest.\n"
            "The current stable app records plugin metadata but does not execute plugin code by default.\n",
        )


def log_error(message: str) -> None:
    ensure_app_dirs()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(fs_path(LOG_PATH), "a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def version_tuple(value: str) -> tuple[int, int, int]:
    parts = []
    for piece in str(value or "0").split(".")[:3]:
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)  # type: ignore[return-value]


def normalize_config(config: dict) -> tuple[dict, bool]:
    changed = False
    previous_version = version_tuple(config.get("version", "0.0.0"))
    if previous_version < (2, 4, 0):
        review = config.setdefault("review", {})
        review["auto_open_file"] = False
        review["external_open_on_review_start"] = False
        changed = True
    if config.get("version") != APP_VERSION:
        config["version"] = APP_VERSION
        changed = True
    return config, changed


def load_config() -> dict:
    ensure_app_dirs()
    if path_exists(CONFIG_PATH):
        try:
            with open(fs_path(CONFIG_PATH), "r", encoding="utf-8") as handle:
                merged = deep_merge(DEFAULT_CONFIG, json.load(handle))
            merged, changed = normalize_config(merged)
            if changed:
                save_config(merged)
            return merged
        except Exception:
            log_error("配置读取失败：\n" + traceback.format_exc())
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    ensure_app_dirs()
    merged = deep_merge(DEFAULT_CONFIG, config)
    merged["version"] = APP_VERSION
    temp_path = CONFIG_PATH.with_suffix(".json.tmp")
    with open(fs_path(temp_path), "w", encoding="utf-8") as handle:
        json.dump(merged, handle, ensure_ascii=False, indent=2)
    os.replace(fs_path(temp_path), fs_path(CONFIG_PATH))


def write_profile_pointer() -> None:
    ensure_dir(DEFAULT_APP_DIR)
    payload = {
        "app_dir": str(APP_DIR),
        "updated_at": iso_now(),
        "app_version": APP_VERSION,
    }
    if PROFILE_POINTER_PATH.resolve() != (APP_DIR / "profile_location.json").resolve():
        write_text_file(PROFILE_POINTER_PATH, json.dumps(payload, ensure_ascii=False, indent=2))


def profile_paths() -> dict:
    return {
        "app_dir": str(APP_DIR),
        "default_app_dir": str(DEFAULT_APP_DIR),
        "profile_pointer_path": str(PROFILE_POINTER_PATH),
        "config_path": str(CONFIG_PATH),
        "db_path": str(DB_PATH),
        "log_path": str(LOG_PATH),
        "backup_dir": str(BACKUP_DIR),
        "plugins_dir": str(PLUGINS_DIR),
        "default_notes_dir": str(DEFAULT_NOTES_DIR),
        "notes_dir": str(notes_dir()),
        "export_dir": str(export_dir()),
    }


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def notes_dir(config: dict | None = None) -> Path:
    if config is None and path_exists(CONFIG_PATH):
        try:
            config = load_config()
        except Exception:
            config = {}
    config = config or {}
    configured = config.get("notes", {}).get("storage_dir") or ""
    return Path(configured).expanduser().resolve() if configured else DEFAULT_NOTES_DIR


def ensure_notes_dir(config: dict | None = None) -> Path:
    target = notes_dir(config)
    ensure_dir(target)
    return target


def export_dir(config: dict | None = None) -> Path:
    if config is None and path_exists(CONFIG_PATH):
        try:
            config = load_config()
        except Exception:
            config = {}
    config = config or {}
    configured = config.get("exports", {}).get("default_dir") or ""
    return Path(configured).expanduser().resolve() if configured else EXPORT_DIR


def ensure_export_dir(config: dict | None = None, target_dir: str | Path | None = None) -> Path:
    target = Path(target_dir).expanduser().resolve() if target_dir else export_dir(config)
    ensure_dir(target)
    return target


def iso_now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None


def human_size(num: int | None) -> str:
    if not num:
        return "0 B"
    value = float(num)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@contextmanager
def get_conn(db_path: Path | None = None):
    ensure_app_dirs()
    conn = sqlite3.connect(fs_path(db_path or DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if column not in {row["name"] for row in rows}:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def db_user_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def set_db_user_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(f"PRAGMA user_version = {int(version)}")


def backup_file(path: Path, reason: str = "manual") -> Path:
    ensure_app_dirs()
    if not path_exists(path):
        raise FileNotFoundError(f"无法备份，文件不存在：{path}")
    safe_reason = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in reason)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"{path.stem}_{safe_reason}_{stamp}{path.suffix}"
    copy_file(path, target)
    rotate_backups()
    return target


def backup_sqlite_database(source: Path, reason: str = "manual") -> Path:
    ensure_app_dirs()
    return backup_sqlite_database_to(source, BACKUP_DIR, reason)


def backup_sqlite_database_to(source: Path, target_dir: Path, reason: str = "manual") -> Path:
    ensure_dir(target_dir)
    if not path_exists(source):
        raise FileNotFoundError(f"无法备份，数据库不存在：{source}")
    safe_reason = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in reason)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = target_dir / f"{source.stem}_{safe_reason}_{stamp}{source.suffix}"
    src = sqlite3.connect(fs_path(source))
    try:
        dst = sqlite3.connect(fs_path(target))
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    if target_dir.resolve() == BACKUP_DIR.resolve():
        rotate_backups()
    return target


def rotate_backups() -> None:
    config = load_config()
    keep = int(config.get("maintenance", {}).get("keep_backup_count", 30) or 30)
    if keep <= 0 or not path_exists(BACKUP_DIR):
        return
    backups = sorted(BACKUP_DIR.glob("*.sqlite"), key=lambda p: path_stat(p).st_mtime, reverse=True)
    for old in backups[keep:]:
        try:
            unlink_file(old)
        except OSError:
            log_error(f"旧备份清理失败：{old}")


def record_migration(conn: sqlite3.Connection, from_version: int, to_version: int, note: str) -> None:
    conn.execute(
        """
        INSERT INTO schema_migrations(from_version, to_version, app_version, migrated_at, note)
        VALUES(?, ?, ?, ?, ?)
        """,
        (from_version, to_version, APP_VERSION, iso_now(), note),
    )


def init_db(db_path: Path | None = None) -> None:
    target_db = db_path or DB_PATH
    existing_version = 0
    if path_exists(target_db):
        with get_conn(target_db) as pre_conn:
            existing_version = db_user_version(pre_conn)
        config = load_config()
        should_backup = config.get("maintenance", {}).get("auto_backup_before_migration", True)
        if should_backup and existing_version < SCHEMA_VERSION:
            backup_sqlite_database(target_db, f"before_schema_{existing_version}_to_{SCHEMA_VERSION}")
    with get_conn(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_version INTEGER NOT NULL,
                to_version INTEGER NOT NULL,
                app_version TEXT NOT NULL,
                migrated_at TEXT NOT NULL,
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS libraries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_path TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                added_at TEXT NOT NULL,
                last_scan_at TEXT,
                file_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT NOT NULL UNIQUE,
                library_id INTEGER,
                root_path TEXT,
                relative_path TEXT,
                file_path TEXT NOT NULL UNIQUE,
                file_name TEXT NOT NULL,
                ext TEXT,
                size_bytes INTEGER DEFAULT 0,
                modified_at TEXT,
                added_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_seen_at TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                tags TEXT DEFAULT '',
                priority INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                due_at TEXT NOT NULL,
                interval_days REAL DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                stability REAL DEFAULT 2.5,
                difficulty REAL DEFAULT 5.0,
                retrievability REAL DEFAULT 1.0,
                review_count INTEGER DEFAULT 0,
                lapse_count INTEGER DEFAULT 0,
                total_read_seconds INTEGER DEFAULT 0,
                last_review_at TEXT,
                pinned INTEGER DEFAULT 0,
                FOREIGN KEY(library_id) REFERENCES libraries(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS review_sessions (
                id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                session_id TEXT,
                started_at TEXT,
                ended_at TEXT NOT NULL,
                duration_seconds INTEGER DEFAULT 0,
                rating INTEGER NOT NULL,
                rating_label TEXT,
                algorithm TEXT,
                scheduled_days REAL,
                ease_factor REAL,
                stability REAL,
                difficulty REAL,
                retrievability REAL,
                FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT NOT NULL UNIQUE,
                item_id INTEGER,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source TEXT DEFAULT 'app',
                FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_items_due ON items(status, due_at);
            CREATE INDEX IF NOT EXISTS idx_items_file_name ON items(file_name);
            CREATE INDEX IF NOT EXISTS idx_items_library ON items(library_id);
            CREATE INDEX IF NOT EXISTS idx_history_item ON review_history(item_id, ended_at);
            CREATE INDEX IF NOT EXISTS idx_notes_item ON notes(item_id, updated_at);
            """
        )
        migrations = [
            ("items", "guid", "TEXT"),
            ("items", "library_id", "INTEGER"),
            ("items", "root_path", "TEXT"),
            ("items", "relative_path", "TEXT"),
            ("items", "priority", "INTEGER DEFAULT 0"),
            ("items", "notes", "TEXT DEFAULT ''"),
            ("items", "stability", "REAL DEFAULT 2.5"),
            ("items", "difficulty", "REAL DEFAULT 5.0"),
            ("items", "retrievability", "REAL DEFAULT 1.0"),
            ("items", "lapse_count", "INTEGER DEFAULT 0"),
            ("items", "pinned", "INTEGER DEFAULT 0"),
        ]
        for table, column, definition in migrations:
            ensure_column(conn, table, column, definition)
        current_version = db_user_version(conn)
        if current_version < 1:
            record_migration(conn, current_version, 1, "初始化 2.0 基础数据结构")
            current_version = 1
        if current_version < 2:
            record_migration(conn, current_version, 2, "加入长期维护元数据与可迁移 schema 版本")
            current_version = 2
        if current_version < 3:
            record_migration(conn, current_version, 3, "加入本地 Markdown 笔记与复习资料关联")
            current_version = 3
        set_db_user_version(conn, SCHEMA_VERSION)
        conn.execute(
            """
            INSERT INTO app_meta(key, value, updated_at)
            VALUES('schema_version', ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (str(SCHEMA_VERSION), iso_now()),
        )
        conn.execute(
            """
            INSERT INTO app_meta(key, value, updated_at)
            VALUES('app_version', ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (APP_VERSION, iso_now()),
        )
        conn.commit()


def normalize_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def is_probably_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def valid_file_ext(path: Path, config: dict) -> bool:
    exts = {ext.lower() for ext in config.get("scan_extensions", [])}
    return not exts or path.suffix.lower() in exts


def safe_filename(value: str, default: str = "note") -> str:
    cleaned = "".join(ch for ch in value.strip() if ch not in '<>:"/\\|?*')
    cleaned = " ".join(cleaned.split())
    return cleaned or default


def clean_note_title(value: str, default: str = "新建笔记") -> str:
    cleaned = " ".join(str(value or "").strip().split())
    return cleaned or default


def unique_file_path(base_dir: Path, title: str, ext: str = ".md", max_stem: int | None = None) -> Path:
    ext = ext if ext.startswith(".") else f".{ext}"
    stem = safe_filename(title, "note")
    if max_stem is not None:
        stem = stem[:max_stem]
    candidate = base_dir / f"{stem}{ext}"
    if not path_exists(candidate):
        return candidate
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = base_dir / f"{stem}_{stamp}{ext}"
    counter = 2
    while path_exists(candidate):
        candidate = base_dir / f"{stem}_{stamp}_{counter}{ext}"
        counter += 1
    return candidate


def unique_note_path(base_dir: Path, title: str, ext: str = ".md") -> Path:
    return unique_file_path(base_dir, title, ext, max_stem=None)


def unique_note_path_resilient(base_dir: Path, title: str, ext: str = ".md") -> Path:
    # First try the full user-visible title. Only shorten the file name when
    # the filesystem rejects the path or component length.
    candidates = [None, 240, 220, 200, 180, 160, 120, 90, 60, 36]
    last_error = None
    for max_stem in candidates:
        candidate = unique_file_path(base_dir, title, ext, max_stem=max_stem)
        try:
            ensure_dir(candidate.parent)
            with open(fs_path(candidate), "x", encoding="utf-8"):
                pass
            unlink_file(candidate)
            return candidate
        except FileExistsError:
            continue
        except OSError as exc:
            last_error = exc
    fallback = unique_file_path(base_dir, f"note_{uuid.uuid4().hex[:12]}", ext, max_stem=32)
    try:
        ensure_dir(fallback.parent)
        with open(fs_path(fallback), "x", encoding="utf-8"):
            pass
        unlink_file(fallback)
        return fallback
    except OSError:
        if last_error:
            raise last_error
        raise


def note_row_to_dict(row: sqlite3.Row) -> dict:
    path = Path(row["file_path"])
    exists = path_exists(path)
    return {
        "id": row["id"],
        "guid": row["guid"],
        "item_id": row["item_id"],
        "title": row["title"],
        "file_path": row["file_path"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "source": row["source"],
        "exists": exists,
        "size": human_size(path_stat(path).st_size) if exists else "0 B",
    }


def ensure_library(conn: sqlite3.Connection, root_path: str) -> int:
    now = iso_now()
    display_name = Path(root_path).name or root_path
    row = conn.execute("SELECT id FROM libraries WHERE root_path=?", (root_path,)).fetchone()
    if row:
        return int(row["id"])
    cur = conn.execute(
        "INSERT INTO libraries(root_path, display_name, added_at) VALUES(?, ?, ?)",
        (root_path, display_name, now),
    )
    return int(cur.lastrowid)


def upsert_item(conn: sqlite3.Connection, file_path: Path, root_path: str, library_id: int) -> str:
    now = iso_now()
    try:
        stat = path_stat(file_path)
    except OSError:
        return "skipped"
    try:
        relative = str(file_path.relative_to(Path(root_path)))
    except ValueError:
        relative = file_path.name
    modified_at = datetime.fromtimestamp(stat.st_mtime).replace(microsecond=0).isoformat()
    due_at = now if load_config()["scheduler"].get("new_item_due_immediately", True) else (
        datetime.now() + timedelta(days=1)
    ).replace(microsecond=0).isoformat()
    existing = conn.execute("SELECT id FROM items WHERE file_path=?", (str(file_path),)).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE items
               SET library_id=?, root_path=?, relative_path=?, file_name=?, ext=?,
                   size_bytes=?, modified_at=?, updated_at=?, last_seen_at=?
             WHERE id=?
            """,
            (
                library_id,
                root_path,
                relative,
                file_path.name,
                file_path.suffix.lower(),
                int(stat.st_size),
                modified_at,
                now,
                now,
                existing["id"],
            ),
        )
        return "updated"
    conn.execute(
        """
        INSERT INTO items(
            guid, library_id, root_path, relative_path, file_path, file_name, ext,
            size_bytes, modified_at, added_at, updated_at, last_seen_at, due_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            library_id,
            root_path,
            relative,
            str(file_path),
            file_path.name,
            file_path.suffix.lower(),
            int(stat.st_size),
            modified_at,
            now,
            now,
            now,
            due_at,
        ),
    )
    return "added"


def scan_library(root_path: str, config: dict | None = None) -> dict:
    config = config or load_config()
    root = Path(root_path).expanduser().resolve()
    if not path_exists(root) or not path_is_dir(root):
        raise ValueError(f"文件库路径不存在：{root}")
    ignore_dirs = set(config.get("ignore_dirs", []))
    follow_hidden = bool(config.get("follow_hidden_dirs", False))
    added = updated = skipped = scanned = 0
    with get_conn() as conn:
        library_id = ensure_library(conn, str(root))
        for dirpath, dirnames, filenames in os.walk(fs_path(root)):
            current = Path(user_path(dirpath))
            kept_dirs = []
            for dirname in dirnames:
                child = current / dirname
                if dirname in ignore_dirs:
                    continue
                if not follow_hidden and is_probably_hidden(child.relative_to(root)):
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in filenames:
                file_path = current / filename
                if not valid_file_ext(file_path, config):
                    skipped += 1
                    continue
                result = upsert_item(conn, file_path, str(root), library_id)
                scanned += 1
                if result == "added":
                    added += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1
        conn.execute(
            "UPDATE libraries SET last_scan_at=?, file_count=(SELECT COUNT(*) FROM items WHERE library_id=?) WHERE id=?",
            (iso_now(), library_id, library_id),
        )
        conn.commit()
    config_roots = [normalize_path(p) for p in config.get("library_roots", [])]
    if str(root) not in config_roots:
        config["library_roots"] = config_roots + [str(root)]
        save_config(config)
    return {
        "root_path": str(root),
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "scanned": scanned,
    }


def current_retrievability(row: sqlite3.Row, now: datetime | None = None) -> float:
    now = now or datetime.now()
    last_review = parse_dt(row["last_review_at"])
    if not last_review:
        return 1.0 if int(row["review_count"] or 0) == 0 else 0.75
    elapsed_days = max(0.0, (now - last_review).total_seconds() / 86400)
    stability = max(0.1, float(row["stability"] or 2.5))
    return clamp((1 + (19 / 81) * elapsed_days / stability) ** -0.5, 0.0, 1.0)


def interval_for_retention(stability: float, desired_retention: float) -> float:
    retention = clamp(float(desired_retention), 0.70, 0.97)
    factor = 19 / 81
    decay = -0.5
    interval = stability / factor * (retention ** (1 / decay) - 1)
    return clamp(interval, 0.01, 3650)


def schedule_fsrs_lite(row: sqlite3.Row, rating: int, config: dict) -> dict:
    now = datetime.now()
    desired = config["scheduler"].get("desired_retention", 0.9)
    stability = max(0.5, float(row["stability"] or 2.5))
    difficulty = clamp(float(row["difficulty"] or 5.0), 1.0, 10.0)
    old_interval = max(0.0, float(row["interval_days"] or 0))
    retrievability = current_retrievability(row, now)
    reviewed_before = int(row["review_count"] or 0) > 0

    if rating == 0:
        new_stability = max(0.35, stability * (0.42 + 0.08 * retrievability))
        difficulty = clamp(difficulty + 0.85, 1.0, 10.0)
        interval_days = 0.03 if reviewed_before else 0.02
        lapse_inc = 1
    elif rating == 1:
        new_stability = max(0.7, stability * (0.92 + 0.03 * (10 - difficulty)))
        difficulty = clamp(difficulty + 0.35, 1.0, 10.0)
        interval_days = max(1.0, min(max(old_interval * 1.2, 1.0), interval_for_retention(new_stability, desired) * 0.65))
        lapse_inc = 0
    elif rating == 3:
        boost = 2.40 + (10 - difficulty) * 0.10 + (1 - retrievability) * 0.30
        new_stability = stability * boost + 0.5
        difficulty = clamp(difficulty - 0.55, 1.0, 10.0)
        interval_days = interval_for_retention(new_stability, desired) * 1.25
        lapse_inc = 0
    else:
        boost = 1.70 + (10 - difficulty) * 0.07 + (1 - retrievability) * 0.20
        new_stability = stability * boost + 0.25
        difficulty = clamp(difficulty - 0.15, 1.0, 10.0)
        interval_days = interval_for_retention(new_stability, desired)
        lapse_inc = 0

    interval_days = clamp(interval_days, 0.02, 3650)
    due_at = now + timedelta(days=interval_days)
    return {
        "algorithm": "FSRS-Lite",
        "due_at": due_at.replace(microsecond=0).isoformat(),
        "interval_days": round(interval_days, 4),
        "ease_factor": float(row["ease_factor"] or 2.5),
        "stability": round(new_stability, 4),
        "difficulty": round(difficulty, 4),
        "retrievability": round(current_retrievability(row, now), 4),
        "lapse_inc": lapse_inc,
    }


def schedule_sm2(row: sqlite3.Row, rating: int, config: dict) -> dict:
    now = datetime.now()
    ease = max(1.3, float(row["ease_factor"] or 2.5))
    interval = max(0.0, float(row["interval_days"] or 0))
    if rating == 0:
        interval = 1
        ease = max(1.3, ease - 0.2)
        lapse_inc = 1
    elif rating == 1:
        interval = max(1, interval * 1.2)
        ease = max(1.3, ease - 0.15)
        lapse_inc = 0
    elif rating == 3:
        interval = 6 if interval < 1 else interval * ease * 1.3
        ease += 0.15
        lapse_inc = 0
    else:
        interval = 6 if interval < 1 else interval * ease
        lapse_inc = 0
    return {
        "algorithm": "SM-2",
        "due_at": (now + timedelta(days=interval)).replace(microsecond=0).isoformat(),
        "interval_days": round(interval, 4),
        "ease_factor": round(ease, 4),
        "stability": float(row["stability"] or interval or 2.5),
        "difficulty": float(row["difficulty"] or 5.0),
        "retrievability": current_retrievability(row, now),
        "lapse_inc": lapse_inc,
    }


def schedule_fixed(row: sqlite3.Row, rating: int, config: dict) -> dict:
    stages = [1, 2, 4, 8, 15, 30, 60, 120, 240, 365]
    review_count = int(row["review_count"] or 0)
    idx = min(review_count, len(stages) - 1)
    if rating == 0:
        idx = 0
        lapse_inc = 1
    elif rating == 3:
        idx = min(idx + 1, len(stages) - 1)
        lapse_inc = 0
    else:
        lapse_inc = 0
    interval = stages[idx]
    return {
        "algorithm": "Fixed",
        "due_at": (datetime.now() + timedelta(days=interval)).replace(microsecond=0).isoformat(),
        "interval_days": float(interval),
        "ease_factor": float(row["ease_factor"] or 2.5),
        "stability": float(interval),
        "difficulty": float(row["difficulty"] or 5.0),
        "retrievability": current_retrievability(row),
        "lapse_inc": lapse_inc,
    }


def calculate_schedule(row: sqlite3.Row, rating: int, config: dict) -> dict:
    algorithm = config.get("scheduler", {}).get("algorithm", "FSRS-Lite")
    if algorithm == "SM-2":
        return schedule_sm2(row, rating, config)
    if algorithm == "Fixed":
        return schedule_fixed(row, rating, config)
    return schedule_fsrs_lite(row, rating, config)


def row_item(row: sqlite3.Row) -> dict:
    now = datetime.now()
    due_at = parse_dt(row["due_at"]) or now
    review_count = int(row["review_count"] or 0)
    status = row["status"] or "active"
    exists = path_exists(row["file_path"])
    return {
        "id": row["id"],
        "guid": row["guid"],
        "library_id": row["library_id"],
        "root_path": row["root_path"],
        "relative_path": row["relative_path"],
        "file_path": row["file_path"],
        "file_name": row["file_name"],
        "ext": row["ext"],
        "size_bytes": row["size_bytes"],
        "size": human_size(row["size_bytes"]),
        "modified_at": row["modified_at"],
        "added_at": row["added_at"],
        "updated_at": row["updated_at"],
        "status": status,
        "tags": row["tags"] or "",
        "priority": int(row["priority"] or 0),
        "notes": row["notes"] or "",
        "due_at": row["due_at"],
        "due_label": due_at.strftime("%Y-%m-%d %H:%M"),
        "due_state": "new" if review_count == 0 else ("due" if due_at <= now else "future"),
        "interval_days": float(row["interval_days"] or 0),
        "ease_factor": float(row["ease_factor"] or 2.5),
        "stability": float(row["stability"] or 2.5),
        "difficulty": float(row["difficulty"] or 5.0),
        "retrievability": round(current_retrievability(row), 3),
        "review_count": review_count,
        "lapse_count": int(row["lapse_count"] or 0),
        "total_read_seconds": int(row["total_read_seconds"] or 0),
        "last_review_at": row["last_review_at"],
        "pinned": bool(row["pinned"]),
        "exists": exists,
        "preview_url": f"/api/file/{row['id']}",
    }


def get_overview() -> dict:
    now = iso_now()
    today = datetime.now().date().isoformat()
    with get_conn() as conn:
        stats = {
            "total": conn.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"],
            "active": conn.execute("SELECT COUNT(*) AS c FROM items WHERE status='active'").fetchone()["c"],
            "due": conn.execute(
                "SELECT COUNT(*) AS c FROM items WHERE status='active' AND due_at<=?", (now,)
            ).fetchone()["c"],
            "new": conn.execute(
                "SELECT COUNT(*) AS c FROM items WHERE status='active' AND review_count=0"
            ).fetchone()["c"],
            "suspended": conn.execute("SELECT COUNT(*) AS c FROM items WHERE status='suspended'").fetchone()["c"],
            "seconds": conn.execute("SELECT COALESCE(SUM(total_read_seconds),0) AS s FROM items").fetchone()["s"],
            "reviewed_today": conn.execute(
                "SELECT COUNT(*) AS c FROM review_history WHERE substr(ended_at,1,10)=?", (today,)
            ).fetchone()["c"],
            "seconds_today": conn.execute(
                "SELECT COALESCE(SUM(duration_seconds),0) AS s FROM review_history WHERE substr(ended_at,1,10)=?",
                (today,),
            ).fetchone()["s"],
        }
        due_rows = conn.execute(
            """
            SELECT * FROM items
             WHERE status='active' AND due_at<=?
             ORDER BY pinned DESC, due_at ASC, priority DESC, file_name ASC
             LIMIT 12
            """,
            (now,),
        ).fetchall()
        future = conn.execute(
            """
            SELECT substr(due_at, 1, 10) AS day, COUNT(*) AS count
              FROM items
             WHERE status='active'
             GROUP BY day
             ORDER BY day ASC
             LIMIT 21
            """
        ).fetchall()
        libraries = conn.execute("SELECT * FROM libraries ORDER BY display_name ASC").fetchall()
        history_dates = [
            row["day"]
            for row in conn.execute(
                "SELECT DISTINCT substr(ended_at,1,10) AS day FROM review_history ORDER BY day DESC LIMIT 120"
            ).fetchall()
        ]
    streak = 0
    cursor = datetime.now().date()
    date_set = set(history_dates)
    while cursor.isoformat() in date_set:
        streak += 1
        cursor -= timedelta(days=1)
    return {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            **profile_paths(),
        },
        "stats": {**stats, "streak": streak},
        "due_items": [row_item(row) for row in due_rows],
        "future_due": [dict(row) for row in future],
        "libraries": [dict(row) for row in libraries],
        "config": load_config(),
        "now": now,
    }


def query_items(params: dict) -> dict:
    search = (params.get("search") or [""])[0].strip()
    status = (params.get("status") or ["active"])[0]
    due = (params.get("due") or ["all"])[0]
    tag = (params.get("tag") or [""])[0].strip()
    library_id = (params.get("library_id") or [""])[0].strip()
    page = max(1, int((params.get("page") or ["1"])[0]))
    page_size = min(500, max(10, int((params.get("page_size") or ["80"])[0])))
    sort = (params.get("sort") or ["due_at"])[0]
    direction = (params.get("direction") or ["asc"])[0].lower()
    allowed_sort = {
        "file_name", "due_at", "added_at", "last_review_at", "review_count",
        "total_read_seconds", "priority", "size_bytes", "retrievability",
    }
    sort = sort if sort in allowed_sort else "due_at"
    direction = "DESC" if direction == "desc" else "ASC"
    clauses = []
    values: list = []
    if status != "all":
        clauses.append("status=?")
        values.append(status)
    if due == "due":
        clauses.append("due_at<=?")
        values.append(iso_now())
    elif due == "future":
        clauses.append("due_at>?")
        values.append(iso_now())
    elif due == "new":
        clauses.append("review_count=0")
    if tag:
        clauses.append("tags LIKE ?")
        values.append(f"%{tag}%")
    if library_id:
        clauses.append("library_id=?")
        values.append(library_id)
    if search:
        clauses.append("(file_name LIKE ? OR file_path LIKE ? OR tags LIKE ? OR notes LIKE ?)")
        values.extend([f"%{search}%"] * 4)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) AS c FROM items{where}", values).fetchone()["c"]
        rows = conn.execute(
            f"""
            SELECT * FROM items
            {where}
            ORDER BY pinned DESC, {sort} {direction}, id ASC
            LIMIT ? OFFSET ?
            """,
            values + [page_size, (page - 1) * page_size],
        ).fetchall()
    return {"items": [row_item(row) for row in rows], "total": total, "page": page, "page_size": page_size}


def choose_folder_dialog() -> str:
    global WEBVIEW_WINDOW
    if WEBVIEW_WINDOW is not None:
        try:
            import webview

            dialog_type = getattr(getattr(webview, "FileDialog", None), "FOLDER", None)
            if dialog_type is None:
                dialog_type = getattr(webview, "FOLDER_DIALOG", 20)
            result = WEBVIEW_WINDOW.create_file_dialog(
                dialog_type=dialog_type,
                directory=str(Path.home()),
                allow_multiple=False,
            )
            if isinstance(result, (list, tuple)):
                return str(result[0]) if result else ""
            return str(result or "")
        except Exception:
            log_error("WebView 文件夹选择失败，尝试 Tk 回退：\n" + traceback.format_exc())

    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    selected = filedialog.askdirectory(title="选择本地文件库")
    root.destroy()
    return selected


def choose_file_dialog(file_types: tuple[str, ...] = ("All files (*.*)",)) -> str:
    global WEBVIEW_WINDOW
    if WEBVIEW_WINDOW is not None:
        try:
            import webview

            dialog_type = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
            if dialog_type is None:
                dialog_type = getattr(webview, "OPEN_DIALOG", 10)
            result = WEBVIEW_WINDOW.create_file_dialog(
                dialog_type=dialog_type,
                directory=str(Path.home()),
                allow_multiple=False,
                file_types=file_types,
            )
            if isinstance(result, (list, tuple)):
                return str(result[0]) if result else ""
            return str(result or "")
        except Exception:
            log_error("WebView 文件选择失败，尝试 Tk 回退：\n" + traceback.format_exc())

    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    selected = filedialog.askopenfilename(title="选择迁移包", filetypes=[("Zip files", "*.zip"), ("All files", "*.*")])
    root.destroy()
    return selected


def open_path(path: str) -> None:
    target = user_path(path)
    if platform.system() == "Windows":
        os.startfile(target)  # type: ignore[attr-defined]
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


def open_with_dialog(path: str) -> None:
    target = user_path(path)
    if platform.system() == "Windows":
        subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", target])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", "-a", "Finder", target])
    else:
        subprocess.Popen(["xdg-open", target])


def open_parent(path: str) -> None:
    target = user_path(path)
    parent = str(Path(target).parent)
    if platform.system() == "Windows":
        subprocess.Popen(["explorer", "/select,", target])
    else:
        open_path(parent)


def start_review(item_id: int | None = None) -> dict:
    with get_conn() as conn:
        if item_id:
            row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        else:
            row = conn.execute(
                """
                SELECT * FROM items
                 WHERE status='active' AND due_at<=?
                 ORDER BY pinned DESC, due_at ASC, priority DESC, file_name ASC
                 LIMIT 1
                """,
                (iso_now(),),
            ).fetchone()
        if not row:
            return {"item": None, "session_id": None}
        session_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO review_sessions(id, item_id, started_at) VALUES(?, ?, ?)",
            (session_id, row["id"], iso_now()),
        )
        conn.commit()
    config = load_config()
    if config.get("review", {}).get("auto_open_file", False) and path_exists(row["file_path"]):
        try:
            open_path(row["file_path"])
        except Exception:
            log_error("打开文件失败：\n" + traceback.format_exc())
    return {"item": row_item(row), "session_id": session_id}


def finish_review(payload: dict) -> dict:
    item_id = int(payload["item_id"])
    rating = int(payload.get("rating", 2))
    rating = max(0, min(3, rating))
    session_id = payload.get("session_id")
    client_duration = int(payload.get("duration_seconds") or 0)
    now = iso_now()
    config = load_config()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        if not row:
            raise ValueError("复习项目不存在")
        started_at = None
        if session_id:
            session = conn.execute("SELECT * FROM review_sessions WHERE id=?", (session_id,)).fetchone()
            if session:
                started_at = session["started_at"]
        started_dt = parse_dt(started_at)
        duration = client_duration
        if started_dt:
            duration = max(duration, int((datetime.now() - started_dt).total_seconds()))
        schedule = calculate_schedule(row, rating, config)
        conn.execute(
            """
            UPDATE items
               SET due_at=?, interval_days=?, ease_factor=?, stability=?, difficulty=?,
                   retrievability=?, review_count=review_count+1,
                   lapse_count=lapse_count+?, total_read_seconds=total_read_seconds+?,
                   last_review_at=?, updated_at=?
             WHERE id=?
            """,
            (
                schedule["due_at"],
                schedule["interval_days"],
                schedule["ease_factor"],
                schedule["stability"],
                schedule["difficulty"],
                schedule["retrievability"],
                schedule["lapse_inc"],
                duration,
                now,
                now,
                item_id,
            ),
        )
        if session_id:
            conn.execute("UPDATE review_sessions SET ended_at=? WHERE id=?", (now, session_id))
        conn.execute(
            """
            INSERT INTO review_history(
                item_id, session_id, started_at, ended_at, duration_seconds, rating,
                rating_label, algorithm, scheduled_days, ease_factor, stability,
                difficulty, retrievability
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                session_id,
                started_at,
                now,
                duration,
                rating,
                RATING_LABELS[rating],
                schedule["algorithm"],
                schedule["interval_days"],
                schedule["ease_factor"],
                schedule["stability"],
                schedule["difficulty"],
                schedule["retrievability"],
            ),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    return {"item": row_item(updated), "schedule": schedule, "duration_seconds": duration}


def update_items(payload: dict) -> dict:
    ids = [int(i) for i in payload.get("ids", [])]
    if not ids:
        raise ValueError("没有选择文件")
    fields = payload.get("fields", {})
    allowed = {"tags", "status", "priority", "notes", "pinned", "due_at"}
    assignments = []
    values = []
    for key, value in fields.items():
        if key in allowed:
            if key == "due_at" and isinstance(value, str) and value.endswith("Z"):
                value = value[:-1]
            assignments.append(f"{key}=?")
            values.append(value)
    if not assignments:
        return {"updated": 0}
    assignments.append("updated_at=?")
    values.append(iso_now())
    placeholders = ",".join(["?"] * len(ids))
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE items SET {', '.join(assignments)} WHERE id IN ({placeholders})",
            values + ids,
        )
        conn.commit()
    return {"updated": cur.rowcount}


def delete_items(payload: dict) -> dict:
    ids = [int(i) for i in payload.get("ids", [])]
    if not ids:
        raise ValueError("没有选择文件")
    placeholders = ",".join(["?"] * len(ids))
    with get_conn() as conn:
        cur = conn.execute(f"DELETE FROM items WHERE id IN ({placeholders})", ids)
        conn.commit()
    return {"deleted": cur.rowcount}


def note_rows_by_ids(conn: sqlite3.Connection, ids: list[int]) -> list[sqlite3.Row]:
    if not ids:
        return []
    placeholders = ",".join(["?"] * len(ids))
    return conn.execute(f"SELECT * FROM notes WHERE id IN ({placeholders})", ids).fetchall()


def list_notes(item_id: int | None = None) -> dict:
    where = ""
    values: list = []
    if item_id:
        where = "WHERE item_id=?"
        values.append(item_id)
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM notes {where} ORDER BY updated_at DESC, id DESC LIMIT 300",
            values,
        ).fetchall()
    return {"notes": [note_row_to_dict(row) for row in rows], "notes_dir": str(ensure_notes_dir())}


def read_note(note_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not row:
        raise ValueError("笔记不存在")
    note = note_row_to_dict(row)
    path = Path(note["file_path"])
    note["content"] = read_text_file(path) if path_exists(path) else ""
    return {"note": note}


def create_note(payload: dict) -> dict:
    config = load_config()
    base_dir = ensure_notes_dir(config)
    item_id = payload.get("item_id")
    item_id = int(item_id) if item_id else None
    title = clean_note_title(payload.get("title") or "新建笔记", "新建笔记")
    ext = config.get("notes", {}).get("default_extension", ".md") or ".md"
    now = iso_now()
    linked_line = ""
    if item_id:
        with get_conn() as conn:
            item = conn.execute("SELECT file_name, file_path FROM items WHERE id=?", (item_id,)).fetchone()
        if item:
            if title == "新建笔记" or "复习笔记" not in title:
                title = f"{item['file_name']} 复习笔记"
            linked_line = f"\n关联资料：{item['file_name']}\n路径：{item['file_path']}\n"
    path = unique_note_path_resilient(base_dir, title, ext)
    content = payload.get("content")
    if content is None:
        content = f"# {title}\n\n创建时间：{now}{linked_line}\n"
    write_text_file(path, content)
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO notes(guid, item_id, title, file_path, created_at, updated_at, source)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), item_id, title, str(path), now, now, payload.get("source") or "app"),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id=?", (cur.lastrowid,)).fetchone()
    if payload.get("open_local"):
        open_parent(str(path))
    return {"note": note_row_to_dict(row)}


def save_note(payload: dict) -> dict:
    note_id = int(payload["id"])
    content = payload.get("content", "")
    title = clean_note_title(payload.get("title") or "未命名笔记", "未命名笔记")
    now = iso_now()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        if not row:
            raise ValueError("笔记不存在")
        path = Path(row["file_path"])
        write_text_file(path, content)
        conn.execute("UPDATE notes SET title=?, updated_at=? WHERE id=?", (title, now, note_id))
        conn.commit()
        updated = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    return {"note": note_row_to_dict(updated)}


def open_note(note_id: int, choose_app: bool = False) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not row:
        raise ValueError("笔记不存在")
    path = row["file_path"]
    if choose_app:
        open_with_dialog(path)
    else:
        open_path(path)
    return {"ok": True}


def delete_notes(payload: dict) -> dict:
    ids = [int(i) for i in payload.get("ids", [])]
    if not ids:
        raise ValueError("没有选择笔记")
    delete_files = bool(payload.get("delete_files", True))
    deleted_files = 0
    missing_files = 0
    errors: list[str] = []
    with get_conn() as conn:
        rows = note_rows_by_ids(conn, ids)
        for row in rows:
            path = Path(row["file_path"])
            if delete_files:
                try:
                    if path_exists(path) and path_is_file(path):
                        unlink_file(path)
                        deleted_files += 1
                    else:
                        missing_files += 1
                except Exception as exc:
                    errors.append(f"{path}: {exc}")
        placeholders = ",".join(["?"] * len(ids))
        cur = conn.execute(f"DELETE FROM notes WHERE id IN ({placeholders})", ids)
        conn.commit()
    return {
        "deleted": cur.rowcount,
        "deleted_files": deleted_files,
        "missing_files": missing_files,
        "errors": errors,
    }


def export_notes(payload: dict) -> dict:
    ids = [int(i) for i in payload.get("ids", [])]
    if not ids:
        raise ValueError("没有选择笔记")
    target_dir = ensure_export_dir(target_dir=payload.get("target_dir") or None)
    copied = 0
    missing = 0
    exported: list[str] = []
    with get_conn() as conn:
        rows = note_rows_by_ids(conn, ids)
    for row in rows:
        src = Path(row["file_path"])
        if not path_exists(src) or not path_is_file(src):
            missing += 1
            continue
        target = target_dir / src.name
        if path_exists(target):
            target = unique_note_path(target_dir, target.stem, target.suffix)
        copy_file(src, target)
        copied += 1
        exported.append(str(target))
    return {"export_dir": str(target_dir), "exported": copied, "missing": missing, "files": exported}


def repair_imported_note_paths() -> None:
    ensure_notes_dir()
    with get_conn() as conn:
        rows = conn.execute("SELECT id, file_path FROM notes").fetchall()
        for row in rows:
            original = Path(row["file_path"])
            candidate = DEFAULT_NOTES_DIR / original.name
            if path_exists(candidate):
                conn.execute("UPDATE notes SET file_path=? WHERE id=?", (str(candidate), row["id"]))
        conn.commit()


def tree_for_library(library_id: int, rel: str = "") -> dict:
    with get_conn() as conn:
        library = conn.execute("SELECT * FROM libraries WHERE id=?", (library_id,)).fetchone()
        if not library:
            raise ValueError("文件库不存在")
        root = Path(library["root_path"]).resolve()
        target = (root / rel).resolve()
        if not str(target).lower().startswith(str(root).lower()):
            raise ValueError("路径越界")
        indexed = {
            row["file_path"]: row["id"]
            for row in conn.execute("SELECT id, file_path FROM items WHERE library_id=?", (library_id,)).fetchall()
        }
    children = []
    if path_exists(target) and path_is_dir(target):
        for child in target.iterdir():
            try:
                stat = path_stat(child)
            except OSError:
                continue
            children.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "rel": str(child.relative_to(root)),
                    "is_dir": path_is_dir(child),
                    "size": human_size(stat.st_size if path_is_file(child) else 0),
                    "ext": child.suffix.lower(),
                    "indexed_id": indexed.get(str(child)),
                }
            )
    children.sort(key=lambda node: (not node["is_dir"], node["name"].lower()))
    return {"library": dict(library), "rel": rel, "children": children}


def backup_database(target_dir: str | Path | None = None) -> dict:
    target = backup_sqlite_database_to(DB_PATH, ensure_export_dir(target_dir=target_dir), "manual") if target_dir else backup_sqlite_database(DB_PATH, "manual")
    return {"backup_path": str(target)}


def export_csv(target_dir: str | Path | None = None) -> Path:
    target_root = ensure_export_dir(target_dir=target_dir)
    target = target_root / f"review_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with get_conn() as conn, open(fs_path(target), "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "file_name", "file_path", "tags", "status", "due_at",
            "review_count", "lapse_count", "total_read_seconds", "last_review_at",
        ])
        for row in conn.execute("SELECT * FROM items ORDER BY file_name ASC"):
            writer.writerow([
                row["file_name"], row["file_path"], row["tags"], row["status"], row["due_at"],
                row["review_count"], row["lapse_count"], row["total_read_seconds"], row["last_review_at"],
            ])
    return target


def export_portable_json(target_dir: str | Path | None = None) -> Path:
    target_root = ensure_export_dir(target_dir=target_dir)
    target = target_root / f"review_portable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with get_conn() as conn:
        payload = {
            "format": "LiFileReviewerPortable",
            "format_version": 1,
            "exported_at": iso_now(),
            "app_version": APP_VERSION,
            "schema_version": db_user_version(conn),
            "config": load_config(),
            "libraries": [dict(row) for row in conn.execute("SELECT * FROM libraries ORDER BY id")],
            "items": [dict(row) for row in conn.execute("SELECT * FROM items ORDER BY id")],
            "review_history": [
                dict(row) for row in conn.execute("SELECT * FROM review_history ORDER BY id")
            ],
            "schema_migrations": [
                dict(row) for row in conn.execute("SELECT * FROM schema_migrations ORDER BY id")
            ],
        }
    write_text_file(target, json.dumps(payload, ensure_ascii=False, indent=2))
    return target


def export_profile_package(target_dir: str | Path | None = None) -> Path:
    ensure_app_dirs()
    target_root = ensure_export_dir(target_dir=target_dir)
    target = target_root / f"LiFileReviewer2_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    included: list[tuple[Path, str]] = []
    for path in [CONFIG_PATH, LOG_PATH]:
        if path_exists(path):
            included.append((path, path.name))
    if path_exists(DB_PATH):
        backup_path = backup_sqlite_database(DB_PATH, "profile_export")
        included.append((backup_path, DB_PATH.name))
    for folder, arc_prefix in [(BACKUP_DIR, "backups"), (PLUGINS_DIR, "plugins"), (ensure_notes_dir(), "notes")]:
        if path_exists(folder):
            for file_path in folder.rglob("*"):
                if path_is_file(file_path):
                    included.append((file_path, str(Path(arc_prefix) / file_path.relative_to(folder))))
    with zipfile.ZipFile(fs_path(target), "w", compression=zipfile.ZIP_DEFLATED) as archive:
        manifest = {
            "format": "LiFileReviewerProfile",
            "format_version": 1,
            "exported_at": iso_now(),
            "app_version": APP_VERSION,
            "source_app_dir": str(APP_DIR),
        }
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        seen = set()
        for src, arcname in included:
            if arcname in seen or src.resolve() == target.resolve() or src.suffix.lower() == ".zip":
                continue
            seen.add(arcname)
            archive.write(fs_path(src), arcname)
    return target


def import_profile_package(package_path: str) -> dict:
    package = Path(package_path).expanduser().resolve()
    if not path_exists(package) or not path_is_file(package):
        raise ValueError(f"迁移包不存在：{package}")
    ensure_app_dirs()
    backup = export_profile_package()
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp_dir = Path(tmp_name)
        with zipfile.ZipFile(fs_path(package), "r") as archive:
            names = archive.namelist()
            if "manifest.json" not in names:
                raise ValueError("这不是有效的 LiFileReviewer 迁移包")
            for name in names:
                normalized = Path(name)
                if normalized.is_absolute() or ".." in normalized.parts:
                    raise ValueError(f"迁移包包含不安全路径：{name}")
            archive.extractall(tmp_dir)
        for name in ["config.json", "review_data.sqlite", "app.log"]:
            src = tmp_dir / name
            if path_exists(src):
                copy_file(src, APP_DIR / name)
        for folder_name in ["backups", "plugins", "notes"]:
            src_dir = tmp_dir / folder_name
            dst_dir = APP_DIR / folder_name
            if path_exists(src_dir):
                ensure_dir(dst_dir)
                for src in src_dir.rglob("*"):
                    if path_is_file(src):
                        dst = dst_dir / src.relative_to(src_dir)
                        copy_file(src, dst)
    config = load_config()
    config.setdefault("notes", {})["storage_dir"] = ""
    config.setdefault("exports", {})["default_dir"] = ""
    save_config(config)
    init_db()
    repair_imported_note_paths()
    return {"imported_from": str(package), "backup_before_import": str(backup), "app": profile_paths()}


def move_profile_dir(target_dir: str) -> dict:
    global APP_DIR
    requested_dir = Path(target_dir).expanduser().resolve()
    new_dir = requested_dir
    if not str(new_dir):
        raise ValueError("缺少新的配置目录")
    old_dir = APP_DIR.resolve()
    if new_dir == old_dir:
        return {"moved": False, "app": profile_paths()}
    if old_dir in new_dir.parents:
        raise ValueError("新的配置目录不能放在当前配置目录内部")
    ensure_app_dirs()
    ensure_dir(new_dir)
    allowed = {
        "backups", "plugins", "notes", "exports", "README.md", "profile_location.json",
        "config.json", "review_data.sqlite", "app.log", "last_health_check.json", "runtime.json",
    }
    if any(new_dir.iterdir()):
        if path_exists(new_dir / "config.json") or path_exists(new_dir / "review_data.sqlite"):
            unexpected = [path.name for path in new_dir.iterdir() if path.name not in allowed]
            if unexpected:
                raise ValueError("目标目录已有其它文件，请选择空文件夹、已有软件数据目录，或它下面的专用文件夹")
        else:
            new_dir = new_dir / "LiFileReviewer2"
            if new_dir == old_dir or old_dir in new_dir.parents:
                raise ValueError("新的配置目录不能放在当前配置目录内部")
            ensure_dir(new_dir)
            if any(new_dir.iterdir()):
                unexpected = [path.name for path in new_dir.iterdir() if path.name not in allowed]
                if unexpected:
                    raise ValueError("目标目录下的 LiFileReviewer2 子目录已有其它文件，请选择空文件夹或专用配置文件夹")
    for item in old_dir.iterdir():
        if item.resolve() == PROFILE_POINTER_PATH.resolve():
            continue
        destination = new_dir / item.name
        if path_exists(destination):
            continue
        shutil.move(fs_path(item), fs_path(destination))
    set_app_dir(new_dir)
    ensure_app_dirs()
    write_profile_pointer()
    pointer_inside_profile = APP_DIR / "profile_location.json"
    write_text_file(
        pointer_inside_profile,
        json.dumps({"app_dir": str(APP_DIR), "updated_at": iso_now(), "app_version": APP_VERSION}, ensure_ascii=False, indent=2),
    )
    init_db()
    return {"moved": True, "requested_dir": str(requested_dir), "app": profile_paths()}


def list_plugins() -> dict:
    ensure_app_dirs()
    plugins = []
    for entry in sorted(PLUGINS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not path_is_dir(entry):
            continue
        manifest = entry / "plugin.json"
        data = {
            "id": entry.name,
            "name": entry.name,
            "version": "",
            "enabled": False,
            "path": str(entry),
            "has_manifest": path_exists(manifest),
        }
        if path_exists(manifest):
            try:
                payload = json.loads(read_text_file(manifest))
                data.update({key: payload.get(key, data.get(key)) for key in ["id", "name", "version", "description"]})
                data["enabled"] = bool(payload.get("enabled", False))
            except Exception:
                data["error"] = "plugin.json 读取失败"
        plugins.append(data)
    return {"plugins": plugins, "plugins_dir": str(PLUGINS_DIR)}


def health_check() -> dict:
    ensure_app_dirs()
    load_config()
    checks = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    add("数据目录", path_exists(APP_DIR) and os.access(fs_path(APP_DIR), os.W_OK), str(APP_DIR))
    add("配置文件", path_exists(CONFIG_PATH), str(CONFIG_PATH))
    add("数据库文件", path_exists(DB_PATH), str(DB_PATH))
    add("插件目录", path_exists(PLUGINS_DIR) and os.access(fs_path(PLUGINS_DIR), os.W_OK), str(PLUGINS_DIR))
    add("笔记目录", path_exists(ensure_notes_dir()) and os.access(fs_path(ensure_notes_dir()), os.W_OK), str(ensure_notes_dir()))
    add("WebUI 资源", path_exists(resource_path("web/index.html")), str(resource_path("web/index.html")))

    try:
        with get_conn() as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            foreign_keys = conn.execute("PRAGMA foreign_key_check").fetchall()
            version = db_user_version(conn)
            item_count = conn.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"]
            missing_count = 0
            for row in conn.execute("SELECT file_path FROM items WHERE status!='done'").fetchall():
                if not path_exists(row["file_path"]):
                    missing_count += 1
        add("SQLite 完整性", integrity == "ok", integrity)
        add("外键一致性", len(foreign_keys) == 0, f"{len(foreign_keys)} 个外键问题")
        add("Schema 版本", version == SCHEMA_VERSION, f"当前 {version}，程序需要 {SCHEMA_VERSION}")
        add("索引记录", True, f"{item_count} 条资料记录")
        add("原始文件可见性", missing_count == 0, f"{missing_count} 个索引文件当前不可访问")
    except Exception as exc:
        add("数据库读取", False, str(exc))

    ok = all(check["ok"] for check in checks)
    report = {
        "ok": ok,
        "checked_at": iso_now(),
        "app_version": APP_VERSION,
        "schema_version": SCHEMA_VERSION,
        "checks": checks,
    }
    report_path = APP_DIR / "last_health_check.json"
    write_text_file(report_path, json.dumps(report, ensure_ascii=False, indent=2))
    report["report_path"] = str(report_path)
    return report


class AppHandler(BaseHTTPRequestHandler):
    server_version = "LiFileReviewer/2.0"

    def log_message(self, fmt: str, *args) -> None:
        log_error(fmt % args)

    def send_json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def serve_static(self, request_path: str) -> None:
        web_dir = resource_path("web")
        if request_path == "/":
            target = web_dir / "index.html"
        else:
            safe = request_path.lstrip("/")
            if safe.startswith("web/"):
                safe = safe[4:]
            target = (web_dir / safe).resolve()
            if os.path.commonpath([str(web_dir.resolve()), str(target)]) != str(web_dir.resolve()):
                self.send_error(403)
                return
        if not path_exists(target) or not path_is_file(target):
            self.send_error(404)
            return
        mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        with open(fs_path(target), "rb") as handle:
            data = handle.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        try:
            if path == "/api/health":
                self.send_json(health_check())
            elif path == "/api/overview":
                self.send_json(get_overview())
            elif path == "/api/items":
                self.send_json(query_items(params))
            elif path == "/api/libraries":
                with get_conn() as conn:
                    rows = conn.execute("SELECT * FROM libraries ORDER BY display_name ASC").fetchall()
                self.send_json({"libraries": [dict(row) for row in rows]})
            elif path == "/api/tree":
                library_id = int((params.get("library_id") or ["0"])[0])
                rel = (params.get("rel") or [""])[0]
                self.send_json(tree_for_library(library_id, rel))
            elif path == "/api/settings":
                self.send_json({"config": load_config(), "paths": get_overview()["app"]})
            elif path == "/api/common-paths":
                self.send_json({
                    "paths": [
                        {"label": "Documents", "path": str(user_documents_dir())},
                        {"label": "Desktop", "path": str(Path.home() / "Desktop")},
                        {"label": "Downloads", "path": str(Path.home() / "Downloads")},
                        {"label": "Home", "path": str(Path.home())},
                        {"label": "Current data folder", "path": str(APP_DIR)},
                    ]
                })
            elif path == "/api/plugins":
                self.send_json(list_plugins())
            elif path == "/api/notes":
                item_id = (params.get("item_id") or [""])[0]
                self.send_json(list_notes(int(item_id) if item_id else None))
            elif path.startswith("/api/notes/"):
                note_id = int(path.rsplit("/", 1)[1])
                self.send_json(read_note(note_id))
            elif path.startswith("/api/history/"):
                item_id = int(path.rsplit("/", 1)[1])
                with get_conn() as conn:
                    rows = conn.execute(
                        "SELECT * FROM review_history WHERE item_id=? ORDER BY ended_at DESC LIMIT 120",
                        (item_id,),
                    ).fetchall()
                self.send_json({"history": [dict(row) for row in rows]})
            elif path.startswith("/api/file/"):
                item_id = int(path.rsplit("/", 1)[1])
                self.serve_file(item_id)
            elif path == "/api/export":
                target = export_csv()
                self.send_json({"export_path": str(target)})
            elif path == "/api/export-portable":
                target = export_portable_json()
                self.send_json({"export_path": str(target)})
            elif path == "/api/export-profile":
                target = export_profile_package()
                self.send_json({"export_path": str(target)})
            elif path == "/" or path.startswith("/web/") or path in ["/style.css", "/app.js"]:
                self.serve_static(path)
            else:
                self.send_error(404)
        except Exception as exc:
            log_error("GET 处理失败：\n" + traceback.format_exc())
            self.send_json({"error": str(exc)}, 500)

    def serve_file(self, item_id: int) -> None:
        with get_conn() as conn:
            row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        if not row:
            self.send_error(404)
            return
        file_path = Path(row["file_path"])
        if not path_exists(file_path) or not path_is_file(file_path):
            self.send_error(404)
            return
        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Disposition", f"inline; filename*=UTF-8''{urllib.parse.quote(file_path.name)}")
        self.send_header("Content-Length", str(path_stat(file_path).st_size))
        self.end_headers()
        with open(fs_path(file_path), "rb") as handle:
            shutil.copyfileobj(handle, self.wfile)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            payload = self.read_json()
            if path == "/api/libraries/select":
                selected = choose_folder_dialog()
                if not selected:
                    self.send_json({"cancelled": True})
                    return
                result = scan_library(selected)
                self.send_json({"cancelled": False, "scan": result})
            elif path == "/api/libraries/add":
                root_path = payload.get("path")
                if not root_path:
                    raise ValueError("缺少文件库路径")
                result = scan_library(root_path)
                self.send_json({"scan": result})
            elif path == "/api/profile/select":
                selected = choose_folder_dialog()
                if not selected:
                    self.send_json({"cancelled": True})
                    return
                self.send_json({"cancelled": False, "path": selected})
            elif path == "/api/export/select-dir":
                selected = choose_folder_dialog()
                if not selected:
                    self.send_json({"cancelled": True})
                    return
                self.send_json({"cancelled": False, "path": selected})
            elif path == "/api/profile/select-package":
                selected = choose_file_dialog(("Zip files (*.zip)", "All files (*.*)"))
                if not selected:
                    self.send_json({"cancelled": True})
                    return
                self.send_json({"cancelled": False, "path": selected})
            elif path == "/api/libraries/scan":
                root_path = payload.get("path")
                if root_path:
                    self.send_json({"scan": scan_library(root_path)})
                else:
                    config = load_config()
                    scans = [scan_library(path, config) for path in config.get("library_roots", [])]
                    self.send_json({"scans": scans})
            elif path == "/api/items/open":
                with get_conn() as conn:
                    row = conn.execute("SELECT file_path FROM items WHERE id=?", (int(payload["id"]),)).fetchone()
                if not row:
                    raise ValueError("文件不存在")
                open_path(row["file_path"])
                self.send_json({"ok": True})
            elif path == "/api/items/open-with":
                with get_conn() as conn:
                    row = conn.execute("SELECT file_path FROM items WHERE id=?", (int(payload["id"]),)).fetchone()
                if not row:
                    raise ValueError("文件不存在")
                open_with_dialog(row["file_path"])
                self.send_json({"ok": True})
            elif path == "/api/items/open-folder":
                with get_conn() as conn:
                    row = conn.execute("SELECT file_path FROM items WHERE id=?", (int(payload["id"]),)).fetchone()
                if not row:
                    raise ValueError("文件不存在")
                open_parent(row["file_path"])
                self.send_json({"ok": True})
            elif path == "/api/path/open":
                target = payload.get("path")
                if not target:
                    raise ValueError("缺少路径")
                resolved = Path(target).expanduser().resolve()
                if not path_exists(resolved):
                    raise ValueError(f"路径不存在：{resolved}")
                if resolved == PROFILE_POINTER_PATH.resolve():
                    raise ValueError("位置指针是内部启动定位文件，不能直接打开")
                open_path(str(resolved))
                self.send_json({"ok": True})
            elif path == "/api/items/update":
                self.send_json(update_items(payload))
            elif path == "/api/items/delete":
                self.send_json(delete_items(payload))
            elif path == "/api/notes/create":
                self.send_json(create_note(payload))
            elif path == "/api/notes/save":
                self.send_json(save_note(payload))
            elif path == "/api/notes/open":
                self.send_json(open_note(int(payload["id"]), bool(payload.get("choose_app"))))
            elif path == "/api/notes/delete":
                self.send_json(delete_notes(payload))
            elif path == "/api/notes/export":
                self.send_json(export_notes(payload))
            elif path == "/api/review/start":
                self.send_json(start_review(payload.get("item_id")))
            elif path == "/api/review/finish":
                self.send_json(finish_review(payload))
            elif path == "/api/settings":
                incoming = payload.get("config", {})
                config = deep_merge(load_config(), incoming)
                save_config(config)
                self.send_json({"config": config})
            elif path == "/api/profile/move":
                target_dir = payload.get("path")
                if not target_dir:
                    raise ValueError("缺少新的配置目录")
                self.send_json(move_profile_dir(target_dir))
            elif path == "/api/profile/import":
                package_path = payload.get("path")
                if not package_path:
                    raise ValueError("缺少迁移包路径")
                self.send_json(import_profile_package(package_path))
            elif path == "/api/backup":
                self.send_json(backup_database(payload.get("target_dir") or None))
            elif path == "/api/export":
                target = export_csv(payload.get("target_dir") or None)
                self.send_json({"export_path": str(target)})
            elif path == "/api/export-portable":
                target = export_portable_json(payload.get("target_dir") or None)
                self.send_json({"export_path": str(target)})
            elif path == "/api/export-profile":
                target = export_profile_package(payload.get("target_dir") or None)
                self.send_json({"export_path": str(target)})
            elif path == "/api/health":
                self.send_json(health_check())
            else:
                self.send_error(404)
        except Exception as exc:
            log_error("POST 处理失败：\n" + traceback.format_exc())
            self.send_json({"error": str(exc)}, 500)


def find_port(preferred: int) -> int:
    for port in [preferred] + list(range(preferred + 1, preferred + 50)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("没有找到可用端口")


def write_runtime_info(port: int) -> None:
    ensure_app_dirs()
    info = {"url": f"http://127.0.0.1:{port}", "port": port, "started_at": iso_now(), "pid": os.getpid()}
    write_text_file(APP_DIR / "runtime.json", json.dumps(info, ensure_ascii=False, indent=2))


def start_server(port: int) -> tuple[ThreadingHTTPServer, str]:
    chosen_port = find_port(port)
    write_runtime_info(chosen_port)
    server = ThreadingHTTPServer(("127.0.0.1", chosen_port), AppHandler)
    url = f"http://127.0.0.1:{chosen_port}"
    return server, url


def run_server_until_stopped(server: ThreadingHTTPServer) -> None:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def launch_desktop_window(url: str, server: ThreadingHTTPServer) -> bool:
    global WEBVIEW_WINDOW
    try:
        import webview
    except Exception:
        log_error("pywebview 不可用，退回浏览器模式：\n" + traceback.format_exc())
        return False

    WEBVIEW_WINDOW = webview.create_window(
        APP_NAME,
        url,
        width=1240,
        height=820,
        min_size=(980, 640),
        confirm_close=True,
    )

    def on_closed() -> None:
        try:
            server.shutdown()
        except Exception:
            log_error("关闭内置服务失败：\n" + traceback.format_exc())

    try:
        WEBVIEW_WINDOW.events.closed += on_closed
    except Exception:
        pass

    webview.start(debug=False)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--browser", action="store_true", help="使用系统浏览器打开，主要用于调试")
    parser.add_argument("--no-window", action="store_true", help="只启动本地服务，不打开桌面窗口")
    parser.add_argument("--health-check", action="store_true", help="运行数据库和资源体检后退出")
    parser.add_argument("--backup", action="store_true", help="备份数据库后退出")
    parser.add_argument("--export-portable", action="store_true", help="导出可移植 JSON 后退出")
    parser.add_argument("--export-profile", action="store_true", help="导出一键迁移配置包后退出")
    args = parser.parse_args()

    ensure_app_dirs()
    init_db()
    if args.health_check:
        print(json.dumps(health_check(), ensure_ascii=False, indent=2))
        return
    if args.backup:
        print(json.dumps(backup_database(), ensure_ascii=False, indent=2))
        return
    if args.export_portable:
        print(json.dumps({"export_path": str(export_portable_json())}, ensure_ascii=False, indent=2))
        return
    if args.export_profile:
        print(json.dumps({"export_path": str(export_profile_package())}, ensure_ascii=False, indent=2))
        return
    config = load_config()
    for root_path in config.get("library_roots", []):
        with get_conn() as conn:
            ensure_library(conn, normalize_path(root_path))
            conn.commit()

    server, url = start_server(args.port)
    print(f"{APP_NAME} 已启动：{url}")
    if args.no_window:
        run_server_until_stopped(server)
        return

    if args.browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        run_server_until_stopped(server)
        return

    if args.no_browser:
        run_server_until_stopped(server)
        return

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    launched = launch_desktop_window(url, server)
    if not launched:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        run_server_until_stopped(server)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log_error("程序启动失败：\n" + traceback.format_exc())
        raise
