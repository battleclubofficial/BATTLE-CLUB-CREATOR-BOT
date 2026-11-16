# -*- coding: utf-8 -*-
"""
BATTLE CLUB TELEGRAM BOT - HIGH-CONCURRENCY SQLITE WAL DATABASE ENGINE (ENTERPRISE v9.0)
- Safe SQLite Write-Ahead Logging (WAL) + Persistent Journal Enforcement (Never falls back to MEMORY journal)
- Verified Online Backup API (`PRAGMA integrity_check` result explicitly verified == 'ok')
- Legacy Ledger Duplicate `idempotency_key` Reconciliation + Database-Level UNIQUE Index Enforcement
- Explicit `BEGIN IMMEDIATE` Atomic Write Transaction Context Manager (`begin_immediate_transaction`)
- Advanced Custom Button Engine:
  * Collision-Free UUID/CSPRNG Button ID Generation (Never overwrites existing IDs)
  * Original Layout, Row Index & Column Position Tracking (`button_original_placements`)
  * Exact Position Restoration on Sub-Button Removal or Custom Container Deletion
  * Circular Reference / Infinite Navigation Cycle Detector (`would_create_container_cycle`)
  * Orphan Layout & Dynamic Message Garbage Collector (`cleanup_orphan_custom_layouts_and_messages`)
- External Traffic Link History & Active/Inactive Lifecycle (`video_external_links`, `video_external_link_history`)
"""

import os
import re
import sys
import uuid
import glob
import json
import math
import time
import sqlite3
import secrets
import threading
import importlib.util
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qsl, urlencode
from datetime import datetime


def _ensure_local_module(mod_name: str, alt_filenames: tuple):
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    try:
        return __import__(mod_name)
    except ImportError:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for fname in alt_filenames:
            cand = os.path.join(base_dir, fname)
            if os.path.isfile(cand):
                spec = importlib.util.spec_from_file_location(mod_name, cand)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    spec.loader.exec_module(mod)
                    return mod
        raise


_ensure_local_module("security", ("security.py", "Security.py"))
_ensure_local_module("ui_validation", ("ui_validation.py", "Ui Validation.py", "Ui_Validation.py"))

from security import (
    hash_password,
    generate_manual_verification_code,
    generate_random_code,
    generate_custom_button_uid,
    normalize_domain_host,
    normalize_bd_payment_number,
    normalize_permanent_app_uid,
    format_display_app_uid,
    canonicalize_app_uid,
    canonicalize_profile_identity
)

_BASE_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_default_db_file() -> str:
    env_db = os.getenv("DB_FILE", "").strip()
    if env_db:
        return env_db
    local_candidate = os.path.join(_BASE_MODULE_DIR, "battle_club.db")
    is_serverless_ro = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or not os.access(_BASE_MODULE_DIR, os.W_OK))
    if is_serverless_ro:
        tmp_db = "/tmp/battle_club.db"
        if not os.path.exists(tmp_db) and os.path.isfile(local_candidate):
            try:
                import shutil
                shutil.copy2(local_candidate, tmp_db)
            except Exception:
                pass
        return tmp_db
    return local_candidate


DB_FILE = _resolve_default_db_file()
MAX_BACKUPS_TO_KEEP = int(os.getenv("MAX_BACKUPS_TO_KEEP", "15"))
_db_init_lock = threading.RLock()
FULL_WIDTH_DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

NUMERIC_SETTING_RULES = {
    "rate_per_1k": (0.01, 100000.0, float),
    "first_1000_views_payment": (0.01, 100000.0, float),
    "every_200_views_payment": (0.01, 50000.0, float),
    "min_withdraw": (1.0, 1000000.0, float),
    "max_daily_wd_count": (1, 100, int),
    "max_daily_wd_amount": (1.0, 100000000.0, float),
    "max_single_withdraw": (1.0, 100000000.0, float),
    "ref_bonus": (0.0, 100000.0, float),
    "redeem_bonus": (0.0, 100000.0, float),
    "max_daily_referrals": (1, 10000, int),
    "ref_unlock_on_first_video": (0, 1, int),
    "min_initial_views": (1, 100000000, int),
    "enforce_72h_rule": (0, 1, int),
    "submission_window_hours": (1, 87600, int),
    "qualification_window_hours": (1, 87600, int),
    "view_tracking_days": (1, 3650, int),
    "earning_duration_days": (1, 3650, int),
    "view_step_size": (1, 1000000, int),
    "view_checking_interval_sec": (10, 86400, int),
    "verification_interval_sec": (10, 86400, int),
    "user_session_timeout_sec": (30, 86400, int),
    "max_payable_views": (0, 1000000000, int),
    "suspicious_auto_reject": (0, 1, int),
    "min_video_duration_sec": (1, 36000, int),
    "view_velocity_threshold": (100, 100000000, int),
    "engagement_threshold_ratio": (0.0, 1.0, float),
    "strike_limit": (1, 100, int),
}


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Opens SQLite connection with WAL mode and busy_timeout.
    Strictly forbids silently falling back to volatile MEMORY journal mode for file-backed databases.
    """
    path = db_path or os.getenv("DB_FILE", DB_FILE)
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=20000;")

    is_mem_db = (str(path).strip() == ":memory:" or str(path).strip().startswith("file::memory:"))
    if not is_mem_db:
        applied_mode = ""
        for j_mode in ("WAL", "TRUNCATE", "DELETE"):
            try:
                res = conn.execute(f"PRAGMA journal_mode={j_mode};").fetchone()
                mode_now = str(res[0] if res else "").strip().lower()
                if mode_now in ("wal", "truncate", "delete"):
                    applied_mode = mode_now
                    break
            except sqlite3.OperationalError:
                continue
        if not applied_mode:
            conn.close()
            raise sqlite3.OperationalError(
                f"Failed to enable a persistent SQLite journal mode (WAL/TRUNCATE/DELETE) on {path}; refusing unsafe MEMORY journal mode."
            )

    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-20000;")
    return conn


@contextmanager
def begin_immediate_transaction(conn: sqlite3.Connection):
    """
    Executes a database block inside an atomic `BEGIN IMMEDIATE` transaction if not already in a transaction.
    If the connection is already inside an outer transaction, participates in that transaction using a `SAVEPOINT`
    so nested failures roll back cleanly without prematurely committing the outer transaction.
    """
    if not conn.in_transaction:
        conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
    else:
        sp_name = f"sp_{secrets.token_hex(4)}"
        conn.execute(f"SAVEPOINT {sp_name}")
        try:
            yield conn
            conn.execute(f"RELEASE SAVEPOINT {sp_name}")
        except Exception:
            conn.execute(f"ROLLBACK TO SAVEPOINT {sp_name}")
            conn.execute(f"RELEASE SAVEPOINT {sp_name}")
            raise


def _cleanup_old_backups(backup_dir: str, keep: int = MAX_BACKUPS_TO_KEEP):
    try:
        files = sorted(
            glob.glob(os.path.join(backup_dir, "battle_club_backup_*.db")),
            key=os.path.getmtime,
            reverse=True
        )
        for old_file in files[max(1, keep):]:
            try:
                os.remove(old_file)
            except Exception:
                pass
    except Exception:
        pass


def verify_sqlite_integrity(conn_or_path) -> tuple:
    """
    Runs `PRAGMA integrity_check;` and reads all result rows to verify the database returns strictly `'ok'`.
    Returns `(is_ok: bool, details: str)`.
    """
    own_conn = False
    conn = conn_or_path
    if isinstance(conn_or_path, str):
        conn = sqlite3.connect(conn_or_path, timeout=30.0)
        own_conn = True
    try:
        rows = conn.execute("PRAGMA integrity_check;").fetchall()
        if not rows:
            return False, "Empty integrity_check response"
        messages = [str(r[0] if not isinstance(r, sqlite3.Row) else r[0]).strip() for r in rows]
        if len(messages) == 1 and messages[0].lower() == "ok":
            return True, "ok"
        return False, "; ".join(messages)
    except Exception as exc:
        return False, str(exc)
    finally:
        if own_conn and conn:
            try:
                conn.close()
            except Exception:
                pass


def backup_database(db_path: str = None) -> str:
    """
    Uses SQLite Online Backup API exclusively and verifies `PRAGMA integrity_check` == 'ok' on the backup file.
    """
    path = db_path or os.getenv("DB_FILE", DB_FILE)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ""
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = os.path.join(backup_dir, f"battle_club_backup_{ts}.db")
    src = None
    dst = None
    try:
        src = get_connection(path)
        dst = sqlite3.connect(backup_path, timeout=30.0)
        with dst:
            src.backup(dst)
        ok_int, int_msg = verify_sqlite_integrity(dst)
        if not ok_int:
            raise sqlite3.DatabaseError(f"Backup integrity check failed: {int_msg}")
    except Exception:
        if dst:
            try:
                dst.close()
            except Exception:
                pass
            dst = None
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except Exception:
                pass
        return ""
    finally:
        if dst:
            try:
                dst.close()
            except Exception:
                pass
        if src:
            try:
                src.close()
            except Exception:
                pass

    _cleanup_old_backups(backup_dir, MAX_BACKUPS_TO_KEEP)
    return backup_path


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, col_def: str):
    if not re.fullmatch(r"[a-zA-Z0-9_]+", str(table)) or not re.fullmatch(r"[a-zA-Z0-9_]+", str(column)):
        raise ValueError("Invalid table or column identifier")
    cur = conn.execute(f"PRAGMA table_info({table})")
    existing = {row["name"] for row in cur.fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")


def _migrate_plaintext_passwords(conn: sqlite3.Connection):
    """Automatically hashes any legacy plaintext passwords and wipes plaintext storage."""
    rows = conn.execute(
        "SELECT user_id, password_plain, password_hash FROM users WHERE password_plain != '' AND password_plain IS NOT NULL"
    ).fetchall()
    for r in rows:
        uid = r["user_id"]
        p_plain = str(r["password_plain"] or "").strip()
        p_hash = str(r["password_hash"] or "").strip()
        if p_plain and (not p_hash or not p_hash.startswith("pbkdf2_sha256$")):
            p_hash = hash_password(p_plain)
        conn.execute(
            "UPDATE users SET password_hash = ?, password_plain = '' WHERE user_id = ?",
            (p_hash, uid)
        )


def reconcile_legacy_ledger_idempotency_keys(conn: sqlite3.Connection) -> dict:
    """
    Safely reconciles any duplicate `idempotency_key` rows in legacy `ledger_transactions`
    without losing a single transaction record, then enforces a database-level UNIQUE index on `idempotency_key`.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE ledger_transactions SET idempotency_key = NULL WHERE idempotency_key = ''")

    dup_groups = conn.execute("""
        SELECT idempotency_key, COUNT(*) as cnt
        FROM ledger_transactions
        WHERE idempotency_key IS NOT NULL
        GROUP BY idempotency_key
        HAVING COUNT(*) > 1
    """).fetchall()

    reconciled_count = 0
    for dg in dup_groups:
        idem_k = str(dg["idempotency_key"])
        rows = conn.execute(
            "SELECT rowid, tx_id, user_id, amount FROM ledger_transactions WHERE idempotency_key = ? ORDER BY rowid ASC",
            (idem_k,)
        ).fetchall()
        for idx, dup_row in enumerate(rows[1:], start=2):
            rid = dup_row["rowid"]
            tx_id = str(dup_row["tx_id"] or f"ROW_{rid}")
            new_key = f"{idem_k}__LEGACY_DUP_{idx}_{tx_id}"
            conn.execute(
                "UPDATE ledger_transactions SET idempotency_key = ? WHERE rowid = ?",
                (new_key, rid)
            )
            reconciled_count += 1
            try:
                conn.execute("""
                    INSERT INTO audit_logs (actor_id, target_user_id, action, details, created_at)
                    VALUES ('SYSTEM_MIGRATION', ?, 'Legacy Ledger Duplicate Key Reconciled', ?, ?)
                """, (
                    str(dup_row["user_id"] or ""),
                    f"Reconciled duplicate idempotency_key '{idem_k}' on tx {tx_id} -> '{new_key}'",
                    now_str
                ))
            except Exception:
                pass

    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_ledger_idempotency_key_unique ON ledger_transactions(idempotency_key)"
    )
    return {"duplicate_groups": len(dup_groups), "reconciled_rows": reconciled_count, "reconciled_duplicates": reconciled_count, "unique_index_enforced": True}


def _normalize_handle(profile_handle: str, profile_url: str) -> str:
    """Safely normalizes profile handle or URL while preserving essential query keys."""
    h = str(profile_handle or "").strip().lstrip("@").rstrip("/")
    if h:
        if re.match(r"^channel/UC[a-zA-Z0-9_-]{20,}$", h, re.IGNORECASE):
            return "channel/" + h.split("/", 1)[1].lower()
        return h.lower()
    raw_url = str(profile_url or "").strip()
    if not raw_url:
        return ""
    m_yt = re.search(r"youtube\.com/(@[a-zA-Z0-9_.-]+|channel/[a-zA-Z0-9_-]+|c/[a-zA-Z0-9_.-]+|user/[a-zA-Z0-9_.-]+)", raw_url, re.IGNORECASE)
    if m_yt:
        val = m_yt.group(1).lower()
        return val.lstrip("@") if val.startswith("@") else val
    m_tt = re.search(r"tiktok\.com/(?:embed/)?@([a-zA-Z0-9_.-]+)", raw_url, re.IGNORECASE)
    if m_tt:
        return m_tt.group(1).lower()
    try:
        parsed = urlparse(raw_url if "://" in raw_url else f"https://{raw_url}")
        keep_params = []
        for k, v in parse_qsl(parsed.query):
            if k.lower() in ("id", "user", "uid", "channel_id"):
                keep_params.append((k.lower(), v))
        path_clean = (parsed.path or "").strip("/")
        if path_clean.startswith("@") and "/" not in path_clean:
            return path_clean.lstrip("@").lower()
        base = f"{(parsed.netloc or '').lower()}{parsed.path}".rstrip("/").lower()
        if keep_params:
            return f"{base}?{urlencode(keep_params)}"
        return base
    except Exception:
        return raw_url.lower().rstrip("/")


def _normalize_video_url_key(raw_url: str) -> str:
    """Normalizes a video URL for secondary duplicate detection across URL variations."""
    u = str(raw_url or "").strip()
    if not u:
        return ""
    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u.lstrip("/")
    try:
        p = urlparse(u)
        host = (p.netloc or "").lower()
        for pref in ("www.", "m.", "mbasic.", "web."):
            if host.startswith(pref):
                host = host[len(pref):]
        path = re.sub(r"/+$", "", p.path or "")
        keep_q = []
        for k, v in parse_qsl(p.query):
            if k.lower() in ("v", "id", "story_fbid", "fbid"):
                keep_q.append((k.lower(), v))
        if keep_q:
            return f"{host}{path}?{urlencode(keep_q)}"
        return f"{host}{path}"
    except Exception:
        return u.lower().rstrip("/")


def _backfill_identity_locks(conn: sqlite3.Connection):
    """Non-destructively populates profile_identity_locks, user_identity_locks, and video_submission_locks."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plats = conn.execute("SELECT * FROM user_platforms WHERE verified = 1 ORDER BY id ASC").fetchall()
    for p in plats:
        plat_k = str(p["platform"] or "").lower().strip()
        handle_k = _normalize_handle(p["profile_handle"], p["profile_url"])
        canon_id = canonicalize_profile_identity(plat_k, handle_k, p["profile_url"])
        if not canon_id:
            continue
        if not p["canonical_profile_id"]:
            conn.execute(
                "UPDATE user_platforms SET canonical_profile_id = ? WHERE id = ?",
                (canon_id, p["id"])
            )
        conn.execute("""
            INSERT OR IGNORE INTO profile_identity_locks (
                canonical_profile_id, platform, profile_handle, profile_url, user_id, locked_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            canon_id, plat_k, handle_k, str(p["profile_url"] or ""),
            str(p["user_id"]), str(p["created_at"] or now_str), now_str
        ))

    users = conn.execute("SELECT user_id, phone, bkash_number, nagad_number, rocket_number, app_uid, joined_at FROM users WHERE registered = 1").fetchall()
    for u in users:
        uid = str(u["user_id"])
        joined = str(u["joined_at"] or now_str)
        for col in ("phone", "bkash_number", "nagad_number", "rocket_number"):
            ph = normalize_bd_payment_number(u[col], allow_rocket_12=True) if u[col] else ""
            if ph:
                conn.execute("""
                    INSERT OR IGNORE INTO user_identity_locks (
                        lock_type, canonical_value, user_id, locked_at, updated_at
                    ) VALUES ('payment_number', ?, ?, ?, ?)
                """, (ph, uid, joined, now_str))
        app_u = str(u["app_uid"] or "").strip()
        if app_u:
            disp_u = format_display_app_uid(app_u)
            if disp_u and disp_u != app_u:
                conn.execute("UPDATE users SET app_uid = ? WHERE user_id = ?", (disp_u, uid))
            canon_uid = canonicalize_app_uid(app_u)
            if canon_uid:
                conn.execute("""
                    INSERT OR IGNORE INTO user_identity_locks (
                        lock_type, canonical_value, user_id, locked_at, updated_at
                    ) VALUES ('app_uid', ?, ?, ?, ?)
                """, (canon_uid, uid, joined, now_str))
            norm_raw = normalize_permanent_app_uid(app_u, enforce_bc_prefix=False)
            if norm_raw and norm_raw != canon_uid:
                conn.execute("""
                    INSERT OR IGNORE INTO user_identity_locks (
                        lock_type, canonical_value, user_id, locked_at, updated_at
                    ) VALUES ('app_uid', ?, ?, ?, ?)
                """, (norm_raw, uid, joined, now_str))

    vids = conn.execute("SELECT sub_id, platform, canonical_video_id, user_id, url, app_uid, status, submitted_at, platform_account_id FROM videos").fetchall()
    for v in vids:
        plat_v = str(v["platform"] or "").lower().strip()
        cid_v = str(v["canonical_video_id"] or "").strip()
        v_app_u = str(v["app_uid"] or "").strip()
        if v_app_u:
            clean_v_u = format_display_app_uid(v_app_u)
            if clean_v_u and clean_v_u != v_app_u:
                conn.execute("UPDATE videos SET app_uid = ? WHERE sub_id = ?", (clean_v_u, v["sub_id"]))
        if int(v["platform_account_id"] or 0) == 0:
            up_first = conn.execute(
                "SELECT id FROM user_platforms WHERE user_id = ? AND LOWER(platform) = ? ORDER BY id ASC LIMIT 1",
                (str(v["user_id"]), plat_v)
            ).fetchone()
            if up_first:
                conn.execute("UPDATE videos SET platform_account_id = ? WHERE sub_id = ?", (int(up_first["id"]), v["sub_id"]))
        if plat_v and cid_v:
            conn.execute("""
                INSERT OR IGNORE INTO video_submission_locks (
                    platform, canonical_video_id, sub_id, first_user_id, video_url, last_status, locked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                plat_v, cid_v, str(v["sub_id"] or ""), str(v["user_id"] or ""),
                str(v["url"] or ""), str(v["status"] or "submitted"), str(v["submitted_at"] or now_str)
            ))

    wds = conn.execute("SELECT wd_id, app_uid, dest, method FROM withdrawals").fetchall()
    for w in wds:
        w_u = str(w["app_uid"] or "").strip()
        clean_w_u = format_display_app_uid(w_u) if w_u else ""
        w_dest = str(w["dest"] or "").strip()
        clean_dest = format_display_app_uid(w_dest) if w["method"] == "BattleClub_UID" and w_dest else w_dest
        if (clean_w_u and clean_w_u != w_u) or (clean_dest != w_dest):
            conn.execute("UPDATE withdrawals SET app_uid = ?, dest = ? WHERE wd_id = ?", (clean_w_u or w_u, clean_dest, w["wd_id"]))


def _migrate_legacy_videos_and_ledger(conn: sqlite3.Connection):
    """Synchronizes legacy video status/columns, full-width message dividers, and ledger fields non-destructively."""
    conn.execute("""
        UPDATE videos
        SET video_url = url
        WHERE (video_url IS NULL OR video_url = '') AND url IS NOT NULL AND url != ''
    """)
    conn.execute("""
        UPDATE videos
        SET credited_amount = reward
        WHERE (credited_amount IS NULL OR credited_amount = 0) AND reward > 0
    """)
    conn.execute("""
        UPDATE videos
        SET eligible_views = paid_views
        WHERE (eligible_views IS NULL OR eligible_views = 0) AND paid_views > 0
    """)
    conn.execute("""
        UPDATE videos
        SET initial_reward_paid = 1
        WHERE (paid_views > 0 OR credited_amount > 0 OR reward > 0) AND COALESCE(initial_reward_paid, 0) = 0
    """)
    conn.execute("""
        UPDATE videos
        SET previous_views = current_views
        WHERE (previous_views IS NULL OR previous_views = 0) AND current_views > 0
    """)
    conn.execute("""
        UPDATE videos
        SET bot_status = 'approved',
            admin_status = CASE WHEN admin_status IN ('approved', 'rejected') THEN admin_status ELSE 'pending' END
        WHERE status = 'approved' AND (bot_status IS NULL OR bot_status = '' OR bot_status = 'pending')
    """)
    conn.execute("""
        UPDATE videos
        SET bot_status = 'approved',
            admin_status = 'approved',
            status = CASE WHEN COALESCE(permanent_approved, 0) = 1 THEN 'permanent_approved' ELSE 'admin_approved' END
        WHERE status = 'admin_approved' AND (admin_status IS NULL OR admin_status != 'approved')
    """)
    conn.execute("""
        UPDATE videos
        SET status = 'permanent_approved'
        WHERE COALESCE(permanent_approved, 0) = 1
          AND admin_status != 'rejected'
          AND bot_status != 'rejected'
          AND status != 'rejected'
          AND status != 'permanent_approved'
    """)
    conn.execute("""
        UPDATE videos
        SET bot_status = CASE WHEN bot_status IS NULL OR bot_status = '' THEN 'approved' ELSE bot_status END,
            admin_status = 'rejected'
        WHERE status = 'rejected' AND (admin_status IS NULL OR admin_status != 'rejected')
    """)
    conn.execute("""
        UPDATE videos
        SET bot_status = 'manual_review',
            admin_status = 'pending'
        WHERE status = 'pending' AND flagged_suspicious = 1 AND (bot_status IS NULL OR bot_status = '' OR bot_status = 'pending')
    """)

    track_days_row = conn.execute(
        "SELECT value FROM dynamic_settings WHERE key IN ('earning_duration_days', 'view_tracking_days') ORDER BY key ASC LIMIT 1"
    ).fetchone()
    track_days = int(float(track_days_row["value"])) if (track_days_row and track_days_row["value"]) else 5
    bot_app_vids = conn.execute(
        "SELECT sub_id, submitted_at_ts, submitted_at FROM videos WHERE bot_status = 'approved' AND (earning_start_ts IS NULL OR earning_start_ts = 0)"
    ).fetchall()
    for bv in bot_app_vids:
        s_ts = float(bv["submitted_at_ts"] or 0) or time.time()
        s_str = str(bv["submitted_at"] or datetime.fromtimestamp(s_ts).strftime("%Y-%m-%d %H:%M:%S"))
        e_ts = s_ts + (track_days * 86400)
        e_str = datetime.fromtimestamp(e_ts).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE videos SET earning_start_ts = ?, earning_start_date = ?, earning_end_ts = ?, earning_end_date = ? WHERE sub_id = ?",
            (s_ts, s_str, e_ts, e_str, bv["sub_id"])
        )

    conn.execute("""
        UPDATE users
        SET registered = 0
        WHERE registered = 1
          AND (password_hash IS NULL OR password_hash = '')
          AND (password_plain IS NULL OR password_plain = '')
          AND (phone IS NULL OR phone = '')
          AND (app_uid IS NULL OR app_uid = '')
          AND COALESCE(status, 'active') != 'deleted'
    """)

    try:
        from ui_validation import (
            reconstruct_html_from_raw_and_entities,
            repair_or_fallback_html,
            ensure_visible_emoji_presentation
        )
    except Exception:
        reconstruct_html_from_raw_and_entities = None
        repair_or_fallback_html = None
        ensure_visible_emoji_presentation = None

    all_dm = conn.execute("SELECT msg_key, content, raw_text, entities_json FROM dynamic_messages").fetchall()
    for dm in all_dm:
        mk = dm["msg_key"]
        c_txt = str(dm["content"] or "")
        raw_t = str(dm["raw_text"] or "")
        ents_j = str(dm["entities_json"] or "[]")
        new_c = c_txt
        try:
            ents_parsed = json.loads(ents_j) if ents_j else []
        except Exception:
            ents_parsed = []
        if (
            reconstruct_html_from_raw_and_entities
            and raw_t
            and ents_parsed
            and any(isinstance(e, dict) and e.get("type") == "custom_emoji" for e in ents_parsed)
            and "<tg-emoji" not in new_c
        ):
            try:
                rebuilt_c = reconstruct_html_from_raw_and_entities(raw_t, ents_parsed)
                if rebuilt_c and "<tg-emoji" in rebuilt_c:
                    new_c = rebuilt_c
            except Exception:
                pass
        new_c = re.sub(r"━{10,29}", FULL_WIDTH_DIVIDER, new_c)
        if mk == "dashboard_msg" and "বর্তমান মেসেজ টেমপ্লেট" in new_c:
            new_c = re.sub(
                r"^\s*⤵️\s*(?:<b>)?বর্তমান মেসেজ টেমপ্লেট[^<\n]*(?:</b>)?\s*(?:<code>[a-zA-Z0-9_]+</code>)?\s*:?\s*\n+",
                "",
                new_c
            )
            new_c = new_c.replace("</code>l", "</code>").replace("</pre>l", "</pre>")
        if repair_or_fallback_html and new_c:
            try:
                new_c = repair_or_fallback_html(new_c)
            except Exception:
                pass
        if new_c != c_txt:
            conn.execute("UPDATE dynamic_messages SET content = ? WHERE msg_key = ?", (new_c, mk))

    if ensure_visible_emoji_presentation:
        try:
            for r_bl in conn.execute("SELECT btn_key, label FROM button_labels").fetchall():
                lbl_old = str(r_bl["label"] or "")
                lbl_new = ensure_visible_emoji_presentation(lbl_old)
                if lbl_new != lbl_old:
                    conn.execute("UPDATE button_labels SET label = ? WHERE btn_key = ?", (lbl_new, r_bl["btn_key"]))
            for r_cb in conn.execute("SELECT btn_key, label FROM custom_buttons").fetchall():
                lbl_old = str(r_cb["label"] or "")
                lbl_new = ensure_visible_emoji_presentation(lbl_old)
                if lbl_new != lbl_old:
                    conn.execute("UPDATE custom_buttons SET label = ? WHERE btn_key = ?", (lbl_new, r_cb["btn_key"]))
        except Exception:
            pass

    conn.execute("""
        UPDATE ledger_transactions
        SET transaction_type = type
        WHERE (transaction_type IS NULL OR transaction_type = '') AND type IS NOT NULL
    """)
    conn.execute("""
        UPDATE ledger_transactions
        SET previous_balance = before_balance,
            new_balance = after_balance
        WHERE previous_balance IS NULL OR new_balance IS NULL
    """)
    conn.execute("""
        UPDATE ledger_transactions
        SET timestamp = created_at
        WHERE (timestamp IS NULL OR timestamp = '') AND created_at IS NOT NULL
    """)
    conn.execute("""
        UPDATE ledger_transactions
        SET video_id = sub_id
        WHERE (video_id IS NULL OR video_id = '') AND sub_id IS NOT NULL AND sub_id != ''
    """)
    conn.execute("""
        UPDATE ledger_transactions
        SET reference_id = tx_id
        WHERE (reference_id IS NULL OR reference_id = '') AND tx_id IS NOT NULL
    """)
    conn.execute("""
        UPDATE video_external_links
        SET original_url = source_url
        WHERE (original_url IS NULL OR original_url = '') AND source_url IS NOT NULL
    """)
    conn.execute("""
        UPDATE video_external_links
        SET final_url = source_url
        WHERE (final_url IS NULL OR final_url = '') AND source_url IS NOT NULL
    """)

    # Migrate legacy default layouts for user_dashboard, user_profile, and admin_platform_settings
    try:
        for lk_mig, old_patterns, new_rows_mig in [
            (
                "user_dashboard",
                [[["u_leaderboard", "u_pwd_change"], ["u_logout", "u_back_home"]]],
                [["u_leaderboard"], ["u_logout", "u_back_home"]]
            ),
            (
                "user_profile",
                [
                    [["u_prof_change_name", "u_prof_change_wd"], ["u_link_more", "u_pwd_change"], ["u_how_to_work"], ["u_back_dashboard", "u_back_home"]],
                    [["u_prof_change_name", "u_prof_change_wd"], ["u_link_more", "u_pwd_change"], ["u_back_dashboard", "u_back_home"]]
                ],
                [["u_prof_change_name", "u_prof_change_wd"], ["u_link_more", "u_pwd_change"], ["u_how_to_work"], ["u_referral", "u_redeem"], ["u_back_home"]]
            ),
            (
                "admin_platform_settings",
                [[["a_plat_settings"], ["a_rate_settings"], ["a_traffic_hub"], ["a_antifraud_settings"], ["a_back_admin"]]],
                [["a_plat_settings"], ["a_rate_settings"], ["a_antifraud_settings"], ["a_back_admin"]]
            )
        ]:
            row_dl = conn.execute("SELECT structure_json FROM dynamic_layouts WHERE layout_key = ?", (lk_mig,)).fetchone()
            if row_dl and row_dl["structure_json"]:
                parsed_dl = json.loads(row_dl["structure_json"])
                if parsed_dl in old_patterns:
                    conn.execute(
                        "UPDATE dynamic_layouts SET structure_json = ? WHERE layout_key = ?",
                        (json.dumps(new_rows_mig, ensure_ascii=False), lk_mig)
                    )
    except Exception:
        pass

    reconcile_legacy_ledger_idempotency_keys(conn)


def _seed_default_button_original_placements(conn: sqlite3.Connection):
    """Seeds `button_original_placements` from `ui_catalog.DEFAULT_LAYOUTS` without overwriting existing records."""
    try:
        _ensure_local_module("ui_catalog", ("ui_catalog.py", "Ui Catalog.py", "Ui_Catalog.py"))
        from ui_catalog import DEFAULT_LAYOUTS
    except Exception:
        return
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for l_key, rows in DEFAULT_LAYOUTS.items():
        if not isinstance(rows, list):
            continue
        for r_idx, row in enumerate(rows):
            if not isinstance(row, list):
                continue
            for c_idx, bk in enumerate(row):
                b_str = str(bk or "").strip()
                if not b_str:
                    continue
                conn.execute("""
                    INSERT OR IGNORE INTO button_original_placements (
                        btn_key, original_layout_key, original_row_index, original_col_index,
                        current_layout_key, current_row_index, current_col_index, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (b_str, l_key, int(r_idx), int(c_idx), l_key, int(r_idx), int(c_idx), now_str))


def init_db(db_path: str = None):
    with _db_init_lock:
        path = db_path or os.getenv("DB_FILE", DB_FILE)
        if path != ":memory:" and os.path.exists(path) and os.path.getsize(path) > 0:
            backup_database(path)

        conn = get_connection(path)
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT DEFAULT '',
                        name TEXT DEFAULT '',
                        phone TEXT DEFAULT '',
                        password_hash TEXT DEFAULT '',
                        password_plain TEXT DEFAULT '',
                        unique_code TEXT DEFAULT '',
                        referral_code TEXT DEFAULT '',
                        bio_verify_code TEXT DEFAULT '',
                        platform_bio_codes TEXT DEFAULT '{}',
                        bio_code_generated_ts REAL DEFAULT 0,
                        active_video_code TEXT DEFAULT '',
                        channel_name TEXT DEFAULT '',
                        youtube_channel_name TEXT DEFAULT '',
                        tiktok_channel_name TEXT DEFAULT '',
                        channel_url TEXT DEFAULT '',
                        channel_subs INTEGER DEFAULT 0,
                        app_uid TEXT DEFAULT '',
                        balance REAL DEFAULT 0.0,
                        held_balance REAL DEFAULT 0.0,
                        debt_balance REAL DEFAULT 0.0,
                        total_earned REAL DEFAULT 0.0,
                        videos_submitted INTEGER DEFAULT 0,
                        videos_approved INTEGER DEFAULT 0,
                        videos_rejected INTEGER DEFAULT 0,
                        ref_by TEXT DEFAULT '',
                        redeemed_ref INTEGER DEFAULT 0,
                        ref_bonus_credited INTEGER DEFAULT 0,
                        ref_count INTEGER DEFAULT 0,
                        daily_ref_date TEXT DEFAULT '',
                        daily_ref_count INTEGER DEFAULT 0,
                        daily_wd_date TEXT DEFAULT '',
                        daily_wd_count INTEGER DEFAULT 0,
                        daily_wd_amount REAL DEFAULT 0.0,
                        registered INTEGER DEFAULT 0,
                        session_logged_out INTEGER DEFAULT 0,
                        session_version INTEGER DEFAULT 1,
                        timeout_notified INTEGER DEFAULT 0,
                        last_active_ts REAL DEFAULT 0,
                        login_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        bio_frozen INTEGER DEFAULT 0,
                        admin_suspended INTEGER DEFAULT 0,
                        duplicate_strikes INTEGER DEFAULT 0,
                        wrong_submit_strikes INTEGER DEFAULT 0,
                        cooldown_until_ts REAL DEFAULT 0,
                        user_btn_style TEXT DEFAULT '',
                        bottom_menu_enabled INTEGER DEFAULT 0,
                        admin_bottom_menu INTEGER DEFAULT 0,
                        language TEXT DEFAULT 'bn',
                        joined_at TEXT DEFAULT ''
                    )
                """)

                _ensure_column(conn, "users", "referral_code", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "platform_bio_codes", "TEXT DEFAULT '{}'")
                _ensure_column(conn, "users", "debt_balance", "REAL DEFAULT 0.0")
                _ensure_column(conn, "users", "ref_bonus_credited", "INTEGER DEFAULT 0")
                _ensure_column(conn, "users", "login_count", "INTEGER DEFAULT 0")
                _ensure_column(conn, "users", "language", "TEXT DEFAULT 'bn'")
                _ensure_column(conn, "users", "session_version", "INTEGER DEFAULT 1")
                _ensure_column(conn, "users", "admin_suspended", "INTEGER DEFAULT 0")
                _ensure_column(conn, "users", "bkash_number", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "nagad_number", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "rocket_number", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "selected_payment_methods", "TEXT DEFAULT '[\x22bKash\x22, \x22BattleClub_UID\x22]'")
                _ensure_column(conn, "users", "profile_edit_unlocked_until", "REAL DEFAULT 0")
                _ensure_column(conn, "users", "youtube_channel_name", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "tiktok_channel_name", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "bottom_menu_enabled", "INTEGER DEFAULT 0")
                _ensure_column(conn, "users", "admin_bottom_menu", "INTEGER DEFAULT 0")
                _ensure_column(conn, "users", "last_failed_url", "TEXT DEFAULT ''")
                _ensure_column(conn, "users", "last_failed_platform", "TEXT DEFAULT ''")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS platform_criteria (
                        platform TEXT PRIMARY KEY,
                        min_subs INTEGER DEFAULT 200,
                        min_total_videos INTEGER DEFAULT 8,
                        qualifying_videos INTEGER DEFAULT 2,
                        min_views INTEGER DEFAULT 1000,
                        max_accounts INTEGER DEFAULT 3,
                        min_initial_views INTEGER DEFAULT 1000,
                        rate_per_1k REAL DEFAULT 15.0,
                        every_200_views_payment REAL DEFAULT 3.0,
                        max_payable_views INTEGER DEFAULT 5000000,
                        step_size INTEGER DEFAULT 200,
                        earning_duration_days INTEGER DEFAULT 5,
                        submission_window_hours INTEGER DEFAULT 72,
                        qualification_window_hours INTEGER DEFAULT 120,
                        verification_link TEXT DEFAULT '',
                        custom_overrides_json TEXT DEFAULT '{}'
                    )
                """)
                _ensure_column(conn, "platform_criteria", "min_total_videos", "INTEGER DEFAULT 8")
                _ensure_column(conn, "platform_criteria", "min_initial_views", "INTEGER DEFAULT 1000")
                _ensure_column(conn, "platform_criteria", "rate_per_1k", "REAL DEFAULT 15.0")
                _ensure_column(conn, "platform_criteria", "every_200_views_payment", "REAL DEFAULT 3.0")
                _ensure_column(conn, "platform_criteria", "max_payable_views", "INTEGER DEFAULT 5000000")
                _ensure_column(conn, "platform_criteria", "step_size", "INTEGER DEFAULT 200")
                _ensure_column(conn, "platform_criteria", "earning_duration_days", "INTEGER DEFAULT 5")
                _ensure_column(conn, "platform_criteria", "submission_window_hours", "INTEGER DEFAULT 72")
                _ensure_column(conn, "platform_criteria", "qualification_window_hours", "INTEGER DEFAULT 120")
                _ensure_column(conn, "platform_criteria", "verification_link", "TEXT DEFAULT ''")
                _ensure_column(conn, "platform_criteria", "custom_overrides_json", "TEXT DEFAULT '{}'")

                for plat in ("youtube", "tiktok", "instagram", "facebook", "telegram"):
                    conn.execute("""
                        INSERT OR IGNORE INTO platform_criteria (
                            platform, min_subs, min_total_videos, qualifying_videos,
                            min_views, max_accounts, min_initial_views, rate_per_1k,
                            every_200_views_payment, max_payable_views, step_size,
                            earning_duration_days, submission_window_hours, qualification_window_hours,
                            verification_link, custom_overrides_json
                        ) VALUES (?, 200, 8, 2, 1000, 3, 1000, 15.0, 3.0, 5000000, 200, 5, 72, 120, '', '{}')
                    """, (plat,))

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_platforms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        profile_url TEXT NOT NULL,
                        profile_handle TEXT NOT NULL,
                        canonical_profile_id TEXT DEFAULT '',
                        display_name TEXT DEFAULT '',
                        subs_count INTEGER DEFAULT 0,
                        bio_code_used TEXT DEFAULT '',
                        verified INTEGER DEFAULT 1,
                        verification_state TEXT DEFAULT 'VERIFIED',
                        bio_missing_flag INTEGER DEFAULT 0,
                        last_bio_check_ts REAL DEFAULT 0,
                        created_at TEXT DEFAULT '',
                        UNIQUE(platform, profile_handle)
                    )
                """)
                _ensure_column(conn, "user_platforms", "verification_state", "TEXT DEFAULT 'VERIFIED'")
                _ensure_column(conn, "user_platforms", "canonical_profile_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "user_platforms", "total_videos_count", "INTEGER DEFAULT 0")
                _ensure_column(conn, "user_platforms", "videos_with_views_collected", "INTEGER DEFAULT 0")
                _ensure_column(conn, "user_platforms", "verification_completeness", "TEXT DEFAULT 'COMPLETE'")
                _ensure_column(conn, "user_platforms", "qualifying_vids_count", "INTEGER DEFAULT 0")
                _ensure_column(conn, "user_platforms", "qualifying_views_total", "INTEGER DEFAULT 0")
                _ensure_column(conn, "user_platforms", "qualifying_views_list_json", "TEXT DEFAULT '[]'")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS profile_identity_locks (
                        canonical_profile_id TEXT PRIMARY KEY,
                        platform TEXT NOT NULL,
                        profile_handle TEXT NOT NULL,
                        profile_url TEXT DEFAULT '',
                        user_id TEXT NOT NULL,
                        locked_at TEXT DEFAULT '',
                        updated_at TEXT DEFAULT '',
                        UNIQUE(platform, profile_handle)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_identity_locks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        lock_type TEXT NOT NULL,
                        canonical_value TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        locked_at TEXT DEFAULT '',
                        updated_at TEXT DEFAULT '',
                        UNIQUE(lock_type, canonical_value)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS video_submission_locks (
                        platform TEXT NOT NULL,
                        canonical_video_id TEXT NOT NULL,
                        sub_id TEXT DEFAULT '',
                        first_user_id TEXT DEFAULT '',
                        video_url TEXT DEFAULT '',
                        last_status TEXT DEFAULT '',
                        locked_at TEXT DEFAULT '',
                        PRIMARY KEY (platform, canonical_video_id)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS used_random_codes (
                        code TEXT PRIMARY KEY,
                        code_type TEXT DEFAULT 'general',
                        user_id TEXT DEFAULT '',
                        ref_id TEXT DEFAULT '',
                        created_at TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS custom_buttons (
                        btn_key TEXT PRIMARY KEY,
                        side TEXT DEFAULT 'user',
                        parent_layout TEXT DEFAULT 'user_home',
                        destination_layout TEXT DEFAULT 'user_home',
                        row_index INTEGER DEFAULT -1,
                        col_index INTEGER DEFAULT -1,
                        parent_container_key TEXT DEFAULT '',
                        original_layout_key TEXT DEFAULT 'user_home',
                        original_row_index INTEGER DEFAULT 0,
                        original_col_index INTEGER DEFAULT 0,
                        label TEXT NOT NULL,
                        style TEXT DEFAULT 'primary',
                        design_style TEXT DEFAULT 'normal',
                        custom_emoji_id TEXT DEFAULT '',
                        msg_key TEXT NOT NULL,
                        layout_key TEXT NOT NULL,
                        created_at TEXT
                    )
                """)
                _ensure_column(conn, "custom_buttons", "destination_layout", "TEXT DEFAULT 'user_home'")
                _ensure_column(conn, "custom_buttons", "row_index", "INTEGER DEFAULT -1")
                _ensure_column(conn, "custom_buttons", "col_index", "INTEGER DEFAULT -1")
                _ensure_column(conn, "custom_buttons", "parent_container_key", "TEXT DEFAULT ''")
                _ensure_column(conn, "custom_buttons", "original_layout_key", "TEXT DEFAULT 'user_home'")
                _ensure_column(conn, "custom_buttons", "original_row_index", "INTEGER DEFAULT 0")
                _ensure_column(conn, "custom_buttons", "original_col_index", "INTEGER DEFAULT 0")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS button_original_placements (
                        btn_key TEXT PRIMARY KEY,
                        original_layout_key TEXT NOT NULL,
                        original_row_index INTEGER NOT NULL DEFAULT 0,
                        original_col_index INTEGER NOT NULL DEFAULT 0,
                        current_layout_key TEXT NOT NULL DEFAULT '',
                        current_row_index INTEGER NOT NULL DEFAULT 0,
                        current_col_index INTEGER NOT NULL DEFAULT 0,
                        updated_at TEXT DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS manual_verification_codes (
                        code TEXT PRIMARY KEY,
                        target_user_id TEXT DEFAULT '',
                        platform TEXT DEFAULT '',
                        profile_url TEXT DEFAULT '',
                        created_by TEXT DEFAULT '',
                        created_at_ts REAL DEFAULT 0,
                        expires_at_ts REAL DEFAULT 0,
                        used INTEGER DEFAULT 0,
                        used_by TEXT DEFAULT '',
                        used_at_ts REAL DEFAULT 0,
                        status TEXT DEFAULT 'active'
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS manual_verification_requests (
                        req_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        profile_url TEXT NOT NULL,
                        profile_handle TEXT DEFAULT '',
                        bio_code TEXT DEFAULT '',
                        manual_code_used TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        admin_id TEXT DEFAULT '',
                        decision_note TEXT DEFAULT '',
                        created_at TEXT DEFAULT '',
                        processed_at TEXT DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS broadcast_jobs (
                        job_id TEXT PRIMARY KEY,
                        admin_id TEXT NOT NULL,
                        content_type TEXT DEFAULT 'text',
                        total_recipients INTEGER DEFAULT 0,
                        sent_count INTEGER DEFAULT 0,
                        failed_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 5,
                        status TEXT DEFAULT 'running',
                        created_at TEXT DEFAULT '',
                        completed_at TEXT DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS broadcast_deliveries (
                        job_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        attempts INTEGER DEFAULT 0,
                        last_error TEXT DEFAULT '',
                        updated_at TEXT DEFAULT '',
                        PRIMARY KEY (job_id, user_id)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS videos (
                        sub_id TEXT PRIMARY KEY,
                        platform TEXT NOT NULL,
                        platform_account_id INTEGER DEFAULT 0,
                        video_id TEXT NOT NULL,
                        canonical_video_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        url TEXT NOT NULL,
                        video_url TEXT DEFAULT '',
                        title TEXT DEFAULT '',
                        unique_code TEXT DEFAULT '',
                        global_code TEXT DEFAULT '',
                        app_uid TEXT DEFAULT '',
                        status TEXT DEFAULT 'pending',
                        bot_status TEXT DEFAULT 'pending',
                        admin_status TEXT DEFAULT 'pending',
                        permanent_approved INTEGER DEFAULT 0,
                        permanent_approved_at TEXT DEFAULT '',
                        permanent_approved_by TEXT DEFAULT '',
                        is_trashed INTEGER DEFAULT 0,
                        trashed_at TEXT DEFAULT '',
                        trashed_by TEXT DEFAULT '',
                        trash_previous_status TEXT DEFAULT '',
                        trash_previous_bot_status TEXT DEFAULT '',
                        trash_previous_admin_status TEXT DEFAULT '',
                        rejection_reason TEXT DEFAULT '',
                        rejection_date TEXT DEFAULT '',
                        current_views INTEGER DEFAULT 0,
                        ytdlp_views INTEGER DEFAULT 0,
                        public_page_views INTEGER DEFAULT 0,
                        dual_source_verified INTEGER DEFAULT 0,
                        single_source_verified INTEGER DEFAULT 0,
                        verification_mode TEXT DEFAULT 'UNVERIFIED',
                        video_duration_sec INTEGER DEFAULT 0,
                        duration_known INTEGER DEFAULT 0,
                        publish_ts REAL DEFAULT 0,
                        publish_date TEXT DEFAULT '',
                        publish_date_known INTEGER DEFAULT 0,
                        comments_verified INTEGER DEFAULT 0,
                        organic_status TEXT DEFAULT 'PENDING_SNAPSHOTS',
                        view_metrics_known INTEGER DEFAULT 0,
                        view_metrics_source TEXT DEFAULT '',
                        qualification_deadline_ts REAL DEFAULT 0,
                        previous_views INTEGER DEFAULT 0,
                        eligible_views INTEGER DEFAULT 0,
                        paid_views INTEGER DEFAULT 0,
                        initial_reward_paid INTEGER DEFAULT 0,
                        reward REAL DEFAULT 0.0,
                        credited_amount REAL DEFAULT 0.0,
                        reversed_amount REAL DEFAULT 0.0,
                        earning_start_date TEXT DEFAULT '',
                        earning_start_ts REAL DEFAULT 0,
                        earning_end_date TEXT DEFAULT '',
                        earning_end_ts REAL DEFAULT 0,
                        approval_date TEXT DEFAULT '',
                        approved_at_ts REAL DEFAULT 0,
                        last_checked_at TEXT DEFAULT '',
                        last_checked_ts REAL DEFAULT 0,
                        flagged_suspicious INTEGER DEFAULT 0,
                        code_missing_flag INTEGER DEFAULT 0,
                        code_missing_warning_ts REAL DEFAULT 0,
                        risk_reason TEXT DEFAULT '',
                        last_code_check_ts REAL DEFAULT 0,
                        submitted_at_ts REAL DEFAULT 0,
                        submitted_at TEXT DEFAULT '',
                        traffic_data_available INTEGER DEFAULT 0,
                        traffic_source_status TEXT DEFAULT 'unknown',
                        channel_page_pct REAL DEFAULT 0.0,
                        channel_page_views INTEGER DEFAULT 0,
                        search_pct REAL DEFAULT 0.0,
                        search_views INTEGER DEFAULT 0,
                        external_pct REAL DEFAULT 0.0,
                        external_views INTEGER DEFAULT 0,
                        deducted_external_views INTEGER DEFAULT 0,
                        traffic_sources_json TEXT DEFAULT '{}',
                        external_links_json TEXT DEFAULT '[]',
                        UNIQUE(platform, canonical_video_id)
                    )
                """)
                _ensure_column(conn, "videos", "platform_account_id", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "video_url", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "bot_status", "TEXT DEFAULT 'pending'")
                _ensure_column(conn, "videos", "admin_status", "TEXT DEFAULT 'pending'")
                _ensure_column(conn, "videos", "permanent_approved", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "permanent_approved_at", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "permanent_approved_by", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "is_trashed", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "trashed_at", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "trashed_by", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "trash_previous_status", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "trash_previous_bot_status", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "trash_previous_admin_status", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "rejection_reason", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "rejection_date", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "previous_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "eligible_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "initial_reward_paid", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "credited_amount", "REAL DEFAULT 0.0")
                _ensure_column(conn, "videos", "reversed_amount", "REAL DEFAULT 0.0")
                _ensure_column(conn, "videos", "earning_start_date", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "earning_start_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "earning_end_date", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "earning_end_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "approval_date", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "approved_at_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "last_checked_at", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "last_checked_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "code_missing_flag", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "code_missing_warning_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "last_code_check_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "view_metrics_known", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "view_metrics_source", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "qualification_deadline_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "ytdlp_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "public_page_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "dual_source_verified", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "single_source_verified", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "verification_mode", "TEXT DEFAULT 'UNVERIFIED'")
                _ensure_column(conn, "videos", "video_duration_sec", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "duration_known", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "publish_ts", "REAL DEFAULT 0")
                _ensure_column(conn, "videos", "publish_date", "TEXT DEFAULT ''")
                _ensure_column(conn, "videos", "publish_date_known", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "comments_verified", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "organic_status", "TEXT DEFAULT 'PENDING_SNAPSHOTS'")
                _ensure_column(conn, "videos", "traffic_data_available", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "traffic_source_status", "TEXT DEFAULT 'unknown'")
                _ensure_column(conn, "videos", "channel_page_pct", "REAL DEFAULT 0.0")
                _ensure_column(conn, "videos", "channel_page_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "search_pct", "REAL DEFAULT 0.0")
                _ensure_column(conn, "videos", "search_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "external_pct", "REAL DEFAULT 0.0")
                _ensure_column(conn, "videos", "external_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "deducted_external_views", "INTEGER DEFAULT 0")
                _ensure_column(conn, "videos", "traffic_sources_json", "TEXT DEFAULT '{}'")
                _ensure_column(conn, "videos", "external_links_json", "TEXT DEFAULT '[]'")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS video_external_links (
                        ext_id TEXT PRIMARY KEY,
                        sub_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        source_url TEXT NOT NULL,
                        original_url TEXT DEFAULT '',
                        final_url TEXT DEFAULT '',
                        domain TEXT DEFAULT '',
                        views_pct REAL DEFAULT 0.0,
                        views_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'pending',
                        is_active INTEGER DEFAULT 1,
                        admin_id TEXT DEFAULT '',
                        decision_at TEXT DEFAULT '',
                        notified INTEGER DEFAULT 0,
                        first_seen_at TEXT DEFAULT '',
                        last_seen_at TEXT DEFAULT '',
                        deactivated_at TEXT DEFAULT '',
                        created_at TEXT DEFAULT ''
                    )
                """)
                _ensure_column(conn, "video_external_links", "original_url", "TEXT DEFAULT ''")
                _ensure_column(conn, "video_external_links", "final_url", "TEXT DEFAULT ''")
                _ensure_column(conn, "video_external_links", "is_active", "INTEGER DEFAULT 1")
                _ensure_column(conn, "video_external_links", "first_seen_at", "TEXT DEFAULT ''")
                _ensure_column(conn, "video_external_links", "last_seen_at", "TEXT DEFAULT ''")
                _ensure_column(conn, "video_external_links", "deactivated_at", "TEXT DEFAULT ''")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_ext_links_sub ON video_external_links(sub_id, is_active, status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_ext_links_plat ON video_external_links(platform, is_active, status)")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS video_external_link_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ext_id TEXT NOT NULL,
                        sub_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        original_url TEXT NOT NULL,
                        final_url TEXT NOT NULL,
                        domain TEXT DEFAULT '',
                        views_pct REAL DEFAULT 0.0,
                        views_count INTEGER DEFAULT 0,
                        is_active INTEGER DEFAULT 1,
                        event_type TEXT DEFAULT 'scan_detected',
                        recorded_at TEXT DEFAULT ''
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_ext_link_hist_sub ON video_external_link_history(sub_id, recorded_at)")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS video_view_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sub_id TEXT NOT NULL,
                        views INTEGER NOT NULL DEFAULT 0,
                        likes INTEGER NOT NULL DEFAULT 0,
                        comments INTEGER NOT NULL DEFAULT 0,
                        source TEXT DEFAULT '',
                        recorded_at_ts REAL NOT NULL,
                        UNIQUE(sub_id, recorded_at_ts)
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_video_view_snapshots_sub_time ON video_view_snapshots(sub_id, recorded_at_ts)")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS withdrawals (
                        wd_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        original_amount REAL DEFAULT 0.0,
                        method TEXT NOT NULL,
                        dest TEXT NOT NULL,
                        app_uid TEXT DEFAULT '',
                        status TEXT DEFAULT 'pending',
                        admin_id TEXT DEFAULT '',
                        decision_reason TEXT DEFAULT '',
                        trx_id TEXT DEFAULT '',
                        payment_note TEXT DEFAULT '',
                        created_at TEXT DEFAULT '',
                        processed_at TEXT DEFAULT ''
                    )
                """)
                _ensure_column(conn, "withdrawals", "original_amount", "REAL DEFAULT 0.0")
                _ensure_column(conn, "withdrawals", "admin_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "withdrawals", "decision_reason", "TEXT DEFAULT ''")
                _ensure_column(conn, "withdrawals", "trx_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "withdrawals", "payment_note", "TEXT DEFAULT ''")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ledger_transactions (
                        tx_id TEXT PRIMARY KEY,
                        idempotency_key TEXT UNIQUE,
                        user_id TEXT NOT NULL,
                        video_id TEXT DEFAULT '',
                        sub_id TEXT DEFAULT '',
                        type TEXT NOT NULL,
                        transaction_type TEXT DEFAULT '',
                        amount REAL NOT NULL,
                        before_balance REAL NOT NULL,
                        previous_balance REAL DEFAULT 0.0,
                        after_balance REAL NOT NULL,
                        new_balance REAL DEFAULT 0.0,
                        reference_id TEXT DEFAULT '',
                        details TEXT DEFAULT '',
                        admin_id TEXT DEFAULT '',
                        created_at TEXT DEFAULT '',
                        timestamp TEXT DEFAULT ''
                    )
                """)
                _ensure_column(conn, "ledger_transactions", "idempotency_key", "TEXT")
                _ensure_column(conn, "ledger_transactions", "video_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "ledger_transactions", "sub_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "ledger_transactions", "transaction_type", "TEXT DEFAULT ''")
                _ensure_column(conn, "ledger_transactions", "previous_balance", "REAL DEFAULT 0.0")
                _ensure_column(conn, "ledger_transactions", "new_balance", "REAL DEFAULT 0.0")
                _ensure_column(conn, "ledger_transactions", "reference_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "ledger_transactions", "admin_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "ledger_transactions", "timestamp", "TEXT DEFAULT ''")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS debt_adjustments (
                        adj_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        sub_id TEXT DEFAULT '',
                        total_clawback REAL NOT NULL,
                        deducted_from_balance REAL NOT NULL,
                        remaining_debt REAL NOT NULL,
                        reason TEXT DEFAULT '',
                        status TEXT DEFAULT 'open',
                        created_at TEXT DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        actor_id TEXT NOT NULL,
                        target_user_id TEXT DEFAULT '',
                        action TEXT NOT NULL,
                        details TEXT DEFAULT '',
                        created_at TEXT DEFAULT ''
                    )
                """)

                conn.execute("CREATE TABLE IF NOT EXISTS dynamic_settings (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")

                default_settings_seed = {
                    "max_payable_views": str(os.getenv("MAX_PAYABLE_VIEWS", "5000000")).strip() or "5000000",
                    "rate_per_1k": "15.0",
                    "first_1000_views_payment": "15.0",
                    "every_200_views_payment": "3.0",
                    "min_initial_views": "1000",
                    "view_step_size": "200",
                    "enforce_72h_rule": "1",
                    "submission_window_hours": "72",
                    "earning_duration_days": "5",
                    "view_tracking_days": "5",
                    "qualification_window_hours": "120",
                    "view_checking_interval_sec": "3600",
                    "verification_interval_sec": "3600",
                    "user_session_timeout_sec": "600",
                    "min_withdraw": "100.0",
                    "max_daily_wd_count": "2",
                    "max_daily_wd_amount": "5000.0",
                    "max_single_withdraw": "5000.0",
                    "wd_eta_text": "১২ থেকে ২৪ ঘণ্টার মধ্যে",
                    "ref_bonus": "10.0",
                    "redeem_bonus": "5.0",
                    "max_daily_referrals": "5",
                    "ref_unlock_on_first_video": "0",
                    "suspicious_auto_reject": "1",
                    "min_video_duration_sec": "10",
                    "view_velocity_threshold": "15000",
                    "engagement_threshold_ratio": "0.0005",
                    "strike_limit": "3",
                    "required_link_config": "all_public",
                    "pending_expiry_action": "permanent_approve_zero_pay",
                    "admin_session_timeout_sec": "3600",
                    "verification_link": "",
                }
                for sk, sv in default_settings_seed.items():
                    conn.execute("INSERT OR IGNORE INTO dynamic_settings (key, value) VALUES (?, ?)", (sk, sv))
                    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (sk, sv))

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS button_labels (
                        btn_key TEXT PRIMARY KEY,
                        label TEXT,
                        icon_custom_emoji_id TEXT DEFAULT '',
                        design_style TEXT DEFAULT 'normal',
                        label_customized INTEGER DEFAULT 0,
                        emoji_customized INTEGER DEFAULT 0,
                        is_visible INTEGER DEFAULT 1
                    )
                """)
                _ensure_column(conn, "button_labels", "icon_custom_emoji_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "button_labels", "design_style", "TEXT DEFAULT 'normal'")
                _ensure_column(conn, "button_labels", "label_customized", "INTEGER DEFAULT 0")
                _ensure_column(conn, "button_labels", "emoji_customized", "INTEGER DEFAULT 0")
                _ensure_column(conn, "button_labels", "is_visible", "INTEGER DEFAULT 1")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS button_styles (
                        btn_key TEXT PRIMARY KEY,
                        style TEXT,
                        icon_custom_emoji_id TEXT DEFAULT '',
                        design_style TEXT DEFAULT 'normal'
                    )
                """)
                _ensure_column(conn, "button_styles", "icon_custom_emoji_id", "TEXT DEFAULT ''")
                _ensure_column(conn, "button_styles", "design_style", "TEXT DEFAULT 'normal'")

                conn.execute("CREATE TABLE IF NOT EXISTS dynamic_layouts (layout_key TEXT PRIMARY KEY, structure_json TEXT)")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dynamic_messages (
                        msg_key TEXT PRIMARY KEY,
                        content TEXT,
                        raw_text TEXT DEFAULT '',
                        entities_json TEXT DEFAULT '[]',
                        prev_content TEXT DEFAULT '',
                        prev_raw_text TEXT DEFAULT '',
                        prev_entities_json TEXT DEFAULT '[]',
                        button_mode TEXT DEFAULT 'default',
                        custom_buttons_json TEXT DEFAULT '[]',
                        version INTEGER DEFAULT 1,
                        updated_by TEXT DEFAULT '',
                        updated_at TEXT DEFAULT ''
                    )
                """)
                _ensure_column(conn, "dynamic_messages", "raw_text", "TEXT DEFAULT ''")
                _ensure_column(conn, "dynamic_messages", "entities_json", "TEXT DEFAULT '[]'")
                _ensure_column(conn, "dynamic_messages", "prev_content", "TEXT DEFAULT ''")
                _ensure_column(conn, "dynamic_messages", "prev_raw_text", "TEXT DEFAULT ''")
                _ensure_column(conn, "dynamic_messages", "prev_entities_json", "TEXT DEFAULT '[]'")
                _ensure_column(conn, "dynamic_messages", "button_mode", "TEXT DEFAULT 'default'")
                _ensure_column(conn, "dynamic_messages", "custom_buttons_json", "TEXT DEFAULT '[]'")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS custom_emoji_registry (
                        emoji_key TEXT PRIMARY KEY,
                        custom_emoji_id TEXT NOT NULL,
                        fallback_emoji TEXT DEFAULT '✨',
                        description TEXT DEFAULT '',
                        updated_at TEXT DEFAULT ''
                    )
                """)

                _migrate_plaintext_passwords(conn)
                _migrate_legacy_videos_and_ledger(conn)
                _backfill_identity_locks(conn)
                _seed_default_button_original_placements(conn)

                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status, registered);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_ref_code ON users(referral_code);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_user ON videos(user_id, platform, status);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_acc ON videos(platform_account_id, status);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_approval_nav ON videos(bot_status, admin_status, platform, is_trashed);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_status_check ON videos(status, last_code_check_ts);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_wd_user_status ON withdrawals(user_id, status);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_user ON ledger_transactions(user_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_video ON ledger_transactions(video_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_debt_user_status ON debt_adjustments(user_id, status);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_logs(target_user_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_prof_locks_user ON profile_identity_locks(user_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_locks_user ON user_identity_locks(user_id, lock_type);")
                conn.execute("PRAGMA optimize;")
        finally:
            conn.close()


def validate_setting_value(key: str, value) -> str:
    """Validates admin configuration values before saving to database. Rejects NaN, Infinity, -Infinity."""
    k = str(key or "").strip()
    if not k:
        raise ValueError("Setting key cannot be empty")
    if value is None:
        raise ValueError(f"Setting value for {k} cannot be None")
    v_str = str(value).strip()
    if k in NUMERIC_SETTING_RULES:
        min_v, max_v, cast_fn = NUMERIC_SETTING_RULES[k]
        try:
            raw_flt = float(v_str)
        except Exception as exc:
            raise ValueError(f"Invalid numeric value for {k}: {v_str}") from exc
        if not math.isfinite(raw_flt):
            raise ValueError(f"Non-finite value (NaN/Infinity) is not allowed for {k}")
        try:
            num_val = cast_fn(raw_flt) if cast_fn is int else raw_flt
        except Exception as exc:
            raise ValueError(f"Invalid numeric value for {k}: {v_str}") from exc
        if num_val < min_v or num_val > max_v:
            raise ValueError(f"Value for {k} must be between {min_v} and {max_v} (got {num_val})")
        return str(num_val)
    if k in ("global_user_theme", "global_admin_theme"):
        if v_str not in ("success", "danger", "primary", "default"):
            raise ValueError(f"Invalid theme style: {v_str}")
    if k == "required_link_config":
        v_low = v_str.strip().lower()
        if v_low not in ("all_public", "on", "off"):
            raise ValueError(f"Invalid required_link_config: {v_str} (allowed: all_public, on, off)")
        return v_low
    if k == "pending_expiry_action":
        v_low = v_str.strip().lower()
        if v_low not in ("permanent_approve_zero_pay", "reject"):
            raise ValueError(f"Invalid pending_expiry_action: {v_str} (allowed: permanent_approve_zero_pay, reject)")
        return v_low
    return v_str


def get_setting(key: str, default: str = "") -> str:
    k = str(key or "").strip()
    if not k:
        return default
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM dynamic_settings WHERE key = ? LIMIT 1", (k,)).fetchone()
        if row and row["value"] is not None:
            return str(row["value"])
        row2 = conn.execute("SELECT value FROM settings WHERE key = ? LIMIT 1", (k,)).fetchone()
        if row2 and row2["value"] is not None:
            return str(row2["value"])
        return default
    except Exception:
        return default
    finally:
        conn.close()


def _update_non_overridden_platform_field(conn: sqlite3.Connection, field: str, val):
    """Updates a platform_criteria column only for platforms that haven't explicitly overridden that field."""
    rows = conn.execute("SELECT platform, custom_overrides_json FROM platform_criteria").fetchall()
    for r in rows:
        try:
            ov = json.loads(r["custom_overrides_json"] or "{}")
        except Exception:
            ov = {}
        if not ov.get(field):
            conn.execute(f"UPDATE platform_criteria SET {field} = ? WHERE platform = ?", (val, r["platform"]))


def set_setting(key: str, value: str):
    k = str(key or "").strip()
    if not k:
        raise ValueError("Setting key cannot be empty")
    v = validate_setting_value(k, value)
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES (?, ?)", (k, v))
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
            conn.execute("UPDATE settings SET value = ? WHERE key = ?", (v, k))
            if k in ("rate_per_1k", "first_1000_views_payment"):
                other_k = "first_1000_views_payment" if k == "rate_per_1k" else "rate_per_1k"
                conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES (?, ?)", (other_k, v))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (other_k, v))
                _update_non_overridden_platform_field(conn, "rate_per_1k", float(v))
                min_init_r = conn.execute("SELECT value FROM dynamic_settings WHERE key = 'min_initial_views' LIMIT 1").fetchone()
                step_r = conn.execute("SELECT value FROM dynamic_settings WHERE key = 'view_step_size' LIMIT 1").fetchone()
                m_init = max(1, int(float(min_init_r["value"]))) if (min_init_r and min_init_r["value"]) else 1000
                st_sz = max(1, int(float(step_r["value"]))) if (step_r and step_r["value"]) else 200
                prop_step_pay = str(round((float(v) / float(m_init)) * st_sz, 4))
                conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES ('every_200_views_payment', ?)", (prop_step_pay,))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('every_200_views_payment', ?)", (prop_step_pay,))
                _update_non_overridden_platform_field(conn, "every_200_views_payment", float(prop_step_pay))
            elif k == "every_200_views_payment":
                _update_non_overridden_platform_field(conn, "every_200_views_payment", float(v))
            elif k == "min_initial_views":
                _update_non_overridden_platform_field(conn, "min_initial_views", int(float(v)))
            elif k == "view_step_size":
                _update_non_overridden_platform_field(conn, "step_size", int(float(v)))
            elif k == "earning_duration_days":
                conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES ('view_tracking_days', ?)", (v,))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('view_tracking_days', ?)", (v,))
                _update_non_overridden_platform_field(conn, "earning_duration_days", int(float(v)))
            elif k == "view_tracking_days":
                conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES ('earning_duration_days', ?)", (v,))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('earning_duration_days', ?)", (v,))
                _update_non_overridden_platform_field(conn, "earning_duration_days", int(float(v)))
            elif k == "submission_window_hours":
                _update_non_overridden_platform_field(conn, "submission_window_hours", int(float(v)))
            elif k == "qualification_window_hours":
                _update_non_overridden_platform_field(conn, "qualification_window_hours", int(float(v)))
            elif k == "max_payable_views":
                _update_non_overridden_platform_field(conn, "max_payable_views", int(float(v)))
            elif k == "verification_link":
                _update_non_overridden_platform_field(conn, "verification_link", str(v))
    finally:
        conn.close()


def get_dynamic_message_record(msg_key: str) -> dict:
    k = str(msg_key or "").strip()
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM dynamic_messages WHERE msg_key = ? LIMIT 1", (k,)).fetchone()
        if not row:
            return {
                "msg_key": k,
                "content": "",
                "raw_text": "",
                "entities": [],
                "prev_content": "",
                "button_mode": "default",
                "custom_buttons": [],
                "version": 0
            }
        d = dict(row)
        try:
            d["entities"] = json.loads(d.get("entities_json") or "[]")
        except Exception:
            d["entities"] = []
        d["button_mode"] = str(d.get("button_mode") or "default").strip().lower()
        if d["button_mode"] not in ("default", "custom", "none"):
            d["button_mode"] = "default"
        try:
            d["custom_buttons"] = json.loads(d.get("custom_buttons_json") or "[]")
            if not isinstance(d["custom_buttons"], list):
                d["custom_buttons"] = []
        except Exception:
            d["custom_buttons"] = []
        return d
    finally:
        conn.close()


def save_dynamic_message_record(
    msg_key: str,
    content: str,
    raw_text: str = "",
    entities: list = None,
    updated_by: str = "admin",
    button_mode: str = None,
    custom_buttons: list = None
):
    k = str(msg_key or "").strip()
    if not k:
        raise ValueError("msg_key cannot be empty")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ent_json = json.dumps(entities or [], ensure_ascii=False)
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            prev = conn.execute("SELECT * FROM dynamic_messages WHERE msg_key = ?", (k,)).fetchone()
            prev_c = str(prev["content"] or "") if prev else ""
            prev_r = str(prev["raw_text"] or "") if prev else ""
            prev_e = str(prev["entities_json"] or "[]") if prev else "[]"
            cur_bmode = str((prev["button_mode"] if (prev and "button_mode" in prev.keys()) else "default") or "default")
            cur_cbtns = str((prev["custom_buttons_json"] if (prev and "custom_buttons_json" in prev.keys()) else "[]") or "[]")
            eff_bmode = str(button_mode).strip().lower() if button_mode is not None else cur_bmode
            if eff_bmode not in ("default", "custom", "none"):
                eff_bmode = "default"
            eff_cbtns_json = json.dumps(custom_buttons, ensure_ascii=False) if custom_buttons is not None else cur_cbtns
            next_v = (int(prev["version"] or 1) + 1) if prev else 1
            conn.execute("""
                INSERT OR REPLACE INTO dynamic_messages (
                    msg_key, content, raw_text, entities_json,
                    prev_content, prev_raw_text, prev_entities_json,
                    button_mode, custom_buttons_json,
                    version, updated_by, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                k, str(content or ""), str(raw_text or ""), ent_json,
                prev_c, prev_r, prev_e,
                eff_bmode, eff_cbtns_json,
                next_v, str(updated_by), now_str
            ))
    finally:
        conn.close()


def set_dynamic_message_button_config(
    msg_key: str,
    button_mode: str = "default",
    custom_buttons: list = None,
    updated_by: str = "admin",
    conn: sqlite3.Connection = None
) -> dict:
    k = str(msg_key or "").strip()
    if not k:
        raise ValueError("msg_key cannot be empty")
    b_mode = str(button_mode or "default").strip().lower()
    if b_mode not in ("default", "custom", "none"):
        b_mode = "default"
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = conn.execute("SELECT * FROM dynamic_messages WHERE msg_key = ?", (k,)).fetchone()
            cur_btns = []
            if row and "custom_buttons_json" in row.keys():
                try:
                    cur_btns = json.loads(row["custom_buttons_json"] or "[]")
                except Exception:
                    cur_btns = []
            eff_btns = custom_buttons if custom_buttons is not None else cur_btns
            btns_json = json.dumps(eff_btns, ensure_ascii=False)
            if row:
                conn.execute(
                    "UPDATE dynamic_messages SET button_mode = ?, custom_buttons_json = ?, updated_by = ?, updated_at = ? WHERE msg_key = ?",
                    (b_mode, btns_json, str(updated_by), now_str, k)
                )
            else:
                conn.execute("""
                    INSERT INTO dynamic_messages (
                        msg_key, content, raw_text, entities_json,
                        prev_content, prev_raw_text, prev_entities_json,
                        button_mode, custom_buttons_json, version, updated_by, updated_at
                    ) VALUES (?, '', '', '[]', '', '', '[]', ?, ?, 1, ?, ?)
                """, (k, b_mode, btns_json, str(updated_by), now_str))
            return {"msg_key": k, "button_mode": b_mode, "custom_buttons": eff_btns}
        if own_conn:
            with begin_immediate_transaction(conn):
                return _exec()
        return _exec()
    finally:
        if own_conn:
            conn.close()


def rollback_dynamic_message_record(msg_key: str, updated_by: str = "admin") -> dict:
    k = str(msg_key or "").strip()
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            row = conn.execute("SELECT * FROM dynamic_messages WHERE msg_key = ?", (k,)).fetchone()
            if not row or not row["prev_content"]:
                return {"ok": False, "msg_key": k, "content": row["content"] if row else ""}
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            restored_c = str(row["prev_content"])
            restored_r = str(row["prev_raw_text"] or "")
            restored_e = str(row["prev_entities_json"] or "[]")
            conn.execute("""
                UPDATE dynamic_messages
                SET content = ?, raw_text = ?, entities_json = ?,
                    prev_content = ?, prev_raw_text = ?, prev_entities_json = ?,
                    version = COALESCE(version, 1) + 1, updated_by = ?, updated_at = ?
                WHERE msg_key = ?
            """, (
                restored_c, restored_r, restored_e,
                str(row["content"] or ""), str(row["raw_text"] or ""), str(row["entities_json"] or "[]"),
                str(updated_by), now_str, k
            ))
            return {"ok": True, "msg_key": k, "content": restored_c}
    finally:
        conn.close()


def get_button_emoji_map(conn: sqlite3.Connection = None) -> dict:
    """
    Returns admin-saved custom emoji configuration per button.
    Preserves explicit empty string `""` when `emoji_customized == 1` so an intentionally cleared
    emoji configuration is NEVER treated as missing configuration.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        out = {}
        customized_keys = set()
        try:
            rows = conn.execute("SELECT * FROM button_labels").fetchall()
            for r in rows:
                rk = r.keys()
                bk = r["btn_key"]
                val = str(r["icon_custom_emoji_id"] or "").strip() if "icon_custom_emoji_id" in rk else ""
                em_cust = int(r["emoji_customized"] or 0) if "emoji_customized" in rk else (1 if val else 0)
                if em_cust == 1 or val:
                    out[bk] = val
                    customized_keys.add(bk)
        except Exception:
            pass
        try:
            rows_s = conn.execute("SELECT btn_key, icon_custom_emoji_id FROM button_styles").fetchall()
            for r in rows_s:
                bk = r["btn_key"]
                val = str(r["icon_custom_emoji_id"] or "").strip()
                if bk not in customized_keys and val:
                    out[bk] = val
        except Exception:
            pass
        return out
    finally:
        if own_conn:
            conn.close()


def set_button_custom_emoji(btn_key: str, custom_emoji_id: str, conn: sqlite3.Connection = None):
    k = str(btn_key or "").strip()
    c_id = re.sub(r"[^0-9]", "", str(custom_emoji_id or "").strip())
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            row_l = conn.execute("SELECT label FROM button_labels WHERE btn_key = ?", (k,)).fetchone()
            if row_l:
                conn.execute(
                    "UPDATE button_labels SET icon_custom_emoji_id = ?, emoji_customized = 1 WHERE btn_key = ?",
                    (c_id, k)
                )
            else:
                conn.execute(
                    "INSERT INTO button_labels (btn_key, label, icon_custom_emoji_id, emoji_customized) VALUES (?, '', ?, 1)",
                    (k, c_id)
                )
            row_s = conn.execute("SELECT style FROM button_styles WHERE btn_key = ?", (k,)).fetchone()
            if row_s:
                conn.execute("UPDATE button_styles SET icon_custom_emoji_id = ? WHERE btn_key = ?", (c_id, k))
            conn.execute("UPDATE custom_buttons SET custom_emoji_id = ? WHERE btn_key = ?", (c_id, k))
        if own_conn:
            with begin_immediate_transaction(conn):
                _exec()
        else:
            _exec()
    finally:
        if own_conn:
            conn.close()


def set_button_visibility(btn_key: str, is_visible: bool, conn: sqlite3.Connection = None):
    k = str(btn_key or "").strip()
    vis_int = 1 if is_visible else 0
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            row_l = conn.execute("SELECT btn_key FROM button_labels WHERE btn_key = ?", (k,)).fetchone()
            if row_l:
                conn.execute("UPDATE button_labels SET is_visible = ? WHERE btn_key = ?", (vis_int, k))
            else:
                conn.execute("INSERT INTO button_labels (btn_key, label, is_visible) VALUES (?, '', ?)", (k, vis_int))
        if own_conn:
            with begin_immediate_transaction(conn):
                _exec()
        else:
            _exec()
    finally:
        if own_conn:
            conn.close()


def get_button_visibility_map(conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        out = {}
        for r in conn.execute("SELECT btn_key, COALESCE(is_visible, 1) as is_vis FROM button_labels").fetchall():
            out[str(r["btn_key"])] = bool(int(r["is_vis"]) == 1)
        return out
    except Exception:
        return {}
    finally:
        if own_conn:
            conn.close()


def set_button_design_style(btn_key: str, design_style: str, conn: sqlite3.Connection = None):
    k = str(btn_key or "").strip()
    d_st = str(design_style or "normal").strip()
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            row_l = conn.execute("SELECT label FROM button_labels WHERE btn_key = ?", (k,)).fetchone()
            if row_l:
                conn.execute("UPDATE button_labels SET design_style = ? WHERE btn_key = ?", (d_st, k))
            else:
                conn.execute("INSERT INTO button_labels (btn_key, label, design_style) VALUES (?, '', ?)", (k, d_st))
            row_s = conn.execute("SELECT style FROM button_styles WHERE btn_key = ?", (k,)).fetchone()
            if row_s:
                conn.execute("UPDATE button_styles SET design_style = ? WHERE btn_key = ?", (d_st, k))
            conn.execute("UPDATE custom_buttons SET design_style = ? WHERE btn_key = ?", (d_st, k))
        if own_conn:
            with begin_immediate_transaction(conn):
                _exec()
        else:
            _exec()
    finally:
        if own_conn:
            conn.close()


def log_audit_event(actor_id: str, action: str, details: str = "", target_user_id: str = "", conn: sqlite3.Connection = None):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        sql = """
            INSERT INTO audit_logs (actor_id, target_user_id, action, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (str(actor_id), str(target_user_id or ""), str(action), str(details), now_str)
        if own_conn:
            with begin_immediate_transaction(conn):
                conn.execute(sql, params)
        else:
            conn.execute(sql, params)
    finally:
        if own_conn:
            conn.close()


def get_platform_criteria(platform: str, conn: sqlite3.Connection = None) -> dict:
    """Fetches exact platform criteria configured in Admin Panel (`platform_criteria` table)."""
    p = str(platform or "youtube").lower().strip()
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        row = conn.execute("SELECT * FROM platform_criteria WHERE platform = ?", (p,)).fetchone()
        if row:
            data = dict(row)
            try:
                ov = json.loads(data.get("custom_overrides_json") or "{}")
            except Exception:
                ov = {}
            data["_overrides"] = ov
            if data.get("max_payable_views") is None:
                data["max_payable_views"] = int(get_setting("max_payable_views", "5000000") or 5000000)
            if data.get("every_200_views_payment") is None:
                data["every_200_views_payment"] = round(float(data.get("rate_per_1k", 15.0)) * 0.2, 2)
            if data.get("min_initial_views") is None:
                data["min_initial_views"] = int(get_setting("min_initial_views", "1000") or 1000)
            if data.get("step_size") is None:
                data["step_size"] = int(get_setting("view_step_size", "200") or 200)
            if data.get("earning_duration_days") is None:
                data["earning_duration_days"] = int(get_setting("earning_duration_days", "5") or 5)
            if data.get("submission_window_hours") is None:
                data["submission_window_hours"] = int(get_setting("submission_window_hours", "72") or 72)
            if data.get("qualification_window_hours") is None:
                data["qualification_window_hours"] = int(get_setting("qualification_window_hours", "120") or 120)
            if not data.get("verification_link"):
                data["verification_link"] = str(get_setting("verification_link", "") or "")
            if data.get("min_total_videos") is None or int(data.get("min_total_videos") or 0) <= 0:
                data["min_total_videos"] = max(1, int(data.get("qualifying_videos") or 2))
            return data
    finally:
        if own_conn:
            conn.close()

    return {
        "platform": p,
        "min_subs": 200,
        "min_total_videos": 8,
        "qualifying_videos": 2,
        "min_views": 1000,
        "max_accounts": 3,
        "min_initial_views": 1000,
        "rate_per_1k": 15.0,
        "every_200_views_payment": 3.0,
        "max_payable_views": 5000000,
        "step_size": 200,
        "earning_duration_days": 5,
        "submission_window_hours": 72,
        "qualification_window_hours": 120,
        "verification_link": "",
        "custom_overrides_json": "{}",
        "_overrides": {}
    }


def update_platform_criteria(platform: str, field: str, value):
    """Validates finite numbers (or verification_link string) and records per-platform overrides."""
    if field == "verification_link":
        clean_link = "" if str(value or "").strip().lower() in ("none", "nane", "clear", "0") else str(value or "").strip()
        p = str(platform or "youtube").lower().strip()
        conn = get_connection()
        try:
            with begin_immediate_transaction(conn):
                if p in ("all", "global"):
                    conn.execute("UPDATE platform_criteria SET verification_link = ?", (clean_link,))
                    conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES ('verification_link', ?)", (clean_link,))
                    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('verification_link', ?)", (clean_link,))
                else:
                    row = conn.execute("SELECT custom_overrides_json FROM platform_criteria WHERE platform = ?", (p,)).fetchone()
                    try:
                        ov = json.loads((row["custom_overrides_json"] if row else "{}") or "{}")
                    except Exception:
                        ov = {}
                    ov["verification_link"] = bool(clean_link)
                    conn.execute(
                        "UPDATE platform_criteria SET verification_link = ?, custom_overrides_json = ? WHERE platform = ?",
                        (clean_link, json.dumps(ov), p)
                    )
        finally:
            conn.close()
        return

    allowed_fields = {
        "min_subs": (1, 100000000, int),
        "min_total_videos": (1, 10000, int),
        "qualifying_videos": (1, 1000, int),
        "min_views": (1, 1000000000, int),
        "max_accounts": (1, 100, int),
        "min_initial_views": (1, 100000000, int),
        "rate_per_1k": (0.01, 100000.0, float),
        "every_200_views_payment": (0.01, 50000.0, float),
        "max_payable_views": (0, 1000000000, int),
        "step_size": (1, 1000000, int),
        "earning_duration_days": (1, 3650, int),
        "submission_window_hours": (1, 87600, int),
        "qualification_window_hours": (1, 87600, int),
    }
    if field not in allowed_fields:
        raise ValueError(f"Invalid criteria field: {field}")

    min_v, max_v, cast_fn = allowed_fields[field]
    try:
        raw_flt = float(str(value).strip())
    except Exception as exc:
        raise ValueError(f"Invalid value for {field}: {value}") from exc
    if not math.isfinite(raw_flt):
        raise ValueError(f"Non-finite value (NaN/Infinity) is not allowed for {field}")
    clean_val = cast_fn(raw_flt) if cast_fn is int else round(raw_flt, 4)
    if clean_val < min_v or clean_val > max_v:
        raise ValueError(f"{field} must be between {min_v} and {max_v}")

    p = str(platform or "youtube").lower().strip()
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            if p in ("all", "global"):
                conn.execute(f"UPDATE platform_criteria SET {field} = ?", (clean_val,))
                if field == "max_payable_views":
                    conn.execute("INSERT OR REPLACE INTO dynamic_settings (key, value) VALUES ('max_payable_views', ?)", (str(clean_val),))
                    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('max_payable_views', ?)", (str(clean_val),))
            else:
                row = conn.execute("SELECT min_initial_views, step_size, rate_per_1k, custom_overrides_json FROM platform_criteria WHERE platform = ?", (p,)).fetchone()
                try:
                    ov = json.loads((row["custom_overrides_json"] if row else "{}") or "{}")
                except Exception:
                    ov = {}
                ov[field] = True
                if field == "rate_per_1k":
                    m_init = max(1, int((row["min_initial_views"] if row else 1000) or 1000))
                    st_sz = max(1, int((row["step_size"] if row else 200) or 200))
                    prop_every = round((float(clean_val) / float(m_init)) * st_sz, 4)
                    conn.execute(
                        "UPDATE platform_criteria SET rate_per_1k = ?, every_200_views_payment = ?, custom_overrides_json = ? WHERE platform = ?",
                        (clean_val, prop_every, json.dumps(ov), p)
                    )
                elif field == "step_size" and not ov.get("every_200_views_payment"):
                    m_init = max(1, int((row["min_initial_views"] if row else 1000) or 1000))
                    r_1k = float((row["rate_per_1k"] if row else 15.0) or 15.0)
                    prop_every = round((r_1k / float(m_init)) * float(clean_val), 4)
                    conn.execute(
                        "UPDATE platform_criteria SET step_size = ?, every_200_views_payment = ?, custom_overrides_json = ? WHERE platform = ?",
                        (clean_val, prop_every, json.dumps(ov), p)
                    )
                elif field == "earning_duration_days" and not ov.get("qualification_window_hours"):
                    qual_hrs = int(clean_val) * 24
                    conn.execute(
                        "UPDATE platform_criteria SET earning_duration_days = ?, qualification_window_hours = ?, custom_overrides_json = ? WHERE platform = ?",
                        (clean_val, qual_hrs, json.dumps(ov), p)
                    )
                else:
                    conn.execute(
                        f"UPDATE platform_criteria SET {field} = ?, custom_overrides_json = ? WHERE platform = ?",
                        (clean_val, json.dumps(ov), p)
                    )
    finally:
        conn.close()


def check_and_lock_profile_identity(
    user_id: str,
    platform: str,
    profile_handle: str,
    profile_url: str = "",
    conn: sqlite3.Connection = None
) -> tuple:
    """
    Locks a verified social profile (`canonical_profile_id`) to a single Telegram `user_id`.
    If the previous owner deleted their account (`status == 'deleted'`), releases the lock so the channel can be re-verified.
    """
    uid = str(user_id).strip()
    p = str(platform or "").lower().strip()
    h = _normalize_handle(profile_handle, profile_url)
    canon_id = canonicalize_profile_identity(p, h, profile_url)
    if not canon_id:
        return False, "প্রোফাইলের স্থায়ী পরিচয় (canonical_profile_id) শনাক্ত করা যায়নি!"

    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            row = conn.execute(
                "SELECT user_id, canonical_profile_id FROM profile_identity_locks WHERE canonical_profile_id = ? OR (platform = ? AND profile_handle = ?) LIMIT 1",
                (canon_id, p, h)
            ).fetchone()
            if row and str(row["user_id"]) != uid:
                other_uid = str(row["user_id"])
                u_other = conn.execute(
                    "SELECT registered, COALESCE(status, 'active') as status, COALESCE(last_active_ts, 0) as last_active_ts FROM users WHERE user_id = ? LIMIT 1",
                    (other_uid,)
                ).fetchone()
                is_active_owner = False
                if u_other:
                    if u_other["status"] != "deleted":
                        if int(u_other["registered"] or 0) == 1:
                            is_active_owner = True
                        elif (now_ts - float(u_other["last_active_ts"] or 0)) < 86400:
                            is_active_owner = True
                if is_active_owner:
                    return False, "এই প্রোফাইল/চ্যানেলটি অন্য একটি টেলিগ্রাম অ্যাকাউন্টের সাথে ইতিমধ্যে যুক্ত (Identity Locked) রয়েছে! দ্বিতীয়বার অন্য অ্যাকাউন্টে যুক্ত করা যাবে না।"
                conn.execute(
                    "DELETE FROM profile_identity_locks WHERE canonical_profile_id = ? OR (platform = ? AND profile_handle = ?)",
                    (canon_id, p, h)
                )
                conn.execute(
                    "DELETE FROM user_platforms WHERE user_id = ? AND platform = ? AND profile_handle = ?",
                    (other_uid, p, h)
                )
                row = None

            existing_up = conn.execute(
                "SELECT user_id FROM user_platforms WHERE platform = ? AND profile_handle = ? LIMIT 1",
                (p, h)
            ).fetchone()
            if existing_up and str(existing_up["user_id"]) != uid:
                return False, "এই প্রোফাইল/চ্যানেলটি ইতিমধ্যে অন্য একজন ইউজারের অ্যাকাউন্টে ভেরিফাইড রয়েছে!"

            if row and str(row["user_id"]) == uid:
                conn.execute(
                    "UPDATE profile_identity_locks SET profile_url = ?, updated_at = ? WHERE canonical_profile_id = ?",
                    (str(profile_url or ""), now_str, canon_id)
                )
            else:
                conn.execute("""
                    INSERT INTO profile_identity_locks (
                        canonical_profile_id, platform, profile_handle, profile_url, user_id, locked_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (canon_id, p, h, str(profile_url or ""), uid, now_str, now_str))
            return True, canon_id

        with begin_immediate_transaction(conn):
            return _exec()
    except sqlite3.IntegrityError:
        return False, "এই প্রোফাইলটি অন্য একটি টেলিগ্রাম অ্যাকাউন্টের সাথে লক করা রয়েছে!"
    finally:
        if own_conn:
            conn.close()


def check_and_lock_user_identity(
    user_id: str,
    phone: str = "",
    app_uid: str = "",
    commit_lock: bool = True,
    conn: sqlite3.Connection = None
) -> tuple:
    """User Identity Lock (`user_identity_locks`) for Payment Number (`01...`) and Battle Club UID (`#107` / `#1007`)."""
    uid = str(user_id).strip()
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _is_other_owner_active(other_uid: str) -> bool:
            u_other = conn.execute(
                "SELECT registered, COALESCE(status, 'active') as status, COALESCE(last_active_ts, 0) as last_active_ts FROM users WHERE user_id = ? LIMIT 1",
                (str(other_uid),)
            ).fetchone()
            if not u_other or u_other["status"] == "deleted":
                return False
            if int(u_other["registered"] or 0) == 1:
                return True
            return (now_ts - float(u_other["last_active_ts"] or 0)) < 86400

        def _exec():
            if phone:
                norm_ph = normalize_bd_payment_number(phone, allow_rocket_12=True) or re.sub(r"[^0-9+]", "", str(phone)).strip()
                if not norm_ph or len(norm_ph) < 11:
                    return False, "সঠিক পেমেন্ট নাম্বার (01XXXXXXXXX) প্রদান করুন!"
                lock_ph = conn.execute(
                    "SELECT user_id FROM user_identity_locks WHERE lock_type = 'payment_number' AND canonical_value = ? LIMIT 1",
                    (norm_ph,)
                ).fetchone()
                if lock_ph and str(lock_ph["user_id"]) != uid:
                    if _is_other_owner_active(str(lock_ph["user_id"])):
                        return False, "এই পেমেন্ট নাম্বারটি ইতিমধ্যে অন্য একটি টেলিগ্রাম অ্যাকাউন্টে যুক্ত রয়েছে!"
                    conn.execute(
                        "DELETE FROM user_identity_locks WHERE lock_type = 'payment_number' AND canonical_value = ?",
                        (norm_ph,)
                    )
                dup_u_ph = conn.execute(
                    "SELECT user_id FROM users WHERE (phone = ? OR bkash_number = ? OR nagad_number = ? OR rocket_number = ?) AND user_id != ? AND registered = 1 AND COALESCE(status, 'active') != 'deleted' LIMIT 1",
                    (norm_ph, norm_ph, norm_ph, norm_ph, uid)
                ).fetchone()
                if dup_u_ph:
                    return False, "এই পেমেন্ট নাম্বারটি ইতিমধ্যে অন্য একটি অ্যাকাউন্টে যুক্ত রয়েছে!"
                if commit_lock:
                    conn.execute("""
                        INSERT OR IGNORE INTO user_identity_locks (
                            lock_type, canonical_value, user_id, locked_at, updated_at
                        ) VALUES ('payment_number', ?, ?, ?, ?)
                    """, (norm_ph, uid, now_str, now_str))

            if app_uid:
                norm_uid = normalize_permanent_app_uid(app_uid, enforce_bc_prefix=False)
                canon_uid = canonicalize_app_uid(app_uid)
                if not norm_uid or len(norm_uid) < 2:
                    return False, "সঠিক Battle Club UID (# সহ সংখ্যা, যেমন #107 বা #1007) প্রদান করুন!"
                lock_u = conn.execute(
                    "SELECT user_id FROM user_identity_locks WHERE lock_type = 'app_uid' AND LOWER(canonical_value) IN (LOWER(?), LOWER(?)) LIMIT 1",
                    (norm_uid, canon_uid)
                ).fetchone()
                if lock_u and str(lock_u["user_id"]) != uid:
                    if _is_other_owner_active(str(lock_u["user_id"])):
                        return False, "এই Battle Club UID-টি অন্য একটি টেলিগ্রাম অ্যাকাউন্টে স্থায়ীভাবে যুক্ত রয়েছে!"
                    conn.execute(
                        "DELETE FROM user_identity_locks WHERE lock_type = 'app_uid' AND LOWER(canonical_value) IN (LOWER(?), LOWER(?))",
                        (norm_uid, canon_uid)
                    )
                dup_u_app = conn.execute(
                    "SELECT user_id FROM users WHERE LOWER(app_uid) IN (LOWER(?), LOWER(?)) AND user_id != ? AND registered = 1 AND COALESCE(status, 'active') != 'deleted' LIMIT 1",
                    (norm_uid, canon_uid, uid)
                ).fetchone()
                if dup_u_app:
                    return False, "এই Battle Club UID-টি অন্য একটি টেলিগ্রাম অ্যাকাউন্টে ইতিমধ্যে ব্যবহৃত হয়েছে!"
                if commit_lock:
                    for val in dict.fromkeys([canon_uid, norm_uid]):
                        if val:
                            conn.execute("""
                                INSERT OR IGNORE INTO user_identity_locks (
                                    lock_type, canonical_value, user_id, locked_at, updated_at
                                ) VALUES ('app_uid', ?, ?, ?, ?)
                            """, (val, uid, now_str, now_str))
            return True, "OK"

        with begin_immediate_transaction(conn):
            return _exec()
    except sqlite3.IntegrityError:
        return False, "প্রদত্ত পেমেন্ট নাম্বার বা Battle Club UID অন্য একটি অ্যাকাউন্টে যুক্ত রয়েছে!"
    finally:
        if own_conn:
            conn.close()


def is_video_submitted_globally(platform: str, canonical_video_id: str, video_url: str = "", conn: sqlite3.Connection = None) -> dict:
    """
    Checks if `(platform, canonical_video_id)` or normalized `video_url` exists in ANY platform or record
    in either `videos` or `video_submission_locks`.
    """
    p = str(platform or "").lower().strip()
    cid = str(canonical_video_id or "").strip()
    norm_u = _normalize_video_url_key(video_url) if video_url else ""
    if not p and not cid and not norm_u:
        return None
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        if cid:
            row_v = conn.execute(
                "SELECT sub_id, user_id, status FROM videos WHERE canonical_video_id = ? LIMIT 1",
                (cid,)
            ).fetchone()
            if row_v:
                return dict(row_v)
            row_l = conn.execute(
                "SELECT sub_id, first_user_id as user_id, last_status as status FROM video_submission_locks WHERE canonical_video_id = ? LIMIT 1",
                (cid,)
            ).fetchone()
            if row_l:
                return dict(row_l)
        if norm_u:
            for r in conn.execute("SELECT sub_id, user_id, status, url FROM videos").fetchall():
                if _normalize_video_url_key(r["url"]) == norm_u:
                    return dict(r)
            for r in conn.execute("SELECT sub_id, first_user_id as user_id, last_status as status, video_url FROM video_submission_locks").fetchall():
                if _normalize_video_url_key(r["video_url"]) == norm_u:
                    return dict(r)
        return None
    finally:
        if own_conn:
            conn.close()


def register_video_submission_lock(
    platform: str,
    canonical_video_id: str,
    sub_id_or_url: str = "",
    user_id: str = "",
    video_url: str = "",
    status: str = "pending",
    sub_id: str = None,
    conn: sqlite3.Connection = None
):
    """Permanently records a submitted video's canonical identity without committing a borrowed `conn`."""
    p = str(platform or "").lower().strip()
    cid = str(canonical_video_id or "").strip()
    if not p or not cid:
        return
    if sub_id is not None:
        eff_sub_id = str(sub_id)
        eff_url = str(sub_id_or_url)
    else:
        eff_sub_id = str(sub_id_or_url)
        eff_url = str(video_url)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        sql = """
            INSERT OR REPLACE INTO video_submission_locks (
                platform, canonical_video_id, sub_id, first_user_id, video_url, last_status, locked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (p, cid, eff_sub_id, str(user_id or ""), eff_url, str(status or "submitted"), now_str)
        if own_conn:
            with begin_immediate_transaction(conn):
                conn.execute(sql, params)
        else:
            conn.execute(sql, params)
    finally:
        if own_conn:
            conn.close()


def save_video_traffic_and_external_links(
    sub_id: str,
    user_id: str,
    platform: str,
    traffic_breakdown: dict,
    external_links: list = None,
    conn: sqlite3.Connection = None
) -> list:
    """
    Stores traffic source analytics and external link lifecycle:
    - Never fabricates percentages when analytics data is unavailable (`traffic_data_available = 0`, `traffic_source_status = 'unknown'`).
    - Stores both `original_url` (`source_url`) and `final_url` (`resolved_url`).
    - Deactivates (`is_active = 0`) any previously active external links that are no longer present in the new scan.
    - Preserves full link history in `video_external_link_history`.
    """
    sid = str(sub_id or "").strip()
    uid = str(user_id or "").strip()
    plat = str(platform or "").lower().strip()
    if not sid:
        return []

    tb = dict(traffic_breakdown or {})
    data_avail = 1 if tb.get("traffic_data_available") else 0
    src_status = str(tb.get("traffic_source_status") or ("verified_analytics" if data_avail else "unknown"))
    ch_pct = round(float(tb.get("channel_page_pct") or 0.0), 2) if data_avail else 0.0
    ch_v = max(0, int(tb.get("channel_page_views") or 0)) if data_avail else 0
    sr_pct = round(float(tb.get("search_pct") or 0.0), 2) if data_avail else 0.0
    sr_v = max(0, int(tb.get("search_views") or 0)) if data_avail else 0
    ex_pct = round(float(tb.get("external_pct") or 0.0), 2)
    ex_v = max(0, int(tb.get("external_views") or 0))

    ext_list = list(external_links if external_links is not None else tb.get("external_links", []))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            current_scan_orig_urls = set()
            saved_active_links = []

            for idx, item in enumerate(ext_list):
                if not isinstance(item, dict):
                    continue
                orig_u = str(item.get("original_url") or item.get("source_url") or "").strip()
                final_u = str(item.get("final_url") or item.get("resolved_url") or orig_u).strip()
                if not orig_u:
                    continue
                dom = normalize_domain_host(item.get("domain") or final_u or orig_u)
                if not dom:
                    continue
                current_scan_orig_urls.add(orig_u)
                v_pct = round(float(item.get("views_pct") or 0.0), 2)
                v_cnt = max(0, int(item.get("views_count") or 0))

                existing = conn.execute(
                    "SELECT * FROM video_external_links WHERE sub_id = ? AND (original_url = ? OR source_url = ?) LIMIT 1",
                    (sid, orig_u, orig_u)
                ).fetchone()
                if existing:
                    ext_id = existing["ext_id"]
                    st_val = existing["status"]
                    notified_val = int(existing["notified"] or 0)
                    first_seen = existing["first_seen_at"] or existing["created_at"] or now_str
                    conn.execute("""
                        UPDATE video_external_links
                        SET source_url = ?,
                            original_url = ?,
                            final_url = ?,
                            domain = ?,
                            views_pct = ?,
                            views_count = ?,
                            is_active = 1,
                            last_seen_at = ?,
                            deactivated_at = ''
                        WHERE ext_id = ?
                    """, (orig_u, orig_u, final_u, dom, v_pct, v_cnt, now_str, ext_id))
                    event_t = "scan_updated"
                else:
                    ext_id = str(item.get("ext_id") or f"EXT_{int(time.time()*1000)}_{idx}_{secrets.token_hex(3).upper()}")
                    st_val = str(item.get("status") or "pending")
                    notified_val = int(item.get("notified") or 0)
                    first_seen = now_str
                    conn.execute("""
                        INSERT INTO video_external_links (
                            ext_id, sub_id, user_id, platform, source_url, original_url, final_url, domain,
                            views_pct, views_count, status, is_active, notified,
                            first_seen_at, last_seen_at, deactivated_at, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, '', ?)
                    """, (
                        ext_id, sid, uid, plat, orig_u, orig_u, final_u, dom,
                        v_pct, v_cnt, st_val, notified_val, first_seen, now_str, now_str
                    ))
                    event_t = "scan_detected"

                conn.execute("""
                    INSERT INTO video_external_link_history (
                        ext_id, sub_id, user_id, platform, original_url, final_url, domain,
                        views_pct, views_count, is_active, event_type, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (ext_id, sid, uid, plat, orig_u, final_u, dom, v_pct, v_cnt, event_t, now_str))

                saved_active_links.append({
                    "ext_id": ext_id,
                    "sub_id": sid,
                    "user_id": uid,
                    "platform": plat,
                    "source_url": orig_u,
                    "original_url": orig_u,
                    "final_url": final_u,
                    "domain": dom,
                    "views_pct": v_pct,
                    "views_count": v_cnt,
                    "status": st_val,
                    "is_active": 1,
                    "notified": notified_val
                })

            prev_active_rows = conn.execute(
                "SELECT * FROM video_external_links WHERE sub_id = ? AND COALESCE(is_active, 1) = 1",
                (sid,)
            ).fetchall()
            for par in prev_active_rows:
                p_orig = str(par["original_url"] or par["source_url"] or "")
                if p_orig not in current_scan_orig_urls:
                    conn.execute(
                        "UPDATE video_external_links SET is_active = 0, deactivated_at = ? WHERE ext_id = ?",
                        (now_str, par["ext_id"])
                    )
                    conn.execute("""
                        INSERT INTO video_external_link_history (
                            ext_id, sub_id, user_id, platform, original_url, final_url, domain,
                            views_pct, views_count, is_active, event_type, recorded_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'deactivated_missing_in_scan', ?)
                    """, (
                        par["ext_id"], sid, uid, plat,
                        str(par["original_url"] or par["source_url"] or ""),
                        str(par["final_url"] or par["source_url"] or ""),
                        str(par["domain"] or ""),
                        float(par["views_pct"] or 0.0),
                        int(par["views_count"] or 0),
                        now_str
                    ))

            conn.execute("""
                UPDATE videos
                SET traffic_data_available = ?,
                    traffic_source_status = ?,
                    channel_page_pct = ?,
                    channel_page_views = ?,
                    search_pct = ?,
                    search_views = ?,
                    external_pct = ?,
                    external_views = ?,
                    traffic_sources_json = ?,
                    external_links_json = ?
                WHERE sub_id = ?
            """, (
                data_avail, src_status, ch_pct, ch_v, sr_pct, sr_v, ex_pct, ex_v,
                json.dumps(tb, ensure_ascii=False),
                json.dumps(saved_active_links, ensure_ascii=False),
                sid
            ))
            return saved_active_links

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def get_video_external_links(
    sub_id: str = None,
    platform: str = None,
    status: str = None,
    active_only: bool = True,
    conn: sqlite3.Connection = None
) -> list:
    """Fetches external links for a video. By default returns only currently active links (`is_active = 1`)."""
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        clauses = []
        params = []
        if sub_id:
            clauses.append("sub_id = ?")
            params.append(str(sub_id))
        if platform and str(platform).lower() not in ("all", ""):
            clauses.append("LOWER(platform) = ?")
            params.append(str(platform).lower())
        if status and str(status).lower() not in ("all", ""):
            clauses.append("LOWER(status) = ?")
            params.append(str(status).lower())
        if active_only is True:
            clauses.append("COALESCE(is_active, 1) = 1")
        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = conn.execute(
            f"SELECT * FROM video_external_links {where_sql} ORDER BY COALESCE(is_active, 1) DESC, COALESCE(views_pct, 0) DESC, rowid ASC",
            tuple(params)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d.setdefault("original_url", d.get("source_url") or "")
            d.setdefault("final_url", d.get("source_url") or "")
            out.append(d)
        return out
    finally:
        if own_conn:
            conn.close()


def get_video_external_link_history(sub_id: str, conn: sqlite3.Connection = None) -> list:
    """Returns full historical scan & status records for a video's external links."""
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        rows = conn.execute(
            "SELECT * FROM video_external_link_history WHERE sub_id = ? ORDER BY id DESC",
            (str(sub_id),)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if own_conn:
            conn.close()


def mark_external_link_notified(ext_id: str, conn: sqlite3.Connection = None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        if own_conn:
            with begin_immediate_transaction(conn):
                conn.execute("UPDATE video_external_links SET notified = 1 WHERE ext_id = ?", (str(ext_id),))
        else:
            conn.execute("UPDATE video_external_links SET notified = 1 WHERE ext_id = ?", (str(ext_id),))
    finally:
        if own_conn:
            conn.close()


def generate_unique_bc_code(code_type: str = "general", user_id: str = "", ref_id: str = "", length: int = 6, conn=None) -> str:
    """
    Generates a globally unique `BC-XXXXXX` random code that has NEVER been issued before
    across Bio Codes, Video Submission Codes, Manual Verification Codes, or Profile Edit Codes.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        for _ in range(100):
            cand = generate_random_code("BC", length=length)
            exists = (
                conn.execute("SELECT 1 FROM used_random_codes WHERE code = ? LIMIT 1", (cand,)).fetchone()
                or conn.execute("SELECT 1 FROM users WHERE bio_verify_code = ? OR active_video_code = ? LIMIT 1", (cand, cand)).fetchone()
                or conn.execute("SELECT 1 FROM videos WHERE unique_code = ? LIMIT 1", (cand,)).fetchone()
                or conn.execute("SELECT 1 FROM manual_verification_codes WHERE code = ? LIMIT 1", (cand,)).fetchone()
            )
            if not exists:
                conn.execute(
                    "INSERT OR IGNORE INTO used_random_codes (code, code_type, user_id, ref_id, created_at) VALUES (?, ?, ?, ?, ?)",
                    (cand, str(code_type or "general"), str(user_id or ""), str(ref_id or ""), now_str)
                )
                if own_conn:
                    conn.commit()
                return cand
        fallback_c = generate_random_code("BC", length=length + 2)
        conn.execute(
            "INSERT OR IGNORE INTO used_random_codes (code, code_type, user_id, ref_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (fallback_c, str(code_type or "general"), str(user_id or ""), str(ref_id or ""), now_str)
        )
        if own_conn:
            conn.commit()
        return fallback_c
    finally:
        if own_conn:
            conn.close()


def create_manual_verification_code(
    admin_id: str,
    target_user_id: str = "",
    platform: str = "",
    profile_url: str = "",
    ttl_sec: int = 300
) -> dict:
    """Generates a single-use random code (`BC-XXXXXX`) with 5-minute TTL for manual platform verification or profile number update."""
    now_ts = time.time()
    eff_ttl = max(30, int(ttl_sec if (ttl_sec is not None and int(ttl_sec) > 0) else 300))
    exp_ts = now_ts + eff_ttl
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            code = generate_unique_bc_code("manual_verify", user_id=str(target_user_id or ""), conn=conn)
            conn.execute("""
                INSERT INTO manual_verification_codes (
                    code, target_user_id, platform, profile_url, created_by,
                    created_at_ts, expires_at_ts, used, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'active')
            """, (
                code, str(target_user_id or "").strip(), str(platform or "").lower().strip(),
                str(profile_url or "").strip(), str(admin_id), now_ts, exp_ts
            ))
            log_audit_event(
                admin_id, "Manual Verification Code Generated",
                f"One-time code {code} issued (target_user={target_user_id or 'any'}, platform={platform or 'any'}, ttl={eff_ttl}s)",
                target_user_id=str(target_user_id or ""),
                conn=conn
            )
        return {"code": code, "expires_at_ts": exp_ts, "ttl_sec": eff_ttl}
    finally:
        conn.close()


def consume_manual_verification_code(
    user_id: str,
    platform: str,
    profile_url: str,
    profile_handle: str,
    bio_code: str,
    raw_code: str,
    failure_reason: str = "",
    auto_approve: bool = True
) -> tuple:
    uid = str(user_id or "").strip()
    plat = str(platform or "").lower().strip()
    code_clean = str(raw_code or "").strip().upper()
    if not code_clean or not re.fullmatch(r"(?:BC|MVR)-[A-Z0-9]{6,10}", code_clean):
        return False, "সঠিক ফরম্যাটের র‍্যান্ডম কোড (যেমন BC-XXXXXX) প্রদান করুন!"

    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            row = conn.execute("SELECT * FROM manual_verification_codes WHERE UPPER(code) = ? LIMIT 1", (code_clean,)).fetchone()
            if not row:
                return False, "প্রদত্ত র‍্যান্ডম কোডটি সঠিক নয়! অ্যাডমিনের থেকে নতুন জেনারেট কোড নিন।"
            if int(row["used"] or 0) == 1 or row["status"] != "active":
                return False, "এই র‍্যান্ডম কোডটি ইতিমধ্যে ১ বার ব্যবহার করা হয়ে গেছে বা নিষ্ক্রিয়! নতুন করে অ্যাডমিনের থেকে আরেকটি র‍্যান্ডম কোড নিন।"
            exp_ts_row = float(row["expires_at_ts"] or 0.0) if "expires_at_ts" in row.keys() else 0.0
            if exp_ts_row > 0 and now_ts > exp_ts_row:
                conn.execute("UPDATE manual_verification_codes SET status = 'expired' WHERE code = ?", (row["code"],))
                return False, "এই র‍্যান্ডম কোডটির ৫ মিনিটের মেয়াদ শেষ হয়ে গেছে! অনুগ্রহ করে অ্যাডমিনের থেকে নতুন কোড নিন।"
            if row["target_user_id"] and str(row["target_user_id"]).strip() != uid:
                return False, "এই র‍্যান্ডম কোডটি আপনার অ্যাকাউন্টের জন্য ইস্যু করা হয়নি!"
            if row["platform"] and str(row["platform"]).lower().strip() not in ("", "any", plat):
                return False, f"এই র‍্যান্ডম কোডটি {plat.upper()} প্ল্যাটফর্মের জন্য নয়!"
            if row["profile_url"] and profile_url and _normalize_handle("", row["profile_url"]) != _normalize_handle("", profile_url):
                return False, "এই র‍্যান্ডম কোডটি অন্য একটি প্রোফাইল লিংকের জন্য ইস্যু করা হয়েছে!"

            clean_prof_u = str(profile_url or "").strip()
            is_synthetic_u = bool(
                not clean_prof_u
                or not clean_prof_u.startswith(("http://", "https://"))
                or f"@user_{uid}" in clean_prof_u
            )
            eff_handle = _normalize_handle(profile_handle, clean_prof_u)
            if not eff_handle or eff_handle.startswith("manual_") or eff_handle == f"user_{uid}":
                is_synthetic_u = True
                eff_handle = eff_handle or f"manual_{uid}_{plat}"

            if auto_approve:
                if is_synthetic_u:
                    return False, "সঠিক চ্যানেল বা প্রোফাইল লিংক ছাড়া ম্যানুয়াল কোড ভেরিফাই করা যাবে না! আগে আপনার প্রোফাইল লিংক দিন।"
                lock_ok, lock_info = check_and_lock_profile_identity(uid, plat, eff_handle, clean_prof_u, conn=conn)
                if not lock_ok:
                    return False, lock_info
                canon_id = lock_info
                crit = conn.execute("SELECT min_subs, max_accounts FROM platform_criteria WHERE platform = ? LIMIT 1", (plat,)).fetchone()
                max_acc = int(crit["max_accounts"] or 3) if crit else 3

                existing_up = conn.execute(
                    "SELECT user_id, subs_count FROM user_platforms WHERE platform = ? AND profile_handle = ?",
                    (plat, eff_handle)
                ).fetchone()
                if not existing_up:
                    cnt = conn.execute(
                        "SELECT COUNT(*) as c FROM user_platforms WHERE user_id = ? AND platform = ? AND verified = 1",
                        (uid, plat)
                    ).fetchone()["c"]
                    if cnt >= max_acc:
                        return False, f"আপনি এই প্ল্যাটফর্মে সর্বোচ্চ {max_acc}টি অ্যাকাউন্ট যুক্ত করতে পারবেন!"
                recorded_subs = int(existing_up["subs_count"] or 0) if existing_up else 0

                conn.execute("""
                    INSERT OR REPLACE INTO user_platforms (
                        user_id, platform, profile_url, profile_handle, canonical_profile_id,
                        display_name, subs_count, bio_code_used, verified, verification_state,
                        bio_missing_flag, last_bio_check_ts, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'MANUAL_VERIFIED', 0, ?, ?)
                """, (uid, plat, clean_prof_u, eff_handle, canon_id, f"{plat.upper()} ({eff_handle[:18]})", recorded_subs, str(bio_code or ""), now_ts, now_str))
                conn.execute(
                    "UPDATE users SET channel_url = CASE WHEN channel_url IS NULL OR channel_url = '' THEN ? ELSE channel_url END WHERE user_id = ?",
                    (clean_prof_u, uid)
                )

            cur = conn.execute(
                "UPDATE manual_verification_codes SET used = 1, used_by = ?, used_at_ts = ?, status = 'used' WHERE code = ? AND used = 0",
                (uid, now_ts, row["code"])
            )
            if cur.rowcount != 1:
                return False, "এই র‍্যান্ডম কোডটি ইতিমধ্যে ব্যবহৃত হয়েছে!"

            req_id = f"MVRQ_{int(now_ts*1000)}_{uid[-4:]}"
            req_status = "approved" if auto_approve else "pending"
            conn.execute("""
                INSERT INTO manual_verification_requests (
                    req_id, user_id, platform, profile_url, profile_handle, bio_code,
                    manual_code_used, decision_note, status, admin_id, created_at, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id, uid, plat, str(profile_url or ""), eff_handle,
                str(bio_code or ""), row["code"], str(failure_reason or ("Verified via Admin Manual Random Code" if auto_approve else "Submitted with Admin Random Code for Manual Approval")),
                req_status, str(row["created_by"] or "ADMIN"), now_str, now_str if auto_approve else ""
            ))
            log_audit_event(
                uid, "Manual Verification Completed via Random Code" if auto_approve else "Manual Verification Requested via Random Code",
                f"Used valid code {row['code']} for {plat} ({profile_url})",
                target_user_id=uid,
                conn=conn
            )
            return True, req_id
    finally:
        conn.close()


def get_manual_verification_requests(status: str = "pending") -> list:
    conn = get_connection()
    try:
        if status == "all":
            rows = conn.execute("SELECT * FROM manual_verification_requests ORDER BY rowid DESC LIMIT 50").fetchall()
        else:
            rows = conn.execute("SELECT * FROM manual_verification_requests WHERE status = ? ORDER BY rowid DESC LIMIT 50", (status,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def resolve_manual_verification_request(req_id: str, decision: str = None, admin_id: str = "admin", note: str = "", approve: bool = None) -> dict:
    eff_dec = ("approve" if approve else "reject") if approve is not None else str(decision or "approve")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            req = conn.execute("SELECT * FROM manual_verification_requests WHERE req_id = ? LIMIT 1", (str(req_id),)).fetchone()
            if not req:
                return {"ok": False, "reason": "Request not found"}
            if req["status"] != "pending":
                d = dict(req)
                return {"ok": True, "already_processed": True, "status": req["status"], "req": d, "request": d}

            uid = str(req["user_id"])
            plat = str(req["platform"]).lower().strip()
            p_url = str(req["profile_url"] or "")
            p_handle = _normalize_handle(req["profile_handle"], p_url) or f"manual_{uid}_{plat}"
            b_code = str(req["bio_code"] or "")

            if eff_dec == "approve":
                crit = conn.execute("SELECT min_subs, max_accounts FROM platform_criteria WHERE platform = ? LIMIT 1", (plat,)).fetchone()
                min_s = int(crit["min_subs"] or 200) if crit else 200
                max_acc = int(crit["max_accounts"] or 3) if crit else 3
                lock_ok, lock_info = check_and_lock_profile_identity(uid, plat, p_handle, p_url, conn=conn)
                if not lock_ok:
                    return {"ok": False, "reason": lock_info}
                canon_id = lock_info
                existing_up = conn.execute(
                    "SELECT user_id FROM user_platforms WHERE platform = ? AND profile_handle = ?",
                    (plat, p_handle)
                ).fetchone()
                if not existing_up:
                    cnt = conn.execute(
                        "SELECT COUNT(*) as c FROM user_platforms WHERE user_id = ? AND platform = ? AND verified = 1",
                        (uid, plat)
                    ).fetchone()["c"]
                    if cnt >= max_acc:
                        return {"ok": False, "reason": f"ইউজার ইতিমধ্যে {plat.upper()} প্ল্যাটফর্মে সর্বোচ্চ {max_acc}টি অ্যাকাউন্ট যুক্ত করেছেন!"}

                conn.execute("""
                    INSERT OR REPLACE INTO user_platforms (
                        user_id, platform, profile_url, profile_handle, canonical_profile_id,
                        display_name, subs_count, bio_code_used, verified, verification_state,
                        bio_missing_flag, last_bio_check_ts, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'VERIFIED', 0, ?, ?)
                """, (uid, plat, p_url, p_handle, canon_id, f"{plat.upper()} ({p_handle[:18]})", min_s, b_code, time.time(), now_str))
                conn.execute(
                    "UPDATE users SET channel_url = CASE WHEN channel_url IS NULL OR channel_url = '' THEN ? ELSE channel_url END, "
                    "channel_subs = CASE WHEN COALESCE(channel_subs, 0) = 0 THEN ? ELSE channel_subs END WHERE user_id = ?",
                    (p_url, min_s, uid)
                )
                conn.execute(
                    "UPDATE manual_verification_requests SET status = 'approved', admin_id = ?, decision_note = ?, processed_at = ? WHERE req_id = ?",
                    (str(admin_id), str(note or "Approved by Admin"), now_str, str(req_id))
                )
                log_audit_event(
                    admin_id, "Manual Platform Verification Approved",
                    f"Approved {req_id} for user {uid} ({plat}: {p_url})",
                    target_user_id=uid,
                    conn=conn
                )
                d = dict(req)
                d["status"] = "approved"
                return {"ok": True, "status": "approved", "req": d, "request": d}
            else:
                conn.execute(
                    "UPDATE manual_verification_requests SET status = 'rejected', admin_id = ?, decision_note = ?, processed_at = ? WHERE req_id = ?",
                    (str(admin_id), str(note or "Rejected by Admin"), now_str, str(req_id))
                )
                log_audit_event(
                    admin_id, "Manual Platform Verification Rejected",
                    f"Rejected {req_id} for user {uid} ({plat}: {p_url})",
                    target_user_id=uid,
                    conn=conn
                )
                d = dict(req)
                d["status"] = "rejected"
                return {"ok": True, "status": "rejected", "req": d, "request": d}
    finally:
        conn.close()


def get_user_platforms(user_id: str, platform: str = None) -> list:
    conn = get_connection()
    try:
        if platform:
            rows = conn.execute(
                "SELECT * FROM user_platforms WHERE user_id = ? AND platform = ? AND verified = 1 ORDER BY id ASC",
                (str(user_id), str(platform).lower().strip())
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM user_platforms WHERE user_id = ? AND verified = 1 ORDER BY id ASC",
                (str(user_id),)
            ).fetchall()
        out_plats = []
        for r in rows:
            d = dict(r)
            d.setdefault("canonical_id", d.get("canonical_profile_id") or d.get("profile_handle") or "")
            d.setdefault("canonical_profile_id", d.get("canonical_id") or "")
            d.setdefault("total_videos_count", int(d.get("total_videos_count") or 0))
            d.setdefault("videos_with_views_collected", int(d.get("videos_with_views_collected") or 0))
            d.setdefault("verification_completeness", str(d.get("verification_completeness") or "COMPLETE"))
            out_plats.append(d)
        return out_plats
    finally:
        conn.close()


def add_verified_user_platform(
    user_id: str,
    platform: str,
    profile_url: str,
    profile_handle: str,
    display_name: str,
    subs_count: int,
    bio_code_used: str,
    verification_state: str = "VERIFIED",
    total_videos_count: int = 0,
    qualifying_vids_count: int = 0,
    qualifying_views_total: int = 0,
    qualifying_views_list: list = None,
    videos_with_views_collected: int = None,
    verification_completeness: str = "COMPLETE",
    replace_existing_for_platform: bool = False,
    allow_same_user_reverify: bool = True
) -> tuple:
    p = str(platform).lower().strip()
    h = _normalize_handle(profile_handle, profile_url)

    crit = get_platform_criteria(p)
    max_acc = int(crit.get("max_accounts", 3))
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    v_collected = int(videos_with_views_collected if videos_with_views_collected is not None else (len(qualifying_views_list) if qualifying_views_list else total_videos_count))
    v_comp = str(verification_completeness or "COMPLETE")

    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            existing_owner = conn.execute(
                "SELECT user_id FROM user_platforms WHERE platform = ? AND profile_handle = ?",
                (p, h)
            ).fetchone()
            if existing_owner and str(existing_owner["user_id"]) != str(user_id):
                return False, "এই প্রোফাইল/চ্যানেলটি ইতিমধ্যে অন্য একজন ইউজারের অ্যাকাউন্টে ভেরিফাইড রয়েছে!"

            if existing_owner and str(existing_owner["user_id"]) == str(user_id) and not allow_same_user_reverify:
                return False, "এই চ্যানেল/প্রোফাইলটি ইতিমধ্যে আপনার অ্যাকাউন্টের সাথে যুক্ত করা আছে! একই অ্যাকাউন্ট দ্বিতীয়বার যুক্ত করা যাবে না।"

            if not (existing_owner and str(existing_owner["user_id"]) == str(user_id)):
                cnt = conn.execute(
                    "SELECT COUNT(*) as c FROM user_platforms WHERE user_id = ? AND platform = ? AND verified = 1",
                    (str(user_id), p)
                ).fetchone()["c"]
                if cnt >= max_acc:
                    return False, f"আপনার একাধিক অ্যাকাউন্ট আছে। লিমিট অনুযায়ী এই প্ল্যাটফর্মে সর্বোচ্চ {max_acc}টি পর্যন্তই অ্যাকাউন্ট যুক্ত করতে পারবেন, এর বেশি যুক্ত করা যাবে না!"

            lock_ok, lock_info = check_and_lock_profile_identity(
                user_id=str(user_id),
                platform=p,
                profile_handle=h,
                profile_url=profile_url,
                conn=conn
            )
            if not lock_ok:
                return False, lock_info
            canon_id = lock_info

            q_list_json = json.dumps(list(qualifying_views_list or []))
            if existing_owner and str(existing_owner["user_id"]) == str(user_id):
                conn.execute("""
                    UPDATE user_platforms
                    SET profile_url = ?, canonical_profile_id = ?, display_name = ?, subs_count = ?, bio_code_used = ?,
                        verified = ?, verification_state = ?, total_videos_count = ?,
                        videos_with_views_collected = ?, verification_completeness = ?,
                        qualifying_vids_count = ?, qualifying_views_total = ?, qualifying_views_list_json = ?,
                        last_bio_check_ts = ?, bio_missing_flag = 0
                    WHERE platform = ? AND profile_handle = ? AND user_id = ?
                """, (
                    profile_url, canon_id, display_name, int(subs_count or 0), bio_code_used,
                    1 if verification_state in ("VERIFIED", "MANUAL_VERIFIED", "PARTIAL_VERIFIED") else 0, "VERIFIED",
                    int(total_videos_count or 0), v_collected, v_comp,
                    int(qualifying_vids_count or 0), int(qualifying_views_total or 0), q_list_json,
                    now_ts, p, h, str(user_id)
                ))
                return True, "Updated"

            conn.execute("""
                INSERT INTO user_platforms (
                    user_id, platform, profile_url, profile_handle, canonical_profile_id, display_name, subs_count,
                    bio_code_used, verified, verification_state, total_videos_count,
                    videos_with_views_collected, verification_completeness,
                    qualifying_vids_count, qualifying_views_total, qualifying_views_list_json,
                    bio_missing_flag, last_bio_check_ts, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """, (
                str(user_id), p, profile_url, h, canon_id, display_name, int(subs_count or 0),
                bio_code_used, 1 if verification_state in ("VERIFIED", "MANUAL_VERIFIED", "PARTIAL_VERIFIED") else 0,
                "VERIFIED", int(total_videos_count or 0), v_collected, v_comp,
                int(qualifying_vids_count or 0), int(qualifying_views_total or 0), q_list_json,
                now_ts, now_str
            ))
        return True, "Added"
    except sqlite3.IntegrityError:
        return False, "এই প্রোফাইলটি ইতিমধ্যে অন্য অ্যাকাউন্টে ব্যবহৃত হয়েছে!"
    finally:
        conn.close()


def move_video_to_trash(sub_id: str, actor_id: str = "ADMIN", conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")
            register_video_submission_lock(
                v["platform"], v["canonical_video_id"], v["sub_id"], v["user_id"], v["url"], "trashed", conn=conn
            )
            if int(v["is_trashed"] or 0) == 1:
                return {
                    "sub_id": str(sub_id),
                    "already_trashed": True,
                    "active_warning": False,
                    "financial_reversal": 0.0
                }
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            was_active = bool(
                int(v["permanent_approved"] or 0) == 0
                and (v["admin_status"] == "approved" or v["bot_status"] in ("approved", "waiting_views"))
            )
            conn.execute("""
                UPDATE videos
                SET is_trashed = 1,
                    trashed_at = ?,
                    trashed_by = ?,
                    trash_previous_status = status,
                    trash_previous_bot_status = bot_status,
                    trash_previous_admin_status = admin_status
                WHERE sub_id = ?
            """, (now_str, str(actor_id), str(sub_id)))
            log_audit_event(
                actor_id, "Video Moved to Trash (No Reversal)",
                f"Video {sub_id} moved to Trash. Credited amount preserved: {float(v['credited_amount'] or v['reward'] or 0):.2f} BDT",
                target_user_id=str(v["user_id"]),
                conn=conn
            )
            return {
                "sub_id": str(sub_id),
                "user_id": str(v["user_id"]),
                "is_trashed": 1,
                "active_warning": was_active,
                "financial_reversal": 0.0,
                "preserved_credit": float(v["credited_amount"] or v["reward"] or 0.0)
            }

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def move_all_permanent_approved_to_trash(platform_filter: str = "all", sub_ids: list = None, actor_id: str = "ADMIN", conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            if sub_ids:
                placeholders = ",".join("?" for _ in sub_ids)
                rows = conn.execute(
                    f"SELECT * FROM videos WHERE sub_id IN ({placeholders}) AND COALESCE(is_trashed, 0) = 0",
                    tuple(str(s) for s in sub_ids)
                ).fetchall()
            elif platform_filter and str(platform_filter).lower() in ("youtube", "tiktok", "instagram", "facebook"):
                rows = conn.execute(
                    "SELECT * FROM videos WHERE COALESCE(permanent_approved, 0) = 1 AND COALESCE(is_trashed, 0) = 0 AND LOWER(platform) = ?",
                    (str(platform_filter).lower(),)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM videos WHERE COALESCE(permanent_approved, 0) = 1 AND COALESCE(is_trashed, 0) = 0"
                ).fetchall()

            moved_ids = []
            for r in rows:
                move_video_to_trash(r["sub_id"], actor_id=actor_id, conn=conn)
                moved_ids.append(r["sub_id"])
            return {"moved_count": len(moved_ids), "sub_ids": moved_ids}

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def restore_video_from_trash(sub_id: str, actor_id: str = "ADMIN", conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")
            if int(v["is_trashed"] or 0) != 1:
                return {
                    "sub_id": str(sub_id),
                    "user_id": str(v["user_id"]),
                    "already_restored": True,
                    "is_trashed": 0,
                    "status": v["status"],
                    "bot_status": v["bot_status"],
                    "admin_status": v["admin_status"],
                    "credited_amount": float(v["credited_amount"] or v["reward"] or 0.0),
                    "paid_views": int(v["paid_views"] or 0)
                }
            prev_st = v["trash_previous_status"] or v["status"] or "pending"
            prev_bot = v["trash_previous_bot_status"] or v["bot_status"] or "pending"
            prev_adm = v["trash_previous_admin_status"] or v["admin_status"] or "pending"
            cur = conn.execute("""
                UPDATE videos
                SET is_trashed = 0,
                    trashed_at = '',
                    trashed_by = '',
                    status = ?,
                    bot_status = ?,
                    admin_status = ?,
                    trash_previous_status = '',
                    trash_previous_bot_status = '',
                    trash_previous_admin_status = ''
                WHERE sub_id = ? AND COALESCE(is_trashed, 0) = 1
            """, (prev_st, prev_bot, prev_adm, str(sub_id)))
            if cur.rowcount != 1:
                return {
                    "sub_id": str(sub_id),
                    "user_id": str(v["user_id"]),
                    "already_restored": True,
                    "is_trashed": 0,
                    "status": v["status"],
                    "bot_status": v["bot_status"],
                    "admin_status": v["admin_status"],
                    "credited_amount": float(v["credited_amount"] or v["reward"] or 0.0),
                    "paid_views": int(v["paid_views"] or 0)
                }
            log_audit_event(
                actor_id, "Video Restored from Trash",
                f"Video {sub_id} restored with status={prev_st}, credit={float(v['credited_amount'] or v['reward'] or 0):.2f} BDT",
                target_user_id=str(v["user_id"]),
                conn=conn
            )
            return {
                "sub_id": str(sub_id),
                "user_id": str(v["user_id"]),
                "is_trashed": 0,
                "status": prev_st,
                "bot_status": prev_bot,
                "admin_status": prev_adm,
                "credited_amount": float(v["credited_amount"] or v["reward"] or 0.0),
                "paid_views": int(v["paid_views"] or 0)
            }

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def permanently_delete_trashed_video(sub_id: str, actor_id: str = "ADMIN", conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                return {"sub_id": str(sub_id), "deleted": False, "reason": "Video not found"}
            uid = str(v["user_id"])
            register_video_submission_lock(
                v["platform"], v["canonical_video_id"], v["sub_id"], uid, v["url"], "permanently_deleted_from_trash", conn=conn
            )
            conn.execute("DELETE FROM video_view_snapshots WHERE sub_id = ?", (str(sub_id),))
            conn.execute("DELETE FROM video_external_links WHERE sub_id = ?", (str(sub_id),))
            conn.execute("DELETE FROM video_external_link_history WHERE sub_id = ?", (str(sub_id),))
            conn.execute("DELETE FROM videos WHERE sub_id = ?", (str(sub_id),))
            log_audit_event(
                actor_id, "Video Permanently Deleted from Trash (Lock Preserved)",
                f"Permanently deleted video {sub_id} ({v['platform']}:{v['canonical_video_id']}) from admin view; duplicate lock & ledger preserved",
                target_user_id=uid,
                conn=conn
            )
            return {"sub_id": str(sub_id), "user_id": uid, "deleted": True}

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def empty_all_trashed_videos(actor_id: str = "ADMIN", conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            rows = conn.execute("SELECT * FROM videos WHERE COALESCE(is_trashed, 0) = 1").fetchall()
            sub_ids = [r["sub_id"] for r in rows]
            for r in rows:
                register_video_submission_lock(
                    r["platform"], r["canonical_video_id"], r["sub_id"], r["user_id"], r["url"], "permanently_deleted_from_trash", conn=conn
                )
            if sub_ids:
                conn.execute("DELETE FROM video_view_snapshots WHERE sub_id IN (SELECT sub_id FROM videos WHERE COALESCE(is_trashed, 0) = 1)")
                conn.execute("DELETE FROM video_external_links WHERE sub_id IN (SELECT sub_id FROM videos WHERE COALESCE(is_trashed, 0) = 1)")
                conn.execute("DELETE FROM video_external_link_history WHERE sub_id IN (SELECT sub_id FROM videos WHERE COALESCE(is_trashed, 0) = 1)")
                conn.execute("DELETE FROM videos WHERE COALESCE(is_trashed, 0) = 1")
            log_audit_event(
                actor_id,
                "Bulk Empty Trash (Locks Preserved)",
                f"Permanently deleted {len(sub_ids)} trashed videos from admin UI; locks & ledger preserved",
                conn=conn
            )
            return {"deleted_count": len(sub_ids), "sub_ids": sub_ids}

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def get_video_approval_counts(conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        result = {
            "pending": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
            "bot_approve": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
            "admin_approve": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
            "permanent_approve": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
            "rejected": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
            "trash": {"total": 0, "youtube": 0, "tiktok": 0, "instagram": 0, "facebook": 0},
        }
        rows = conn.execute("""
            SELECT platform, bot_status, admin_status, status,
                   COALESCE(permanent_approved, 0) as perm_app,
                   COALESCE(is_trashed, 0) as trashed,
                   COUNT(*) as cnt
            FROM videos
            GROUP BY platform, bot_status, admin_status, status, perm_app, trashed
        """).fetchall()
        for r in rows:
            plat = str(r["platform"] or "").lower()
            b_st = str(r["bot_status"] or "").lower()
            a_st = str(r["admin_status"] or "").lower()
            st = str(r["status"] or "").lower()
            perm = int(r["perm_app"] or 0)
            trashed = int(r["trashed"] or 0)
            c = int(r["cnt"] or 0)

            if trashed == 1:
                result["trash"]["total"] += c
                if plat in result["trash"]:
                    result["trash"][plat] += c
                continue

            if a_st == "rejected" or b_st == "rejected" or st == "rejected":
                result["rejected"]["total"] += c
                if plat in result["rejected"]:
                    result["rejected"][plat] += c
                continue

            if perm == 1 or st == "permanent_approved":
                result["permanent_approve"]["total"] += c
                if plat in result["permanent_approve"]:
                    result["permanent_approve"][plat] += c
                continue

            if a_st == "approved":
                result["admin_approve"]["total"] += c
                if plat in result["admin_approve"]:
                    result["admin_approve"][plat] += c
                continue

            if b_st == "approved":
                result["bot_approve"]["total"] += c
                if plat in result["bot_approve"]:
                    result["bot_approve"][plat] += c
                continue

            result["pending"]["total"] += c
            if plat in result["pending"]:
                result["pending"][plat] += c

        return result
    finally:
        if own_conn:
            conn.close()


def is_video_permanently_locked(arg1: str, arg2: str = None, arg3: str = None, conn: sqlite3.Connection = None) -> bool:
    if isinstance(arg2, sqlite3.Connection) and conn is None:
        conn = arg2
        arg2 = None
    if arg2 is not None:
        return bool(is_video_submitted_globally(arg1, arg2, video_url=str(arg3 or ""), conn=conn))
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        row = conn.execute("SELECT permanent_approved FROM videos WHERE sub_id = ? LIMIT 1", (str(arg1),)).fetchone()
        return bool(row and int(row["permanent_approved"] or 0) == 1)
    finally:
        if own_conn:
            conn.close()


def delete_user_account_completely(
    user_id: str,
    actor_id: str = "",
    conn: sqlite3.Connection = None,
    hard_delete: bool = False
) -> dict:
    uid = str(user_id or "").strip()
    if not uid:
        return {"ok": False, "deleted": False, "user_id": ""}

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            u = conn.execute("SELECT * FROM users WHERE user_id = ? LIMIT 1", (uid,)).fetchone()
            if u and not hard_delete:
                debt_v = round(float(u["debt_balance"] or 0.0), 2)
                bal_v = round(float(u["balance"] or 0.0), 2)
                if debt_v > 0 or bal_v < 0:
                    eff_debt = max(debt_v, abs(min(0.0, bal_v)))
                    return {
                        "ok": False,
                        "deleted": False,
                        "debt_blocked": True,
                        "debt_balance": eff_debt,
                        "reason": f"বকেয়া ঋণ ({eff_debt:.2f}৳) থাকায় অ্যাকাউন্ট ডিলিট করা যাবে না! আগে ঋণ পরিশোধ করুন, তারপর অ্যাকাউন্ট ডিলিট করুন।",
                        "user_id": uid
                    }

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if u:
                cur_bal = round(float(u["balance"] or 0.0), 2)
                cur_held = round(float(u["held_balance"] or 0.0), 2)
                pend_wds = conn.execute(
                    "SELECT wd_id, amount FROM withdrawals WHERE user_id = ? AND status = 'pending'",
                    (uid,)
                ).fetchall()
                for pw in pend_wds:
                    w_id = str(pw["wd_id"])
                    w_amt = round(float(pw["amount"] or 0.0), 2)
                    conn.execute(
                        "UPDATE withdrawals SET status = 'cancelled', processed_at = ?, decision_reason = 'Cancelled due to user account deletion' WHERE wd_id = ?",
                        (now_str, w_id)
                    )
                    if w_amt > 0:
                        prev_b = cur_bal
                        cur_bal = round(cur_bal + w_amt, 2)
                        cur_held = max(0.0, round(cur_held - w_amt, 2))
                        tx_id = f"TX_DEL_WD_{int(time.time()*1000)}_{w_id[-6:]}"
                        conn.execute("""
                            INSERT OR IGNORE INTO ledger_transactions (
                                tx_id, idempotency_key, user_id, video_id, sub_id,
                                type, transaction_type, amount,
                                before_balance, previous_balance, after_balance, new_balance,
                                reference_id, details, admin_id, created_at, timestamp
                            ) VALUES (?, ?, ?, '', '', 'Withdraw Cancelled', 'Withdraw Cancelled', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            tx_id, f"DEL_WD_CANCEL:{w_id}", uid, w_amt, prev_b, prev_b, cur_bal, cur_bal,
                            w_id, f"Auto-cancelled pending withdrawal {w_id} upon account deletion", str(actor_id or uid), now_str, now_str
                        ))
                if cur_bal > 0:
                    tx_id_f = f"TX_DEL_FORFEIT_{int(time.time()*1000)}_{uid[-4:]}"
                    conn.execute("""
                        INSERT OR IGNORE INTO ledger_transactions (
                            tx_id, idempotency_key, user_id, video_id, sub_id,
                            type, transaction_type, amount,
                            before_balance, previous_balance, after_balance, new_balance,
                            reference_id, details, admin_id, created_at, timestamp
                        ) VALUES (?, ?, ?, '', '', 'Account Deletion Forfeiture', 'Account Deletion Forfeiture', ?, ?, ?, 0.0, 0.0, ?, ?, ?, ?, ?)
                    """, (
                        tx_id_f, f"DEL_FORFEIT:{uid}:{int(time.time()*1000)}_{secrets.token_hex(2)}", uid, -cur_bal, cur_bal, cur_bal,
                        uid, f"Balance forfeited upon account deletion ({cur_bal:.2f} BDT)", str(actor_id or uid), now_str, now_str
                    ))

            user_vids = conn.execute("SELECT sub_id, platform, canonical_video_id, url, status FROM videos WHERE user_id = ?", (uid,)).fetchall()
            for uv in user_vids:
                register_video_submission_lock(
                    uv["platform"], uv["canonical_video_id"], uv["sub_id"], uid, uv["url"], "user_account_deleted", conn=conn
                )

            conn.execute(
                "DELETE FROM video_view_snapshots WHERE sub_id IN (SELECT sub_id FROM videos WHERE user_id = ?)",
                (uid,)
            )
            conn.execute("DELETE FROM video_external_links WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM video_external_link_history WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM videos WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM user_platforms WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM profile_identity_locks WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM user_identity_locks WHERE user_id = ?", (uid,))

            log_audit_event(
                actor_id or uid,
                "Admin Permanent Remove User" if hard_delete else "User Account Self-Deleted (Tombstone)",
                f"User {uid} account deleted (hard_delete={hard_delete}); video locks & ledger preserved",
                target_user_id=uid,
                conn=conn
            )

            if hard_delete:
                conn.execute("DELETE FROM debt_adjustments WHERE user_id = ?", (uid,))
                conn.execute("DELETE FROM withdrawals WHERE user_id = ?", (uid,))
                conn.execute("DELETE FROM users WHERE user_id = ?", (uid,))
            else:
                conn.execute("""
                    UPDATE users
                    SET phone = '',
                        bkash_number = '',
                        nagad_number = '',
                        rocket_number = '',
                        password_hash = '',
                        password_plain = '',
                        channel_name = '',
                        youtube_channel_name = '',
                        tiktok_channel_name = '',
                        channel_url = '',
                        channel_subs = 0,
                        app_uid = '',
                        balance = 0.0,
                        held_balance = 0.0,
                        debt_balance = 0.0,
                        total_earned = 0.0,
                        videos_submitted = 0,
                        videos_approved = 0,
                        videos_rejected = 0,
                        registered = 0,
                        session_logged_out = 1,
                        session_version = COALESCE(session_version, 1) + 1,
                        status = 'deleted',
                        bio_frozen = 0,
                        admin_suspended = 0,
                        duplicate_strikes = 0,
                        wrong_submit_strikes = 0,
                        cooldown_until_ts = 0
                    WHERE user_id = ?
                """, (uid,))

            return {"ok": True, "deleted": True, "hard_deleted": hard_delete, "tombstone": not hard_delete, "user_id": uid}

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


# ==============================================================================
# ADVANCED CUSTOM BUTTON PLACEMENT, NESTING, CYCLE DETECTION & RESTORATION ENGINE
# ==============================================================================
def generate_unique_custom_button_id(prefix: str = "cbtn", conn: sqlite3.Connection = None) -> str:
    """
    Generates a cryptographically secure, collision-free Custom Button ID (`cbtn_<12_hex>`).
    Checks `custom_buttons`, `button_labels`, `button_styles`, `button_original_placements`,
    and `used_random_codes` so an existing button ID can NEVER be overwritten.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        existing = set()
        for tbl in ("custom_buttons", "button_labels", "button_styles", "button_original_placements"):
            try:
                for r in conn.execute(f"SELECT btn_key FROM {tbl}").fetchall():
                    if r["btn_key"]:
                        existing.add(str(r["btn_key"]).strip())
            except Exception:
                pass
        try:
            _ensure_local_module("ui_catalog", ("ui_catalog.py", "Ui Catalog.py", "Ui_Catalog.py"))
            from ui_catalog import DEFAULT_BUTTON_LABELS
            existing.update(DEFAULT_BUTTON_LABELS.keys())
        except Exception:
            pass
        for _ in range(100):
            cand = generate_custom_button_uid(prefix=prefix, existing_keys=existing)
            if cand not in existing:
                return cand
        return f"{prefix}_{uuid.uuid4().hex[:14]}"
    finally:
        if own_conn:
            conn.close()


def get_button_original_placement(btn_key: str, conn: sqlite3.Connection = None) -> dict:
    """Returns the recorded original `(original_layout_key, original_row_index, original_col_index)` for `btn_key`."""
    bk = str(btn_key or "").strip()
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        row = conn.execute("SELECT * FROM button_original_placements WHERE btn_key = ? LIMIT 1", (bk,)).fetchone()
        if row:
            return dict(row)
        cb = conn.execute("SELECT * FROM custom_buttons WHERE btn_key = ? LIMIT 1", (bk,)).fetchone()
        if cb:
            return {
                "btn_key": bk,
                "original_layout_key": cb["original_layout_key"] or cb["destination_layout"] or cb["parent_layout"] or ("admin_home" if cb["side"] == "admin" else "user_home"),
                "original_row_index": max(0, int(cb["original_row_index"] or 0)),
                "original_col_index": max(0, int(cb["original_col_index"] or 0)),
                "current_layout_key": cb["destination_layout"] or cb["parent_layout"] or "",
                "current_row_index": max(0, int(cb["row_index"] or 0)),
                "current_col_index": max(0, int(cb["col_index"] or 0))
            }
        def_l = "admin_home" if bk.startswith("a_") else "user_home"
        return {
            "btn_key": bk,
            "original_layout_key": def_l,
            "original_row_index": 999,
            "original_col_index": 0,
            "current_layout_key": def_l,
            "current_row_index": 999,
            "current_col_index": 0
        }
    finally:
        if own_conn:
            conn.close()


def record_button_placement(
    btn_key: str,
    layout_key: str,
    row_index: int,
    col_index: int,
    set_as_original: bool = False,
    preserve_original: bool = True,
    conn: sqlite3.Connection = None
) -> None:
    """
    Records a button's current `(layout_key, row_index, col_index)`.
    If no record exists yet in `button_original_placements` (or `set_as_original=True`),
    also sets `original_layout_key`, `original_row_index`, and `original_col_index`.
    """
    bk = str(btn_key or "").strip()
    lk = str(layout_key or "").strip()
    if not bk or not lk:
        return
    r_idx = max(0, int(row_index if row_index is not None else 0))
    c_idx = max(0, int(col_index if col_index is not None else 0))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            existing = conn.execute("SELECT * FROM button_original_placements WHERE btn_key = ? LIMIT 1", (bk,)).fetchone()
            if not existing or set_as_original:
                conn.execute("""
                    INSERT OR REPLACE INTO button_original_placements (
                        btn_key, original_layout_key, original_row_index, original_col_index,
                        current_layout_key, current_row_index, current_col_index, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bk, lk, r_idx, c_idx, lk, r_idx, c_idx, now_str))
            else:
                conn.execute("""
                    UPDATE button_original_placements
                    SET current_layout_key = ?, current_row_index = ?, current_col_index = ?, updated_at = ?
                    WHERE btn_key = ?
                """, (lk, r_idx, c_idx, now_str, bk))

        if own_conn:
            with begin_immediate_transaction(conn):
                _exec()
        else:
            _exec()
    finally:
        if own_conn:
            conn.close()


def sync_layout_placements_in_db(layout_key: str, structure: list, conn: sqlite3.Connection = None) -> None:
    """Updates `current_layout_key`, `current_row_index`, `current_col_index` for all buttons in `structure`."""
    lk = str(layout_key or "").strip()
    if not lk or not isinstance(structure, list):
        return
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            for r_idx, row in enumerate(structure):
                if not isinstance(row, list):
                    continue
                for c_idx, bk in enumerate(row):
                    record_button_placement(str(bk), lk, r_idx, c_idx, set_as_original=False, conn=conn)
        if own_conn:
            with begin_immediate_transaction(conn):
                _exec()
        else:
            _exec()
    finally:
        if own_conn:
            conn.close()


def _load_all_layouts_from_db(conn: sqlite3.Connection) -> dict:
    try:
        _ensure_local_module("ui_catalog", ("ui_catalog.py", "Ui Catalog.py", "Ui_Catalog.py"))
        from ui_catalog import DEFAULT_LAYOUTS
        all_layouts = {k: [list(r) for r in v if isinstance(r, list)] for k, v in DEFAULT_LAYOUTS.items()}
    except Exception:
        all_layouts = {}
    for r in conn.execute("SELECT layout_key, structure_json FROM dynamic_layouts").fetchall():
        try:
            parsed = json.loads(r["structure_json"] or "[]")
            if isinstance(parsed, list):
                all_layouts[str(r["layout_key"])] = [list(row) for row in parsed if isinstance(row, list)]
        except Exception:
            continue
    for cb in conn.execute("SELECT layout_key FROM custom_buttons").fetchall():
        all_layouts.setdefault(str(cb["layout_key"]), [])
    return all_layouts


def locate_button_across_all_layouts(btn_key: str, conn: sqlite3.Connection = None) -> list:
    """
    Scans all layouts in the database and default catalog to find every `(layout_key, row_index, col_index)`
    where `btn_key` is currently located.
    """
    bk = str(btn_key or "").strip()
    if not bk:
        return []
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        all_layouts = _load_all_layouts_from_db(conn)
        locations = []
        for l_key, rows in all_layouts.items():
            for r_idx, row in enumerate(rows):
                for c_idx, k in enumerate(row):
                    if k == bk:
                        locations.append({
                            "layout_key": l_key,
                            "row_index": r_idx,
                            "col_index": c_idx
                        })
        return locations
    finally:
        if own_conn:
            conn.close()


def would_create_container_cycle(
    moving_btn_key: str,
    target_layout_or_container_key: str,
    conn: sqlite3.Connection = None,
    return_reason: bool = False
):
    """
    Detects whether placing `moving_btn_key` into `target_layout_or_container_key` would create a Circular Reference
    or Infinite Navigation loop in nested folders.
    Returns `bool` by default, or `(is_cycle: bool, reason: str)` when `return_reason=True`.
    """
    def _ret(flag: bool, msg: str):
        return (flag, msg) if return_reason else flag

    m_bk = str(moving_btn_key or "").strip()
    t_raw = str(target_layout_or_container_key or "").strip()
    if not m_bk or not t_raw:
        return _ret(False, "OK")

    target_layout = t_raw if t_raw.startswith("custom_page_") else (f"custom_page_{t_raw}" if t_raw.startswith("cbtn_") else t_raw)
    moving_layout = f"custom_page_{m_bk}"

    if m_bk == t_raw or target_layout == moving_layout:
        return _ret(True, "Circular Reference প্রতিরোধ করা হয়েছে: কোনো ফোল্ডার বাটনের ভেতরে নিজেকে ঢোকানো যাবে না!")

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        cb_row = conn.execute("SELECT layout_key FROM custom_buttons WHERE btn_key = ? LIMIT 1", (m_bk,)).fetchone()
        if not cb_row and not m_bk.startswith("cbtn_"):
            return _ret(False, "OK")
        if cb_row and cb_row["layout_key"]:
            moving_layout = str(cb_row["layout_key"])

        if target_layout == moving_layout:
            return _ret(True, "Circular Reference প্রতিরোধ করা হয়েছে: একই কাস্টম ফোল্ডারের ভেতরে নিজেকে যুক্ত করা যাবে না!")

        all_layouts = _load_all_layouts_from_db(conn)
        cb_map = {}
        parent_map = {}
        for r in conn.execute("SELECT btn_key, layout_key, parent_layout, parent_container_key FROM custom_buttons").fetchall():
            bk_r = str(r["btn_key"])
            lk_r = str(r["layout_key"] or f"custom_page_{bk_r}")
            cb_map[bk_r] = lk_r
            p_cont = str(r["parent_container_key"] or "").strip()
            p_lay = str(r["parent_layout"] or "").strip()
            if p_cont:
                parent_map[lk_r] = f"custom_page_{p_cont}"
            elif p_lay.startswith("custom_page_"):
                parent_map[lk_r] = p_lay

        visited_layouts = set()
        queue = [moving_layout]
        while queue:
            cur_lk = queue.pop(0)
            if cur_lk in visited_layouts:
                continue
            visited_layouts.add(cur_lk)
            if cur_lk == target_layout:
                return _ret(True, "Circular Reference / Infinite Navigation শনাক্ত হয়েছে! সাব-ফোল্ডারের ভেতরে তার প্যারেন্ট ফোল্ডার যুক্ত করা যাবে না।")
            rows = all_layouts.get(cur_lk, [])
            for row in rows:
                for child_bk in row:
                    if child_bk == t_raw:
                        return _ret(True, "Circular Reference / Infinite Navigation শনাক্ত হয়েছে! সাব-ফোল্ডারের ভেতরে তার প্যারেন্ট ফোল্ডার যুক্ত করা যাবে না।")
                    child_lk = cb_map.get(child_bk) or (f"custom_page_{child_bk}" if str(child_bk).startswith("cbtn_") else "")
                    if child_lk and child_lk not in visited_layouts:
                        queue.append(child_lk)

        cur_anc = target_layout
        seen_anc = set()
        while cur_anc and cur_anc not in seen_anc:
            seen_anc.add(cur_anc)
            if cur_anc == moving_layout:
                return _ret(True, "Circular Reference / Infinite Navigation শনাক্ত হয়েছে!")
            cur_anc = parent_map.get(cur_anc, "")

        return _ret(False, "OK")
    finally:
        if own_conn:
            conn.close()


def _insert_button_at_exact_position(rows: list, btn_key: str, row_index: int, col_index: int, join_row: bool = True) -> list:
    """
    Inserts `btn_key` into `rows` at `(row_index, col_index)` without duplicates.
    """
    cleaned = [[k for k in r if k != btn_key] for r in (rows or []) if isinstance(r, list)]
    cleaned = [r for r in cleaned if r]

    if not cleaned:
        return [[btn_key]]

    r_idx = int(row_index if row_index is not None else len(cleaned))
    c_idx = int(col_index if col_index is not None else 0)

    if r_idx < 0:
        r_idx = 0

    if join_row and 0 <= r_idx < len(cleaned):
        target_row = cleaned[r_idx]
        safe_c = max(0, min(c_idx, len(target_row)))
        target_row.insert(safe_c, btn_key)
    elif r_idx <= len(cleaned):
        cleaned.insert(r_idx, [btn_key])
    else:
        cleaned.append([btn_key])
    return [r for r in cleaned if r]


def restore_button_to_original_placement(
    btn_key: str,
    from_container_layout: str = "",
    conn: sqlite3.Connection = None,
    avoid_layouts: set = None
) -> dict:
    """
    Removes `btn_key` from `from_container_layout` (if specified) and restores it to its exact
    recorded `(original_layout_key, original_row_index, original_col_index)`.
    If its `original_layout_key` was a deleted custom container, falls back to the nearest valid parent layout.
    """
    bk = str(btn_key or "").strip()
    if not bk or bk.endswith("_direct"):
        return {"ok": False, "btn_key": bk}

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            all_layouts = _load_all_layouts_from_db(conn)
            active_cbtn_layouts = {str(r["layout_key"]) for r in conn.execute("SELECT layout_key FROM custom_buttons").fetchall()}
            blocked = set(avoid_layouts or ())

            if from_container_layout and from_container_layout in all_layouts:
                c_rows = [[k for k in r if k != bk] for r in all_layouts[from_container_layout]]
                c_rows = [r for r in c_rows if r]
                all_layouts[from_container_layout] = c_rows
                conn.execute(
                    "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                    (from_container_layout, json.dumps(c_rows, ensure_ascii=False))
                )

            orig_info = get_button_original_placement(bk, conn=conn)
            orig_lk = str(orig_info.get("original_layout_key") or ("admin_home" if bk.startswith("a_") else "user_home"))
            orig_r = int(orig_info.get("original_row_index", 0))
            orig_c = int(orig_info.get("original_col_index", 0))

            if orig_lk in blocked or (orig_lk.startswith("custom_page_") and orig_lk not in active_cbtn_layouts):
                orig_lk = "admin_home" if bk.startswith("a_") else "user_home"

            for lk_scan, r_list in list(all_layouts.items()):
                if lk_scan != orig_lk and any(bk in r for r in r_list):
                    cleaned_scan = [[k for k in r if k != bk] for r in r_list]
                    cleaned_scan = [r for r in cleaned_scan if r]
                    all_layouts[lk_scan] = cleaned_scan
                    conn.execute(
                        "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                        (lk_scan, json.dumps(cleaned_scan, ensure_ascii=False))
                    )

            target_rows = all_layouts.get(orig_lk, [])
            try:
                _ensure_local_module("ui_catalog", ("ui_catalog.py", "Ui Catalog.py", "Ui_Catalog.py"))
                from ui_catalog import DEFAULT_LAYOUTS
                def_rows = DEFAULT_LAYOUTS.get(orig_lk, [])
            except Exception:
                def_rows = []

            join_existing = False
            if 0 <= orig_r < len(def_rows) and len(def_rows[orig_r]) > 1 and 0 <= orig_r < len(target_rows):
                join_existing = True
            elif orig_c > 0 and 0 <= orig_r < len(target_rows):
                join_existing = True

            updated_target = _insert_button_at_exact_position(target_rows, bk, orig_r, orig_c, join_row=join_existing)
            all_layouts[orig_lk] = updated_target
            conn.execute(
                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                (orig_lk, json.dumps(updated_target, ensure_ascii=False))
            )
            sync_layout_placements_in_db(orig_lk, updated_target, conn=conn)
            return {
                "ok": True,
                "btn_key": bk,
                "restored_layout_key": orig_lk,
                "restored_to_layout": orig_lk,
                "restored_row_index": orig_r,
                "restored_col_index": orig_c,
                "updated_layout": updated_target
            }

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def cleanup_orphan_custom_layouts_and_messages(conn: sqlite3.Connection = None) -> dict:
    """
    Removes any orphan `custom_page_*` layouts in `dynamic_layouts` and orphan `custom_msg_*`
    templates in `dynamic_messages` that do not belong to any active record in `custom_buttons`.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            active_cbs = conn.execute("SELECT btn_key, layout_key, msg_key FROM custom_buttons").fetchall()
            valid_keys = {str(r["btn_key"]) for r in active_cbs}
            valid_layouts = {str(r["layout_key"]) for r in active_cbs}
            valid_msgs = {str(r["msg_key"]) for r in active_cbs}

            removed_layouts = []
            for r in conn.execute("SELECT layout_key FROM dynamic_layouts WHERE layout_key LIKE 'custom_page_%'").fetchall():
                lk = str(r["layout_key"])
                if lk not in valid_layouts:
                    conn.execute("DELETE FROM dynamic_layouts WHERE layout_key = ?", (lk,))
                    removed_layouts.append(lk)

            removed_msgs = []
            for r in conn.execute("SELECT msg_key FROM dynamic_messages WHERE msg_key LIKE 'custom_msg_%'").fetchall():
                mk = str(r["msg_key"])
                if mk not in valid_msgs:
                    conn.execute("DELETE FROM dynamic_messages WHERE msg_key = ?", (mk,))
                    removed_msgs.append(mk)

            for tbl in ("button_labels", "button_styles", "button_original_placements"):
                for r in conn.execute(f"SELECT btn_key FROM {tbl} WHERE btn_key LIKE 'cbtn_%'").fetchall():
                    bk = str(r["btn_key"])
                    base_bk = bk[:-7] if bk.endswith("_direct") else bk
                    if base_bk not in valid_keys:
                        conn.execute(f"DELETE FROM {tbl} WHERE btn_key = ?", (bk,))

            return {"removed_layouts": removed_layouts, "removed_messages": removed_msgs}

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def create_custom_button_transactional(
    side: str,
    parent_layout: str,
    destination_layout: str = "",
    label: str = "নতুন বাটন",
    msg_content: str = "",
    row_index: int = -1,
    col_index: int = 0,
    drop_mode: str = "bot",
    parent_container_key: str = "",
    sub_buttons: list = None,
    sub_button_keys: list = None,
    raw_msg_text: str = "",
    msg_entities: list = None,
    style: str = "primary",
    design_style: str = "normal",
    custom_emoji_id: str = "",
    btn_key: str = None,
    updated_by: str = "admin",
    conn: sqlite3.Connection = None
) -> dict:
    """
    Atomically creates a new Custom Button / Nested Folder ONLY upon Final Confirmation inside a SQLite
    `BEGIN IMMEDIATE` transaction.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            s_side = "admin" if str(side).lower().strip() == "admin" else "user"
            p_lay = str(parent_layout or ("admin_home" if s_side == "admin" else "user_home")).strip()
            p_cont = str(parent_container_key or "").strip()

            if btn_key:
                cand_key = str(btn_key).strip()
                exists = (
                    conn.execute("SELECT 1 FROM custom_buttons WHERE btn_key = ? LIMIT 1", (cand_key,)).fetchone()
                    or conn.execute("SELECT 1 FROM button_labels WHERE btn_key = ? LIMIT 1", (cand_key,)).fetchone()
                )
                if exists:
                    raise ValueError(f"Button ID '{cand_key}' ইতিমধ্যে বিদ্যমান! পুরোনো বাটন Overwrite করা যাবে না।")
            else:
                cand_key = generate_unique_custom_button_id(prefix="cbtn", conn=conn)

            c_msg_key = f"custom_msg_{cand_key}"
            c_layout_key = str(destination_layout).strip() if (destination_layout and str(destination_layout).startswith("custom_page_")) else f"custom_page_{cand_key}"
            dest_lay = str(destination_layout or c_layout_key).strip()

            if p_cont:
                cont_rec = conn.execute("SELECT side, layout_key FROM custom_buttons WHERE btn_key = ? LIMIT 1", (p_cont,)).fetchone()
                if cont_rec and str(cont_rec["side"] or "").lower().strip() in ("user", "admin") and str(cont_rec["side"]).lower().strip() != s_side:
                    raise ValueError("ইউজার সাইডের বাটন অ্যাডমিন কন্টেইনারে বা অ্যাডমিন বাটন ইউজার কন্টেইনারে যুক্ত করা নিষিদ্ধ (Cross-side boundary violation)!")
                placement_lay = str(cont_rec["layout_key"]) if cont_rec else f"custom_page_{p_cont}"
            else:
                placement_lay = p_lay

            if s_side == "user" and (placement_lay.startswith("admin_") or dest_lay.startswith("admin_")):
                raise ValueError("ইউজার সাইডের বাটন অ্যাডমিন পেজে যুক্ত করা নিষিদ্ধ (Cross-side boundary violation)!")
            if s_side == "admin" and (placement_lay.startswith("user_") or dest_lay.startswith("user_")):
                raise ValueError("অ্যাডমিন সাইডের বাটন ইউজার পেজে যুক্ত করা নিষিদ্ধ (Cross-side boundary violation)!")

            lbl = str(label or "নতুন বাটন").strip()
            st_col = style if style in ("success", "danger", "primary") else ("primary" if s_side == "admin" else "success")
            des = str(design_style or "normal").strip()
            em_id = re.sub(r"[^0-9]", "", str(custom_emoji_id or "").strip())
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cyc_flag, cyc_reason = would_create_container_cycle(cand_key, placement_lay, conn=conn, return_reason=True)
            if cyc_flag:
                raise ValueError(cyc_reason)

            eff_subs = sub_button_keys if sub_button_keys is not None else (sub_buttons or [])
            sub_list = [str(x).strip() for x in eff_subs if str(x).strip() and str(x).strip() != cand_key]
            for sb in sub_list:
                if s_side == "user" and sb.startswith("a_"):
                    raise ValueError(f"ইউজার কন্টেইনার বাটনের ভেতরে অ্যাডমিন বাটন ({sb}) যুক্ত করা নিষিদ্ধ!")
                if s_side == "admin" and sb.startswith("u_"):
                    raise ValueError(f"অ্যাডমিন কন্টেইনার বাটনের ভেতরে ইউজার বাটন ({sb}) যুক্ত করা নিষিদ্ধ!")
                sb_rec = conn.execute("SELECT side FROM custom_buttons WHERE btn_key = ? LIMIT 1", (sb,)).fetchone()
                if sb_rec and str(sb_rec["side"] or "").lower().strip() in ("user", "admin") and str(sb_rec["side"]).lower().strip() != s_side:
                    raise ValueError(f"ভিন্ন সাইডের কাস্টম বাটন ({sb}) একত্রিত করা নিষিদ্ধ!")
                s_cyc, s_reason = would_create_container_cycle(sb, c_layout_key, conn=conn, return_reason=True)
                if s_cyc:
                    raise ValueError(s_reason)

            all_layouts = _load_all_layouts_from_db(conn)
            dest_rows = [list(r) for r in all_layouts.get(placement_lay, []) if isinstance(r, list)]

            if drop_mode == "top":
                eff_r = 0
                eff_c = 0
                dest_rows.insert(0, [cand_key])
            elif drop_mode == "row" and 0 <= int(row_index) < len(dest_rows):
                eff_r = int(row_index)
                target_r = dest_rows[eff_r]
                eff_c = max(0, min(int(col_index if col_index >= 0 else len(target_r)), len(target_r)))
                target_r.insert(eff_c, cand_key)
            elif drop_mode == "before" and 0 <= int(row_index) <= len(dest_rows):
                eff_r = int(row_index)
                eff_c = 0
                dest_rows.insert(eff_r, [cand_key])
            elif int(row_index) >= 0 and int(row_index) <= len(dest_rows):
                eff_r = int(row_index)
                eff_c = max(0, int(col_index or 0))
                if eff_c > 0 and eff_r < len(dest_rows):
                    target_r = dest_rows[eff_r]
                    eff_c = min(eff_c, len(target_r))
                    target_r.insert(eff_c, cand_key)
                else:
                    dest_rows.insert(eff_r, [cand_key])
                    eff_c = 0
            else:
                eff_r = len(dest_rows)
                eff_c = 0
                dest_rows.append([cand_key])

            conn.execute("""
                INSERT INTO custom_buttons (
                    btn_key, side, parent_layout, destination_layout,
                    row_index, col_index, parent_container_key,
                    original_layout_key, original_row_index, original_col_index,
                    label, style, design_style, custom_emoji_id,
                    msg_key, layout_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cand_key, s_side, placement_lay, dest_lay,
                eff_r, eff_c, p_cont,
                placement_lay, eff_r, eff_c,
                lbl, st_col, des, em_id,
                c_msg_key, c_layout_key, now_str
            ))

            conn.execute(
                "INSERT OR REPLACE INTO button_labels (btn_key, label, icon_custom_emoji_id, design_style) VALUES (?, ?, ?, ?)",
                (cand_key, lbl, em_id, des)
            )
            conn.execute(
                "INSERT OR REPLACE INTO button_styles (btn_key, style, icon_custom_emoji_id, design_style) VALUES (?, ?, ?, ?)",
                (cand_key, st_col, em_id, des)
            )
            record_button_placement(cand_key, placement_lay, eff_r, eff_c, set_as_original=True, conn=conn)

            conn.execute(
                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                (placement_lay, json.dumps(dest_rows, ensure_ascii=False))
            )
            sync_layout_placements_in_db(placement_lay, dest_rows, conn=conn)
            all_layouts[placement_lay] = dest_rows

            child_layout = []
            for sb in sub_list:
                locs = locate_button_across_all_layouts(sb, conn=conn)
                if locs:
                    first_loc = locs[0]
                    existing_orig = conn.execute("SELECT 1 FROM button_original_placements WHERE btn_key = ? LIMIT 1", (sb,)).fetchone()
                    if not existing_orig:
                        record_button_placement(
                            sb, first_loc["layout_key"], first_loc["row_index"], first_loc["col_index"],
                            set_as_original=True, conn=conn
                        )
                for lk_s, rows_s in list(all_layouts.items()):
                    if lk_s == c_layout_key:
                        continue
                    if any(sb in r for r in rows_s):
                        new_rs = [[k for k in r if k != sb] for r in rows_s]
                        new_rs = [r for r in new_rs if r]
                        all_layouts[lk_s] = new_rs
                        conn.execute(
                            "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                            (lk_s, json.dumps(new_rs, ensure_ascii=False))
                        )
                        sync_layout_placements_in_db(lk_s, new_rs, conn=conn)
                child_layout.append([sb])

            conn.execute(
                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                (c_layout_key, json.dumps(child_layout, ensure_ascii=False))
            )
            sync_layout_placements_in_db(c_layout_key, child_layout, conn=conn)

            eff_msg = str(msg_content or f"📂 <b>{lbl}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের অপশনগুলো থেকে নির্বাচন করুন:")
            eff_raw_msg = str(raw_msg_text or eff_msg)
            eff_ents_json = json.dumps(msg_entities or [], ensure_ascii=False)
            prev_dm = conn.execute("SELECT button_mode, custom_buttons_json FROM dynamic_messages WHERE msg_key = ? LIMIT 1", (c_msg_key,)).fetchone()
            pres_bmode = str((prev_dm["button_mode"] if prev_dm and prev_dm["button_mode"] else "default")).strip().lower()
            if pres_bmode not in ("default", "custom", "none"):
                pres_bmode = "default"
            pres_cbtns = str((prev_dm["custom_buttons_json"] if prev_dm and prev_dm["custom_buttons_json"] else "[]"))
            conn.execute("""
                INSERT OR REPLACE INTO dynamic_messages (
                    msg_key, content, raw_text, entities_json,
                    prev_content, prev_raw_text, prev_entities_json,
                    button_mode, custom_buttons_json,
                    version, updated_by, updated_at
                ) VALUES (?, ?, ?, ?, '', '', '[]', ?, ?, 1, ?, ?)
            """, (c_msg_key, eff_msg, eff_raw_msg, eff_ents_json, pres_bmode, pres_cbtns, str(updated_by), now_str))

            return {
                "ok": True,
                "btn_key": cand_key,
                "side": s_side,
                "parent_layout": placement_lay,
                "destination_layout": dest_lay,
                "row_index": eff_r,
                "col_index": eff_c,
                "parent_container_key": p_cont,
                "label": lbl,
                "style": st_col,
                "design_style": des,
                "custom_emoji_id": em_id,
                "msg_key": c_msg_key,
                "layout_key": c_layout_key,
                "sub_buttons": sub_list
            }

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def delete_custom_button_transactional(btn_key: str, conn: sqlite3.Connection = None) -> dict:
    """
    Atomically deletes a Custom Container Button (`btn_key`):
    1. Detects the container's actual current location across ALL layouts (even if moved after creation).
    2. Recursively collects all functional buttons inside `custom_page_<btn_key>` (and any nested containers being dissolved or restores nested containers to their original locations).
    3. Restores every child button inside the deleted container to its exact original `(original_layout_key, original_row_index, original_col_index)`.
    4. Removes `btn_key`, its layout `custom_page_<btn_key>`, its message `custom_msg_<btn_key>`, and cleans up all orphan records.
    """
    bk = str(btn_key or "").strip()
    if not bk:
        return {"ok": False, "reason": "Empty button key"}

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        def _exec():
            cb_row = conn.execute("SELECT * FROM custom_buttons WHERE btn_key = ? LIMIT 1", (bk,)).fetchone()
            c_layout_key = str(cb_row["layout_key"]) if cb_row and cb_row["layout_key"] else f"custom_page_{bk}"
            c_msg_key = str(cb_row["msg_key"]) if cb_row and cb_row["msg_key"] else f"custom_msg_{bk}"
            direct_key = f"{bk}_direct"

            actual_locations = locate_button_across_all_layouts(bk, conn=conn)
            all_layouts = _load_all_layouts_from_db(conn)

            child_rows = all_layouts.get(c_layout_key, [])
            child_keys = [k for r in child_rows for k in r if k and k != direct_key and k != bk]

            # Remove `bk` and `direct_key` from every layout where they currently reside
            for lk_name, rows_list in list(all_layouts.items()):
                if lk_name == c_layout_key:
                    continue
                if any(k in (bk, direct_key) for r in rows_list for k in r):
                    cleaned = [[k for k in r if k not in (bk, direct_key)] for r in rows_list]
                    cleaned = [r for r in cleaned if r]
                    all_layouts[lk_name] = cleaned
                    conn.execute(
                        "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                        (lk_name, json.dumps(cleaned, ensure_ascii=False))
                    )
                    sync_layout_placements_in_db(lk_name, cleaned, conn=conn)

            # Delete the container record and its layout/message before restoring children so children never restore back into the deleted container
            conn.execute("DELETE FROM custom_buttons WHERE btn_key = ?", (bk,))
            conn.execute("DELETE FROM dynamic_layouts WHERE layout_key = ?", (c_layout_key,))
            conn.execute("DELETE FROM dynamic_messages WHERE msg_key = ?", (c_msg_key,))
            for k_del in (bk, direct_key):
                conn.execute("DELETE FROM button_labels WHERE btn_key = ?", (k_del,))
                conn.execute("DELETE FROM button_styles WHERE btn_key = ?", (k_del,))
                conn.execute("DELETE FROM button_original_placements WHERE btn_key = ?", (k_del,))

            restored_children = []
            for ck in child_keys:
                res_r = restore_button_to_original_placement(
                    ck,
                    from_container_layout="",
                    conn=conn,
                    avoid_layouts={c_layout_key}
                )
                if res_r.get("ok"):
                    restored_children.append(res_r)

            cleanup_info = cleanup_orphan_custom_layouts_and_messages(conn=conn)
            return {
                "ok": True,
                "deleted_btn_key": bk,
                "detected_locations": actual_locations,
                "restored_children": restored_children,
                "restored_buttons": restored_children,
                "cleanup": cleanup_info
            }

        with begin_immediate_transaction(conn):
            return _exec()
    finally:
        if own_conn:
            conn.close()


def get_all_custom_buttons(side: str = "") -> list:
    conn = get_connection()
    try:
        if side in ("user", "admin"):
            rows = conn.execute("SELECT * FROM custom_buttons WHERE side = ? ORDER BY rowid ASC", (side,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM custom_buttons ORDER BY rowid ASC").fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


def get_custom_button(btn_key: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM custom_buttons WHERE btn_key = ? LIMIT 1", (str(btn_key or "").strip(),)).fetchone()
        return dict(row) if row else {}
    except Exception:
        return {}
    finally:
        conn.close()


def save_custom_button(
    btn_key: str,
    side: str,
    parent_layout: str,
    label: str,
    style: str = "primary",
    design_style: str = "normal",
    custom_emoji_id: str = "",
    msg_key: str = "",
    layout_key: str = "",
    destination_layout: str = "",
    row_index: int = 0,
    col_index: int = 0,
    parent_container_key: str = "",
    allow_update: bool = True
) -> dict:
    bk = str(btn_key or "").strip()
    s_side = "admin" if str(side).lower().strip() == "admin" else "user"
    p_lay = str(parent_layout or ("admin_home" if s_side == "admin" else "user_home")).strip()
    d_lay = str(destination_layout or p_lay).strip()
    lbl = str(label or "নতুন বাটন").strip()
    st_col = style if style in ("success", "danger", "primary") else "primary"
    des = str(design_style or "normal").strip()
    em_id = str(custom_emoji_id or "").strip()
    m_key = str(msg_key or f"custom_msg_{bk}").strip()
    l_key = str(layout_key or f"custom_page_{bk}").strip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            existing = conn.execute("SELECT * FROM custom_buttons WHERE btn_key = ? LIMIT 1", (bk,)).fetchone()
            if existing and not allow_update:
                raise ValueError(f"Custom button ID '{bk}' already exists and overwrite is disabled.")
            if not existing:
                conn.execute("""
                    INSERT INTO custom_buttons (
                        btn_key, side, parent_layout, destination_layout,
                        row_index, col_index, parent_container_key,
                        original_layout_key, original_row_index, original_col_index,
                        label, style, design_style, custom_emoji_id,
                        msg_key, layout_key, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bk, s_side, p_lay, d_lay,
                    int(row_index), int(col_index), str(parent_container_key or ""),
                    d_lay, int(row_index), int(col_index),
                    lbl, st_col, des, em_id, m_key, l_key, now_str
                ))
                record_button_placement(bk, d_lay, int(row_index), int(col_index), set_as_original=True, conn=conn)
            else:
                conn.execute("""
                    UPDATE custom_buttons
                    SET side = ?, parent_layout = ?, destination_layout = ?,
                        label = ?, style = ?, design_style = ?, custom_emoji_id = ?,
                        msg_key = ?, layout_key = ?
                    WHERE btn_key = ?
                """, (s_side, p_lay, d_lay, lbl, st_col, des, em_id, m_key, l_key, bk))
        return get_custom_button(bk)
    finally:
        conn.close()


def delete_custom_button_record(btn_key: str) -> bool:
    res = delete_custom_button_transactional(btn_key)
    return bool(res.get("ok"))


# ==============================================================================
# COMPATIBILITY WRAPPERS FOR BOT & TEST SUITE (v9.0)
# ==============================================================================
def generate_admin_manual_verify_code(admin_id: str = "admin", expiry_sec: int = 300, target_user_id: str = "", platform: str = "", profile_url: str = "") -> dict:
    eff_ttl = int(expiry_sec if (expiry_sec is not None and int(expiry_sec) > 0) else 300)
    res = create_manual_verification_code(
        admin_id=str(admin_id),
        target_user_id=str(target_user_id or ""),
        platform=str(platform or ""),
        profile_url=str(profile_url or ""),
        ttl_sec=eff_ttl
    )
    res["expires_at_str"] = "৫ মিনিট (১ বার ব্যবহারযোগ্য)"
    return res


def consume_admin_manual_verify_code(
    code: str,
    user_id: str,
    platform: str = "",
    profile_url: str = "",
    bio_code: str = "",
    auto_bind: bool = False
) -> dict:
    uid = str(user_id or "").strip()
    plat = str(platform or "").lower().strip() or "youtube"
    p_url = str(profile_url or "").strip()
    h = _normalize_handle("", p_url) or f"manual_{uid}_{plat}"
    ok, res_or_err = consume_manual_verification_code(
        user_id=uid,
        platform=plat,
        profile_url=p_url,
        profile_handle=h,
        bio_code=str(bio_code or ""),
        raw_code=str(code or ""),
        failure_reason="Submitted with Admin Random Code for Manual Approval" if not auto_bind else "Instant Bypass via Admin Random Code",
        auto_approve=bool(auto_bind and p_url)
    )
    if not ok:
        return {"ok": False, "reason": res_or_err}
    return {"ok": True, "code": str(code or "").strip().upper(), "req_id": res_or_err, "auto_approved": bool(auto_bind and p_url)}


def create_manual_verification_request(
    user_id: str,
    platform: str,
    profile_url: str,
    bio_code: str,
    code_used: str = "",
    failure_reason: str = "",
    status: str = "pending"
) -> str:
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uid = str(user_id or "").strip()
    plat = str(platform or "").lower().strip()
    req_id = f"MVRQ_{int(now_ts*1000)}_{uid[-4:]}"
    h = _normalize_handle("", profile_url) or f"manual_{uid}_{plat}"
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            conn.execute("""
                INSERT INTO manual_verification_requests (
                    req_id, user_id, platform, profile_url, profile_handle, bio_code,
                    manual_code_used, decision_note, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (req_id, uid, plat, str(profile_url or ""), h, str(bio_code or ""), str(code_used or ""), str(failure_reason or ""), str(status or "pending"), now_str))
        return req_id
    finally:
        conn.close()


def get_pending_manual_verifications() -> list:
    rows = get_manual_verification_requests("pending")
    out = []
    for r in rows:
        d = dict(r)
        d.setdefault("id", d.get("req_id"))
        d.setdefault("code_used", d.get("manual_code_used", ""))
        out.append(d)
    return out


def get_dynamic_message_history(msg_key: str, limit: int = 8) -> list:
    rec = get_dynamic_message_record(msg_key)
    prev = str(rec.get("prev_content") or "").strip()
    if not prev:
        return []
    return [{
        "id": 1,
        "msg_key": msg_key,
        "content": prev,
        "saved_at": rec.get("updated_at") or "Previous Version"
    }]


def rollback_dynamic_message(msg_key: str, hist_id: int = 1, actor_id: str = "admin") -> dict:
    try:
        res = rollback_dynamic_message_record(msg_key, updated_by=str(actor_id))
        return {"ok": True, "content": res.get("content", ""), "msg_key": msg_key}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}


def consume_code_and_create_manual_request(
    code: str,
    user_id: str,
    platform: str,
    profile_url: str,
    bio_code: str,
    failure_reason: str = "",
    auto_approve: bool = False
) -> dict:
    h = _normalize_handle("", profile_url) or f"manual_{user_id}_{platform}"
    ok, res_or_err = consume_manual_verification_code(
        user_id=str(user_id),
        platform=str(platform),
        profile_url=str(profile_url),
        profile_handle=h,
        bio_code=str(bio_code or ""),
        raw_code=str(code or ""),
        failure_reason=str(failure_reason or ""),
        auto_approve=auto_approve
    )
    if not ok:
        return {"ok": False, "reason": res_or_err}
    return {"ok": True, "req_id": res_or_err, "code": str(code or "").strip().upper(), "auto_approved": auto_approve}


def create_broadcast_job(admin_id: str, content_type: str = "text", max_retries: int = 5) -> dict:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_id = f"BCJOB_{int(time.time()*1000)}_{secrets.token_hex(2).upper()}"
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            users = conn.execute("SELECT user_id FROM users WHERE COALESCE(status, 'active') != 'deleted'").fetchall()
            uids = [str(r["user_id"]) for r in users if str(r["user_id"]).strip()]
            conn.execute("""
                INSERT INTO broadcast_jobs (
                    job_id, admin_id, content_type, total_recipients, sent_count, failed_count, max_retries, status, created_at
                ) VALUES (?, ?, ?, ?, 0, 0, ?, 'running', ?)
            """, (job_id, str(admin_id), str(content_type or "text"), len(uids), int(max_retries or 5), now_str))
            for u_id in uids:
                conn.execute("""
                    INSERT OR IGNORE INTO broadcast_deliveries (
                        job_id, user_id, status, attempts, last_error, updated_at
                    ) VALUES (?, ?, 'pending', 0, '', ?)
                """, (job_id, u_id, now_str))
        return {"job_id": job_id, "total_recipients": len(uids), "user_ids": uids}
    finally:
        conn.close()


def get_pending_broadcast_targets(job_id: str, max_retries: int = 5) -> list:
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT user_id, attempts FROM broadcast_deliveries
            WHERE job_id = ? AND status != 'delivered' AND attempts < ?
            ORDER BY rowid ASC
        """, (str(job_id), int(max_retries or 5))).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def record_broadcast_delivery_attempt(job_id: str, user_id: str, delivered: bool, error_msg: str = ""):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st = "delivered" if delivered else "failed"
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            conn.execute("""
                UPDATE broadcast_deliveries
                SET status = CASE WHEN status = 'delivered' THEN 'delivered' ELSE ? END,
                    attempts = attempts + 1,
                    last_error = ?,
                    updated_at = ?
                WHERE job_id = ? AND user_id = ?
            """, (st, str(error_msg or "")[:200], now_str, str(job_id), str(user_id)))
    finally:
        conn.close()


def finalize_broadcast_job(job_id: str) -> dict:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            stats = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'delivered' AND attempts > 1 THEN 1 ELSE 0 END) as retried_ok,
                    SUM(CASE WHEN status != 'delivered' THEN 1 ELSE 0 END) as failed
                FROM broadcast_deliveries
                WHERE job_id = ?
            """, (str(job_id),)).fetchone()
            tot = int(stats["total"] or 0)
            snt = int(stats["sent"] or 0)
            ret_ok = int(stats["retried_ok"] or 0)
            fld = int(stats["failed"] or 0)
            conn.execute("""
                UPDATE broadcast_jobs
                SET sent_count = ?, failed_count = ?, status = 'completed', completed_at = ?
                WHERE job_id = ?
            """, (snt, fld, now_str, str(job_id)))
            return {"job_id": job_id, "total": tot, "sent": snt, "retried_ok": ret_ok, "failed": fld}
    finally:
        conn.close()


def sync_and_get_pending_broadcast_targets(job_id: str, max_retries: int = 5) -> list:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            users = conn.execute("SELECT user_id FROM users WHERE COALESCE(status, 'active') != 'deleted'").fetchall()
            for r in users:
                u_id = str(r["user_id"]).strip()
                if u_id:
                    conn.execute("""
                        INSERT OR IGNORE INTO broadcast_deliveries (
                            job_id, user_id, status, attempts, last_error, updated_at
                        ) VALUES (?, ?, 'pending', 0, '', ?)
                    """, (str(job_id), u_id, now_str))
            total_c = conn.execute("SELECT COUNT(*) as c FROM broadcast_deliveries WHERE job_id = ?", (str(job_id),)).fetchone()["c"]
            conn.execute("UPDATE broadcast_jobs SET total_recipients = ? WHERE job_id = ?", (int(total_c or 0), str(job_id)))
            rows = conn.execute("""
                SELECT user_id, attempts FROM broadcast_deliveries
                WHERE job_id = ? AND status != 'delivered' AND attempts < ?
                ORDER BY rowid ASC
            """, (str(job_id), int(max_retries or 5))).fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def verify_and_consume_profile_edit_random_code(user_id: str, raw_code: str, unlock_seconds: int = 600) -> dict:
    uid = str(user_id or "").strip()
    c_str = str(raw_code or "").strip().upper()
    if not re.fullmatch(r"(?:BC|MVR)-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ0-9]{6,10}", c_str):
        return {"ok": False, "reason": "সঠিক ফরম্যাটের র‍্যান্ডম কোড দিন (যেমন BC-XXXXXX)!"}
    now_ts = time.time()
    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            row = conn.execute("SELECT * FROM manual_verification_codes WHERE code = ?", (c_str,)).fetchone()
            if not row:
                return {"ok": False, "reason": "এই র‍্যান্ডম কোডটি পাওয়া যায়নি! অ্যাডমিনের থেকে নতুন কোড নিন।"}
            if int(row["used"] or 0) == 1 or row["status"] != "active":
                return {"ok": False, "reason": "এই র‍্যান্ডম কোডটি ইতিমধ্যে ১ বার ব্যবহার করা হয়ে গেছে! নতুন আরেকটি কোড নিন।"}
            if row["target_user_id"] and str(row["target_user_id"]) != uid:
                return {"ok": False, "reason": "এই র‍্যান্ডম কোডটি আপনার ইউজার আইডির জন্য তৈরি করা হয়নি!"}
            cur = conn.execute(
                "UPDATE manual_verification_codes SET used = 1, used_by = ?, used_at_ts = ?, status = 'used_profile_edit' WHERE code = ? AND used = 0",
                (uid, now_ts, c_str)
            )
            if cur.rowcount != 1:
                return {"ok": False, "reason": "র‍্যান্ডম কোডটি ইতিমধ্যে ব্যবহৃত হয়েছে!"}
            unlock_until = now_ts + max(60, int(unlock_seconds or 600))
            conn.execute("UPDATE users SET profile_edit_unlocked_until = ? WHERE user_id = ?", (unlock_until, uid))
            log_audit_event(uid, "Profile Edit Random Code Verified", f"Verified code {c_str} for profile/payment update", target_user_id=uid, conn=conn)
            return {"ok": True, "code": c_str, "unlocked_until": unlock_until}
    finally:
        conn.close()


def _split_stored_multi_values(raw_val: str) -> list:
    if not raw_val:
        return []
    s = str(raw_val).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            arr = json.loads(s)
            if isinstance(arr, list):
                return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    return [p.strip() for p in re.split(r"[,;|\n]+", s) if p.strip()]


def update_user_payment_and_profile_info(
    user_id: str,
    field: str,
    new_value: str,
    action: str = "replace",
    slot_index: int = None
) -> dict:
    """
    Enterprise v10.0 Profile & Multi-Slot Payment Number / UID Updater:
    - Supports `name`, `channel_name`, `youtube_channel_name`, `tiktok_channel_name`, `platform_acc_name:<id>`
    - Supports up to 2 numbers/UIDs per method across all 4 methods:
      `bkash_number` (max 2), `nagad_number` (max 2), `rocket_number` (max 2), `app_uid` (max 2).
    - Supports `action='add'` (adds a 2nd slot if < 2 exist), `action='replace'` (updates slot `slot_index` or replaces),
      and `action='delete'` (removes slot `slot_index`).
    """
    uid = str(user_id or "").strip()
    f_key = str(field or "").strip()
    val = str(new_value or "").strip()
    act = str(action or "replace").strip().lower()

    if ":" in f_key and not f_key.startswith("platform_acc_name:"):
        # Support encoded field format like `bkash_number:add` or `bkash_number:replace:1` or `bkash_number:delete:0`
        f_parts = f_key.split(":")
        f_key = f_parts[0]
        if len(f_parts) > 1 and f_parts[1] in ("add", "replace", "delete"):
            act = f_parts[1]
        if len(f_parts) > 2 and f_parts[2].lstrip("-").isdigit():
            slot_index = int(f_parts[2])

    if not uid or (not val and act != "delete"):
        return {"ok": False, "reason": "ফাঁকা মান গ্রহণযোগ্য নয়!"}

    conn = get_connection()
    try:
        with begin_immediate_transaction(conn):
            u = conn.execute("SELECT * FROM users WHERE user_id = ?", (uid,)).fetchone()
            if not u:
                return {"ok": False, "reason": "ইউজার পাওয়া যায়নি!"}

            if f_key == "name":
                if len(val) < 2:
                    return {"ok": False, "reason": "নাম কমপক্ষে ২ অক্ষরের হতে হবে!"}
                conn.execute("UPDATE users SET name = ? WHERE user_id = ?", (val, uid))
                log_audit_event(uid, "Profile Name Updated", f"Updated name to {val}", target_user_id=uid, conn=conn)
                return {"ok": True, "field": f_key, "value": val}

            if f_key.startswith("platform_acc_name:"):
                plat_id_s = f_key.split(":", 1)[1].strip()
                if len(val) < 2:
                    return {"ok": False, "reason": "ভেরিফিকেশন অ্যাকাউন্টের নাম কমপক্ষে ২ অক্ষরের হতে হবে!"}
                if plat_id_s.isdigit():
                    p_row = conn.execute("SELECT * FROM user_platforms WHERE id = ? AND user_id = ?", (int(plat_id_s), uid)).fetchone()
                    if p_row:
                        conn.execute("UPDATE user_platforms SET display_name = ? WHERE id = ? AND user_id = ?", (val[:60], int(plat_id_s), uid))
                        pk_low = str(p_row["platform"] or "").lower()
                        if pk_low == "youtube":
                            conn.execute("UPDATE users SET youtube_channel_name = ?, channel_name = ? WHERE user_id = ?", (val[:60], val[:60], uid))
                        elif pk_low == "tiktok":
                            conn.execute("UPDATE users SET tiktok_channel_name = ?, channel_name = ? WHERE user_id = ?", (val[:60], val[:60], uid))
                        log_audit_event(uid, "Verified Account Name Updated", f"Updated platform #{plat_id_s} name to {val}", target_user_id=uid, conn=conn)
                        return {"ok": True, "field": f_key, "value": val[:60]}
                conn.execute("UPDATE users SET channel_name = ? WHERE user_id = ?", (val[:60], uid))
                conn.execute("UPDATE user_platforms SET display_name = ? WHERE user_id = ?", (val[:60], uid))
                return {"ok": True, "field": "channel_name", "value": val[:60]}

            if f_key in ("channel_name", "youtube_channel_name", "tiktok_channel_name"):
                if len(val) < 2:
                    return {"ok": False, "reason": "চ্যানেল / প্রোফাইলের নাম কমপক্ষে ২ অক্ষরের হতে হবে!"}
                conn.execute(f"UPDATE users SET {f_key} = ? WHERE user_id = ?", (val[:60], uid))
                if f_key == "youtube_channel_name":
                    conn.execute("UPDATE user_platforms SET display_name = ? WHERE user_id = ? AND LOWER(platform) = 'youtube'", (val[:60], uid))
                elif f_key == "tiktok_channel_name":
                    conn.execute("UPDATE user_platforms SET display_name = ? WHERE user_id = ? AND LOWER(platform) = 'tiktok'", (val[:60], uid))
                else:
                    conn.execute("UPDATE user_platforms SET display_name = ? WHERE user_id = ?", (val[:60], uid))
                log_audit_event(uid, "Channel Name Updated", f"Updated {f_key} to {val}", target_user_id=uid, conn=conn)
                return {"ok": True, "field": f_key, "value": val[:60]}

            if f_key == "app_uid":
                cur_uids = _split_stored_multi_values(u["app_uid"] if "app_uid" in u.keys() else "")
                cur_uids = [format_display_app_uid(x) for x in cur_uids if format_display_app_uid(x)]
                if act == "delete":
                    if len(cur_uids) <= 1:
                        return {"ok": False, "reason": "কমপক্ষে ১টি Battle Club UID সংরক্ষিত থাকা আবশ্যক! আপনি এটি পরিবর্তন (Edit) করতে পারেন।"}
                    idx_del = int(slot_index) if (slot_index is not None and 0 <= int(slot_index) < len(cur_uids)) else (len(cur_uids) - 1)
                    removed_u = cur_uids.pop(idx_del)
                    rem_canon = canonicalize_app_uid(removed_u)
                    conn.execute(
                        "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'app_uid' AND LOWER(canonical_value) IN (LOWER(?), LOWER(?))",
                        (uid, removed_u, rem_canon)
                    )
                    new_joined = ", ".join(cur_uids)
                    conn.execute("UPDATE users SET app_uid = ? WHERE user_id = ?", (new_joined, uid))
                    log_audit_event(uid, "Battle Club UID Deleted", f"Removed {removed_u}; active: {new_joined}", target_user_id=uid, conn=conn)
                    return {"ok": True, "field": f_key, "value": new_joined, "slots": cur_uids}

                # Parse candidate UID(s)
                raw_parts = [p.strip() for p in re.split(r"[,;|\n]+", val) if p.strip()]
                if len(raw_parts) > 2:
                    return {"ok": False, "reason": "সর্বোচ্চ ২টি Battle Club UID যুক্ত করা যাবে! ২টির অধিক সেট করা যাবে না।"}
                cand_uids = []
                for rp in raw_parts:
                    du = format_display_app_uid(rp)
                    if len(re.sub(r"[^0-9A-Z]", "", du)) < 2:
                        return {"ok": False, "reason": "সঠিক Battle Club অ্যাপ UID হ্যাশট্যাগ ও সংখ্যা (যেমন #107 বা #1007) সহ দিন!"}
                    if du not in cand_uids:
                        cand_uids.append(du)

                if act == "add":
                    if len(cur_uids) >= 2:
                        return {"ok": False, "reason": "আপনার ইতিমধ্যে ২টি Battle Club UID সেট করা আছে! নতুন UID সেট করতে আগের যেকোনো ১টি ডিলিট বা পরিবর্তন করুন।"}
                    for cu in cand_uids:
                        if any(canonicalize_app_uid(cu) == canonicalize_app_uid(ex) for ex in cur_uids):
                            return {"ok": False, "reason": f"{cu} ইতিমধ্যে আপনার অ্যাকাউন্টে যুক্ত আছে!"}
                        if len(cur_uids) >= 2:
                            return {"ok": False, "reason": "সর্বোচ্চ ২টি Battle Club UID সেট করা যাবে!"}
                        ok_l, msg_l = check_and_lock_user_identity(uid, app_uid=cu, commit_lock=True, conn=conn)
                        if not ok_l:
                            return {"ok": False, "reason": msg_l}
                        cur_uids.append(cu)
                    new_joined = ", ".join(cur_uids)
                elif slot_index is not None and 0 <= int(slot_index) < len(cur_uids) and len(cand_uids) == 1:
                    target_u = cand_uids[0]
                    old_u = cur_uids[int(slot_index)]
                    ok_l, msg_l = check_and_lock_user_identity(uid, app_uid=target_u, commit_lock=True, conn=conn)
                    if not ok_l:
                        return {"ok": False, "reason": msg_l}
                    if old_u != target_u:
                        old_canon = canonicalize_app_uid(old_u)
                        conn.execute(
                            "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'app_uid' AND LOWER(canonical_value) IN (LOWER(?), LOWER(?))",
                            (uid, old_u, old_canon)
                        )
                    cur_uids[int(slot_index)] = target_u
                    # Deduplicate while preserving order
                    dedup_u = []
                    for x in cur_uids:
                        if x not in dedup_u:
                            dedup_u.append(x)
                    cur_uids = dedup_u[:2]
                    new_joined = ", ".join(cur_uids)
                else:
                    for cu in cand_uids:
                        ok_l, msg_l = check_and_lock_user_identity(uid, app_uid=cu, commit_lock=True, conn=conn)
                        if not ok_l:
                            return {"ok": False, "reason": msg_l}
                    for old_u in cur_uids:
                        if all(canonicalize_app_uid(old_u) != canonicalize_app_uid(cu) for cu in cand_uids):
                            old_canon = canonicalize_app_uid(old_u)
                            conn.execute(
                                "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'app_uid' AND LOWER(canonical_value) IN (LOWER(?), LOWER(?))",
                                (uid, old_u, old_canon)
                            )
                    cur_uids = cand_uids[:2]
                    new_joined = ", ".join(cur_uids)

                conn.execute("UPDATE users SET app_uid = ? WHERE user_id = ?", (new_joined, uid))
                log_audit_event(uid, "Battle Club UID Updated", f"Updated app_uid to {new_joined}", target_user_id=uid, conn=conn)
                return {"ok": True, "field": f_key, "value": new_joined, "slots": cur_uids}

            if f_key in ("bkash_number", "nagad_number", "rocket_number", "phone"):
                eff_col = "bkash_number" if f_key == "phone" and not str(u["bkash_number"] or "").strip() else f_key
                cur_nums = _split_stored_multi_values(u[eff_col] if eff_col in u.keys() else "")
                allow_12 = (eff_col == "rocket_number")
                cur_nums = [normalize_bd_payment_number(x, allow_rocket_12=allow_12) for x in cur_nums if normalize_bd_payment_number(x, allow_rocket_12=allow_12)]

                if act == "delete":
                    if not cur_nums:
                        return {"ok": False, "reason": "ডিলিট করার মতো কোনো নাম্বার যুক্ত নেই!"}
                    idx_del = int(slot_index) if (slot_index is not None and 0 <= int(slot_index) < len(cur_nums)) else (len(cur_nums) - 1)
                    removed_n = cur_nums.pop(idx_del)
                    # Only delete lock if this number isn't still used in another method of this user
                    other_cols = [c for c in ("bkash_number", "nagad_number", "rocket_number") if c != eff_col]
                    still_used = False
                    for oc in other_cols:
                        if removed_n in _split_stored_multi_values(u[oc] if oc in u.keys() else ""):
                            still_used = True
                    if not still_used:
                        conn.execute(
                            "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'payment_number' AND canonical_value = ?",
                            (uid, removed_n)
                        )
                    new_joined = ", ".join(cur_nums)
                    conn.execute(f"UPDATE users SET {eff_col} = ? WHERE user_id = ?", (new_joined, uid))
                    if eff_col == "bkash_number" and cur_nums:
                        conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (cur_nums[0], uid))
                    log_audit_event(uid, f"Payment Number Deleted ({eff_col})", f"Removed {removed_n}; active: {new_joined}", target_user_id=uid, conn=conn)
                    return {"ok": True, "field": eff_col, "value": new_joined, "slots": cur_nums}

                # Check if user entered multiple numbers separated by space/comma
                raw_tokens = [p.strip() for p in re.split(r"[\s,;]+", val.strip()) if p.strip()]
                if len(raw_tokens) > 1:
                    return {"ok": False, "reason": "একবারে ১টি সচল নাম্বার লিখে পাঠান (একই মাধ্যমে সর্বোচ্চ ২টি নাম্বার ধাপে ধাপে যুক্ত করা যাবে)!"}

                clean_ph = normalize_bd_payment_number(val, allow_rocket_12=allow_12)
                if not clean_ph:
                    return {"ok": False, "reason": "সঠিক বাংলাদেশি মোবাইল পেমেন্ট নাম্বার (01XXXXXXXXX) দিন!"}

                if act == "add":
                    if len(cur_nums) >= 2:
                        return {"ok": False, "reason": "এই মাধ্যমে ইতিমধ্যে সর্বোচ্চ ২টি নাম্বার যুক্ত আছে! নতুন নাম্বার যুক্ত করতে আগের যেকোনো ১টি ডিলিট বা পরিবর্তন করুন।"}
                    if clean_ph in cur_nums:
                        return {"ok": False, "reason": f"{clean_ph} নাম্বারটি ইতিমধ্যে এই মাধ্যমে যুক্ত আছে!"}
                    ok_l, msg_l = check_and_lock_user_identity(uid, phone=clean_ph, commit_lock=True, conn=conn)
                    if not ok_l:
                        return {"ok": False, "reason": msg_l}
                    cur_nums.append(clean_ph)
                elif slot_index is not None and 0 <= int(slot_index) < len(cur_nums):
                    old_ph = cur_nums[int(slot_index)]
                    ok_l, msg_l = check_and_lock_user_identity(uid, phone=clean_ph, commit_lock=True, conn=conn)
                    if not ok_l:
                        return {"ok": False, "reason": msg_l}
                    if old_ph != clean_ph:
                        other_cols = [c for c in ("bkash_number", "nagad_number", "rocket_number") if c != eff_col]
                        still_used = any(old_ph in _split_stored_multi_values(u[oc] if oc in u.keys() else "") for oc in other_cols)
                        if not still_used:
                            conn.execute(
                                "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'payment_number' AND canonical_value = ?",
                                (uid, old_ph)
                            )
                    cur_nums[int(slot_index)] = clean_ph
                    dedup_n = []
                    for x in cur_nums:
                        if x not in dedup_n:
                            dedup_n.append(x)
                    cur_nums = dedup_n[:2]
                else:
                    # Default behavior: if 0 numbers exist, set as 1st; if 1 exists and act=='replace' without slot_index, replace slot 0 (or if 2 exist, replace slot 0)
                    old_ph = cur_nums[0] if cur_nums else ""
                    ok_l, msg_l = check_and_lock_user_identity(uid, phone=clean_ph, commit_lock=True, conn=conn)
                    if not ok_l:
                        return {"ok": False, "reason": msg_l}
                    if old_ph and old_ph != clean_ph:
                        other_cols = [c for c in ("bkash_number", "nagad_number", "rocket_number") if c != eff_col]
                        still_used = any(old_ph in _split_stored_multi_values(u[oc] if oc in u.keys() else "") for oc in other_cols)
                        if not still_used and old_ph not in cur_nums[1:]:
                            conn.execute(
                                "DELETE FROM user_identity_locks WHERE user_id = ? AND lock_type = 'payment_number' AND canonical_value = ?",
                                (uid, old_ph)
                            )
                    if cur_nums:
                        cur_nums[0] = clean_ph
                        dedup_n = []
                        for x in cur_nums:
                            if x not in dedup_n:
                                dedup_n.append(x)
                        cur_nums = dedup_n[:2]
                    else:
                        cur_nums = [clean_ph]

                new_joined = ", ".join(cur_nums)
                conn.execute(f"UPDATE users SET {eff_col} = ? WHERE user_id = ?", (new_joined, uid))
                if f_key == "phone" and eff_col != "phone":
                    conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (clean_ph, uid))
                elif not str(u["phone"] or "").strip() or eff_col == "bkash_number":
                    conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (cur_nums[0], uid))

                m_map = {"bkash_number": "bKash", "nagad_number": "Nagad", "rocket_number": "Rocket"}
                m_name = m_map.get(eff_col)
                if m_name:
                    try:
                        cur_sel = json.loads(u["selected_payment_methods"] or "[]")
                    except Exception:
                        cur_sel = ["bKash", "BattleClub_UID"]
                    if m_name not in cur_sel:
                        cur_sel.append(m_name)
                    if "BattleClub_UID" not in cur_sel:
                        cur_sel.append("BattleClub_UID")
                    conn.execute("UPDATE users SET selected_payment_methods = ? WHERE user_id = ?", (json.dumps(cur_sel), uid))
                log_audit_event(uid, f"Payment Number Updated ({eff_col})", f"Updated {eff_col} to {new_joined}", target_user_id=uid, conn=conn)
                return {"ok": True, "field": eff_col, "value": new_joined, "latest_added": clean_ph, "slots": cur_nums}

            return {"ok": False, "reason": "অবৈধ প্রোফাইল ফিল্ড!"}
    finally:
        conn.close()


def get_button_design_map(conn: sqlite3.Connection = None) -> dict:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        out = {}
        for tbl in ("button_labels", "button_styles"):
            try:
                rows = conn.execute(f"SELECT btn_key, design_style FROM {tbl}").fetchall()
                for r in rows:
                    val = str(r["design_style"] or "").strip()
                    if val and val != "normal":
                        out[r["btn_key"]] = val
            except Exception:
                continue
        return out
    finally:
        if own_conn:
            conn.close()

def run_database_integrity_diagnostics(conn: sqlite3.Connection = None) -> dict:
    """Runs PRAGMA integrity_check, PRAGMA foreign_key_check, and ledger balance conservation diagnostics (P1-24)."""
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        ok_int, int_msg = verify_sqlite_integrity(conn)
        fk_rows = conn.execute("PRAGMA foreign_key_check;").fetchall()
        fk_list = [dict(r) if isinstance(r, sqlite3.Row) else list(r) for r in fk_rows]
        return {
            "ok": bool(ok_int and len(fk_list) == 0),
            "integrity_check": int_msg,
            "foreign_key_violations": fk_list,
        }
    finally:
        if own_conn and conn:
            conn.close()