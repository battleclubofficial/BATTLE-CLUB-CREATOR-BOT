# -*- coding: utf-8 -*-
"""
BATTLE CLUB TELEGRAM BOT - ENTERPRISE SECURITY & CRYPTOGRAPHY MODULE (v9.0)
- Strictly YouTube & TikTok Only Platform Domain Allowlist
- PBKDF2-HMAC-SHA256 Password Hashing with Random Cryptographic Salt (200,000 iterations)
- Constant-Time Password & Admin Secret Comparison (`hmac.compare_digest`)
- Role-Bound Admin Session Unlock & Failed Login Attempt Counter (4-5 Attempt Support Trigger)
- Bounded Memory Caches with Automatic Expiry Cleanup (`MAX_MEMORY_CACHE_ENTRIES`)
- Collision-Free UUID / Cryptographically Secure Custom Button ID & Token Generators
- Proper Domain Normalization (`normalize_domain_host` without `lstrip("www.")` bug)
- Fail-Closed DNS Resolution, DNS-Rebinding Socket Pinning & Per-Hop Redirect SSRF Validator
- Navigation-Safe Rate Limiter, Duplicate Callback Guard & Atomic Flow Lock per User/Action
"""

import re
import ssl
import uuid
import time
import hmac
import socket
import hashlib
import secrets
import ipaddress
import threading
import http.client
import urllib.parse
import urllib.request
import urllib.error

_rate_limit_lock = threading.RLock()
_rate_limit_buckets = {}
_flow_locks = {}
_recent_callbacks = {}
_failed_login_counts = {}
_admin_unlocked_sessions = {}

MAX_MEMORY_CACHE_ENTRIES = 5000

PLATFORM_ALLOWED_DOMAINS = {
    "youtube": [
        "youtube.com",
        "youtu.be",
        "m.youtube.com",
        "www.youtube.com",
        "music.youtube.com",
        "youtube-nocookie.com"
    ],
    "tiktok": [
        "tiktok.com",
        "vm.tiktok.com",
        "vt.tiktok.com",
        "m.tiktok.com",
        "www.tiktok.com",
        "t.tiktok.com"
    ]
}

KNOWN_SHORTLINK_DOMAINS = {
    "bit.ly",
    "bitly.com",
    "tinyurl.com",
    "cutt.ly",
    "t.co",
    "is.gd",
    "v.gd",
    "rb.gy",
    "rebrand.ly",
    "shorturl.at",
    "ow.ly",
    "buff.ly",
    "tiny.cc",
    "s.id",
    "lnkd.in",
    "bl.ink",
    "soo.gd",
    "clck.ru"
}

NAVIGATION_CALLBACK_PREFIXES = (
    "umenu:dashboard",
    "umenu:profile",
    "umenu:submit_menu",
    "umenu:my_videos",
    "umenu:link_more",
    "umenu:withdraw",
    "umenu:wd_list",
    "umenu:history",
    "umenu:leaderboard",
    "umenu:referral",
    "umenu:redeem",
    "umenu:activity",
    "umenu:pwd_change",
    "umenu:color",
    "umenu:lang_toggle",
    "umenu:delete_acc",
    "umenu:cancel_home",
    "umenu:settings_hub",
    "umenu:bottom_toggle",
    "umyvid_plat:",
    "umyvid_acc:",
    "umyvid_cat:",
    "umyvid_item:",
    "u_refresh_vid:",
    "uman_code_prompt:",
    "upay_wd:",
    "upay_plat:",
    "upay_ledger:",
    "uwd_fast_dest:",
    "uwd_other_plat:",
    "uwd_other_go",
    "uprof_name_menu",
    "uprof_wd_num_menu",
    "uprof_edit:",
    "uprof_code_req:",
    "reg_toggle:",
    "reg_pay_toggle:",
    "reg_pay_confirm",
    "reg_man_code",
    "reg_step2_go",
    "cbtn_open:",
    "admin_hub",
    "adm_welcome",
    "adm_view_metrics",
    "adm_vsec:",
    "adm_vsec_item:",
    "adm_perm_sel:",
    "adm_perm_sel_all:",
    "adm_traffic:",
    "adm_traffic_item:",
    "adm_tr_item:",
    "adm_psel:",
    "adm_ulist:",
    "adm_usearch",
    "adm_uview:",
    "adm_uact_log:",
    "adm_ustat_menu:",
    "adm_uvplat:",
    "adm_vitem:",
    "adm_all_vids:",
    "adm_fin_history:",
    "adm_audit_history:",
    "adm_wd_reports_hub",
    "adm_uwd_hub:",
    "adm_wd_users:",
    "adm_wd_ulist_items:",
    "adm_wd_detail:",
    "adm_settings_hub",
    "adm_plat_settings_hub",
    "adm_gen_settings_hub",
    "adm_db_export_hub",
    "adm_adv_hub",
    "adm_gen_hub",
    "adm_export_hub",
    "adm_bottom_toggle",
    "adm_shub:",
    "adm_man_ver:",
    "adm_set_theme:",
    "adm_wd_limit_hub",
    "adm_edit_ref_hub",
    "adm_edit_rate_days",
    "adm_crit:hub",
    "adm_crit:view:",
    "adm_btn_editor_hub",
    "adm_ball_list:",
    "adm_bpage:",
    "adm_bpos_hub",
    "adm_bpos_page:",
    "adm_bdesign:",
    "adm_bmove_page:",
    "adm_bmp:",
    "adm_bdp:",
    "adm_elayout:",
    "adm_bitem:",
    "adm_cbl",
    "adm_cbn:",
    "adm_cbv:",
    "adm_cbp:",
    "adm_cbw:",
    "adm_cbprev:",
    "adm_msg_hub",
    "adm_msg_page:",
    "adm_trash:",
    "adm_trash_item:",
    "adm_guide_map",
    "adm_cmd_shortcuts",
    "adm_cmd_cat:",
    "uset_color:",
    "usub_plat:",
    "usub_acc:",
    "ulink_act:",
    "uwd_method:",
    "udel_step2",
    "adm_trash_move:",
    "adm_vrej_prompt:",
    "adm_vrej_cancel:",
    "adm_vrereview:",
    "adm_wd_paid_prompt:",
    "adm_rlayout:",
    "adm_bmove:",
    "adm_bde:",
    "adm_bdi:",
    "adm_bme:",
    "adm_bmove_page_pick:",
    "adm_bmove_page_exec:",
    "adm_cbw_",
    "adm_cbt:",
    "adm_bcol:",
    "adm_bren:",
    "adm_bemoji:",
    "adm_bstrip_em:",
    "adm_breset:",
    "adm_bvis:",
    "adm_emsg:",
    "adm_emsg_hist:",
    "adm_emsg_rb:",
    "adm_emsg_reset:",
    "adm_emsg_bmode:",
    "adm_emsg_badd:",
    "adm_emsg_bdel:",
    "adm_toggle:",
    "adm_apply_theme:",
    "adm_wd_lset:",
    "adm_crit:",
    "adm_rset:",
    "adm_mvr_gen",
    "adm_edit_",
    "adm_broadcast_prompt",
    "adm_export_data",
    "adm_toggle_bottom_menu",
    "adm_logout",
    "adm_uimp:",
    "adm_upwd:",
    "adm_uedit_info:",
    "adm_uref_hist:",
    "adm_uset_st:",
    "adm_trash_empty_confirm",
    "u_unfreeze_req",
    "reg_confirm_selection",
    "umenu:how_to_work",
    "umenu:menu_mode_toggle",
    "page:",
    "nav:"
)

SENSITIVE_CALLBACK_PREFIXES = (
    "vd:",
    "ext_act:",
    "ext_reset:",
    "adm_vdecision:",
    "adm_vrej_exec:",
    "adm_perm_approve:",
    "adm_perm_trash_all_exec",
    "adm_perm_trash_sel_exec:",
    "adm_wd_act:",
    "adm_ubal:",
    "adm_udel_u:",
    "adm_udel_force:",
    "adm_trash_del:",
    "adm_trash_restore:",
    "adm_man_ver_act:",
    "adm_mvr_act:",
    "adm_cbconf:",
    "adm_cbw_confirm",
    "adm_cbd:",
    "adm_trash_empty_exec",
    "adm_toggle:",
    "adm_mvr_gen",
    "adm_uset_st:",
    "umenu:menu_mode_toggle",
    "adm_toggle_bottom_menu",
    "umenu:lang_toggle",
    "u_recheck_vcode:",
    "uconfirm_del_acc"
)


def _enforce_cache_bounds(
    cache_dict: dict,
    now_ts: float = None,
    expiry_Window_sec: float = 900.0,
    max_entries: int = MAX_MEMORY_CACHE_ENTRIES,
    value_type: str = "timestamp"
) -> None:
    """
    Purges expired items and bounds dictionary size to `max_entries` (evicting oldest entries first).
    `value_type`:
      - 'timestamp': value is an expiry timestamp (`exp_ts <= now_ts` means expired)
      - 'seen_ts': value is a creation timestamp (`now_ts - seen_ts >= expiry_Window_sec` means expired)
      - 'ts_list': value is a list of creation timestamps
    """
    now = float(now_ts if now_ts is not None else time.time())
    max_cap = max(10, int(max_entries or MAX_MEMORY_CACHE_ENTRIES))

    if value_type == "timestamp":
        for k, exp_ts in list(cache_dict.items()):
            try:
                if float(exp_ts) <= now:
                    cache_dict.pop(k, None)
            except Exception:
                cache_dict.pop(k, None)
        if len(cache_dict) > max_cap:
            sorted_keys = sorted(cache_dict.keys(), key=lambda k: float(cache_dict.get(k, 0.0)))
            for k in sorted_keys[: len(cache_dict) - max_cap]:
                cache_dict.pop(k, None)

    elif value_type == "seen_ts":
        cutoff = now - max(1.0, float(expiry_Window_sec))
        for k, seen_ts in list(cache_dict.items()):
            try:
                if float(seen_ts) < cutoff:
                    cache_dict.pop(k, None)
            except Exception:
                cache_dict.pop(k, None)
        if len(cache_dict) > max_cap:
            sorted_keys = sorted(cache_dict.keys(), key=lambda k: float(cache_dict.get(k, 0.0)))
            for k in sorted_keys[: len(cache_dict) - max_cap]:
                cache_dict.pop(k, None)

    elif value_type == "ts_list":
        cutoff = now - max(1.0, float(expiry_Window_sec))
        for k, ts_list in list(cache_dict.items()):
            if not isinstance(ts_list, list):
                cache_dict.pop(k, None)
                continue
            filtered = [t for t in ts_list if isinstance(t, (int, float)) and t > cutoff]
            if filtered:
                cache_dict[k] = filtered
            else:
                cache_dict.pop(k, None)
        if len(cache_dict) > max_cap:
            sorted_keys = sorted(
                cache_dict.keys(),
                key=lambda k: (cache_dict[k][-1] if cache_dict.get(k) else 0.0)
            )
            for k in sorted_keys[: len(cache_dict) - max_cap]:
                cache_dict.pop(k, None)


def cleanup_security_caches(now_ts: float = None, max_entries: int = MAX_MEMORY_CACHE_ENTRIES) -> dict:
    """Explicitly cleans up all in-memory security caches and enforces maximum memory bounds."""
    now = float(now_ts if now_ts is not None else time.time())
    with _rate_limit_lock:
        _enforce_cache_bounds(_rate_limit_buckets, now, expiry_Window_sec=60.0, max_entries=max_entries, value_type="ts_list")
        _enforce_cache_bounds(_failed_login_counts, now, expiry_Window_sec=900.0, max_entries=max_entries, value_type="ts_list")
        _enforce_cache_bounds(_flow_locks, now, max_entries=max_entries, value_type="timestamp")
        _enforce_cache_bounds(_recent_callbacks, now, expiry_Window_sec=30.0, max_entries=max_entries, value_type="seen_ts")
        _enforce_cache_bounds(_admin_unlocked_sessions, now, max_entries=max_entries, value_type="timestamp")
        return {
            "rate_limit_buckets": len(_rate_limit_buckets),
            "failed_login_counts": len(_failed_login_counts),
            "flow_locks": len(_flow_locks),
            "recent_callbacks": len(_recent_callbacks),
            "admin_unlocked_sessions": len(_admin_unlocked_sessions)
        }


def translate_bengali_digits(text: str) -> str:
    """Translates Bengali digits (০-৯) to standard ASCII digits (0-9)."""
    return str(text or "").translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))


def hash_password(password: str, iterations: int = 200000) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a 16-byte random cryptographic salt."""
    pwd_str = str(password or "").strip()
    if not pwd_str:
        return ""
    safe_iters = max(100000, int(iterations or 200000))
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        pwd_str.encode("utf-8"),
        salt.encode("ascii"),
        safe_iters
    )
    return f"pbkdf2_sha256${safe_iters}${salt}${dk.hex()}"


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Verifies a candidate password against a stored PBKDF2-HMAC-SHA256 hash in constant time."""
    if not stored_hash or candidate_password is None:
        return False
    cand_str = str(candidate_password).strip()
    if not cand_str:
        return False
    stored_str = str(stored_hash).strip()
    try:
        if stored_str.startswith("pbkdf2_sha256$"):
            parts = stored_str.split("$")
            if len(parts) != 4:
                return False
            iterations = int(parts[1])
            salt = parts[2]
            expected_hex = parts[3]
            dk = hashlib.pbkdf2_hmac(
                "sha256",
                cand_str.encode("utf-8"),
                salt.encode("ascii"),
                iterations
            )
            return hmac.compare_digest(dk.hex(), expected_hex)
        elif "$" in stored_str:
            salt, expected_hex = stored_str.split("$", 1)
            dk = hashlib.pbkdf2_hmac(
                "sha256",
                cand_str.encode("utf-8"),
                salt.encode("ascii"),
                100000
            )
            return hmac.compare_digest(dk.hex(), expected_hex)
        elif re.fullmatch(r"[0-9a-fA-F]{64}", stored_str):
            legacy_hex = hashlib.sha256(cand_str.encode("utf-8")).hexdigest()
            return hmac.compare_digest(stored_str.lower(), legacy_hex.lower())
        else:
            return False
    except Exception:
        return False


def verify_admin_secret(candidate_secret: str, expected_secret: str) -> bool:
    """Constant-time comparison for Admin Password / Secret verification."""
    cand = str(candidate_secret or "").strip()
    exp = str(expected_secret or "").strip()
    if not cand or not exp:
        return False
    if exp.startswith("pbkdf2_sha256$"):
        return verify_password(exp, cand)
    return hmac.compare_digest(cand.encode("utf-8"), exp.encode("utf-8"))


def is_authorized_numeric_admin_id(user_id: str, super_admin_id: str = "8145274317", admins_csv: str = "8145274317") -> bool:
    """Strictly validates admin identity by immutable numeric Telegram user ID only (never by username)."""
    uid = str(user_id or "").strip()
    if not uid or not uid.isdigit():
        return False
    sa_clean = str(super_admin_id or "").strip()
    if sa_clean and sa_clean.isdigit() and uid == sa_clean:
        return True
    adm_ids = {x.strip() for x in str(admins_csv or "").split(",") if x.strip().isdigit()}
    return uid in adm_ids


def unlock_admin_session(user_id: str, ttl_sec: int = 3600) -> float:
    """Unlocks admin session for an authorized admin user ID for `ttl_sec` seconds."""
    uid = str(user_id or "").strip()
    if not uid or not uid.isdigit():
        return 0.0
    now = time.time()
    exp = now + max(60, int(ttl_sec or 3600))
    with _rate_limit_lock:
        _admin_unlocked_sessions[uid] = exp
        _enforce_cache_bounds(_admin_unlocked_sessions, now, value_type="timestamp")
    return exp


def is_admin_session_unlocked(user_id: str) -> bool:
    """Checks if an admin user ID currently has an active unlocked admin session."""
    uid = str(user_id or "").strip()
    now = time.time()
    with _rate_limit_lock:
        exp = _admin_unlocked_sessions.get(uid, 0.0)
        if exp > now:
            return True
        if uid in _admin_unlocked_sessions:
            _admin_unlocked_sessions.pop(uid, None)
        return False


def touch_admin_session(user_id: str, ttl_sec: int = 3600) -> None:
    """Refreshes an already-unlocked admin session's expiry timestamp."""
    uid = str(user_id or "").strip()
    now = time.time()
    with _rate_limit_lock:
        if _admin_unlocked_sessions.get(uid, 0.0) > now:
            _admin_unlocked_sessions[uid] = now + max(60, int(ttl_sec or 3600))


def lock_admin_session(user_id: str) -> None:
    """Locks/clears an admin session."""
    uid = str(user_id or "").strip()
    with _rate_limit_lock:
        _admin_unlocked_sessions.pop(uid, None)


def record_failed_login(user_id: str, window_sec: int = 900, max_entries: int = MAX_MEMORY_CACHE_ENTRIES) -> int:
    """Records a failed password attempt and returns the consecutive failure count within `window_sec`."""
    uid = str(user_id or "").strip()
    now = time.time()
    win = max(60, int(window_sec or 900))
    with _rate_limit_lock:
        timestamps = _failed_login_counts.get(uid, [])
        cutoff = now - win
        timestamps = [t for t in timestamps if t > cutoff]
        timestamps.append(now)
        _failed_login_counts[uid] = timestamps
        _enforce_cache_bounds(_failed_login_counts, now, expiry_Window_sec=win, max_entries=max_entries, value_type="ts_list")
        return len(_failed_login_counts.get(uid, timestamps))


def get_failed_login_count(user_id: str, window_sec: int = 900) -> int:
    """Returns current failed password attempt count for `user_id`."""
    uid = str(user_id or "").strip()
    now = time.time()
    win = max(60, int(window_sec or 900))
    with _rate_limit_lock:
        timestamps = _failed_login_counts.get(uid, [])
        cutoff = now - win
        timestamps = [t for t in timestamps if t > cutoff]
        if timestamps:
            _failed_login_counts[uid] = timestamps
        else:
            _failed_login_counts.pop(uid, None)
        return len(timestamps)


def reset_failed_login(user_id: str) -> None:
    """Clears failed login counter after successful authentication."""
    uid = str(user_id or "").strip()
    with _rate_limit_lock:
        _failed_login_counts.pop(uid, None)


def mask_sensitive_secret(secret: str) -> str:
    """Masks sensitive strings so plaintext passwords are never exposed in logs or UI."""
    val = str(secret or "").strip()
    if not val or val.startswith("pbkdf2_sha256$"):
        return "•••••••• (PBKDF2-SHA256 Protected)"
    if len(val) <= 2:
        return "••••"
    return f"{val[0]}{'•' * min(6, len(val) - 2)}{val[-1]}"


def generate_random_code(prefix: str = "BC", length: int = 6) -> str:
    """Generates an unpredictable uppercase alphanumeric verification code."""
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    token = "".join(secrets.choice(alphabet) for _ in range(max(4, int(length))))
    clean_prefix = re.sub(r"[^A-Z0-9]", "", str(prefix or "BC").upper())
    return f"{clean_prefix}-{token}" if clean_prefix else token


def generate_custom_button_uid(prefix: str = "cbtn", existing_keys: set = None) -> str:
    """
    Generates a collision-free UUIDv4 + CSPRNG custom button ID (`cbtn_<12_hex>`)
    that fits comfortably inside Telegram's 64-byte callback_data limit and never overwrites existing IDs.
    """
    clean_p = re.sub(r"[^a-zA-Z0-9_]", "", str(prefix or "cbtn").lower()).rstrip("_") or "cbtn"
    known = set(existing_keys or ())
    for _ in range(100):
        u_hex = uuid.uuid4().hex[:8] + secrets.token_hex(2)
        cand = f"{clean_p}_{u_hex}"
        if cand not in known:
            return cand
    return f"{clean_p}_{uuid.uuid4().hex[:12]}"


def generate_manual_verification_code(length: int = 6) -> str:
    """Generates a single-use Admin-issued Manual Verification / Profile Edit code (`BC-XXXXXX`)."""
    return generate_random_code(prefix="BC", length=length)


def generate_referral_code(user_id: str = "") -> str:
    """Generates a hard-to-guess unique referral code."""
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    rand_part = "".join(secrets.choice(alphabet) for _ in range(7))
    suffix = str(user_id)[-3:] if str(user_id).isdigit() else "".join(secrets.choice(alphabet) for _ in range(2))
    return f"REF-{rand_part}{suffix}"


def generate_idempotency_token(prefix: str = "TX") -> str:
    """Generates a collision-free reference / idempotency token for financial operations."""
    clean_p = re.sub(r"[^A-Z0-9_]", "", str(prefix or "TX").upper())
    return f"{clean_p}_{int(time.time() * 1000)}_{secrets.token_hex(6).upper()}"


def normalize_domain_host(raw_url_or_host: str) -> str:
    """
    Properly normalizes a domain or URL into its lowercase hostname without `www.` prefix.
    Fixes the classic `.lstrip("www.")` bug (which corrupted domains starting with 'w' like `www.wrestling.com` -> `restling.com`).
    Returns empty string if not a valid registrable domain/host.
    """
    raw = str(raw_url_or_host or "").strip()
    if not raw or any(ch in raw for ch in (" ", "\t", "\r", "\n", "<", ">", '"', "'")):
        return ""
    if "://" in raw:
        try:
            parsed = urllib.parse.urlparse(raw)
            host = (parsed.hostname or "").strip().lower()
        except Exception:
            return ""
    else:
        slash_idx = raw.find("/")
        q_idx = raw.find("?")
        cut_idx = min([i for i in (slash_idx, q_idx) if i != -1], default=-1)
        host_part = raw[:cut_idx] if cut_idx != -1 else raw
        if "@" in host_part:
            return ""
        if ":" in host_part:
            host_part = host_part.split(":", 1)[0]
        host = host_part.strip().lower()

    host = host.rstrip(".")
    if host.startswith("www."):
        host = host[4:]

    if not host or "." not in host:
        return ""
    try:
        ipaddress.ip_address(host)
        return ""
    except ValueError:
        pass

    labels = host.split(".")
    if len(labels) < 2:
        return ""
    tld = labels[-1]
    if not (re.fullmatch(r"[a-z]{2,24}", tld) or re.fullmatch(r"xn--[a-z0-9]{2,30}", tld)):
        return ""
    for lbl in labels:
        if not lbl or len(lbl) > 63:
            return ""
        if lbl.startswith("-") or lbl.endswith("-"):
            return ""
        if not re.fullmatch(r"[a-z0-9-]+", lbl):
            return ""
    return host


def normalize_bd_payment_number(raw_phone: str, allow_rocket_12: bool = True) -> str:
    """
    Normalizes Bangladeshi mobile payment numbers (bKash/Nagad/Rocket) into 11-digit `01XXXXXXXXX`
    (or 12-digit `01XXXXXXXXXX` for Rocket when `allow_rocket_12=True`).
    Returns empty string if invalid.
    """
    txt = translate_bengali_digits(raw_phone)
    cleaned = re.sub(r"[\s().-]", "", txt)
    if cleaned.startswith("+880"):
        cleaned = "0" + cleaned[4:]
    elif cleaned.startswith("880") and len(cleaned) in (13, 14):
        cleaned = "0" + cleaned[3:]
    if re.fullmatch(r"01[3-9][0-9]{8}", cleaned):
        return cleaned
    if allow_rocket_12 and re.fullmatch(r"01[3-9][0-9]{9}", cleaned):
        return cleaned
    return ""


def format_display_app_uid(raw_uid: str) -> str:
    """
    Formats Battle Club App UID for user/admin display strictly as `#` + number (`#107`, `#1007`, `#20010`),
    stripping any `#BC`, `BC-`, or `BC_` prefix while keeping internal canonical locks intact.
    """
    txt = translate_bengali_digits(raw_uid)
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", str(txt or "").strip()).upper()
    if not cleaned:
        return ""
    cleaned = re.sub(r"^(?:BC[-_]?)+(?=[0-9A-Z])", "", cleaned)
    if not cleaned:
        return ""
    return f"#{cleaned}"


def normalize_permanent_app_uid(raw_uid: str, enforce_bc_prefix: bool = False) -> str:
    """
    Normalizes Battle Club App UID with leading `#` (e.g., `#107` or `#1007`).
    If `enforce_bc_prefix=False` (default), strips `BC` so visible UID is strictly `#` + number (`#1007`).
    """
    txt = translate_bengali_digits(raw_uid)
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", str(txt or "").strip()).upper()
    if not cleaned:
        return ""
    if enforce_bc_prefix:
        cleaned_num = re.sub(r"^BC[-_]?", "", cleaned)
        return f"#BC{cleaned_num}"
    cleaned = re.sub(r"^(?:BC[-_]?)+(?=[0-9A-Z])", "", cleaned)
    return f"#{cleaned}"


def canonicalize_app_uid(raw_uid: str) -> str:
    """
    Returns a canonical lock key for Battle Club App UID so `#BC12345`, `BC12345`, `12345`, and `#12345`
    map to the exact same identity lock key (`#BC12345`) without breaking existing DB locks.
    """
    txt = translate_bengali_digits(raw_uid)
    body = re.sub(r"[^a-zA-Z0-9_-]", "", str(txt or "").strip()).upper()
    if not body:
        return ""
    body_stripped = re.sub(r"^BC[-_]?(?=[0-9])", "", body)
    if body_stripped.isdigit():
        return f"#BC{body_stripped}"
    return f"#{body}"


def canonicalize_profile_identity(platform: str, profile_handle: str, profile_url: str = "") -> str:
    """
    Creates a permanent canonical_profile_id (`<platform>:<normalized_handle>`)
    for locking a social profile to a single Telegram user account.
    """
    p = str(platform or "").strip().lower()
    h = str(profile_handle or "").strip().lower().lstrip("@").rstrip("/")
    if not h and profile_url:
        try:
            parsed = urllib.parse.urlparse(str(profile_url).strip().lower())
            keep_params = []
            for k, v in urllib.parse.parse_qsl(parsed.query):
                if k in ("id", "user", "uid", "channel_id"):
                    keep_params.append((k, v))
            base = f"{parsed.netloc}{parsed.path}".rstrip("/")
            h = f"{base}?{urllib.parse.urlencode(keep_params)}" if keep_params else base
        except Exception:
            h = str(profile_url).strip().lower().rstrip("/")
    if not p or not h:
        return ""
    return f"{p}:{h}"


def is_navigation_callback(callback_data: str) -> bool:
    """
    Returns True for all navigation, menu, toggle, editor, and pagination callbacks
    so rapid button clicks are never blocked. Only sensitive financial/approval/delete
    callbacks in SENSITIVE_CALLBACK_PREFIXES return False.
    """
    cb = str(callback_data or "").strip()
    if not cb:
        return False
    if any(cb.startswith(pref) for pref in SENSITIVE_CALLBACK_PREFIXES):
        return False
    return True


def check_rate_limit(
    user_id: str,
    action: str = "general",
    max_calls: int = 12,
    window_sec: int = 10,
    is_navigation: bool = False,
    max_cache_entries: int = MAX_MEMORY_CACHE_ENTRIES
) -> tuple:
    """
    Thread-safe sliding-window rate limiter with expiry cleanup & maximum memory bound.
    Returns (allowed: bool, retry_after_sec: float)
    """
    now = time.time()
    nav_flag = is_navigation or str(action).startswith("nav:") or is_navigation_callback(action)
    eff_action = "nav_fast" if nav_flag else str(action).strip()
    max_c = max(60, int(max_calls or 12)) if nav_flag else max(1, int(max_calls or 12))
    win_s = 5 if nav_flag else max(1, int(window_sec or 10))

    key = f"{str(user_id).strip()}:{eff_action}"
    with _rate_limit_lock:
        timestamps = _rate_limit_buckets.get(key, [])
        cutoff = now - win_s
        timestamps = [t for t in timestamps if t > cutoff]
        if len(timestamps) >= max_c:
            retry_after = max(1.0, round(win_s - (now - timestamps[0]), 1))
            _rate_limit_buckets[key] = timestamps
            _enforce_cache_bounds(_rate_limit_buckets, now, expiry_Window_sec=max(win_s, 60.0), max_entries=max_cache_entries, value_type="ts_list")
            return False, retry_after
        timestamps.append(now)
        _rate_limit_buckets[key] = timestamps
        if len(_rate_limit_buckets) > max_cache_entries:
            _enforce_cache_bounds(_rate_limit_buckets, now, expiry_Window_sec=max(win_s, 60.0), max_entries=max_cache_entries, value_type="ts_list")
        return True, 0.0


def reset_rate_limit(user_id: str, action: str = None) -> None:
    """Resets rate limit bucket for a specific user (and optional action)."""
    uid_prefix = f"{str(user_id).strip()}:"
    with _rate_limit_lock:
        if action:
            _rate_limit_buckets.pop(f"{str(user_id).strip()}:{str(action).strip()}", None)
            _rate_limit_buckets.pop(f"{str(user_id).strip()}:nav_fast", None)
        else:
            for k in list(_rate_limit_buckets.keys()):
                if k.startswith(uid_prefix):
                    _rate_limit_buckets.pop(k, None)


def check_duplicate_callback(user_id: str, callback_data: str, ttl_sec: float = 1.5) -> bool:
    """
    Prevents accidental double-taps on sensitive financial/approval buttons within `ttl_sec`.
    Never blocks navigation callbacks.
    Returns True if duplicate (should be ignored), False otherwise.
    """
    cb = str(callback_data or "").strip()
    if not cb or is_navigation_callback(cb):
        return False
    now = time.time()
    key = f"{str(user_id).strip()}:{cb}"
    with _rate_limit_lock:
        prev_ts = _recent_callbacks.get(key, 0.0)
        if (now - prev_ts) < float(ttl_sec):
            return True
        _recent_callbacks[key] = now
        if len(_recent_callbacks) > MAX_MEMORY_CACHE_ENTRIES:
            _enforce_cache_bounds(_recent_callbacks, now, expiry_Window_sec=30.0, max_entries=MAX_MEMORY_CACHE_ENTRIES, value_type="seen_ts")
        return False


def acquire_flow_lock(user_id: str, flow_key: str = "sensitive", ttl_sec: float = 15.0) -> bool:
    """Acquires a per-user short-lived lock for sensitive mutations (withdrawals, approvals, reversals)."""
    now = time.time()
    key = f"{str(user_id).strip()}:{str(flow_key).strip()}"
    with _rate_limit_lock:
        exp = _flow_locks.get(key, 0.0)
        if exp > now:
            return False
        _flow_locks[key] = now + max(1.0, float(ttl_sec))
        if len(_flow_locks) > MAX_MEMORY_CACHE_ENTRIES:
            _enforce_cache_bounds(_flow_locks, now, max_entries=MAX_MEMORY_CACHE_ENTRIES, value_type="timestamp")
        return True


def release_flow_lock(user_id: str, flow_key: str = "sensitive") -> None:
    """Releases a per-user sensitive flow lock."""
    key = f"{str(user_id).strip()}:{str(flow_key).strip()}"
    with _rate_limit_lock:
        _flow_locks.pop(key, None)


def _is_disallowed_ip(ip_str: str) -> bool:
    """Returns True if an IPv4/IPv6 address is private, loopback, link-local, reserved, carrier-grade NAT, or unspecified."""
    try:
        ip_obj = ipaddress.ip_address(str(ip_str).strip())
        if getattr(ip_obj, "ipv4_mapped", None):
            ip_obj = ip_obj.ipv4_mapped
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            return True
        if isinstance(ip_obj, ipaddress.IPv4Address):
            if ip_obj in ipaddress.IPv4Network("100.64.0.0/10"):
                return True
        return False
    except ValueError:
        return True


def resolve_and_validate_public_ips(hostname: str) -> tuple:
    """
    Resolves DNS for `hostname` and validates that all resolved IPs are public.
    FAIL-CLOSED: If DNS resolution fails (`socket.gaierror`), times out, or returns no IPs,
    returns `(False, [], reason)`.
    """
    host = str(hostname or "").strip().lower().rstrip(".")
    if not host:
        return False, [], "লিঙ্কে কোনো বৈধ ডোমেইন পাওয়া যায়নি।"

    try:
        ip_obj = ipaddress.ip_address(host)
        if _is_disallowed_ip(str(ip_obj)):
            return False, [], "প্রাইভেট বা রিজার্ভড IP অ্যাড্রেস অনুমোদিত নয়!"
        return True, [str(ip_obj)], "OK"
    except ValueError:
        pass

    try:
        addr_info = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False, [], f"DNS রেজোলিউশন ব্যর্থ হয়েছে ({host}) — Fail-Closed Security Policy!"
    except Exception as exc:
        return False, [], f"DNS যাচাই ব্যর্থ হয়েছে ({str(exc)[:60]}) — Fail-Closed Security Policy!"

    if not addr_info:
        return False, [], f"DNS রেজোলিউশনে কোনো বৈধ IP পাওয়া যায়নি ({host})!"

    validated_ips = []
    for item in addr_info:
        sockaddr = item[4]
        if not sockaddr:
            continue
        resolved_ip = str(sockaddr[0]).strip()
        if _is_disallowed_ip(resolved_ip):
            return False, [], f"DNS রেজোলিউশনে প্রাইভেট বা অভ্যন্তরীণ IP ({resolved_ip}) পাওয়া গেছে (SSRF Blocked)!"
        if resolved_ip not in validated_ips:
            validated_ips.append(resolved_ip)

    if not validated_ips:
        return False, [], f"DNS রেজোলিউশনে কোনো পাবলিক IP পাওয়া যায়নি ({host})!"

    return True, validated_ips, "OK"


def is_safe_public_url_with_ips(url: str, allowed_domains: list = None, resolve_dns: bool = True) -> dict:
    """
    SSRF Protection, Domain Allowlist & Fail-Closed DNS Validator:
    Returns dict: `{"ok": bool, "reason": str, "hostname": str, "ips": list[str], "normalized_url": str}`
    """
    raw = str(url or "").strip()
    if not raw:
        return {"ok": False, "reason": "খালি লিংক গ্রহণযোগ্য নয়।", "hostname": "", "ips": [], "normalized_url": ""}
    if len(raw) > 2048 or any(ch in raw for ch in ("\r", "\n", chr(0))):
        return {"ok": False, "reason": "অবৈধ বা অতিরিক্ত বড় URL।", "hostname": "", "ips": [], "normalized_url": ""}

    if raw.startswith("@"):
        raw = f"https://www.youtube.com/{raw}"
    elif not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        raw = "https://" + raw.lstrip("/")

    try:
        parsed = urllib.parse.urlparse(raw)
    except Exception:
        return {"ok": False, "reason": "অবৈধ URL ফরম্যাট।", "hostname": "", "ips": [], "normalized_url": ""}

    if parsed.scheme.lower() not in ("http", "https"):
        return {"ok": False, "reason": "শুধুমাত্র HTTP/HTTPS লিংক সমর্থিত।", "hostname": "", "ips": [], "normalized_url": ""}

    if parsed.username or parsed.password:
        return {"ok": False, "reason": "URL-এর ভেতরে ইউজারনেম/পাসওয়ার্ড অনুমোদিত নয়।", "hostname": "", "ips": [], "normalized_url": ""}

    hostname = (parsed.hostname or "").strip().lower().rstrip(".")
    if not hostname:
        return {"ok": False, "reason": "লিঙ্কে কোনো বৈধ ডোমেইন পাওয়া যায়নি।", "hostname": "", "ips": [], "normalized_url": ""}

    blocked_hosts = {
        "localhost",
        "localhost.localdomain",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "169.254.169.254",
        "metadata.google.internal",
        "metadata",
        "100.100.100.200"
    }
    if (
        hostname in blocked_hosts
        or hostname.endswith(".local")
        or hostname.endswith(".internal")
        or hostname.endswith(".localhost")
        or hostname.endswith(".lan")
    ):
        return {"ok": False, "reason": "স্থানীয় বা অভ্যন্তরীণ নেটওয়ার্ক লিংক (SSRF) সম্পূর্ণ নিষিদ্ধ!", "hostname": hostname, "ips": [], "normalized_url": raw}

    if re.fullmatch(r"[0-9]+", hostname) or re.fullmatch(r"0x[0-9a-f]+", hostname):
        return {"ok": False, "reason": "সংখ্যাভিত্তিক বা অস্পষ্ট IP হোস্টনেম অনুমোদিত নয়!", "hostname": hostname, "ips": [], "normalized_url": raw}

    try:
        ipaddress.ip_address(hostname)
        if _is_disallowed_ip(hostname):
            return {"ok": False, "reason": "প্রাইভেট বা রিজার্ভড IP অ্যাড্রেস অনুমোদিত নয়!", "hostname": hostname, "ips": [], "normalized_url": raw}
        if allowed_domains:
            return {"ok": False, "reason": "সরাসরি IP অ্যাড্রেস গ্রহণযোগ্য নয়; অনুমোদিত প্ল্যাটফর্ম ডোমেইন ব্যবহার করুন।", "hostname": hostname, "ips": [], "normalized_url": raw}
    except ValueError:
        pass

    if allowed_domains:
        domain_ok = False
        for d in allowed_domains:
            d_clean = str(d or "").lower().strip().lstrip(".")
            if not d_clean:
                continue
            if hostname == d_clean or hostname.endswith("." + d_clean):
                domain_ok = True
                break
        if not domain_ok:
            return {"ok": False, "reason": f"অনুমোদিত প্ল্যাটফর্ম ডোমেইন নয় ({hostname})।", "hostname": hostname, "ips": [], "normalized_url": raw}

    validated_ips = []
    if resolve_dns:
        dns_ok, ips, dns_reason = resolve_and_validate_public_ips(hostname)
        if not dns_ok:
            return {"ok": False, "reason": dns_reason, "hostname": hostname, "ips": [], "normalized_url": raw}
        validated_ips = ips

    return {"ok": True, "reason": "OK", "hostname": hostname, "ips": validated_ips, "normalized_url": raw}


def is_safe_public_url(url: str, allowed_domains: list = None, resolve_dns: bool = True) -> tuple:
    """
    SSRF Protection & URL Allowlist Validator (Fail-Closed on DNS resolution failure when `resolve_dns=True`).
    Returns (is_safe: bool, reason: str)
    """
    res = is_safe_public_url_with_ips(url, allowed_domains=allowed_domains, resolve_dns=resolve_dns)
    return res["ok"], res["reason"]


def validate_platform_url(platform: str, url: str, extra_domains: list = None, resolve_dns: bool = False) -> tuple:
    """
    Validates that a URL is safe from SSRF and belongs to the specified platform's official domains (YouTube or TikTok only).
    Note: `resolve_dns` defaults to False for fast offline syntax/domain checks, while live network requests always enforce `resolve_dns=True` with IP pinning.
    Returns (is_valid: bool, reason: str)
    """
    p_key = str(platform or "").strip().lower()
    domains = list(PLATFORM_ALLOWED_DOMAINS.get(p_key, []))
    if extra_domains:
        for ed in extra_domains:
            if ed not in domains:
                domains.append(ed)
    if not domains:
        return False, f"অসমর্থিত প্ল্যাটফর্ম ({p_key}) — শুধুমাত্র YouTube এবং TikTok সমর্থিত।"
    return is_safe_public_url(url, allowed_domains=domains, resolve_dns=resolve_dns)


class _PinnedIPHTTPConnection(http.client.HTTPConnection):
    """HTTPConnection that connects directly to a pre-validated IP address to prevent DNS Rebinding."""
    def __init__(self, host, pinned_ip=None, **kwargs):
        super().__init__(host, **kwargs)
        self._pinned_ip = pinned_ip

    def connect(self):
        target_host = self._pinned_ip or self.host
        self.sock = socket.create_connection((target_host, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self._tunnel()


class _PinnedIPHTTPSConnection(http.client.HTTPSConnection):
    """HTTPSConnection that connects directly to a pre-validated IP while verifying TLS Certificate & SNI against `self.host`."""
    def __init__(self, host, pinned_ip=None, context=None, **kwargs):
        if context is None:
            context = ssl.create_default_context()
        super().__init__(host, context=context, **kwargs)
        self._pinned_ip = pinned_ip

    def connect(self):
        target_host = self._pinned_ip or self.host
        sock = socket.create_connection((target_host, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
            server_hostname = self._tunnel_host
        else:
            server_hostname = self.host
        self.sock = self._context.wrap_socket(sock, server_hostname=server_hostname)


class _PinnedIPHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, ip_map: dict):
        super().__init__()
        self._ip_map = ip_map or {}

    def http_open(self, req):
        host = ( urllib.parse.urlparse(req.full_url).hostname or "" ).lower().rstrip(".")
        pinned_ip = self._ip_map.get(host)
        return self.do_open(lambda h, **kw: _PinnedIPHTTPConnection(h, pinned_ip=pinned_ip, **kw), req)


class _PinnedIPHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, ip_map: dict, context=None):
        super().__init__(context=context)
        self._ip_map = ip_map or {}
        self._ssl_ctx = context or ssl.create_default_context()

    def https_open(self, req):
        host = ( urllib.parse.urlparse(req.full_url).hostname or "" ).lower().rstrip(".")
        pinned_ip = self._ip_map.get(host)
        return self.do_open(
            lambda h, **kw: _PinnedIPHTTPSConnection(h, pinned_ip=pinned_ip, context=self._ssl_ctx, **kw),
            req,
            context=self._ssl_ctx
        )


class _NoAutoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Disables automatic urllib redirect following so every hop can be manually validated for SSRF, loops & DNS rebinding."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def safe_urlopen_with_redirects(
    url: str,
    headers: dict = None,
    timeout: int = 6,
    max_redirects: int = 6,
    max_read_bytes: int = 2_500_000,
    allowed_domains: list = None,
    stop_on_login_wall: bool = True,
    max_bytes: int = None
) -> dict:
    """
    Executes an HTTP/HTTPS GET request with:
    1. Fail-closed DNS validation before every hop
    2. Socket-level IP pinning to prevent DNS Rebinding between check and connect
    3. TLS certificate verification enabled (`ssl.create_default_context()`)
    4. Hop-by-hop redirect validation, redirect loop detection, and maximum redirect limit (`max_redirects`)
    """
    if max_bytes is not None:
        max_read_bytes = max(0, int(max_bytes))
    current_url = str(url or "").strip()
    if current_url and not re.match(r"^https?://", current_url, re.IGNORECASE):
        current_url = "https://" + current_url.lstrip("/")

    visited_urls = set()
    redirect_chain = []
    ip_map = {}
    req_headers = dict(headers or {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"})
    last_valid_url = current_url

    for hop in range(max(0, int(max_redirects)) + 1):
        if current_url in visited_urls:
            return {
                "ok": False,
                "original_url": str(url),
                "final_url": last_valid_url,
                "final_domain": normalize_domain_host(last_valid_url),
                "redirect_chain": redirect_chain,
                "body": b"",
                "status_code": 0,
                "error_category": "redirect_loop",
                "reason": "Redirect Loop শনাক্ত হয়েছে!",
                "error": "Redirect Loop শনাক্ত হয়েছে!"
            }
        visited_urls.add(current_url)

        val_res = is_safe_public_url_with_ips(current_url, allowed_domains=allowed_domains, resolve_dns=True)
        if not val_res["ok"]:
            err_cat = "dns_failure" if "DNS" in val_res["reason"] else "ssrf_blocked"
            return {
                "ok": False,
                "original_url": str(url),
                "final_url": last_valid_url,
                "final_domain": normalize_domain_host(last_valid_url),
                "redirect_chain": redirect_chain,
                "body": b"",
                "status_code": 0,
                "error_category": err_cat,
                "reason": val_res["reason"],
                "error": val_res["reason"]
            }

        current_url = val_res["normalized_url"]
        last_valid_url = current_url
        redirect_chain.append(current_url)
        if val_res["hostname"] and val_res["ips"]:
            ip_map[val_res["hostname"]] = val_res["ips"][0]

        opener = urllib.request.build_opener(
            _PinnedIPHTTPHandler(ip_map),
            _PinnedIPHTTPSHandler(ip_map),
            _NoAutoRedirectHandler()
        )
        req = urllib.request.Request(current_url, headers=req_headers)
        try:
            with opener.open(req, timeout=timeout) as resp:
                status_code = getattr(resp, "status", None) or resp.getcode() or 200
                body = resp.read(max_read_bytes) if max_read_bytes > 0 else b""
                return {
                    "ok": True,
                    "original_url": str(url),
                    "final_url": current_url,
                    "final_domain": normalize_domain_host(current_url),
                    "redirect_chain": redirect_chain,
                    "body": body,
                    "status_code": int(status_code),
                    "error_category": "none",
                    "reason": "OK",
                "error": "OK"
                }
        except urllib.error.HTTPError as he:
            code = int(getattr(he, "code", 0) or 0)
            if code in (301, 302, 303, 307, 308):
                if hop >= int(max_redirects):
                    return {
                        "ok": False,
                        "original_url": str(url),
                        "final_url": last_valid_url,
                        "final_domain": normalize_domain_host(last_valid_url),
                        "redirect_chain": redirect_chain,
                        "body": b"",
                        "status_code": code,
                        "error_category": "max_redirects_exceeded",
                        "reason": f"সর্বোচ্চ Redirect সীমা ({max_redirects}) অতিক্রম করেছে!",
                "error": f"সর্বোচ্চ Redirect সীমা ({max_redirects}) অতিক্রম করেছে!"
                    }
                loc = ""
                if he.headers:
                    loc = he.headers.get("Location") or he.headers.get("location") or ""
                loc = str(loc).strip()
                if not loc:
                    return {
                        "ok": False,
                        "original_url": str(url),
                        "final_url": last_valid_url,
                        "final_domain": normalize_domain_host(last_valid_url),
                        "redirect_chain": redirect_chain,
                        "body": b"",
                        "status_code": code,
                        "error_category": "invalid_redirect",
                        "reason": "Redirect Location পাওয়া যায়নি।",
                "error": "Redirect Location পাওয়া যায়নি।"
                    }
                next_url = urllib.parse.urljoin(current_url, loc)
                if stop_on_login_wall and any(w in next_url.lower() for w in ("/login", "/accounts/login", "/checkpoint", "/recover", "login.php")):
                    try:
                        parsed_lw = urllib.parse.urlparse(next_url)
                        qs = dict(urllib.parse.parse_qsl(parsed_lw.query))
                        unwrapped = urllib.parse.unquote(str(qs.get("next") or qs.get("u") or qs.get("continue") or "")).strip()
                        if unwrapped:
                            cand_u = urllib.parse.urljoin(current_url, unwrapped)
                            if "/login" not in cand_u.lower():
                                current_url = cand_u
                                continue
                    except Exception:
                        pass
                    return {
                        "ok": True,
                        "original_url": str(url),
                        "final_url": last_valid_url,
                        "final_domain": normalize_domain_host(last_valid_url),
                        "redirect_chain": redirect_chain,
                        "body": b"",
                        "status_code": code,
                        "error_category": "login_wall",
                        "reason": "Login wall redirect intercepted",
                "error": "Login wall redirect intercepted"
                    }
                current_url = next_url
                continue

            err_body = b""
            try:
                err_body = he.read(max_read_bytes) if max_read_bytes > 0 else b""
            except Exception:
                pass
            err_cat = "rate_limited" if code == 429 else ("http_error" if code >= 400 else "unknown")
            return {
                "ok": False,
                "original_url": str(url),
                "final_url": last_valid_url,
                "final_domain": normalize_domain_host(last_valid_url),
                "redirect_chain": redirect_chain,
                "body": err_body,
                "status_code": code,
                "error_category": err_cat,
                "reason": f"HTTP Error {code}",
                "error": f"HTTP Error {code}"
            }
        except Exception as exc:
            return {
                "ok": False,
                "original_url": str(url),
                "final_url": last_valid_url,
                "final_domain": normalize_domain_host(last_valid_url),
                "redirect_chain": redirect_chain,
                "body": b"",
                "status_code": 0,
                "error_category": "network_failure",
                "reason": str(exc)[:120],
                "error": str(exc)[:120]
            }

    return {
        "ok": False,
        "original_url": str(url),
        "final_url": last_valid_url,
        "final_domain": normalize_domain_host(last_valid_url),
        "redirect_chain": redirect_chain,
        "body": b"",
        "status_code": 0,
        "error_category": "max_redirects_exceeded",
        "reason": f"সর্বোচ্চ Redirect সীমা ({max_redirects}) অতিক্রম করেছে!",
                "error": f"সর্বোচ্চ Redirect সীমা ({max_redirects}) অতিক্রম করেছে!"
    }


# Compatibility aliases
record_failed_login_attempt = record_failed_login
clear_failed_login_attempts = reset_failed_login


def parse_multi_payment_numbers(raw_val: str, allow_rocket_12: bool = True, max_items: int = 2) -> list:
    """
    Parses a stored or user-entered payment number string (comma, pipe, or newline separated)
    into a deduplicated list of up to `max_items` normalized Bangladesh payment numbers.
    """
    if not raw_val:
        return []
    s = str(raw_val).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            import json
            arr = json.loads(s)
            if isinstance(arr, list):
                s = ",".join(str(x) for x in arr)
        except Exception:
            pass
    out = []
    for part in re.split(r"[,;|\n]+", s):
        p = part.strip()
        if not p:
            continue
        norm = normalize_bd_payment_number(p, allow_rocket_12=allow_rocket_12)
        if norm and norm not in out:
            out.append(norm)
            if len(out) >= max_items:
                break
    return out


def parse_multi_app_uids(raw_val: str, max_items: int = 2) -> list:
    """
    Parses a stored or user-entered Battle Club App UID string (comma, pipe, or newline separated)
    into a deduplicated list of up to `max_items` formatted App UIDs (e.g. ['#1007', '#1008']).
    """
    if not raw_val:
        return []
    s = str(raw_val).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            import json
            arr = json.loads(s)
            if isinstance(arr, list):
                s = ",".join(str(x) for x in arr)
        except Exception:
            pass
    out = []
    seen_canon = set()
    for part in re.split(r"[,;|\n]+", s):
        p = part.strip()
        if not p:
            continue
        disp = format_display_app_uid(p)
        canon = canonicalize_app_uid(disp)
        if disp and len(re.sub(r"[^0-9A-Z]", "", disp)) >= 2 and canon not in seen_canon:
            seen_canon.add(canon)
            out.append(disp)
            if len(out) >= max_items:
                break
    return out
clear_failed_login = clear_failed_login_attempts