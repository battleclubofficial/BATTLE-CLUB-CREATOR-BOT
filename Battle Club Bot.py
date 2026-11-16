# -*- coding: utf-8 -*-
# ==============================================================================
# BATTLE CLUB TELEGRAM BOT - Creator Sponsorship Verification (Enterprise v8.0)
# Strictly YouTube & TikTok Only + 100% Real Profile & Video Verification
# Mandatory Battle Club UID First -> 1/2/3 Payment Methods (bKash, Nagad, Rocket)
# Separate Per-Platform Channel Names + 2-Step Password Confirmation
# Advanced Settings Hub: Button Name/Design/Emoji Editor, Message Editor,
# Cross-Page & Same-Page Button Position Mover with Live Previews
# Per-User & Per-Admin Inline / Bottom Menu Toggle (ReplyKeyboardMarkup)
# Full-Width 30-Char Dividers (Zero Right-Side Gap on Mobile Telegram)
# Traffic Source Percentage Analytics + Reset Earnings + 5-Day / 50-Lakh Cap
# ==============================================================================
import os
import re
import sys
import csv
import json
import sqlite3
import secrets
import time
import html
import threading
import importlib.util
from functools import wraps
from datetime import datetime

os.environ.setdefault("TZ", "Asia/Dhaka")
try:
    time.tzset()
except Exception:
    pass


def _load_local_env_files():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for env_name in (".env", "bot.env", "env.txt"):
        for cand_dir in (os.getcwd(), base_dir):
            env_path = os.path.join(cand_dir, env_name)
            if os.path.isfile(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw_line in ef:
                            line = raw_line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip()
                            if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
                                v = v[1:-1]
                            if k and k not in os.environ:
                                os.environ[k] = v
                except Exception:
                    pass


_load_local_env_files()


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


_ensure_local_module("ui_catalog", ("ui_catalog.py", "Ui Catalog.py", "Ui_Catalog.py"))
_ensure_local_module("ui_validation", ("ui_validation.py", "Ui Validation.py", "Ui_Validation.py"))
_ensure_local_module("security", ("security.py", "Security.py"))
_ensure_local_module("finance", ("finance.py", "Finance.py"))
_ensure_local_module("database", ("database.py", "Database.py"))
_ensure_local_module("verifier", ("verifier.py", "Verifier.py"))

try:
    import telebot
    from telebot import types
except ImportError:
    from ui_validation import types as _fallback_types

    class _FallbackUser:
        def __init__(self, id=0, username="", first_name="Creator", last_name=""):
            self.id = id
            self.username = username
            self.first_name = first_name
            self.last_name = last_name

    class _FallbackChat:
        def __init__(self, id=0, username=""):
            self.id = id
            self.username = username

    class _FallbackLinkPreviewOptions:
        def __init__(self, is_disabled=False, url=None, prefer_large_media=True, show_above_text=True):
            self.is_disabled = is_disabled
            self.url = url
            self.prefer_large_media = prefer_large_media
            self.show_above_text = show_above_text

    _fallback_types.User = _FallbackUser
    _fallback_types.Chat = _FallbackChat
    _fallback_types.LinkPreviewOptions = _FallbackLinkPreviewOptions
    types = _fallback_types

    class _SentMessage:
        _next_id = 1000

        def __init__(self, chat_id, text, reply_markup=None, parse_mode=None, entities=None):
            _SentMessage._next_id += 1
            self.message_id = _SentMessage._next_id
            self.chat = _FallbackChat(id=chat_id)
            self.text = text
            self.reply_markup = reply_markup
            self.parse_mode = parse_mode
            self.entities = entities or []

    class _FallbackTeleBot:
        def __init__(self, token, parse_mode="HTML", num_threads=8):
            self.token = token
            self.parse_mode = parse_mode
            self.num_threads = num_threads
            self.message_handlers = []
            self.callback_handlers = []
            self.sent_messages = []
            self.edited_messages = []
            self.answered_callbacks = []

        def message_handler(self, commands=None, func=None, content_types=None):
            def decorator(handler):
                self.message_handlers.append({
                    "commands": commands,
                    "func": func,
                    "content_types": content_types,
                    "handler": handler
                })
                return handler
            return decorator

        def callback_query_handler(self, func=None):
            def decorator(handler):
                self.callback_handlers.append({"func": func, "handler": handler})
                return handler
            return decorator

        def send_message(self, chat_id, text, parse_mode=None, entities=None, reply_markup=None, **kwargs):
            msg = _SentMessage(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode, entities=entities)
            self.sent_messages.append(msg)
            return msg

        def edit_message_text(self, text, chat_id, message_id, parse_mode=None, entities=None, reply_markup=None, **kwargs):
            msg = _SentMessage(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode, entities=entities)
            msg.message_id = message_id
            self.edited_messages.append(msg)
            return msg

        def answer_callback_query(self, callback_query_id, text=None, show_alert=False, **kwargs):
            self.answered_callbacks.append({"id": callback_query_id, "text": text, "show_alert": show_alert})
            return True

        def delete_message(self, chat_id, message_id):
            return True

        def send_document(self, chat_id, document, caption=""):
            return _SentMessage(chat_id, caption)

        def copy_message(self, chat_id, from_chat_id, message_id):
            return _SentMessage(chat_id, f"Copied {message_id}")

        def get_me(self):
            return _FallbackUser(id=999999, username="BattleClubBot", first_name="BattleClubBot")

        def remove_webhook(self):
            return True

        def infinity_polling(self, timeout=20, long_polling_timeout=10, **kwargs):
            return None

    class _FallbackTelebotModule:
        TeleBot = _FallbackTeleBot
        types = _fallback_types

    telebot = _FallbackTelebotModule()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID", "8145274317").strip()
DB_FILE = os.getenv("DB_FILE", "battle_club.db")
USER_SESSION_TIMEOUT = int(os.getenv("USER_SESSION_TIMEOUT", "600"))

_PLACEHOLDER_PREFIXES = ("YOUR_", "REPLACE_", "CHANGE_ME", "<", "EXAMPLE_")

if __name__ == "__main__":
    if not BOT_TOKEN or BOT_TOKEN.upper().startswith(_PLACEHOLDER_PREFIXES):
        raise RuntimeError("BOT_TOKEN is missing or set to a placeholder. Configure a valid BOT_TOKEN in your private .env file before starting the bot.")
    if not ADMIN_PASSWORD or ADMIN_PASSWORD.upper().startswith(_PLACEHOLDER_PREFIXES):
        raise RuntimeError("ADMIN_PASSWORD is missing or set to a placeholder. Configure a valid ADMIN_PASSWORD in your private .env file before starting the bot.")
else:
    if not BOT_TOKEN or BOT_TOKEN.upper().startswith(_PLACEHOLDER_PREFIXES):
        BOT_TOKEN = "000000000:TEST_OFFLINE_TOKEN"
    if not ADMIN_PASSWORD or ADMIN_PASSWORD.upper().startswith(_PLACEHOLDER_PREFIXES):
        ADMIN_PASSWORD = "TEST_ADMIN_PASSWORD"

from security import (
    is_authorized_numeric_admin_id,
    unlock_admin_session,
    is_admin_session_unlocked,
    touch_admin_session,
    lock_admin_session,
    reset_failed_login,
    hash_password,
    verify_password,
    verify_admin_secret,
    mask_sensitive_secret,
    generate_random_code,
    generate_referral_code,
    normalize_bd_payment_number,
    parse_multi_payment_numbers,
    parse_multi_app_uids,
    normalize_permanent_app_uid,
    format_display_app_uid,
    canonicalize_app_uid,
    canonicalize_profile_identity,
    is_navigation_callback,
    check_rate_limit,
    check_duplicate_callback,
    acquire_flow_lock,
    release_flow_lock,
    record_failed_login_attempt,
    clear_failed_login_attempts,
    record_failed_login,
    clear_failed_login,
    get_failed_login_count,
    generate_custom_button_uid,
    cleanup_security_caches,
    normalize_domain_host
)
from database import (
    init_db,
    get_connection,
    set_setting as db_set_setting,
    get_platform_criteria,
    update_platform_criteria,
    get_user_platforms,
    add_verified_user_platform,
    check_and_lock_profile_identity,
    check_and_lock_user_identity,
    verify_and_consume_profile_edit_random_code,
    update_user_payment_and_profile_info,
    delete_user_account_completely,
    move_video_to_trash,
    move_all_permanent_approved_to_trash,
    restore_video_from_trash,
    permanently_delete_trashed_video,
    empty_all_trashed_videos,
    is_video_permanently_locked,
    is_video_submitted_globally,
    register_video_submission_lock,
    save_video_traffic_and_external_links,
    get_video_external_links,
    mark_external_link_notified,
    generate_admin_manual_verify_code,
    consume_admin_manual_verify_code,
    create_manual_verification_request,
    get_pending_manual_verifications,
    get_manual_verification_requests,
    resolve_manual_verification_request,
    create_broadcast_job,
    get_pending_broadcast_targets,
    sync_and_get_pending_broadcast_targets,
    record_broadcast_delivery_attempt,
    finalize_broadcast_job,
    get_button_emoji_map,
    set_button_custom_emoji,
    get_button_design_map,
    set_button_design_style,
    log_audit_event,
    validate_setting_value,
    get_dynamic_message_record,
    save_dynamic_message_record,
    get_dynamic_message_history,
    rollback_dynamic_message,
    get_video_approval_counts,
    generate_unique_bc_code,
    get_all_custom_buttons,
    get_custom_button,
    save_custom_button,
    delete_custom_button_record,
    generate_unique_custom_button_id,
    get_button_original_placement,
    record_button_placement,
    sync_layout_placements_in_db,
    locate_button_across_all_layouts,
    would_create_container_cycle,
    restore_button_to_original_placement,
    cleanup_orphan_custom_layouts_and_messages,
    create_custom_button_transactional,
    delete_custom_button_transactional,
    get_video_external_link_history,
    begin_immediate_transaction,
    verify_sqlite_integrity,
    reconcile_legacy_ledger_idempotency_keys,
    set_button_visibility,
    get_button_visibility_map,
    set_dynamic_message_button_config
)
from finance import (
    get_or_create_ledger_entry,
    process_idempotent_milestone_payout,
    process_bot_approval_credit,
    verify_video_finance_eligibility,
    transition_expired_pending_video,
    resolve_external_link_financial_action,
    reset_external_link_video_earnings,
    admin_accept_bot_approved_video,
    admin_permanent_approve_video,
    admin_reject_video_with_reversal,
    admin_reaccept_rejected_video,
    admin_mark_withdrawal_paid,
    admin_cancel_withdrawal_with_refund,
    get_video_payment_rates,
    get_video_tracking_days,
    get_max_payable_views_setting
)
from verifier import (
    detect_platform,
    canonicalize_video_id,
    parse_human_number,
    verify_profile_strict,
    verify_video_submission_strict,
    verify_bio_code_only,
    verify_video_code_only,
    verify_dual_source_views,
    assess_organic_view_risk,
    analyze_video_traffic_sources,
    extract_metadata_via_ytdlp,
    fetch_video_public_metadata,
    reverify_video_code_and_ownership_only,
    resolve_shortlink_redirect_chain,
    classify_verification_failure,
    _uid_matches_caption,
    PLATFORMS
)
from ui_catalog import (
    FULL_WIDTH_DIVIDER,
    COLOR_PALETTE,
    BUTTON_TEXT_DESIGN_STYLES,
    ALLOWED_DYNAMIC_LAYOUT_KEYS,
    LAYOUT_PAGE_TITLES,
    DEFAULT_SETTINGS,
    CRITERIA_FIELD_EXPLANATIONS,
    SETTING_FIELD_EXPLANATIONS,
    DEFAULT_BUTTON_LABELS,
    DEFAULT_BUTTON_LABELS_EN,
    DEFAULT_BUTTON_EMOJIS,
    MAIN_ADMIN_BUTTON_KEYS,
    SETTINGS_ONLY_BUTTON_KEYS,
    DEFAULT_LAYOUTS,
    SETTINGS_CONTROL_HUB_SUBMENUS,
    PLATFORM_SETTINGS_SUBMENUS,
    GENERAL_SETTINGS_SUBMENUS,
    ADVANCED_SETTINGS_SUBMENUS,
    DEFAULT_MESSAGES,
    DEFAULT_MESSAGES_EN,
    MESSAGE_TEMPLATE_LABELS,
    ADMIN_GUIDE_TEXT,
    COMMAND_SHORTCUT_CATEGORIES,
    build_full_command_shortcut_text
)
from ui_validation import (
    BUTTON_RUNTIME_CAPS,
    StyledInlineButton,
    StyledKeyboardButton,
    make_reply_btn,
    short_layout_code,
    resolve_layout_key,
    validate_callback_data,
    apply_button_text_design,
    ensure_full_width_message,
    ensure_visible_emoji_presentation,
    normalize_button_label_and_extract_emoji,
    reconstruct_html_from_raw_and_entities,
    make_btn as _base_make_btn,
    strip_legacy_action_routes,
    resolve_menu_layout,
    paginate_items,
    build_pagination_row,
    unescape_allowed_html_tags,
    serialize_message_entities,
    extract_rich_html_text,
    html_to_plain_and_telegram_entities,
    parse_telegram_html,
    strip_tg_emoji_tags,
    repair_or_fallback_html,
    strip_leading_default_emojis,
    extract_leading_default_emojis,
    supports_button_custom_emoji
)

BOT_NUM_THREADS = max(1, min(32, int(os.getenv("BOT_NUM_THREADS", "8") or 8)))
USER_ACTION_COOLDOWN_SEC = float(os.getenv("USER_ACTION_COOLDOWN_SEC", "1.5") or 1.5)
BATCH_REQUEST_DELAY_SEC = float(os.getenv("BATCH_REQUEST_DELAY_SEC", "0.35") or 0.35)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", num_threads=BOT_NUM_THREADS)
db_lock = threading.RLock()

if hasattr(telebot, "apihelper") and hasattr(telebot.apihelper, "_make_request"):
    _orig_make_request = telebot.apihelper._make_request

    def _safe_make_request(token, method_name, method="get", params=None, files=None, **kwargs):
        if isinstance(params, dict):
            if params.get("entities") or params.get("caption_entities"):
                params.pop("parse_mode", None)
            elif "parse_mode" in params and not params["parse_mode"]:
                params.pop("parse_mode", None)
            lpo = params.get("link_preview_options")
            if lpo is not None and not isinstance(lpo, (str, bytes)):
                try:
                    if hasattr(lpo, "to_json"):
                        params["link_preview_options"] = lpo.to_json()
                    elif hasattr(lpo, "to_dict"):
                        params["link_preview_options"] = json.dumps(lpo.to_dict())
                    elif isinstance(lpo, dict):
                        params["link_preview_options"] = json.dumps(lpo)
                except Exception:
                    params.pop("link_preview_options", None)
        for attempt in range(3):
            try:
                return _orig_make_request(token, method_name, method=method, params=params, files=files, **kwargs)
            except Exception as exc:
                err_s = str(exc)
                m_wait = re.search(r"retry after\s+([0-9]+)", err_s, re.IGNORECASE)
                if m_wait and attempt < 2:
                    wait_sec = min(15, max(1, int(m_wait.group(1))))
                    time.sleep(wait_sec)
                    continue
                raise

    telebot.apihelper._make_request = _safe_make_request

_orig_bot_send_message = bot.send_message
_orig_bot_edit_message_text = bot.edit_message_text
_orig_bot_answer_callback_query = bot.answer_callback_query
_answered_callback_ids = {}
_answered_cb_lock = threading.RLock()

_BOT_DELIVERY_CAPS = {
    "custom_emoji_entities": True,
    "custom_emoji_html": True,
    "link_preview_options": True
}


def _patched_send_message(chat_id, text, parse_mode=None, entities=None, reply_markup=None, **kwargs):
    eff_pm = "" if entities else ("HTML" if parse_mode is None else parse_mode)
    return _orig_bot_send_message(chat_id, text, parse_mode=eff_pm, entities=entities, reply_markup=reply_markup, **kwargs)


def _patched_edit_message_text(text, chat_id=None, message_id=None, parse_mode=None, entities=None, reply_markup=None, **kwargs):
    eff_pm = "" if entities else ("HTML" if parse_mode is None else parse_mode)
    return _orig_bot_edit_message_text(text, chat_id, message_id, parse_mode=eff_pm, entities=entities, reply_markup=reply_markup, **kwargs)


def _patched_answer_callback_query(callback_query_id, text=None, show_alert=False, **kwargs):
    cb_id = str(callback_query_id or "").strip()
    if not cb_id or cb_id.startswith("cmd_"):
        return True
    now_t = time.time()
    with _answered_cb_lock:
        if cb_id in _answered_callback_ids:
            return True
        _answered_callback_ids[cb_id] = now_t
        if len(_answered_callback_ids) > 4000:
            cutoff = now_t - 120.0
            for k, v in list(_answered_callback_ids.items()):
                if v < cutoff:
                    _answered_callback_ids.pop(k, None)
    try:
        return _orig_bot_answer_callback_query(callback_query_id, text=text, show_alert=show_alert, **kwargs)
    except Exception:
        return False


bot.send_message = _patched_send_message
bot.edit_message_text = _patched_edit_message_text
bot.answer_callback_query = _patched_answer_callback_query
user_memory_states = {}
admin_unlocked_sessions = {}
admin_perm_selected_videos = {}

# In-Memory Cache for Instant Zero-Latency Button & Message Rendering
CACHE_SETTINGS = {}
CACHE_LABELS = {}
CACHE_STYLES = {}
CACHE_DESIGNS = {}
CACHE_BUTTON_EMOJIS = {}
CACHE_BUTTON_LABEL_CUSTOMIZED = set()
CACHE_BUTTON_EMOJI_CUSTOMIZED = set()
CACHE_BUTTON_VISIBILITY = {}
CACHE_LAYOUTS = {}
CACHE_MESSAGES = {}
CACHE_MESSAGE_ENTITIES = {}
CACHE_MESSAGE_BUTTON_MODES = {}
CACHE_MESSAGE_CUSTOM_BUTTONS = {}
_THREAD_MSG_CTX = threading.local()

PAYMENT_PLATFORM_LABELS = {
    "bKash": "🌸 বিকাশ (bKash)",
    "Nagad": "🍊 নগদ (Nagad)",
    "Rocket": "🚀 রকেট (Rocket)",
    "BattleClub_UID": "🎮 Battle Club UID"
}

ORDINAL_ACCOUNT_LABELS_BN = {
    1: "১ম অ্যাকাউন্ট (First Account)",
    2: "২য় অ্যাকাউন্ট (Second Account)",
    3: "৩য় অ্যাকাউন্ট (Third Account)",
    4: "৪র্থ অ্যাকাউন্ট (Fourth Account)",
    5: "৫ম অ্যাকাউন্ট (Fifth Account)"
}

# Universal Button Key -> Callback Route Map (so any button moved to any page works 100%)
GLOBAL_BUTTON_CALLBACK_MAP = {
    "u_dashboard": "umenu:dashboard",
    "u_how_to_work": "umenu:how_to_work",
    "u_profile": "umenu:profile",
    "u_submit": "umenu:submit_menu",
    "u_my_videos": "umenu:my_videos",
    "u_link_more": "umenu:link_more",
    "u_withdraw": "umenu:withdraw",
    "u_wd_list": "umenu:wd_list:all:0",
    "u_history": "umenu:history",
    "u_leaderboard": "umenu:leaderboard",
    "u_settings": "umenu:settings_hub",
    "u_referral": "umenu:referral",
    "u_redeem": "umenu:redeem",
    "u_activity": "umenu:activity",
    "u_pwd_change": "umenu:pwd_change",
    "u_logout": "umenu:logout",
    "u_color": "umenu:color",
    "u_lang": "umenu:lang_toggle",
    "u_menu_mode_toggle": "umenu:menu_mode_toggle",
    "u_delete_acc": "umenu:delete_acc",
    "u_back": "umenu:cancel_home",
    "u_home": "umenu:cancel_home",
    "u_prof_name_edit": "uprof_name_menu",
    "u_prof_wd_num_edit": "uprof_wd_num_menu",
    "u_plat_youtube": "reg_toggle:youtube",
    "u_plat_tiktok": "reg_toggle:tiktok",
    "u_plat_both": "reg_toggle:all2",
    "u_plat_confirm": "reg_confirm_selection",
    "a_metrics": "adm_view_metrics",
    "a_wd_reports": "adm_wd_reports_hub",
    "a_pending_vids": "adm_vsec:pe:select:0",
    "a_bot_approve": "adm_vsec:ba:select:0",
    "a_admin_approve": "adm_vsec:aa:select:0",
    "a_perm_approve": "adm_vsec:pa:select:0",
    "a_rejected_vids": "adm_vsec:rj:select:0",
    "a_trash": "adm_trash:0",
    "a_user_list": "adm_ulist:0",
    "a_all_vids": "adm_all_vids:0",
    "a_traffic_ext": "adm_traffic:all:0",
    "a_fin_ledger": "adm_fin_history:0",
    "a_broadcast": "adm_broadcast_prompt",
    "a_settings": "adm_settings_hub",
    "a_adv_settings": "adm_adv_hub",
    "a_plat_settings": "adm_plat_settings_hub",
    "a_gen_settings": "adm_gen_settings_hub",
    "a_btn_editor": "adm_btn_editor_hub",
    "a_msg_editor": "adm_msg_hub",
    "a_btn_pos_editor": "adm_bpos_hub",
    "a_tutorial_vid": "adm_edit_top_yt",
    "a_db_export": "adm_db_export_hub",
    "a_menu_mode_toggle": "adm_toggle_bottom_menu",
    "a_logout": "adm_logout",
    "a_back": "admin_hub",
    "a_user_home": "umenu:cancel_home",
    "a_super_admin_panel": "admin_hub",
    "u_settings_hub": "umenu:settings_hub",
    "u_bottom_toggle": "umenu:menu_mode_toggle",
    "u_back_home": "umenu:cancel_home",
    "u_prof_change_name": "uprof_name_menu",
    "u_prof_change_wd": "uprof_wd_num_menu",
    "u_back_dashboard": "umenu:dashboard",
    "a_traffic_hub": "adm_traffic:all:0",
    "a_bottom_toggle": "adm_toggle_bottom_menu",
    "a_rate_settings": "adm_edit_rate_days",
    "a_wd_settings": "adm_wd_limit_hub",
    "a_ref_settings": "adm_edit_ref_hub",
    "a_antifraud_settings": "adm_shub:antifraud",
    "a_general_settings": "adm_gen_settings_hub",
    "a_back_admin": "admin_hub",
    "a_man_ver": "adm_man_ver:hub",
    "a_mvr_gen": "adm_mvr_gen",
    "a_hashtag_yt": "adm_shub:hashtag_yt",
    "a_support_group": "adm_shub:support_group",
    "a_export_hub": "adm_db_export_hub",
    "a_export": "adm_export_data",
    "a_fin_history": "adm_fin_history:0",
    "a_msg_hub": "adm_msg_hub",
    "a_lb_customizer": "adm_lb_customizer",
    "a_admin_guide": "adm_guide_map",
    "a_cmd_list": "adm_cmd_shortcuts"
}

# Reverse map from callback_data -> canonical btn_key so buttons created without explicit btn_key still inherit custom emoji & design
GLOBAL_CALLBACK_BUTTON_REVERSE_MAP = {}
for _bk_k, _bk_cb in GLOBAL_BUTTON_CALLBACK_MAP.items():
    if _bk_k in DEFAULT_BUTTON_LABELS or _bk_cb not in GLOBAL_CALLBACK_BUTTON_REVERSE_MAP:
        GLOBAL_CALLBACK_BUTTON_REVERSE_MAP[_bk_cb] = _bk_k


def _resolve_btn_key_from_callback(callback_data: str) -> str:
    cb_s = str(callback_data or "").strip()
    if not cb_s:
        return ""
    if cb_s in GLOBAL_CALLBACK_BUTTON_REVERSE_MAP:
        return GLOBAL_CALLBACK_BUTTON_REVERSE_MAP[cb_s]
    if cb_s == "uprof_edit:name":
        return "u_prof_change_acc_name"
    if cb_s == "uprof_edit:app_uid":
        return "u_prof_change_uid"
    if cb_s == "uwd_method:bKash":
        return "u_wd_bkash"
    if cb_s == "uwd_method:Nagad":
        return "u_wd_nagad"
    if cb_s == "uwd_method:Rocket":
        return "u_wd_rocket"
    if cb_s == "uwd_method:BattleClub_UID":
        return "u_wd_uid"
    if cb_s in ("uwd_method:other_way", "uwd_other_go"):
        return "u_wd_other"
    return ""


_CUSTOM_EMOJI_STICKER_CHAR_CACHE = {}


def _resolve_custom_emoji_fallback_char(emoji_id: str, default_char: str = "") -> str:
    """
    Resolves the official Unicode fallback emoji for a Telegram `custom_emoji_id` via `getCustomEmojiStickers`
    (cached in memory) so buttons with custom emojis ALWAYS have a visible color emoji even if
    `icon_custom_emoji_id` is not rendered by the client or bot!
    """
    cid = re.sub(r"[^0-9]", "", str(emoji_id or "").strip())
    if not cid:
        return ensure_visible_emoji_presentation(default_char)
    if cid in _CUSTOM_EMOJI_STICKER_CHAR_CACHE:
        return _CUSTOM_EMOJI_STICKER_CHAR_CACHE[cid]
    resolved_ch = ""
    try:
        if hasattr(bot, "get_custom_emoji_stickers") and BOT_TOKEN and not BOT_TOKEN.startswith("000000000:"):
            stickers = bot.get_custom_emoji_stickers([cid])
            if stickers and len(stickers) > 0:
                resolved_ch = ensure_visible_emoji_presentation(str(getattr(stickers[0], "emoji", "") or "").strip())
        elif hasattr(telebot, "apihelper") and hasattr(telebot.apihelper, "_make_request") and BOT_TOKEN and not BOT_TOKEN.startswith("000000000:"):
            res = telebot.apihelper._make_request(
                BOT_TOKEN,
                "getCustomEmojiStickers",
                params={"custom_emoji_ids": json.dumps([cid])}
            )
            if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
                resolved_ch = ensure_visible_emoji_presentation(str(res[0].get("emoji", "") or "").strip())
    except Exception:
        resolved_ch = ""
    if resolved_ch:
        _CUSTOM_EMOJI_STICKER_CHAR_CACHE[cid] = resolved_ch
        return resolved_ch
    return ensure_visible_emoji_presentation(default_char)


def make_btn(text, callback_data=None, url=None, style=None, icon_custom_emoji_id=None, btn_key=None, design_style=None):
    resolved_key = btn_key or _resolve_btn_key_from_callback(callback_data)
    emoji_id = icon_custom_emoji_id
    if not emoji_id and resolved_key:
        emoji_id = get_btn_emoji(resolved_key)
    clean_text = ensure_visible_emoji_presentation(strip_tg_emoji_tags(str(text or "")).strip() or str(text or ""))
    eff_design = design_style if design_style is not None else (get_btn_design(resolved_key) if resolved_key else "normal")
    styled_text = apply_button_text_design(clean_text, eff_design) if eff_design and eff_design != "normal" else clean_text
    return _base_make_btn(
        text=styled_text,
        callback_data=callback_data,
        url=url,
        style=style,
        icon_custom_emoji_id=emoji_id,
    )


def video_decision_callback(decision: str, sub_id: str, section: str, platform_filter: str = "all") -> str:
    sec_map = {
        "pending": "pe",
        "bot_approve": "ba",
        "admin_approve": "aa",
        "permanent_approve": "pa",
        "rejected": "rj",
        "pe": "pe",
        "ba": "ba",
        "aa": "aa",
        "pa": "pa",
        "rj": "rj"
    }
    s_short = sec_map.get(str(section or "bot_approve"), str(section or "ba")[:2])
    return validate_callback_data(f"vd:{decision}:{sub_id}:{s_short}:{platform_filter}")


def _expand_section_code(sec_code: str) -> str:
    rev = {
        "pe": "pending",
        "ba": "bot_approve",
        "aa": "admin_approve",
        "pa": "permanent_approve",
        "rj": "rejected",
        "pending": "pending",
        "bot_approve": "bot_approve",
        "admin_approve": "admin_approve",
        "permanent_approve": "permanent_approve",
        "rejected": "rejected"
    }
    return rev.get(str(sec_code or "bot_approve"), "bot_approve")


def _short_section_code(section: str) -> str:
    fwd = {
        "pending": "pe",
        "bot_approve": "ba",
        "admin_approve": "aa",
        "permanent_approve": "pa",
        "rejected": "rj"
    }
    return fwd.get(str(section or "bot_approve"), str(section or "ba")[:2])


# ==============================================================================
# OUTGOING MESSAGE PREPARATION, FULL-WIDTH BUBBLE FIX & CUSTOM EMOJI DELIVERY
# ==============================================================================
def attach_top_youtube_preview(text, yt_url):
    u = str(yt_url or "").strip()
    if not u or u.lower() in ("none", "nane"):
        return str(text)
    inv_link = f'<a href="{html.escape(u)}">&#8205;</a>'
    return f"{inv_link}{text}"


def build_link_preview_options(top_yt_url=None, disable_preview=True):
    u = str(top_yt_url or "").strip()
    has_top_vid = bool(u and u.lower() not in ("none", "nane"))
    # Only use LinkPreviewOptions when a specific top_yt_url preview is needed;
    # otherwise use standard `disable_web_page_preview` which never fails across any telebot version!
    if has_top_vid and _BOT_DELIVERY_CAPS.get("link_preview_options", True):
        try:
            if hasattr(types, "LinkPreviewOptions"):
                return {"link_preview_options": types.LinkPreviewOptions(is_disabled=False, url=u, prefer_large_media=True, show_above_text=True)}
        except Exception:
            pass
    return {"disable_web_page_preview": False if has_top_vid else bool(disable_preview)}


def _adapt_caps_from_error(err: Exception):
    err_low = str(err or "").lower()
    if "link_preview_options" in err_low:
        _BOT_DELIVERY_CAPS["link_preview_options"] = False
    if "entities_too_long" in err_low:
        _BOT_DELIVERY_CAPS["custom_emoji_entities"] = False
    if any(k in err_low for k in ("button_style_invalid", 'unknown field "style"')):
        BUTTON_RUNTIME_CAPS["allow_style"] = False
    if any(k in err_low for k in ("button_custom_emoji_invalid", 'unknown field "icon_custom_emoji_id"')):
        BUTTON_RUNTIME_CAPS["allow_custom_emoji"] = False


def esc(text):
    return html.escape(str(text if text is not None else ""))


def normalize_digits(text):
    return str(text or "").translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))


def _split_datetime_str(dt_raw: str) -> tuple:
    """Splits a timestamp like '2026-11-12 17:45:00' into ('2026-11-12', '17:45')."""
    s = str(dt_raw or "").strip()
    if not s:
        now_dt = datetime.now()
        return now_dt.strftime("%Y-%m-%d"), now_dt.strftime("%H:%M")
    parts = s.split()
    d_part = parts[0] if parts else s
    t_part = parts[1][:5] if len(parts) > 1 else "00:00"
    return d_part, t_part


def build_visual_progress_bar(pct: float, length: int = 10) -> str:
    p = max(0.0, min(100.0, float(pct or 0.0)))
    filled = int(round((p / 100.0) * length))
    filled = max(0, min(length, filled))
    return "█" * filled + "░" * (length - filled)


USER_ACTIVE_BOTTOM_BUTTON_MAP = {}
USER_LAST_BOT_MSG_ID = {}
USER_ACTIVE_UI_MSGS = {}
_UI_CLEAN_LOCK = threading.RLock()


def track_ui_message(uid: str, message_id: int, ts: float = None):
    """Records an active UI/prompt/navigation message ID for `uid` in a thread-safe list."""
    uid_s = str(uid or "").strip()
    if not uid_s or uid_s.startswith("-") or not message_id:
        return
    now_t = float(ts if ts is not None else time.time())
    with _UI_CLEAN_LOCK:
        lst = USER_ACTIVE_UI_MSGS.setdefault(uid_s, [])
        existing_ids = {item[0] if isinstance(item, tuple) else int(item) for item in lst}
        if int(message_id) not in existing_ids:
            lst.append((int(message_id), now_t))
        if len(lst) > 40:
            del lst[:-40]
        USER_LAST_BOT_MSG_ID[uid_s] = int(message_id)


def cleanup_user_ui_messages(chat_id, uid: str = None, keep_message_ids=None, min_age_sec: float = 0.0):
    """
    Deletes previously tracked UI/prompt/processing messages for `uid` so chat history stays completely clean.
    Messages in `keep_message_ids` or newer than `min_age_sec` (e.g. sent in the same turn) are preserved.
    """
    uid_s = str(uid if uid is not None else chat_id).strip()
    if not uid_s or uid_s.startswith("-"):
        return
    keep_set = {int(x) for x in (keep_message_ids or []) if x}
    now_t = time.time()
    to_delete = []
    remaining = []
    with _UI_CLEAN_LOCK:
        lst = list(USER_ACTIVE_UI_MSGS.get(uid_s) or [])
        for item in lst:
            mid = int(item[0]) if isinstance(item, tuple) else int(item)
            mts = float(item[1]) if (isinstance(item, tuple) and len(item) > 1) else 0.0
            if mid in keep_set or (min_age_sec > 0 and (now_t - mts) < min_age_sec):
                remaining.append((mid, mts))
            else:
                to_delete.append(mid)
        USER_ACTIVE_UI_MSGS[uid_s] = remaining
    for mid in to_delete:
        try:
            bot.delete_message(chat_id, mid)
        except Exception:
            pass


def schedule_message_auto_delete(chat_id, message_id: int, delay_sec: float = 7.0, uid: str = None):
    """Deletes a specific message (e.g. Logout confirmation) automatically after `delay_sec` seconds."""
    if not message_id:
        return
    def _del_task():
        try:
            bot.delete_message(chat_id, int(message_id))
        except Exception:
            pass
        if uid:
            with _UI_CLEAN_LOCK:
                lst = USER_ACTIVE_UI_MSGS.get(str(uid)) or []
                USER_ACTIVE_UI_MSGS[str(uid)] = [
                    it for it in lst if (int(it[0]) if isinstance(it, tuple) else int(it)) != int(message_id)
                ]
    if delay_sec <= 0:
        _del_task()
    else:
        t = threading.Timer(float(delay_sec), _del_task)
        t.daemon = True
        t.start()


def _reorder_keyboard_bottom_rows(reply_markup):
    """
    Ensures universal bottom button ordering on InlineKeyboardMarkup:
    - Any Admin Page Edit tools (`📐 বাটন সাজান`, `✏️ মেসেজ এডিট`) appear ABOVE the Back/Home buttons.
    - `🔙 ফিরে যান (Back)` and `🏠 হোমপেজ / অ্যাডমিন ড্যাশবোর্ডে ফিরে যান` always stay at the very bottom!
    """
    if not reply_markup or getattr(reply_markup, "__class__", None).__name__ == "ReplyKeyboardMarkup":
        return reply_markup
    if not hasattr(reply_markup, "keyboard") or not isinstance(reply_markup.keyboard, list) or len(reply_markup.keyboard) < 2:
        return reply_markup

    normal_rows = []
    edit_tool_rows = []
    back_home_rows = []

    for row in reply_markup.keyboard:
        if not row:
            continue
        cbs = [str(getattr(b, "callback_data", "") or (b.get("callback_data", "") if isinstance(b, dict) else "")) for b in row]
        txts = [str(getattr(b, "text", "") or (b.get("text", "") if isinstance(b, dict) else "")) for b in row]
        is_edit_row = any(cb.startswith(("adm_elayout:", "adm_emsg:")) for cb in cbs) and all(
            cb.startswith(("adm_elayout:", "adm_emsg:", "adm_lb_customizer")) for cb in cbs if cb
        )
        is_back_home_row = all(
            (
                cb in ("umenu:cancel_home", "admin_hub", "umenu:profile", "umenu:dashboard", "umenu:settings_hub", "adm_settings_hub", "adm_adv_hub", "adm_plat_settings_hub", "adm_gen_settings_hub")
                or any(k in t for k in ("🔙", "ফিরে যান", "Back", "হোমপেজে", "ড্যাশবোর্ডে যান", "বাতিল করুন"))
            )
            for cb, t in zip(cbs, txts)
        )
        if is_edit_row:
            edit_tool_rows.append(row)
        elif is_back_home_row and (edit_tool_rows or normal_rows):
            back_home_rows.append(row)
        else:
            if back_home_rows:
                normal_rows.extend(back_home_rows)
                back_home_rows = []
            normal_rows.append(row)

    if edit_tool_rows and back_home_rows:
        reply_markup.keyboard = normal_rows + edit_tool_rows + back_home_rows
    return reply_markup


def prepare_outgoing(text, reply_markup=None, menu_id=None, include_admin_guide=False):
    raw_s = strip_legacy_action_routes(str(text or ""))
    if include_admin_guide:
        raw_s = f"{raw_s}\n\n{ADMIN_GUIDE_TEXT}"
    reply_markup = _reorder_keyboard_bottom_rows(reply_markup)
    has_btns = bool(reply_markup is not None)
    full_width_s = ensure_full_width_message(raw_s, has_buttons=has_btns)
    clean_html = repair_or_fallback_html(full_width_s)
    plain_text, entities, has_custom_emoji = parse_telegram_html(clean_html)
    return {
        "html_text": clean_html,
        "plain_text": plain_text,
        "entities": entities,
        "has_custom_emoji": has_custom_emoji,
        "reply_markup": reply_markup,
        "menu_id": menu_id if menu_id in ALLOWED_DYNAMIC_LAYOUT_KEYS else None
    }


def _extract_btn_fields(btn):
    """Safely extracts (text, url, callback_data, style, icon_custom_emoji_id) whether `btn` is a dict or Button object."""
    if isinstance(btn, dict):
        return (
            ensure_visible_emoji_presentation(str(btn.get("text", "") or "")),
            btn.get("url"),
            btn.get("callback_data"),
            btn.get("style"),
            btn.get("icon_custom_emoji_id")
        )
    return (
        ensure_visible_emoji_presentation(str(getattr(btn, "text", btn) or "")),
        getattr(btn, "url", None),
        getattr(btn, "callback_data", None),
        getattr(btn, "style", None),
        getattr(btn, "icon_custom_emoji_id", None)
    )


def _strip_color_keep_emoji_keyboard(reply_markup):
    """Strips only `style` while preserving `icon_custom_emoji_id` on all buttons."""
    if not reply_markup or not hasattr(reply_markup, "keyboard"):
        return reply_markup
    cls_name = getattr(reply_markup, "__class__", None).__name__
    if cls_name == "ReplyKeyboardMarkup":
        rk = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in reply_markup.keyboard:
            r_btns = []
            for btn in row:
                txt, _, _, _, em = _extract_btn_fields(btn)
                r_btns.append(StyledKeyboardButton(text=txt, style=None, icon_custom_emoji_id=em))
            if r_btns:
                rk.row(*r_btns)
        return rk
    kb = types.InlineKeyboardMarkup()
    for row in reply_markup.keyboard:
        r_btns = []
        for btn in row:
            txt, url, cb, _, em = _extract_btn_fields(btn)
            if url:
                r_btns.append(StyledInlineButton(text=txt, url=str(url), style=None, icon_custom_emoji_id=em))
            elif cb:
                r_btns.append(StyledInlineButton(text=txt, callback_data=str(cb), style=None, icon_custom_emoji_id=em))
        if r_btns:
            kb.row(*r_btns)
    return kb


def _strip_emoji_keep_color_keyboard(reply_markup):
    """
    Strips only `icon_custom_emoji_id` while preserving button colors (`style`: success/danger/primary)
    and NEVER re-injecting a normal emoji into `txt` if the admin deleted the normal emoji!
    """
    if not reply_markup or not hasattr(reply_markup, "keyboard"):
        return reply_markup
    cls_name = getattr(reply_markup, "__class__", None).__name__
    if cls_name == "ReplyKeyboardMarkup":
        rk = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in reply_markup.keyboard:
            r_btns = []
            for btn in row:
                txt, _, _, st, _ = _extract_btn_fields(btn)
                r_btns.append(StyledKeyboardButton(text=txt, style=st, icon_custom_emoji_id=None))
            if r_btns:
                rk.row(*r_btns)
        return rk
    kb = types.InlineKeyboardMarkup()
    for row in reply_markup.keyboard:
        r_btns = []
        for btn in row:
            txt, url, cb, st, _ = _extract_btn_fields(btn)
            if url:
                r_btns.append(StyledInlineButton(text=txt, url=str(url), style=st, icon_custom_emoji_id=None))
            elif cb:
                r_btns.append(StyledInlineButton(text=txt, callback_data=str(cb), style=st, icon_custom_emoji_id=None))
        if r_btns:
            kb.row(*r_btns)
    return kb


def _downgrade_keyboard_to_standard(reply_markup):
    if not reply_markup or not hasattr(reply_markup, "keyboard"):
        return reply_markup
    cls_name = getattr(reply_markup, "__class__", None).__name__
    if cls_name == "ReplyKeyboardMarkup":
        rk = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in reply_markup.keyboard:
            std_row = []
            for btn in row:
                txt, _, _, _, _ = _extract_btn_fields(btn)
                std_row.append(types.KeyboardButton(text=txt))
            if std_row:
                rk.row(*std_row)
        return rk
    kb = types.InlineKeyboardMarkup()
    for row in reply_markup.keyboard:
        std_row = []
        for btn in row:
            txt, url, cb, _, _ = _extract_btn_fields(btn)
            if url:
                std_row.append(types.InlineKeyboardButton(text=txt, url=str(url)))
            elif cb:
                std_row.append(types.InlineKeyboardButton(text=txt, callback_data=str(cb)))
        if std_row:
            kb.row(*std_row)
    return kb


def _is_admin_markup_context(reply_markup, menu_id=None) -> bool:
    if str(menu_id or "").startswith("admin"):
        return True
    if not reply_markup or not hasattr(reply_markup, "keyboard"):
        return False
    admin_cbs = 0
    user_cbs = 0
    for row in reply_markup.keyboard:
        for btn in row:
            _, _, cb, _, _ = _extract_btn_fields(btn)
            cb = str(cb or "")
            if not cb:
                continue
            if cb in ("admin_hub",) or cb.startswith(("adm_elayout:", "adm_emsg:")):
                continue
            if cb.startswith(("adm_", "vd:", "ext_act:")):
                admin_cbs += 1
            else:
                user_cbs += 1
    return admin_cbs > 0 and user_cbs == 0


def should_convert_markup_to_bottom_menu(chat_id, reply_markup, menu_id=None) -> bool:
    """
    Determines if an InlineKeyboardMarkup should be rendered exclusively in the Bottom Menu
    (ReplyKeyboardMarkup) with ZERO inline buttons on the message box above.
    """
    if reply_markup is None:
        return False
    cls_name = getattr(reply_markup, "__class__", None).__name__
    if cls_name in ("ReplyKeyboardMarkup", "ReplyKeyboardRemove"):
        return False
    if not hasattr(reply_markup, "keyboard") or not reply_markup.keyboard:
        return False
    uid = str(chat_id or "").strip()
    if not uid or uid.startswith("-"):
        return False
    try:
        u = get_user(uid)
    except Exception:
        u = None
    if not u:
        return False
    if _is_admin_markup_context(reply_markup, menu_id=menu_id):
        return int(u.get("admin_bottom_menu") or 0) == 1
    return int(u.get("bottom_menu_enabled") or 0) == 1


def convert_inline_to_bottom_reply_keyboard(uid: str, inline_kb, u_obj: dict = None):
    """
    Converts ANY page or sub-page InlineKeyboardMarkup into a colored, custom-emoji
    ReplyKeyboardMarkup (`StyledKeyboardButton`) and registers all button texts in
    `USER_ACTIVE_BOTTOM_BUTTON_MAP[uid]`.
    Enterprise v9.0 Fix:
    - Guarantees that multiple buttons with the same label (`b_txt`) on a Bottom Menu NEVER
      overwrite each other's callbacks! Duplicate labels are disambiguated (`Label [2]`, `Label [3]`)
      and all callbacks for `b_txt` are also preserved in `btn_map["__multi__:" + b_txt]`.
    """
    uid_s = str(uid or "").strip()
    if getattr(inline_kb, "__class__", None).__name__ == "ReplyKeyboardMarkup":
        return inline_kb
    u = u_obj
    if u is None and uid_s:
        try:
            u = get_user(uid_s)
        except Exception:
            u = None
    u_style = (u.get("user_btn_style") or "").strip() if u else ""
    is_adm_ctx = _is_admin_markup_context(inline_kb)

    rk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_map = {}
    label_counts = {}
    multi_callbacks = {}

    for r_idx, row in enumerate(getattr(inline_kb, "keyboard", [])):
        r_btns = []
        for c_idx, btn in enumerate(row):
            b_txt, b_url, b_cb, b_style, b_emoji = _extract_btn_fields(btn)
            b_txt = b_txt.strip()
            if not b_txt:
                continue
            if not is_adm_ctx and u_style in ("success", "danger", "primary"):
                b_style = u_style
            if b_style not in ("success", "danger", "primary"):
                b_style = "primary"
            _rk_k = None
            if b_cb:
                _rk_k = _resolve_btn_key_from_callback(b_cb)
                if not b_emoji and _rk_k:
                    b_emoji = get_btn_emoji(_rk_k) or None

            entry = {
                "callback_data": b_cb,
                "url": b_url,
                "btn_key": _rk_k,
                "row_index": r_idx,
                "col_index": c_idx
            }
            multi_callbacks.setdefault(b_txt, []).append(entry)

            if b_txt not in label_counts:
                label_counts[b_txt] = 1
                disp_txt = b_txt
            else:
                label_counts[b_txt] += 1
                dup_num = label_counts[b_txt]
                disp_txt = f"{b_txt} [{dup_num}]"
                while disp_txt in btn_map:
                    dup_num += 1
                    disp_txt = f"{b_txt} [{dup_num}]"

            r_btns.append(StyledKeyboardButton(text=disp_txt, style=b_style, icon_custom_emoji_id=b_emoji))
            btn_map[disp_txt] = dict(entry, display_text=disp_txt, base_text=b_txt)

        if r_btns:
            rk.row(*r_btns)

    for base_lbl, entries_list in multi_callbacks.items():
        btn_map[f"__multi__:{base_lbl}"] = entries_list

    if uid_s:
        USER_ACTIVE_BOTTOM_BUTTON_MAP[uid_s] = btn_map
    return rk


def _record_and_return_sent(chat_id, sent_msg, track_ui=True):
    if sent_msg is not None and getattr(sent_msg, "message_id", None) and track_ui:
        track_ui_message(str(chat_id), int(sent_msg.message_id))
    return sent_msg


DURABLE_NOTIFICATION_MSG_KEYS = {
    "withdraw_success_msg",
    "withdraw_paid_msg",
    "withdraw_rejected_msg",
    "video_bot_approved_msg",
    "video_admin_approved_msg",
    "video_permanent_approved_msg",
    "video_counting_completed_msg",
    "video_rejected_msg",
    "video_qualification_expired_msg",
    "video_review_needed_msg",
    "video_deleted_freeze_msg",
    "bio_removed_freeze_msg",
    "video_code_removed_freeze_msg",
    "ch_banned_msg",
    "ch_frozen_msg",
    "ch_inactive_msg",
    "suspicious_video_alert_msg",
    "external_link_admin_alert_msg",
    "manual_verify_admin_alert_msg",
}


def is_durable_notification_message(msg_key: str = None, text: str = "") -> bool:
    """
    Identifies permanent/durable messages (payment receipts, withdrawal confirmations,
    video approval/rejection alerts, bonus credits, security/freeze warnings) that must
    NEVER be auto-deleted by UI cleanup (`P1-17`).
    """
    if msg_key and str(msg_key) in DURABLE_NOTIFICATION_MSG_KEYS:
        return True
    s = str(text or "")
    durable_markers = (
        "নতুন রেফারেল বোনাস!",
        "ভিউ মাইলস্টোন বোনাস যুক্ত হয়েছে!",
        "আপনার উইথড্র রিকোয়েস্ট",
        "উইথড্র পেমেন্ট সফলভাবে সম্পন্ন",
        "অ্যাকাউন্ট সাময়িকভাবে ফ্রিজ",
        "সন্দেহজনক ভিডিও",
        "এক্সটার্নাল লিংক শনাক্ত",
        "ম্যানুয়াল ভেরিফিকেশন রিকোয়েস্টটি অ্যাডমিন প্যানেল থেকে রিজেক্ট",
    )
    return any(m in s for m in durable_markers)


def safe_send(
    chat_id,
    text,
    reply_markup=None,
    disable_preview=True,
    top_yt_url=None,
    menu_id=None,
    include_admin_guide=False,
    entities=None,
    msg_key=None,
    track_ui=True,
    auto_clean_prev=True
):
    eff_mk = msg_key or getattr(_THREAD_MSG_CTX, "last_msg_key", None)
    try:
        _THREAD_MSG_CTX.last_msg_key = None
    except Exception:
        pass
    if is_durable_notification_message(eff_mk, text):
        track_ui = False
        auto_clean_prev = False
    if auto_clean_prev and track_ui and chat_id and not str(chat_id).startswith("-"):
        cleanup_user_ui_messages(chat_id, str(chat_id), min_age_sec=0.35)
    eff_markup = apply_message_button_customization(eff_mk, reply_markup) if eff_mk else reply_markup
    if should_convert_markup_to_bottom_menu(chat_id, eff_markup, menu_id=menu_id):
        eff_markup = convert_inline_to_bottom_reply_keyboard(str(chat_id), eff_markup)

    prepared = prepare_outgoing(text, reply_markup=eff_markup, menu_id=menu_id, include_admin_guide=include_admin_guide)
    preview_kwargs = build_link_preview_options(top_yt_url=top_yt_url, disable_preview=disable_preview)
    std_preview_kwargs = {"disable_web_page_preview": False if (top_yt_url and str(top_yt_url).lower() not in ("none", "nane")) else bool(disable_preview)}
    eff_entities = entities if entities is not None else (prepared["entities"] if (prepared["has_custom_emoji"] and _BOT_DELIVERY_CAPS.get("custom_emoji_entities", True)) else None)
    rich_html = prepared["html_text"]
    html_fallback = strip_tg_emoji_tags(rich_html)
    kb_full = prepared["reply_markup"]

    # 1. Primary path: parse_mode="HTML" keeping 100% of <tg-emoji emoji-id="..."> AND full button custom emoji + color style!
    if _BOT_DELIVERY_CAPS.get("custom_emoji_html", True):
        for kb_cand, prev_kw in (
            (kb_full, preview_kwargs),
            (kb_full, std_preview_kwargs),
            (_strip_color_keep_emoji_keyboard(kb_full), std_preview_kwargs),
            (_strip_emoji_keep_color_keyboard(kb_full), std_preview_kwargs),
            (_downgrade_keyboard_to_standard(kb_full), std_preview_kwargs),
        ):
            try:
                return _record_and_return_sent(chat_id, bot.send_message(
                    chat_id,
                    rich_html,
                    parse_mode="HTML",
                    entities=None,
                    reply_markup=kb_cand,
                    **prev_kw
                ), track_ui=track_ui)
            except Exception as e_html:
                _adapt_caps_from_error(e_html)
                err_s = str(e_html or "").lower()
                # If the error is solely link_preview_options, next iteration retries kb_full with std_preview_kwargs!
                if "link_preview_options" in err_s:
                    continue
                # If the error is a message HTML/entity parse error (not a button error), break to try entities path
                if any(k in err_s for k in ("can't parse entities", "entity", "tag")) and "button" not in err_s:
                    break

    # 2. Secondary path: explicit UTF-16 `entities` (still keeping 100% of custom_emoji in message AND buttons!)
    if eff_entities:
        for kb_cand in (
            kb_full,
            _strip_color_keep_emoji_keyboard(kb_full),
            _strip_emoji_keep_color_keyboard(kb_full),
            _downgrade_keyboard_to_standard(kb_full),
        ):
            try:
                return _record_and_return_sent(chat_id, bot.send_message(
                    chat_id,
                    prepared["plain_text"],
                    parse_mode=None,
                    entities=eff_entities,
                    reply_markup=kb_cand,
                    **std_preview_kwargs
                ), track_ui=track_ui)
            except Exception as e_ent:
                _adapt_caps_from_error(e_ent)

    # 3. Last-resort fallback only if Telegram rejected custom_emoji in the message itself
    for kb_cand in (
        kb_full,
        _strip_emoji_keep_color_keyboard(kb_full),
        _downgrade_keyboard_to_standard(kb_full),
    ):
        try:
            return _record_and_return_sent(chat_id, bot.send_message(
                chat_id,
                html_fallback,
                parse_mode="HTML",
                entities=None,
                reply_markup=kb_cand,
                **std_preview_kwargs
            ), track_ui=track_ui)
        except Exception as e_fb:
            _adapt_caps_from_error(e_fb)

    try:
        return _record_and_return_sent(chat_id, bot.send_message(
            chat_id,
            prepared["plain_text"],
            parse_mode="",
            entities=None,
            reply_markup=_downgrade_keyboard_to_standard(kb_full),
            **std_preview_kwargs
        ), track_ui=track_ui)
    except Exception as e_final:
        _adapt_caps_from_error(e_final)
        return None


def safe_edit(
    chat_id,
    message_id,
    text,
    reply_markup=None,
    disable_preview=True,
    top_yt_url=None,
    menu_id=None,
    include_admin_guide=False,
    entities=None,
    msg_key=None
):
    eff_mk = msg_key or getattr(_THREAD_MSG_CTX, "last_msg_key", None)
    try:
        _THREAD_MSG_CTX.last_msg_key = None
    except Exception:
        pass
    reply_markup = apply_message_button_customization(eff_mk, reply_markup) if eff_mk else reply_markup
    use_bottom_kb = should_convert_markup_to_bottom_menu(chat_id, reply_markup, menu_id=menu_id)
    if (
        not message_id
        or use_bottom_kb
        or (reply_markup is not None and getattr(reply_markup, "__class__", None).__name__ in ("ReplyKeyboardMarkup", "ReplyKeyboardRemove"))
    ):
        if message_id and use_bottom_kb:
            try:
                bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            except Exception:
                pass
        return safe_send(
            chat_id,
            text,
            reply_markup=reply_markup,
            disable_preview=disable_preview,
            top_yt_url=top_yt_url,
            menu_id=menu_id,
            include_admin_guide=include_admin_guide,
            entities=entities
        )
    if chat_id and message_id and not str(chat_id).startswith("-"):
        track_ui_message(str(chat_id), int(message_id))
    prepared = prepare_outgoing(text, reply_markup=reply_markup, menu_id=menu_id, include_admin_guide=include_admin_guide)
    preview_kwargs = build_link_preview_options(top_yt_url=top_yt_url, disable_preview=disable_preview)
    std_preview_kwargs = {"disable_web_page_preview": False if (top_yt_url and str(top_yt_url).lower() not in ("none", "nane")) else bool(disable_preview)}
    eff_entities = entities if entities is not None else (prepared["entities"] if (prepared["has_custom_emoji"] and _BOT_DELIVERY_CAPS.get("custom_emoji_entities", True)) else None)
    rich_html = prepared["html_text"]
    html_fallback = strip_tg_emoji_tags(rich_html)
    kb_full = prepared["reply_markup"]

    # 1. Primary path: parse_mode="HTML" keeping 100% of <tg-emoji emoji-id="..."> AND full button custom emoji + color style!
    if _BOT_DELIVERY_CAPS.get("custom_emoji_html", True):
        for kb_cand, prev_kw in (
            (kb_full, preview_kwargs),
            (kb_full, std_preview_kwargs),
            (_strip_color_keep_emoji_keyboard(kb_full), std_preview_kwargs),
            (_strip_emoji_keep_color_keyboard(kb_full), std_preview_kwargs),
            (_downgrade_keyboard_to_standard(kb_full), std_preview_kwargs),
        ):
            try:
                return bot.edit_message_text(
                    rich_html,
                    chat_id,
                    message_id,
                    parse_mode="HTML",
                    entities=None,
                    reply_markup=kb_cand,
                    **prev_kw
                )
            except Exception as e_html:
                err_s = str(e_html or "").lower()
                if "message is not modified" in err_s:
                    return None
                if any(k in err_s for k in ("message to edit not found", "message can't be edited", "message_id_invalid")):
                    return safe_send(
                        chat_id, text, reply_markup=reply_markup, disable_preview=disable_preview,
                        top_yt_url=top_yt_url, menu_id=menu_id, include_admin_guide=include_admin_guide, entities=eff_entities
                    )
                _adapt_caps_from_error(e_html)
                if "link_preview_options" in err_s:
                    continue
                if any(k in err_s for k in ("can't parse entities", "entity", "tag")) and "button" not in err_s:
                    break

    # 2. Secondary path: explicit UTF-16 `entities`
    if eff_entities:
        for kb_cand in (
            kb_full,
            _strip_color_keep_emoji_keyboard(kb_full),
            _strip_emoji_keep_color_keyboard(kb_full),
            _downgrade_keyboard_to_standard(kb_full),
        ):
            try:
                return bot.edit_message_text(
                    prepared["plain_text"],
                    chat_id,
                    message_id,
                    parse_mode=None,
                    entities=eff_entities,
                    reply_markup=kb_cand,
                    **std_preview_kwargs
                )
            except Exception as e_ent:
                err_s = str(e_ent or "").lower()
                if "message is not modified" in err_s:
                    return None
                _adapt_caps_from_error(e_ent)

    # 3. Last-resort fallback
    for kb_cand in (
        kb_full,
        _strip_emoji_keep_color_keyboard(kb_full),
        _downgrade_keyboard_to_standard(kb_full),
    ):
        try:
            return bot.edit_message_text(
                html_fallback,
                chat_id,
                message_id,
                parse_mode="HTML",
                entities=None,
                reply_markup=kb_cand,
                **std_preview_kwargs
            )
        except Exception as e_fb:
            err_s = str(e_fb or "").lower()
            if "message is not modified" in err_s:
                return None
            _adapt_caps_from_error(e_fb)

    return safe_send(
        chat_id,
        text,
        reply_markup=reply_markup,
        disable_preview=disable_preview,
        top_yt_url=top_yt_url,
        menu_id=menu_id,
        include_admin_guide=include_admin_guide,
        entities=eff_entities
    )


def _guard(action_name="callback", sensitive=False):
    def decorator(func):
        @wraps(func)
        def wrapper(call_or_msg, *args, **kwargs):
            if getattr(call_or_msg, "_guard_entered", False):
                return func(call_or_msg, *args, **kwargs)
            try:
                setattr(call_or_msg, "_guard_entered", True)
            except Exception:
                pass
            user_obj = getattr(call_or_msg, "from_user", None)
            uid = str(getattr(user_obj, "id", "0"))
            cb_data = str(getattr(call_or_msg, "data", "") or "")
            is_nav = bool(cb_data and is_navigation_callback(cb_data) and not sensitive)

            allowed, retry_s = check_rate_limit(
                uid,
                action=cb_data or action_name,
                max_calls=45 if is_nav else 10,
                window_sec=5 if is_nav else 10,
                is_navigation=is_nav
            )
            if not allowed:
                if hasattr(call_or_msg, "id"):
                    bot.answer_callback_query(call_or_msg.id, f"অনুগ্রহ করে {retry_s} সেকেন্ড অপেক্ষা করুন!", show_alert=True)
                return None

            if not is_nav and cb_data:
                if check_duplicate_callback(uid, cb_data, ttl_sec=USER_ACTION_COOLDOWN_SEC):
                    if hasattr(call_or_msg, "id"):
                        bot.answer_callback_query(call_or_msg.id, "প্রসেসিং চলছে...", show_alert=False)
                    return None

            if sensitive and not is_nav:
                if not acquire_flow_lock(uid, flow_key=action_name, ttl_sec=12.0):
                    if hasattr(call_or_msg, "id"):
                        bot.answer_callback_query(call_or_msg.id, "একটি কাজ চলমান রয়েছে, অনুগ্রহ করে অপেক্ষা করুন।", show_alert=True)
                    return None
                try:
                    return func(call_or_msg, *args, **kwargs)
                except Exception as exc:
                    print(f"[CALLBACK ERROR in {action_name}]: {exc}")
                    if hasattr(call_or_msg, "id"):
                        try:
                            bot.answer_callback_query(call_or_msg.id, "⚠️ সাময়িক ত্রুটি, আবার চেষ্টা করুন।", show_alert=False)
                        except Exception:
                            pass
                    return None
                finally:
                    release_flow_lock(uid, flow_key=action_name)
                    if hasattr(call_or_msg, "id"):
                        try:
                            bot.answer_callback_query(call_or_msg.id)
                        except Exception:
                            pass

            try:
                return func(call_or_msg, *args, **kwargs)
            except Exception as exc:
                print(f"[CALLBACK ERROR in {action_name}]: {exc}")
                if hasattr(call_or_msg, "id"):
                    try:
                        bot.answer_callback_query(call_or_msg.id, "⚠️ সাময়িক ত্রুটি, আবার চেষ্টা করুন।", show_alert=False)
                    except Exception:
                        pass
                return None
            finally:
                if hasattr(call_or_msg, "id"):
                    try:
                        bot.answer_callback_query(call_or_msg.id)
                    except Exception:
                        pass
        return wrapper
    return decorator


# ==============================================================================
# SETTINGS, CACHING & DYNAMIC CONFIGURATION
# ==============================================================================
def preload_all_caches():
    with db_lock:
        conn = get_connection()
        try:
            cleanup_orphan_custom_layouts_and_messages(conn=conn)
        except Exception:
            pass

        # Remove stale cbtn_* entries from in-memory caches before reloading
        active_cbtn_rows = conn.execute("SELECT * FROM custom_buttons").fetchall()
        active_cbtn_keys = {r["btn_key"] for r in active_cbtn_rows}
        active_cbtn_layouts = {r["layout_key"] for r in active_cbtn_rows}
        active_cbtn_msgs = {r["msg_key"] for r in active_cbtn_rows}

        for k_old in list(GLOBAL_BUTTON_CALLBACK_MAP.keys()):
            if (k_old.startswith("cbtn_") or k_old.endswith("_direct")) and k_old not in active_cbtn_keys:
                # Keep _direct only if its parent custom button still exists
                base_k = k_old[:-7] if k_old.endswith("_direct") else k_old
                if base_k not in active_cbtn_keys:
                    GLOBAL_BUTTON_CALLBACK_MAP.pop(k_old, None)
                    DEFAULT_BUTTON_LABELS.pop(k_old, None)
                    CACHE_LABELS.pop(k_old, None)
                    CACHE_STYLES.pop(k_old, None)
                    CACHE_DESIGNS.pop(k_old, None)
                    CACHE_BUTTON_EMOJIS.pop(k_old, None)

        for lk_old in list(CACHE_LAYOUTS.keys()):
            if str(lk_old).startswith("custom_page_") and lk_old not in active_cbtn_layouts:
                CACHE_LAYOUTS.pop(lk_old, None)
                DEFAULT_LAYOUTS.pop(lk_old, None)
                LAYOUT_PAGE_TITLES.pop(lk_old, None)

        for mk_old in list(CACHE_MESSAGES.keys()):
            if str(mk_old).startswith("custom_msg_") and mk_old not in active_cbtn_msgs:
                CACHE_MESSAGES.pop(mk_old, None)
                CACHE_MESSAGE_ENTITIES.pop(mk_old, None)

        for r in conn.execute("SELECT key, value FROM dynamic_settings").fetchall():
            CACHE_SETTINGS[r["key"]] = r["value"]
        CACHE_BUTTON_EMOJIS.clear()
        CACHE_BUTTON_LABEL_CUSTOMIZED.clear()
        CACHE_BUTTON_EMOJI_CUSTOMIZED.clear()
        CACHE_BUTTON_VISIBILITY.clear()
        CACHE_MESSAGE_BUTTON_MODES.clear()
        CACHE_MESSAGE_CUSTOM_BUTTONS.clear()
        try:
            for cb_row in active_cbtn_rows:
                bk = cb_row["btn_key"]
                GLOBAL_BUTTON_CALLBACK_MAP[bk] = f"cbtn_open:{bk}"
                norm_cb_lbl = ensure_visible_emoji_presentation(cb_row["label"])
                DEFAULT_BUTTON_LABELS[bk] = norm_cb_lbl
                CACHE_LABELS[bk] = norm_cb_lbl
                CACHE_BUTTON_LABEL_CUSTOMIZED.add(bk)
                if cb_row["style"]:
                    CACHE_STYLES[bk] = cb_row["style"]
                if cb_row["design_style"]:
                    CACHE_DESIGNS[bk] = cb_row["design_style"]
                if cb_row["custom_emoji_id"]:
                    CACHE_BUTTON_EMOJIS[bk] = str(cb_row["custom_emoji_id"]).strip()
                    CACHE_BUTTON_EMOJI_CUSTOMIZED.add(bk)
                LAYOUT_PAGE_TITLES[cb_row["layout_key"]] = f"📂 {norm_cb_lbl}"
                DEFAULT_LAYOUTS.setdefault(cb_row["layout_key"], [])
        except Exception:
            pass
        for r in conn.execute("SELECT * FROM button_labels").fetchall():
            rk = r.keys()
            bk = r["btn_key"]
            lbl_cust = int(r["label_customized"] or 0) if "label_customized" in rk else (1 if r["label"] else 0)
            em_cust = int(r["emoji_customized"] or 0) if "emoji_customized" in rk else (1 if ("icon_custom_emoji_id" in rk and r["icon_custom_emoji_id"]) else 0)
            is_vis = int(r["is_visible"] if ("is_visible" in rk and r["is_visible"] is not None) else 1)
            CACHE_BUTTON_VISIBILITY[bk] = bool(is_vis == 1)
            if lbl_cust == 1 or r["label"]:
                CACHE_LABELS[bk] = ensure_visible_emoji_presentation(r["label"] or "")
                CACHE_BUTTON_LABEL_CUSTOMIZED.add(bk)
            if "icon_custom_emoji_id" in rk:
                em_val = str(r["icon_custom_emoji_id"] or "").strip()
                if em_cust == 1 or em_val:
                    CACHE_BUTTON_EMOJIS[bk] = em_val
                    CACHE_BUTTON_EMOJI_CUSTOMIZED.add(bk)
            if "design_style" in rk and r["design_style"]:
                CACHE_DESIGNS[bk] = r["design_style"]
        for r in conn.execute("SELECT * FROM button_styles").fetchall():
            rk = r.keys()
            bk = r["btn_key"]
            if r["style"]:
                CACHE_STYLES[bk] = r["style"]
            if (
                "icon_custom_emoji_id" in rk
                and r["icon_custom_emoji_id"]
                and bk not in CACHE_BUTTON_EMOJI_CUSTOMIZED
                and not CACHE_BUTTON_EMOJIS.get(bk)
            ):
                CACHE_BUTTON_EMOJIS[bk] = str(r["icon_custom_emoji_id"]).strip()
            if "design_style" in rk and r["design_style"]:
                CACHE_DESIGNS[bk] = r["design_style"]
        for r in conn.execute("SELECT layout_key, structure_json FROM dynamic_layouts").fetchall():
            if r["layout_key"] in ALLOWED_DYNAMIC_LAYOUT_KEYS or str(r["layout_key"]).startswith("custom_page_"):
                try:
                    CACHE_LAYOUTS[r["layout_key"]] = json.loads(r["structure_json"])
                except Exception:
                    pass
        for r in conn.execute("SELECT * FROM dynamic_messages").fetchall():
            rk = r.keys()
            mk = r["msg_key"]
            c_val = str(r["content"] or "")
            if "<tg-emoji" not in c_val and r["raw_text"] and r["entities_json"]:
                try:
                    ents_l = json.loads(r["entities_json"] or "[]")
                    if any(isinstance(e, dict) and e.get("type") == "custom_emoji" for e in ents_l):
                        c_val = reconstruct_html_from_raw_and_entities(str(r["raw_text"]), ents_l) or c_val
                except Exception:
                    pass
            CACHE_MESSAGES[mk] = c_val
            b_mode = str((r["button_mode"] if "button_mode" in rk else "default") or "default").strip().lower()
            if b_mode not in ("default", "custom", "none"):
                b_mode = "default"
            CACHE_MESSAGE_BUTTON_MODES[mk] = b_mode
            if "custom_buttons_json" in rk and r["custom_buttons_json"]:
                try:
                    c_btns = json.loads(r["custom_buttons_json"] or "[]")
                    if isinstance(c_btns, list):
                        CACHE_MESSAGE_CUSTOM_BUTTONS[mk] = c_btns
                except Exception:
                    pass
        conn.close()
try:
    init_db()
    preload_all_caches()
except Exception as _init_exc:
    print(f"[INIT WARNING]: {_init_exc}")


def get_setting(key: str, default=None):
    if key in CACHE_SETTINGS and CACHE_SETTINGS[key] is not None:
        return CACHE_SETTINGS[key]
    val = get_setting_db(key)
    if val is not None:
        CACHE_SETTINGS[key] = val
        return val
    return DEFAULT_SETTINGS.get(key, default)


def get_setting_db(key: str):
    with db_lock:
        conn = get_connection()
        row = conn.execute("SELECT value FROM dynamic_settings WHERE key = ?", (key,)).fetchone()
        conn.close()
    return row["value"] if row else None


def set_setting_val(key: str, value: str):
    CACHE_SETTINGS[key] = str(value)
    set_setting(key, str(value))


def get_btn_raw_label(btn_key: str, lang: str = "bn") -> str:
    if btn_key in CACHE_BUTTON_LABEL_CUSTOMIZED or (btn_key in CACHE_LABELS and CACHE_LABELS[btn_key] != ""):
        return CACHE_LABELS.get(btn_key, "")
    if str(lang or "bn").lower() == "en" and btn_key in DEFAULT_BUTTON_LABELS_EN:
        return DEFAULT_BUTTON_LABELS_EN[btn_key]
    return DEFAULT_BUTTON_LABELS.get(btn_key, btn_key)


def is_btn_label_admin_customized(btn_key: str) -> bool:
    return btn_key in CACHE_BUTTON_LABEL_CUSTOMIZED


def get_btn_visibility(btn_key: str) -> bool:
    return bool(CACHE_BUTTON_VISIBILITY.get(btn_key, True))


def set_btn_visibility_val(btn_key: str, is_visible: bool):
    vis = bool(is_visible)
    CACHE_BUTTON_VISIBILITY[btn_key] = vis
    with db_lock:
        set_button_visibility(btn_key, vis)


def get_btn_design(btn_key: str) -> str:
    return CACHE_DESIGNS.get(btn_key, "normal") or "normal"


def set_btn_design_val(btn_key: str, design_style: str):
    st = str(design_style or "normal").strip()
    if st not in BUTTON_TEXT_DESIGN_STYLES:
        st = "normal"
    CACHE_DESIGNS[btn_key] = st
    with db_lock:
        set_button_design_style(btn_key, st)


def get_btn_label(btn_key: str, lang: str = "bn", apply_design: bool = False) -> str:
    base_lbl = get_btn_raw_label(btn_key, lang=lang)
    if apply_design:
        return apply_button_text_design(base_lbl, get_btn_design(btn_key))
    return base_lbl


def set_btn_label_val(btn_key: str, label: str):
    CACHE_LABELS[btn_key] = str(label)
    CACHE_BUTTON_LABEL_CUSTOMIZED.add(btn_key)
    set_btn_label(btn_key, str(label))


def get_btn_emoji(btn_key: str) -> str:
    if btn_key in CACHE_BUTTON_EMOJI_CUSTOMIZED or btn_key in CACHE_BUTTON_EMOJIS:
        return str(CACHE_BUTTON_EMOJIS.get(btn_key, "") or "")
    return DEFAULT_BUTTON_EMOJIS.get(btn_key, "")


def set_btn_emoji_val(btn_key: str, emoji_id: str):
    clean_id = re.sub(r"[^0-9]", "", str(emoji_id or "").strip())
    CACHE_BUTTON_EMOJIS[btn_key] = clean_id
    CACHE_BUTTON_EMOJI_CUSTOMIZED.add(btn_key)
    if clean_id:
        BUTTON_RUNTIME_CAPS["allow_custom_emoji"] = True
    with db_lock:
        set_button_custom_emoji(btn_key, clean_id)


def reset_single_button_to_default(btn_key: str):
    bk = str(btn_key or "").strip()
    CACHE_LABELS.pop(bk, None)
    CACHE_BUTTON_EMOJIS.pop(bk, None)
    CACHE_STYLES.pop(bk, None)
    CACHE_DESIGNS.pop(bk, None)
    CACHE_BUTTON_VISIBILITY.pop(bk, None)
    CACHE_BUTTON_LABEL_CUSTOMIZED.discard(bk)
    CACHE_BUTTON_EMOJI_CUSTOMIZED.discard(bk)
    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute("DELETE FROM button_labels WHERE btn_key = ?", (bk,))
            conn.execute("DELETE FROM button_styles WHERE btn_key = ?", (bk,))
        conn.close()


def get_btn_style(btn_key: str, u_style_override: str = None) -> str:
    if u_style_override in ("success", "danger", "primary") and str(btn_key).startswith("u_"):
        return u_style_override
    if btn_key in CACHE_STYLES and CACHE_STYLES[btn_key] in ("success", "danger", "primary"):
        return CACHE_STYLES[btn_key]
    return get_setting("global_admin_theme", "primary") if str(btn_key).startswith("a_") else get_setting("global_user_theme", "success")


def set_btn_style_val(btn_key: str, style: str):
    CACHE_STYLES[btn_key] = str(style)
    set_btn_style(btn_key, str(style))


def get_layout_val(layout_key: str) -> list:
    return get_layout(layout_key)


def set_layout_val(layout_key: str, structure: list):
    set_layout(layout_key, structure)


def get_msg(msg_key: str, lang: str = "bn", **kwargs):
    is_en = str(lang or "bn").lower() == "en"
    default_tpl = DEFAULT_MESSAGES_EN.get(msg_key, DEFAULT_MESSAGES.get(msg_key, "")) if is_en else DEFAULT_MESSAGES.get(msg_key, "")
    template = CACHE_MESSAGES.get(msg_key)
    if not template:
        rec = get_dynamic_message_record(msg_key)
        c_db = str(rec.get("content") or "")
        if "<tg-emoji" not in c_db and rec.get("raw_text") and rec.get("entities"):
            try:
                if any(isinstance(e, dict) and e.get("type") == "custom_emoji" for e in rec["entities"]):
                    c_db = reconstruct_html_from_raw_and_entities(str(rec["raw_text"]), rec["entities"]) or c_db
            except Exception:
                pass
        if c_db:
            template = c_db
            CACHE_MESSAGES[msg_key] = c_db
        else:
            template = default_tpl
    res = str(template or default_tpl or "")
    fallback_res = str(default_tpl or "")
    for k, v in kwargs.items():
        res = res.replace("{" + str(k) + "}", str(v))
        fallback_res = fallback_res.replace("{" + str(k) + "}", str(v))
    cleaned_res = strip_legacy_action_routes(res)
    cleaned_fallback = strip_legacy_action_routes(fallback_res)
    try:
        _THREAD_MSG_CTX.last_msg_key = str(msg_key or "")
    except Exception:
        pass
    return repair_or_fallback_html(cleaned_res, cleaned_fallback)


def apply_message_button_customization(msg_key: str, reply_markup=None):
    """
    Applies Admin-configured per-message button customization (Section 4):
    - `button_mode == 'none'`: returns `None` (Buttonless message customization).
    - `button_mode == 'custom'`: attaches Admin-configured custom buttons (`CACHE_MESSAGE_CUSTOM_BUTTONS[msg_key]`).
    - `button_mode == 'default'`: returns `reply_markup` unchanged.
    """
    if reply_markup is not None and getattr(reply_markup, "_custom_btns_applied", False):
        return reply_markup
    mk = str(msg_key or "").strip()
    if not mk:
        return reply_markup
    b_mode = CACHE_MESSAGE_BUTTON_MODES.get(mk, "default")
    if b_mode == "none":
        return None
    if b_mode == "custom":
        c_rows = CACHE_MESSAGE_CUSTOM_BUTTONS.get(mk) or []
        if not c_rows:
            return reply_markup
        kb = types.InlineKeyboardMarkup()
        if reply_markup is not None and hasattr(reply_markup, "keyboard"):
            for r in reply_markup.keyboard:
                if r:
                    kb.row(*r)
        for row in c_rows:
            if not isinstance(row, list):
                continue
            r_btns = []
            for item in row:
                if not isinstance(item, dict):
                    continue
                lbl = str(item.get("text") or "Button").strip()
                target = str(item.get("target") or item.get("url") or item.get("callback_data") or "").strip()
                st_col = str(item.get("style") or "primary").strip()
                em_id = str(item.get("icon_custom_emoji_id") or "").strip()
                if not lbl or not target:
                    continue
                if target.startswith(("http://", "https://", "tg://")):
                    r_btns.append(make_btn(lbl, url=target, style=st_col, icon_custom_emoji_id=em_id or None))
                else:
                    cb_val = GLOBAL_BUTTON_CALLBACK_MAP.get(target, target)
                    r_btns.append(make_btn(lbl, callback_data=cb_val, style=st_col, icon_custom_emoji_id=em_id or None))
            if r_btns:
                kb.row(*r_btns)
        try:
            kb._custom_btns_applied = True
        except Exception:
            pass
        return kb
    if reply_markup is not None:
        try:
            reply_markup._custom_btns_applied = True
        except Exception:
            pass
    return reply_markup


def set_msg_val(msg_key: str, content: str, raw_text: str = "", entities: list = None, updated_by="admin"):
    CACHE_MESSAGES[msg_key] = content
    save_dynamic_message_record(msg_key, content, raw_text=raw_text, entities=entities, updated_by=updated_by)


# ==============================================================================
# USER & ADMIN HELPERS
# ==============================================================================
def get_user(user_id: str) -> dict:
    with db_lock:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),)).fetchone()
        conn.close()
    return dict(row) if row else None


def get_user_label(u: dict) -> str:
    if not u:
        return "Unknown"
    if u.get("username"):
        return f"@{u['username'].lstrip('@')}"
    if u.get("name"):
        return u["name"]
    if u.get("phone"):
        return u["phone"]
    return f"User-{str(u.get('user_id', ''))[-4:]}"


def get_user_saved_numbers_list(u: dict, method: str) -> list:
    """Returns up to 2 saved numbers/UIDs for `method` ('bKash', 'Nagad', 'Rocket', 'BattleClub_UID')."""
    if not u:
        return []
    m = str(method or "").strip()
    if m == "BattleClub_UID":
        return parse_multi_app_uids(u.get("app_uid") or "", max_items=2)
    col_map = {"bKash": "bkash_number", "Nagad": "nagad_number", "Rocket": "rocket_number"}
    col = col_map.get(m, "phone")
    raw_v = str(u.get(col) or "").strip()
    if not raw_v and m == "bKash":
        raw_v = str(u.get("phone") or "").strip()
    return parse_multi_payment_numbers(raw_v, allow_rocket_12=(m == "Rocket"), max_items=2)


def format_user_payment_numbers_summary(u: dict) -> str:
    """Formats a user's saved bKash, Nagad, Rocket numbers (up to 2 per method) for Dashboard & Profile."""
    if not u:
        return "N/A"
    parts = []
    bk_list = get_user_saved_numbers_list(u, "bKash")
    ng_list = get_user_saved_numbers_list(u, "Nagad")
    rk_list = get_user_saved_numbers_list(u, "Rocket")
    ph = str(u.get("phone") or "").strip()
    if bk_list:
        parts.append(f"বিকাশ: {', '.join(bk_list)}")
    if ng_list:
        parts.append(f"নগদ: {', '.join(ng_list)}")
    if rk_list:
        parts.append(f"রকেট: {', '.join(rk_list)}")
    if not parts and ph:
        parts.append(ph)
    return " | ".join(parts) if parts else (ph or "N/A")


def format_user_platform_channel_names(u: dict, plats: list = None) -> str:
    """Formats the user's YouTube & TikTok channel names for Dashboard & Profile."""
    if not u:
        return "N/A"
    yt_n = str(u.get("youtube_channel_name") or "").strip()
    tt_n = str(u.get("tiktok_channel_name") or "").strip()
    ch_n = str(u.get("channel_name") or "").strip()
    if plats:
        for p in plats:
            pk = str(p.get("platform") or "").lower()
            dn = str(p.get("display_name") or "").strip()
            if pk == "youtube" and not yt_n and dn:
                yt_n = dn
            elif pk == "tiktok" and not tt_n and dn:
                tt_n = dn
    parts = []
    if yt_n:
        parts.append(f"YouTube: {yt_n}")
    if tt_n:
        parts.append(f"TikTok: {tt_n}")
    if parts:
        return " | ".join(parts)
    return ch_n or "N/A"


def get_user_saved_number_for_method(u: dict, method: str, slot_index: int = None) -> str:
    if not u:
        return ""
    nums = get_user_saved_numbers_list(u, method)
    if not nums:
        return ""
    if slot_index is not None:
        if 0 <= int(slot_index) < len(nums):
            return nums[int(slot_index)]
        return nums[0]
    return nums[0]


def get_user_selected_mobile_methods(u: dict) -> list:
    """
    Returns ONLY the mobile payment methods (`bKash`, `Nagad`, `Rocket`) for which the user
    has actually saved a payment number during registration or via Profile (with Admin random code).
    """
    if not u:
        return ["bKash"]
    saved_methods = []
    for m, col in (("bKash", "bkash_number"), ("Nagad", "nagad_number"), ("Rocket", "rocket_number")):
        if str(u.get(col) or "").strip() and m not in saved_methods:
            saved_methods.append(m)
    if saved_methods:
        return saved_methods
    if str(u.get("phone") or "").strip():
        return ["bKash"]
    raw_sel = u.get("selected_payment_methods")
    if raw_sel:
        try:
            parsed = json.loads(raw_sel) if isinstance(raw_sel, str) else list(raw_sel)
            for m in parsed:
                if m in ("bKash", "Nagad", "Rocket") and m not in saved_methods:
                    saved_methods.append(m)
        except Exception:
            pass
    return saved_methods


def _format_boxed_activity_logs(logs: list) -> str:
    if not logs:
        return "╭────────────────────────────╮\n│ 📭 কোনো সাম্প্রতিক কার্যক্রম লগ নেই।\n╰────────────────────────────╯"
    boxes = []
    for idx, r in enumerate(logs, start=1):
        act_raw = str(r["action"] or "Activity")
        det_raw = str(r["details"] or "")
        ts_raw = str(r["created_at"] or "")
        d_s, t_s = _split_datetime_str(ts_raw)
        try:
            act_bn = _translate_audit_action_bn(act_raw)
        except Exception:
            act_bn = act_raw
        boxes.append(
            f"╭─ 🔹 <b>#{idx}. {esc(act_bn)}</b>\n"
            f"│ 📝 বিবরণ: {esc(det_raw)}\n"
            f"╰─ 📅 তারিখ: <code>{esc(d_s)}</code> | 🕒 সময়: <code>{esc(t_s)}</code>"
        )
    return "\n\n".join(boxes)


def ensure_user(user_obj) -> dict:
    uid = str(user_obj.id)
    uname = (user_obj.username or "").strip().lower().lstrip("@")
    full_name = f"{getattr(user_obj, 'first_name', '') or ''} {getattr(user_obj, 'last_name', '') or ''}".strip() or "Creator"
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    with db_lock:
        conn = get_connection()
        with conn:
            row = conn.execute("SELECT * FROM users WHERE user_id = ?", (uid,)).fetchone()
            if not row:
                bio_c = generate_unique_bc_code("bio_verify", user_id=uid, conn=conn)
                vid_c = generate_unique_bc_code("video_submit", user_id=uid, conn=conn)
                u_code = f"BC-{uid[-6:]}"
                ref_c = generate_referral_code(uid)
                conn.execute("""
                    INSERT INTO users (
                        user_id, username, name, unique_code, referral_code, bio_verify_code, bio_code_generated_ts,
                        active_video_code, registered, session_logged_out, last_active_ts, status, joined_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 'active', ?)
                """, (uid, uname, full_name, u_code, ref_c, bio_c, now_ts, vid_c, now_ts, now_str))
            else:
                cur_bio = str(row["bio_verify_code"] or "").strip()
                cur_vid = str(row["active_video_code"] or "").strip()
                if not cur_bio or not cur_bio.upper().startswith("BC-"):
                    cur_bio = generate_unique_bc_code("bio_verify", user_id=uid, conn=conn)
                    conn.execute("UPDATE users SET bio_verify_code = ? WHERE user_id = ?", (cur_bio, uid))
                if not cur_vid or not cur_vid.upper().startswith("BC-"):
                    cur_vid = generate_unique_bc_code("video_submit", user_id=uid, conn=conn)
                    conn.execute("UPDATE users SET active_video_code = ? WHERE user_id = ?", (cur_vid, uid))
                has_real_reg = int(row["registered"] or 0) == 1 and bool(str(row["password_hash"] or row["password_plain"] or "").strip())
                if not has_real_reg and int(row["registered"] or 0) == 1:
                    conn.execute("UPDATE users SET username = ?, registered = 0, last_active_ts = ? WHERE user_id = ?", (uname, now_ts, uid))
                else:
                    conn.execute("UPDATE users SET username = ?, last_active_ts = ? WHERE user_id = ?", (uname, now_ts, uid))
        conn.close()
    return get_user(uid)


def is_authorized_admin(user_or_uid) -> bool:
    """
    Strictly verifies admin authorization by immutable numeric Telegram user ID ONLY (P0-01).
    Never trusts mutable Telegram usernames (`super_admin_usernames`) to grant admin privileges.
    """
    if hasattr(user_or_uid, "id"):
        uid = str(user_or_uid.id).strip()
    else:
        uid = str(user_or_uid or "").strip()
    if not uid or not uid.isdigit():
        return False
    if SUPER_ADMIN_ID and str(SUPER_ADMIN_ID).strip().isdigit() and uid == str(SUPER_ADMIN_ID).strip():
        return True
    adm_raw = get_setting("admins", "8145274317")
    adm_list = [x.strip() for x in str(adm_raw or "").split(",") if x.strip().isdigit()]
    return uid in adm_list


def is_admin_unlocked(user_or_uid) -> bool:
    """
    Verifies both (1) numeric Admin ID authorization AND (2) an active, non-expired password-unlocked admin session.
    """
    if hasattr(user_or_uid, "id"):
        uid = str(user_or_uid.id).strip()
    else:
        uid = str(user_or_uid or "").strip()
    if not is_authorized_admin(uid):
        admin_unlocked_sessions.pop(uid, None)
        try:
            lock_admin_session(uid)
        except Exception:
            pass
        return False
    now_t = time.time()
    ttl_sec = max(60, int(get_setting("admin_session_timeout_sec", "3600") or 3600))
    ts_val = admin_unlocked_sessions.get(uid)
    if ts_val:
        ts_f = float(ts_val)
        if 0 < ts_f <= now_t + 5 and (now_t - ts_f) < ttl_sec:
            return True
        admin_unlocked_sessions.pop(uid, None)
        try:
            lock_admin_session(uid)
        except Exception:
            pass
        return False
    if is_admin_session_unlocked(uid):
        admin_unlocked_sessions[uid] = now_t
        return True
    return False


def require_unlocked_admin_session(call_or_msg) -> bool:
    """
    Enforces numeric Admin ID + active password-unlocked session on all privileged admin callbacks/commands (P0-01).
    Never auto-creates a session inside a callback handler!
    """
    user_obj = getattr(call_or_msg, "from_user", None)
    uid = str(getattr(user_obj, "id", "") or "").strip()
    is_cb = hasattr(call_or_msg, "data")
    chat_id = getattr(getattr(call_or_msg, "message", None), "chat", None)
    chat_id = getattr(chat_id, "id", None) if chat_id else getattr(getattr(call_or_msg, "chat", None), "id", None)
    if not is_authorized_admin(user_obj):
        if is_cb:
            bot.answer_callback_query(call_or_msg.id, "⛔ শুধুমাত্র অনুমোদিত অ্যাডমিন আইডি এই বাটন ব্যবহার করতে পারবেন!", show_alert=True)
        return False
    if not is_admin_unlocked(uid):
        user_memory_states[uid] = {"step": "awaiting_admin_password", "pending_admin_cb": getattr(call_or_msg, "data", "") if is_cb else ""}
        if is_cb:
            bot.answer_callback_query(call_or_msg.id, "🔐 সুপার অ্যাডমিন প্যানেলে প্রবেশ করতে আপনার অ্যাডমিন পাসওয়ার্ড লিখে পাঠান!", show_alert=True)
        if chat_id:
            safe_send(chat_id, "🔐 <b>অ্যাডমিন সেশন লক রয়েছে!</b>\nসুপার অ্যাডমিন প্যানেলে প্রবেশ করতে আপনার গোপন <b>অ্যাডমিন পাসওয়ার্ড</b> লিখে পাঠান:")
        return False
    ttl_sec = max(60, int(get_setting("admin_session_timeout_sec", "3600") or 3600))
    admin_unlocked_sessions[uid] = time.time()
    try:
        touch_admin_session(uid, ttl_sec=ttl_sec)
    except Exception:
        pass
    return True


def get_all_admin_ids() -> list:
    adm_raw = get_setting("admins", "8145274317")
    adm_ids = set([int(x.strip()) for x in str(adm_raw or "").split(",") if x.strip().isdigit()])
    if SUPER_ADMIN_ID and str(SUPER_ADMIN_ID).strip().isdigit():
        adm_ids.add(int(str(SUPER_ADMIN_ID).strip()))
    return sorted(list(adm_ids))


def check_user_session_lock(chat_id, user_obj, call_id=None) -> bool:
    uid = str(user_obj.id)
    u = get_user(uid) or ensure_user(user_obj)
    if not u or not u.get("registered") or not (u.get("password_hash") or u.get("password_plain")):
        return True

    if is_admin_unlocked(uid):
        return True

    now_ts = time.time()
    last_ts = float(u.get("last_active_ts", 0) or 0)
    if last_ts > now_ts + 60:
        last_ts = now_ts
    timeout_limit = int(get_setting("user_session_timeout_sec", "600"))
    already_logged_out = bool(int(u.get("session_logged_out") or 0) == 1)
    timed_out_now = bool(not already_logged_out and last_ts > 0 and (now_ts - last_ts) >= timeout_limit)

    if already_logged_out or timed_out_now:
        was_notified = bool(int(u.get("timeout_notified") or 0) == 1)
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET session_logged_out = 1, timeout_notified = 1 WHERE user_id = ?", (uid,))
            conn.close()
        user_memory_states[uid] = {"step": "awaiting_session_password"}
        if call_id:
            bot.answer_callback_query(call_id, "🔐 ড্যাশবোর্ডে প্রবেশ করতে আপনার পাসওয়ার্ড লিখে পাঠান!", show_alert=True)
        if timed_out_now and not was_notified:
            safe_send(chat_id, get_msg("session_logout_msg"))
        else:
            safe_send(chat_id, get_msg("login_password_prompt_msg"))
        return False

    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute("UPDATE users SET last_active_ts = ?, timeout_notified = 0 WHERE user_id = ?", (now_ts, uid))
        conn.close()
    return True


def check_user_cooldown(u: dict) -> tuple:
    cd_ts = float(u.get("cooldown_until_ts", 0) or 0)
    now_ts = time.time()
    if cd_ts > now_ts:
        rem_hr = round((cd_ts - now_ts) / 3600.0, 1)
        strike_lim = int(get_setting("strike_limit", "3"))
        return True, f"⏳ <b>সাবমিশন কুলডাউন!</b> পরপর {strike_lim} বার নিয়ম ভঙ্গের কারণে আপনার ভিডিও সাবমিশন সাময়িক ব্লক রয়েছে। অবশিষ্ট সময়: <b>{rem_hr} ঘণ্টা</b>।"
    return False, ""


# ==============================================================================
# CORE DB-BACKED SETTINGS, BUTTON, LAYOUT & MESSAGE HELPERS
# ==============================================================================
def set_setting(key: str, value: str):
    clean_v = validate_setting_value(key, value)
    with db_lock:
        db_set_setting(key, str(clean_v))
    CACHE_SETTINGS[key] = str(clean_v)
    if key in ("rate_per_1k", "first_1000_views_payment"):
        CACHE_SETTINGS["first_1000_views_payment"] = str(clean_v)
        CACHE_SETTINGS["rate_per_1k"] = str(clean_v)
        m_init = max(1, int(float(CACHE_SETTINGS.get("min_initial_views") or 1000)))
        st_sz = max(1, int(float(CACHE_SETTINGS.get("view_step_size") or 200)))
        CACHE_SETTINGS["every_200_views_payment"] = str(round((float(clean_v) / float(m_init)) * st_sz, 4))
    elif key == "earning_duration_days":
        CACHE_SETTINGS["view_tracking_days"] = str(clean_v)
    elif key == "view_tracking_days":
        CACHE_SETTINGS["earning_duration_days"] = str(clean_v)


def set_btn_label(btn_key: str, label: str):
    norm_lbl = ensure_visible_emoji_presentation(str(label or "").strip())
    CACHE_LABELS[btn_key] = norm_lbl
    CACHE_BUTTON_LABEL_CUSTOMIZED.add(btn_key)
    if str(btn_key).startswith("cbtn_"):
        DEFAULT_BUTTON_LABELS[btn_key] = norm_lbl
    emoji_id = get_btn_emoji(btn_key)
    design_st = get_btn_design(btn_key)
    em_cust = 1 if (btn_key in CACHE_BUTTON_EMOJI_CUSTOMIZED or emoji_id) else 0
    vis_int = 1 if get_btn_visibility(btn_key) else 0
    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO button_labels (btn_key, label, icon_custom_emoji_id, design_style, label_customized, emoji_customized, is_visible) VALUES (?, ?, ?, ?, 1, ?, ?)",
                (btn_key, norm_lbl, emoji_id, design_st, em_cust, vis_int)
            )
            conn.execute(
                "UPDATE custom_buttons SET label = ?, custom_emoji_id = ?, design_style = ? WHERE btn_key = ?",
                (norm_lbl, emoji_id, design_st, btn_key)
            )
        conn.close()


def set_btn_style(btn_key: str, style: str):
    CACHE_STYLES[btn_key] = str(style)
    emoji_id = get_btn_emoji(btn_key)
    design_st = get_btn_design(btn_key)
    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO button_styles (btn_key, style, icon_custom_emoji_id, design_style) VALUES (?, ?, ?, ?)",
                (btn_key, str(style), emoji_id, design_st)
            )
            conn.execute(
                "UPDATE custom_buttons SET style = ?, custom_emoji_id = ?, design_style = ? WHERE btn_key = ?",
                (str(style), emoji_id, design_st, btn_key)
            )
        conn.close()


def get_layout(layout_key: str) -> list:
    return resolve_menu_layout(layout_key, cached_layouts=CACHE_LAYOUTS, default_layouts=DEFAULT_LAYOUTS)


def get_all_active_layout_keys() -> list:
    base = list(ALLOWED_DYNAMIC_LAYOUT_KEYS)
    try:
        for cb in get_all_custom_buttons():
            lk = cb.get("layout_key", "")
            if lk and lk not in base:
                base.append(lk)
                LAYOUT_PAGE_TITLES[lk] = f"📂 {cb.get('label', lk)}"
                DEFAULT_LAYOUTS.setdefault(lk, [])
    except Exception:
        pass
    return base


def is_valid_layout_key(layout_key: str) -> bool:
    lk = resolve_layout_key(layout_key)
    return lk in ALLOWED_DYNAMIC_LAYOUT_KEYS or lk.startswith("custom_page_")


def sync_all_menus_after_button_change(trigger_uid: str = None, notify_chat_id=None):
    """
    Synchronizes all caches, layouts, callback maps, orphan records, and active User + Admin
    Bottom Menu keyboards immediately after any button Create, Move, Rename, Delete, or Restore.
    """
    preload_all_caches()
    try:
        with db_lock:
            conn = get_connection()
            bm_users = conn.execute(
                "SELECT user_id, bottom_menu_enabled, admin_bottom_menu FROM users WHERE COALESCE(bottom_menu_enabled, 0) = 1 OR COALESCE(admin_bottom_menu, 0) = 1"
            ).fetchall()
            conn.close()
        for r_u in bm_users:
            u_id_str = str(r_u["user_id"])
            if is_authorized_admin(u_id_str) and int(r_u["admin_bottom_menu"] or 0) == 1:
                build_admin_bottom_reply_keyboard(u_id_str)
            elif int(r_u["bottom_menu_enabled"] or 0) == 1:
                build_user_bottom_reply_keyboard(u_id_str)
        # Also refresh any currently tracked bottom menu sessions in memory
        for active_uid in list(USER_ACTIVE_BOTTOM_BUTTON_MAP.keys()):
            if is_authorized_admin(active_uid):
                u_act = get_user(active_uid)
                if u_act and int(u_act.get("admin_bottom_menu") or 0) == 1:
                    build_admin_bottom_reply_keyboard(active_uid)
                else:
                    build_user_bottom_reply_keyboard(active_uid, u_obj=u_act)
            else:
                build_user_bottom_reply_keyboard(active_uid)
    except Exception:
        pass


def set_layout(layout_key: str, structure: list, sync_menus: bool = True):
    layout_key = resolve_layout_key(layout_key)
    if not is_valid_layout_key(layout_key):
        return
    clean_struct = [[str(k).strip() for k in r if str(k).strip()] for r in (structure or []) if isinstance(r, list)]
    clean_struct = [r for r in clean_struct if r]
    CACHE_LAYOUTS[layout_key] = json.loads(json.dumps(clean_struct))
    with db_lock:
        conn = get_connection()
        with begin_immediate_transaction(conn):
            conn.execute(
                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                (layout_key, json.dumps(clean_struct, ensure_ascii=False))
            )
            sync_layout_placements_in_db(layout_key, clean_struct, conn=conn)
        conn.close()
    if sync_menus:
        sync_all_menus_after_button_change()


def find_button_current_layout(btn_key: str, fallback_layout_key: str = "") -> str:
    """Finds which layout page currently contains `btn_key` across all dynamic & custom layout pages."""
    b_k = str(btn_key or "").strip()
    try:
        locs = locate_button_across_all_layouts(b_k)
        if locs:
            if fallback_layout_key:
                resolved_fb = resolve_layout_key(fallback_layout_key)
                for lc in locs:
                    if lc["layout_key"] == resolved_fb:
                        return resolved_fb
            return locs[0]["layout_key"]
    except Exception:
        pass
    if fallback_layout_key:
        resolved_fb = resolve_layout_key(fallback_layout_key)
        fb_rows = get_layout(resolved_fb)
        if any(b_k in r for r in fb_rows if isinstance(r, list)):
            return resolved_fb
    for l_key in get_all_active_layout_keys():
        rows = get_layout(l_key)
        if any(b_k in r for r in rows if isinstance(r, list)):
            return l_key
    if fallback_layout_key:
        return resolve_layout_key(fallback_layout_key)
    return "admin_home" if b_k.startswith("a_") else "user_home"


def move_button_across_pages(
    from_layout_key: str,
    to_layout_key: str,
    btn_key: str,
    drop_mode: str = "bot",
    row_index: int = 0,
    col_index: int = None
) -> dict:
    """
    Moves ANY button (`btn_key`) from `from_layout_key` to ANY page, custom button folder, or exact row/slot (`to_layout_key`),
    persisting both layouts transactionally while:
    - Preventing circular references when moving custom container buttons (`would_create_container_cycle`)
    - Preserving original `(original_layout_key, original_row_index, original_col_index)` in `button_original_placements`
    - Synchronizing `custom_buttons.parent_layout`, `row_index`, `col_index`, and `parent_container_key`
    - Updating User and Admin Inline + Bottom Menus immediately.
    """
    from_l_key = resolve_layout_key(from_layout_key)
    to_l_key = resolve_layout_key(to_layout_key)
    b_k = str(btn_key or "").strip()

    if not is_valid_layout_key(from_l_key) or not is_valid_layout_key(to_l_key):
        return {"ok": False, "reason": "অবৈধ পেজ সিলেকশন!"}

    # Strict User-Side vs Admin-Side Button Separation
    def _detect_btn_side(k_str: str, fallback_lk: str = "") -> str:
        ks = str(k_str or "").strip()
        if ks.startswith("a_"):
            return "admin"
        if ks.startswith("u_"):
            return "user"
        if ks.startswith("cbtn_"):
            cb_r = get_custom_button(ks) or {}
            if cb_r.get("side") in ("admin", "user"):
                return cb_r["side"]
        return "admin" if str(fallback_lk).startswith("admin") else "user"

    def _detect_layout_side(lk_str: str) -> str:
        ls = str(lk_str or "").strip()
        if ls.startswith("admin"):
            return "admin"
        if ls.startswith("user"):
            return "user"
        if ls.startswith("custom_page_"):
            c_k = ls[len("custom_page_"):]
            cb_r = get_custom_button(c_k) or {}
            if cb_r.get("side") in ("admin", "user"):
                return cb_r["side"]
            if c_k.startswith("a_"):
                return "admin"
        return "user"

    btn_side_val = _detect_btn_side(b_k, from_l_key)
    to_side_val = _detect_layout_side(to_l_key)
    if btn_side_val != to_side_val:
        return {
            "ok": False,
            "reason": "⛔ ইউজার সাইডের বাটন অ্যাডমিন প্যানেলে এবং অ্যাডমিন প্যানেলের বাটন ইউজার সাইডে স্থানান্তর করা যাবে না!"
        }

    with db_lock:
        conn = get_connection()
        try:
            if would_create_container_cycle(b_k, to_l_key, conn=conn):
                conn.close()
                return {
                    "ok": False,
                    "reason": "⛔ Circular Reference প্রতিরোধ করা হয়েছে: একটি কাস্টম ফোল্ডারকে তার নিজের বা সাব-ফোল্ডারের ভেতরে স্থানান্তর করা যাবে না!"
                }
        finally:
            conn.close()

    src_layout = [list(r) for r in get_layout(from_l_key) if isinstance(r, list)]
    orig_r_found, orig_c_found = 0, 0
    removed_from_src = False
    new_src = []
    for r_i, row in enumerate(src_layout):
        if b_k in row:
            removed_from_src = True
            orig_r_found = r_i
            orig_c_found = row.index(b_k)
        filtered = [k for k in row if k != b_k]
        if filtered:
            new_src.append(filtered)

    # Record original placement before moving so restoration is 100% exact
    with db_lock:
        conn = get_connection()
        with begin_immediate_transaction(conn):
            if removed_from_src:
                record_button_placement(
                    b_k,
                    from_l_key,
                    orig_r_found,
                    orig_c_found,
                    preserve_original=True,
                    conn=conn
                )
            else:
                locs = locate_button_across_all_layouts(b_k, conn=conn)
                if locs:
                    first_loc = locs[0]
                    record_button_placement(
                        b_k,
                        first_loc["layout_key"],
                        first_loc["row_index"],
                        first_loc["col_index"],
                        preserve_original=True,
                        conn=conn
                    )
                    for lc in locs:
                        act_lk = lc["layout_key"]
                        if act_lk != to_l_key:
                            act_rows = [list(r) for r in get_layout(act_lk) if isinstance(r, list)]
                            cleaned_act = [[k for k in r if k != b_k] for r in act_rows]
                            cleaned_act = [r for r in cleaned_act if r]
                            CACHE_LAYOUTS[act_lk] = json.loads(json.dumps(cleaned_act))
                            conn.execute(
                                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                                (act_lk, json.dumps(cleaned_act, ensure_ascii=False))
                            )
                            sync_layout_placements_in_db(act_lk, cleaned_act, conn=conn)

            if from_l_key != to_l_key:
                CACHE_LAYOUTS[from_l_key] = json.loads(json.dumps(new_src))
                conn.execute(
                    "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                    (from_l_key, json.dumps(new_src, ensure_ascii=False))
                )
                sync_layout_placements_in_db(from_l_key, new_src, conn=conn)
                dst_layout = [[k for k in r if k != b_k] for r in get_layout(to_l_key) if isinstance(r, list)]
                dst_layout = [r for r in dst_layout if r]
            else:
                dst_layout = new_src

            if drop_mode == "top":
                dst_layout.insert(0, [b_k])
            elif drop_mode == "row" and 0 <= int(row_index) < len(dst_layout):
                if b_k not in dst_layout[int(row_index)]:
                    if col_index is not None and 0 <= int(col_index) <= len(dst_layout[int(row_index)]):
                        dst_layout[int(row_index)].insert(int(col_index), b_k)
                    else:
                        dst_layout[int(row_index)].append(b_k)
            elif drop_mode == "before" and 0 <= int(row_index) <= len(dst_layout):
                dst_layout.insert(int(row_index), [b_k])
            else:
                dst_layout.append([b_k])

            CACHE_LAYOUTS[to_l_key] = json.loads(json.dumps(dst_layout))
            conn.execute(
                "INSERT OR REPLACE INTO dynamic_layouts (layout_key, structure_json) VALUES (?, ?)",
                (to_l_key, json.dumps(dst_layout, ensure_ascii=False))
            )
            sync_layout_placements_in_db(to_l_key, dst_layout, conn=conn)
        conn.close()

    sync_all_menus_after_button_change()
    return {
        "ok": True,
        "from_layout_key": from_l_key,
        "to_layout_key": to_l_key,
        "from_layout": new_src,
        "to_layout": dst_layout
    }


def move_button_into_target_button(from_layout_key: str, target_btn_key: str, moving_btn_key: str) -> dict:
    """
    Moves `moving_btn_key` INSIDE `target_btn_key` with strict cycle prevention (`would_create_container_cycle`):
    - If `target_btn_key` maps to one of the dynamic pages or a custom button (`cbtn_*`),
      moves `moving_btn_key` directly into that target button's page layout.
    - If `target_btn_key` is a regular action button, creates a dedicated container for it without overwriting IDs.
    """
    t_bk = str(target_btn_key or "").strip()
    m_bk = str(moving_btn_key or "").strip()
    if t_bk == m_bk:
        return {"ok": False, "reason": "একই বাটনের ভেতরে নিজেকে ঢোকানো যাবে না!"}
    t_side = "admin" if (t_bk.startswith("a_") or (t_bk.startswith("cbtn_") and (get_custom_button(t_bk) or {}).get("side") == "admin")) else "user"
    m_side = "admin" if (m_bk.startswith("a_") or (m_bk.startswith("cbtn_") and (get_custom_button(m_bk) or {}).get("side") == "admin")) else "user"
    if t_side != m_side:
        return {"ok": False, "reason": "⛔ ইউজার সাইডের বাটন অ্যাডমিন বাটনের ভেতরে এবং অ্যাডমিন বাটন ইউজার বাটনের ভেতরে স্থানান্তর করা যাবে না!"}

    with db_lock:
        conn = get_connection()
        try:
            if would_create_container_cycle(m_bk, t_bk, conn=conn):
                conn.close()
                return {
                    "ok": False,
                    "reason": "⛔ Circular Reference প্রতিরোধ করা হয়েছে: নেস্টেড ফোল্ডারের ভেতরে প্যারেন্ট ফোল্ডার যুক্ত করা যাবে না!"
                }
        finally:
            conn.close()

    builtin_page_map = {
        "u_dashboard": "user_dashboard",
        "u_profile": "user_profile",
        "u_settings": "user_settings_hub",
        "u_settings_hub": "user_settings_hub",
        "a_settings": "admin_settings_hub",
        "a_plat_settings": "admin_platform_settings",
        "a_gen_settings": "admin_general_settings",
        "a_general_settings": "admin_general_settings",
        "a_adv_settings": "admin_advanced_settings",
    }
    if t_bk in builtin_page_map:
        dest_l_key = builtin_page_map[t_bk]
        return move_button_across_pages(from_layout_key, dest_l_key, m_bk, drop_mode="bot")

    cb_rec = get_custom_button(t_bk)
    if cb_rec and cb_rec.get("layout_key"):
        dest_l_key = cb_rec["layout_key"]
        return move_button_across_pages(from_layout_key, dest_l_key, m_bk, drop_mode="bot")

    side = "admin" if t_bk.startswith("a_") else "user"
    parent_l_key = find_button_current_layout(t_bk, resolve_layout_key(from_layout_key))
    raw_lbl = get_btn_raw_label(t_bk)
    orig_cb = GLOBAL_BUTTON_CALLBACK_MAP.get(t_bk, "")
    direct_key = f"{t_bk}_direct"
    if orig_cb and not orig_cb.startswith("cbtn_open:"):
        GLOBAL_BUTTON_CALLBACK_MAP[direct_key] = orig_cb
        DEFAULT_BUTTON_LABELS[direct_key] = raw_lbl
        CACHE_LABELS[direct_key] = raw_lbl
        CACHE_STYLES[direct_key] = get_btn_style(t_bk)

    c_layout_key = f"custom_page_{t_bk}"
    c_msg_key = f"custom_msg_{t_bk}"
    save_custom_button(
        btn_key=t_bk,
        side=side,
        parent_layout=parent_l_key,
        label=raw_lbl,
        style=get_btn_style(t_bk),
        design_style=get_btn_design(t_bk),
        custom_emoji_id=get_btn_emoji(t_bk),
        msg_key=c_msg_key,
        layout_key=c_layout_key,
        allow_update=True
    )
    GLOBAL_BUTTON_CALLBACK_MAP[t_bk] = f"cbtn_open:{t_bk}"
    LAYOUT_PAGE_TITLES[c_layout_key] = f"📂 {raw_lbl}"
    DEFAULT_LAYOUTS.setdefault(c_layout_key, [[direct_key]] if direct_key in GLOBAL_BUTTON_CALLBACK_MAP else [])
    if not CACHE_MESSAGES.get(c_msg_key):
        set_msg(c_msg_key, f"📂 <b>{esc(raw_lbl)}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় বাটনটি নির্বাচন করুন:")
    cur_c_rows = get_layout(c_layout_key)
    if not cur_c_rows and direct_key in GLOBAL_BUTTON_CALLBACK_MAP:
        set_layout(c_layout_key, [[direct_key]], sync_menus=False)
    return move_button_across_pages(from_layout_key, c_layout_key, m_bk, drop_mode="bot")


def set_msg(msg_key: str, content: str, updated_by="admin", raw_text: str = "", entities: list = None):
    CACHE_MESSAGES[msg_key] = content
    _BOT_DELIVERY_CAPS["custom_emoji_entities"] = True
    _BOT_DELIVERY_CAPS["custom_emoji_html"] = True
    if entities is not None:
        CACHE_MESSAGE_ENTITIES[msg_key] = entities
    with db_lock:
        save_dynamic_message_record(msg_key, content, raw_text=raw_text, entities=entities, updated_by=str(updated_by))


# ==============================================================================
# ZERO-LATENCY DYNAMIC KEYBOARDS & BOTTOM MENU (ReplyKeyboardMarkup) SUPPORT
# ==============================================================================
def append_page_edit_tools(kb, uid, msg_key=None, layout_key=None):
    if not uid or not is_admin_unlocked(uid):
        return kb
    if getattr(kb, "__class__", None).__name__ == "ReplyKeyboardMarkup":
        return kb
    edit_btns = []
    if layout_key and resolve_layout_key(layout_key) in ALLOWED_DYNAMIC_LAYOUT_KEYS:
        sc = short_layout_code(resolve_layout_key(layout_key))
        edit_btns.append(make_btn("📐 বাটন সাজান", callback_data=f"adm_elayout:{sc}", style="success"))
    if msg_key:
        edit_btns.append(make_btn("✏️ মেসেজ এডিট", callback_data=f"adm_emsg:{msg_key}", style="primary"))
    if edit_btns:
        kb.row(*edit_btns)
    return kb


def _render_button_for_key(k: str, u_lang: str = "bn", u_style: str = "", count_suffix: dict = None, ignore_visibility: bool = False):
    if not ignore_visibility and not get_btn_visibility(k):
        return None
    sup = get_setting("support_link", "https://t.me/battleclubsupport")
    grp = get_setting("group_link", "https://t.me/battleclubcreator")
    lbl = get_btn_label(k, lang=u_lang) + (count_suffix.get(k, "") if count_suffix else "")
    st = get_btn_style(k, u_style)
    em_id = get_btn_emoji(k)
    des = get_btn_design(k)
    if k == "u_support":
        return make_btn(lbl, url=sup, style=st, icon_custom_emoji_id=em_id, btn_key=k, design_style=des)
    if k == "u_group":
        return make_btn(lbl, url=grp, style=st, icon_custom_emoji_id=em_id, btn_key=k, design_style=des)
    cb = GLOBAL_BUTTON_CALLBACK_MAP.get(k)
    if cb:
        return make_btn(lbl, callback_data=cb, style=st, icon_custom_emoji_id=em_id, btn_key=k, design_style=des)
    return None


def build_dynamic_page_inline_keyboard(layout_key: str, uid: str = None, u_obj: dict = None, count_suffix: dict = None, msg_key: str = None):
    l_key = resolve_layout_key(layout_key)
    u = u_obj or (get_user(uid) if uid else None)
    u_style = (u.get("user_btn_style", "") if u else "") if not l_key.startswith("admin") else ""
    u_lang = (u.get("language", "bn") if u else "bn") or "bn"
    kb = types.InlineKeyboardMarkup()
    layout = [list(r) for r in get_layout(l_key) if isinstance(r, list)]
    for row_keys in layout:
        r_btns = []
        for k in row_keys:
            b = _render_button_for_key(k, u_lang=u_lang, u_style=u_style, count_suffix=count_suffix)
            if b is not None:
                r_btns.append(b)
        if r_btns:
            kb.row(*r_btns)
    if uid and (msg_key or l_key):
        append_page_edit_tools(kb, uid, msg_key=msg_key, layout_key=l_key)
    return kb


def build_user_bottom_reply_keyboard(uid: str, u_obj: dict = None):
    """
    Builds a colorful, custom-emoji ReplyKeyboardMarkup (`StyledKeyboardButton`) for the User Bottom Menu,
    preserving Green (`success`), Red (`danger`), Blue (`primary`) styles and `icon_custom_emoji_id`.
    """
    u = u_obj or get_user(uid)
    inline_kb = build_dynamic_page_inline_keyboard("user_home", uid=uid, u_obj=u, msg_key="welcome_msg")
    if is_authorized_admin(uid):
        has_adm_btn = any(getattr(b, "callback_data", "") == "admin_hub" for r in inline_kb.keyboard for b in r)
        if not has_adm_btn:
            inline_kb.row(make_btn(get_btn_label("a_super_admin_panel"), callback_data="admin_hub", style=get_btn_style("a_super_admin_panel") or "danger", btn_key="a_super_admin_panel"))
    return convert_inline_to_bottom_reply_keyboard(uid, inline_kb, u_obj=u)


def build_admin_bottom_reply_keyboard(uid: str):
    """
    Builds a colorful, custom-emoji ReplyKeyboardMarkup (`StyledKeyboardButton`) for the Admin Bottom Menu,
    preserving Green (`success`), Red (`danger`), Blue (`primary`) styles and `icon_custom_emoji_id`.
    """
    u = get_user(uid) if uid else None
    with db_lock:
        counts = get_video_approval_counts()
    count_suffix = {
        "a_pending_vids": f" ({counts.get('pending', {}).get('total', 0)})",
        "a_bot_approve": f" ({counts['bot_approve']['total']})",
        "a_admin_approve": f" ({counts['admin_approve']['total']})",
        "a_perm_approve": f" ({counts['permanent_approve']['total']})",
        "a_rejected_vids": f" ({counts['rejected']['total']})",
        "a_trash": f" ({counts['trash']['total']})"
    }
    inline_kb = build_dynamic_page_inline_keyboard(
        "admin_home",
        uid=uid,
        u_obj=u,
        count_suffix=count_suffix,
        msg_key="admin_dashboard_msg"
    )
    has_user_switch = any(getattr(b, "callback_data", "") == "umenu:cancel_home" for r in inline_kb.keyboard for b in r)
    if not has_user_switch:
        inline_kb.row(make_btn(get_btn_label("a_user_home"), callback_data="umenu:cancel_home", style=get_btn_style("a_user_home") or "success", btn_key="a_user_home"))
    return convert_inline_to_bottom_reply_keyboard(uid, inline_kb, u_obj=u)


def is_user_bottom_menu_enabled(u: dict) -> bool:
    if not u:
        return False
    return int(u.get("bottom_menu_enabled") or 0) == 1


def is_admin_bottom_menu_enabled(u: dict) -> bool:
    if not u:
        return False
    return int(u.get("admin_bottom_menu") or 0) == 1


def build_user_home_keyboard(uid, u_obj=None, force_inline: bool = False):
    u = u_obj or get_user(uid)
    if not force_inline and is_user_bottom_menu_enabled(u):
        return build_user_bottom_reply_keyboard(uid, u)
    kb = build_dynamic_page_inline_keyboard("user_home", uid=uid, u_obj=u, msg_key="welcome_msg")
    if is_authorized_admin(uid):
        has_adm_btn = any(getattr(b, "callback_data", "") == "admin_hub" for r in kb.keyboard for b in r)
        if not has_adm_btn:
            kb.row(make_btn(get_btn_label("a_super_admin_panel"), callback_data="admin_hub", style=get_btn_style("a_super_admin_panel") or "danger", btn_key="a_super_admin_panel"))
    return kb


def build_admin_dashboard_keyboard(uid=None, force_inline: bool = False):
    u = get_user(uid) if uid else None
    if not force_inline and is_admin_bottom_menu_enabled(u):
        return build_admin_bottom_reply_keyboard(uid)
    with db_lock:
        counts = get_video_approval_counts()
    pe_cnt = counts.get("pending", {}).get("total", 0)
    b_cnt = counts["bot_approve"]["total"]
    a_cnt = counts["admin_approve"]["total"]
    p_cnt = counts["permanent_approve"]["total"]
    r_cnt = counts["rejected"]["total"]
    t_cnt = counts["trash"]["total"]
    count_suffix = {
        "a_pending_vids": f" ({pe_cnt})",
        "a_bot_approve": f" ({b_cnt})",
        "a_admin_approve": f" ({a_cnt})",
        "a_perm_approve": f" ({p_cnt})",
        "a_rejected_vids": f" ({r_cnt})",
        "a_trash": f" ({t_cnt})"
    }
    kb = build_dynamic_page_inline_keyboard(
        "admin_home",
        uid=uid,
        u_obj=u,
        count_suffix=count_suffix,
        msg_key="admin_dashboard_msg"
    )
    has_user_switch = any(getattr(b, "callback_data", "") == "umenu:cancel_home" for r in kb.keyboard for b in r)
    if not has_user_switch:
        kb.row(make_btn(get_btn_label("a_user_home"), callback_data="umenu:cancel_home", style=get_btn_style("a_user_home") or "success", btn_key="a_user_home"))
    return kb


# ==============================================================================
# PART 3: STRICT 7-STEP ONBOARDING FLOW
# 1. Verify Channel(s) -> 2. Mandatory Battle Club UID FIRST ->
# 3. Payment Methods (1, 2, or all 3 of bKash/Nagad/Rocket, 1 number each) ->
# 4. User Account Name -> 5. Per-Platform Channel Name(s) ->
# 6. Strong Password -> 7. Confirm Password -> 8. Dashboard Access
# ==============================================================================
def start_step2_mandatory_uid_flow(chat_id, uid: str, st: dict, verification_summary: str = "", edit_message_id: int = None):
    """
    Transitions onboarding from Step 1 (Channel Verification) to Step 2 (Mandatory Battle Club UID FIRST)
    per Part 3, Items 27–30.
    """
    st["step"] = "reg_app_uid"
    st["ver_summary_html"] = verification_summary or st.get("ver_summary_html") or "✅ আপনার প্ল্যাটফর্ম সফলভাবে যাচাই হয়েছে!"
    user_memory_states[uid] = st

    txt = (
        f"{st['ver_summary_html']}\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        + get_msg("reg_uid_input_msg", verification_summary=st.get("ver_summary_html", "✅ প্ল্যাটফর্ম যাচাই সম্পন্ন!"))
    )
    kb = types.InlineKeyboardMarkup()
    append_page_edit_tools(kb, uid, msg_key="reg_uid_input_msg")
    eff_kb = kb if (is_admin_unlocked(uid)) else None
    if edit_message_id:
        safe_edit(chat_id, edit_message_id, txt, reply_markup=eff_kb)
    else:
        safe_send(chat_id, txt, reply_markup=eff_kb)


def build_onboarding_payment_selection_keyboard(uid: str, selected_methods: list = None):
    sel = [m for m in (selected_methods or ["bKash"]) if m in ("bKash", "Nagad", "Rocket")]
    if not sel:
        sel = ["bKash"]

    kb = types.InlineKeyboardMarkup()
    bk_mark = "✅" if "bKash" in sel else "⬜"
    ng_mark = "✅" if "Nagad" in sel else "⬜"
    rk_mark = "✅" if "Rocket" in sel else "⬜"

    kb.row(
        make_btn(f"{bk_mark} 🌸 বিকাশ (bKash)", callback_data="reg_pay_toggle:bKash", style="danger" if "bKash" in sel else "primary"),
        make_btn(f"{ng_mark} 🍊 নগদ (Nagad)", callback_data="reg_pay_toggle:Nagad", style="success" if "Nagad" in sel else "primary")
    )
    kb.row(
        make_btn(f"{rk_mark} 🚀 রকেট (Rocket)", callback_data="reg_pay_toggle:Rocket", style="primary"),
        make_btn("✅ 🎮 Battle Club UID (বাধ্যতামূলক)", callback_data="reg_pay_toggle:BattleClub_UID", style="success")
    )
    kb.row(make_btn("🌟 সব মাধ্যম একসাথে সিলেক্ট করুন (বিকাশ, নগদ, রকেট ও UID)", callback_data="reg_pay_toggle:all3", style="success"))
    kb.row(make_btn(f"🚀 পেমেন্ট মেথড কনফার্ম করুন ({len(sel)}টি সিলেক্টেড)", callback_data="reg_pay_confirm", style="success"))
    append_page_edit_tools(kb, uid, msg_key="reg_payment_methods_select_msg")
    return kb


def start_step3_payment_selection_flow(chat_id, uid: str, st: dict, edit_message_id: int = None):
    """Transitions onboarding from Step 2 (Mandatory UID) to Step 3 (bKash/Nagad/Rocket Selection)."""
    sel_methods = [m for m in (st.get("selected_pay_methods") or ["bKash"]) if m in ("bKash", "Nagad", "Rocket")]
    if not sel_methods:
        sel_methods = ["bKash"]
    st["selected_pay_methods"] = sel_methods + ["BattleClub_UID"]
    st["step"] = "reg_phone_select"
    st["pay_queue"] = list(sel_methods)
    user_memory_states[uid] = st

    uid_summary = f"✅ <b>Battle Club UID লক হয়েছে:</b> <code>{esc(st.get('app_uid', ''))}</code>"
    txt = get_msg("reg_payment_methods_select_msg", verification_summary=uid_summary)
    kb = build_onboarding_payment_selection_keyboard(uid, sel_methods)
    if edit_message_id:
        safe_edit(chat_id, edit_message_id, txt, reply_markup=kb)
    else:
        safe_send(chat_id, txt, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("reg_pay_toggle:") or c.data == "reg_pay_confirm")
@_guard("reg_payment_selection")
def handle_onboarding_payment_selection(call):
    uid = str(call.from_user.id)
    st = user_memory_states.setdefault(uid, {"step": "reg_phone_select", "selected_pay_methods": ["bKash", "BattleClub_UID"]})
    sel = [m for m in (st.get("selected_pay_methods") or ["bKash"]) if m in ("bKash", "Nagad", "Rocket")]
    if not sel:
        sel = ["bKash"]

    if call.data.startswith("reg_pay_toggle:"):
        target = call.data.split(":", 1)[1]
        if target == "BattleClub_UID":
            bot.answer_callback_query(call.id, "✅ Battle Club UID বাধ্যতামূলকভাবে যুক্ত রয়েছে!", show_alert=False)
            return
        if target in ("all3", "all4"):
            sel = ["bKash", "Nagad", "Rocket"]
        elif target in ("bKash", "Nagad", "Rocket"):
            if target in sel:
                if len(sel) <= 1:
                    bot.answer_callback_query(call.id, "⚠️ বিকাশ, নগদ বা রকেট—কমপক্ষে যেকোনো ১টি মোবাইল পেমেন্ট মেথড সিলেক্ট থাকতে হবে!", show_alert=True)
                    return
                sel.remove(target)
            else:
                sel.append(target)
        st["selected_pay_methods"] = sel + ["BattleClub_UID"]
        st["pay_queue"] = [m for m in ("bKash", "Nagad", "Rocket") if m in sel]
        user_memory_states[uid] = st

        uid_sum = f"✅ <b>Battle Club UID:</b> <code>{esc(st.get('app_uid', ''))}</code>"
        txt = get_msg("reg_payment_methods_select_msg", verification_summary=uid_sum)
        kb = build_onboarding_payment_selection_keyboard(uid, sel)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "reg_pay_confirm":
        pay_q = [m for m in ("bKash", "Nagad", "Rocket") if m in sel]
        if not pay_q:
            pay_q = ["bKash"]
        st["selected_pay_methods"] = pay_q + ["BattleClub_UID"]
        st["pay_queue"] = list(pay_q)
        st["step"] = "reg_phone"
        user_memory_states[uid] = st

        first_m = pay_q[0]
        m_title = PAYMENT_PLATFORM_LABELS.get(first_m, first_m)
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="reg_payment_number_input_msg")
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("reg_payment_number_input_msg", method_title=m_title),
            reply_markup=kb if (is_admin_unlocked(uid)) else None
        )
        bot.answer_callback_query(call.id, f"{len(pay_q)}টি মোবাইল পেমেন্ট মেথড সিলেক্ট করা হয়েছে!")


# ==============================================================================
# START COMMAND & ONBOARDING PLATFORM SELECTION (YOUTUBE & TIKTOK)
# ==============================================================================
def send_onboarding_home(chat_id, uid, u):
    bio_c = str((u or {}).get("bio_verify_code") or "").strip()
    if not bio_c or not bio_c.upper().startswith("BC-"):
        with db_lock:
            conn = get_connection()
            with conn:
                bio_c = generate_unique_bc_code("bio_verify", user_id=uid, conn=conn)
                conn.execute("UPDATE users SET bio_verify_code = ?, bio_code_generated_ts = ? WHERE user_id = ?", (bio_c, time.time(), uid))
            conn.close()

    user_memory_states[uid] = {"step": "reg_select_platforms", "selected": ["youtube"], "verified_platforms": []}
    kb = types.InlineKeyboardMarkup()
    kb.row(
        make_btn(f"✅ {get_btn_label('u_plat_youtube')}", callback_data="reg_toggle:youtube", style="success", btn_key="u_plat_youtube"),
        make_btn(f"⬜ {get_btn_label('u_plat_tiktok')}", callback_data="reg_toggle:tiktok", style="primary", btn_key="u_plat_tiktok")
    )
    kb.row(make_btn(get_btn_label("u_plat_both"), callback_data="reg_toggle:all2", style="primary", btn_key="u_plat_both"))
    kb.row(make_btn(f"{get_btn_label('u_plat_confirm')} (1টি)", callback_data="reg_confirm_selection", style="success", btn_key="u_plat_confirm"))
    append_page_edit_tools(kb, uid, msg_key="reg_step1_yt_msg")
    if is_authorized_admin(uid):
        kb.row(
            make_btn(get_btn_label("a_super_admin_panel"), callback_data="admin_hub", style=get_btn_style("a_super_admin_panel") or "danger", btn_key="a_super_admin_panel"),
            make_btn(get_btn_label("a_user_home"), callback_data="umenu:cancel_home", style=get_btn_style("a_user_home") or "success", btn_key="a_user_home")
        )

    top_yt = get_setting("home_youtube_link", "")
    txt = attach_top_youtube_preview(get_msg("reg_step1_yt_msg"), top_yt)
    safe_send(chat_id, txt, reply_markup=kb, top_yt_url=top_yt)


@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = str(message.from_user.id)
    cleanup_user_ui_messages(message.chat.id, uid)
    u = ensure_user(message.from_user)
    user_memory_states.pop(uid, None)
    admin_unlocked_sessions.pop(uid, None)
    try:
        lock_admin_session(uid)
    except Exception:
        pass

    if u.get("status") == "deleted":
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET status = 'active', registered = 0 WHERE user_id = ?", (uid,))
            conn.close()
        u = get_user(uid)

    if u.get("status") == "banned" and not is_authorized_admin(uid):
        safe_send(message.chat.id, get_msg("ch_banned_msg"))
        return

    parts = (message.text or "").split()
    if len(parts) > 1 and "ref_" in parts[1]:
        ref_cand = parts[1].replace("ref_", "").strip()
        if ref_cand != uid and not u.get("redeemed_ref"):
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute("UPDATE users SET ref_by = ? WHERE user_id = ?", (ref_cand, uid))
                conn.close()

    # When Admin presses /start, show the normal platform verification screen with BOTH Super Admin Panel & User Home Page buttons!
    if is_authorized_admin(uid) and not (int(u.get("registered") or 0) == 1 and (u.get("password_hash") or u.get("password_plain"))):
        send_onboarding_home(message.chat.id, uid, u)
        return

    has_verified_account = bool(int(u.get("registered") or 0) == 1 and (u.get("password_hash") or u.get("password_plain")))
    if not has_verified_account:
        send_onboarding_home(message.chat.id, uid, u)
        return

    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute("UPDATE users SET session_logged_out = 1, timeout_notified = 1 WHERE user_id = ?", (uid,))
        conn.close()
    user_memory_states[uid] = {"step": "awaiting_session_password"}
    top_yt = get_setting("home_youtube_link", "")
    login_txt = attach_top_youtube_preview(get_msg("login_password_prompt_msg"), top_yt)
    if is_authorized_admin(uid):
        adm_start_kb = types.InlineKeyboardMarkup()
        adm_start_kb.row(
            make_btn(get_btn_label("a_super_admin_panel"), callback_data="admin_hub", style=get_btn_style("a_super_admin_panel") or "danger", btn_key="a_super_admin_panel"),
            make_btn(get_btn_label("a_user_home"), callback_data="umenu:cancel_home", style=get_btn_style("a_user_home") or "success", btn_key="a_user_home")
        )
        safe_send(message.chat.id, login_txt, reply_markup=adm_start_kb, top_yt_url=top_yt)
    else:
        safe_send(message.chat.id, login_txt, top_yt_url=top_yt)


@bot.message_handler(commands=[
    'admin', 'admin_guide', 'commands', 'metrics', 'users', 'user', 'search_user',
    'messages', 'buttons', 'broadcast', 'settings', 'platforms', 'rates',
    'withdrawals', 'ledger', 'pending', 'bot_approve', 'admin_approve', 'perm_approve',
    'rejected', 'trash', 'export', 'run_monitor', 'advanced'
])
def handle_admin_direct_commands(message):
    if not require_unlocked_admin_session(message):
        return
    uid = str(message.from_user.id)
    text_parts = (message.text or "").strip().split(maxsplit=1)
    cmd = text_parts[0].lstrip("/").split("@")[0].lower()
    arg = text_parts[1].strip() if len(text_parts) > 1 else ""

    if cmd == "admin_guide":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("⌨️ কমান্ড ও শর্টকাট তালিকা", callback_data="adm_cmd_shortcuts", style="primary"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে যান", callback_data="adm_settings_hub", style="danger"))
        safe_send(message.chat.id, ADMIN_GUIDE_TEXT, reply_markup=kb)
        return

    if cmd == "commands":
        kb = build_command_shortcuts_keyboard("all")
        safe_send(message.chat.id, build_full_command_shortcut_text("all"), reply_markup=kb)
        return

    if cmd == "admin":
        safe_send(message.chat.id, get_msg("admin_welcome_msg"), reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
        return

    if cmd == "metrics":
        txt = render_admin_master_metrics_text()
        safe_send(message.chat.id, txt, reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
        return

    if cmd == "run_monitor":
        run_video_monitoring_pass()
        safe_send(message.chat.id, "✅ ভিউ ও ভেরিফিকেশন মনিটরিং পাস সফলভাবে সম্পন্ন হয়েছে!", reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
        return

    cb_route_map = {
        "users": "adm_ulist:0",
        "user": f"adm_uview:{arg}" if arg else "adm_ulist:0",
        "search_user": "adm_usearch",
        "messages": "adm_msg_hub",
        "buttons": "adm_btn_editor_hub",
        "advanced": "adm_adv_hub",
        "broadcast": "adm_broadcast_prompt",
        "settings": "adm_settings_hub",
        "platforms": "adm_crit:hub",
        "rates": "adm_edit_rate_days",
        "withdrawals": "adm_wd_reports_hub",
        "ledger": "adm_fin_history:0",
        "pending": "adm_vsec:pe:select:0",
        "bot_approve": "adm_vsec:ba:select:0",
        "admin_approve": "adm_vsec:aa:select:0",
        "perm_approve": "adm_vsec:pa:select:0",
        "rejected": "adm_vsec:rj:select:0",
        "trash": "adm_trash:0",
        "export": "adm_db_export_hub"
    }
    target_cb = cb_route_map.get(cmd, "admin_hub")
    placeholder = safe_send(message.chat.id, "⏳ লোড হচ্ছে...")

    class _SyntheticCall:
        def __init__(self, u_obj, msg_obj, data_str):
            self.id = f"cmd_{int(time.time()*1000)}"
            self.from_user = u_obj
            self.message = msg_obj
            self.data = data_str

    syn_call = _SyntheticCall(message.from_user, placeholder, target_cb)
    if target_cb.startswith("adm_vsec:"):
        handle_admin_video_approval_sections(syn_call)
    elif target_cb.startswith("adm_ulist:") or target_cb == "adm_usearch":
        handle_admin_user_list(syn_call)
    elif target_cb.startswith("adm_uview:"):
        handle_admin_user_profile_control(syn_call)
    elif target_cb.startswith("adm_wd_"):
        handle_admin_wd_reports_system(syn_call)
    elif target_cb.startswith("adm_fin_history:"):
        handle_admin_financial_history(syn_call)
    elif target_cb.startswith("adm_trash:"):
        handle_admin_trash_system(syn_call)
    elif target_cb in ("adm_msg_hub", "adm_btn_editor_hub", "adm_adv_hub", "adm_bpos_hub"):
        handle_dynamic_ui_and_message_editors(syn_call)
    else:
        handle_admin_settings_and_limits(syn_call)


@bot.callback_query_handler(func=lambda c: c.data.startswith("reg_toggle:") or c.data == "reg_confirm_selection")
@_guard("onboarding_selection")
def handle_onboarding_selection(call):
    uid = str(call.from_user.id)
    st = user_memory_states.setdefault(uid, {"step": "reg_select_platforms", "selected": ["youtube"], "verified_platforms": []})
    u = get_user(uid) or ensure_user(call.from_user)

    if call.data.startswith("reg_toggle:"):
        p = call.data.split(":", 1)[1]
        sel = [pk for pk in st.get("selected", ["youtube"]) if pk in ("youtube", "tiktok")]
        if not sel:
            sel = ["youtube"]
        if p in ("all2", "all4", "all"):
            sel = ["youtube", "tiktok"]
        elif p in ("youtube", "tiktok"):
            if p in sel:
                if len(sel) > 1:
                    sel.remove(p)
            else:
                sel.append(p)
        st["selected"] = sel

        kb = types.InlineKeyboardMarkup()
        row1 = []
        for pk, bk in [("youtube", "u_plat_youtube"), ("tiktok", "u_plat_tiktok")]:
            mark = "✅" if pk in sel else "⬜"
            st_col = "success" if pk in sel else "primary"
            row1.append(make_btn(f"{mark} {get_btn_label(bk)}", callback_data=f"reg_toggle:{pk}", style=st_col, btn_key=bk))
        kb.row(*row1)
        kb.row(make_btn(get_btn_label("u_plat_both"), callback_data="reg_toggle:all2", style="primary", btn_key="u_plat_both"))
        kb.row(make_btn(f"{get_btn_label('u_plat_confirm')} ({len(sel)}টি)", callback_data="reg_confirm_selection", style="success", btn_key="u_plat_confirm"))
        append_page_edit_tools(kb, uid, msg_key="reg_step1_yt_msg")

        safe_edit(call.message.chat.id, call.message.message_id, get_msg("reg_step1_yt_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "reg_confirm_selection":
        sel = [pk for pk in st.get("selected", ["youtube"]) if pk in ("youtube", "tiktok")] or ["youtube"]
        st["step"] = "reg_platform_input"
        st["queue"] = list(sel)
        st["verified_platforms"] = list(st.get("verified_platforms") or [])
        curr_p = st["queue"][0]
        crit = get_platform_criteria(curr_p)
        total_req_v = int(crit["min_views"]) * int(crit["qualifying_videos"])

        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="reg_code_prompt_msg")
        txt = get_msg(
            "reg_code_prompt_msg",
            platform_title=PLATFORMS[curr_p]["title"],
            bio_code=u["bio_verify_code"],
            min_subs=crit["min_subs"],
            min_total_vids=crit.get("min_total_videos", 8),
            qual_vids=crit["qualifying_videos"],
            min_views=crit["min_views"],
            total_req_views=total_req_v
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb if (is_admin_unlocked(uid)) else None)
        bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "u_unfreeze_req" or c.data.startswith("u_recheck_vcode:"))
@_guard("unfreeze_req", sensitive=True)
def handle_unfreeze_request(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u:
        return
    if call.data.startswith("u_recheck_vcode:"):
        sub_id = call.data.split(":", 1)[1].strip()
        with db_lock:
            conn = get_connection()
            v_row = conn.execute("SELECT * FROM videos WHERE sub_id = ? AND user_id = ? LIMIT 1", (sub_id, uid)).fetchone()
            conn.close()
        if not v_row:
            bot.answer_callback_query(call.id, "ভিডিওটি পাওয়া যায়নি!", show_alert=True)
            return
        v = dict(v_row)
        plats = get_user_platforms(uid, v["platform"])
        v_link_global = get_setting("verification_link", "")
        bot.answer_callback_query(call.id, "🔍 ভিডিওর ভেরিফিকেশন কোড ও ভেরিফাইড অ্যাকাউন্ট মালিকানা যাচাই করা হচ্ছে...")
        rev_res = reverify_video_code_and_ownership_only(
            v["platform"],
            v["url"],
            plats,
            v["unique_code"],
            verification_link=v_link_global
        )
        if not rev_res.get("ok"):
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔄 আবার যাচাই করুন", callback_data=f"u_recheck_vcode:{sub_id}", style="success"))
            kb.row(make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_send(call.message.chat.id, f"❌ <b>যাচাই ব্যর্থ:</b> {esc(rev_res.get('reason', 'কোড পাওয়া যায়নি!'))}", reply_markup=kb)
            return
        # Restore code_missing_flag = 0 and code_missing_warning_ts = 0 WITHOUT resetting time or earnings!
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute(
                    "UPDATE videos SET code_missing_flag = 0, code_missing_warning_ts = 0, last_code_check_ts = ? WHERE sub_id = ?",
                    (time.time(), sub_id)
                )
                conn.execute(
                    "UPDATE users SET bio_frozen = 0, status = CASE WHEN status = 'inactive' THEN 'active' ELSE status END WHERE user_id = ?",
                    (uid,)
                )
                log_audit_event(uid, "Video Code Re-Verified", f"Video {sub_id} code {v['unique_code']} & ownership verified (time & earnings preserved)", target_user_id=uid, conn=conn)
            conn.close()
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"✅ <b>ভেরিফিকেশন কোড (<code>{esc(v['unique_code'])}</code>) ও ভেরিফাইড অ্যাকাউন্ট মালিকানা সফলভাবে যাচাই হয়েছে!</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"🎬 ভিডিও: <b>{esc(v['title'][:40])}</b>\n"
            f"💰 আপনার পূর্বের অর্জিত টাকা (<b>{float(v.get('credited_amount') or v.get('reward') or 0.0):.2f}৳</b>) এবং অতিবাহিত সময় ১০০% অক্ষুণ্ণ রয়েছে!",
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u:
        return
    plats = get_user_platforms(uid)
    if not plats:
        bot.answer_callback_query(call.id, "কোনো ভেরিফাইড প্রোফাইল পাওয়া যায়নি!", show_alert=True)
        return

    bot.answer_callback_query(call.id, "🔍 আপনার চ্যানেলের বায়ো কোড/লিংক এবং ভিডিওর হ্যাশট্যাগ/ইউনিকোড যাচাই করা হচ্ছে...")
    b_code = u["bio_verify_code"]
    v_link_global = get_setting("verification_link", "")
    all_ok = True
    fail_detail = ""
    for p in plats:
        p_crit = get_platform_criteria(p["platform"])
        v_link = p_crit.get("verification_link") or v_link_global
        chk = verify_bio_code_only(p["platform"], p["profile_url"], p["bio_code_used"] or b_code, verification_link=v_link)
        if not chk.get("network_ok"):
            all_ok = False
            fail_detail = f"নেটওয়ার্ক বা সার্ভার ত্রুটির কারণে প্রোফাইল ({p['platform'].upper()}) এই মুহূর্তে যাচাই করা সম্ভব হয়নি (Unknown / Unreachable)। অনুগ্রহ করে একটু পর আবার চেষ্টা করুন।"
            break
        if not chk.get("bio_found"):
            all_ok = False
            fail_detail = f"প্রোফাইল ({p['platform'].upper()}) বায়োতে কোড <code>{esc(p['bio_code_used'] or b_code)}</code> পাওয়া যায়নি!"
            break

    if all_ok:
        with db_lock:
            conn = get_connection()
            flagged_vids = conn.execute(
                "SELECT * FROM videos WHERE user_id = ? AND admin_status != 'rejected' AND COALESCE(is_trashed, 0) = 0 AND code_missing_flag = 1",
                (uid,)
            ).fetchall()
            conn.close()
        for fv in flagged_vids:
            vchk = verify_video_code_only(fv["platform"], fv["url"], fv["unique_code"], fv["app_uid"], fv["global_code"], verification_link=v_link_global)
            if not vchk.get("network_ok"):
                all_ok = False
                fail_detail = f"নেটওয়ার্ক ত্রুটির কারণে আপনার ভিডিও ({esc(fv['title'][:25])}) এই মুহূর্তে যাচাই করা সম্ভব হয়নি (Unreachable)। একটু পর আবার চেষ্টা করুন।"
                break
            if not vchk.get("codes_found"):
                all_ok = False
                fail_detail = f"আপনার ভিডিওতে ({esc(fv['title'][:25])}) কোড/হ্যাশট্যাগ <code>{esc(', '.join(vchk.get('missing', [])))}</code> পাওয়া যায়নি!"
                break

    if all_ok:
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET bio_frozen = 0, status = CASE WHEN status = 'inactive' THEN 'active' ELSE status END WHERE user_id = ?", (uid,))
                conn.execute("UPDATE user_platforms SET bio_missing_flag = 0, last_bio_check_ts = ? WHERE user_id = ?", (time.time(), uid))
                conn.execute("UPDATE videos SET code_missing_flag = 0, last_code_check_ts = ? WHERE user_id = ?", (time.time(), uid))
                log_audit_event(uid, "Account Unfrozen", "Bio & video codes verified and restored", target_user_id=uid, conn=conn)
            conn.close()
        safe_edit(
            call.message.chat.id, call.message.message_id,
            "✅ <b>সকল ভেরিফিকেশন কোড ও হ্যাশট্যাগ সফলভাবে পাওয়া গেছে! আপনার অ্যাকাউন্ট স্বয়ংক্রিয়ভাবে সচল (Active) ও আনফ্রিজ করা হয়েছে।</b>",
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
    else:
        safe_send(call.message.chat.id, f"❌ <b>আনফ্রিজ ব্যর্থ:</b> {fail_detail}\nসঠিকভাবে বায়ো এবং ভিডিওতে কোড ও হ্যাশট্যাগ বসিয়ে আবার চেষ্টা করুন।")


# ==============================================================================
# PART 4 & 9: LEADERBOARD NEXT-RANK TARGET & USER DASHBOARD (4 BUTTONS ONLY)
# ==============================================================================
def _compute_user_leaderboard_progress(user_id: str, my_earned: float) -> dict:
    """
    Computes user's rank (`Top 3`, `Top 10`, or `#N`), visual progress bar,
    needed earnings for `Top 1`, and needed earnings for the immediate next higher rank (`#N-1`, e.g., `#5 -> #4`, `#10 -> #9`).
    """
    uid = str(user_id)
    with db_lock:
        conn = get_connection()
        all_ranked = conn.execute("""
            SELECT user_id, total_earned, videos_approved
            FROM users
            WHERE registered = 1 AND COALESCE(status, 'active') != 'deleted'
            ORDER BY total_earned DESC, videos_approved DESC
        """).fetchall()
        conn.close()

    my_rank = next((i + 1 for i, r in enumerate(all_ranked) if str(r["user_id"]) == uid), len(all_ranked) + 1)
    top_1_earned = float(all_ranked[0]["total_earned"] or 0.0) if all_ranked else 0.0
    tenth_earned = float(all_ranked[9]["total_earned"] or 0.0) if len(all_ranked) >= 10 else 0.0
    rate_1k = max(1.0, float(get_setting("rate_per_1k", "15.0")))

    if my_rank <= 3:
        rank_badge = f"#{my_rank} (Top 3 🏅)"
    elif my_rank <= 10:
        rank_badge = f"#{my_rank} (Top 10 🌟)"
    else:
        rank_badge = f"#{my_rank}"

    next_rank_num = max(1, my_rank - 1)
    if my_rank > 1 and (my_rank - 2) < len(all_ranked):
        next_rank_earned = float(all_ranked[my_rank - 2]["total_earned"] or 0.0)
    else:
        next_rank_earned = top_1_earned

    if my_rank == 1 and my_earned >= top_1_earned and len(all_ranked) > 0:
        progress_pct = 100.0
        p_bar = build_visual_progress_bar(100.0)
        summary_line = (
            f"• বর্তমান পজিশন: <b>{rank_badge}</b> | অগ্রগতি: <code>[{p_bar}]</code> <b>100%</b>\n"
            f"• 🌟 অভিনন্দন! আপনি বর্তমানে লিডারবোর্ডের #1 শীর্ষ স্থানে অবস্থান করছেন!"
        )
        gap_notice = (
            f"• আপনার বর্তমান পজিশন: <b>{rank_badge}</b>\n"
            f"• প্রগ্রেস বার: <code>[{p_bar}]</code> <b>100%</b>\n"
            f"• 🌟 অভিনন্দন! আপনি ইতিমধ্যে লিডারবোর্ডের #1 শীর্ষ অবস্থানে আছেন!"
        )
    elif len(all_ranked) >= 10 and my_rank > 10:
        target_top10 = max(1.0, round(tenth_earned + 1.0, 2))
        need_top10 = max(0.0, round(target_top10 - my_earned, 2))
        need_next = max(0.0, round((next_rank_earned + 1.0) - my_earned, 2))
        need_top1 = max(0.0, round((top_1_earned + 1.0) - my_earned, 2))
        progress_pct = min(99.9, round((my_earned / target_top10) * 100.0, 1))
        p_bar = build_visual_progress_bar(progress_pct)
        need_vids = max(1, int((need_top10 / rate_1k) + 0.999))
        summary_line = (
            f"• বর্তমান পজিশন: <b>{rank_badge}</b> | টপ ১০ প্রগ্রেস: <code>[{p_bar}]</code> <b>{progress_pct:.1f}%</b>\n"
            f"• পরবর্তী র‍্যাঙ্ক (#{next_rank_num})-এ যেতে প্রয়োজন: <b>{need_next:.2f} টাকা</b>\n"
            f"• Top 10-এ ঢুকতে প্রয়োজন: <b>{need_top10:.2f} টাকা</b> (আনুমানিক <b>{need_vids}টি</b> ভিডিও) | #1 হতে প্রয়োজন: <b>{need_top1:.2f} টাকা</b>"
        )
        gap_notice = (
            f"• বর্তমান র‍্যাঙ্ক: <b>{rank_badge}</b> | প্রগ্রেস: <code>[{p_bar}]</code> <b>{progress_pct:.1f}%</b>\n"
            f"• পরবর্তী পজিশন (<b>#{next_rank_num}</b>)-এ যেতে আরও প্রয়োজন: <b>{need_next:.2f} টাকা</b>\n"
            f"• <b>Top 10</b>-এ উঠতে আরও প্রয়োজন: <b>{need_top10:.2f} টাকা</b> | <b>#1 Top</b> হতে প্রয়োজন: <b>{need_top1:.2f} টাকা</b>"
        )
    else:
        target_top1 = max(1.0, round(top_1_earned + 1.0, 2))
        need_top1 = max(0.0, round(target_top1 - my_earned, 2))
        need_next = max(0.0, round((next_rank_earned + 1.0) - my_earned, 2))
        progress_pct = min(99.9, round((my_earned / target_top1) * 100.0, 1))
        p_bar = build_visual_progress_bar(progress_pct)
        need_vids = max(1, int((need_top1 / rate_1k) + 0.999))
        summary_line = (
            f"• বর্তমান পজিশন: <b>{rank_badge}</b> | টপ ১ প্রগ্রেস: <code>[{p_bar}]</code> <b>{progress_pct:.1f}%</b>\n"
            f"• পরবর্তী র‍্যাঙ্ক (<b>#{next_rank_num}</b>)-এ উঠতে আরও প্রয়োজন: <b>{need_next:.2f} টাকা</b>\n"
            f"• <b>#1 Top</b>-এ উঠতে আরও প্রয়োজন: <b>{need_top1:.2f} টাকা</b> (আনুমানিক <b>{need_vids}টি</b> ভিডিও)"
        )
        gap_notice = (
            f"• বর্তমান র‍্যাঙ্ক: <b>{rank_badge}</b> | প্রগ্রেস: <code>[{p_bar}]</code> <b>{progress_pct:.1f}%</b>\n"
            f"• পরবর্তী পজিশন (<b>#{next_rank_num}</b>)-এ যেতে আরও প্রয়োজন: <b>{need_next:.2f} টাকা</b>\n"
            f"• <b>#1 Top</b>-এ উঠতে আরও প্রয়োজন: <b>{need_top1:.2f} টাকা</b> (আনুমানিক <b>{need_vids}টি</b> ভিডিও)"
        )

    return {
        "rank": my_rank,
        "rank_badge": rank_badge,
        "progress_pct": f"{progress_pct:.1f}",
        "progress_bar": p_bar,
        "summary_line": summary_line,
        "gap_notice": gap_notice
    }


def render_user_dashboard_view(uid, target_u=None, is_admin_impersonation=False):
    u = target_u or get_user(uid)
    t_uid = str(u["user_id"])
    plats = get_user_platforms(t_uid)
    g_code = get_setting("global_required_code", "#BattleClub")
    with db_lock:
        conn = get_connection()
        v_all = conn.execute(
            "SELECT bot_status, admin_status, status, COALESCE(permanent_approved, 0) as perm FROM videos WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0",
            (t_uid,)
        ).fetchall()
        wd_rows = conn.execute(
            "SELECT status, COUNT(*) as c, COALESCE(SUM(amount), 0) as s FROM withdrawals WHERE user_id = ? GROUP BY status",
            (t_uid,)
        ).fetchall()
        conn.close()

    pend_v, bot_app_v, adm_app_v, perm_app_v, rej_v = 0, 0, 0, 0, 0
    for vr in v_all:
        if vr["admin_status"] == "rejected" or vr["bot_status"] == "rejected" or vr["status"] == "rejected":
            rej_v += 1
        elif int(vr["perm"] or 0) == 1:
            perm_app_v += 1
        elif vr["admin_status"] == "approved":
            adm_app_v += 1
        elif vr["bot_status"] == "approved":
            bot_app_v += 1
        else:
            pend_v += 1

    app_v_total = bot_app_v + adm_app_v + perm_app_v
    sub_v_total = max(int(u.get("videos_submitted") or 0), len(v_all))

    wd_map = {"paid": (0, 0.0), "pending": (0, 0.0), "cancelled": (0, 0.0), "rejected": (0, 0.0)}
    wd_total_cnt, wd_total_amt = 0, 0.0
    for wr in wd_rows:
        c_val = int(wr["c"] or 0)
        s_val = float(wr["s"] or 0.0)
        wd_total_cnt += c_val
        wd_total_amt += s_val
        sk = wr["status"] if wr["status"] in wd_map else "cancelled"
        pc, ps = wd_map.get(sk, (0, 0.0))
        wd_map[sk] = (pc + c_val, ps + s_val)

    ref_code_disp = u.get("referral_code") or f"REF-{t_uid}"
    lb_prog = _compute_user_leaderboard_progress(t_uid, float(u.get("total_earned", 0.0) or 0.0))
    pay_summary = format_user_payment_numbers_summary(u)
    ch_names_summary = format_user_platform_channel_names(u, plats)
    debt_val = float(u.get("debt_balance", 0.0) or 0.0)
    bal_val = float(u.get("balance", 0.0) or 0.0)
    fin_status = f"⚠️ ঋণাত্মক / ডেট (-{debt_val:.2f}৳)" if debt_val > 0 else "🟢 স্বাভাবিক (Clear)"

    txt = get_msg(
        "dashboard_msg",
        user_label=esc(get_user_label(u)),
        user_id=esc(t_uid),
        name=esc(u.get("name")),
        channel_name=esc(ch_names_summary),
        app_uid=esc(format_display_app_uid(u.get("app_uid"))),
        phone=esc(pay_summary),
        balance=f"{bal_val:.2f}",
        held_balance=f"{float(u.get('held_balance', 0)):.2f}",
        debt_balance=f"{debt_val:.2f}",
        total_earned=f"{float(u.get('total_earned', 0)):.2f}",
        financial_status=fin_status,
        wd_total_cnt=wd_total_cnt,
        wd_total_amt=f"{wd_total_amt:.2f}",
        wd_paid_cnt=wd_map["paid"][0],
        wd_paid_amt=f"{wd_map['paid'][1]:.2f}",
        wd_pend_cnt=wd_map["pending"][0],
        wd_pend_amt=f"{wd_map['pending'][1]:.2f}",
        wd_canc_cnt=wd_map["cancelled"][0],
        wd_canc_amt=f"{wd_map['cancelled'][1]:.2f}",
        wd_rej_cnt=wd_map["rejected"][0],
        wd_rej_amt=f"{wd_map['rejected'][1]:.2f}",
        videos_submitted=sub_v_total,
        videos_approved=app_v_total,
        videos_bot_approved=bot_app_v,
        videos_admin_approved=adm_app_v,
        videos_perm_approved=perm_app_v,
        videos_pending=pend_v,
        videos_rejected=rej_v,
        leaderboard_progress=lb_prog["summary_line"],
        ref_count=u.get("ref_count", 0),
        ref_code=esc(ref_code_disp),
        bio_code=esc(u.get("bio_verify_code")),
        unique_code=esc(u.get("active_video_code")),
        global_code=esc(g_code),
        channel_url=esc(u.get("channel_url") or "Connected")
    )
    if is_admin_impersonation:
        txt = f"👁️ <b>[অ্যাডমিন লগইন প্রিভিউ মোড — {esc(get_user_label(u))}]</b>\n\n" + txt

    kb = types.InlineKeyboardMarkup()
    for p in plats:
        p_title = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
        kb.row(make_btn(f"🔗 Open Link ({p_title}: {p['display_name'][:18]})", url=p["profile_url"], style="primary"))

    if not is_admin_impersonation:
        # Part 4, Items 46–47: Keep ONLY Leaderboard, Change Password, Logout, Back to Home Page inside Dashboard!
        dash_kb = build_dynamic_page_inline_keyboard("user_dashboard", uid=uid, u_obj=u, msg_key="dashboard_msg")
        for r in dash_kb.keyboard:
            kb.row(*r)
    else:
        kb.row(make_btn("🔙 ইউজার কন্ট্রোলে ফিরে যান", callback_data=f"adm_uview:{u['user_id']}", style="danger"))
    return txt, kb


# ==============================================================================
# PART 5: USER PROFILE (6 BUTTONS ONLY; CHANGE NAME HAS ONLY NAME & APP UID)
# ==============================================================================
def render_user_profile_view(uid, u=None):
    u = u or get_user(uid)
    t_uid = str(u["user_id"])
    plats = get_user_platforms(t_uid)
    plat_lines = []
    for idx_p, p in enumerate(plats, start=1):
        p_t = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
        tot_v = int(p.get("total_videos_count") or 0)
        q_vids = int(p.get("qualifying_vids_count") or 0)
        q_views = int(p.get("qualifying_views_total") or 0)
        plat_lines.append(
            f"• {p_t} #{idx_p} ({p['display_name']} — সাবস্ক্রাইবার/ফলোয়ার: {p['subs_count']}, মোট ভিডিও: {tot_v}টি, যোগ্য ভিডিও: {q_vids}টি, যোগ্য ভিউজ: {q_views})"
        )
    plat_summary = "\n".join(plat_lines) if plat_lines else "কোনো প্ল্যাটফর্ম যুক্ত নেই"
    pay_summary = format_user_payment_numbers_summary(u)
    ch_names_summary = format_user_platform_channel_names(u, plats)

    txt = get_msg(
        "profile_msg",
        user_label=esc(get_user_label(u)),
        user_id=esc(t_uid),
        name=esc(u.get("name")),
        channel_name=esc(ch_names_summary),
        app_uid=esc(format_display_app_uid(u.get("app_uid"))),
        phone=esc(pay_summary),
        platforms_summary=esc(plat_summary),
        bio_code=esc(u.get("bio_verify_code")),
        unique_code=esc(u.get("active_video_code"))
    )
    kb = types.InlineKeyboardMarkup()
    for p in plats:
        p_t = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
        kb.row(make_btn(f"🔗 {p_t}: {p['display_name'][:20]}", url=p["profile_url"], style="primary"))

    # Part 5, Item 51: 6 Profile Buttons (Change Name, Change Withdraw Number, Add New Account, Change Password, Back to Dashboard, Back to Home Page)
    prof_kb = build_dynamic_page_inline_keyboard("user_profile", uid=uid, u_obj=u, msg_key="profile_msg")
    for r in prof_kb.keyboard:
        kb.row(*r)
    return txt, kb


@bot.callback_query_handler(func=lambda c: (
    c.data in ("uprof_name_menu", "uprof_wd_num_menu")
    or c.data.startswith("uprof_edit:")
    or c.data.startswith("uprof_wd_manage:")
    or c.data.startswith("uprof_wd_del:")
    or c.data == "uprof_ch_name_menu"
))
@_guard("uprof_edit")
def handle_user_profile_edit_prompt(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u or not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return

    if call.data == "uprof_name_menu":
        # 3 options inside Change Name submenu: (1) Own Name, (2) Battle Club App UID, (3) Verified Account / Platform Name
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("✏️ নিজের নাম পরিবর্তন করুন", callback_data="uprof_edit:name", style="success"))
        kb.row(make_btn("🆔 Battle Club অ্যাপের UID পরিবর্তন করুন", callback_data="uprof_edit:app_uid", style="primary"))
        kb.row(make_btn("📺 ভেরিফিকেশন অ্যাকাউন্টের নাম পরিবর্তন করুন", callback_data="uprof_ch_name_menu", style="success"))
        append_page_edit_tools(kb, uid, msg_key="profile_name_submenu_msg")
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("profile_name_submenu_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "uprof_ch_name_menu":
        plats = get_user_platforms(uid)
        if len(plats) <= 1:
            call.data = f"uprof_edit:platform_acc_name:{plats[0]['id']}" if plats else "uprof_edit:channel_name"
        else:
            kb = types.InlineKeyboardMarkup()
            for idx_p, p in enumerate(plats, start=1):
                p_t = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
                ord_bn = ORDINAL_ACCOUNT_LABELS_BN.get(idx_p, f"#{idx_p} অ্যাকাউন্ট")
                kb.row(make_btn(f"📺 {p_t} ({ord_bn}: {p['display_name'][:20]})", callback_data=f"uprof_edit:platform_acc_name:{p['id']}", style="primary"))
            kb.row(make_btn("🔙 নাম পরিবর্তন মেনুতে ফিরে যান", callback_data="uprof_name_menu", style="danger"))
            safe_edit(
                call.message.chat.id,
                call.message.message_id,
                f"📺 <b>কোন ভেরিফিকেশন অ্যাকাউন্টের নাম পরিবর্তন করতে চান?</b>\n{FULL_WIDTH_DIVIDER}\nনিচের তালিকা থেকে অ্যাকাউন্ট সিলেক্ট করুন:",
                reply_markup=kb
            )
            bot.answer_callback_query(call.id)
            return

    if call.data.startswith("uprof_wd_del:"):
        _, col_k, slot_s = call.data.split(":", 2)
        slot_idx = int(slot_s) if slot_s.isdigit() else 0
        with db_lock:
            del_res = update_user_payment_and_profile_info(uid, f"{col_k}:delete:{slot_idx}", "", action="delete", slot_index=slot_idx)
        if not del_res.get("ok"):
            bot.answer_callback_query(call.id, del_res.get("reason", "ডিলিট করা যায়নি!"), show_alert=True)
        else:
            bot.answer_callback_query(call.id, "🗑️ নাম্বার/UID সফলভাবে ডিলিট করা হয়েছে! এখন চাইলে নতুন আরেকটি যুক্ত করতে পারবেন।", show_alert=True)
        m_back_map = {"bkash_number": "bKash", "nagad_number": "Nagad", "rocket_number": "Rocket", "app_uid": "BattleClub_UID"}
        call.data = f"uprof_wd_manage:{m_back_map.get(col_k, 'bKash')}"
        u = get_user(uid) or u

    if call.data.startswith("uprof_wd_manage:"):
        m_key = call.data.split(":", 1)[1]
        col_map = {"bKash": "bkash_number", "Nagad": "nagad_number", "Rocket": "rocket_number", "BattleClub_UID": "app_uid"}
        col_k = col_map.get(m_key, "bkash_number")
        slots = get_user_saved_numbers_list(u, m_key)
        m_title = PAYMENT_PLATFORM_LABELS.get(m_key, m_key)
        kb = types.InlineKeyboardMarkup()
        lines = [
            f"📱 <b>{m_title} — নাম্বার / UID ম্যানেজার (সর্বোচ্চ ২টি):</b>",
            FULL_WIDTH_DIVIDER,
            f"• বর্তমানে সংরক্ষিত আছে: <b>{len(slots)}/2টি</b>"
        ]
        for idx_s, s_val in enumerate(slots):
            lines.append(f"  ├ <b>#{idx_s+1}:</b> <code>{esc(s_val)}</code>")
            row_btns = [
                make_btn(f"✏️ #{idx_s+1} পরিবর্তন ({s_val})", callback_data=f"uprof_edit:{col_k}:replace:{idx_s}", style="primary")
            ]
            if len(slots) > 1 or m_key != "BattleClub_UID":
                row_btns.append(make_btn(f"🗑️ #{idx_s+1} ডিলিট করুন", callback_data=f"uprof_wd_del:{col_k}:{idx_s}", style="danger"))
            kb.row(*row_btns)
        if len(slots) < 2:
            kb.row(make_btn(f"➕ নতুন {m_title} যুক্ত করুন ({len(slots)+1}/2)", callback_data=f"uprof_edit:{col_k}:add", style="success"))
        else:
            lines.append("\n⚠️ <i>সর্বোচ্চ ২টি পূর্ণ হয়েছে! নতুন আরেকটি সেট করতে উপরের যেকোনো ১টি ডিলিট বা পরিবর্তন করুন।</i>")
        kb.row(make_btn("🔙 উইথড্র নাম্বার মেনুতে ফিরে যান", callback_data="uprof_wd_num_menu", style="primary"))
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, "\n".join(lines), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "uprof_wd_num_menu":
        # Support up to 2 numbers/UIDs per method across all 4 methods: bKash, Nagad, Rocket, and Battle Club App UID!
        kb = types.InlineKeyboardMarkup()
        summary_lines = []
        btn_meta = [
            ("bKash", "🌸 বিকাশ নাম্বার", "uprof_wd_manage:bKash", "danger"),
            ("Nagad", "🍊 নগদ নাম্বার", "uprof_wd_manage:Nagad", "success"),
            ("Rocket", "🚀 রকেট নাম্বার", "uprof_wd_manage:Rocket", "primary"),
            ("BattleClub_UID", "🎮 Battle Club App UID", "uprof_wd_manage:BattleClub_UID", "success"),
        ]
        for m_key, b_lbl, b_cb, b_st in btn_meta:
            slots = get_user_saved_numbers_list(u, m_key)
            disp_n = ", ".join(slots) if slots else "যুক্ত নেই — নতুন যুক্ত করুন"
            summary_lines.append(f"│ • {PAYMENT_PLATFORM_LABELS.get(m_key, m_key)} ({len(slots)}/2): <code>{esc(disp_n)}</code>")
            kb.row(make_btn(f"{b_lbl} ({len(slots)}/2টি যুক্ত)", callback_data=b_cb, style=b_st))
        append_page_edit_tools(kb, uid, msg_key="profile_wd_num_submenu_msg")
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        txt = get_msg("profile_wd_num_submenu_msg", selected_methods_summary="\n".join(summary_lines))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    raw_field_spec = call.data.split(":", 1)[1]
    base_field = raw_field_spec.split(":")[0] if not raw_field_spec.startswith("platform_acc_name:") else "channel_name"
    field_labels = {
        "name": "অ্যাকাউন্টের নাম",
        "app_uid": "Battle Club অ্যাপের UID (#1007)",
        "bkash_number": "🌸 বিকাশ (bKash) নাম্বার",
        "nagad_number": "🍊 নগদ (Nagad) নাম্বার",
        "rocket_number": "🚀 রকেট (Rocket) নাম্বার",
        "channel_name": "📺 ভেরিফিকেশন অ্যাকাউন্ট / চ্যানেলের নাম"
    }
    if base_field not in field_labels:
        bot.answer_callback_query(call.id, "অবৈধ প্রোফাইল ফিল্ড!", show_alert=True)
        return

    # Check 2-slot cap if action is ':add'
    if ":add" in raw_field_spec:
        m_check_map = {"bkash_number": "bKash", "nagad_number": "Nagad", "rocket_number": "Rocket", "app_uid": "BattleClub_UID"}
        m_chk = m_check_map.get(base_field)
        if m_chk and len(get_user_saved_numbers_list(u, m_chk)) >= 2:
            bot.answer_callback_query(call.id, "⚠️ সর্বোচ্চ ২টি নাম্বার/UID সেট করা যাবে! নতুন যুক্ত করতে আগের যেকোনো ১টি ডিলিট বা পরিবর্তন করুন।", show_alert=True)
            return

    lbl = field_labels[base_field]
    kb = types.InlineKeyboardMarkup()

    if base_field in ("name", "app_uid", "channel_name") and not raw_field_spec.startswith("app_uid:"):
        user_memory_states[uid] = {"step": "awaiting_profile_update", "field": raw_field_spec}
        msg_k = "profile_uid_edit_prompt_msg" if base_field == "app_uid" else "profile_name_edit_prompt_msg"
        append_page_edit_tools(kb, uid, msg_key=msg_k)
        kb.row(make_btn("🔙 নাম পরিবর্তন মেনুতে ফিরে যান", callback_data="uprof_name_menu", style="primary"))
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg(msg_k, field_label=lbl),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return
    field = raw_field_spec

    # Require one-time Admin Random Code (`BC-XXXXXX`) both to add a new payment number and to change an existing payment number!
    unlocked_until = float(u.get("profile_edit_unlocked_until") or 0)
    if unlocked_until > time.time():
        user_memory_states[uid] = {"step": "awaiting_profile_update", "field": field}
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("profile_random_code_verified_msg", field_label=lbl),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    user_memory_states[uid] = {"step": "awaiting_profile_edit_random_code", "field": field}
    sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
    code_kb = types.InlineKeyboardMarkup()
    code_kb.row(make_btn("💬 অ্যাডমিনের থেকে র‍্যান্ডম কোড নিন", url=sup_url, style="primary"))
    code_kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
    append_page_edit_tools(code_kb, uid, msg_key="profile_random_code_prompt_msg")
    safe_edit(
        call.message.chat.id,
        call.message.message_id,
        get_msg("profile_random_code_prompt_msg", field_label=lbl),
        reply_markup=code_kb
    )
    bot.answer_callback_query(call.id, "অ্যাডমিনের র‍্যান্ডম কোড দিয়ে ভেরিফাই করুন!")


# ==============================================================================
# PART 7: MY VIDEOS (PLATFORM -> ORDINAL ACCOUNT -> 6 VIDEO CATEGORIES)
# ==============================================================================
def render_my_videos_platform_hub(uid: str, u: dict = None):
    u = u or get_user(uid)
    plats = get_user_platforms(uid)
    yt_cnt = sum(1 for p in plats if str(p.get("platform")).lower() == "youtube")
    tt_cnt = sum(1 for p in plats if str(p.get("platform")).lower() == "tiktok")

    kb = types.InlineKeyboardMarkup()
    if yt_cnt > 0:
        kb.row(make_btn(f"📺 YouTube ({yt_cnt}টি অ্যাকাউন্ট)", callback_data="umyvid_plat:youtube", style="danger"))
    if tt_cnt > 0:
        kb.row(make_btn(f"🎵 TikTok ({tt_cnt}টি অ্যাকাউন্ট)", callback_data="umyvid_plat:tiktok", style="primary"))
    if yt_cnt == 0 and tt_cnt == 0:
        kb.row(
            make_btn("📺 YouTube", callback_data="umyvid_plat:youtube", style="danger"),
            make_btn("🎵 TikTok", callback_data="umyvid_plat:tiktok", style="primary")
        )
    append_page_edit_tools(kb, uid, msg_key="my_videos_platform_select_msg")
    kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
    return get_msg("my_videos_platform_select_msg"), kb


@bot.callback_query_handler(func=lambda c: c.data.startswith("umyvid_plat:") or c.data.startswith("umyvid_acc:"))
@_guard("my_videos_hierarchy")
def handle_my_videos_hierarchy(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u or not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return

    if call.data.startswith("umyvid_plat:"):
        plat = call.data.split(":", 1)[1].lower()
        if plat not in ("youtube", "tiktok"):
            plat = "youtube"
        plats = get_user_platforms(uid, plat)
        kb = types.InlineKeyboardMarkup()
        st_col = "danger" if plat == "youtube" else "primary"
        if not plats:
            kb.row(make_btn("🔙 প্ল্যাটফর্ম সিলেকশনে ফিরে যান", callback_data="umenu:my_videos", style="primary"))
            kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_edit(
                call.message.chat.id,
                call.message.message_id,
                f"📭 আপনার কোনো ভেরিফাইড <b>{PLATFORMS[plat]['title']}</b> অ্যাকাউন্ট যুক্ত নেই।",
                reply_markup=kb
            )
            bot.answer_callback_query(call.id)
            return

        # Part 7, Items 73–74: Show exact number of bound accounts labeled in order of addition (First Account, Second Account...)
        for idx_p, p in enumerate(plats, start=1):
            ord_lbl = ORDINAL_ACCOUNT_LABELS_BN.get(idx_p, f"#{idx_p} অ্যাকাউন্ট")
            disp_n = p.get("display_name") or p.get("profile_handle") or f"Account {idx_p}"
            kb.row(make_btn(f"🎬 {ord_lbl} — {disp_n}", callback_data=f"umyvid_acc:{plat}:{p['id']}:all:0", style=st_col))

        append_page_edit_tools(kb, uid, msg_key="my_videos_account_select_msg")
        kb.row(make_btn("🔙 প্ল্যাটফর্ম সিলেকশনে ফিরে যান", callback_data="umenu:my_videos", style="primary"))
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        txt = get_msg(
            "my_videos_account_select_msg",
            platform_title=PLATFORMS[plat]["title"],
            account_count=len(plats)
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("umyvid_acc:"):
        parts = call.data.split(":")
        plat = parts[1].lower()
        acc_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        flt = parts[3] if len(parts) > 3 else "all"
        p_idx = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
        per_p = 8

        plats = get_user_platforms(uid, plat)
        chosen_idx = 1
        chosen_p = None
        for idx_p, p in enumerate(plats, start=1):
            if int(p.get("id") or 0) == acc_id:
                chosen_idx = idx_p
                chosen_p = p
                break
        if acc_id > 0 and not chosen_p:
            bot.answer_callback_query(call.id, "⛔ অবৈধ বা অননুমোদিত অ্যাকাউন্ট আইডি!", show_alert=True)
            return
        if not chosen_p and plats:
            chosen_p = plats[0]
            chosen_idx = 1
            acc_id = int(chosen_p.get("id") or 0)

        with db_lock:
            conn = get_connection()
            if len(plats) <= 1:
                all_vids = conn.execute(
                    "SELECT * FROM videos WHERE user_id = ? AND LOWER(platform) = ? AND COALESCE(is_trashed, 0) = 0 ORDER BY rowid DESC",
                    (uid, plat)
                ).fetchall()
            else:
                all_vids = conn.execute(
                    "SELECT * FROM videos WHERE user_id = ? AND LOWER(platform) = ? AND COALESCE(is_trashed, 0) = 0 AND (platform_account_id = ? OR (? = 1 AND COALESCE(platform_account_id, 0) = 0)) ORDER BY rowid DESC",
                    (uid, plat, acc_id, chosen_idx)
                ).fetchall()
            conn.close()

        c_pend, c_bot, c_adm, c_perm, c_rej = 0, 0, 0, 0, 0
        tot_vid_earn = 0.0
        filtered = []
        for vr in all_vids:
            cred = float(vr["credited_amount"] or vr["reward"] or 0.0)
            if vr["admin_status"] == "rejected" or vr["bot_status"] == "rejected" or vr["status"] == "rejected":
                c_rej += 1
                v_cat = "rejected"
            elif int(vr["permanent_approved"] or 0) == 1:
                c_perm += 1
                tot_vid_earn += cred
                v_cat = "permanent_approved"
            elif vr["admin_status"] == "approved":
                c_adm += 1
                tot_vid_earn += cred
                v_cat = "admin_approved"
            elif vr["bot_status"] == "approved":
                c_bot += 1
                tot_vid_earn += cred
                v_cat = "bot_approved"
            else:
                c_pend += 1
                v_cat = "pending"
            if flt == "all" or flt == v_cat or (flt == "approved" and v_cat in ("admin_approved", "permanent_approved")):
                filtered.append((vr, v_cat, cred))

        p_meta = paginate_items(filtered, page=p_idx, per_page=per_p)
        kb = types.InlineKeyboardMarkup()
        # Part 7, Item 75: 6 Video Status Categories (All, Pending, Bot Approved, Admin Approved, Permanent Approved, Rejected)
        kb.row(
            make_btn(f"{'✅ ' if flt=='all' else ''}📋 সব ভিডিও ({len(all_vids)})", callback_data=f"umyvid_acc:{plat}:{acc_id}:all:0", style="primary"),
            make_btn(f"{'✅ ' if flt=='pending' else ''}⏳ পেন্ডিং ({c_pend})", callback_data=f"umyvid_acc:{plat}:{acc_id}:pending:0", style="primary")
        )
        kb.row(
            make_btn(f"{'✅ ' if flt=='bot_approved' else ''}🤖 বট অ্যাপ্রুভ ({c_bot})", callback_data=f"umyvid_acc:{plat}:{acc_id}:bot_approved:0", style="success"),
            make_btn(f"{'✅ ' if flt=='admin_approved' else ''}👑 অ্যাডমিন অ্যাপ্রুভ ({c_adm})", callback_data=f"umyvid_acc:{plat}:{acc_id}:admin_approved:0", style="success")
        )
        kb.row(
            make_btn(f"{'✅ ' if flt=='permanent_approved' else ''}🔒 পার্মানেন্ট অ্যাপ্রুভ ({c_perm})", callback_data=f"umyvid_acc:{plat}:{acc_id}:permanent_approved:0", style="success"),
            make_btn(f"{'✅ ' if flt=='rejected' else ''}❌ রিজেক্টেড ({c_rej})", callback_data=f"umyvid_acc:{plat}:{acc_id}:rejected:0", style="danger")
        )
        for vr, v_cat, cred in p_meta["items"]:
            ic = "🔒" if v_cat == "permanent_approved" else ("👑" if v_cat == "admin_approved" else ("🤖" if v_cat == "bot_approved" else ("❌" if v_cat == "rejected" else "⏳")))
            kb.row(make_btn(f"{ic} [{vr['platform'].upper()}] {vr['current_views']} ভিউ — {cred:.1f}৳", callback_data=f"umyvid_item:{vr['sub_id']}:{plat}:{acc_id}:{flt}:{p_meta['page']}", style="primary"))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"umyvid_acc:{plat}:{acc_id}:{flt}")
        if nav_row:
            kb.row(*nav_row)
        # Part 7, Item 76: NO "New Video Submit" button inside My Videos; include Back buttons!
        append_page_edit_tools(kb, uid, msg_key="my_videos_list_msg")
        kb.row(
            make_btn("🔙 অ্যাকাউন্ট তালিকায় যান", callback_data=f"umyvid_plat:{plat}", style="primary"),
            make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
        )
        ord_lbl = ORDINAL_ACCOUNT_LABELS_BN.get(chosen_idx, f"#{chosen_idx} অ্যাকাউন্ট")
        acc_disp = f"{PLATFORMS[plat]['title']} ({ord_lbl} — {chosen_p['display_name'] if chosen_p else ''}) [{flt.upper()}]"
        txt = get_msg(
            "my_videos_list_msg",
            filter_title=esc(acc_disp),
            page=p_meta["page"] + 1,
            total_pages=p_meta["total_pages"],
            total_vids=len(all_vids),
            pending_cnt=c_pend,
            bot_approved_cnt=c_bot,
            admin_approved_cnt=c_adm,
            perm_approved_cnt=c_perm,
            rejected_cnt=c_rej,
            total_earned=f"{tot_vid_earn:.2f}",
            items_hint=("👇 নিচের যেকোনো ভিডিও বাটনে ক্লিক করে সম্পূর্ণ বিস্তারিত দেখুন:" if p_meta["items"] else "📭 এই ক্যাটাগরিতে কোনো ভিডিও নেই।")
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return


# ==============================================================================
# DYNAMIC PAYMENT LIST HUB & SUBVIEWS (upay_wd, upay_plat, upay_ledger)
# ==============================================================================
def render_user_payment_list_hub(uid: str, u: dict = None):
    u = u or get_user(uid)
    u_plats = get_user_platforms(uid)
    verified_plat_keys = []
    for p in u_plats:
        pk = str(p["platform"]).lower()
        if pk not in verified_plat_keys and pk in ("youtube", "tiktok"):
            verified_plat_keys.append(pk)

    with db_lock:
        conn = get_connection()
        wd_rows = conn.execute(
            "SELECT status, COUNT(*) as c, COALESCE(SUM(amount), 0) as s FROM withdrawals WHERE user_id = ? GROUP BY status",
            (uid,)
        ).fetchall()
        vid_rows = conn.execute("""
            SELECT LOWER(platform) as plat,
                   COUNT(*) as total_v,
                   SUM(CASE WHEN (bot_status = 'approved' OR admin_status = 'approved' OR COALESCE(permanent_approved, 0) = 1)
                             AND admin_status != 'rejected' AND status != 'rejected' THEN 1 ELSE 0 END) as app_v,
                   COALESCE(SUM(CASE WHEN credited_amount > 0 THEN credited_amount ELSE reward END), 0) as earned_s,
                   COALESCE(SUM(reversed_amount), 0) as rev_s
            FROM videos
            WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0 AND LOWER(platform) IN ('youtube', 'tiktok')
            GROUP BY LOWER(platform)
        """, (uid,)).fetchall()
        conn.close()

    wd_total_cnt, wd_total_amt = 0, 0.0
    wd_paid_cnt, wd_paid_amt = 0, 0.0
    wd_pend_cnt, wd_pend_amt = 0, 0.0
    wd_rej_cnt, wd_rej_amt = 0, 0.0
    for wr in wd_rows:
        c_val = int(wr["c"] or 0)
        s_val = float(wr["s"] or 0.0)
        wd_total_cnt += c_val
        wd_total_amt += s_val
        if wr["status"] == "paid":
            wd_paid_cnt += c_val
            wd_paid_amt += s_val
        elif wr["status"] == "pending":
            wd_pend_cnt += c_val
            wd_pend_amt += s_val
        elif wr["status"] in ("rejected", "cancelled"):
            wd_rej_cnt += c_val
            wd_rej_amt += s_val

    plat_stats = {r["plat"]: r for r in vid_rows}
    plat_lines = []
    for pk in verified_plat_keys:
        p_title = PLATFORMS.get(pk, {}).get("title", pk.upper())
        pr = plat_stats.get(pk)
        v_cnt = int(pr["total_v"] or 0) if pr else 0
        e_amt = float(pr["earned_s"] or 0.0) if pr else 0.0
        r_amt = float(pr["rev_s"] or 0.0) if pr else 0.0
        plat_lines.append(
            f"• <b>{esc(p_title)}</b>: মোট ভিডিও <b>{v_cnt}টি</b> | আয়: <b>{e_amt:.2f}৳</b> | কর্তন: <b>{r_amt:.2f}৳</b>"
        )
    if not plat_lines:
        plat_lines.append("• এখনো কোনো ভেরিফাইড প্ল্যাটফর্ম যুক্ত নেই।")

    txt = get_msg(
        "payment_list_hub_msg",
        wd_total_cnt=wd_total_cnt,
        wd_total_amt=f"{wd_total_amt:.2f}",
        wd_paid_cnt=wd_paid_cnt,
        wd_paid_amt=f"{wd_paid_amt:.2f}",
        wd_pend_cnt=wd_pend_cnt,
        wd_pend_amt=f"{wd_pend_amt:.2f}",
        wd_rej_cnt=wd_rej_cnt,
        wd_rej_amt=f"{wd_rej_amt:.2f}",
        platform_breakdown="\n".join(plat_lines)
    )

    kb = types.InlineKeyboardMarkup()
    kb.row(
        make_btn(f"⏳ পেন্ডিং উইথড্র ({wd_pend_cnt}টি)", callback_data="upay_wd:pending:0", style="primary"),
        make_btn(f"✅ কমপ্লিট উইথড্র ({wd_paid_cnt}টি)", callback_data="upay_wd:paid:0", style="success")
    )
    kb.row(
        make_btn(f"❌ রিজেক্টেড উইথড্র ({wd_rej_cnt}টি)", callback_data="upay_wd:rejected:0", style="danger"),
        make_btn(f"📤 সব উইথড্র ({wd_total_cnt}টি)", callback_data="upay_wd:all:0", style="primary")
    )

    style_map = {"youtube": "danger", "tiktok": "primary"}
    for pk in verified_plat_keys:
        p_title = PLATFORMS.get(pk, {}).get("title", pk.upper())
        pr = plat_stats.get(pk)
        v_cnt = int(pr["total_v"] or 0) if pr else 0
        e_amt = float(pr["earned_s"] or 0.0) if pr else 0.0
        kb.row(
            make_btn(
                f"{p_title} পেমেন্ট ({v_cnt}টি ভিডিও — {e_amt:.2f}৳)",
                callback_data=f"upay_plat:{pk}:0",
                style=style_map.get(pk, "primary")
            )
        )

    kb.row(make_btn("📜 সম্পূর্ণ লেজার লেনদেন হিস্ট্রি", callback_data="upay_ledger:0", style="primary"))
    append_page_edit_tools(kb, uid, msg_key="payment_list_hub_msg")
    kb.row(make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
    return txt, kb


@bot.callback_query_handler(func=lambda c: c.data.startswith("upay_wd:") or c.data.startswith("upay_plat:") or c.data.startswith("upay_ledger:"))
@_guard("user_payment_subview")
def handle_user_payment_list_subviews(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u or not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return
    user_memory_states.pop(uid, None)

    if call.data.startswith("upay_wd:"):
        parts = call.data.split(":")
        st_flt = parts[1] if len(parts) > 1 else "all"
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        per_p = 8
        with db_lock:
            conn = get_connection()
            if st_flt == "paid":
                rows = conn.execute("SELECT * FROM withdrawals WHERE user_id = ? AND status = 'paid' ORDER BY rowid DESC", (uid,)).fetchall()
                st_title = "কমপ্লিট হওয়া উইথড্র রিকোয়েস্ট"
            elif st_flt == "pending":
                rows = conn.execute("SELECT * FROM withdrawals WHERE user_id = ? AND status = 'pending' ORDER BY rowid DESC", (uid,)).fetchall()
                st_title = "পেন্ডিং উইথড্র রিকোয়েস্ট"
            elif st_flt == "rejected":
                rows = conn.execute("SELECT * FROM withdrawals WHERE user_id = ? AND status IN ('rejected', 'cancelled') ORDER BY rowid DESC", (uid,)).fetchall()
                st_title = "রিজেক্টেড / বাতিল উইথড্র রিকোয়েস্ট"
            else:
                rows = conn.execute("SELECT * FROM withdrawals WHERE user_id = ? ORDER BY rowid DESC", (uid,)).fetchall()
                st_title = "সকল উইথড্র রিকোয়েস্ট"
            conn.close()

        tot_amt = sum(float(r["amount"] or 0.0) for r in rows)
        p_meta = paginate_items(rows, page=page, per_page=per_p)
        lines = []
        for r in p_meta["items"]:
            st_lbl = "✅ COMPLETED" if r["status"] == "paid" else ("🚫 CANCELLED (Refunded)" if r["status"] == "cancelled" else ("❌ REJECTED (Refunded)" if r["status"] == "rejected" else "⏳ PENDING"))
            trx_note = f"\n  ├ নোট/TrxID: <code>{esc(r['trx_id'] or r['decision_reason'])}</code>" if (r["trx_id"] or r["decision_reason"]) else ""
            d_s, t_s = _split_datetime_str(r["created_at"])
            lines.append(
                f"• <b>{float(r['amount']):.2f}৳ ({esc(r['method'])})</b> — <b>{st_lbl}</b>\n"
                f"  ├ নাম্বার/UID: <code>{esc(format_display_app_uid(r['dest']) if r['method']=='BattleClub_UID' else r['dest'])}</code>{trx_note}\n"
                f"  └ 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>"
            )
        items_txt = f"\n{FULL_WIDTH_DIVIDER}\n".join(lines) if lines else "📭 এই ক্যাটাগরিতে কোনো উইথড্র রেকর্ড পাওয়া যায়নি।"
        txt = get_msg(
            "payment_wd_status_msg",
            status_title=st_title,
            page=p_meta["page"] + 1,
            total_pages=p_meta["total_pages"],
            total_items=p_meta["total_items"],
            total_amount=f"{tot_amt:.2f}",
            items_text=items_txt
        )
        kb = types.InlineKeyboardMarkup()
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"upay_wd:{st_flt}")
        if nav_row:
            kb.row(*nav_row)
        append_page_edit_tools(kb, uid, msg_key="payment_wd_status_msg")
        kb.row(make_btn("🔙 পেমেন্ট লিস্টে ফিরে যান", callback_data="umenu:history", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("upay_plat:"):
        parts = call.data.split(":")
        plat_k = parts[1].lower()
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        per_p = 8
        with db_lock:
            conn = get_connection()
            v_rows = conn.execute(
                "SELECT * FROM videos WHERE user_id = ? AND LOWER(platform) = ? AND COALESCE(is_trashed, 0) = 0 ORDER BY rowid DESC",
                (uid, plat_k)
            ).fetchall()
            conn.close()

        tot_v = len(v_rows)
        app_v = sum(1 for v in v_rows if (v["bot_status"] == "approved" or v["admin_status"] == "approved" or int(v["permanent_approved"] or 0) == 1) and v["admin_status"] != "rejected" and v["status"] != "rejected")
        rej_v = sum(1 for v in v_rows if v["admin_status"] == "rejected" or v["bot_status"] == "rejected" or v["status"] == "rejected")
        earned_sum = sum(float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0)) for v in v_rows)
        ded_sum = sum(float(v["reversed_amount"] or 0.0) for v in v_rows)

        p_meta = paginate_items(v_rows, page=page, per_page=per_p)
        lines = []
        for idx, v in enumerate(p_meta["items"], start=(p_meta["page"] * per_p) + 1):
            cred = float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0))
            rev = float(v["reversed_amount"] or 0.0)
            if v["admin_status"] == "rejected" or v["bot_status"] == "rejected" or v["status"] == "rejected":
                st_s = f"❌ REJECTED (কর্তন: {rev:.2f}৳)"
            elif int(v["permanent_approved"] or 0) == 1:
                st_s = f"🔒 PERMANENT APPROVED (+{cred:.2f}৳)"
            elif v["admin_status"] == "approved":
                st_s = f"👑 ADMIN APPROVED (+{cred:.2f}৳)"
            elif v["bot_status"] == "approved":
                st_s = f"🤖 BOT APPROVED (+{cred:.2f}৳)"
            else:
                st_s = "⏳ PENDING (0.00৳)"
            d_s, t_s = _split_datetime_str(v["submitted_at"])
            lines.append(
                f"<b>#{idx}. {esc(v['title'][:32])}</b>\n"
                f"  ├ ভিউ: <b>{v['current_views']}</b> (পেইড ভিউ: <b>{v['paid_views']}</b>)\n"
                f"  ├ পেমেন্ট স্ট্যাটাস: <b>{st_s}</b>\n"
                f"  └ 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>"
            )
        items_txt = f"\n{FULL_WIDTH_DIVIDER}\n".join(lines) if lines else "📭 এই প্ল্যাটফর্মে এখনো কোনো ভিডিও সাবমিট করা হয়নি।"
        p_title = PLATFORMS.get(plat_k, {}).get("title", plat_k.upper())
        txt = get_msg(
            "payment_platform_detail_msg",
            platform_title=p_title,
            page=p_meta["page"] + 1,
            total_pages=p_meta["total_pages"],
            total_vids=tot_v,
            approved_vids=app_v,
            rejected_vids=rej_v,
            earned_amount=f"{earned_sum:.2f}",
            deducted_amount=f"{ded_sum:.2f}",
            items_text=items_txt
        )
        kb = types.InlineKeyboardMarkup()
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"upay_plat:{plat_k}")
        if nav_row:
            kb.row(*nav_row)
        append_page_edit_tools(kb, uid, msg_key="payment_platform_detail_msg")
        kb.row(make_btn("🔙 পেমেন্ট লিস্টে ফিরে যান", callback_data="umenu:history", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("upay_ledger:"):
        # Show the last 10 transactions in Payment List Ledger History
        page = int(call.data.split(":", 1)[1] or 0)
        per_p = 10
        with db_lock:
            conn = get_connection()
            all_rows = conn.execute("SELECT * FROM ledger_transactions WHERE user_id = ? ORDER BY rowid DESC LIMIT 10", (uid,)).fetchall()
            conn.close()
        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        lines = []
        for r in p_meta["items"]:
            v_ref = f" (Ref: <code>{esc(r['video_id'] or r['reference_id'])}</code>)" if (r["video_id"] or r["reference_id"]) else ""
            prev_b = float(r["previous_balance"] if r["previous_balance"] is not None else (r["before_balance"] or 0.0))
            new_b = float(r["new_balance"] if r["new_balance"] is not None else (r["after_balance"] or 0.0))
            amt_v = float(r["amount"] or 0.0)
            tx_t_raw = str(r["transaction_type"] or r["type"] or "")
            is_deduct = any(w in tx_t_raw.lower() for w in ("debit", "clawback", "reversal", "reserve", "forfeiture")) or amt_v < 0
            sign_lbl = f"-{abs(amt_v):.2f}৳ (কর্তন)" if is_deduct and new_b <= prev_b else f"+{abs(amt_v):.2f}৳ (যোগ)"
            d_s, t_s = _split_datetime_str(r["timestamp"] or r["created_at"])
            lines.append(
                f"💠 <b>{esc(_translate_tx_type_bn(tx_t_raw))}</b>{v_ref}\n"
                f"  ├ আগের ব্যালেন্স: <b>{prev_b:.2f}৳</b>\n"
                f"  ├ লেনদেন (যোগ/কর্তন): <b>{sign_lbl}</b>\n"
                f"  ├ নতুন ব্যালেন্স: <b>{new_b:.2f}৳</b>\n"
                f"  └ 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>"
            )
        items_txt = f"\n{FULL_WIDTH_DIVIDER}\n".join(lines) if lines else "📭 কোনো লেনদেন রেকর্ড পাওয়া যায়নি।"
        txt = get_msg(
            "payment_ledger_list_msg",
            page=p_meta["page"] + 1,
            total_pages=p_meta["total_pages"],
            balance=f"{float(u.get('balance', 0)):.2f}",
            debt_balance=f"{float(u.get('debt_balance', 0)):.2f}",
            items_text=items_txt
        )
        kb = types.InlineKeyboardMarkup()
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "upay_ledger")
        if nav_row:
            kb.row(*nav_row)
        append_page_edit_tools(kb, uid, msg_key="payment_ledger_list_msg")
        kb.row(make_btn("🔙 পেমেন্ট লিস্টে ফিরে যান", callback_data="umenu:history", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return


# ==============================================================================
# USER MENU CALLBACK ROUTER (DASHBOARD, PROFILE, MY VIDEOS, SETTINGS HUB, WITHDRAW)
# ==============================================================================
@bot.callback_query_handler(func=lambda c: c.data.startswith("umenu:"))
@_guard("user_menu")
def handle_user_menu_callbacks(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not u:
        return

    if u.get("status") == "banned":
        bot.answer_callback_query(call.id, "আপনার অ্যাকাউন্টটি ব্যান করা হয়েছে!", show_alert=True)
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("ch_banned_msg"))
        return

    parts_pre = call.data.split(":")
    act_pre = parts_pre[1] if len(parts_pre) > 1 else ""
    is_froz_u = bool(int(u.get("bio_frozen") or 0) == 1 or str(u.get("status") or "").lower() == "frozen")
    is_inact_u = bool(str(u.get("status") or "").lower() == "inactive" and not is_froz_u)

    # Frozen user: can do everything EXCEPT Withdraw and Video Submit!
    if is_froz_u and act_pre in ("withdraw", "submit_menu"):
        bot.answer_callback_query(call.id, "❄️ আপনার অ্যাকাউন্টটি বর্তমানে ফ্রিজ (Frozen) রয়েছে! ফ্রিজ অবস্থায় ভিডিও সাবমিট ও উইথড্র বন্ধ থাকে।", show_alert=True)
        sup_u = get_setting("support_link", "https://t.me/battleclubsupport")
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔄 বায়ো ও ভিডিও কোড রি-চেক এবং আনফ্রিজ করুন", callback_data="u_unfreeze_req", style="success"))
        kb.row(make_btn("💬 অফিসিয়াল সাপোর্টে যোগাযোগ করুন", url=sup_u, style="primary"))
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("ch_frozen_msg"), reply_markup=kb)
        return

    # Inactive user: can do everything EXCEPT Withdraw!
    if is_inact_u and act_pre == "withdraw":
        bot.answer_callback_query(call.id, "⏸️ আপনার অ্যাকাউন্টটি বর্তমানে ইনঅ্যাক্টিভ (Inactive) থাকায় উইথড্র রিকোয়েস্ট সাবমিট করা যাবে না!", show_alert=True)
        sup_u = get_setting("support_link", "https://t.me/battleclubsupport")
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("💬 অফিসিয়াল সাপোর্টে যোগাযোগ করুন", url=sup_u, style="primary"))
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("ch_inactive_msg"), reply_markup=kb)
        return

    parts = call.data.split(":")
    act = parts[1]
    page_arg = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    if act == "cancel_home":
        user_memory_states.pop(uid, None)
        if not u.get("registered") and not (is_admin_unlocked(uid)):
            send_onboarding_home(call.message.chat.id, uid, u)
            bot.answer_callback_query(call.id)
            return
        top_yt = get_setting("home_youtube_link", "")
        u_lang = (u.get("language") or "bn").lower()
        w_txt = attach_top_youtube_preview(get_msg("welcome_msg", lang=u_lang, name=esc(u.get("name")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid), top_yt)
        safe_edit(call.message.chat.id, call.message.message_id, w_txt, reply_markup=build_user_home_keyboard(uid, u), top_yt_url=top_yt, menu_id="user_home")
        bot.answer_callback_query(call.id)
        return

    if not u.get("registered") and not (is_admin_unlocked(uid)):
        bot.answer_callback_query(call.id, "আগে আপনার চ্যানেল ভেরিফিকেশন সম্পন্ন করুন!", show_alert=True)
        send_onboarding_home(call.message.chat.id, uid, u)
        return

    if not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return
    if act not in ("redeem", "pwd_change"):
        user_memory_states.pop(uid, None)

    if act == "how_to_work":
        u_lang = (u.get("language") or "bn").lower()
        top_yt = get_setting("home_youtube_link", "")
        tut_msg = get_msg("how_to_work_video_msg", lang=u_lang)
        kb = types.InlineKeyboardMarkup()
        if top_yt and str(top_yt).lower() not in ("none", "nane"):
            play_lbl = "▶️ Watch Tutorial Video (ভিডিও প্লে করুন)" if u_lang == "en" else "▶️ টিউটোরিয়াল ভিডিওটি প্লে করুন"
            kb.row(make_btn(play_lbl, url=top_yt, style="success"))
        else:
            no_v_note = "\n\n⚠️ <i>(অ্যাডমিন প্যানেল থেকে এখনো কোনো টিউটোরিয়াল ভিডিও লিংক যুক্ত করা হয়নি।)</i>" if u_lang != "en" else "\n\n⚠️ <i>(No tutorial video link has been configured by Admin yet.)</i>"
            tut_msg += no_v_note
        back_prof_lbl = get_btn_label("u_profile", lang=u_lang)
        back_home_lbl = get_btn_label("u_back_home", lang=u_lang)
        kb.row(
            make_btn(back_prof_lbl, callback_data="umenu:profile", style="primary"),
            make_btn(back_home_lbl, callback_data="umenu:cancel_home", style="danger")
        )
        append_page_edit_tools(kb, uid, msg_key="how_to_work_video_msg")
        full_tut_txt = attach_top_youtube_preview(tut_msg, top_yt)
        safe_edit(call.message.chat.id, call.message.message_id, full_tut_txt, reply_markup=kb, disable_preview=False, top_yt_url=top_yt)
        bot.answer_callback_query(call.id)
        return

    if act == "dashboard":
        user_memory_states.pop(uid, None)
        txt, kb = render_user_dashboard_view(uid, u)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "profile":
        user_memory_states.pop(uid, None)
        txt, kb = render_user_profile_view(uid, u)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "settings_hub":
        # Part 10, Items 95–100: User Settings Hub housing Refer, Redeem, Activity, Password Change, Button Color, Language, Menu Mode Toggle, Delete Account
        u_lang = "English (EN)" if (u.get("language") or "bn").lower() == "en" else "বাংলা (BN)"
        m_mode = "🟢 নিচের কিবোর্ড মেনু (Bottom Menu ON)" if is_user_bottom_menu_enabled(u) else "🔵 উপরের ইনলাইন বাটন (Inline Menu ON)"
        col_st = COLOR_PALETTE.get(u.get("user_btn_style") or "default", "ডিফল্ট (Default)")
        txt = get_msg(
            "user_settings_hub_msg",
            user_label=esc(get_user_label(u)),
            menu_mode_status=m_mode,
            lang_status=u_lang,
            color_status=col_st,
            menu_mode=m_mode,
            language=u_lang
        )
        kb = build_dynamic_page_inline_keyboard("user_settings_hub", uid=uid, u_obj=u, msg_key="user_settings_hub_msg")
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "menu_mode_toggle":
        # Part 10, Items 97–100: Toggle between Bottom Menu (`ReplyKeyboardMarkup`) and Top Message Box Buttons (`InlineKeyboardMarkup`) per user
        cur_bm = int(u.get("bottom_menu_enabled") or 0)
        new_bm = 0 if cur_bm == 1 else 1
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET bottom_menu_enabled = ? WHERE user_id = ?", (new_bm, uid))
            conn.close()
        u_fresh = get_user(uid)
        u_lang = (u_fresh.get("language") or "bn").lower()
        top_yt = get_setting("home_youtube_link", "")
        w_txt = attach_top_youtube_preview(get_msg("welcome_msg", lang=u_lang, name=esc(u_fresh.get("name")), balance=f"{float(u_fresh.get('balance', 0)):.2f}", user_id=uid), top_yt)
        if new_bm == 1:
            if getattr(call, "message", None) and getattr(call.message, "message_id", None):
                try:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                except Exception:
                    pass
            bot.answer_callback_query(call.id, "⌨️ নিচের ইনলাইন/মেনু বাটন চালু করা হয়েছে!")
            safe_send(
                call.message.chat.id,
                "✅ <b>নিচের মেনু বাটন (Bottom Menu) চালু হয়েছে!</b>\nএখন মেসেজ বক্সের উপরে কোনো বাটন আসবে না—সকল পেজ ও সাব-পেজের বাটন নিচে কালারফুলভাবে দেখা যাবে।\n\n" + w_txt,
                reply_markup=build_user_bottom_reply_keyboard(uid, u_fresh),
                top_yt_url=top_yt,
                menu_id="user_home"
            )
        else:
            USER_ACTIVE_BOTTOM_BUTTON_MAP.pop(uid, None)
            bot.answer_callback_query(call.id, "🔵 মেসেজ বক্সের উপরের বাটন চালু করা হয়েছে!")
            safe_send(
                call.message.chat.id,
                "✅ <b>মেসেজ বক্সের উপরের বাটন চালু হয়েছে!</b>\nনিচের বাটন বন্ধ করা হয়েছে।",
                reply_markup=types.ReplyKeyboardRemove()
            )
            safe_send(call.message.chat.id, w_txt, reply_markup=build_user_home_keyboard(uid, u_fresh, force_inline=True), top_yt_url=top_yt, menu_id="user_home")
        return

    if act in ("submit_menu", "submit_grp_confirmed"):
        is_cd, cd_txt = check_user_cooldown(u)
        if is_cd:
            bot.answer_callback_query(call.id, "আপনার ভিডিও সাবমিশন সাময়িক ব্লক রয়েছে!", show_alert=True)
            safe_send(call.message.chat.id, cd_txt)
            return
        u_plats = get_user_platforms(uid)
        verified_p_keys = []
        for p in u_plats:
            pk = p["platform"].lower()
            if pk in ("youtube", "tiktok") and pk not in verified_p_keys:
                verified_p_keys.append(pk)
        if not verified_p_keys:
            bot.answer_callback_query(call.id, "প্রথমে একটি প্ল্যাটফর্ম ভেরিফিকেশন সম্পন্ন করুন!", show_alert=True)
            call.data = "umenu:link_more"
            return handle_user_menu_callbacks(call)

        grp_url = str(get_setting("group_link", "https://t.me/battleclubcreator") or "").strip()
        if act == "submit_menu" and grp_url and grp_url.lower() not in ("none", "nane", "0", "off"):
            # Check if bot can verify live group membership or if user must confirm joining the group first
            grp_verified = False
            m_g = re.search(r"t\.me/([a-zA-Z0-9_]{4,})", grp_url)
            if m_g and not grp_url.startswith("https://t.me/+") and hasattr(bot, "get_chat_member") and BOT_TOKEN and not BOT_TOKEN.startswith("000000000:"):
                try:
                    cm = bot.get_chat_member("@" + m_g.group(1), int(uid))
                    if cm and getattr(cm, "status", "") in ("member", "administrator", "creator"):
                        grp_verified = True
                except Exception:
                    grp_verified = False
            if not grp_verified:
                bot.answer_callback_query(
                    call.id,
                    "📢 ভিডিও সাবমিট করার পূর্বে আমাদের অফিসিয়াল টেলিগ্রাম গ্রুপে জয়েন করুন!",
                    show_alert=True
                )
                g_kb = types.InlineKeyboardMarkup()
                g_kb.row(make_btn("👥 অফিসিয়াল গ্রুপে জয়েন করুন (Join Group)", url=grp_url, style="primary"))
                g_kb.row(make_btn("✅ জয়েন করেছি — ভিডিও সাবমিটে যান", callback_data="umenu:submit_grp_confirmed", style="success"))
                append_page_edit_tools(g_kb, uid, msg_key="video_submit_group_join_msg")
                g_kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
                safe_edit(call.message.chat.id, call.message.message_id, get_msg("video_submit_group_join_msg"), reply_markup=g_kb)
                return

        kb = types.InlineKeyboardMarkup()
        style_map = {"youtube": "danger", "tiktok": "primary"}
        for pk in verified_p_keys:
            p_cnt = len(get_user_platforms(uid, pk))
            cnt_lbl = f" ({p_cnt}টি অ্যাকাউন্ট)" if p_cnt > 1 else ""
            kb.row(make_btn(f"{PLATFORMS[pk]['title']} ভিডিও সাবমিট করুন{cnt_lbl}", callback_data=f"usub_plat:{pk}", style=style_map.get(pk, "primary")))
        append_page_edit_tools(kb, uid, msg_key="video_submit_plat_select_msg")
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("video_submit_plat_select_msg", platform_count=len(verified_p_keys)), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "link_more":
        debt_b = float(u.get("debt_balance", 0.0) or 0.0)
        bal_b = float(u.get("balance", 0.0) or 0.0)
        if debt_b > 0 or bal_b < 0:
            eff_debt = max(debt_b, abs(min(0.0, bal_b)))
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("💬 সাপোর্টে যোগাযোগ করুন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
            append_page_edit_tools(kb, uid, msg_key="debt_bind_block_msg")
            kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_edit(call.message.chat.id, call.message.message_id, get_msg("debt_bind_block_msg", debt_balance=f"{eff_debt:.2f}"), reply_markup=kb)
            bot.answer_callback_query(call.id, f"আপনার একাউন্টে {eff_debt:.2f}৳ ঋণ রয়েছে! আগে ঋণ পরিশোধ করুন।", show_alert=True)
            return
        kb = types.InlineKeyboardMarkup()
        for pk in ["youtube", "tiktok"]:
            crit = get_platform_criteria(pk)
            cur_cnt = len(get_user_platforms(uid, pk))
            kb.row(make_btn(f"{PLATFORMS[pk]['title']} যুক্ত করুন ({cur_cnt}/{crit['max_accounts']}টি)", callback_data=f"ulink_act:{pk}", style="primary"))
        # Part 7, Item 77: Use "Back to Home Page" instead of "Back to Dashboard" on Add New Account page!
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🌐 <b>নতুন অ্যাকাউন্ট যোগ করার জন্য প্ল্যাটফর্ম (YouTube / TikTok) বেছে নিন:</b>\n{FULL_WIDTH_DIVIDER}\n(অ্যাডমিন নির্ধারিত সাবস্ক্রাইবার/ফলোয়ার, মোট ভিডিও, যোগ্য ভিডিও, ভিউ ও বায়ো কোড ভেরিফিকেশন ১০০% সম্পূর্ণ হওয়ার পর যুক্ত হবে)",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if act == "withdraw":
        user_memory_states.pop(uid, None)
        debt_b = float(u.get("debt_balance", 0.0) or 0.0)
        if debt_b > 0:
            bot.answer_callback_query(call.id, f"বকেয়া ঋণ ({debt_b:.2f}৳) পরিশোধ না হওয়া পর্যন্ত নতুন উইথড্র করা যাবে না!", show_alert=True)
            return
        bal = float(u.get("balance", 0.0))
        min_w = float(get_setting("min_withdraw", "100.0"))
        max_d_cnt = int(get_setting("max_daily_wd_count", "2"))
        max_d_amt = float(get_setting("max_daily_wd_amount", "5000.0"))
        today_s = datetime.now().strftime("%Y-%m-%d")

        d_cnt = int(u.get("daily_wd_count", 0)) if u.get("daily_wd_date") == today_s else 0
        d_amt = float(u.get("daily_wd_amount", 0.0)) if u.get("daily_wd_date") == today_s else 0.0
        rem_cnt = max(0, max_d_cnt - d_cnt)
        rem_amt = max(0.0, round(max_d_amt - d_amt, 2))

        if bal <= 0 or bal < min_w:
            # Strict Withdraw Lock: User cannot enter the Withdraw Request page at all when balance < min_withdraw!
            need_more = max(0.0, round(min_w - bal, 2))
            lock_alert = (
                f"🔒 উইথড্র রিকোয়েস্ট লক রয়েছে!\n"
                f"আপনার পর্যাপ্ত পরিমাণ ব্যালেন্স নেই (বর্তমান ব্যালেন্স: {bal:.2f}৳)।\n"
                f"আপনি ন্যূনতম {min_w:.2f}৳ হলে উইথড্র করতে পারবেন (আরও {need_more:.2f}৳ প্রয়োজন)।"
            )
            bot.answer_callback_query(call.id, lock_alert, show_alert=True)
            if str(getattr(call, "id", "")).startswith("cmd_"):
                # When pressed from Bottom Menu (ReplyKeyboardMarkup), Telegram does not display popup alerts on text messages,
                # so send the lock notice while keeping the user strictly on the Home Page keyboard!
                safe_send(
                    call.message.chat.id,
                    get_msg(
                        "withdraw_insufficient_balance_msg",
                        current_balance=f"{bal:.2f}",
                        balance=f"{bal:.2f}",
                        min_withdraw=f"{min_w:.2f}",
                        needed_amount=f"{need_more:.2f}"
                    ),
                    reply_markup=build_user_home_keyboard(uid, u),
                    menu_id="user_home"
                )
            return
        if rem_cnt <= 0 or rem_amt <= 0:
            bot.answer_callback_query(call.id, f"আজকের উইথড্র লিমিট শেষ! (দিনে সর্বোচ্চ {max_d_cnt} বার / {max_d_amt}৳)", show_alert=True)
            return

        sel_mobile = get_user_selected_mobile_methods(u)
        uid_disp = get_user_saved_number_for_method(u, "BattleClub_UID")

        kb = types.InlineKeyboardMarkup()
        m_btns = []
        for m in sel_mobile:
            saved_n = get_user_saved_number_for_method(u, m)
            suf = f" [{saved_n[-4:]}]" if saved_n else ""
            if m == "bKash":
                m_btns.append(make_btn(f"🌸 বিকাশ (bKash){suf}", callback_data="uwd_method:bKash", style="danger"))
            elif m == "Nagad":
                m_btns.append(make_btn(f"🍊 নগদ (Nagad){suf}", callback_data="uwd_method:Nagad", style="success"))
            elif m == "Rocket":
                m_btns.append(make_btn(f"🚀 রকেট (Rocket){suf}", callback_data="uwd_method:Rocket", style="primary"))
        m_btns.append(make_btn(f"🎮 Battle Club UID{f' [{uid_disp}]' if uid_disp else ''}", callback_data="uwd_method:BattleClub_UID", style="success"))
        for idx_b in range(0, len(m_btns), 2):
            kb.row(*m_btns[idx_b:idx_b + 2])
        kb.row(make_btn("🔄 অন্যান্য মাধ্যম (Another Method)", callback_data="uwd_method:other_way", style="primary"))
        kb.row(make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        append_page_edit_tools(kb, uid, msg_key="withdraw_msg")

        txt = get_msg("withdraw_msg", balance=f"{bal:.2f}", min_withdraw=f"{min_w:.2f}", daily_wd_rem=rem_cnt, daily_amt_rem=f"{rem_amt:.2f}")
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "wd_list":
        wd_flt = parts[2] if len(parts) > 2 and not parts[2].isdigit() else "all"
        wd_page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else page_arg
        per_p = 8
        with db_lock:
            conn = get_connection()
            all_rows = conn.execute("SELECT * FROM withdrawals WHERE user_id = ? ORDER BY rowid DESC", (uid,)).fetchall()
            conn.close()
        paid_rows = [r for r in all_rows if r["status"] == "paid"]
        pend_rows = [r for r in all_rows if r["status"] == "pending"]
        canc_rows = [r for r in all_rows if r["status"] == "cancelled"]
        rej_rows = [r for r in all_rows if r["status"] == "rejected"]
        paid_cnt, paid_amt = len(paid_rows), sum(float(r["amount"] or 0.0) for r in paid_rows)
        pend_cnt, pend_amt = len(pend_rows), sum(float(r["amount"] or 0.0) for r in pend_rows)
        canc_cnt, canc_amt = len(canc_rows), sum(float(r["amount"] or 0.0) for r in canc_rows)
        rej_cnt, rej_amt = len(rej_rows), sum(float(r["amount"] or 0.0) for r in rej_rows)

        if wd_flt == "paid":
            target_rows = paid_rows
        elif wd_flt == "pending":
            target_rows = pend_rows
        elif wd_flt in ("rejected", "cancelled"):
            wd_flt = "rejected"
            target_rows = [r for r in all_rows if r["status"] in ("rejected", "cancelled")]
        else:
            wd_flt = "all"
            target_rows = all_rows

        comb_rej_cnt = rej_cnt + canc_cnt
        comb_rej_amt = rej_amt + canc_amt
        p_meta = paginate_items(target_rows, page=wd_page, per_page=per_p)
        lines = []
        for r in p_meta["items"]:
            st_lbl = "COMPLETED ✅" if r["status"] == "paid" else ("REJECTED ❌" if r["status"] in ("rejected", "cancelled") else "PENDING ⏳")
            trx_note = f"\n  ├ নোট/TrxID: <code>{esc(r['trx_id'] or r['decision_reason'])}</code>" if (r["trx_id"] or r["decision_reason"]) else ""
            dest_disp = format_display_app_uid(r["dest"]) if r["method"] == "BattleClub_UID" else r["dest"]
            d_s, t_s = _split_datetime_str(r["created_at"])
            lines.append(f"• <b>{float(r['amount']):.2f}৳ ({esc(r['method'])})</b> — <b>{st_lbl}</b>\n  ├ নাম্বার/UID: <code>{esc(dest_disp)}</code>{trx_note}\n  └ 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>")
        items_txt = "\n".join(lines) if lines else "📭 এই ক্যাটাগরিতে কোনো উইথড্র রিকোয়েস্ট পাওয়া যায়নি।"
        tot_w_cnt = len(all_rows)
        tot_w_amt = sum(float(r["amount"] or 0.0) for r in all_rows)
        txt = get_msg(
            "withdraw_list_msg",
            page=p_meta["page"] + 1,
            total_pages=p_meta["total_pages"],
            total_cnt=tot_w_cnt,
            total_amt=f"{tot_w_amt:.2f}",
            paid_cnt=paid_cnt,
            paid_amt=f"{paid_amt:.2f}",
            pend_cnt=pend_cnt,
            pend_amt=f"{pend_amt:.2f}",
            canc_cnt=0,
            canc_amt="0.00",
            rej_cnt=comb_rej_cnt,
            rej_amt=f"{comb_rej_amt:.2f}",
            items_text=items_txt
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(f"{'✅ ' if wd_flt=='pending' else ''}⏳ পেন্ডিং উইথড্র ({pend_cnt})", callback_data="umenu:wd_list:pending:0", style="primary"),
            make_btn(f"{'✅ ' if wd_flt=='paid' else ''}✅ পেইড উইথড্র ({paid_cnt})", callback_data="umenu:wd_list:paid:0", style="success")
        )
        kb.row(
            make_btn(f"{'✅ ' if wd_flt=='rejected' else ''}❌ রিজেক্ট উইথড্র ({comb_rej_cnt})", callback_data="umenu:wd_list:rejected:0", style="danger"),
            make_btn(f"{'✅ ' if wd_flt=='all' else ''}📋 সব ({len(all_rows)})", callback_data="umenu:wd_list:all:0", style="primary")
        )
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"umenu:wd_list:{wd_flt}")
        if nav_row:
            kb.row(*nav_row)
        append_page_edit_tools(kb, uid, msg_key="withdraw_list_msg")
        kb.row(make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "my_videos":
        # Part 7, Items 72–76: My Videos opens Platform Selection (YouTube / TikTok) first!
        # Also supports direct filter legacy callback `umenu:my_videos:<filter>:<page>` if called with explicit filter
        if len(parts) > 2 and parts[2] in ("pending", "bot_approved", "admin_approved", "permanent_approved", "rejected"):
            plats = get_user_platforms(uid)
            first_plat = plats[0]["platform"].lower() if plats else "youtube"
            first_id = int(plats[0]["id"]) if plats else 0
            call.data = f"umyvid_acc:{first_plat}:{first_id}:{parts[2]}:{page_arg}"
            return handle_my_videos_hierarchy(call)
        txt, kb = render_my_videos_platform_hub(uid, u)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "history":
        txt, kb = render_user_payment_list_hub(uid, u)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "referral":
        ref_c = u.get("referral_code") or f"REF-{uid}"
        bonus = get_setting("ref_bonus", "10.0")
        red_bonus = get_setting("redeem_bonus", "5.0")
        max_d_ref = get_setting("max_daily_referrals", "5")
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🎟️ রেফার কোড রিডিম করুন", callback_data="umenu:redeem", style="success"), make_btn("🔙 সেটিংসে যান", callback_data="umenu:settings_hub", style="primary"))
        kb.row(make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        append_page_edit_tools(kb, uid, msg_key="referral_msg")
        txt = get_msg(
            "referral_msg",
            bonus=bonus,
            redeem_bonus=red_bonus,
            max_daily_ref=max_d_ref,
            ref_count=u.get("ref_count", 0),
            ref_code=esc(ref_c)
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "leaderboard":
        with db_lock:
            conn = get_connection()
            all_ranked = conn.execute("""
                SELECT u.user_id, u.name, u.username, u.total_earned, u.videos_approved,
                       COALESCE((SELECT SUM(w.amount) FROM withdrawals w WHERE w.user_id = u.user_id AND w.status = 'paid'), 0) as total_wd
                FROM users u
                WHERE u.registered = 1 AND u.status != 'deleted'
                ORDER BY u.total_earned DESC, u.videos_approved DESC
            """).fetchall()
            conn.close()
        rows = all_ranked[:10]
        medals = ["🥇 Top 1", "🥈 Top 2", "🥉 Top 3", "4️⃣ Top 4", "5️⃣ Top 5", "6️⃣ Top 6", "7️⃣ Top 7", "8️⃣ Top 8", "9️⃣ Top 9", "🔟 Top 10"]
        name_style_cfg = get_setting("leaderboard_name_style", "bold_sans") or "bold_sans"
        lines = []
        for idx, r in enumerate(rows):
            rank_num = idx + 1
            badge_html = get_setting(f"leaderboard_rank_{rank_num}_badge", medals[idx]) or medals[idx]
            # Strictly show ONLY the Creator's Name (never @username!)
            creator_name_raw = str(r["name"] or f"ক্রিয়েটর #{rank_num}").strip()
            if creator_name_raw.startswith("@"):
                creator_name_raw = creator_name_raw.lstrip("@")
            styled_name = apply_button_text_design(creator_name_raw, name_style_cfg)
            earned_v = float(r["total_earned"] or 0.0)
            wd_v = float(r["total_wd"] or 0.0)
            v_cnt = int(r["videos_approved"] or 0)
            lines.append(f"{badge_html} — <b>{esc(styled_name)}</b>\n   ├ ভিডিও: <b>{v_cnt}টি</b> | আয়: <b>{earned_v:.2f}৳</b> | উইথড্র: <b>{wd_v:.2f}৳</b>")
        while len(lines) < 10:
            r_num = len(lines) + 1
            badge_html = get_setting(f"leaderboard_rank_{r_num}_badge", medals[r_num - 1]) or medals[r_num - 1]
            lines.append(f"{badge_html} — <i>ক্রিয়েটর_{r_num}</i> — ভিডিও: 0টি | আয়: 0.00৳ | উইথড্র: 0.00৳")

        my_earned = float(u.get("total_earned", 0.0) or 0.0)
        lb_prog = _compute_user_leaderboard_progress(uid, my_earned)
        txt = get_msg(
            "leaderboard_msg",
            leaderboard_rows="\n\n".join(lines),
            my_earned=f"{my_earned:.2f}",
            my_videos=u.get("videos_approved", 0),
            progress_pct=lb_prog["progress_pct"],
            gap_notice=lb_prog["gap_notice"]
        )
        kb = types.InlineKeyboardMarkup()
        if is_admin_unlocked(uid):
            kb.row(make_btn("🏆 লিডারবোর্ড Rank 1-10 ও স্টাইল এডিট করুন", callback_data="adm_lb_customizer", style="success"))
        append_page_edit_tools(kb, uid, msg_key="leaderboard_msg")
        kb.row(make_btn("📊 ড্যাশবোর্ডে যান", callback_data="umenu:dashboard", style="primary"), make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "redeem":
        user_memory_states[uid] = {"step": "awaiting_redeem_code"}
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="redeem_msg")
        kb.row(make_btn("🔙 সেটিংসে ফিরে যান", callback_data="umenu:settings_hub", style="primary"), make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("redeem_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "activity":
        with db_lock:
            conn = get_connection()
            logs = conn.execute("SELECT * FROM audit_logs WHERE actor_id = ? OR target_user_id = ? ORDER BY id DESC LIMIT 12", (uid, uid)).fetchall()
            conn.close()
        strike_lim = int(get_setting("strike_limit", "3"))
        freeze_st = "❄️ ফ্রিজ (Frozen)" if int(u.get("bio_frozen") or 0) == 1 else "🟢 স্বাভাবিক (Clear)"
        txt = get_msg(
            "user_activity_msg",
            account_status=esc(str(u.get("status", "active")).upper()),
            login_count=u.get("login_count", 0),
            freeze_status=freeze_st,
            dup_strikes=u.get("duplicate_strikes", 0),
            wrong_strikes=u.get("wrong_submit_strikes", 0),
            strike_limit=strike_lim,
            activity_logs=_format_boxed_activity_logs(logs)
        )
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="user_activity_msg")
        kb.row(make_btn("🔙 সেটিংসে ফিরে যান", callback_data="umenu:settings_hub", style="primary"), make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "pwd_change":
        user_memory_states[uid] = {"step": "awaiting_old_user_pwd"}
        sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("💬 পাসওয়ার্ড মনে নেই? সরাসরি অ্যাডমিনের সাথে কথা বলুন", url=sup_url, style="primary"))
        append_page_edit_tools(kb, uid, msg_key="pwd_change_old_prompt_msg")
        kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("pwd_change_old_prompt_msg"),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if act == "logout":
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET session_logged_out = 1, timeout_notified = 1 WHERE user_id = ?", (uid,))
            conn.close()
        user_memory_states.pop(uid, None)
        cleanup_user_ui_messages(call.message.chat.id, uid)
        if getattr(call, "message", None) and getattr(call.message, "message_id", None):
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
        sent_l = safe_send(call.message.chat.id, get_msg("user_logout_confirm_msg"), track_ui=True, auto_clean_prev=False)
        if sent_l and getattr(sent_l, "message_id", None):
            schedule_message_auto_delete(call.message.chat.id, sent_l.message_id, delay_sec=7.0, uid=uid)
        bot.answer_callback_query(call.id, "সফলভাবে লগআউট করা হয়েছে!")
        return

    if act == "lang_toggle":
        cur_lang = (u.get("language") or "bn").lower()
        new_lang = "en" if cur_lang == "bn" else "bn"
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (new_lang, uid))
            conn.close()
        u_updated = get_user(uid)
        toast = "🌐 Language switched to English!" if new_lang == "en" else "🌐 ভাষা বাংলায় পরিবর্তন করা হয়েছে!"
        bot.answer_callback_query(call.id, toast)
        top_yt = get_setting("home_youtube_link", "")
        w_txt = attach_top_youtube_preview(get_msg("welcome_msg", lang=new_lang, name=esc(u_updated.get("name")), balance=f"{float(u_updated.get('balance', 0)):.2f}", user_id=uid), top_yt)
        safe_edit(call.message.chat.id, call.message.message_id, w_txt, reply_markup=build_user_home_keyboard(uid, u_updated), top_yt_url=top_yt, menu_id="user_home")
        return

    if act == "color":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("সবুজ (Green)", callback_data="uset_color:success", style="success"), make_btn("লাল (Red)", callback_data="uset_color:danger", style="danger"))
        kb.row(make_btn("নীল (Blue)", callback_data="uset_color:primary", style="primary"), make_btn("ডিফল্ট থিম", callback_data="uset_color:default"))
        kb.row(make_btn("🔙 সেটিংসে ফিরে যান", callback_data="umenu:settings_hub", style="primary"), make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🎨 <b>আপনার বাটন কালার সিলেক্ট করুন:</b>\n{FULL_WIDTH_DIVIDER}", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if act == "delete_acc":
        debt_b = float(u.get("debt_balance", 0.0) or 0.0)
        if debt_b > 0:
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("💬 সাপোর্টে যোগাযোগ করুন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
            kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_edit(
                call.message.chat.id, call.message.message_id,
                get_msg("delete_acc_debt_block_msg", debt_balance=f"{debt_b:.2f}"),
                reply_markup=kb
            )
            bot.answer_callback_query(call.id, "আগে ঋণ পরিশোধ করুন, তারপর অ্যাকাউন্ট ডিলিট করুন!", show_alert=True)
            return
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("⚠️ ১ম কনফার্মেশন: এগিয়ে যান", callback_data="udel_step2", style="danger"), make_btn("না, ফিরে যান", callback_data="umenu:cancel_home", style="success"))
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"⚠️ <b>আপনি কি সত্যিই আপনার অ্যাকাউন্ট ডিলিট করতে চান? (ধাপ ১/২)</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"আপনার বর্তমান ব্যালেন্স: <b>{float(u.get('balance', 0)):.2f}৳</b> | হোল্ড ব্যালেন্স: <b>{float(u.get('held_balance', 0)):.2f}৳</b>\n"
            "ডিলিট করার আগে ব্যালেন্স উইথড্র করে নেওয়ার পরামর্শ দেওয়া হচ্ছে। পরবর্তী চূড়ান্ত কনফার্মেশনের জন্য নিচের বাটনে চাপ দিন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if act == "admin_panel" and is_authorized_admin(uid):
        if not require_unlocked_admin_session(call):
            return
        call.data = "admin_hub"
        return handle_admin_master_dashboard(call)

    top_yt = get_setting("home_youtube_link", "")
    u_lang = (u.get("language") or "bn").lower()
    w_txt = attach_top_youtube_preview(get_msg("welcome_msg", lang=u_lang, name=esc(u.get("name")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid), top_yt)
    safe_edit(call.message.chat.id, call.message.message_id, w_txt, reply_markup=build_user_home_keyboard(uid, u), top_yt_url=top_yt, menu_id="user_home")
    bot.answer_callback_query(call.id)


# ==============================================================================
# SUBMIT, LINK MORE & WITHDRAW CALLBACK HANDLERS
# ==============================================================================
@bot.callback_query_handler(func=lambda c: c.data.startswith("usub_plat:") or c.data.startswith("usub_acc:"))
@_guard("video_submit_start")
def handle_video_submit_start(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return
    if not u or u.get("status") == "banned":
        bot.answer_callback_query(call.id, "আপনার অ্যাকাউন্ট নিষিদ্ধ (Banned)!", show_alert=True)
        return
    if int(u.get("bio_frozen") or 0) == 1 or str(u.get("status") or "").lower() == "frozen":
        bot.answer_callback_query(call.id, "❄️ অ্যাকাউন্ট ফ্রিজ (Frozen) থাকায় ভিডিও সাবমিট বন্ধ রয়েছে!", show_alert=True)
        return
    is_cd, cd_txt = check_user_cooldown(u)
    if is_cd:
        bot.answer_callback_query(call.id, "কুলডাউন চলছে!", show_alert=True)
        safe_send(call.message.chat.id, cd_txt)
        return

    selected_acc_id = None
    if call.data.startswith("usub_acc:"):
        parts_a = call.data.split(":", 2)
        plat = parts_a[1].lower()
        selected_acc_id = int(parts_a[2]) if len(parts_a) > 2 and parts_a[2].isdigit() else None
    else:
        plat = call.data.split(":", 1)[1].lower()

    if plat not in ("youtube", "tiktok"):
        bot.answer_callback_query(call.id, "শুধুমাত্র YouTube এবং TikTok সমর্থিত!", show_alert=True)
        return
    plats = get_user_platforms(uid, plat)
    if not plats:
        bot.answer_callback_query(call.id, f"আপনার কোনো ভেরিফাইড {PLATFORMS[plat]['title']} অ্যাকাউন্ট যুক্ত নেই! আগে 'নতুন অ্যাকাউন্ট যোগ করুন' থেকে যুক্ত করুন।", show_alert=True)
        return

    # If the user has ONLY 1 verified account on this platform, go DIRECTLY to the video link submission prompt!
    # If the user has 2 or more verified accounts, show the account selection buttons!
    if selected_acc_id is None and len(plats) == 1:
        selected_acc_id = int(plats[0].get("id") or 0)

    if selected_acc_id is None:
        kb = types.InlineKeyboardMarkup()
        st_col = "danger" if plat == "youtube" else "primary"
        for idx_p, p in enumerate(plats, start=1):
            ord_lbl = ORDINAL_ACCOUNT_LABELS_BN.get(idx_p, f"#{idx_p} অ্যাকাউন্ট")
            acc_lbl = f"🎬 {ord_lbl} — {p['display_name']} (@{p['profile_handle']})"
            kb.row(make_btn(acc_lbl, callback_data=f"usub_acc:{plat}:{p['id']}", style=st_col))
        append_page_edit_tools(kb, uid, msg_key="video_submit_acc_select_msg")
        kb.row(
            make_btn("🔙 প্ল্যাটফর্ম তালিকায় ফিরে যান", callback_data="umenu:submit_grp_confirmed", style="primary"),
            make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
        )
        txt_sel = get_msg(
            "video_submit_acc_select_msg",
            platform_title=PLATFORMS[plat]["title"],
            account_count=len(plats)
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt_sel, reply_markup=kb)
        bot.answer_callback_query(call.id, "কোন অ্যাকাউন্ট থেকে ভিডিও সাবমিট করবেন তা নির্বাচন করুন!")
        return

    chosen_plat_row = next((p for p in plats if selected_acc_id is not None and int(p.get("id") or 0) == selected_acc_id), None)
    if not chosen_plat_row:
        bot.answer_callback_query(call.id, "⛔ অবৈধ বা অননুমোদিত অ্যাকাউন্ট আইডি!", show_alert=True)
        return
    with db_lock:
        conn = get_connection()
        with conn:
            vid_code = generate_unique_bc_code("video_submit", user_id=uid, conn=conn)
            conn.execute("UPDATE users SET active_video_code = ? WHERE user_id = ?", (vid_code, uid))
            rate, _, _, _ = get_video_payment_rates(conn, platform=plat)
            t_days = get_video_tracking_days(conn, platform=plat)
        conn.close()

    user_memory_states[uid] = {
        "step": "awaiting_video_link",
        "platform": plat,
        "selected_platform_id": int(chosen_plat_row.get("id") or 0)
    }
    g_code = get_setting("global_required_code", "#BattleClub")
    chosen_ord_idx = next((idx_p for idx_p, p in enumerate(plats, start=1) if int(p.get("id") or 0) == int(chosen_plat_row.get("id") or 0)), 1)
    chosen_ord_lbl = ORDINAL_ACCOUNT_LABELS_BN.get(chosen_ord_idx, f"#{chosen_ord_idx} অ্যাকাউন্ট")
    plat_disp_title = f"{PLATFORMS[plat]['title']} ({chosen_ord_lbl}: {chosen_plat_row['display_name']})"

    txt = get_msg(
        "video_submit_msg",
        platform_title=plat_disp_title,
        bio_code=esc(chosen_plat_row.get("bio_code_used") or u["bio_verify_code"]),
        unique_code=esc(vid_code),
        app_uid=esc(format_display_app_uid(u["app_uid"])),
        global_code=esc(g_code),
        rate=rate,
        track_days=t_days
    )
    kb = types.InlineKeyboardMarkup()
    if len(plats) > 1:
        kb.row(make_btn("🔄 অন্য চ্যানেল/অ্যাকাউন্ট বেছে নিন", callback_data=f"usub_plat:{plat}", style="primary"))
    kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
    append_page_edit_tools(kb, uid, msg_key="video_submit_msg")
    safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("ulink_act:"))
@_guard("link_more_start")
def handle_link_more_platform_start(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return
    if u:
        debt_b = float(u.get("debt_balance", 0.0) or 0.0)
        bal_b = float(u.get("balance", 0.0) or 0.0)
        if debt_b > 0 or bal_b < 0:
            eff_debt = max(debt_b, abs(min(0.0, bal_b)))
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("💬 সাপোর্টে যোগাযোগ করুন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
            append_page_edit_tools(kb, uid, msg_key="debt_bind_block_msg")
            kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_edit(call.message.chat.id, call.message.message_id, get_msg("debt_bind_block_msg", debt_balance=f"{eff_debt:.2f}"), reply_markup=kb)
            bot.answer_callback_query(call.id, f"আপনার একাউন্টে {eff_debt:.2f}৳ ঋণ রয়েছে! আগে ঋণ পরিশোধ করুন।", show_alert=True)
            return
    plat = call.data.split(":", 1)[1].lower()
    if plat not in ("youtube", "tiktok"):
        bot.answer_callback_query(call.id, "শুধুমাত্র YouTube এবং TikTok সমর্থিত!", show_alert=True)
        return
    crit = get_platform_criteria(plat)
    max_acc = int(crit["max_accounts"])

    existing = get_user_platforms(uid, plat)
    if len(existing) >= max_acc:
        lim_txt = get_msg(
            "account_limit_reached_msg",
            platform_title=PLATFORMS[plat]["title"],
            max_accounts=max_acc
        )
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="account_limit_reached_msg")
        # Part 7, Item 77: Back to Home Page on Add New Account page
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, lim_txt, reply_markup=kb)
        bot.answer_callback_query(call.id, f"আপনি সর্বোচ্চ {max_acc}টি অ্যাকাউন্ট ইতিমধ্যে যুক্ত করেছেন!", show_alert=True)
        return

    with db_lock:
        conn_bc = get_connection()
        with conn_bc:
            fresh_bio_c = generate_unique_bc_code("bio_verify", user_id=uid, conn=conn_bc)
        conn_bc.close()
    user_memory_states[uid] = {"step": "awaiting_extra_platform_link", "platform": plat, "extra_bio_code": fresh_bio_c}
    total_req_v = int(crit["min_views"]) * int(crit["qualifying_videos"])
    min_tot_vids = int(crit.get("min_total_videos") or crit["qualifying_videos"])
    kb = types.InlineKeyboardMarkup()
    kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
    append_page_edit_tools(kb, uid, msg_key="reg_code_prompt_msg")

    prompt_txt = get_msg(
        "reg_code_prompt_msg",
        platform_title=f"{PLATFORMS[plat]['title']} ({len(existing)+1}/{max_acc})",
        bio_code=fresh_bio_c,
        min_subs=crit["min_subs"],
        min_total_vids=min_tot_vids,
        qual_vids=crit["qualifying_videos"],
        min_views=crit["min_views"],
        total_req_views=total_req_v
    )
    safe_edit(call.message.chat.id, call.message.message_id, prompt_txt, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: (
    c.data.startswith("uwd_method:") or
    c.data.startswith("uwd_fast_dest:") or
    c.data == "uwd_other_go" or
    c.data.startswith("uwd_other_plat:")
))
@_guard("withdraw_method_pick")
def handle_withdraw_method_pick(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    if not check_user_session_lock(call.message.chat.id, call.from_user, call_id=call.id):
        return
    if not u or u.get("status") != "active" or u.get("bio_frozen"):
        bot.answer_callback_query(call.id, "আপনার অ্যাকাউন্টে উইথড্র সাময়িক স্থগিত রয়েছে!", show_alert=True)
        return
    debt_b = float(u.get("debt_balance", 0.0) or 0.0)
    if debt_b > 0:
        user_memory_states.pop(uid, None)
        bot.answer_callback_query(call.id, f"🔒 বকেয়া ঋণ ({debt_b:.2f}৳) পরিশোধ না হওয়া পর্যন্ত উইথড্র লক রয়েছে!", show_alert=True)
        return
    bal_chk = float(u.get("balance", 0.0) or 0.0)
    min_w_chk = float(get_setting("min_withdraw", "100.0"))
    if bal_chk <= 0 or bal_chk < min_w_chk:
        user_memory_states.pop(uid, None)
        need_m = max(0.0, round(min_w_chk - bal_chk, 2))
        bot.answer_callback_query(
            call.id,
            f"🔒 উইথড্র লক রয়েছে! আপনার পর্যাপ্ত পরিমাণ ব্যালেন্স নেই ({bal_chk:.2f}৳)। ন্যূনতম {min_w_chk:.2f}৳ হলে উইথড্র করতে পারবেন (আরও {need_m:.2f}৳ প্রয়োজন)।",
            show_alert=True
        )
        return

    if call.data.startswith("uwd_fast_dest:"):
        st = user_memory_states.get(uid) or {}
        if st.get("step") not in ("awaiting_wd_phone", "awaiting_wd_other_dest"):
            bot.answer_callback_query(call.id, "উইথড্র সেশন পাওয়া যায়নি, আবার চেষ্টা করুন!", show_alert=True)
            return
        method = st.get("method", "bKash")
        fd_parts = call.data.split(":")
        slot_idx = int(fd_parts[2]) if (len(fd_parts) > 2 and fd_parts[2].isdigit()) else 0
        dest_val = get_user_saved_number_for_method(u, method, slot_index=slot_idx)
        if not dest_val:
            bot.answer_callback_query(call.id, f"আপনার একাউন্টে {method}-এর নাম্বার যুক্ত নেই! নাম্বারটি লিখে পাঠান অথবা 'অন্য উপায়' ব্যবহার করুন।", show_alert=True)
            return

        class _SyntheticMsg:
            def __init__(self, u_obj, c_obj, txt_v):
                self.from_user = u_obj
                self.chat = c_obj
                self.text = txt_v

        bot.answer_callback_query(call.id, "উইথড্র রিকোয়েস্ট প্রসেস হচ্ছে...")
        process_wd_phone_step(_SyntheticMsg(call.from_user, call.message.chat, dest_val), u, st)
        return

    # Part 8, Items 80–82: "Another Method" strict 3-step sequence:
    # Step 1: Method Name -> Step 2: Account Info -> Step 3: Withdraw Amount (with Cancel & Back to Home Page)
    if call.data == "uwd_other_go" or call.data == "uwd_method:other_way":
        user_memory_states[uid] = {
            "step": "awaiting_wd_other_method_name",
            "method": "other_way",
            "is_other_way": True
        }
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("🌸 বিকাশ (bKash)", callback_data="uwd_other_plat:bKash", style="danger"),
            make_btn("🍊 নগদ (Nagad)", callback_data="uwd_other_plat:Nagad", style="success")
        )
        kb.row(
            make_btn("🚀 রকেট (Rocket)", callback_data="uwd_other_plat:Rocket", style="primary"),
            make_btn("🎮 Battle Club UID", callback_data="uwd_other_plat:BattleClub_UID", style="success")
        )
        kb.row(
            make_btn("✖️ বাতিল করুন (Cancel)", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
        )
        append_page_edit_tools(kb, uid, msg_key="withdraw_other_way_method_name_prompt_msg")
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("withdraw_other_way_method_name_prompt_msg", balance=f"{float(u.get('balance', 0)):.2f}"),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("uwd_other_plat:"):
        plat_m = call.data.split(":", 1)[1]
        st = user_memory_states.get(uid) or {}
        st["method"] = plat_m
        st["is_other_way"] = True
        st["step"] = "awaiting_wd_other_dest"
        user_memory_states[uid] = st
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔄 মাধ্যমের নাম পরিবর্তন করুন", callback_data="uwd_other_go", style="primary"))
        kb.row(
            make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
        )
        append_page_edit_tools(kb, uid, msg_key="withdraw_other_way_input_msg")
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("withdraw_other_way_input_msg", method=esc(plat_m)),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    method = call.data.split(":", 1)[1]
    if method not in ("bKash", "Nagad", "Rocket", "BattleClub_UID"):
        bot.answer_callback_query(call.id, "অবৈধ পেমেন্ট মেথড।", show_alert=True)
        return
    user_memory_states[uid] = {"step": "awaiting_wd_amount", "method": method, "is_other_way": False}

    bal = float(u.get("balance", 0.0))
    min_w = float(get_setting("min_withdraw", "100.0"))
    kb = types.InlineKeyboardMarkup()
    kb.row(
        make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
        make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
    )
    saved_d = get_user_saved_number_for_method(u, method) or "যুক্ত নেই"
    prompt = get_msg("withdraw_amount_prompt_msg", method=esc(method), saved_dest=esc(saved_d), balance=f"{bal:.2f}", minimum=f"{min_w:.2f}")
    safe_edit(call.message.chat.id, call.message.message_id, prompt, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("uset_color:"))
@_guard("user_color_set")
def handle_user_color_set(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    col = call.data.split(":", 1)[1]
    col_val = "" if col == "default" else col
    with db_lock:
        conn = get_connection()
        with conn:
            conn.execute("UPDATE users SET user_btn_style = ? WHERE user_id = ?", (col_val, uid))
        conn.close()
    u = get_user(uid) or u
    u_lang = (u.get("language") or "bn").lower()
    top_yt = get_setting("home_youtube_link", "")
    w_txt = attach_top_youtube_preview(
        get_msg("welcome_msg", lang=u_lang, name=esc(u.get("name")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid),
        top_yt
    )
    safe_edit(call.message.chat.id, call.message.message_id, w_txt, reply_markup=build_user_home_keyboard(uid, u), top_yt_url=top_yt, menu_id="user_home")
    bot.answer_callback_query(call.id, "বাটন কালার পরিবর্তন হয়েছে!")


@bot.callback_query_handler(func=lambda c: (
    c.data in ("udel_step2", "uconfirm_del_acc") or
    c.data.startswith("uman_code_prompt:") or
    c.data.startswith("umyvid_item:") or
    c.data.startswith("u_refresh_vid:")
))
@_guard("user_extra_actions", sensitive=True)
def handle_user_delete_and_manual_code_actions(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)

    if call.data.startswith("uman_code_prompt:"):
        plat = call.data.split(":", 1)[1]
        st = user_memory_states.get(uid) or {}
        st["step"] = "awaiting_user_manual_verify_code"
        st["platform"] = plat
        st["manual_wait_started_ts"] = time.time()
        user_memory_states[uid] = st
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("💬 অ্যাডমিনকে মেসেজ করে র‍্যান্ডম কোড নিন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
        kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("manual_verify_code_input_prompt_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("umyvid_item:") or call.data.startswith("u_refresh_vid:"):
        is_live_refresh = call.data.startswith("u_refresh_vid:")
        parts = call.data.split(":")
        sub_id = parts[1]
        plat_back = parts[2] if len(parts) > 2 else "youtube"
        acc_back = parts[3] if len(parts) > 3 and parts[3].isdigit() else "0"
        flt = parts[4] if len(parts) > 4 else (parts[2] if len(parts) > 2 else "all")
        pg = parts[5] if len(parts) > 5 else (parts[3] if len(parts) > 3 else "0")

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? AND user_id = ? AND COALESCE(is_trashed, 0) = 0", (sub_id, uid)).fetchone()
            conn.close()
        if not v:
            bot.answer_callback_query(call.id, "ভিডিওটি পাওয়া যায়নি!", show_alert=True)
            return

        refresh_toast = ""
        is_rej_now = (v["admin_status"] == "rejected" or v["bot_status"] == "rejected" or v["status"] == "rejected")
        is_perm_now = int(v["permanent_approved"] or 0) == 1
        if is_live_refresh and not is_rej_now and not is_perm_now:
            v_url_live = v["video_url"] or v["url"]
            live_meta = fetch_video_public_metadata(v["platform"], v_url_live)
            if isinstance(live_meta, dict) and (live_meta.get("view_count") is not None or live_meta.get("play_count") is not None):
                raw_lv = live_meta.get("view_count") if live_meta.get("view_count") is not None else live_meta.get("play_count")
                live_v = max(int(v["current_views"] or 0), parse_human_number(raw_lv))
                live_l = max(0, parse_human_number(live_meta.get("like_count") or 0))
                live_c = max(0, parse_human_number(live_meta.get("comment_count") or 0))
                v_link_cfg = get_platform_criteria(v["platform"]).get("verification_link") or get_setting("verification_link", "")
                tr_live = analyze_video_traffic_sources(
                    platform_key=v["platform"],
                    video_url=v_url_live,
                    caption_text=str(live_meta.get("description") or v["title"] or ""),
                    cur_views=live_v,
                    cur_likes=live_l,
                    cur_comments=live_c,
                    ytdlp_info=live_meta,
                    verification_link=v_link_cfg
                )
                added_money = 0.0
                suspicious_blocked = False
                suspicious_reason = ""
                vel_thr_l = float(get_setting("view_velocity_threshold", "15000"))
                eng_thr_l = float(get_setting("engagement_threshold_ratio", "0.0005"))
                auto_rej_susp_l = get_setting("suspicious_auto_reject", "1") == "1"
                live_src = str(live_meta.get("metric_source") or "live-refresh")[:40]
                with db_lock:
                    conn = get_connection()
                    try:
                        now_ts_l = time.time()
                        now_str_l = datetime.fromtimestamp(now_ts_l).strftime("%Y-%m-%d %H:%M:%S")
                        with conn:
                            conn.execute(
                                "INSERT OR IGNORE INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES (?, ?, ?, ?, ?, ?)",
                                (sub_id, live_v, live_l, live_c, live_src, now_ts_l)
                            )
                        prior_rows_l = conn.execute(
                            "SELECT views, likes, comments, source, recorded_at_ts FROM video_view_snapshots WHERE sub_id=? ORDER BY recorded_at_ts DESC LIMIT 20",
                            (sub_id,)
                        ).fetchall()
                        prior_snaps_l = [dict(s) for s in reversed(prior_rows_l)]
                        risk_l = assess_organic_view_risk(
                            prior_snaps_l,
                            live_v,
                            live_l,
                            live_c,
                            velocity_threshold=vel_thr_l,
                            engagement_threshold=eng_thr_l,
                            auto_reject_enabled=auto_rej_susp_l,
                            traffic_breakdown=tr_live
                        )
                        org_st_l = str(risk_l.get("organic_status") or ("verified_organic" if risk_l.get("organic_verified") else "pending_snapshots"))
                        with conn:
                            conn.execute(
                                "UPDATE videos SET previous_views = current_views, current_views = ?, organic_status = ?, view_metrics_known = 1, view_metrics_source = ?, last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                                (live_v, org_st_l, live_src, now_str_l, now_ts_l, sub_id)
                            )
                            save_video_traffic_and_external_links(
                                sub_id=sub_id, user_id=uid, platform=v["platform"],
                                traffic_breakdown=tr_live, external_links=tr_live.get("external_links", []), conn=conn
                            )
                            if risk_l.get("suspicious") or float(risk_l.get("risk_score") or 0.0) >= 0.75:
                                suspicious_blocked = True
                                suspicious_reason = str(risk_l.get("reason") or "অস্বাভাবিক ভিউ বৃদ্ধি শনাক্ত হয়েছে")
                                if auto_rej_susp_l:
                                    admin_reject_video_with_reversal(
                                        conn,
                                        sub_id=sub_id,
                                        rejection_reason=f"অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি: {suspicious_reason}",
                                        admin_id="BOT_ANTI_FRAUD"
                                    )
                                else:
                                    conn.execute(
                                        "UPDATE videos SET flagged_suspicious = 1, bot_status = CASE WHEN admin_status = 'pending' THEN 'manual_review' ELSE bot_status END, status = CASE WHEN admin_status = 'pending' THEN 'manual_review' ELSE status END, risk_reason = ? WHERE sub_id = ?",
                                        (suspicious_reason, sub_id)
                                    )
                            else:
                                min_req_v = get_video_payment_rates(conn, sub_id=sub_id)[2]
                                ded_ext_v = int(v["deducted_external_views"] or 0)
                                net_live_v = max(0, live_v - ded_ext_v)
                                dl_ts_l = float(v["qualification_deadline_ts"] or 0.0)
                                if v["bot_status"] in ("waiting_views", "pending") and not int(v["flagged_suspicious"] or 0):
                                    if dl_ts_l > 0 and now_ts_l > dl_ts_l:
                                        transition_expired_pending_video(
                                            conn, sub_id,
                                            reason=f"নির্ধারিত যোগ্যতা সময়সীমায় প্রয়োজনীয় {min_req_v} ভিউ পূরণ হয়নি।",
                                            expiry_action=get_setting("pending_expiry_action", "permanent_approve_zero_pay"),
                                            now_ts=now_ts_l
                                        )
                                    elif net_live_v >= min_req_v and risk_l.get("organic_verified") is True:
                                        credited_l, _ = process_bot_approval_credit(conn, sub_id, uid, live_v, now_ts=now_ts_l)
                                        added_money = float(credited_l or 0.0)
                                elif (v["bot_status"] == "approved" or v["admin_status"] == "approved") and not int(v["flagged_suspicious"] or 0):
                                    credited_l, _ = process_idempotent_milestone_payout(
                                        conn, sub_id, uid, live_v, int(v["paid_views"] or v["eligible_views"] or 0)
                                    )
                                    added_money = float(credited_l or 0.0)
                    finally:
                        conn.close()
                if suspicious_blocked:
                    refresh_toast = f"⚠️ সন্দেহজনক/ফেক ভিউ শনাক্ত হয়েছে: {suspicious_reason[:80]}"
                elif added_money > 0:
                    _unlock_referral_on_first_video_approval(uid)
                    refresh_toast = f"✅ লাইভ ভিউ আপডেট হয়েছে ({live_v} ভিউ) এবং +{added_money:.2f}৳ আপনার ব্যালেন্সে যোগ হয়েছে!"
                else:
                    refresh_toast = f"🔄 লাইভ ভিউ আপডেট হয়েছে: বর্তমান ভিউ {live_v}"
            else:
                refresh_toast = "⚠️ এই মুহূর্তে নতুন ভিউ ডেটা পাওয়া যায়নি, কিছুক্ষণ পর আবার চেষ্টা করুন।"

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? AND user_id = ? AND COALESCE(is_trashed, 0) = 0", (sub_id, uid)).fetchone()
            conn.close()
        if not v:
            return

        cred = float(v["credited_amount"] or v["reward"] or 0.0)
        is_perm = int(v["permanent_approved"] or 0) == 1
        if v["admin_status"] == "rejected" or v["bot_status"] == "rejected" or v["status"] == "rejected":
            st_lbl = f"❌ REJECTED ({v['rejection_reason'] or 'অর্গানিক ভিউ না / নিয়ম ভঙ্গ'})"
        elif is_perm:
            st_lbl = "🔒 PERMANENT APPROVED"
        elif v["admin_status"] == "approved":
            st_lbl = "👑 ADMIN APPROVED"
        elif v["bot_status"] == "approved":
            st_lbl = "🤖 BOT APPROVED"
        else:
            st_lbl = "⏳ PENDING (ভিউ শর্ত পূরণের অপেক্ষায়)"
        end_ts = float(v["earning_end_ts"] or 0)
        rem_days = max(0, int((end_ts - time.time()) / 86400)) if end_ts > 0 and not is_perm else (0 if is_perm else int(get_setting("earning_duration_days", "5")))
        v_url = v["video_url"] or v["url"]

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔗 ভিডিওটি ওপেন করুন", url=v_url, style="primary"))
        if not is_perm and v["admin_status"] != "rejected" and v["bot_status"] != "rejected":
            kb.row(make_btn("🔄 লাইভ ভিউ ও ইনকাম আপডেট করুন", callback_data=f"u_refresh_vid:{sub_id}:{plat_back}:{acc_back}:{flt}:{pg}", style="success"))

        traffic_user_block = _append_video_traffic_and_ext_links_ui(
            v, kb, sec_short="uv", plat_flt=plat_back, from_traffic_page=True, include_admin_actions=False
        )
        txt = (
            f"🎬 <b>ভিডিও বিস্তারিত রিপোর্ট:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"🌐 প্ল্যাটফর্ম: <b>{esc(PLATFORMS.get(v['platform'], {}).get('title', v['platform'].upper()))}</b>\n"
            f"📌 শিরোনাম: <b>{esc(v['title'])}</b>\n"
            f"🔗 ভিডিও: <a href=\"{esc(v_url)}\">🎬 ভিডিও লিংক ওপেন করুন</a>\n"
            f"👁️ বর্তমান ভিউ: <b>{v['current_views']}</b> (পেইড ভিউ: <b>{v['paid_views']}</b>)\n"
            f"💰 অর্জিত আয়: <b>{cred:.2f} টাকা</b>\n"
            f"📋 স্ট্যাটাস: <b>{esc(st_lbl)}</b>\n"
            f"⏳ অবশিষ্ট আর্নিং সময়: <b>{rem_days} দিন</b>\n"
            f"📅 সাবমিটের তারিখ: <b>{esc(v['submitted_at'])}</b>\n"
            f"{traffic_user_block}"
        )
        if plat_back in ("youtube", "tiktok") and str(acc_back).isdigit() and int(acc_back) > 0:
            kb.row(make_btn("🔙 আমার ভিডিও তালিকায় ফিরে যান", callback_data=f"umyvid_acc:{plat_back}:{acc_back}:{flt}:{pg}", style="danger"))
        else:
            kb.row(make_btn("🔙 আমার ভিডিও তালিকায় ফিরে যান", callback_data="umenu:my_videos", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id, refresh_toast if refresh_toast else None, show_alert=bool(refresh_toast))
        return

    if call.data == "udel_step2":
        if not u:
            return
        debt_b = float(u.get("debt_balance", 0.0) or 0.0)
        if debt_b > 0:
            bot.answer_callback_query(call.id, "আগে ঋণ পরিশোধ করুন, তারপর অ্যাকাউন্ট ডিলিট করুন!", show_alert=True)
            return
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("🔥 চূড়ান্ত কনফার্ম: স্থায়ীভাবে ডিলিট করুন", callback_data="uconfirm_del_acc", style="danger"),
            make_btn("🔙 না, ফিরে যান", callback_data="umenu:cancel_home", style="success")
        )
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            get_msg("delete_acc_confirm_msg", balance=f"{float(u.get('balance', 0)):.2f}", held_balance=f"{float(u.get('held_balance', 0)):.2f}"),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    with db_lock:
        res_del = delete_user_account_completely(uid, actor_id=uid, hard_delete=False)
    if not res_del.get("ok"):
        bot.answer_callback_query(call.id, res_del.get("reason", "ডিলিট করা যায়নি!"), show_alert=True)
        return
    user_memory_states.pop(uid, None)
    safe_edit(
        call.message.chat.id,
        call.message.message_id,
        f"🗑️ <b>আপনার অ্যাকাউন্ট, ব্যালেন্স এবং প্রোফাইল বাইন্ডিং সম্পূর্ণ রিলিজ ও ডিলিট করা হয়েছে!</b>\n{FULL_WIDTH_DIVIDER}\n"
        "পরবর্তীতে চাইলে আপনার চ্যানেল দিয়ে আবার নতুন করে অ্যাকাউন্ট ভেরিফিকেশন করতে পারবেন (তবে পূর্বে সাবমিটকৃত কোনো ভিডিও লিংক দ্বিতীয়বার সাবমিট করা যাবে না)। পুনরায় শুরু করতে /start চাপুন।"
    )
    bot.answer_callback_query(call.id, "অ্যাকাউন্ট সম্পূর্ণ ডিলিট হয়েছে!")


# ==============================================================================
# PART 18: TRAFFIC SOURCE & EXTERNAL LINK ADMIN HELPERS & HANDLERS
# - Clean `<a href>` link (NO raw long URL in status text)
# - Channel & Search shown as percentages only
# - External Link buttons with warning & percentage
# - Video actions: `Open Video`, `Reset`, `Accept / Admin Approve` (NO Permanent Approve)
# - `Back` returns to exact originating page (`adm_traffic` or `adm_vsec`)
# ==============================================================================
def _build_rejection_financial_summary_note(rej_res: dict, user_id: str) -> str:
    notes = []
    cancelled_wds = rej_res.get("auto_cancelled_wds") or []
    if cancelled_wds:
        tot_w = sum(float(item.get("amount") or 0.0) for item in cancelled_wds)
        notes.append(
            f"🔄 <b>পেন্ডিং উইথড্র ক্যানসেল ও সমন্বয়:</b> আপনার পেন্ডিং থাকা <b>{len(cancelled_wds)}টি উইথড্র ({tot_w:.2f} টাকা)</b> স্বয়ংক্রিয়ভাবে ক্যানসেল হয়ে ব্যালেন্সে ফেরত আনা হয়েছে এবং সেখান থেকে রিজেক্ট হওয়া ভিডিওর টাকা কেটে নেওয়া হয়েছে।"
        )
    u_after = get_user(user_id) or {}
    debt_now = float(u_after.get("debt_balance", 0.0) or 0.0)
    if debt_now > 0:
        notes.append(
            f"⚠️ <b>ঋণ / মাইনাস ব্যালেন্স (-{debt_now:.2f} টাকা):</b> আপনার একাউন্টে পর্যাপ্ত ব্যালেন্স বা পেন্ডিং উইথড্র না থাকায় এই ভিডিওর আন্ডারে <b>-{debt_now:.2f} টাকা</b> আপনার একাউন্টে ঋণ (Minus) হয়ে রয়েছে। পরবর্তীতে আপনার নতুন ভিডিওর ভিউজ বা পরবর্তী ইনকাম থেকে এই <b>{debt_now:.2f} টাকা</b> স্বয়ংক্রিয়ভাবে মাইনাস হয়ে কেটে নেওয়ার পর পুনরায় আপনার মূল ব্যালেন্সে টাকা গণনা শুরু হবে।"
        )
    return ("\n\n" + "\n".join(notes)) if notes else ""


def _append_video_traffic_and_ext_links_ui(
    v_row,
    kb=None,
    sec_short: str = "ba",
    plat_flt: str = "all",
    from_traffic_page: bool = False,
    include_admin_actions: bool = True
) -> str:
    """
    Enterprise v9.0 Traffic Source & External Link UI Renderer:
    - Shows `Unknown / Unavailable` when reliable platform analytics data is unavailable
      (`traffic_data_available == 0` or `channel_page_pct is None`); never fabricates 75%/25% defaults.
    - Shows Channel Page, Profile Page, and Search Traffic strictly as Percentage and View Count
      (never creates External Link Buttons for them).
    - Separates currently Active External Links (`is_active == 1`) from historical deactivated links
      (`is_active == 0`), and opens the actual external website (`final_url` or `original_url`) on click.
    """
    sub_id = str(v_row["sub_id"])
    plat_low = str(v_row["platform"] or "youtube").lower()
    v_keys = v_row.keys() if hasattr(v_row, "keys") else v_row

    raw_ch_pct = v_row["channel_page_pct"] if "channel_page_pct" in v_keys else None
    raw_sr_pct = v_row["search_pct"] if "search_pct" in v_keys else None
    raw_ex_pct = v_row["external_pct"] if "external_pct" in v_keys else None
    ch_views = int(v_row["channel_page_views"] or 0) if "channel_page_views" in v_keys and v_row["channel_page_views"] is not None else 0
    sr_views = int(v_row["search_views"] or 0) if "search_views" in v_keys and v_row["search_views"] is not None else 0
    ex_views = int(v_row["external_views"] or 0) if "external_views" in v_keys and v_row["external_views"] is not None else 0
    ded_v = int(v_row["deducted_external_views"] if "deducted_external_views" in v_keys and v_row["deducted_external_views"] is not None else 0)

    traffic_avail = bool(
        (int(v_row["traffic_data_available"] or 0) == 1)
        if ("traffic_data_available" in v_keys and v_row["traffic_data_available"] is not None)
        else (raw_ch_pct is not None and raw_sr_pct is not None)
    )
    traffic_status_str = str(
        (v_row["traffic_source_status"] if "traffic_source_status" in v_keys and v_row["traffic_source_status"] else "")
        or ("Verified Analytics" if traffic_avail else "Unknown / Unavailable")
    )

    if plat_low == "tiktok":
        ch_lbl = "🎵 TikTok প্রোফাইল / পেজ থেকে"
        sr_lbl = "🔍 TikTok সার্চ (Search) থেকে"
    else:
        ch_lbl = "📺 YouTube চ্যানেল / পেজ থেকে"
        sr_lbl = "🔍 YouTube সার্চ (Search) থেকে"

    active_ext_links = get_video_external_links(sub_id=sub_id, active_only=True)
    all_ext_links = get_video_external_links(sub_id=sub_id, active_only=False)
    inactive_ext_links = [el for el in all_ext_links if int(el.get("is_active", 1) or 0) == 0]

    if not traffic_avail:
        traffic_lines = [
            FULL_WIDTH_DIVIDER,
            f"📊 <b>ট্রাফিক সোর্স ও অর্গানিক ভিউ বিশ্লেষণ:</b> ℹ️ <b>[{esc(traffic_status_str)}]</b>",
            f"├ {ch_lbl}: <b>Unknown / Unavailable</b>",
            f"└ {sr_lbl}: <b>Unknown / Unavailable</b>"
            + (f" <i>[কর্তনকৃত ভিউ: -{ded_v}]</i>" if ded_v > 0 else "")
        ]
    else:
        ch_pct = float(raw_ch_pct or 0.0)
        sr_pct = float(raw_sr_pct or 0.0)
        ex_pct = float(raw_ex_pct or 0.0)
        has_ext = bool(ex_pct > 0 or active_ext_links)
        susp_tag = " ⚠️ <b>[এক্সটার্নাল লিংক শনাক্ত!]</b>" if has_ext else " ✅ <b>[অর্গানিক সোর্স]</b>"
        if not has_ext:
            traffic_lines = [
                FULL_WIDTH_DIVIDER,
                f"📊 <b>ট্রাফিক সোর্স ও অর্গানিক ভিউ বিশ্লেষণ:{susp_tag}</b>",
                f"├ {ch_lbl}: <b>{ch_pct:.1f}% ({ch_views} ভিউ)</b>",
                f"└ {sr_lbl}: <b>{sr_pct:.1f}% ({sr_views} ভিউ)</b>"
                + (f" <i>[কর্তনকৃত ভিউ: -{ded_v}]</i>" if ded_v > 0 else "")
            ]
        else:
            traffic_lines = [
                FULL_WIDTH_DIVIDER,
                f"📊 <b>ট্রাফিক সোর্স ও অর্গানিক ভিউ বিশ্লেষণ:{susp_tag}</b>",
                f"├ {ch_lbl}: <b>{ch_pct:.1f}% ({ch_views} ভিউ)</b>",
                f"├ {sr_lbl}: <b>{sr_pct:.1f}% ({sr_views} ভিউ)</b>",
                f"└ 🌐 এক্সটার্নাল লিংক থেকে: <b>{ex_pct:.1f}% ({ex_views} ভিউ)</b>"
                + (f" <i>[কর্তনকৃত ভিউ: -{ded_v}]</i>" if ded_v > 0 else "")
            ]

    if active_ext_links:
        traffic_lines.append("\n⚠️ <b>বর্তমানে সক্রিয় (Active) এক্সটার্নাল লিংকসমূহ:</b>")
        for idx, el in enumerate(active_ext_links, start=1):
            e_id = el["ext_id"]
            dom = el.get("domain") or "External Site"
            orig_u = str(el.get("original_url") or el.get("source_url") or "").strip()
            final_u = str(el.get("final_url") or orig_u).strip()
            target_web_url = final_u or orig_u
            l_pct = float(el.get("views_pct") or 0.0)
            l_cnt = int(el.get("views_count") or 0)
            st_el = str(el.get("status") or "pending").upper()
            redir_note = f" (Original: <code>{esc(orig_u)}</code>)" if (orig_u and final_u and orig_u != final_u) else ""
            traffic_lines.append(
                f"  {idx}. 🔗 <a href=\"{esc(target_web_url)}\">{esc(dom)}</a>{redir_note} — <b>{l_pct:.1f}% ({l_cnt} ভিউ) [{st_el}]</b>"
            )
            if kb is not None and target_web_url.startswith(("http://", "https://")):
                kb.row(make_btn(f"🔗 {dom} — {l_pct:.1f}% ({l_cnt} ভিউ)", url=target_web_url, style="danger"))
                if include_admin_actions and not from_traffic_page:
                    kb.row(
                        make_btn(f"✅ Accept ({l_pct:.1f}%)", callback_data=f"ext_act:app:{e_id}:{sec_short}:{plat_flt}", style="success"),
                        make_btn(f"🔄 Reset (০৳ ও রিসেট)", callback_data=f"ext_act:reset:{sub_id}:{sec_short}:{plat_flt}", style="primary"),
                        make_btn(f"❌ Reject ({l_cnt} ভিউ)", callback_data=f"ext_act:rej:{e_id}:{sec_short}:{plat_flt}", style="danger")
                    )

    if inactive_ext_links:
        traffic_lines.append("\n📜 <b>পূর্বে শনাক্তকৃত কিন্তু নতুন স্ক্যানে অনুপস্থিত (Inactive History) লিংক:</b>")
        for idx_h, el_h in enumerate(inactive_ext_links[:5], start=1):
            dom_h = el_h.get("domain") or "External Site"
            orig_h = str(el_h.get("original_url") or el_h.get("source_url") or "").strip()
            deact_at = str(el_h.get("deactivated_at") or el_h.get("last_seen_at") or "").strip()
            traffic_lines.append(
                f"  • <s>{esc(dom_h)}</s> (<code>{esc(orig_h)}</code>) — <i>[Inactive / Deactivated {esc(deact_at)}]</i>"
            )

    return "\n".join(traffic_lines)


def _notify_admins_of_external_links(u_dict: dict, sub_id: str, platform_key: str, total_views: int, traffic_info: dict, saved_links: list):
    if not saved_links:
        return
    p_title = PLATFORMS.get(platform_key, {}).get("title", platform_key.upper())
    u_lbl = get_user_label(u_dict)
    uid = str(u_dict.get("user_id", ""))

    for el in saved_links:
        if int(el.get("notified") or 0) == 1:
            continue
        ext_id = el["ext_id"]
        s_url = el["source_url"]
        dom = el.get("domain") or "External Site"
        l_pct = float(el.get("views_pct") or 0.0)
        l_cnt = int(el.get("views_count") or 0)

        msg_txt = get_msg(
            "external_traffic_alert_msg",
            user_label=esc(u_lbl),
            user_id=esc(uid),
            sub_id=esc(sub_id),
            platform=esc(p_title),
            total_views=total_views,
            channel_pct=f"{float(traffic_info.get('channel_page_pct', 0)):.1f}",
            channel_views=int(traffic_info.get("channel_page_views", 0)),
            search_pct=f"{float(traffic_info.get('search_pct', 0)):.1f}",
            search_views=int(traffic_info.get("search_views", 0)),
            external_pct=f"{float(traffic_info.get('external_pct', 0)):.1f}",
            external_views=int(traffic_info.get("external_views", 0)),
            source_url=esc(s_url),
            link_pct=f"{l_pct:.1f}",
            link_views=l_cnt
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"⚠️ এক্সটার্নাল ওয়েবসাইট ভিজিট করুন ({dom}) — {l_pct:.1f}%", url=s_url, style="danger"))
        kb.row(
            make_btn(f"✅ Accept Video (Admin Approve)", callback_data=f"ext_act:app:{ext_id}:tr:all", style="success"),
            make_btn(f"🔄 Reset (০৳ ও রিসেট)", callback_data=f"ext_act:reset:{sub_id}:tr:all", style="primary")
        )
        kb.row(
            make_btn("❌ Reject Video (সম্পূর্ণ টাকা কর্তন)", callback_data=f"ext_act:rej:{ext_id}:tr:all", style="danger"),
            make_btn("👤 ইউজারের প্রোফাইলে যান", callback_data=f"adm_uview:{uid}:tr:{sub_id}:all:0", style="primary")
        )
        kb.row(make_btn("🔎 ট্রাফিক সোর্স ভিডিও কার্ড দেখুন", callback_data=f"adm_tr_item:{sub_id}:all:0", style="primary"))
        for adm_id in get_all_admin_ids():
            try:
                safe_send(adm_id, msg_txt, reply_markup=kb)
            except Exception:
                pass
        with db_lock:
            mark_external_link_notified(ext_id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_traffic:") or c.data.startswith("adm_tr_item:") or c.data.startswith("ext_act:"))
@_guard("admin_traffic_and_ext_links", sensitive=True)
def handle_admin_traffic_and_external_links(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)

    if call.data.startswith("ext_act:"):
        parts = call.data.split(":")
        act_short = parts[1]
        target_id = parts[2]
        sec_short = parts[3] if len(parts) > 3 else "tr"
        plat_flt = parts[4] if len(parts) > 4 else "all"

        if act_short == "reset":
            # Part 18, Items 173–174: Reset Video Earnings to 0 and restart view tracking from current views!
            sub_id = target_id
            with db_lock:
                conn = get_connection()
                try:
                    with conn:
                        res_rst = reset_external_link_video_earnings(conn, sub_id=sub_id, admin_id=admin_uid)
                except Exception as exc:
                    conn.close()
                    bot.answer_callback_query(call.id, f"⚠️ {str(exc)[:140]}", show_alert=True)
                    return
                conn.close()
            rev_a = float(res_rst.get("reversed_amount") or 0.0)
            bot.answer_callback_query(
                call.id,
                f"🔄 ভিডিওটি Reset করা হয়েছে! পূর্বের আয় ({rev_a:.2f}৳) কেটে ০৳ করা হয়েছে এবং বর্তমান ভিউ থেকে পুনরায় নতুন ভিউ গণনা শুরু হবে।",
                show_alert=True
            )
            if sec_short == "tr":
                call.data = f"adm_tr_item:{sub_id}:{plat_flt}:0"
                return handle_admin_traffic_and_external_links(call)
            call.data = f"adm_vsec_item:{sec_short}:{sub_id}:{plat_flt}"
            return handle_admin_video_approval_sections(call)

        if act_short == "app_vid":
            sub_id = target_id
            earn_days = int(get_setting("earning_duration_days", get_setting("view_tracking_days", "5")))
            with db_lock:
                conn = get_connection()
                try:
                    with conn:
                        admin_accept_bot_approved_video(conn, sub_id=sub_id, admin_id=admin_uid, earning_duration_days=earn_days)
                except Exception as exc:
                    conn.close()
                    bot.answer_callback_query(call.id, f"⚠️ {str(exc)[:140]}", show_alert=True)
                    return
                conn.close()
            bot.answer_callback_query(call.id, "✅ ভিডিওটি Accept (Admin Approve) করা হয়েছে!", show_alert=True)
            if sec_short == "tr":
                call.data = f"adm_tr_item:{sub_id}:{plat_flt}:0"
                return handle_admin_traffic_and_external_links(call)
            call.data = f"adm_vsec_item:aa:{sub_id}:{plat_flt}"
            return handle_admin_video_approval_sections(call)

        ext_id = target_id
        decision = "approve" if act_short == "app" else "reject"

        with db_lock:
            conn = get_connection()
            try:
                with conn:
                    res = resolve_external_link_financial_action(conn, ext_id=ext_id, decision=decision, admin_id=admin_uid)
            except Exception as exc:
                conn.close()
                bot.answer_callback_query(call.id, f"⚠️ {str(exc)[:140]}", show_alert=True)
                return
            conn.close()

        sub_id = res["sub_id"]
        if decision == "approve":
            toast = f"✅ এক্সটার্নাল লিংক ({res['domain']} — {res['views_pct']}%) অ্যাকসেপ্ট করা হয়েছে! ভিডিওটি Admin Approved তালিকায় যুক্ত হয়েছে।"
            next_sec = "aa"
        else:
            rev_a = float(res.get("reversed_amount", 0.0))
            fin_note = _build_rejection_financial_summary_note(res, res["user_id"])
            toast = f"❌ এক্সটার্নাল প্ল্যাটফর্ম ({res['domain']}) থেকে ফেক ভিউ আসায় ভিডিওটি Reject করা হয়েছে এবং {rev_a:.2f}৳ কেটে নেওয়া হয়েছে!"
            next_sec = "rj"
            try:
                safe_send(
                    int(res["user_id"]),
                    f"⚠️ <b>এক্সটার্নাল লিংক / ফেক ভিউ রিজেক্ট নোটিশ!</b>\n{FULL_WIDTH_DIVIDER}\n"
                    f"আপনার ভিডিও (<code>{esc(sub_id)}</code>)-এ এক্সটার্নাল সাইট (<code>{esc(res['domain'])}</code>) থেকে আসা <b>{res['views_pct']}% ({res['views_count']} ভিউ)</b> অ্যাডমিন যাচাইয়ে বাতিল (Rejected) করা হয়েছে।\n"
                    f"💸 রিজেক্ট হওয়া ভিডিওর আন্ডারে কর্তনকৃত ক্রেডিট: <b>{rev_a:.2f} টাকা</b>"
                    + fin_note
                )
            except Exception:
                pass

        bot.answer_callback_query(call.id, toast, show_alert=True)
        if sec_short == "tr":
            call.data = f"adm_tr_item:{sub_id}:{plat_flt}:0"
            return handle_admin_traffic_and_external_links(call)
        call.data = f"adm_vsec_item:{next_sec}:{sub_id}:{plat_flt}"
        return handle_admin_video_approval_sections(call)

    if call.data.startswith("adm_tr_item:"):
        # Part 18, Items 168–176: Dedicated Traffic Source Video Card
        # - No raw long URL in status text (clean `<a href>` link)
        # - Channel & Search as percentages only
        # - Actions: `Open Video`, `Reset`, `Accept (Admin Approve)` — NO `Permanent Approve`!
        # - Back button returns to exact Traffic Source page (`adm_traffic:<plat_flt>:<page>`)
        parts = call.data.split(":")
        sub_id = parts[1]
        plat_flt = parts[2] if len(parts) > 2 else "all"
        page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v:
            bot.answer_callback_query(call.id, "ভিডিওটি পাওয়া যায়নি!", show_alert=True)
            return

        u_o = get_user(v["user_id"]) or {}
        plat_title = PLATFORMS.get(v["platform"], {}).get("title", v["platform"].upper())
        u_plat_rows = get_user_platforms(v["user_id"], v["platform"])
        acc_pid = int(v["platform_account_id"] or 0) if "platform_account_id" in v.keys() else 0
        acc_ord_idx = next((idx_p for idx_p, p in enumerate(u_plat_rows, start=1) if int(p.get("id") or 0) == acc_pid), 1)
        acc_row_match = next((p for p in u_plat_rows if int(p.get("id") or 0) == acc_pid), (u_plat_rows[0] if u_plat_rows else None))
        if acc_row_match:
            ord_bn = ORDINAL_ACCOUNT_LABELS_BN.get(acc_ord_idx, f"#{acc_ord_idx} অ্যাকাউন্ট")
            plat_title = f"{plat_title} — {ord_bn} ({acc_row_match.get('display_name') or acc_row_match.get('profile_handle')})"
        v_link = v["video_url"] or v["url"]
        cred_amt = float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0))

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔗 Open Video (ভিডিওটি ওপেন করুন)", url=v_link, style="primary"))
        traffic_block = _append_video_traffic_and_ext_links_ui(v, kb, sec_short="tr", plat_flt=plat_flt, from_traffic_page=True)

        txt = (
            f"🌐 <b>ট্রাফিক সোর্স ও এক্সটার্নাল লিংক বিশ্লেষণ কার্ড</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"👤 ইউজার: <b>{esc(get_user_label(u_o))}</b> (ID: <code>{esc(v['user_id'])}</code> | UID: <code>{esc(format_display_app_uid(v['app_uid']))}</code>)\n"
            f"🌐 প্ল্যাটফর্ম: <b>{esc(plat_title)}</b>\n"
            f"🎬 ভিডিও: <a href=\"{esc(v_link)}\">🔗 ভিডিও লিংক / ওপেন ভিডিও</a>\n"
            f"👁️ বর্তমান ভিউ: <b>{v['current_views']}</b> (পেইড ভিউ: <b>{v['paid_views']}</b>)\n"
            f"💰 অর্জিত আয়: <b>{cred_amt:.2f} টাকা</b>\n"
            f"📋 বর্তমান স্ট্যাটাস: <b>{esc(str(v['admin_status'] or v['bot_status']).upper())}</b>\n"
            f"{traffic_block}"
        )
        kb.row(
            make_btn("✅ Accept (Admin Approve - 0৳ Extra)", callback_data=f"ext_act:app_vid:{sub_id}:tr:{plat_flt}", style="success"),
            make_btn("❌ Reject (টাকা কর্তন ও রিজেক্ট)", callback_data=f"adm_vrej_prompt:{sub_id}:tr:{plat_flt}", style="danger")
        )
        kb.row(
            make_btn("🔄 Reset (আয় ০৳ ও রিসেট)", callback_data=f"ext_act:reset:{sub_id}:tr:{plat_flt}", style="primary"),
            make_btn("👤 ইউজারের প্রোফাইলে যান", callback_data=f"adm_uview:{v['user_id']}:tr:{sub_id}:{plat_flt}:{page}", style="primary")
        )
        kb.row(make_btn("🔙 ট্রাফিক সোর্স তালিকায় ফিরে যান", callback_data=f"adm_traffic:{plat_flt}:{page}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    parts = call.data.split(":")
    plat_flt = parts[1] if len(parts) > 1 else "all"
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    per_p = 8

    with db_lock:
        conn = get_connection()
        where_c = ["COALESCE(is_trashed, 0) = 0", "LOWER(platform) IN ('youtube', 'tiktok')"]
        params = []
        if plat_flt in ("youtube", "tiktok"):
            where_c.append("LOWER(platform) = ?")
            params.append(plat_flt)
        v_rows = conn.execute(
            f"SELECT * FROM videos WHERE {' AND '.join(where_c)} ORDER BY COALESCE(external_pct, 0) DESC, rowid DESC",
            tuple(params)
        ).fetchall()
        conn.close()

    p_meta = paginate_items(v_rows, page=page, per_page=per_p)
    kb = types.InlineKeyboardMarkup()
    kb.row(
        make_btn(f"{'✅ ' if plat_flt=='youtube' else ''}📺 YouTube (YT)", callback_data="adm_traffic:youtube:0", style="danger" if plat_flt == "youtube" else "primary"),
        make_btn(f"{'✅ ' if plat_flt=='tiktok' else ''}🎵 TikTok", callback_data="adm_traffic:tiktok:0", style="success" if plat_flt == "tiktok" else "primary")
    )
    if plat_flt != "all":
        kb.row(make_btn("🌐 উভয় প্ল্যাটফর্ম দেখুন (YouTube & TikTok)", callback_data="adm_traffic:all:0", style="primary"))

    lines = [
        f"🌐 <b>ট্রাফিক সোর্স ও এক্সটার্নাল লিংক বিশ্লেষণ ({plat_flt.upper()} — পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']}):</b>",
        FULL_WIDTH_DIVIDER,
        "প্রতিটি ভিডিওর ভিউ কোন সোর্স (চ্যানেল/প্রোফাইল পেজ, সার্চ, এক্সটার্নাল লিংক) থেকে কত পার্সেন্ট এসেছে তা নিচে দেখুন:"
    ]
    for v in p_meta["items"]:
        u_o = get_user(v["user_id"])
        vk = v.keys() if hasattr(v, "keys") else v
        tr_avail = bool((int(v["traffic_data_available"] or 0) == 1) if ("traffic_data_available" in vk and v["traffic_data_available"] is not None) else (v["channel_page_pct"] is not None and v["search_pct"] is not None))
        if tr_avail:
            ch_p = float(v["channel_page_pct"] or 0.0)
            sr_p = float(v["search_pct"] or 0.0)
            ex_p = float(v["external_pct"] or 0.0)
            ic = "⚠️" if ex_p > 0 else "✅"
            summary_tag = f"Ch:{ch_p:.0f}% | Search:{sr_p:.0f}% | Ext:{ex_p:.0f}%"
            btn_st_tr = "danger" if ex_p > 0 else "primary"
        else:
            ic = "ℹ️"
            summary_tag = "Traffic: Unknown / Unavailable"
            btn_st_tr = "primary"
        kb.row(
            make_btn(
                f"{ic} [{v['platform'].upper()}] {get_user_label(u_o)} — {summary_tag}",
                callback_data=f"adm_tr_item:{v['sub_id']}:{plat_flt}:{p_meta['page']}",
                style=btn_st_tr
            )
        )

    nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_traffic:{plat_flt}")
    if nav_row:
        kb.row(*nav_row)
    kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
    safe_edit(call.message.chat.id, call.message.message_id, "\n".join(lines), reply_markup=kb)
    bot.answer_callback_query(call.id)


# ==============================================================================
# PART 11–13: ADMIN DASHBOARD MASTER METRICS & 5-SECTION VIDEO APPROVAL
# - Includes 24h Inactive, 3-4 Days Inactive, and Negative / Problem-Inactive users
# - Clicking a Video Approval Section shows ONLY YouTube & TikTok buttons first (no redundant 5 status buttons!)
# - Shows how many videos each user submitted (`[মোট ভিডিও: Xটি]`)
# ==============================================================================
def render_admin_master_metrics_text() -> str:
    now_ts = time.time()
    ts_24h = now_ts - 86400.0
    ts_3d = now_ts - (3.0 * 86400.0)
    with db_lock:
        conn = get_connection()
        u_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_u,
                SUM(CASE WHEN registered = 1 THEN 1 ELSE 0 END) as reg_u,
                SUM(CASE WHEN registered = 0 THEN 1 ELSE 0 END) as pend_ver_u,
                SUM(CASE WHEN status = 'active' AND COALESCE(bio_frozen, 0) = 0 THEN 1 ELSE 0 END) as act_u,
                SUM(CASE WHEN status = 'inactive' OR COALESCE(bio_frozen, 0) = 1 THEN 1 ELSE 0 END) as inact_u,
                SUM(CASE WHEN registered = 1 AND last_active_ts > 0 AND (last_active_ts <= ? AND last_active_ts > ?) THEN 1 ELSE 0 END) as inact_24h_u,
                SUM(CASE WHEN registered = 1 AND last_active_ts > 0 AND last_active_ts <= ? THEN 1 ELSE 0 END) as inact_3d_u,
                SUM(CASE WHEN COALESCE(debt_balance, 0) > 0 OR COALESCE(balance, 0) < 0 OR COALESCE(bio_frozen, 0) = 1 THEN 1 ELSE 0 END) as neg_prob_u,
                SUM(CASE WHEN status IN ('banned', 'deleted') THEN 1 ELSE 0 END) as ban_u,
                SUM(balance) as sum_bal,
                SUM(total_earned) as sum_earned,
                SUM(held_balance) as sum_held,
                SUM(debt_balance) as sum_debt
            FROM users
        """, (ts_24h, ts_3d, ts_3d)).fetchone()
        v_counts = get_video_approval_counts(conn)
        v_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_v,
                SUM(CASE WHEN (flagged_suspicious = 1 OR COALESCE(external_pct, 0) > 0) AND COALESCE(is_trashed, 0) = 0 THEN 1 ELSE 0 END) as flag_v
            FROM videos
            WHERE LOWER(platform) IN ('youtube', 'tiktok')
        """).fetchone()
        w_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_w,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pend_w,
                SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_w,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as canc_w,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rej_w,
                SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as paid_amt,
                SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) as pend_amt
            FROM withdrawals
        """).fetchone()
        conn.close()

    return get_msg(
        "admin_dashboard_msg",
        total_users=u_stats["total_u"] or 0,
        verified_users=u_stats["reg_u"] or 0,
        pending_users=u_stats["pend_ver_u"] or 0,
        active_users=u_stats["act_u"] or 0,
        inactive_users=u_stats["inact_u"] or 0,
        inactive_24h_users=u_stats["inact_24h_u"] or 0,
        inactive_3d_users=u_stats["inact_3d_u"] or 0,
        neg_problem_users=u_stats["neg_prob_u"] or 0,
        negative_activity_users=u_stats["neg_prob_u"] or 0,
        banned_users=u_stats["ban_u"] or 0,
        total_videos=v_stats["total_v"] or 0,
        pending_videos=v_counts.get("pending", {}).get("total", 0),
        bot_approved_videos=v_counts["bot_approve"]["total"],
        admin_approved_videos=v_counts["admin_approve"]["total"],
        perm_approved_videos=v_counts["permanent_approve"]["total"],
        rejected_videos=v_counts["rejected"]["total"],
        trashed_videos=v_counts["trash"]["total"],
        suspicious_videos=v_stats["flag_v"] or 0,
        total_earnings=f"{float(u_stats['sum_earned'] or 0):.2f}",
        available_balance=f"{float(u_stats['sum_bal'] or 0):.2f}",
        held_balance=f"{float(u_stats['sum_held'] or w_stats['pend_amt'] or 0):.2f}",
        debt_balance=f"{float(u_stats['sum_debt'] or 0):.2f}",
        total_wd_amount=f"{float((w_stats['paid_amt'] or 0) + (w_stats['pend_amt'] or 0)):.2f}",
        paid_wd_amount=f"{float(w_stats['paid_amt'] or 0):.2f}",
        paid_wd_count=w_stats["paid_w"] or 0,
        pending_wd_count=w_stats["pend_w"] or 0,
        cancelled_only_wd_count=w_stats["canc_w"] or 0,
        rejected_only_wd_count=w_stats["rej_w"] or 0,
        cancelled_wd_count=(w_stats["canc_w"] or 0) + (w_stats["rej_w"] or 0),
        rejected_wd_count=w_stats["rej_w"] or 0
    )


@bot.callback_query_handler(func=lambda c: c.data in ("admin_hub", "adm_view_metrics", "adm_logout", "adm_toggle_bottom_menu"))
@_guard("admin_dashboard")
def handle_admin_master_dashboard(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)

    if call.data == "adm_toggle_bottom_menu":
        u = get_user(uid) or ensure_user(call.from_user)
        cur_abm = int(u.get("admin_bottom_menu") or 0)
        new_abm = 0 if cur_abm == 1 else 1
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET admin_bottom_menu = ? WHERE user_id = ?", (new_abm, uid))
            conn.close()
        if new_abm == 1:
            if getattr(call, "message", None) and getattr(call.message, "message_id", None):
                try:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                except Exception:
                    pass
            bot.answer_callback_query(call.id, "⌨️ অ্যাডমিন নিচের বাটন মেনু চালু করা হয়েছে!")
            safe_send(
                call.message.chat.id,
                "✅ <b>অ্যাডমিন বটম মেনু (Bottom Menu) চালু হয়েছে!</b>\nএখন মেসেজ বক্সের উপরে কোনো বাটন আসবে না—অ্যাডমিন প্যানেলের সকল পেজ ও সাব-পেজের বাটন নিচে কালারফুলভাবে দেখা যাবে।\n\n" + get_msg("admin_welcome_msg"),
                reply_markup=build_admin_bottom_reply_keyboard(uid),
                menu_id="admin_home"
            )
        else:
            USER_ACTIVE_BOTTOM_BUTTON_MAP.pop(uid, None)
            bot.answer_callback_query(call.id, "🔵 অ্যাডমিন উপরের মেসেজ বক্স বাটন চালু করা হয়েছে!")
            safe_send(
                call.message.chat.id,
                "✅ <b>অ্যাডমিন উপরের মেসেজ বক্স বাটন চালু হয়েছে!</b>\nনিচের বাটন বন্ধ করা হয়েছে।",
                reply_markup=types.ReplyKeyboardRemove()
            )
            safe_send(call.message.chat.id, get_msg("admin_welcome_msg"), reply_markup=build_admin_dashboard_keyboard(uid, force_inline=True), menu_id="admin_home")
        return

    if call.data == "adm_logout":
        admin_unlocked_sessions.pop(uid, None)
        user_memory_states.pop(uid, None)
        try:
            lock_admin_session(uid)
        except Exception:
            pass
        cleanup_user_ui_messages(call.message.chat.id, uid)
        if getattr(call, "message", None) and getattr(call.message, "message_id", None):
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
        sent_al = safe_send(call.message.chat.id, get_msg("admin_logout_confirm_msg"), track_ui=True, auto_clean_prev=False)
        if sent_al and getattr(sent_al, "message_id", None):
            schedule_message_auto_delete(call.message.chat.id, sent_al.message_id, delay_sec=7.0, uid=uid)
        bot.answer_callback_query(call.id, "অ্যাডমিন প্যানেল থেকে লগআউট সম্পন্ন হয়েছে!")
        return

    user_memory_states.pop(uid, None)
    if call.data == "adm_view_metrics":
        txt = render_admin_master_metrics_text()
    else:
        txt = get_msg("admin_welcome_msg")
    safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: (
    c.data.startswith("adm_vsec:") or
    c.data.startswith("adm_vsec_item:") or
    c.data.startswith("adm_perm_sel:") or
    c.data.startswith("adm_perm_sel_all:") or
    c.data.startswith("adm_perm_trash_sel_exec:") or
    c.data.startswith("adm_vrej_prompt:") or
    c.data.startswith("adm_vrej_cancel:") or
    c.data.startswith("adm_vrej_exec:") or
    c.data.startswith("adm_vrereview:") or
    c.data.startswith("adm_perm_approve:") or
    c.data.startswith("adm_trash_move:") or
    c.data in ("adm_perm_trash_all_confirm", "adm_perm_trash_all_exec")
))
@_guard("admin_video_sections")
def handle_admin_video_approval_sections(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)
    if not str(call.data or "").startswith(("adm_vrej_prompt:", "adm_vrej_exec:", "adm_vrej_cancel:")):
        if (user_memory_states.get(admin_uid) or {}).get("admin_action") == "custom_reject_video_reason":
            user_memory_states.pop(admin_uid, None)

    if call.data.startswith("adm_perm_sel:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        plat_flt = parts[2] if len(parts) > 2 else "all"
        page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
        sel_set = admin_perm_selected_videos.setdefault(admin_uid, set())
        if sub_id in sel_set:
            sel_set.remove(sub_id)
        else:
            sel_set.add(sub_id)
        bot.answer_callback_query(call.id, f"সিলেক্টেড ভিডিও: {len(sel_set)}টি")
        call.data = f"adm_vsec:pa:{plat_flt}:{page}"

    if call.data.startswith("adm_perm_sel_all:"):
        parts = call.data.split(":")
        plat_flt = parts[1] if len(parts) > 1 else "all"
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        with db_lock:
            conn = get_connection()
            if plat_flt in ("youtube", "tiktok"):
                rows_p = conn.execute(
                    "SELECT sub_id FROM videos WHERE COALESCE(permanent_approved, 0) = 1 AND COALESCE(is_trashed, 0) = 0 AND admin_status != 'rejected' AND LOWER(platform) = ?",
                    (plat_flt,)
                ).fetchall()
            else:
                rows_p = conn.execute(
                    "SELECT sub_id FROM videos WHERE COALESCE(permanent_approved, 0) = 1 AND COALESCE(is_trashed, 0) = 0 AND admin_status != 'rejected' AND LOWER(platform) IN ('youtube', 'tiktok')"
                ).fetchall()
            conn.close()
        all_ids = {r["sub_id"] for r in rows_p}
        sel_set = admin_perm_selected_videos.setdefault(admin_uid, set())
        if all_ids and all_ids.issubset(sel_set):
            sel_set.difference_update(all_ids)
            bot.answer_callback_query(call.id, "সব সিলেকশন ক্লিয়ার করা হয়েছে।")
        else:
            sel_set.update(all_ids)
            bot.answer_callback_query(call.id, f"সব ({len(sel_set)}টি) সিলেক্ট করা হয়েছে!")
        call.data = f"adm_vsec:pa:{plat_flt}:{page}"

    if call.data.startswith("adm_perm_trash_sel_exec:"):
        parts = call.data.split(":")
        plat_flt = parts[1] if len(parts) > 1 else "all"
        sel_set = list(admin_perm_selected_videos.get(admin_uid) or [])
        if not sel_set:
            bot.answer_callback_query(call.id, "প্রথমে অন্তত ১টি ভিডিও সিলেক্ট করুন!", show_alert=True)
            return
        with db_lock:
            res_mv = move_all_permanent_approved_to_trash(sub_ids=sel_set, actor_id=admin_uid)
        admin_perm_selected_videos.pop(admin_uid, None)
        bot.answer_callback_query(
            call.id,
            f"🗑️ সিলেক্টকৃত {res_mv.get('moved_count', 0)}টি ভিডিও কোনো ব্যালেন্স কর্তন ছাড়াই Trash-এ পাঠানো হয়েছে (ডুপ্লিকেট লক অক্ষুণ্ণ)!",
            show_alert=True
        )
        call.data = f"adm_vsec:pa:{plat_flt}:0"

    if call.data.startswith("adm_vsec:"):
        parts = call.data.split(":")
        sec = _expand_section_code(parts[1])
        plat_flt = parts[2] if len(parts) > 2 else "select"
        page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
        per_p = 8
        s_short = _short_section_code(sec)

        with db_lock:
            conn = get_connection()
            counts = get_video_approval_counts(conn)
            sec_counts = counts.get(sec, counts["bot_approve"])
            conn.close()

        sec_msg_keys = {
            "pending": "admin_pending_only_video_report_msg",
            "bot_approve": "admin_pending_video_report_msg",
            "admin_approve": "admin_approved_video_report_msg",
            "permanent_approve": "admin_permanent_video_report_msg",
            "rejected": "admin_rejected_video_report_msg"
        }

        # Part 13, Items 113–116: When clicking a video approval section, show ONLY YouTube & TikTok buttons first (plus Back),
        # WITHOUT repeating the 5 video approval section buttons inside sub-pages!
        if plat_flt == "select":
            kb = types.InlineKeyboardMarkup()
            kb.row(
                make_btn(f"📺 YouTube ({sec_counts.get('youtube', 0)}টি ভিডিও)", callback_data=f"adm_vsec:{s_short}:youtube:0", style="danger"),
                make_btn(f"🎵 TikTok ({sec_counts.get('tiktok', 0)}টি ভিডিও)", callback_data=f"adm_vsec:{s_short}:tiktok:0", style="primary")
            )
            kb.row(make_btn(f"🌐 উভয় প্ল্যাটফর্ম দেখুন ({sec_counts.get('total', 0)}টি ভিডিও)", callback_data=f"adm_vsec:{s_short}:all:0", style="success"))
            kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
            header = get_msg(
                sec_msg_keys.get(sec, "admin_pending_video_report_msg"),
                platform_filter="YOUTUBE / TIKTOK SELECT",
                total_items=sec_counts.get("total", 0)
            ) + "\n👇 কোন প্ল্যাটফর্মের ভিডিও দেখতে চান তা সিলেক্ট করুন:"
            safe_edit(call.message.chat.id, call.message.message_id, header, reply_markup=kb)
            bot.answer_callback_query(call.id)
            return

        with db_lock:
            conn = get_connection()
            where_clauses = ["COALESCE(is_trashed, 0) = 0", "LOWER(platform) IN ('youtube', 'tiktok')"]
            params = []
            if sec == "pending":
                where_clauses.append("(COALESCE(permanent_approved, 0) = 0 AND admin_status = 'pending' AND bot_status IN ('waiting_views', 'manual_review', 'pending') AND status != 'rejected')")
            elif sec == "bot_approve":
                where_clauses.append("(COALESCE(permanent_approved, 0) = 0 AND admin_status = 'pending' AND bot_status = 'approved' AND status != 'rejected')")
            elif sec == "admin_approve":
                where_clauses.append("(COALESCE(permanent_approved, 0) = 0 AND admin_status = 'approved' AND status != 'rejected')")
            elif sec == "permanent_approve":
                where_clauses.append("(COALESCE(permanent_approved, 0) = 1 AND admin_status != 'rejected' AND status != 'rejected')")
            else:
                where_clauses.append("(admin_status = 'rejected' OR bot_status = 'rejected' OR status = 'rejected')")

            if plat_flt in ("youtube", "tiktok"):
                where_clauses.append("LOWER(platform) = ?")
                params.append(plat_flt)

            where_sql = " AND ".join(where_clauses)
            all_rows = conn.execute(
                f"SELECT * FROM videos WHERE {where_sql} ORDER BY rowid DESC",
                tuple(params)
            ).fetchall()
            user_vid_totals = {}
            for r_cnt in conn.execute("SELECT user_id, COUNT(*) as c FROM videos WHERE COALESCE(is_trashed, 0) = 0 GROUP BY user_id").fetchall():
                user_vid_totals[str(r_cnt["user_id"])] = int(r_cnt["c"] or 0)
            conn.close()

        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        sel_set = admin_perm_selected_videos.get(admin_uid) or set()

        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                f"{'✅ ' if plat_flt == 'youtube' else ''}📺 YouTube ({sec_counts.get('youtube', 0)})",
                callback_data=f"adm_vsec:{s_short}:youtube:0",
                style="danger" if plat_flt == "youtube" else "primary"
            ),
            make_btn(
                f"{'✅ ' if plat_flt == 'tiktok' else ''}🎵 TikTok ({sec_counts.get('tiktok', 0)})",
                callback_data=f"adm_vsec:{s_short}:tiktok:0",
                style="success" if plat_flt == "tiktok" else "primary"
            )
        )
        if plat_flt != "all":
            kb.row(make_btn(f"🌐 উভয় প্ল্যাটফর্ম দেখুন ({sec_counts.get('total', 0)})", callback_data=f"adm_vsec:{s_short}:all:0", style="primary"))

        for v in p_meta["items"]:
            u_o = get_user(v["user_id"])
            u_lbl = get_user_label(u_o)
            u_tot_vids = user_vid_totals.get(str(v["user_id"]), 1)
            p_up = str(v["platform"] or "").upper()
            ext_p = float(v["external_pct"] if "external_pct" in v.keys() and v["external_pct"] is not None else 0.0)
            ext_tag = f" [⚠️Ext:{ext_p:.0f}%]" if ext_p > 0 else ""
            if sec == "pending":
                flag_ic = "🚨" if (v["flagged_suspicious"] or ext_p > 0) else "⏳"
                btn_txt = f"{flag_ic} {u_lbl} ({u_tot_vids}টি) [{p_up}] — {v['current_views']} ভিউ{ext_tag}"
                kb.row(make_btn(btn_txt, callback_data=f"adm_vsec_item:{s_short}:{v['sub_id']}:{plat_flt}", style="primary"))
            elif sec == "bot_approve":
                cred_v = float(v["credited_amount"] or v["reward"] or 0.0)
                btn_txt = f"🤖 {u_lbl} ({u_tot_vids}টি) [{p_up}] — {v['current_views']} ভিউ ({cred_v:.1f}৳){ext_tag}"
                kb.row(make_btn(btn_txt, callback_data=f"adm_vsec_item:{s_short}:{v['sub_id']}:{plat_flt}", style="danger" if ext_p > 0 else "primary"))
            elif sec == "admin_approve":
                cred_v = float(v["credited_amount"] or v["reward"] or 0.0)
                btn_txt = f"👑 {u_lbl} ({u_tot_vids}টি) [{p_up}] — {v['current_views']} ভিউ ({cred_v:.1f}৳){ext_tag}"
                kb.row(make_btn(btn_txt, callback_data=f"adm_vsec_item:{s_short}:{v['sub_id']}:{plat_flt}", style="primary"))
            elif sec == "permanent_approve":
                cred_v = float(v["credited_amount"] or v["reward"] or 0.0)
                chk_mark = "☑️" if v["sub_id"] in sel_set else "⬜"
                kb.row(
                    make_btn(f"{chk_mark} সিলেক্ট", callback_data=f"adm_perm_sel:{v['sub_id']}:{plat_flt}:{p_meta['page']}", style="success" if v["sub_id"] in sel_set else "primary"),
                    make_btn(f"🔒 {u_lbl} ({u_tot_vids}টি) [{p_up}] — {v['current_views']} ভিউ ({cred_v:.1f}৳)", callback_data=f"adm_vsec_item:{s_short}:{v['sub_id']}:{plat_flt}", style="primary")
                )
            else:
                rev_v = float(v["reversed_amount"] or 0.0)
                org_tag = " [অর্গানিক না]" if (v["flagged_suspicious"] or "অর্গানিক" in str(v["rejection_reason"] or "")) else ""
                btn_txt = f"❌ {u_lbl} ({u_tot_vids}টি) [{p_up}]{org_tag} — Reversed: {rev_v:.1f}৳"
                kb.row(make_btn(btn_txt, callback_data=f"adm_vsec_item:{s_short}:{v['sub_id']}:{plat_flt}", style="danger"))

        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_vsec:{s_short}:{plat_flt}")
        if nav_row:
            kb.row(*nav_row)

        if sec == "permanent_approve" and p_meta["total_items"] > 0:
            kb.row(
                make_btn("☑️ সব সিলেক্ট / আনসিলেক্ট (Select All)", callback_data=f"adm_perm_sel_all:{plat_flt}:{p_meta['page']}", style="primary"),
                make_btn(f"🗑️ সিলেক্টকৃত ডিলিট ({len(sel_set)}টি)", callback_data=f"adm_perm_trash_sel_exec:{plat_flt}", style="danger")
            )
            kb.row(make_btn(f"🗑️ সব Permanent Approved ভিডিও একসাথে Trash-এ পাঠান ({p_meta['total_items']}টি)", callback_data="adm_perm_trash_all_confirm", style="danger"))

        # Part 13, Item 115: Do NOT repeat the 5 approval section buttons at the bottom of sub-pages; show clean Back buttons!
        kb.row(
            make_btn("🔙 প্ল্যাটফর্ম সিলেকশনে যান", callback_data=f"adm_vsec:{s_short}:select:0", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )

        header = get_msg(
            sec_msg_keys.get(sec, "admin_pending_video_report_msg"),
            platform_filter=plat_flt.upper(),
            total_items=p_meta["total_items"]
        ) + f"\n📄 পৃষ্ঠা: <b>{p_meta['page']+1}/{p_meta['total_pages']}</b>\nনিচের ভিডিও বাটনে ক্লিক করে বিস্তারিত ট্রাফিক সোর্স ও রিভিউ দেখুন:"
        safe_edit(call.message.chat.id, call.message.message_id, header, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_vsec_item:"):
        parts = call.data.split(":")
        sec = _expand_section_code(parts[1])
        s_short = _short_section_code(sec)
        sub_id = parts[2]
        plat_flt = parts[3] if len(parts) > 3 else "all"

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v:
            bot.answer_callback_query(call.id, "ভিডিওটি পাওয়া যায়নি!", show_alert=True)
            return

        u_o = get_user(v["user_id"]) or {}
        uname_disp = f"@{u_o.get('username').lstrip('@')}" if u_o.get("username") else "N/A"
        plat_title = PLATFORMS.get(v["platform"], {}).get("title", v["platform"].upper())
        v_link = v["video_url"] or v["url"]
        cred_amt = float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0))
        rev_amt = float(v["reversed_amount"] or 0.0)
        is_perm = int(v["permanent_approved"] or 0) == 1
        bot_ver_st = "অর্গানিক ভিউ না (অর্গানিক ভিউ যাচাই হয়নি)" if v["flagged_suspicious"] else f"Bot {str(v['bot_status'] or 'approved').upper()} (100% Organic Verified)"
        rev_st = "PERMANENT APPROVED" if is_perm else str(v["admin_status"] or "pending").upper()

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔗 Open Link (ভিডিওটি ওপেন করে দেখুন)", url=v_link, style="primary"))
        traffic_block = _append_video_traffic_and_ext_links_ui(v, kb, sec_short=s_short, plat_flt=plat_flt)

        if sec == "pending":
            q_deadline = float(v["qualification_deadline_ts"] or 0)
            q_remaining = max(0, round((q_deadline - time.time()) / 3600.0, 1)) if q_deadline else 120.0
            min_target_v = int(get_setting("min_initial_views", "1000"))
            dur_val = int(v["video_duration_sec"] or 0)
            txt = (
                f"⏳ <b>PENDING VIDEO — বিস্তারিত যাচাই কার্ড</b>\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"📅 সাবমিটের সময়: <b>{esc(v['submitted_at'])}</b>\n"
                f"🌐 প্ল্যাটফর্ম: <b>{esc(plat_title)}</b>\n"
                f"👤 সাবমিটকারী: <b>{esc(uname_disp)}</b> ({esc(u_o.get('name') or 'Creator')} | ID: <code>{esc(v['user_id'])}</code>)\n"
                f"🆔 Battle Club UID: <code>{esc(format_display_app_uid(v['app_uid']))}</code>\n"
                f"🔗 ভিডিও: <a href=\"{esc(v_link)}\">🎬 ভিডিও লিংক ওপেন করুন</a>\n"
                f"🔖 Canonical Video ID: <code>{esc(v['canonical_video_id'])}</code>\n"
                f"⏱️ ভিডিওর দৈর্ঘ্য (Duration): <b>{dur_val} সেকেন্ড</b>\n"
                f"🎯 ন্যূনতম ভিউ টার্গেট: <b>{min_target_v} ভিউ</b> (বাকি সময়: <b>{q_remaining} ঘণ্টা</b>)\n"
                f"👁️ বর্তমান ভিউ: <b>{v['current_views']}</b> (yt-dlp: {v['ytdlp_views']} | Page: {v['public_page_views']})\n"
                f"💰 ক্রেডিটকৃত আয়: <b>0.00 টাকা (ভিউ টার্গেট পূরণ না হওয়া পর্যন্ত ০৳)</b>\n"
                f"🛡️ বট ভেরিফিকেশন স্ট্যাটাস: <b>{esc(bot_ver_st)}</b>\n"
                + (f"⚠️ নোট/রিস্ক: <b>{esc(v['risk_reason'])}</b>\n" if v["risk_reason"] else "")
                + f"{traffic_block}\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"ℹ️ <i>Pending ভিডিও নির্দিষ্ট সময়ের মধ্যে {min_target_v}+ ভিউ পূরণ করলে স্বয়ংক্রিয়ভাবে Bot Approved সেকশনে যাবে এবং ক্রেডিট পাবে।</i>"
            )
            kb.row(
                make_btn("🔄 লাইভ ভিউ চেক ও Bot Approve", callback_data=video_decision_callback("bot_credit", sub_id, sec, plat_flt), style="success"),
                make_btn("❌ Reject", callback_data=f"adm_vrej_prompt:{sub_id}:{s_short}:{plat_flt}", style="danger")
            )
            kb.row(make_btn("🗑️ Move to Trash", callback_data=f"adm_trash_move:{sub_id}:{s_short}:{plat_flt}", style="danger"))

        elif sec == "bot_approve":
            txt = (
                f"🤖 <b>BOT APPROVE — ভিডিও রিভিউ কার্ড</b>\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"🆔 User ID: <code>{esc(v['user_id'])}</code> | UID: <code>{esc(format_display_app_uid(v['app_uid']))}</code>\n"
                f"👤 Username: <b>{esc(uname_disp)}</b> ({esc(u_o.get('name') or 'Creator')})\n"
                f"🌐 Platform: <b>{esc(plat_title)}</b>\n"
                f"🔗 Video: <a href=\"{esc(v_link)}\">🎬 ভিডিও লিংক ওপেন করুন</a>\n"
                f"👁️ Current Views: <b>{v['current_views']}</b> (Paid Views: <b>{v['paid_views']}</b>)\n"
                f"🎯 Bot Status: <b>{esc(v['bot_status'])}</b>\n"
                f"💰 Credited Earnings (Bot Approval): <b>{cred_amt:.2f} টাকা</b>\n"
                f"📅 Submission Date: <b>{esc(v['submitted_at'])}</b>\n"
                f"🛡️ Bot Verification Status: <b>{esc(bot_ver_st)}</b>\n"
                f"📋 Review Status: <b>{esc(rev_st)}</b>\n"
                + (f"⚠️ Risk Note: <b>{esc(v['risk_reason'])}</b>\n" if v["risk_reason"] else "")
                + f"{traffic_block}\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"ℹ️ <i>Bot Approved ভিডিও Admin Approve করলে দ্বিতীয়বার কোনো অতিরিক্ত টাকা যুক্ত হবে না, শুধু স্ট্যাটাস পরিবর্তন হবে। আর Reject করলে ওই ভিডিওর আন্ডারে যোগ হওয়া টাকা ({cred_amt:.2f}৳) একাউন্ট থেকে কেটে নেওয়া হবে।</i>"
            )
            kb.row(
                make_btn("✅ Accept (Admin Approve - 0৳ Extra)", callback_data=video_decision_callback("approve", sub_id, sec, plat_flt), style="success"),
                make_btn("🔒 Permanent Approve", callback_data=f"adm_perm_approve:{sub_id}:{s_short}:{plat_flt}", style="success")
            )
            kb.row(
                make_btn("❌ Reject (Reverse Credit)", callback_data=f"adm_vrej_prompt:{sub_id}:{s_short}:{plat_flt}", style="danger"),
                make_btn("🗑️ Move to Trash", callback_data=f"adm_trash_move:{sub_id}:{s_short}:{plat_flt}", style="danger")
            )

        elif sec in ("admin_approve", "permanent_approve"):
            now_ts = time.time()
            end_ts = float(v["earning_end_ts"] or 0)
            mon_active = (end_ts == 0 or now_ts <= end_ts) and v["admin_status"] == "approved" and not is_perm
            cur_status_str = "🔒 Permanent Approved (ভিউ গণনা ও পেমেন্ট সম্পন্ন — আর কোনো টাকা যোগ হবে না)" if is_perm else ("🟢 Active Monitoring" if mon_active else "⏹️ Earning Period Expired")
            earn_period_str = f"{v['earning_start_date'] or v['submitted_at']} হতে {v['earning_end_date'] or 'চলমান'}"
            header_lbl = "🔒 <b>PERMANENT APPROVED VIDEO</b>" if is_perm else "👑 <b>ADMIN APPROVE — ফাইনাল অনুমোদিত ভিডিও</b>"
            txt = (
                f"{header_lbl}\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"👤 User Details: <b>{esc(get_user_label(u_o))}</b> (ID: <code>{esc(v['user_id'])}</code> | UID: <code>{esc(format_display_app_uid(v['app_uid']))}</code>)\n"
                f"🌐 Platform: <b>{esc(plat_title)}</b>\n"
                f"🔗 Video: <a href=\"{esc(v_link)}\">🎬 ভিডিও লিংক ওপেন করুন</a>\n"
                f"👁️ Current Views: <b>{v['current_views']}</b> (Previous: <b>{v['previous_views']}</b> | Eligible Paid: <b>{v['eligible_views'] or v['paid_views']}</b>)\n"
                f"💰 Credited Earnings: <b>{cred_amt:.2f} টাকা</b>\n"
                f"📅 Approval Date: <b>{esc(v['approval_date'] or v['submitted_at'])}</b>\n"
                f"⏳ Earning Period: <b>{esc(earn_period_str)}</b>\n"
                f"📡 Current Status: <b>{cur_status_str}</b>\n"
                f"{traffic_block}"
            )
            if not is_perm:
                kb.row(make_btn("🔒 Mark as PERMANENT APPROVE", callback_data=f"adm_perm_approve:{sub_id}:{s_short}:{plat_flt}", style="success"))
            kb.row(
                make_btn("❌ Reject & Reverse Earnings", callback_data=f"adm_vrej_prompt:{sub_id}:{s_short}:{plat_flt}", style="danger"),
                make_btn("🗑️ Move to Trash (No Reversal)", callback_data=f"adm_trash_move:{sub_id}:{s_short}:{plat_flt}", style="danger")
            )

        else:
            rej_r_disp = v["rejection_reason"] or "অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি"
            txt = (
                f"❌ <b>REJECTED VIDEO — বিস্তারিত ও অর্গানিক/ফেক যাচাই কার্ড</b>\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"👤 User Information: <b>{esc(get_user_label(u_o))}</b> (ID: <code>{esc(v['user_id'])}</code> | UID: <code>{esc(format_display_app_uid(v['app_uid']))}</code>)\n"
                f"🌐 Platform: <b>{esc(plat_title)}</b>\n"
                f"🔗 Video: <a href=\"{esc(v_link)}\">🎬 ভিডিও লিংক ওপেন করুন</a>\n"
                f"👁️ Observed Views: <b>{v['current_views']}</b>\n"
                f"💸 Reversed Earnings: <b>{rev_amt:.2f} টাকা</b>\n"
                f"🚫 স্ট্যাটাস নোট: <b>অর্গানিক ভিউ না / অর্গানিক ভিউ যাচাই হয়নি</b>\n"
                f"📋 Rejection Reason: <b>{esc(rej_r_disp)}</b>\n"
                f"📅 Rejection Date: <b>{esc(v['rejection_date'] or v['submitted_at'])}</b>\n"
                f"{traffic_block}\n"
                f"{FULL_WIDTH_DIVIDER}\n"
                f"ℹ️ <i>অ্যাডমিন চেক করে যদি দেখেন এটি অর্গানিক ভিউ (বট ভুলবশত রিজেক্ট করেছে), তবে নিচের Re-Accept বাটনে চাপ দিলে কেটে নেওয়া টাকা ইউজারের অ্যাকাউন্টে পুনরায় যুক্ত হয়ে যাবে।</i>"
            )
            kb.row(
                make_btn("🔄 Re-review (লাইভ চেক)", callback_data=f"adm_vrereview:{sub_id}:{plat_flt}", style="primary"),
                make_btn("✅ Re-Accept (অর্গানিক অনুমোদন ও ব্যালেন্স ফেরত)", callback_data=video_decision_callback("reaccept", sub_id, sec, plat_flt), style="success")
            )
            kb.row(
                make_btn("🔒 Permanent Approve", callback_data=f"adm_perm_approve:{sub_id}:{s_short}:{plat_flt}", style="success"),
                make_btn("🗑️ Move to Trash", callback_data=f"adm_trash_move:{sub_id}:{s_short}:{plat_flt}", style="danger")
            )
            kb.row(
                make_btn("✏️ Update Reject Reason", callback_data=f"adm_vrej_prompt:{sub_id}:{s_short}:{plat_flt}", style="danger")
            )

        kb.row(make_btn("👤 ইউজারের প্রোফাইলে যান", callback_data=f"adm_uview:{v['user_id']}:vs:{s_short}:{sub_id}:{plat_flt}", style="primary"))
        kb.row(make_btn(f"🔙 {sec.upper()} তালিকায় ফিরে যান", callback_data=f"adm_vsec:{s_short}:{plat_flt}:0", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_perm_trash_all_confirm":
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("🗑️ হ্যাঁ, সব Permanent Approved ভিডিও Trash-এ পাঠান", callback_data="adm_perm_trash_all_exec", style="danger"),
            make_btn("🔙 না, ফিরে যান", callback_data="adm_vsec:pa:all:0", style="success")
        )
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"⚠️ <b>আপনি কি নিশ্চিতভাবে সকল Permanent Approved ভিডিও একসাথে Trash-এ স্থানান্তর করতে চান?</b>\n{FULL_WIDTH_DIVIDER}\n"
            "(এতে কোনো ইউজারের ব্যালেন্স কাটা যাবে না বা Financial Reversal হবে না এবং ভিডিও লিংক স্থায়ীভাবে লক থাকবে।)",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_perm_trash_all_exec":
        with db_lock:
            res_mv = move_all_permanent_approved_to_trash(actor_id=admin_uid)
        admin_perm_selected_videos.pop(admin_uid, None)
        bot.answer_callback_query(call.id, f"🗑️ মোট {res_mv.get('moved_count', 0)}টি Permanent Approved ভিডিও Trash-এ পাঠানো হয়েছে!", show_alert=True)
        call.data = "adm_trash:0"
        handle_admin_trash_system(call)
        return

    if call.data.startswith("adm_perm_approve:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        plat_flt = parts[3] if len(parts) > 3 else "all"
        earn_days = int(get_setting("earning_duration_days", get_setting("view_tracking_days", "5")))

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            if not v:
                conn.close()
                return
            try:
                with conn:
                    res_info = admin_permanent_approve_video(conn, sub_id=sub_id, admin_id=admin_uid, earning_duration_days=earn_days)
            except Exception as exc:
                conn.close()
                bot.answer_callback_query(call.id, f"⚠️ {str(exc)[:140]}", show_alert=True)
                return
            conn.close()

        _unlock_referral_on_first_video_approval(v["user_id"])
        try:
            safe_send(
                int(v["user_id"]),
                get_msg("video_admin_approved_user_msg", title=esc(v["title"][:35]), earning_end=esc(res_info.get("earning_end_date", "")))
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id, "🔒 ভিডিওটি PERMANENT APPROVE করা হয়েছে!", show_alert=True)
        call.data = f"adm_vsec_item:pa:{sub_id}:{plat_flt}"
        handle_admin_video_approval_sections(call)
        return

    if call.data.startswith("adm_trash_move:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        with db_lock:
            tr_info = move_video_to_trash(sub_id, actor_id=admin_uid)
        warn_txt = "⚠️ সতর্কবার্তা: এটি একটি চলমান ভিডিও ছিল! " if tr_info.get("active_warning") else ""
        bot.answer_callback_query(
            call.id,
            f"{warn_txt}কোনো Financial Reversal ছাড়াই ভিডিওটি Trash-এ স্থানান্তরিত হয়েছে ({tr_info.get('preserved_credit', 0):.2f}৳ অক্ষুণ্ণ)।",
            show_alert=True
        )
        call.data = f"adm_trash_item:{sub_id}:0"
        handle_admin_trash_system(call)
        return

    if call.data.startswith("adm_vrereview:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v:
            return
        bot.answer_callback_query(call.id, "🔍 ভিডিওটির বর্তমান ভিউ ও কোড পুনরায় পরীক্ষা করা হচ্ছে...")
        vchk = verify_video_code_only(v["platform"], v["url"], v["unique_code"], v["app_uid"], v["global_code"], verification_link=get_setting("verification_link", ""))
        if not vchk.get("network_ok"):
            code_st = "⚠️ যাচাই করা সম্ভব হয়নি (নেটওয়ার্ক ত্রুটি / Unreachable)"
        elif vchk.get("codes_found"):
            code_st = "✅ সব কোড ও হ্যাশট্যাগ পাওয়া গেছে"
        else:
            code_st = f"❌ মিসিং: {', '.join(vchk.get('missing', []))}"
        safe_send(
            call.message.chat.id,
            f"🔄 <b>Re-Review ফলাফল</b> (Video <code>{esc(sub_id)}</code>):\n{FULL_WIDTH_DIVIDER}\n"
            f"• নেটওয়ার্ক স্ট্যাটাস: <b>{'OK' if vchk.get('network_ok') else 'Unreachable'}</b>\n"
            f"• কোড ও হ্যাশট্যাগ চেক: <b>{esc(code_st)}</b>\n"
            f"• পূর্বে কেটে নেওয়া আয় (Reversed): <b>{float(v['reversed_amount'] or 0):.2f} টাকা</b>"
        )
        return

    if call.data.startswith("adm_vrej_prompt:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        sec = _expand_section_code(parts[2]) if len(parts) > 2 else "bot_approve"
        s_short = _short_section_code(sec)
        plat_flt = parts[3] if len(parts) > 3 else "all"

        user_memory_states[admin_uid] = {
            "admin_action": "custom_reject_video_reason",
            "sub_id": sub_id,
            "sec": sec,
            "plat_flt": plat_flt
        }
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("⚡ Quick Reject (অর্গানিক ভিউ না — ফেক ভিউ)", callback_data=f"adm_vrej_exec:{sub_id}:{s_short}:{plat_flt}:NonOrganicViews", style="danger"))
        kb.row(make_btn("✖️ বাতিল করুন", callback_data=f"adm_vrej_cancel:{sub_id}:{s_short}:{plat_flt}", style="primary"))
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"❌ <b>ভিডিও রিজেক্টের কারণ লিখুন</b> (<code>{esc(sub_id)}</code>)\n{FULL_WIDTH_DIVIDER}\n"
            "কারণ লিখে পাঠান। কারণ না লিখে এগোতে <code>SKIP</code> লিখুন; বাতিল করতে <code>CANCEL</code> লিখুন বা নিচের Cancel বাটন চাপুন।",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_vrej_cancel:"):
        _, sub_id, s_short, plat_flt = call.data.split(":", 3)
        user_memory_states.pop(admin_uid, None)
        bot.answer_callback_query(call.id, "Reject বাতিল করা হয়েছে।")
        call.data = f"adm_vsec_item:{s_short}:{sub_id}:{plat_flt}"
        handle_admin_video_approval_sections(call)
        return

    if call.data.startswith("adm_vrej_exec:"):
        parts = call.data.split(":", 4)
        sub_id = parts[1]
        plat_flt = parts[3] if len(parts) > 3 else "all"
        raw_r = parts[4] if len(parts) > 4 else "Admin Rejected"
        reason_str = "অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি (সম্ভাব্য ফেক ভিউ)" if raw_r == "NonOrganicViews" else raw_r
        user_memory_states.pop(admin_uid, None)

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            if not v:
                conn.close()
                return
            with conn:
                rej_info = admin_reject_video_with_reversal(
                    conn, sub_id=sub_id, rejection_reason=reason_str, admin_id=admin_uid, force_admin_clawback=True
                )
            conn.close()

        if rej_info.get("permanent_protected"):
            bot.answer_callback_query(
                call.id,
                "🔒 এই ভিডিওটি PERMANENT APPROVED স্টেজে লক রয়েছে! এর ব্যালেন্স অক্ষত থাকবে এবং কোনো টাকা কাটা যাবে না।",
                show_alert=True
            )
            call.data = f"adm_vsec_item:pa:{sub_id}:{plat_flt}"
            handle_admin_video_approval_sections(call)
            return

        rev_amt = float(rej_info.get("reversed_amount", 0.0))
        fin_note = _build_rejection_financial_summary_note(rej_info, v["user_id"])
        try:
            safe_send(
                int(v["user_id"]),
                get_msg("video_rejected_msg", title=esc(v["title"][:35]), reason=esc(reason_str), reversed=f"{rev_amt:.2f}") + fin_note
            )
        except Exception:
            pass

        bot.answer_callback_query(call.id, f"ভিডিওটি Reject ও {rev_amt:.2f}৳ Reversal করা হয়েছে!", show_alert=True)
        call.data = f"adm_vsec_item:rj:{sub_id}:{plat_flt}"
        handle_admin_video_approval_sections(call)
        return


# ==============================================================================
# ADMIN TRASH / RECYCLE BIN MANAGEMENT
# ==============================================================================
@bot.callback_query_handler(func=lambda c: (
    c.data.startswith("adm_trash:") or
    c.data.startswith("adm_trash_item:") or
    c.data.startswith("adm_trash_restore:") or
    c.data.startswith("adm_trash_del:") or
    c.data in ("adm_trash_empty_confirm", "adm_trash_empty_exec")
))
@_guard("admin_trash")
def handle_admin_trash_system(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)

    if call.data.startswith("adm_trash:"):
        page = int(call.data.split(":", 1)[1] or 0)
        per_p = 8
        with db_lock:
            conn = get_connection()
            rows = conn.execute("SELECT * FROM videos WHERE COALESCE(is_trashed, 0) = 1 ORDER BY rowid DESC").fetchall()
            conn.close()

        p_meta = paginate_items(rows, page=page, per_page=per_p)
        kb = types.InlineKeyboardMarkup()
        for v in p_meta["items"]:
            u_o = get_user(v["user_id"])
            cred = float(v["credited_amount"] or v["reward"] or 0.0)
            kb.row(
                make_btn(
                    f"🗑️ {get_user_label(u_o)} [{v['platform'].upper()}] — {v['current_views']} ভিউ ({cred:.1f}৳)",
                    callback_data=f"adm_trash_item:{v['sub_id']}:{p_meta['page']}",
                    style="primary"
                )
            )
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_trash")
        if nav_row:
            kb.row(*nav_row)
        if p_meta["total_items"] > 0:
            kb.row(make_btn(f"🔥 সব ট্র্যাশ খালি করুন ({p_meta['total_items']}টি Bulk Delete)", callback_data="adm_trash_empty_confirm", style="danger"))
        kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))

        txt = get_msg("admin_trash_report_msg", total_items=p_meta["total_items"]) + f"\n📄 পৃষ্ঠা: <b>{p_meta['page']+1}/{p_meta['total_pages']}</b>"
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_trash_item:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v:
            bot.answer_callback_query(call.id, "ভিডিওটি পাওয়া যায়নি!", show_alert=True)
            return
        u_o = get_user(v["user_id"]) or {}
        cred = float(v["credited_amount"] or v["reward"] or 0.0)
        was_active = v["trash_previous_admin_status"] == "approved" or v["trash_previous_bot_status"] in ("approved", "waiting_views")
        warn_banner = "⚠️ <b>চলমান ভিডিও সতর্কবার্তা:</b> ট্র্যাশে পাঠানোর পূর্বে এই ভিডিওটি সক্রিয় ছিল।\n" if was_active else ""
        txt = (
            f"🗑️ <b>TRASH / রিসাইকেল বিন — ভিডিও বিস্তারিত</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"{warn_banner}"
            f"🆔 Video ID: <code>{esc(v['sub_id'])}</code>\n"
            f"👤 ইউজার: <b>{esc(get_user_label(u_o))}</b> (ID: <code>{esc(v['user_id'])}</code>)\n"
            f"🌐 প্ল্যাটফর্ম: <b>{esc(v['platform'].upper())}</b>\n"
            f"👁️ ভিউ: <b>{v['current_views']}</b> (Paid Views: <b>{v['paid_views']}</b>)\n"
            f"💰 অক্ষুণ্ণ ক্রেডিট (No Reversal): <b>{cred:.2f} টাকা</b>\n"
            f"📅 ট্র্যাশে পাঠানোর সময়: <b>{esc(v['trashed_at'] or 'N/A')}</b>\n"
            f"📋 পূর্ববর্তী স্ট্যাটাস: <b>{esc(v['trash_previous_status'] or v['status'])}</b>"
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔗 Open Link (ভিডিও দেখুন)", url=v["video_url"] or v["url"], style="primary"))
        kb.row(
            make_btn("♻️ Restore করুন", callback_data=f"adm_trash_restore:{sub_id}:{page}", style="success"),
            make_btn("🔥 স্থায়ীভাবে Delete করুন", callback_data=f"adm_trash_del:{sub_id}:{page}", style="danger")
        )
        kb.row(make_btn("🔙 ট্র্যাশ তালিকায় ফিরে যান", callback_data=f"adm_trash:{page}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_trash_restore:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        with db_lock:
            res = restore_video_from_trash(sub_id, actor_id=admin_uid)
        bot.answer_callback_query(call.id, f"♻️ ভিডিওটি সফলভাবে Restore হয়েছে (ক্রেডিট {res['credited_amount']:.2f}৳ অক্ষুণ্ণ)!", show_alert=True)
        sec_target = "rj" if res["admin_status"] == "rejected" else ("aa" if res["admin_status"] == "approved" else "ba")
        call.data = f"adm_vsec_item:{sec_target}:{sub_id}:all"
        handle_admin_video_approval_sections(call)
        return

    if call.data == "adm_trash_empty_confirm":
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("🔥 হ্যাঁ, সব স্থায়ীভাবে মুছুন", callback_data="adm_trash_empty_exec", style="danger"),
            make_btn("🔙 না, ফিরে যান", callback_data="adm_trash:0", style="success")
        )
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"⚠️ <b>আপনি কি নিশ্চিতভাবে Trash-এ থাকা সকল ভিডিও একসাথে স্থায়ীভাবে Delete (Bulk Clear) করতে চান?</b>\n{FULL_WIDTH_DIVIDER}\n(এতে কোনো Financial Reversal হবে না এবং লেজার ও ডুপ্লিকেট লক অক্ষুণ্ণ থাকবে।)",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_trash_empty_exec":
        with db_lock:
            res_bulk = empty_all_trashed_videos(actor_id=admin_uid)
        bot.answer_callback_query(call.id, f"🔥 মোট {res_bulk['deleted_count']}টি ট্র্যাশ ভিডিও স্থায়ীভাবে মুছে ফেলা হয়েছে!", show_alert=True)
        call.data = "adm_trash:0"
        handle_admin_trash_system(call)
        return

    if call.data.startswith("adm_trash_del:"):
        parts = call.data.split(":")
        sub_id = parts[1]
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        with db_lock:
            permanently_delete_trashed_video(sub_id, actor_id=admin_uid)
        bot.answer_callback_query(call.id, "🔥 ভিডিওটি স্থায়ীভাবে Delete করা হয়েছে!", show_alert=True)
        call.data = f"adm_trash:{page}"
        handle_admin_trash_system(call)
        return


# ==============================================================================
# PROFESSIONAL FINANCIAL LEDGER & AUDIT HISTORY (adm_fin_history & adm_audit_history)
# ==============================================================================
def _translate_tx_type_bn(tx_type: str) -> str:
    t = str(tx_type or "").strip()
    mapping = {
        "Video Milestone": "🎬 ভিডিও ভিউ মাইলস্টোন পেমেন্ট (Video Milestone)",
        "Bot Approval Credit": "🤖 বট অ্যাপ্রুভাল ভিউ ক্রেডিট (Bot Approval Credit)",
        "Video Clawback": "❌ রিজেক্টেড ভিডিও ক্রেডিট কর্তন (Video Reversal)",
        "Video Reversal": "❌ ভিডিও রিভার্সাল কর্তন (Video Reversal)",
        "External Link Clawback": "🌐 এক্সটার্নাল লিংক ভিউ কর্তন (External Link Reversal)",
        "External Link Reset": "🔄 এক্সটার্নাল লিংক আয় রিসেট (External Link Reset)",
        "Video Reversal Restore": "♻️ রি-অ্যাকসেপ্ট ভিডিও ক্রেডিট পুনরুদ্ধার (Re-Accept Restore)",
        "Earnings Restoration": "♻️ আয় পুনরুদ্ধার (Earnings Restore)",
        "Withdraw Reserve": "⏳ উইথড্র রিকোয়েস্ট হোল্ড (Withdraw Hold Reserve)",
        "Withdraw Paid": "✅ উইথড্র পেমেন্ট সম্পন্ন (Withdraw Paid)",
        "Withdraw Cancelled": "🔄 বাতিলকৃত উইথড্র ব্যালেন্স রিফান্ড (Withdraw Refund)",
        "Withdraw Refund": "🔄 উইথড্র রিফান্ড (Withdraw Refund)",
        "Withdraw Partial Refund": "🔄 আংশিক উইথড্র সমন্বয় (Partial Withdraw Adjust)",
        "Referral Bonus": "🎁 সফল রেফারেল বোনাস (Referral Bonus)",
        "Redeem Bonus": "🎟️ রেফার কোড রিডিম ওয়েলকাম বোনাস (Redeem Bonus)",
        "Admin Credit": "➕ অ্যাডমিন কর্তৃক ব্যালেন্স যোগ (Admin Credit)",
        "Admin Debit": "➖ অ্যাডমিন কর্তৃক ব্যালেন্স কর্তন (Admin Debit)",
        "Account Deletion Forfeiture": "🗑️ অ্যাকাউন্ট ডিলিট ব্যালেন্স সমন্বয় (Account Deletion)"
    }
    return mapping.get(t, f"💳 {t}")


def _translate_audit_action_bn(action: str) -> str:
    a = str(action or "").strip()
    mapping = {
        "Session Login": "🔐 পাসওয়ার্ড দিয়ে ড্যাশবোর্ড লগইন (User Login)",
        "Admin Panel Unlock": "👑 সুপার অ্যাডমিন প্যানেল আনলক (Admin Unlock)",
        "Password Changed": "🔑 ইউজার পাসওয়ার্ড পরিবর্তন (Password Update)",
        "Admin Change Password": "🔑 অ্যাডমিন কর্তৃক পাসওয়ার্ড রিসেট (Admin Password Reset)",
        "Account Unfrozen": "🟢 বায়ো/ভিডিও কোড যাচাই ও আনফ্রিজ (Account Unfrozen)",
        "Bio Code Removed": "❄️ বায়ো কোড সরানোর কারণে ফ্রিজ (Bio Code Missing Freeze)",
        "Video Code Removed": "🚨 ভিডিও কোড সরানোর কারণে ফ্রিজ (Video Code Missing Freeze)",
        "Video Deleted Penalty (Account Frozen)": "❄️ সোশ্যাল প্ল্যাটফর্ম থেকে ভিডিও ডিলিট পেনাল্টি (Video Deleted Freeze)",
        "Manual Verification Code Generated": "🔑 ম্যানুয়াল ভেরিফিকেশন / নাম্বার চেঞ্জ র‍্যান্ডম কোড তৈরি (Random Code Issued)",
        "Manual Verification Requested via Random Code": "📩 র‍্যান্ডম কোড দিয়ে ম্যানুয়াল ভেরিফিকেশন আবেদন (Manual Verify Request)",
        "Manual Platform Verification Approved": "✅ অ্যাডমিন কর্তৃক ম্যানুয়াল ভেরিফিকেশন অনুমোদন (Manual Verify Approved)",
        "Manual Platform Verification Rejected": "❌ অ্যাডমিন কর্তৃক ম্যানুয়াল ভেরিফিকেশন বাতিল (Manual Verify Rejected)",
        "Profile Edit Unlocked via Admin Random Code": "🔓 র‍্যান্ডম কোড দিয়ে পেমেন্ট নাম্বার/চ্যানেল এডিট আনলক (Profile Edit Unlocked)",
        "Admin Approve Video (Zero Extra Credit)": "👑 অ্যাডমিন ভিডিও অনুমোদন — অতিরিক্ত ক্রেডিট ছাড়া (Admin Approve)",
        "Permanent Approve Video": "🔒 স্থায়ী ভিডিও অনুমোদন (Permanent Approve)",
        "Admin Reject Video & Reversal": "❌ ভিডিও রিজেক্ট ও ক্রেডিট রিভার্সাল (Video Reject & Reversal)",
        "Admin Re-Accept Rejected Video": "♻️ রিজেক্টেড ভিডিও পুনরায় অনুমোদন ও টাকা ফেরত (Video Re-Accept)",
        "Video Moved to Trash (No Reversal)": "🗑️ ভিডিও ট্র্যাশে স্থানান্তর — ব্যালেন্স অক্ষুণ্ণ (Moved to Trash)",
        "Video Restored from Trash": "♻️ ট্র্যাশ থেকে ভিডিও পুনরুদ্ধার (Restored from Trash)",
        "Video Permanently Deleted from Trash (Lock Preserved)": "🔥 ট্র্যাশ থেকে স্থায়ী ডিলিট — ডুপ্লিকেট লক অক্ষুণ্ণ (Trash Deleted)",
        "Bulk Empty Trash (Locks Preserved)": "🔥 সম্পূর্ণ ট্র্যাশ খালি করা হয়েছে (Bulk Trash Cleared)",
        "User Account Self-Deleted (Tombstone)": "🔴 ইউজার নিজে অ্যাকাউন্ট ডিলিট করেছেন (User Self-Deleted)",
        "Admin Permanent Remove User": "🗑️ অ্যাডমিন কর্তৃক ইউজার সম্পূর্ণ মুছে ফেলা হয়েছে (Admin Removed User)"
    }
    return mapping.get(a, f"🛡️ {a}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_fin_history:") or c.data.startswith("adm_audit_history:"))
@_guard("admin_fin_history")
def handle_admin_financial_history(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    uid = str(call.from_user.id)
    is_audit_tab = call.data.startswith("adm_audit_history:")
    page = int(call.data.split(":", 1)[1] or 0)
    per_p = 8

    if is_audit_tab:
        with db_lock:
            conn = get_connection()
            all_rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC").fetchall()
            conn.close()
        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        lines = [
            f"🛡️ <b>SYSTEM &amp; SECURITY AUDIT HISTORY (পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']} — মোট {p_meta['total_items']}টি রেকর্ড)</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "প্রতিটি অডিট লগে কে, কখন, কোন ইউজারের উপর কী অ্যাকশন নিয়েছেন তার পূর্ণাঙ্গ বিবরণ নিচে দেওয়া হলো:"
        ]
        for r in p_meta["items"]:
            target_id = str(r["target_user_id"] or r["actor_id"] or "")
            u_t = get_user(target_id) if target_id else None
            u_disp = f"{get_user_label(u_t)} (<code>{esc(target_id)}</code>)" if u_t else f"<code>{esc(target_id or 'SYSTEM')}</code>"
            act_bn = _translate_audit_action_bn(r["action"])
            d_s, t_s = _split_datetime_str(r["created_at"])
            lines.append(
                f"🔹 <b>{esc(act_bn)}</b>\n"
                f"  ├ সংশ্লিষ্ট ইউজার: {u_disp}\n"
                f"  ├ সম্পাদনকারী (Actor): <code>{esc(r['actor_id'])}</code>\n"
                f"  ├ বিস্তারিত বিবরণ: <i>{esc(r['details'])}</i>\n"
                f"  └ 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>"
            )
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("💳 ফিন্যান্সিয়াল লেজার হিস্ট্রি", callback_data="adm_fin_history:0", style="primary"),
            make_btn("✅ 🛡️ অডিট লগ হিস্ট্রি", callback_data="adm_audit_history:0", style="success")
        )
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_audit_history")
        if nav_row:
            kb.row(*nav_row)
        kb.row(
            make_btn("📂 ডাটাবেজ ও CSV এক্সপোর্ট হাবে যান", callback_data="adm_db_export_hub", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(call.message.chat.id, call.message.message_id, f"\n{FULL_WIDTH_DIVIDER}\n".join(lines), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    with db_lock:
        conn = get_connection()
        all_rows = conn.execute("SELECT * FROM ledger_transactions ORDER BY rowid DESC").fetchall()
        conn.close()

    p_meta = paginate_items(all_rows, page=page, per_page=per_p)
    lines = [get_msg("admin_financial_report_msg", total_tx=p_meta["total_items"]) + f"\n📄 পৃষ্ঠা: <b>{p_meta['page']+1}/{p_meta['total_pages']}</b>"]
    for r in p_meta["items"]:
        u_t = get_user(r["user_id"])
        u_name_str = f"{get_user_label(u_t)} (ID: <code>{esc(r['user_id'])}</code>)" if u_t else f"<code>{esc(r['user_id'])}</code>"
        tx_title = _translate_tx_type_bn(r["transaction_type"] or r["type"])
        vid_tag = f"\n  ├ ভিডিও / রেফারেন্স ID: <code>{esc(r['video_id'] or r['reference_id'])}</code>" if (r["video_id"] or r["reference_id"]) else ""
        det_str = f"\n  ├ কারণ ও বিবরণ: <i>{esc(r['details'])}</i>" if r["details"] else ""
        amt_v = float(r["amount"] or 0.0)
        amt_fmt = f"+{amt_v:.2f} টাকা" if amt_v >= 0 else f"{amt_v:.2f} টাকা"
        d_s, t_s = _split_datetime_str(r["timestamp"] or r["created_at"])
        lines.append(
            f"💠 <b>{esc(tx_title)}</b>\n"
            f"  ├ ইউজার: {u_name_str}\n"
            f"  ├ লেনদেনের পরিমাণ: <b>{amt_fmt}</b>\n"
            f"  ├ ব্যালেন্স পরিবর্তন: {float(r['previous_balance'] or r['before_balance']):.2f}৳ ➡️ <b>{float(r['new_balance'] or r['after_balance']):.2f}৳</b>"
            f"{vid_tag}{det_str}\n"
            f"  └ TxID: <code>{esc(r['tx_id'])}</code> | 📅 তারিখ: <b>{esc(d_s)}</b> | 🕒 সময়: <b>{esc(t_s)}</b>"
        )

    kb = types.InlineKeyboardMarkup()
    kb.row(
        make_btn("✅ 💳 ফিন্যান্সিয়াল লেজার হিস্ট্রি", callback_data="adm_fin_history:0", style="success"),
        make_btn("🛡️ সিস্টেম ও অডিট লগ হিস্ট্রি", callback_data="adm_audit_history:0", style="primary")
    )
    nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_fin_history")
    if nav_row:
        kb.row(*nav_row)
    append_page_edit_tools(kb, uid, msg_key="admin_financial_report_msg")
    kb.row(
        make_btn("📂 ডাটাবেজ ও CSV এক্সপোর্ট হাবে যান", callback_data="adm_db_export_hub", style="primary"),
        make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
    )
    safe_edit(call.message.chat.id, call.message.message_id, f"\n{FULL_WIDTH_DIVIDER}\n".join(lines), reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_ulist:") or c.data == "adm_usearch")
@_guard("admin_user_list")
def handle_admin_user_list(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    uid = str(call.from_user.id)
    if call.data == "adm_usearch":
        user_memory_states[uid] = {"admin_action": "search_user"}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_ulist:0", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🔍 <b>ইউজার সার্চ:</b>\n{FULL_WIDTH_DIVIDER}\nইউজারের নাম, ইউজারনেম, মোবাইল নাম্বার বা UID লিখে পাঠান:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    page = int(call.data.split(":", 1)[1])
    per_p = 10
    with db_lock:
        conn = get_connection()
        all_rows = conn.execute("SELECT * FROM users ORDER BY rowid DESC").fetchall()
        conn.close()

    p_meta = paginate_items(all_rows, page=page, per_page=per_p)
    kb = types.InlineKeyboardMarkup()
    kb.row(make_btn("🔍 ইউজার সার্চ করুন", callback_data="adm_usearch", style="success"))
    for r in p_meta["items"]:
        u_d = dict(r)
        u_st = str(u_d.get("status") or "active").lower()
        is_froz = int(u_d.get("bio_frozen") or 0) == 1 or u_st == "frozen"
        if u_st == "deleted":
            st_icon = "🗑️ [DEL]"
            btn_col = "danger"
        elif u_st == "banned":
            st_icon = "🔴 [BN]"
            btn_col = "danger"
        elif is_froz:
            st_icon = "❄️ [FR]"
            btn_col = "primary"
        elif u_st == "inactive":
            st_icon = "🟡 [AN]"
            btn_col = "success"
        else:
            st_icon = "🔵 [AC]"
            btn_col = "primary"
        kb.row(make_btn(f"{st_icon} {get_user_label(u_d)} — {float(u_d['balance']):.1f}৳", callback_data=f"adm_uview:{u_d['user_id']}", style=btn_col))

    nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_ulist")
    if nav_row:
        kb.row(*nav_row)
    append_page_edit_tools(kb, uid, msg_key="admin_user_history_msg")
    kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger"))
    hdr = get_msg("admin_user_history_msg", total_users=p_meta["total_items"]) + f"\n📄 পৃষ্ঠা: <b>{p_meta['page']+1}/{p_meta['total_pages']}</b>"
    safe_edit(call.message.chat.id, call.message.message_id, hdr, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: (
    c.data.startswith("adm_uview:") or
    c.data.startswith("adm_ustat_menu:") or
    c.data.startswith("adm_uset_st:") or
    c.data.startswith("adm_udel_u:") or
    c.data.startswith("adm_udel_force:") or
    c.data.startswith("adm_udel_wait:") or
    c.data.startswith("adm_uimp:") or
    c.data.startswith("adm_upwd:") or
    c.data.startswith("adm_ubal:") or
    c.data.startswith("adm_uact_log:") or
    c.data.startswith("adm_uedit_info:") or
    c.data.startswith("adm_uref_hist:")
))
@_guard("admin_user_profile")
def handle_admin_user_profile_control(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)

    if call.data.startswith("adm_uref_hist:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid)
        with db_lock:
            conn = get_connection()
            referred_users = conn.execute("SELECT user_id, name, username, registered, joined_at FROM users WHERE ref_by = ? ORDER BY rowid DESC LIMIT 20", (t_uid,)).fetchall()
            conn.close()
        r_lines = [f"• <b>{esc(get_user_label(dict(ru)))}</b> (ID: <code>{ru['user_id']}</code>) — {'✅ Verified' if ru['registered'] else '⏳ Pending'} ({ru['joined_at']})" for ru in referred_users]
        txt = (
            f"🎁 <b>রেফারেল হিস্ট্রি — {esc(get_user_label(t_u))}</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• মোট সফল রেফার: <b>{t_u.get('ref_count', 0)} জন</b>\n"
            f"• রেফার কোড: <code>{esc(t_u.get('referral_code') or t_uid)}</code>\n"
            f"• রেফার করেছেন (Referred By): <code>{esc(t_u.get('ref_by') or 'None')}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            + ("\n".join(r_lines) if r_lines else "📭 কোনো রেফারেল রেকর্ড পাওয়া যায়নি।")
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_uact_log:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid) or {}
        with db_lock:
            conn = get_connection()
            logs = conn.execute("SELECT * FROM audit_logs WHERE actor_id = ? OR target_user_id = ? ORDER BY id DESC LIMIT 12", (t_uid, t_uid)).fetchall()
            conn.close()
        strike_lim = int(get_setting("strike_limit", "3"))
        freeze_st = "❄️ হ্যাঁ (Frozen)" if int(t_u.get("bio_frozen") or 0) == 1 else "🟢 না (Clear)"
        rep = get_msg(
            "admin_user_activity_report_msg",
            user_label=esc(get_user_label(t_u)),
            user_id=esc(t_uid),
            account_status=esc(str(t_u.get("status", "active")).upper()),
            login_count=t_u.get("login_count", 0),
            videos_submitted=t_u.get("videos_submitted", 0),
            videos_approved=t_u.get("videos_approved", 0),
            videos_rejected=t_u.get("videos_rejected", 0),
            dup_strikes=t_u.get("duplicate_strikes", 0),
            wrong_strikes=t_u.get("wrong_submit_strikes", 0),
            strike_limit=strike_lim,
            freeze_status=freeze_st,
            activity_logs=_format_boxed_activity_logs(logs)
        )
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, admin_uid, msg_key="admin_user_activity_report_msg")
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, rep, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_ubal:"):
        _, mode, t_uid = call.data.split(":")
        t_u = get_user(t_uid)
        user_memory_states[admin_uid] = {"admin_action": "adjust_user_balance", "mode": mode, "target_uid": t_uid}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        act_lbl = "যোগ (Add Balance)" if mode == "add" else "কেটে নেওয়া (Deduct Balance)"
        safe_edit(call.message.chat.id, call.message.message_id, f"💰 <b>ব্যালেন্স {act_lbl} — {esc(get_user_label(t_u))}</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান ব্যালেন্স: <b>{float(t_u.get('balance', 0)):.2f}৳</b>\n\nকত টাকা {act_lbl} করতে চান সংখ্যায় লিখে পাঠান:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_uedit_info:"):
        _, field, t_uid = call.data.split(":")
        t_u = get_user(t_uid)
        user_memory_states[admin_uid] = {"admin_action": "edit_user_field", "field": field, "target_uid": t_uid}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"✏️ <b>ইউজারের {esc(field)} পরিবর্তন ({esc(get_user_label(t_u))}):</b>\n{FULL_WIDTH_DIVIDER}\nনতুন মানটি লিখে পাঠান:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_uimp:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid)
        if not t_u:
            return
        txt, kb = render_user_dashboard_view(admin_uid, target_u=t_u, is_admin_impersonation=True)
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id, "ইউজার ড্যাশবোর্ড লগইন ভিউ ওপেন হয়েছে!")
        return

    if call.data.startswith("adm_upwd:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid)
        user_memory_states[admin_uid] = {"admin_action": "change_user_pwd", "target_uid": t_uid}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"🔑 <b>ইউজার পাসওয়ার্ড পরিবর্তন ({esc(get_user_label(t_u))}):</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"• নিরাপত্তা স্ট্যাটাস: <code>{esc(mask_sensitive_secret(t_u.get('password_hash')))}</code>\n\n"
            f"নতুন পাসওয়ার্ডটি লিখে পাঠান:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_ustat_menu:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔵 Active (AC) করুন — সব চালু", callback_data=f"adm_uset_st:active:{t_uid}", style="primary"))
        kb.row(make_btn("🟡 Inactive (AN) করুন — শুধু উইথড্র বন্ধ", callback_data=f"adm_uset_st:inactive:{t_uid}", style="success"))
        kb.row(make_btn("❄️ Freeze (FR) করুন — উইথড্র ও ভিডিও সাবমিট বন্ধ", callback_data=f"adm_uset_st:frozen:{t_uid}", style="primary"))
        kb.row(make_btn("🔴 Ban (BN) করুন — সম্পূর্ণ নিষিদ্ধ", callback_data=f"adm_uset_st:banned:{t_uid}", style="danger"))
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"⚙️ <b>Account Status পরিবর্তন ({esc(get_user_label(t_u))}):</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান স্ট্যাটাস: <b>{t_u.get('status', 'active').upper()}</b> (Frozen: <b>{'হ্যাঁ' if t_u.get('bio_frozen') else 'না'}</b>)", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_uset_st:"):
        _, new_st, t_uid = call.data.split(":")
        froz_flag = 1 if new_st == "frozen" else 0
        db_st = "inactive" if new_st == "frozen" else new_st
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET status = ?, bio_frozen = ?, duplicate_strikes = 0, wrong_submit_strikes = 0, cooldown_until_ts = 0 WHERE user_id = ?", (db_st, froz_flag, t_uid))
                log_audit_event(admin_uid, f"Set User Status: {new_st.upper()}", f"User {t_uid} status updated to {new_st}", target_user_id=t_uid, conn=conn)
            conn.close()
        bot.answer_callback_query(call.id, f"অ্যাকাউন্ট স্ট্যাটাস {new_st.upper()} করা হয়েছে!")
        call.data = f"adm_uview:{t_uid}"

    if call.data.startswith("adm_udel_wait:"):
        t_uid = call.data.split(":", 1)[1]
        bot.answer_callback_query(call.id, "⏳ অ্যাকাউন্ট ডিলিট বাতিল করা হয়েছে (ঋণ শোধ হওয়া পর্যন্ত অপেক্ষা করা হবে)!", show_alert=True)
        call.data = f"adm_uview:{t_uid}"

    if call.data.startswith("adm_udel_force:"):
        t_uid = call.data.split(":", 1)[1]
        with db_lock:
            delete_user_account_completely(t_uid, actor_id=admin_uid, hard_delete=True)
            log_audit_event(admin_uid, "Admin Permanent Remove User (With Debt)", f"Permanently removed user {t_uid} with debt from database", target_user_id=t_uid)
        user_memory_states.pop(str(t_uid), None)
        bot.answer_callback_query(call.id, "ইউজারের ঋণসহ সকল হিস্ট্রি ও অ্যাকাউন্ট ডাটাবেজ থেকে সম্পূর্ণভাবে মুছে ফেলা হয়েছে!", show_alert=True)
        call.data = "adm_ulist:0"
        handle_admin_user_list(call)
        return

    if call.data.startswith("adm_udel_u:"):
        t_uid = call.data.split(":", 1)[1]
        t_u = get_user(t_uid)
        if t_u:
            debt_v = round(float(t_u.get("debt_balance", 0.0) or 0.0), 2)
            bal_v = round(float(t_u.get("balance", 0.0) or 0.0), 2)
            if debt_v > 0 or bal_v < 0:
                eff_debt = max(debt_v, abs(min(0.0, bal_v)))
                kb = types.InlineKeyboardMarkup()
                kb.row(make_btn("✅ হ্যাঁ, ঋণসহ ডিলিট করুন", callback_data=f"adm_udel_force:{t_uid}", style="danger"))
                kb.row(make_btn("⏳ না, ঋণ শোধ হওয়া পর্যন্ত অপেক্ষা করুন", callback_data=f"adm_udel_wait:{t_uid}", style="success"))
                append_page_edit_tools(kb, admin_uid, msg_key="admin_delete_user_debt_confirm_msg")
                safe_edit(
                    call.message.chat.id,
                    call.message.message_id,
                    get_msg(
                        "admin_delete_user_debt_confirm_msg",
                        user_label=esc(get_user_label(t_u)),
                        user_id=esc(t_uid),
                        debt_balance=f"{eff_debt:.2f}",
                        balance=f"{bal_v:.2f}"
                    ),
                    reply_markup=kb
                )
                bot.answer_callback_query(call.id, f"⚠️ ইউজারের একাউন্টে {eff_debt:.2f}৳ ঋণ রয়েছে! আপনি কি ঋণসহ ডিলিট করতে চান?", show_alert=True)
                return
        with db_lock:
            delete_user_account_completely(t_uid, actor_id=admin_uid, hard_delete=True)
            log_audit_event(admin_uid, "Admin Permanent Remove User", f"Permanently removed user {t_uid} from database", target_user_id=t_uid)
        user_memory_states.pop(str(t_uid), None)
        bot.answer_callback_query(call.id, "ইউজারের সকল হিস্ট্রি ও অ্যাকাউন্ট ডাটাবেজ থেকে সম্পূর্ণভাবে মুছে ফেলা হয়েছে!", show_alert=True)
        call.data = "adm_ulist:0"
        handle_admin_user_list(call)
        return

    uview_parts = call.data.split(":")
    t_uid = uview_parts[1] if len(uview_parts) > 1 else ""
    uview_back_cb = None
    uview_back_lbl = None
    if len(uview_parts) >= 5 and uview_parts[2] == "tr":
        tr_sub = uview_parts[3]
        tr_plat = uview_parts[4]
        tr_pg = uview_parts[5] if len(uview_parts) > 5 else "0"
        uview_back_cb = f"adm_tr_item:{tr_sub}:{tr_plat}:{tr_pg}"
        uview_back_lbl = "🔙 পূর্বের ট্রাফিক সোর্স / ভিডিও কার্ডে ফিরে যান"
    elif len(uview_parts) >= 5 and uview_parts[2] == "vs":
        vs_sec = uview_parts[3]
        vs_sub = uview_parts[4]
        vs_plat = uview_parts[5] if len(uview_parts) > 5 else "all"
        uview_back_cb = f"adm_vsec_item:{vs_sec}:{vs_sub}:{vs_plat}"
        uview_back_lbl = "🔙 পূর্বের ভিডিও যাচাই কার্ডে ফিরে যান"
    u = get_user(t_uid)
    if not u:
        bot.answer_callback_query(call.id, "ইউজার পাওয়া যায়নি!", show_alert=True)
        return

    if str(u.get("status") or "").lower() == "deleted":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔴 সম্পূর্ণভাবে মুছে ফেলুন (Permanent Delete)", callback_data=f"adm_udel_u:{t_uid}", style="danger"))
        kb.row(make_btn("🔙 ইউজার লিস্টে ফিরে যান", callback_data="adm_ulist:0", style="primary"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🗑️🔴 <b>ইউজার অ্যাকাউন্টটি ডিলিট করে দিয়েছেন ({esc(get_user_label(u))})</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• ইউজার ID: <code>{esc(t_uid)}</code>\n"
            f"• স্ট্যাটাস: <b>DELETED BY USER (সকল হিস্ট্রি ও ব্যালেন্স ক্লিয়ার করা হয়েছে)</b>\n\n"
            f"আপনি চাইলে নিচের লাল বাটনটি চাপ দিয়ে এই রেকর্ডটি অ্যাডমিন লিস্ট থেকেও সম্পূর্ণভাবে মুছে দিতে পারেন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    plats = get_user_platforms(t_uid)
    with db_lock:
        conn = get_connection()
        v_rows = conn.execute(
            "SELECT platform, bot_status, admin_status, status, COUNT(*) as c FROM videos WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0 AND LOWER(platform) IN ('youtube', 'tiktok') GROUP BY platform, bot_status, admin_status, status",
            (t_uid,)
        ).fetchall()
        w_rows = conn.execute("SELECT status, COUNT(*) as c, SUM(amount) as s FROM withdrawals WHERE user_id = ? GROUP BY status", (t_uid,)).fetchall()
        conn.close()

    plat_v_counts = {"youtube": 0, "tiktok": 0}
    st_v_counts = {"approved": 0, "rejected": 0, "pending": 0}
    for vr in v_rows:
        pk = vr["platform"].lower()
        if pk in plat_v_counts:
            plat_v_counts[pk] += vr["c"]
        if vr["admin_status"] == "rejected" or vr["status"] == "rejected":
            st_v_counts["rejected"] += vr["c"]
        elif vr["admin_status"] == "approved":
            st_v_counts["approved"] += vr["c"]
        else:
            st_v_counts["pending"] += vr["c"]

    wd_summary = {"pending": (0, 0.0), "paid": (0, 0.0), "cancelled": (0, 0.0)}
    for wr in w_rows:
        st_k = "cancelled" if wr["status"] in ("rejected", "cancelled") else wr["status"]
        prev_c, prev_s = wd_summary.get(st_k, (0, 0.0))
        wd_summary[st_k] = (prev_c + wr["c"], prev_s + float(wr["s"] or 0))

    plat_hist_lines = []
    for p in plats:
        p_t = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
        plat_hist_lines.append(
            f"  ├ {p_t} ({esc(p['display_name'][:18])}): সাবস্ক্রাইবার/ফলোয়ার <b>{p.get('subs_count', 0)}</b> | মোট ভিডিও <b>{p.get('total_videos_count', 0)}টি</b> | যোগ্য ভিডিও <b>{p.get('qualifying_vids_count', 0)}টি ({p.get('qualifying_views_total', 0)} ভিউ)</b>"
        )
    plat_hist_txt = ("\n" + "\n".join(plat_hist_lines)) if plat_hist_lines else ""
    pay_summary = format_user_payment_numbers_summary(u)
    ch_names_summary = format_user_platform_channel_names(u, plats)

    txt = (
        f"👤 <b>ইউজার সম্পূর্ণ হিস্ট্রি ও কন্ট্রোল ({esc(get_user_label(u))})</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        f"• নাম: <b>{esc(u.get('name'))}</b> | চ্যানেল: <b>{esc(ch_names_summary)}</b>\n"
        f"• ইউজার ID: <code>{u['user_id']}</code> | স্ট্যাটাস: <b>{u.get('status', 'active').upper()}</b>\n"
        f"• পেমেন্ট নাম্বারসমূহ: <code>{esc(pay_summary)}</code>\n"
        f"• Battle Club UID: <code>{esc(format_display_app_uid(u.get('app_uid')))}</code>\n"
        f"• পাসওয়ার্ড সুরক্ষা: <code>{esc(mask_sensitive_secret(u.get('password_hash')))}</code>\n"
        f"• বায়ো ভেরিফাই কোড: <code>{esc(u.get('bio_verify_code'))}</code>\n"
        f"• বর্তমান ভিডিও ইউনিকোড: <code>{esc(u.get('active_video_code'))}</code>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        f"💰 বর্তমান ব্যালেন্স: <b>{float(u.get('balance', 0)):.2f}৳</b> | হোল্ড: <b>{float(u.get('held_balance', 0)):.2f}৳</b> | ডেট/ঋণ: <b>{float(u.get('debt_balance', 0)):.2f}৳</b>\n"
        f"🏆 মোট আয়: <b>{float(u.get('total_earned', 0)):.2f}৳</b>\n"
        f"💸 উইথড্র: ⏳ প্রসেসিং {wd_summary['pending'][0]}টি ({wd_summary['pending'][1]:.0f}৳) | ✅ কমপ্লিট {wd_summary['paid'][0]}টি ({wd_summary['paid'][1]:.0f}৳) | ❌ ক্যানসেল {wd_summary['cancelled'][0]}টি\n"
        f"🎬 ভিডিও: 👑 Admin Approved {st_v_counts.get('approved', 0)}টি | 🤖 Bot Approved/Pending {st_v_counts.get('pending', 0)}টি | ❌ Rejected {st_v_counts.get('rejected', 0)}টি\n"
        f"🌐 যুক্ত প্ল্যাটফর্ম সংখ্যা: <b>{len(plats)} টি</b>{plat_hist_txt}"
    )

    kb = types.InlineKeyboardMarkup()
    for p in plats:
        p_t = PLATFORMS.get(p["platform"], {}).get("title", p["platform"].upper())
        kb.row(make_btn(f"🔗 Open Link ({p_t} - {p['display_name'][:16]})", url=p["profile_url"], style="primary"))

    kb.row(
        make_btn(f"📺 YouTube ({plat_v_counts['youtube']})", callback_data=f"adm_uvplat:{t_uid}:youtube:all:0", style="danger"),
        make_btn(f"🎵 TikTok ({plat_v_counts['tiktok']})", callback_data=f"adm_uvplat:{t_uid}:tiktok:all:0", style="primary")
    )
    kb.row(
        make_btn(f"👑 Admin App ({st_v_counts.get('approved', 0)})", callback_data=f"adm_uvplat:{t_uid}:all:approved:0", style="success"),
        make_btn(f"❌ Rejected ({st_v_counts.get('rejected', 0)})", callback_data=f"adm_uvplat:{t_uid}:all:rejected:0", style="danger"),
        make_btn(f"🤖 Bot App ({st_v_counts.get('pending', 0)})", callback_data=f"adm_uvplat:{t_uid}:all:pending:0", style="primary")
    )
    kb.row(
        make_btn("💸 উইথড্র হিস্ট্রি (৪ বাটন)", callback_data=f"adm_uwd_hub:{t_uid}", style="success"),
        make_btn("🎁 রেফারেল হিস্ট্রি", callback_data=f"adm_uref_hist:{t_uid}", style="primary")
    )
    kb.row(
        make_btn("👁️ অ্যাকাউন্ট লগইন ভিউ", callback_data=f"adm_uimp:{t_uid}", style="primary"),
        make_btn("🔑 পাসওয়ার্ড পরিবর্তন", callback_data=f"adm_upwd:{t_uid}", style="success")
    )
    kb.row(
        make_btn("➕ ব্যালেন্স যোগ করুন", callback_data=f"adm_ubal:add:{t_uid}", style="success"),
        make_btn("➖ ব্যালেন্স কেটে নিন", callback_data=f"adm_ubal:deduct:{t_uid}", style="danger")
    )
    kb.row(
        make_btn("📋 সকল কার্যক্রম ও রিপোর্ট", callback_data=f"adm_uact_log:{t_uid}", style="primary"),
        make_btn("✏️ নাম এডিট করুন", callback_data=f"adm_uedit_info:name:{t_uid}", style="success")
    )
    kb.row(
        make_btn("🔑 র‍্যান্ডম কোড জেনারেট (নাম্বার/ভেরিফাই)", callback_data="adm_mvr_gen", style="success"),
        make_btn("⚙️ Account Status", callback_data=f"adm_ustat_menu:{t_uid}", style="primary")
    )
    kb.row(make_btn("🗑️ অ্যাকাউন্ট ডিলিট", callback_data=f"adm_udel_u:{t_uid}", style="danger"))
    append_page_edit_tools(kb, admin_uid, msg_key="dashboard_msg")
    if uview_back_cb and uview_back_lbl:
        kb.row(make_btn(uview_back_lbl, callback_data=uview_back_cb, style="primary"))
    kb.row(make_btn("🔙 ইউজার লিস্টে ফিরে যান", callback_data="adm_ulist:0", style="danger"))
    safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: (
    c.data.startswith("adm_uvplat:") or
    c.data.startswith("adm_vitem:") or
    c.data.startswith("adm_vdecision:") or
    c.data.startswith("vd:") or
    c.data.startswith("adm_all_vids:")
))
@_guard("admin_videos_and_decisions")
def handle_admin_user_and_all_videos(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)

    if call.data.startswith("adm_all_vids:"):
        page = int(call.data.split(":", 1)[1])
        per_p = 10
        with db_lock:
            conn = get_connection()
            all_rows = conn.execute("SELECT * FROM videos WHERE COALESCE(is_trashed, 0) = 0 AND LOWER(platform) IN ('youtube', 'tiktok') ORDER BY rowid DESC").fetchall()
            conn.close()
        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        kb = types.InlineKeyboardMarkup()
        for v in p_meta["items"]:
            u_o = get_user(v["user_id"])
            st_ic = "🔒" if int(v["permanent_approved"] or 0) == 1 else ("👑" if v["admin_status"] == "approved" else ("❌" if v["admin_status"] == "rejected" else "🤖"))
            kb.row(make_btn(f"{st_ic} {get_user_label(u_o)} ({v['platform'].upper()}) — {v['current_views']} views", callback_data=f"adm_vitem:{v['sub_id']}", style="primary"))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_all_vids")
        if nav_row:
            kb.row(*nav_row)
        kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🎬 <b>সকল সাবমিটকৃত ভিডিও ({p_meta['total_items']} টি — পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']}):</b>\n{FULL_WIDTH_DIVIDER}\nভিডিওর উপর ক্লিক করে বিস্তারিত ও অ্যাকশন দেখুন:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_uvplat:"):
        parts = call.data.split(":")
        t_uid, plat_flt, st_flt = parts[1], parts[2], parts[3]
        page = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
        per_p = 8
        u_o = get_user(t_uid)
        query = "SELECT * FROM videos WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0 AND LOWER(platform) IN ('youtube', 'tiktok')"
        params = [t_uid]
        if plat_flt != "all":
            query += " AND LOWER(platform) = ?"
            params.append(plat_flt.lower())
        if st_flt == "approved":
            query += " AND admin_status = 'approved'"
        elif st_flt == "rejected":
            query += " AND (admin_status = 'rejected' OR status = 'rejected')"
        elif st_flt == "pending":
            query += " AND admin_status = 'pending' AND bot_status != 'rejected'"
        query += " ORDER BY rowid DESC"

        with db_lock:
            conn = get_connection()
            all_rows = conn.execute(query, tuple(params)).fetchall()
            conn.close()

        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        kb = types.InlineKeyboardMarkup()
        for idx, v in enumerate(p_meta["items"], start=(p_meta["page"] * per_p) + 1):
            st_ic = "🔒" if int(v["permanent_approved"] or 0) == 1 else ("👑" if v["admin_status"] == "approved" else ("❌" if v["admin_status"] == "rejected" else "🤖"))
            kb.row(make_btn(f"{st_ic} #{idx} {v['platform'].upper()} — {v['current_views']} ভিউ ({float(v['credited_amount'] or v['reward'] or 0):.1f}৳)", callback_data=f"adm_vitem:{v['sub_id']}", style="primary"))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_uvplat:{t_uid}:{plat_flt}:{st_flt}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🎬 <b>{esc(get_user_label(u_o))}-এর ভিডিও তালিকা ({plat_flt.upper()} / {st_flt.upper()} — মোট {p_meta['total_items']}টি):</b>\n{FULL_WIDTH_DIVIDER}\nযেকোনো ভিডিও বাটনে ক্লিক করুন:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_vitem:"):
        sub_id = call.data.split(":", 1)[1]
        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v:
            bot.answer_callback_query(call.id, "ভিডিও পাওয়া যায়নি!", show_alert=True)
            return
        if int(v["is_trashed"] or 0) == 1:
            call.data = f"adm_trash_item:{sub_id}:0"
            handle_admin_trash_system(call)
            return
        sec_target = "rj" if (v["admin_status"] == "rejected" or v["status"] == "rejected") else ("pa" if int(v["permanent_approved"] or 0) == 1 else ("aa" if v["admin_status"] == "approved" else ("ba" if v["bot_status"] == "approved" else "pe")))
        call.data = f"adm_vsec_item:{sec_target}:{sub_id}:all"
        handle_admin_video_approval_sections(call)
        return

    if call.data.startswith("adm_vdecision:") or call.data.startswith("vd:"):
        parts = call.data.split(":")
        dec = parts[1]
        sub_id = parts[2]
        sec = _expand_section_code(parts[3]) if len(parts) > 3 else "bot_approve"
        s_short = _short_section_code(sec)
        plat_flt = parts[4] if len(parts) > 4 else "all"
        earn_days = int(get_setting("earning_duration_days", get_setting("view_tracking_days", "5")))

        with db_lock:
            conn = get_connection()
            v_init = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            conn.close()
        if not v_init:
            return
        if dec == "reject":
            user_memory_states[admin_uid] = {
                "admin_action": "custom_reject_video_reason",
                "sub_id": sub_id,
                "sec": sec,
                "plat_flt": plat_flt
            }
            bot.answer_callback_query(call.id)
            call.data = f"adm_vrej_prompt:{sub_id}:{s_short}:{plat_flt}"
            handle_admin_video_approval_sections(call)
            return

        live_fetched_meta = None
        if dec == "bot_credit":
            try:
                live_fetched_meta = fetch_video_public_metadata(v_init["platform"], v_init["video_url"] or v_init["url"])
            except Exception:
                live_fetched_meta = None

        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            if not v:
                conn.close()
                return
            t_uid = v["user_id"]
            try:
                with conn:
                    if dec == "bot_credit":
                        if int(v["flagged_suspicious"] or 0) == 1:
                            raise ValueError("সন্দেহজনক (Suspicious) ফ্ল্যাগ থাকা ভিডিওতে সরাসরি বট ক্রেডিট দেওয়া যাবে না!")
                        if int(v["code_missing_flag"] or 0) == 1:
                            raise ValueError("ভিডিওতে বাধ্যতামূলক কোড অনুপস্থিত থাকায় বট ক্রেডিট দেওয়া যাবে না!")
                        if "duration_known" in v.keys() and v["duration_known"] is not None and int(v["duration_known"]) == 0:
                            if not (isinstance(live_fetched_meta, dict) and int(live_fetched_meta.get("duration") or 0) >= int(get_setting("min_video_duration_sec", "10"))):
                                raise ValueError("ভিডিওর Duration যাচাইকৃত নয়; বট ক্রেডিট দেওয়া যাবে না!")
                        if "publish_date_known" in v.keys() and v["publish_date_known"] is not None and int(v["publish_date_known"]) == 0:
                            if not (isinstance(live_fetched_meta, dict) and (live_fetched_meta.get("timestamp") or live_fetched_meta.get("upload_date"))):
                                raise ValueError("ভিডিওর Publish Date যাচাইকৃত নয়; বট ক্রেডিট দেওয়া যাবে না!")
                        live_has_views = bool(
                            isinstance(live_fetched_meta, dict)
                            and (live_fetched_meta.get("view_count") is not None or live_fetched_meta.get("play_count") is not None)
                        )
                        if not live_has_views and int(v["view_metrics_known"] or 0) == 0:
                            raise ValueError("লাইভ ভিউ সংগৃহীত হয়নি; নেটওয়ার্ক সচল থাকলে আবার চেষ্টা করুন!")
                        if str(v["verification_mode"] or "").upper() == "SOURCE_CONFLICT" and not live_has_views:
                            raise ValueError("দুই সোর্সের ভিউ কাউন্টে অসামঞ্জস্যতা (SOURCE_CONFLICT) থাকায় লাইভ ভিউ ছাড়া বট ক্রেডিট দেওয়া যাবে না!")
                        actual_v = int(v["current_views"] or 0)
                        min_req_v = get_video_payment_rates(conn, sub_id=sub_id)[2]
                        if live_has_views:
                            raw_lv = live_fetched_meta.get("view_count") if live_fetched_meta.get("view_count") is not None else live_fetched_meta.get("play_count")
                            scraped_lv = max(0, parse_human_number(raw_lv))
                            actual_v = scraped_lv if scraped_lv > 0 else actual_v
                            conn.execute(
                                "UPDATE videos SET previous_views = current_views, current_views = ?, view_metrics_known = 1, verification_mode = CASE WHEN verification_mode = 'SOURCE_CONFLICT' THEN 'SINGLE_SOURCE_VERIFIED' ELSE verification_mode END WHERE sub_id = ?",
                                (actual_v, sub_id)
                            )
                            v_link_c = get_platform_criteria(v["platform"], conn=conn).get("verification_link") or ""
                            tr_upd = analyze_video_traffic_sources(
                                platform_key=v["platform"],
                                video_url=v["video_url"] or v["url"],
                                caption_text=str(live_fetched_meta.get("description") or v["title"] or ""),
                                cur_views=actual_v,
                                cur_likes=parse_human_number(live_fetched_meta.get("like_count") or 0),
                                cur_comments=parse_human_number(live_fetched_meta.get("comment_count") or 0),
                                ytdlp_info=live_fetched_meta,
                                verification_link=v_link_c
                            )
                            save_video_traffic_and_external_links(
                                sub_id=sub_id, user_id=t_uid, platform=v["platform"],
                                traffic_breakdown=tr_upd, external_links=tr_upd.get("external_links", []), conn=conn
                            )
                        ded_ext_v = int(v["deducted_external_views"] or 0)
                        net_v = max(0, actual_v - ded_ext_v)
                        if net_v < min_req_v:
                            raise ValueError(f"ভিডিওটির বর্তমান আসল অর্গানিক ভিউ {net_v}, কিন্তু ন্যূনতম টার্গেট {min_req_v} ভিউ পূর্ণ না হওয়া পর্যন্ত বট ক্রেডিট যোগ হবে না!")
                        snap_cnt_bc = int(conn.execute("SELECT COUNT(*) as c FROM video_view_snapshots WHERE sub_id = ?", (sub_id,)).fetchone()["c"] or 0)
                        log_audit_event(
                            admin_uid,
                            "Admin Manual Bot Credit Override",
                            f"Manual bot_credit override on video {sub_id} (views={actual_v}, net_views={net_v}, snapshots={snap_cnt_bc})",
                            target_user_id=t_uid,
                            conn=conn
                        )
                        conn.execute(
                            "UPDATE videos SET organic_status = CASE WHEN organic_status = 'verified_organic' THEN 'verified_organic' ELSE 'admin_override' END WHERE sub_id = ?",
                            (sub_id,)
                        )
                        credited_now, _ = process_bot_approval_credit(conn, sub_id, t_uid, actual_v)
                        if float(credited_now or 0.0) <= 0 and int(v["initial_reward_paid"] or 0) == 0:
                            raise ValueError("ভিডিওটি বট ক্রেডিটের শর্ত পূরণ করেনি (০ টাকা ক্রেডিট)!")
                        v_chk = conn.execute("SELECT permanent_approved FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
                        target_sec = "pa" if (v_chk and int(v_chk["permanent_approved"] or 0) == 1) else "ba"
                        toast_msg = f"ভিডিওটি Bot Approved করা হয়েছে (আসল ভিউ: {actual_v}, ক্রেডিট: {float(credited_now or 0):.2f}৳)!"
                    elif dec == "approve":
                        res_info = admin_accept_bot_approved_video(conn, sub_id=sub_id, admin_id=admin_uid, earning_duration_days=earn_days)
                        try:
                            safe_send(
                                int(t_uid),
                                get_msg("video_admin_approved_user_msg", title=esc(v["title"][:35]), earning_end=esc(res_info.get("earning_end_date", "")))
                            )
                        except Exception:
                            pass
                        target_sec = "pa" if int(res_info.get("permanent_approved") or 0) == 1 else "aa"
                        toast_msg = "ভিডিওটি ADMIN APPROVE-এ স্থানান্তরিত হয়েছে (দ্বিতীয়বার কোনো অতিরিক্ত টাকা যোগ হয়নি)!"

                    elif dec == "reaccept":
                        res_info = admin_reaccept_rejected_video(conn, sub_id=sub_id, admin_id=admin_uid, earning_duration_days=earn_days)
                        restored_v = float(res_info.get("restored_amount", 0.0))
                        try:
                            safe_send(
                                int(t_uid),
                                get_msg("video_reaccepted_user_msg", title=esc(v["title"][:35]), restored=f"{restored_v:.2f}")
                            )
                        except Exception:
                            pass
                        target_sec = "aa"
                        toast_msg = f"ভিডিওটি পুনরায় Accept ও {restored_v:.2f}৳ Restore করা হয়েছে!"

                    else:
                        target_sec = s_short
                        toast_msg = "আপডেট সম্পন্ন!"
            except Exception as exc:
                conn.close()
                bot.answer_callback_query(call.id, f"⚠️ {str(exc)[:160]}", show_alert=True)
                return
            conn.close()

        _unlock_referral_on_first_video_approval(t_uid)
        bot.answer_callback_query(call.id, toast_msg, show_alert=True)
        call.data = f"adm_vsec_item:{target_sec}:{sub_id}:{plat_flt}"
        handle_admin_video_approval_sections(call)


# ==============================================================================
# ADMIN WITHDRAWAL REPORTS (PENDING, PAID WITH TRXID/SKIP, CANCELLED, REJECTED)
# ==============================================================================
@bot.callback_query_handler(func=lambda c: (
    c.data == "adm_wd_reports_hub" or
    c.data.startswith("adm_uwd_hub:") or
    c.data.startswith("adm_wd_users:") or
    c.data.startswith("adm_wd_ulist_items:") or
    c.data.startswith("adm_wd_detail:") or
    c.data.startswith("adm_wd_act:") or
    c.data.startswith("adm_wd_paid_prompt:")
))
@_guard("admin_withdrawals")
def handle_admin_wd_reports_system(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    admin_uid = str(call.from_user.id)

    if call.data == "adm_wd_reports_hub" or call.data.startswith("adm_uwd_hub:"):
        target_uid = call.data.split(":", 1)[1] if ":" in call.data else "all"
        with db_lock:
            conn = get_connection()
            if target_uid == "all":
                cnt_pend = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE status = 'pending'").fetchone()["c"]
                cnt_paid = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE status = 'paid'").fetchone()["c"]
                cnt_canc = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE status = 'cancelled'").fetchone()["c"]
                cnt_rej = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE status = 'rejected'").fetchone()["c"]
                header = get_msg(
                    "admin_withdrawal_report_msg",
                    pending_count=cnt_pend,
                    paid_count=cnt_paid,
                    cancelled_only_count=cnt_canc,
                    rejected_only_count=cnt_rej,
                    cancelled_count=cnt_canc + cnt_rej,
                    rejected_count=cnt_rej
                )
            else:
                cnt_pend = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE user_id = ? AND status = 'pending'", (target_uid,)).fetchone()["c"]
                cnt_paid = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE user_id = ? AND status = 'paid'", (target_uid,)).fetchone()["c"]
                cnt_canc = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE user_id = ? AND status = 'cancelled'", (target_uid,)).fetchone()["c"]
                cnt_rej = conn.execute("SELECT COUNT(*) as c FROM withdrawals WHERE user_id = ? AND status = 'rejected'", (target_uid,)).fetchone()["c"]
                u_o = get_user(target_uid)
                header = f"📋 <b>{esc(get_user_label(u_o))}-এর উইথড্র হিস্ট্রি:</b>\n{FULL_WIDTH_DIVIDER}"
            conn.close()

        kb = types.InlineKeyboardMarkup()
        comb_rej = int(cnt_rej or 0) + int(cnt_canc or 0)
        if target_uid == "all":
            kb.row(make_btn(f"⏳ Pending Withdrawals ({cnt_pend})", callback_data="adm_wd_users:pending:0", style="primary"))
            kb.row(make_btn(f"✅ Paid Withdrawals ({cnt_paid})", callback_data="adm_wd_users:paid:0", style="success"))
            kb.row(make_btn(f"❌ Rejected Withdrawals ({comb_rej})", callback_data="adm_wd_users:rejected:0", style="danger"))
            append_page_edit_tools(kb, admin_uid, msg_key="admin_withdrawal_report_msg")
            kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
        else:
            kb.row(make_btn(f"⏳ পেন্ডিং উইথড্র ({cnt_pend}টি)", callback_data=f"adm_wd_ulist_items:pending:{target_uid}:0", style="primary"))
            kb.row(make_btn(f"✅ পেইড উইথড্র ({cnt_paid}টি)", callback_data=f"adm_wd_ulist_items:paid:{target_uid}:0", style="success"))
            kb.row(make_btn(f"❌ রিজেক্ট উইথড্র ({comb_rej}টি)", callback_data=f"adm_wd_ulist_items:rejected:{target_uid}:0", style="danger"))
            kb.row(make_btn("🔙 ইউজার প্রোফাইলে ফিরে যান", callback_data=f"adm_uview:{target_uid}", style="danger"))

        safe_edit(call.message.chat.id, call.message.message_id, header, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_users:"):
        parts = call.data.split(":")
        st_key = parts[1]
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        per_p = 10
        with db_lock:
            conn = get_connection()
            all_rows = (conn.execute("SELECT user_id, COUNT(*) as c, SUM(amount) as s FROM withdrawals WHERE status IN ('rejected', 'cancelled') GROUP BY user_id ORDER BY MAX(rowid) DESC").fetchall() if st_key == "rejected" else conn.execute("SELECT user_id, COUNT(*) as c, SUM(amount) as s FROM withdrawals WHERE status = ? GROUP BY user_id ORDER BY MAX(rowid) DESC", (st_key,)).fetchall())
            conn.close()

        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        kb = types.InlineKeyboardMarkup()
        for r in p_meta["items"]:
            u_o = get_user(r["user_id"])
            kb.row(make_btn(f"👤 {get_user_label(u_o)} — {r['c']}টি ({float(r['s'] or 0):.0f}৳)", callback_data=f"adm_wd_ulist_items:{st_key}:{r['user_id']}:0", style="primary"))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_wd_users:{st_key}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(make_btn("🔙 উইথড্র রিপোর্টে ফিরে যান", callback_data="adm_wd_reports_hub", style="danger"))

        t_map = {
            "cancelled": "🚫 উইথড্র ক্যানসেল হওয়া ইউজার তালিকা",
            "rejected": "❌ উইথড্র রিজেক্টেড হওয়া ইউজার তালিকা",
            "pending": "⏳ উইথড্র প্রসেসিং ইউজার তালিকা",
            "paid": "✅ উইথড্র কমপ্লিট হওয়া ইউজার তালিকা"
        }
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{t_map.get(st_key, st_key)} (মোট {p_meta['total_items']} জন ইউজার):</b>\n{FULL_WIDTH_DIVIDER}\nইউজারের নামের উপর ক্লিক করে বিস্তারিত তারিখ ও হিস্ট্রি দেখুন:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_ulist_items:"):
        parts = call.data.split(":")
        st_key, t_uid = parts[1], parts[2]
        page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
        per_p = 8
        u_o = get_user(t_uid)
        with db_lock:
            conn = get_connection()
            all_rows = (conn.execute("SELECT * FROM withdrawals WHERE user_id = ? AND status IN ('rejected', 'cancelled') ORDER BY rowid DESC", (t_uid,)).fetchall() if st_key == "rejected" else conn.execute("SELECT * FROM withdrawals WHERE user_id = ? AND status = ? ORDER BY rowid DESC", (t_uid, st_key)).fetchall())
            conn.close()

        p_meta = paginate_items(all_rows, page=page, per_page=per_p)
        lines = [f"👤 <b>ইউজার: {esc(get_user_label(u_o))} ({st_key.upper()} — মোট {p_meta['total_items']}টি)</b>\n{FULL_WIDTH_DIVIDER}"]
        kb = types.InlineKeyboardMarkup()
        for idx, w in enumerate(p_meta["items"], start=(p_meta["page"] * per_p) + 1):
            note_s = f"\n├ TrxID/Note: <code>{esc(w['trx_id'] or w['decision_reason'])}</code>" if (w["trx_id"] or w["decision_reason"]) else ""
            dest_disp = format_display_app_uid(w["dest"]) if w["method"] == "BattleClub_UID" else w["dest"]
            lines.append(
                f"<b>#{idx}. পরিমাণ: {float(w['amount']):.2f}৳ ({w['method']})</b>\n"
                f"├ নাম্বার/UID: <code>{esc(dest_disp)}</code>{note_s}\n"
                f"├ উইথড্র দেওয়ার তারিখ: <b>{w['created_at']}</b>\n"
                f"└ কমপ্লিট/ক্যানসেল তারিখ: <b>{w['processed_at'] or 'প্রসেসিংয়ে আছে'}</b>"
            )
            kb.row(make_btn(f"🔎 #{idx} বিস্তারিত ও অ্যাকশন ({w['amount']}৳ - {w['method']})", callback_data=f"adm_wd_detail:{w['wd_id']}", style="primary"))

        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_wd_ulist_items:{st_key}:{t_uid}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(make_btn("👤 ইউজারের সম্পূর্ণ হিস্ট্রি প্রোফাইল দেখুন", callback_data=f"adm_uview:{t_uid}", style="success"))
        kb.row(make_btn("🔙 তালিকায় ফিরে যান", callback_data=f"adm_wd_users:{st_key}:0", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, "\n\n".join(lines), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_detail:"):
        wid = call.data.split(":", 1)[1]
        with db_lock:
            conn = get_connection()
            w = conn.execute("SELECT * FROM withdrawals WHERE wd_id = ?", (wid,)).fetchone()
            conn.close()
        if not w:
            return
        u_o = get_user(w["user_id"])
        plats = get_user_platforms(w["user_id"])
        with db_lock:
            conn = get_connection()
            pend_v = conn.execute("SELECT COUNT(*) as c FROM videos WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0 AND admin_status = 'pending' AND bot_status != 'rejected'", (w["user_id"],)).fetchone()["c"]
            paid_sum = conn.execute("SELECT COALESCE(SUM(amount), 0) as s FROM withdrawals WHERE user_id = ? AND status = 'paid'", (w["user_id"],)).fetchone()["s"]
            conn.close()

        plat_str = ", ".join([p["platform"].upper() for p in plats]) or "None"
        trx_str = w["trx_id"] or w["payment_note"] or w["decision_reason"] or "N/A"
        dest_disp = format_display_app_uid(w["dest"]) if w["method"] == "BattleClub_UID" else w["dest"]
        txt = (
            f"💸 <b>উইথড্র রিকোয়েস্ট ও ইউজার সম্পূর্ণ প্রোফাইল হিস্ট্রি</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"👤 একাউন্টের নাম: <b>{esc(u_o.get('name'))}</b> ({esc(get_user_label(u_o))})\n"
            f"💰 উইথড্র পরিমাণ: <b>{float(w['amount']):.2f} টাকা</b> | স্ট্যাটাস: <b>{esc(w['status'].upper())}</b>\n"
            f"💳 কোন নাম্বারে/UID-তে দিয়েছে: <b>{w['method']}</b> — <code>{esc(dest_disp)}</code>\n"
            f"🆔 Battle Club UID: <code>{esc(format_display_app_uid(w['app_uid']))}</code>\n"
            f"🧾 TrxID / Note: <code>{esc(trx_str)}</code>\n"
            f"📅 উইথড্র তারিখ: <b>{w['created_at']}</b>\n"
            f"📅 কমপ্লিট/ক্যানসেল তারিখ: <b>{w['processed_at'] or 'প্রসেসিং'}</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"📊 <b>ইউজারের ভিডিও ও ব্যালেন্স হিস্ট্রি:</b>\n"
            f"├ মোট সাবমিট ভিডিও: <b>{u_o.get('videos_submitted', 0)} টি</b>\n"
            f"├ ✅ এক্সেপ্ট/অ্যাক্টিভ ভিডিও: <b>{u_o.get('videos_approved', 0)} টি</b>\n"
            f"├ ❌ রিজেক্ট হওয়া ভিডিও: <b>{u_o.get('videos_rejected', 0)} টি</b>\n"
            f"├ ⏳ পেন্ডিং ভিডিও: <b>{pend_v} টি</b>\n"
            f"├ বর্তমান ব্যালেন্স: <b>{float(u_o.get('balance', 0)):.2f} টাকা</b> (হোল্ড: <b>{float(u_o.get('held_balance', 0)):.2f}৳</b> | ঋণ: <b>{float(u_o.get('debt_balance', 0)):.2f}৳</b>)\n"
            f"├ এ পর্যন্ত মোট উইথড্র: <b>{float(paid_sum):.2f} টাকা</b>\n"
            f"└ যুক্ত প্ল্যাটফর্ম ({len(plats)}টি): <b>{plat_str}</b>"
        )
        kb = types.InlineKeyboardMarkup()
        if w["status"] == "pending":
            kb.row(
                make_btn("✅ Paid (TrxID / Note দিন)", callback_data=f"adm_wd_paid_prompt:{wid}", style="success"),
                make_btn("⚡ Paid (SKIP Note)", callback_data=f"adm_wd_act:paid:{wid}", style="success")
            )
            kb.row(
                make_btn("❌ Reject করুন (Refund)", callback_data=f"adm_wd_act:reject:{wid}", style="danger")
            )
        kb.row(make_btn("👤 ইউজারের সম্পূর্ণ প্রোফাইল ও ভিডিও দেখুন", callback_data=f"adm_uview:{w['user_id']}", style="primary"))
        kb.row(make_btn("🔙 উইথড্র রিপোর্টে ফিরে যান", callback_data="adm_wd_reports_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_paid_prompt:"):
        wid = call.data.split(":", 1)[1]
        user_memory_states[admin_uid] = {"admin_action": "wd_paid_trx_note", "wd_id": wid}
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("⏭️ SKIP (নোট ছাড়াই Paid করুন)", callback_data=f"adm_wd_act:paid:{wid}", style="success"),
            make_btn("✖️ বাতিল করুন", callback_data=f"adm_wd_detail:{wid}", style="danger")
        )
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"🧾 <b>উইথড্র পেমেন্ট TrxID / Payment Note</b> (<code>{esc(wid)}</code>):\n{FULL_WIDTH_DIVIDER}\n"
            "আপনার পেমেন্টের TrxID বা নোট লিখে পাঠান। নোট না দিতে চাইলে <code>SKIP</code> লিখুন অথবা নিচের SKIP বাটনে ক্লিক করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_act:"):
        _, act, wid = call.data.split(":")
        user_memory_states.pop(admin_uid, None)
        with db_lock:
            conn = get_connection()
            w = conn.execute("SELECT * FROM withdrawals WHERE wd_id = ?", (wid,)).fetchone()
            if not w or w["status"] != "pending":
                conn.close()
                bot.answer_callback_query(call.id, "ইতিমধ্যে প্রসেস করা হয়েছে!", show_alert=True)
                return
            amt = float(w["amount"])
            t_uid = w["user_id"]
            try:
                with conn:
                    if act == "paid":
                        admin_mark_withdrawal_paid(conn, wd_id=wid, admin_id=admin_uid, trx_id="SKIP", payment_note="SKIP")
                    elif act == "cancel":
                        admin_cancel_withdrawal_with_refund(conn, wd_id=wid, admin_id=admin_uid, reason="Admin Cancelled", target_status="cancelled")
                    elif act == "reject":
                        admin_cancel_withdrawal_with_refund(conn, wd_id=wid, admin_id=admin_uid, reason="Admin Rejected", target_status="rejected")
                    else:
                        raise ValueError("অজানা withdrawal action")
            except Exception as exc:
                conn.close()
                bot.answer_callback_query(call.id, f"লেনদেন সম্পন্ন হয়নি: {str(exc)[:120]}", show_alert=True)
                return
            try:
                if act == "paid":
                    safe_send(int(t_uid), get_msg("withdraw_paid_msg", amount=f"{amt:.2f}", method=esc(w["method"]), dest=esc(w["dest"])))
                else:
                    safe_send(int(t_uid), get_msg("withdraw_rejected_msg", amount=f"{amt:.2f}", method=esc(w["method"]), dest=esc(w["dest"])))
            except Exception:
                pass
            conn.close()
        bot.answer_callback_query(call.id, "উইথড্র আপডেট সম্পন্ন!")
        call.data = f"adm_wd_detail:{wid}"
        handle_admin_wd_reports_system(call)


# ==============================================================================
# PART 17 & 19: ADMIN SETTINGS HUB (PLATFORM, GENERAL, DATABASE EXPORT + LEDGER)
# ==============================================================================
def build_command_shortcuts_keyboard(active_cat: str = "all"):
    kb = types.InlineKeyboardMarkup()
    cats = [
        ("👑 Admin", "admin"),
        ("👥 Users", "users"),
        ("✏️ Messages", "messages"),
        ("⚙️ Config", "config"),
        ("💰 Finance", "finance"),
        ("🛡️ Verify", "verification"),
        ("📂 Database", "database"),
        ("🔧 Fix", "troubleshooting")
    ]
    for i in range(0, len(cats), 2):
        row = []
        for lbl, c_key in cats[i:i+2]:
            st = "success" if active_cat == c_key else "primary"
            row.append(make_btn(lbl, callback_data=f"adm_cmd_cat:{c_key}", style=st))
        kb.row(*row)
    kb.row(make_btn("📋 সব ক্যাটাগরি একসাথে দেখুন", callback_data="adm_cmd_cat:all", style="success"))
    kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
    return kb


@bot.callback_query_handler(func=lambda c: (
    c.data in (
        "adm_settings_hub", "adm_plat_settings_hub", "adm_gen_settings_hub",
        "adm_db_export_hub", "adm_man_ver:hub", "adm_mvr_gen",
        "adm_wd_limit_hub", "adm_edit_hashtags", "adm_edit_top_yt",
        "adm_edit_req_link", "adm_set_req_link:all_public", "adm_set_req_link:off", "adm_toggle_expiry_action", "adm_edit_ver_link", "adm_edit_support_link",
        "adm_edit_group_link", "adm_edit_ref_hub", "adm_edit_rate_days",
        "adm_broadcast_prompt", "adm_bc_done", "adm_bc_clear", "adm_export_data", "adm_guide_map", "adm_cmd_shortcuts"
    ) or
    c.data.startswith("adm_mvr_act:") or
    c.data.startswith("adm_shub:") or
    c.data.startswith("adm_toggle:") or
    c.data.startswith("adm_set_theme:") or
    c.data.startswith("adm_apply_theme:") or
    c.data.startswith("adm_wd_lset:") or
    c.data.startswith("adm_crit:") or
    c.data.startswith("adm_cmd_cat:") or
    c.data.startswith("adm_rset:")
))
@_guard("admin_settings_hub")
def handle_admin_settings_and_limits(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    uid = str(call.from_user.id)

    if call.data == "adm_settings_hub":
        kb = types.InlineKeyboardMarkup()
        for idx, (lbl, cb_str, st_col) in enumerate(SETTINGS_CONTROL_HUB_SUBMENUS, start=1):
            kb.row(make_btn(f"{idx}. {lbl}", callback_data=cb_str, style=st_col))
        append_page_edit_tools(kb, uid, msg_key="admin_settings_msg", layout_key="admin_settings_hub")
        kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))

        f_1k = get_setting("first_1000_views_payment", get_setting("rate_per_1k", "15.0"))
        ev_200 = get_setting("every_200_views_payment", "3.0")
        e_days = get_setting("earning_duration_days", get_setting("view_tracking_days", "5"))
        max_v = get_setting("max_payable_views", "5000000")
        txt = get_msg(
            "admin_settings_msg",
            global_code=esc(get_setting("global_required_code")),
            verification_link=esc(get_setting("verification_link") or "none"),
            first_1k=f_1k,
            every_200=ev_200,
            max_views=max_v,
            earning_days=e_days,
            min_withdraw=get_setting("min_withdraw", "100.0"),
            max_daily_wd_count=get_setting("max_daily_wd_count", "2"),
            max_daily_wd_amount=get_setting("max_daily_wd_amount", "5000.0"),
            ref_bonus=get_setting("ref_bonus", "10.0"),
            redeem_bonus=get_setting("redeem_bonus", "5.0")
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_plat_settings_hub":
        # Part 17, Items 143–144: Separate Platform Settings Menu (including Traffic Source settings inside)
        kb = types.InlineKeyboardMarkup()
        for idx, (lbl, cb_str, st_col) in enumerate(PLATFORM_SETTINGS_SUBMENUS, start=1):
            kb.row(make_btn(f"{idx}. {lbl}", callback_data=cb_str, style=st_col))
        append_page_edit_tools(kb, uid, msg_key="admin_platform_settings_msg", layout_key="admin_platform_settings")
        kb.row(
            make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে যান", callback_data="adm_settings_hub", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("admin_platform_settings_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_gen_settings_hub":
        # Part 17, Items 143 & 145: Separate General Settings Menu (housing Database CSV Export & Financial Ledger)
        kb = types.InlineKeyboardMarkup()
        for idx, (lbl, cb_str, st_col) in enumerate(GENERAL_SETTINGS_SUBMENUS, start=1):
            kb.row(make_btn(f"{idx}. {lbl}", callback_data=cb_str, style=st_col))
        append_page_edit_tools(kb, uid, msg_key="admin_general_settings_msg", layout_key="admin_general_settings")
        kb.row(
            make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে যান", callback_data="adm_settings_hub", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("admin_general_settings_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_db_export_hub":
        # Part 17, Item 145: Database CSV Export section houses Financial Ledger & Audit History
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("📊 Users Database CSV ডাউনলোড করুন", callback_data="adm_export_data", style="success"))
        kb.row(
            make_btn("📜 ফিন্যান্সিয়াল লেজার হিস্ট্রি", callback_data="adm_fin_history:0", style="primary"),
            make_btn("🛡️ সিস্টেম ও অডিট লগ হিস্ট্রি", callback_data="adm_audit_history:0", style="primary")
        )
        append_page_edit_tools(kb, uid, msg_key="admin_db_export_hub_msg")
        kb.row(
            make_btn("🔙 জেনারেল সেটিংসে ফিরে যান", callback_data="adm_gen_settings_hub", style="primary"),
            make_btn("🔙 সেটিংস হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger")
        )
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("admin_db_export_hub_msg"), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data in ("adm_man_ver:hub", "adm_shub:manual_verify", "adm_mvr_gen") or call.data.startswith("adm_mvr_act:"):
        if call.data == "adm_mvr_gen":
            with db_lock:
                c_info = generate_admin_manual_verify_code(admin_id=uid, expiry_sec=300)
            bot.answer_callback_query(call.id, f"নতুন ওয়ান-টাইম কোড তৈরি হয়েছে: {c_info['code']} (১ বার ব্যবহারযোগ্য)", show_alert=True)
            gen_kb = types.InlineKeyboardMarkup()
            append_page_edit_tools(gen_kb, uid, msg_key="admin_random_code_generated_msg")
            safe_send(
                call.message.chat.id,
                get_msg(
                    "admin_random_code_generated_msg",
                    code=esc(c_info["code"]),
                    expires_at=esc(c_info["expires_at_str"])
                ),
                reply_markup=gen_kb if (is_admin_unlocked(uid)) else None
            )

        elif call.data.startswith("adm_mvr_act:"):
            _, m_act, req_id_s = call.data.split(":")
            approve_flag = (m_act == "approve")
            with db_lock:
                res_mvr = resolve_manual_verification_request(str(req_id_s), admin_id=uid, approve=approve_flag)
            if not res_mvr.get("ok"):
                bot.answer_callback_query(call.id, res_mvr.get("reason", "প্রসেস করা যায়নি!"), show_alert=True)
            else:
                req_d = res_mvr["request"]
                t_uid = str(req_d["user_id"])
                p_key = str(req_d["platform"]).lower()
                p_title = PLATFORMS.get(p_key, {}).get("title", p_key.upper())
                if approve_flag:
                    t_u = get_user(t_uid)
                    if t_u and not int(t_u.get("registered") or 0):
                        cur_st = user_memory_states.get(t_uid) or {}
                        ver_list = list(cur_st.get("verified_platforms") or [])
                        if p_key not in ver_list:
                            ver_list.append(p_key)
                        rem_queue = [pk for pk in (cur_st.get("queue") or []) if pk != p_key and pk in ("youtube", "tiktok")]
                        if rem_queue:
                            next_p = rem_queue[0]
                            n_crit = get_platform_criteria(next_p)
                            n_tot_v = int(n_crit["min_views"]) * int(n_crit["qualifying_videos"])
                            user_memory_states[t_uid] = {
                                "step": "reg_platform_input",
                                "queue": rem_queue,
                                "verified_platforms": ver_list,
                                "primary_url": cur_st.get("primary_url") or req_d["profile_url"],
                                "primary_subs": 200
                            }
                            try:
                                safe_send(
                                    int(t_uid),
                                    f"✅ <b>ম্যানুয়ালি অ্যাকসেপ্ট করা হইছে আপনার {esc(p_title)} অ্যাকাউন্ট!</b>\n\n"
                                    + get_msg(
                                        "reg_code_prompt_msg",
                                        platform_title=PLATFORMS[next_p]["title"],
                                        bio_code=t_u["bio_verify_code"],
                                        min_subs=n_crit["min_subs"],
                                        min_total_vids=n_crit.get("min_total_videos", 8),
                                        qual_vids=n_crit["qualifying_videos"],
                                        min_views=n_crit["min_views"],
                                        total_req_views=n_tot_v
                                    )
                                )
                            except Exception:
                                pass
                        else:
                            new_st = {
                                "step": "reg_app_uid",
                                "verified_platforms": ver_list,
                                "primary_url": cur_st.get("primary_url") or req_d["profile_url"],
                                "primary_subs": 200,
                                "selected_pay_methods": ["bKash", "BattleClub_UID"],
                                "pay_queue": ["bKash"],
                                "ver_summary_html": get_msg("manual_verify_approved_msg", platform_title=p_title)
                            }
                            user_memory_states[t_uid] = new_st
                            try:
                                start_step2_mandatory_uid_flow(
                                    int(t_uid),
                                    t_uid,
                                    new_st,
                                    verification_summary=get_msg("manual_verify_approved_msg", platform_title=p_title)
                                )
                            except Exception:
                                pass
                    else:
                        user_memory_states.pop(t_uid, None)
                        try:
                            safe_send(
                                int(t_uid),
                                f"✅ <b>অ্যাডমিন ম্যানুয়াল ভেরিফিকেশন অনুমোদিত!</b>\nআপনার <b>{esc(p_title)}</b> প্রোফাইলটি ভেরিফাইড (VERIFIED) ও যুক্ত করা হয়েছে। এখন আপনি এই অ্যাকাউন্ট থেকে ভিডিও সাবমিট করতে পারবেন!",
                                reply_markup=build_user_home_keyboard(t_uid, get_user(t_uid)),
                                menu_id="user_home"
                            )
                        except Exception:
                            pass
                    bot.answer_callback_query(call.id, "✅ ম্যানুয়াল ভেরিফিকেশন Approve করা হয়েছে এবং ইউজারকে পরবর্তী ধাপে পাঠানো হয়েছে!", show_alert=True)
                else:
                    t_u = get_user(t_uid)
                    user_memory_states.pop(t_uid, None)
                    try:
                        safe_send(int(t_uid), f"❌ <b>আপনার {esc(p_title)} ম্যানুয়াল ভেরিফিকেশন রিকোয়েস্টটি অ্যাডমিন রিভিউতে বাতিল করা হয়েছে।</b>")
                        if t_u and not int(t_u.get("registered") or 0):
                            send_onboarding_home(int(t_uid), t_uid, t_u)
                    except Exception:
                        pass
                    bot.answer_callback_query(call.id, "❌ ম্যানুয়াল ভেরিফিকেশন রিকোয়েস্ট Reject করা হয়েছে!", show_alert=True)

        with db_lock:
            pend_list = get_pending_manual_verifications()
            recent_all = get_manual_verification_requests("all")[:5]
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔑 নতুন র‍্যান্ডম কোড জেনারেট করুন (ভেরিফাই ও নাম্বার চেঞ্জ)", callback_data="adm_mvr_gen", style="success"))
        lines = [
            "🛠️ <b>প্ল্যাটফর্ম ম্যানুয়াল প্রসেসিং ও নাম্বার পরিবর্তন র‍্যান্ডম কোড হাব:</b>",
            FULL_WIDTH_DIVIDER,
            "ℹ️ ইউজার সাপোর্টে যোগাযোগ করলে এখান থেকে ওয়ান-টাইম <code>BC-XXXXXX</code> র‍্যান্ডম কোড তৈরি করে দিন।\n"
            "• <b>চ্যানেল ভেরিফিকেশনের ক্ষেত্রে:</b> ইউজার কোডটি দিলে নিচে পেন্ডিং রিকোয়েস্ট হিসেবে জমা হবে এবং আপনি <b>✅ Approve</b> করলে অ্যাকাউন্টটি সম্পূর্ণ VERIFIED হয়ে পরবর্তী ধাপে চলে যাবে।\n"
            "• <b>বিকাশ/নগদ/রকেট নাম্বার পরিবর্তনের ক্ষেত্রে:</b> ইউজার প্রোফাইল এডিট অপশনে গিয়ে কোডটি দিলেই বট সাথে সাথে যাচাই করে তাকে নাম্বার আপডেট করার অপশন দেবে!",
            f"• পেন্ডিং ম্যানুয়াল ভেরিফিকেশন রিকোয়েস্ট: <b>{len(pend_list)} টি</b>"
        ]
        for r_item in pend_list[:10]:
            req_id_val = r_item.get("req_id") or r_item.get("id")
            u_inf = get_user(r_item["user_id"]) or {}
            p_t = PLATFORMS.get(r_item["platform"], {}).get("title", r_item["platform"].upper())
            lines.append(
                f"\n🆔 Req <code>{esc(req_id_val)}</code> — <b>{esc(get_user_label(u_inf))}</b> (ID: <code>{r_item['user_id']}</code>)\n"
                f"├ প্ল্যাটফর্ম: <b>{esc(p_t)}</b> | র‍্যান্ডম কোড: <code>{esc(r_item.get('code_used') or r_item.get('manual_code_used'))}</code>\n"
                f"├ বায়ো কোড: <code>{esc(r_item['bio_code'])}</code>\n"
                f"└ প্রোফাইল: <a href=\"{esc(r_item['profile_url'])}\">🔗 প্রোফাইল লিংক ওপেন করুন</a>"
            )
            kb.row(make_btn(f"🔗 প্রোফাইল দেখুন ({r_item['platform'].upper()})", url=r_item["profile_url"], style="primary"))
            kb.row(
                make_btn("✅ Approve (Verified হিসেবে যুক্ত করুন)", callback_data=f"adm_mvr_act:approve:{req_id_val}", style="success"),
                make_btn("❌ Reject", callback_data=f"adm_mvr_act:reject:{req_id_val}", style="danger")
            )
        if not pend_list and recent_all:
            lines.append("\n📋 <b>সাম্প্রতিক ম্যানুয়াল প্রসেসিং রেকর্ড:</b>")
            for rc in recent_all:
                lines.append(f"• <code>{esc(rc.get('manual_code_used'))}</code> — User <code>{esc(rc.get('user_id'))}</code> ({rc.get('platform', '').upper()}) — <b>{rc.get('status', '').upper()}</b>")
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, "\n".join(lines), reply_markup=kb)
        if not call.data.startswith("adm_mvr_"):
            bot.answer_callback_query(call.id)
        return

    if call.data == "adm_shub:antifraud":
        auto_rej = get_setting("suspicious_auto_reject", "1") == "1"
        min_dur = get_setting("min_video_duration_sec", "10")
        vel_thr = get_setting("view_velocity_threshold", "15000")
        eng_thr = get_setting("engagement_threshold_ratio", "0.0005")
        eng_pct = round(float(eng_thr) * 100.0, 4)
        strk_lim = get_setting("strike_limit", "3")

        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                f"🚨 ফেক/সন্দেহজনক ভিউ মোড: {'🟢 অটো-রিজেক্ট (Rejected বাটনে যাবে)' if auto_rej else '🟡 ম্যানুয়াল রিভিউ (Payment Block)'}",
                callback_data="adm_rset:suspicious_auto_reject:adm_shub:antifraud",
                style="danger" if auto_rej else "primary"
            )
        )
        kb.row(make_btn(f"⏱️ Minimum Video Duration ({min_dur} সেকেন্ড)", callback_data="adm_rset:min_video_duration_sec:adm_shub:antifraud", style="primary"))
        kb.row(make_btn(f"🚀 View Velocity Threshold ({vel_thr} ভিউ/ঘণ্টা)", callback_data="adm_rset:view_velocity_threshold:adm_shub:antifraud", style="success"))
        kb.row(make_btn(f"💬 Engagement Threshold Ratio ({eng_thr} = {eng_pct}%)", callback_data="adm_rset:engagement_threshold_ratio:adm_shub:antifraud", style="primary"))
        kb.row(make_btn(f"⚠️ Strike Limit ({strk_lim} স্ট্রাইক)", callback_data="adm_rset:strike_limit:adm_shub:antifraud", style="danger"))
        kb.row(make_btn("🔙 প্ল্যাটফর্ম সেটিংসে ফিরে যান", callback_data="adm_plat_settings_hub", style="primary"))
        kb.row(
            make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="primary"),
            make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger")
        )

        txt = (
            "🛡️ <b>অ্যান্টি-ফ্রড, ট্রাফিক সোর্স ও অর্গানিক/ফেক ভিউ রিস্ক সেটিংস (বিস্তারিত বিবরণসহ):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• <b>ফেক ভিউ শনাক্তকরণ অ্যাকশন:</b> <b>{'ON (অটো-রিজেক্ট ও ব্যালেন্স কর্তন)' if auto_rej else 'OFF (পেমেন্ট ব্লক ও ম্যানুয়াল রিভিউ)'}</b>\n"
            f"  └ <i>পরিবর্তন করলে কী হবে:</i> এটি ON থাকলে ফেক ভিউ ধরা পড়লেই ভিডিওটি সরাসরি Rejected হয়ে অর্জিত টাকা কেটে যাবে।\n\n"
            f"• <b>Minimum Video Duration:</b> <b>{min_dur} সেকেন্ড</b>\n"
            f"  └ <i>পরিবর্তন করলে কী হবে:</i> {min_dur} সেকেন্ডের কম দৈর্ঘ্যের ভিডিও সাবমিট করলে বট স্বয়ংক্রিয়ভাবে রিজেক্ট করবে।\n\n"
            f"• <b>View Velocity Threshold:</b> <b>{vel_thr} ভিউ/ঘণ্টা</b>\n"
            f"  └ <i>পরিবর্তন করলে কী হবে:</i> ঘণ্টায় {vel_thr}+ অস্বাভাবিক ভিউ স্পাইক হলে এবং লাইক/কমেন্ট না থাকলে বট ফেক প্যানেল ভিউ হিসেবে ধরবে।\n\n"
            f"• <b>Engagement Threshold Ratio:</b> <b>{eng_thr} ({eng_pct}%)</b>\n"
            f"  └ <i>পরিবর্তন করলে কী হবে:</i> মোট ভিউয়ের বিপরীতে কমপক্ষে {eng_pct}% লাইক/কমেন্ট না থাকলে ফেক ভিউ হিসেবে শনাক্ত হবে।\n\n"
            f"• <b>Strike Limit:</b> <b>{strk_lim} বার</b>\n"
            f"  └ <i>পরিবর্তন করলে কী হবে:</i> ইউজার পরপর {strk_lim} বার ডুপ্লিকেট বা অন্য চ্যানেলের ভুল ভিডিও দিলে তার একাউন্ট অটো-ফ্রিজ হবে।"
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_shub:hashtag_yt":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("📌 বাধ্যতামূলক হ্যাশট্যাগ পরিবর্তন", callback_data="adm_edit_hashtags", style="success"))
        kb.row(make_btn("🔗 ভেরিফিকেশন লিংক (Verification Link) সেটআপ", callback_data="adm_edit_ver_link", style="primary"))
        kb.row(make_btn("🎥 হোমপেজ ইউটিউব ভিডিও লিংক সেটআপ", callback_data="adm_edit_top_yt", style="danger"))
        kb.row(make_btn(f"⚙️ Required Link Configuration ({get_setting('required_link_config', 'all_public')})", callback_data="adm_edit_req_link", style="primary"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        txt = (
            "🔐 <b>হ্যাশট্যাগ, ভেরিফিকেশন লিংক ও ইউটিউব লিংক সেটআপ:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• Mandatory Hashtags: <code>{esc(get_setting('global_required_code'))}</code>\n"
            f"• Verification Link (Bio/Video): <code>{esc(get_setting('verification_link') or 'none')}</code>\n"
            f"• YouTube Homepage Link: <code>{esc(get_setting('home_youtube_link') or 'none')}</code>\n"
            f"• Required Link Config: <code>{esc(get_setting('required_link_config', 'all_public'))}</code>"
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_shub:support_group":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("💬 সাপোর্ট লিংক পরিবর্তন করুন", callback_data="adm_edit_support_link", style="primary"))
        kb.row(make_btn("👥 কমিউনিটি গ্রুপ লিংক পরিবর্তন করুন", callback_data="adm_edit_group_link", style="success"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        txt = (
            "💬 <b>সাপোর্ট ও গ্রুপ লিংক পরিবর্তন:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• Support Link: <code>{esc(get_setting('support_link'))}</code>\n"
            f"• Group Link: <code>{esc(get_setting('group_link'))}</code>\n\n"
            "<i>(সাপোর্ট লিংক পরিবর্তন করলে বটের সকল সাপোর্ট বাটন ও পাসওয়ার্ড রিসেট সাপোর্ট লিংকে স্বয়ংক্রিয়ভাবে নতুন লিংকটি যুক্ত হবে।)</i>"
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_guide_map":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("⌨️ কমান্ড ও শর্টকাট তালিকা দেখুন", callback_data="adm_cmd_shortcuts", style="primary"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, ADMIN_GUIDE_TEXT, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_cmd_shortcuts" or call.data.startswith("adm_cmd_cat:"):
        cat = call.data.split(":", 1)[1] if ":" in call.data else "all"
        kb = build_command_shortcuts_keyboard(cat)
        safe_edit(call.message.chat.id, call.message.message_id, build_full_command_shortcut_text(cat), reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_toggle:"):
        parts = call.data.split(":")
        t_key = parts[1]
        back_cb = ":".join(parts[2:]) if len(parts) > 2 else "adm_settings_hub"
        cur_v = get_setting(t_key, "0")
        new_v = "0" if str(cur_v) == "1" else "1"
        set_setting(t_key, new_v)
        bot.answer_callback_query(call.id, f"{t_key} = {'ON (1)' if new_v == '1' else 'OFF (0)'} সেট করা হয়েছে!")
        call.data = back_cb
        handle_admin_settings_and_limits(call)
        return

    if call.data.startswith("adm_set_theme:"):
        target = call.data.split(":", 1)[1]
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("সবুজ (Success)", callback_data=f"adm_apply_theme:{target}:success", style="success"), make_btn("লাল (Danger)", callback_data=f"adm_apply_theme:{target}:danger", style="danger"))
        kb.row(make_btn("নীল (Primary)", callback_data=f"adm_apply_theme:{target}:primary", style="primary"))
        kb.row(make_btn("🎛️ বাটন ধরে ধরে কালার ও নাম বদলান", callback_data=f"adm_elayout:{'admin_home' if target == 'admin' else 'user_home'}", style="success"))
        kb.row(make_btn("🔙 অ্যাডভান্সড সেটিংসে ফিরে যান", callback_data="adm_adv_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🎨 <b>{'এডমিন' if target == 'admin' else 'ইউজার'} প্যানেলের বাটন কালার সিলেক্ট করুন:</b>\n{FULL_WIDTH_DIVIDER}", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_apply_theme:"):
        _, target, col = call.data.split(":")
        set_setting("global_admin_theme" if target == "admin" else "global_user_theme", col)
        prefix = "a_" if target == "admin" else "u_"
        for k in DEFAULT_BUTTON_LABELS:
            if k.startswith(prefix):
                set_btn_style(k, col)
        bot.answer_callback_query(call.id, "কালার থিম আপডেট হয়েছে!")
        call.data = "adm_btn_editor_hub"
        handle_dynamic_ui_and_message_editors(call)
        return

    if call.data == "adm_wd_limit_hub":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"📉 মিনিমাম উইথড্র লিমিট ({get_setting('min_withdraw')}৳)", callback_data="adm_wd_lset:min_withdraw", style="primary"))
        kb.row(make_btn(f"🔢 দিনে কয়টা উইথড্র দিতে পারবে ({get_setting('max_daily_wd_count')} বার)", callback_data="adm_wd_lset:max_daily_wd_count", style="success"))
        kb.row(make_btn(f"💵 দিনে সর্বোচ্চ কত টাকা উইথড্র ({get_setting('max_daily_wd_amount')}৳)", callback_data="adm_wd_lset:max_daily_wd_amount", style="danger"))
        kb.row(make_btn(f"💰 প্রতিবারে সর্বোচ্চ উইথড্র ({get_setting('max_single_withdraw', '5000.0')}৳)", callback_data="adm_wd_lset:max_single_withdraw", style="primary"))
        kb.row(make_btn(f"⏳ উইথড্র পেমেন্ট পাওয়ার সম্ভাব্য সময় ({get_setting('wd_eta_text')})", callback_data="adm_wd_lset:wd_eta_text", style="success"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"💸 <b>উইথড্র লিমিট সেটিংস:</b>\n{FULL_WIDTH_DIVIDER}\nকোন লিমিটটি পরিবর্তন করতে চান তা সিলেক্ট করুন:", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_wd_lset:"):
        key = call.data.split(":", 1)[1]
        user_memory_states[uid] = {"admin_action": "set_setting_num", "key": key, "back": "adm_wd_limit_hub"}
        cur_val = get_setting(key)
        expl = SETTING_FIELD_EXPLANATIONS.get(key, "এই উইথড্র লিমিটটি পরিবর্তন করলে সাথে সাথে নতুন নিয়ম কার্যকর হবে।")
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 উইথড্র লিমিট সেটিংসে ফিরে যান", callback_data="adm_wd_limit_hub", style="danger"))
        safe_send(
            call.message.chat.id,
            f"✍️ <b>উইথড্র সেটিংস আপডেট:</b> <code>{esc(key)}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"📊 বর্তমান মান: <b>{esc(cur_val)}</b>\n"
            f"📌 <b>এটি চেঞ্জ করলে কী হবে:</b>\n{esc(expl)}\n\n"
            f"👇 এখন নতুন মানটি লিখে পাঠান:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_ref_hub":
        unlock_first = get_setting("ref_unlock_on_first_video", "0") == "1"
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"🎁 রেফারকারী কত টাকা পাবে ({get_setting('ref_bonus')}৳)", callback_data="adm_rset:ref_bonus:adm_edit_ref_hub", style="success"))
        kb.row(make_btn(f"🎟️ রিডিম বোনাস ({get_setting('redeem_bonus')}৳)", callback_data="adm_rset:redeem_bonus:adm_edit_ref_hub", style="primary"))
        kb.row(make_btn(f"👥 দৈনিক রেফার/রিডিম লিমিট ({get_setting('max_daily_referrals')} জন)", callback_data="adm_rset:max_daily_referrals:adm_edit_ref_hub", style="success"))
        kb.row(
            make_btn(
                f"🔓 ১ম ভিডিও অ্যাপ্রুভ আনলক টগল: {'🟢 চালু (ON)' if unlock_first else '⚪ বন্ধ (Instant)'}",
                callback_data="adm_toggle:ref_unlock_on_first_video:adm_edit_ref_hub",
                style="success" if unlock_first else "primary"
            )
        )
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, f"🎁 <b>রেফার ও রিডিম সেটিংস:</b>\n{FULL_WIDTH_DIVIDER}", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_rate_days":
        enf_72h = get_setting("enforce_72h_rule", "1") == "1"
        min_init_v = int(float(get_setting("min_initial_views", "1000") or 1000))
        f_1k_pay = get_setting("first_1000_views_payment", get_setting("rate_per_1k", "15.0"))
        ev_200_pay = get_setting("every_200_views_payment", "3.0")
        step_sz = int(float(get_setting("view_step_size", "200") or 200))
        max_cap_v = int(float(get_setting("max_payable_views", "5000000") or 5000000))
        earn_d = get_setting("earning_duration_days", get_setting("view_tracking_days", "5"))
        sub_hrs = int(float(get_setting("submission_window_hours", "72") or 72))
        sub_days_disp = round(sub_hrs / 24.0, 1)
        qual_hrs = int(float(get_setting("qualification_window_hours", "120") or 120))
        qual_days_disp = round(qual_hrs / 24.0, 1)
        step_pct = round((step_sz / max(1, min_init_v)) * 100.0, 1)

        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(f"🎯 ১ম টার্গেট ভিউ ({min_init_v} ভিউ)", callback_data="adm_rset:min_initial_views:adm_edit_rate_days", style="primary"),
            make_btn(f"💸 ১ম টার্গেট পেমেন্ট ({f_1k_pay}৳)", callback_data="adm_rset:first_1000_views_payment:adm_edit_rate_days", style="success")
        )
        kb.row(
            make_btn(f"💵 প্রতি স্টেপ পেমেন্ট ({ev_200_pay}৳)", callback_data="adm_rset:every_200_views_payment:adm_edit_rate_days", style="primary"),
            make_btn(f"🔢 ভিউ স্টেপ সাইজ ({step_sz} ভিউ = {step_pct}%)", callback_data="adm_rset:view_step_size:adm_edit_rate_days", style="success")
        )
        kb.row(make_btn(f"🔒 সর্বোচ্চ পেমেন্ট ভিউ ক্যাপ ({max_cap_v} ভিউ)", callback_data="adm_rset:max_payable_views:adm_edit_rate_days", style="success"))
        kb.row(
            make_btn(f"📅 ভিউ কাউন্ট মেয়াদ ({earn_d} দিন)", callback_data="adm_rset:earning_duration_days:adm_edit_rate_days", style="primary"),
            make_btn(f"⏳ পেন্ডিং টার্গেট মেয়াদ ({qual_days_disp} দিন / {qual_hrs}h)", callback_data="adm_rset:qualification_window_hours:adm_edit_rate_days", style="success")
        )
        kb.row(
            make_btn(
                f"⏰ পাবলিক সময়সীমা নিয়ম: {'🟢 ON' if enf_72h else '🔴 OFF'}",
                callback_data="adm_toggle:enforce_72h_rule:adm_edit_rate_days",
                style="success" if enf_72h else "danger"
            ),
            make_btn(f"📤 পাবলিকের পর সাবমিট সময় ({sub_days_disp} দিন / {sub_hrs}h)", callback_data="adm_rset:submission_window_hours:adm_edit_rate_days", style="primary")
        )
        cur_exp_act = get_setting("pending_expiry_action", "permanent_approve_zero_pay")
        exp_act_lbl = "🔒 ০৳ Permanent Approve" if cur_exp_act == "permanent_approve_zero_pay" else "❌ ০৳ Auto Reject"
        kb.row(make_btn(f"⌛ পেন্ডিং মেয়াদ শেষ হলে: {exp_act_lbl}", callback_data="adm_toggle_expiry_action", style="primary"))
        kb.row(make_btn(f"⏱️ ভিউ চেকিং ও অর্গানিক যাচাই ইন্টারভ্যাল ({get_setting('view_checking_interval_sec', '3600')}s)", callback_data="adm_rset:view_checking_interval_sec:adm_edit_rate_days", style="success"))
        kb.row(make_btn(f"🛡️ বায়ো ও কোড চেকিং ইন্টারভ্যাল ({get_setting('verification_interval_sec', '3600')}s)", callback_data="adm_rset:verification_interval_sec:adm_edit_rate_days", style="primary"))
        kb.row(make_btn(f"🔒 ইউজার সেশন লগআউট টাইমআউট ({get_setting('user_session_timeout_sec', '600')}s)", callback_data="adm_rset:user_session_timeout_sec:adm_edit_rate_days", style="danger"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))

        txt = (
            "📈 <b>ভিউ রেট, মেয়াদ ও ইন্টারভ্যাল সেটিংস (কোনটা চেঞ্জ করলে কী হবে তার বিস্তারিত গাইড):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"🎯 <b>১ম টার্গেট ভিউ ও পেমেন্ট:</b> <b>{min_init_v} ভিউ (১০০% প্রাথমিক টার্গেট) ➡️ {f_1k_pay} টাকা</b>\n"
            f"  └ <i>কাজ:</i> ভিডিওতে {min_init_v} ভিউ পূর্ণ না হওয়া পর্যন্ত ০ টাকা থাকবে; {min_init_v} ভিউ পূর্ণ হলেই {f_1k_pay}৳ যোগ হবে।\n\n"
            f"💵 <b>পরবর্তী ভিউ স্টেপ ও পেমেন্ট:</b> <b>প্রতি +{step_sz} ভিউ ({step_pct}% বৃদ্ধি) ➡️ +{ev_200_pay} টাকা</b>\n"
            f"  └ <i>কাজ:</i> প্রথম {min_init_v} ভিউয়ের পর প্রতি {step_sz} ভিউ পূর্ণ হলে একাউন্টে {ev_200_pay}৳ করে যোগ হতে থাকবে।\n\n"
            f"🔒 <b>সর্বোচ্চ পেমেন্ট ভিউ ক্যাপ ও মেয়াদ:</b> <b>{max_cap_v} ভিউ (৫০ লাখ) | মেয়াদ: {earn_d} দিন</b>\n"
            f"  └ <i>কাজ:</i> {earn_d} দিন শেষ হলে অথবা {max_cap_v} ভিউ পূর্ণ হলেই ফাইনাল যোগ্য ভিউয়ের পেমেন্ট হিসাব করে সাথে সাথে <b>Permanent Approve</b> হয়ে যাবে।\n\n"
            f"📤 <b>পাবলিকের পর সাবমিট সময়সীমা:</b> <b>{sub_days_disp} দিন ({sub_hrs} ঘণ্টা) [{'চালু' if enf_72h else 'বন্ধ'}]</b>\n"
            f"  └ <i>কাজ:</i> চ্যানেলে ভিডিও পাবলিক করার পর {sub_hrs} ঘণ্টার মধ্যে লিংক সাবমিট না করলে বট পুরাতন ভিডিও রিজেক্ট করে দেবে।"
        )
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_rset:"):
        parts = call.data.split(":")
        key = parts[1]
        back_cb = ":".join(parts[2:]) if len(parts) > 2 else "adm_edit_rate_days"
        user_memory_states[uid] = {"admin_action": "set_setting_num", "key": key, "back": back_cb}
        cur_val = get_setting(key)
        exp_msg_key = f"setting_exp_{key}"
        exp_body = get_msg(exp_msg_key) if exp_msg_key in DEFAULT_MESSAGES else (
            f"⚙️ <b>সেটিংস বিবরণ: {esc(key)}</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"📌 <b>এই সেটিংসের কাজ ও পরিবর্তনের প্রভাব:</b>\n{esc(SETTING_FIELD_EXPLANATIONS.get(key, 'এই অপশনটি পরিবর্তন করলে সিস্টেমের সংশ্লিষ্ট নিয়ম সাথে সাথে আপডেট হবে।'))}\n{FULL_WIDTH_DIVIDER}"
        )
        extra_hint = "\n💡 <i>টিপস: দিন হিসেবে দিতে চাইলে যেমন ৩ দিন হলে</i> <code>3d</code> <i>অথবা ঘণ্টায়</i> <code>72</code> <i>লিখুন।</i>" if key in ("submission_window_hours", "qualification_window_hours") else ""
        kb = types.InlineKeyboardMarkup()
        if key in ("suspicious_auto_reject", "enforce_72h_rule", "ref_unlock_on_first_video"):
            is_on = str(cur_val) == "1"
            kb.row(
                make_btn(
                    f"🔄 এখনই টগল করুন ({'🟢 ON -> 🔴 OFF করুন' if is_on else '🔴 OFF -> 🟢 ON করুন'})",
                    callback_data=f"adm_toggle:{key}:{back_cb}",
                    style="danger" if is_on else "success"
                )
            )
        append_page_edit_tools(kb, uid, msg_key=exp_msg_key)
        kb.row(
            make_btn("🔙 ফিরে যান", callback_data=back_cb, style="primary"),
            make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_send(
            call.message.chat.id,
            f"{exp_body}\n"
            f"📊 বর্তমান মান: <b>{esc(cur_val)}</b>{extra_hint}\n\n"
            f"👇 এখন নতুন মানটি সংখ্যায় লিখে পাঠান (অথবা উপরের টগল/এডিট বাটন ব্যবহার করুন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_crit:hub":
        yt_c = get_platform_criteria("youtube")
        tt_c = get_platform_criteria("tiktok")
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(f"📺 YouTube শর্ত ও রেট ({yt_c['min_subs']}+ Subs, {yt_c['rate_per_1k']}৳)", callback_data="adm_crit:view:youtube", style="danger"),
            make_btn(f"🎵 TikTok শর্ত ও রেট ({tt_c['min_subs']}+ Followers, {tt_c['rate_per_1k']}৳)", callback_data="adm_crit:view:tiktok", style="primary")
        )
        kb.row(make_btn("🔙 প্ল্যাটফর্ম সেটিংসে ফিরে যান", callback_data="adm_plat_settings_hub", style="primary"))
        kb.row(make_btn("🔙 সেটিংস ও কন্ট্রোল হাবে ফিরে যান", callback_data="adm_settings_hub", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            "🌐 <b>মাল্টি-প্ল্যাটফর্ম ভেরিফিকেশন শর্ত ও ভিউ রেট হাব (YouTube &amp; TikTok):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "এখান থেকে YouTube এবং TikTok উভয় প্ল্যাটফর্মের ভেরিফিকেশন রিকোয়ারমেন্ট (সাবস্ক্রাইবার/ফলোয়ার, মোট পাবলিক ভিডিও, যোগ্য ভিডিও, ভিউ শর্ত, ভেরিফিকেশন লিংক) এবং ভিডিও আর্নিং রিকোয়ারমেন্ট বিস্তারিত ব্যাখ্যাসহ এডিট ও আপডেট করতে পারবেন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_crit:view:"):
        plat = call.data.split(":", 2)[2].lower()
        if plat not in ("youtube", "tiktok"):
            plat = "youtube"
        crit = get_platform_criteria(plat)
        sub_w_hrs = int(crit.get("submission_window_hours", 72))
        sub_w_days = round(sub_w_hrs / 24.0, 1)
        qual_w_hrs = int(crit.get("qualification_window_hours", 120))
        qual_w_days = round(qual_w_hrs / 24.0, 1)
        min_init_v = int(crit.get("min_initial_views", 1000))
        step_sz_v = int(crit.get("step_size", 200))
        step_pct = round((step_sz_v / max(1, min_init_v)) * 100.0, 1)
        min_tot_v = max(1, int(crit.get("min_total_videos", 8)))
        qual_v = int(crit.get("qualifying_videos", 2))
        qual_v_pct = round((qual_v / min_tot_v) * 100.0, 1)
        tot_req_v = int(crit["min_views"]) * qual_v
        ver_link_v = crit.get("verification_link") or get_setting("verification_link", "") or "none"

        txt = (
            f"⚙️ <b>{PLATFORMS[plat]['title']} — ভেরিফিকেশন শর্ত ও ভিডিও আর্নিং সেটিংস (বিস্তারিত বিবরণসহ):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"🛡️ <b>১. চ্যানেল/প্রোফাইল ভেরিফিকেশন রিকোয়ারমেন্ট (৫ ধাপ ক্রম):</b>\n"
            f"├ 🔗 <b>১. বায়ো কোড / ভেরিফিকেশন লিংক:</b> <code>{esc(ver_link_v)}</code>\n"
            f"├ 👥 <b>২. ন্যূনতম সাবস্ক্রাইবার/ফলোয়ার:</b> <b>{crit['min_subs']} জন (১০০% শর্ত)</b>\n"
            f"├ 📹 <b>৩. ন্যূনতম পাবলিক ভিডিও:</b> <b>{min_tot_v} টি</b>\n"
            f"├ 🎬 <b>৪. ন্যূনতম যোগ্যতা ভিডিও:</b> <b>{qual_v} টি ({qual_v_pct}% ভিডিও)</b>\n"
            f"├ 👁️ <b>৫. যোগ্য ভিডিওর ন্যূনতম ভিউ:</b> <b>প্রতিটিতে {crit['min_views']}+ ভিউ (মোট {tot_req_v}+ ভিউ)</b>\n"
            f"└ 📱 <b>অ্যাকাউন্ট লিমিট:</b> <b>সর্বোচ্চ {crit['max_accounts']} টি চ্যানেল</b> (নতুন অ্যাকাউন্ট যোগ করার সীমা)\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"🎬 <b>২. ভিডিও সাবমিটার ও ভিউ গণনা রিকোয়ারমেন্ট:</b>\n"
            f"├ 🎯 <b>১ম পেমেন্ট টার্গেট ভিউ:</b> <b>{min_init_v} ভিউ ➡️ {crit.get('rate_per_1k', 15.0)} টাকা</b>\n"
            f"├ 💵 <b>পরবর্তী স্টেপ ভিউ ও পেমেন্ট:</b> <b>প্রতি +{step_sz_v} ভিউ ({step_pct}% বৃদ্ধি) ➡️ +{crit.get('every_200_views_payment', 3.0)} টাকা</b>\n"
            f"├ 📅 <b>ভিউ কাউন্ট মেয়াদ:</b> <b>{crit.get('earning_duration_days', 5)} দিন</b> (শেষ হলেই Permanent Approve)\n"
            f"├ ⏳ <b>পেন্ডিং টার্গেট পূরণ মেয়াদ:</b> <b>{qual_w_days} দিন ({qual_w_hrs} ঘণ্টা)</b>\n"
            f"├ 📤 <b>পাবলিকের পর সাবমিট সময়সীমা:</b> <b>{sub_w_days} দিন ({sub_w_hrs} ঘণ্টা)</b>\n"
            f"└ 🔒 <b>সর্বোচ্চ ভিউ ক্যাপ:</b> <b>{crit.get('max_payable_views', 5000000)} ভিউ</b>"
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"🔗 ভেরিফিকেশন লিংক ({ver_link_v[:18]})", callback_data=f"adm_crit:edit:{plat}:verification_link", style="success"))
        kb.row(make_btn(f"👥 সাবস্ক্রাইবার/ফলোয়ার ({crit['min_subs']})", callback_data=f"adm_crit:edit:{plat}:min_subs", style="primary"))
        kb.row(make_btn(f"📹 পাবলিক ভিডিও সংখ্যা ({min_tot_v}টি)", callback_data=f"adm_crit:edit:{plat}:min_total_videos", style="success"))
        kb.row(
            make_btn(f"🎬 যোগ্য ভিডিও ({qual_v}টি)", callback_data=f"adm_crit:edit:{plat}:qualifying_videos", style="primary"),
            make_btn(f"👁️ ন্যূনতম ভিউ ({crit['min_views']})", callback_data=f"adm_crit:edit:{plat}:min_views", style="success")
        )
        kb.row(
            make_btn(f"🎯 ১ম টার্গেট ভিউ ({min_init_v})", callback_data=f"adm_crit:edit:{plat}:min_initial_views", style="primary"),
            make_btn(f"💸 ১ম পেমেন্ট ({crit.get('rate_per_1k', 15.0)}৳)", callback_data=f"adm_crit:edit:{plat}:rate_per_1k", style="success")
        )
        kb.row(
            make_btn(f"🔢 ভিউ স্টেপ ({step_sz_v} ভিউ)", callback_data=f"adm_crit:edit:{plat}:step_size", style="primary"),
            make_btn(f"💵 স্টেপ পেমেন্ট ({crit.get('every_200_views_payment', 3.0)}৳)", callback_data=f"adm_crit:edit:{plat}:every_200_views_payment", style="success")
        )
        kb.row(
            make_btn(f"📅 ভিউ কাউন্ট মেয়াদ ({crit.get('earning_duration_days', 5)} দিন)", callback_data=f"adm_crit:edit:{plat}:earning_duration_days", style="primary"),
            make_btn(f"⏳ পেন্ডিং মেয়াদ ({qual_w_hrs}h)", callback_data=f"adm_crit:edit:{plat}:qualification_window_hours", style="success")
        )
        kb.row(
            make_btn(f"📤 সাবমিট সময় ({sub_w_hrs}h)", callback_data=f"adm_crit:edit:{plat}:submission_window_hours", style="primary"),
            make_btn(f"🔒 সর্বোচ্চ ভিউ ক্যাপ ({crit.get('max_payable_views', 5000000)})", callback_data=f"adm_crit:edit:{plat}:max_payable_views", style="success")
        )
        kb.row(make_btn(f"📱 অ্যাকাউন্ট লিমিট ({crit['max_accounts']}টি)", callback_data=f"adm_crit:edit:{plat}:max_accounts", style="danger"))
        kb.row(make_btn("🔙 প্ল্যাটফর্ম তালিকায় যান", callback_data="adm_crit:hub", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_crit:edit:"):
        _, _, plat, field = call.data.split(":")
        user_memory_states[uid] = {"admin_action": "update_crit", "plat": plat, "field": field}
        crit = get_platform_criteria(plat)
        cur_v = crit.get(field, "")
        meta_exp = CRITERIA_FIELD_EXPLANATIONS.get(field, {})
        f_title = meta_exp.get("title", field)
        f_unit = meta_exp.get("unit", "")
        f_impact = meta_exp.get("impact", "এটি পরিবর্তন করলে ভেরিফিকেশন ও ভিউ গণনায় সাথে সাথে নতুন নিয়ম কার্যকর হবে।")
        extra_h = "\n💡 <i>টিপস: দিন হিসেবে দিতে চাইলে যেমন</i> <code>3d</code> <i>লিখুন অথবা ঘণ্টায় যেমন</i> <code>72</code> <i>লিখুন।</i>" if field in ("submission_window_hours", "qualification_window_hours") else ""
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data=f"adm_crit:view:{plat}", style="danger"))
        safe_send(
            call.message.chat.id,
            f"✍️ <b>{PLATFORMS[plat]['title']} — {esc(f_title)} আপডেট করুন:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"📊 বর্তমান সেট করা মান: <b>{esc(str(cur_v))} {esc(f_unit)}</b>\n\n"
            f"📌 <b>এটি চেঞ্জ করলে কী পরিবর্তন আসবে:</b>\n{esc(f_impact)}{extra_h}\n\n"
            f"👇 এখন নতুন মানটি নিচে লিখে পাঠান:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_hashtags":
        user_memory_states[uid] = {"admin_action": "set_hashtags"}
        safe_send(call.message.chat.id, f"🔐 <b>বাধ্যতামূলক হ্যাশট্যাগ সেটআপ:</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান: <code>{esc(get_setting('global_required_code'))}</code>\n\nনতুন হ্যাশট্যাগগুলো স্পেস দিয়ে লিখে পাঠান:")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_ver_link":
        user_memory_states[uid] = {"admin_action": "set_ver_link"}
        safe_send(call.message.chat.id, f"🔗 <b>ভেরিফিকেশন লিংক (Verification Link) সেটআপ:</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান: <code>{esc(get_setting('verification_link') or 'none')}</code>\n\nনতুন ভেরিফিকেশন লিংক পাঠান (বন্ধ করতে <code>none</code> লিখুন):")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_top_yt":
        user_memory_states[uid] = {"admin_action": "set_top_yt"}
        safe_send(call.message.chat.id, f"🎥 <b>স্টার্ট ও হোমপেজ ইউটিউব ভিডিও লিংক:</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান: <code>{esc(get_setting('home_youtube_link') or 'none')}</code>\nনতুন ইউটিউব লিংক পাঠান (বন্ধ করতে <code>none</code> লিখুন):")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_toggle_expiry_action":
        cur_ea = get_setting("pending_expiry_action", "permanent_approve_zero_pay").strip().lower()
        new_ea = "reject" if cur_ea == "permanent_approve_zero_pay" else "permanent_approve_zero_pay"
        set_setting("pending_expiry_action", new_ea)
        bot.answer_callback_query(
            call.id,
            f"✅ পেন্ডিং মেয়াদ শেষ হলে অ্যাকশন = {'❌ ০ টাকায় Auto Reject' if new_ea == 'reject' else '🔒 ০ টাকায় Permanent Approve'} সেট করা হয়েছে!",
            show_alert=True
        )
        call.data = "adm_edit_rate_days"
        return handle_admin_settings_and_limits(call)

    if call.data == "adm_edit_req_link" or call.data.startswith("adm_set_req_link:"):
        if call.data.startswith("adm_set_req_link:"):
            target_cfg = call.data.split(":", 1)[1].strip().lower()
            if target_cfg in ("all_public", "on"):
                cur_vlink = str(get_setting("verification_link", "") or "").strip()
                if not cur_vlink or cur_vlink.lower() in ("none", "nane", "0", "off"):
                    bot.answer_callback_query(
                        call.id,
                        "⚠️ আগে একটি বৈধ Verification Link সেট করুন, তারপর Required Link ON করুন!",
                        show_alert=True
                    )
                    return
            set_setting("required_link_config", target_cfg)
            bot.answer_callback_query(
                call.id,
                f"✅ Required Link Configuration = {'🟢 ON (all_public)' if target_cfg != 'off' else '🔴 OFF (off)'} সেট করা হয়েছে!",
                show_alert=True
            )
            call.data = "adm_shub:hashtag_yt"
            return handle_admin_settings_and_limits(call)

        cur_cfg = get_setting("required_link_config", "all_public").strip().lower()
        cur_vlink = get_setting("verification_link", "") or "none"
        is_req_on = cur_cfg not in ("off", "none", "0", "false", "disabled")
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                f"{'✅ ' if is_req_on else ''}🟢 চালু রাখুন (ON — Code + Link উভয়ই বাধ্যতামূলক)",
                callback_data="adm_set_req_link:all_public",
                style="success"
            )
        )
        kb.row(
            make_btn(
                f"{'✅ ' if not is_req_on else ''}🔴 বন্ধ রাখুন (OFF — শুধু Unique Code বাধ্যতামূলক)",
                callback_data="adm_set_req_link:off",
                style="danger"
            )
        )
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:hashtag_yt", style="primary"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🔗 <b>Required Link Configuration (ভেরিফিকেশন লিংক শর্ত টগল):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• বর্তমান স্ট্যাটাস: <b>{'🟢 ON (all_public)' if is_req_on else '🔴 OFF (off)'}</b>\n"
            f"• বর্তমান Verification Link: <code>{esc(cur_vlink)}</code>\n\n"
            f"📌 <b>নিয়ম:</b> ইউনিক কোড (<code>BC-XXXXXX</code>) সবসময়ই বাধ্যতামূলক। এটি <b>ON</b> থাকলে এবং বৈধ Verification Link সেট করা থাকলে ইউনিক কোডের পাশাপাশি ভেরিফিকেশন লিংকটিও বাধ্যতামূলক হবে:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_support_link":
        user_memory_states[uid] = {"admin_action": "set_support_link"}
        safe_send(call.message.chat.id, f"💬 <b>সাপোর্ট লিংক পরিবর্তন:</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান: <code>{esc(get_setting('support_link'))}</code>\nনতুন টেলিগ্রাম সাপোর্ট লিংক পাঠান:")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_edit_group_link":
        user_memory_states[uid] = {"admin_action": "set_group_link"}
        safe_send(call.message.chat.id, f"👥 <b>গ্রুপ লিংক পরিবর্তন:</b>\n{FULL_WIDTH_DIVIDER}\nবর্তমান: <code>{esc(get_setting('group_link'))}</code>\nনতুন টেলিগ্রাম গ্রুপ লিংক পাঠান:")
        bot.answer_callback_query(call.id)
        return

    if call.data in ("adm_broadcast_prompt", "adm_bc_clear"):
        user_memory_states[uid] = {"admin_action": "broadcast_msg", "queue": []}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("✅ ডান / পাঠান (Done)", callback_data="adm_bc_done", style="success"))
        kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
        safe_send(
            call.message.chat.id,
            f"📢 <b>মাল্টি-মেসেজ ব্রডকাস্ট সিস্টেম (Multi-Message Broadcast):</b>\n{FULL_WIDTH_DIVIDER}\n"
            "আপনি একসাথে ১টি বা একাধিক (৪-৫টি বা তার বেশি) মেসেজ পাঠাতে পারবেন!\n"
            "✅ টেক্সট মেসেজ, প্রিমিয়াম কাস্টম ইমোজি, ভয়েস, অডিও, ভিডিও, ফটো ও রেকর্ড—সবকিছু সাপোর্টেড।\n"
            "📌 <b>ব্যবহার বিধি:</b>\n"
            "১. নিচে একের পর এক আপনার মেসেজগুলো পাঠান (প্রতিটি মেসেজ ব্রডকাস্ট কিউতে জমা হবে)।\n"
            "২. সব মেসেজ দেওয়া শেষ হলে নিচের <b>✅ ডান / পাঠান (Done)</b> বাটনে ক্লিক করুন—তখন সব মেসেজ একসাথে সকল ইউজারের কাছে ৫-ধাপ স্বয়ংক্রিয় রিট্রাইসহ চলে যাবে!",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id, "ব্রডকাস্ট কিউ প্রস্তুত!" if call.data == "adm_broadcast_prompt" else "ব্রডকাস্ট কিউ ক্লিয়ার করা হয়েছে!")
        return

    if call.data == "adm_bc_done":
        st_bc = user_memory_states.get(uid) or {}
        q_list = list(st_bc.get("queue") or [])
        if not q_list:
            bot.answer_callback_query(call.id, "⚠️ আগে কমপক্ষে ১টি ব্রডকাস্ট মেসেজ লিখে বা মিডিয়া পাঠান, তারপর Done চাপুন!", show_alert=True)
            return
        user_memory_states.pop(uid, None)
        bot.answer_callback_query(call.id, f"📢 মোট {len(q_list)}টি মেসেজ ব্রডকাস্ট করা হচ্ছে...")
        _execute_broadcast_queue_delivery(call.message.chat.id, uid, q_list)
        return

    if call.data == "adm_export_data":
        csv_file = "battle_club_users.csv"
        with db_lock:
            conn = get_connection()
            rows = conn.execute("SELECT * FROM users").fetchall()
            conn.close()
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["UserID", "Username", "Name", "AppUID", "Phone", "bKash", "Nagad", "Rocket", "PasswordSecurity", "BioCode", "Balance", "HeldBalance", "DebtBalance", "TotalEarned", "Status"])
            for r in rows:
                w.writerow([
                    r["user_id"], r["username"], r["name"], format_display_app_uid(r["app_uid"]), r["phone"],
                    r["bkash_number"] if "bkash_number" in r.keys() else "",
                    r["nagad_number"] if "nagad_number" in r.keys() else "",
                    r["rocket_number"] if "rocket_number" in r.keys() else "",
                    mask_sensitive_secret(r["password_hash"]), r["bio_verify_code"],
                    r["balance"], r["held_balance"], r["debt_balance"], r["total_earned"], r["status"]
                ])
        with open(csv_file, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption="📊 Users Database CSV Export (PBKDF2 Protected)")
        bot.answer_callback_query(call.id, "এক্সপোর্ট সম্পন্ন!")


# ==============================================================================
# PART 1 (ITEMS 3–13) & PART 17: ADVANCED SETTINGS HUB (`adm_adv_hub`)
# 1. Button Name, Text Design & Premium Custom Emoji Editor (All User & Admin Buttons, Paginated + Live Preview)
# 2. Message, Status & Premium Custom Emoji Editor (All Messages + Full Current Copy + Live Preview)
# 3. Button Position Change / বাটনের জায়গা পরিবর্তন করুন (Same-Page & Cross-Page Button Mover + Live Page Preview)
# ==============================================================================
def move_button_in_layout(layout, btn_key, direction):
    r_idx, c_idx = None, None
    for ri, row in enumerate(layout):
        if btn_key in row:
            r_idx, c_idx = ri, row.index(btn_key)
            break
    if r_idx is None:
        return layout
    if direction == "up" and r_idx > 0:
        layout[r_idx], layout[r_idx - 1] = layout[r_idx - 1], layout[r_idx]
    elif direction == "down" and r_idx < len(layout) - 1:
        layout[r_idx], layout[r_idx + 1] = layout[r_idx + 1], layout[r_idx]
    elif direction == "left" and c_idx > 0:
        row = layout[r_idx]
        row[c_idx], row[c_idx - 1] = row[c_idx - 1], row[c_idx]
    elif direction == "right" and c_idx < len(layout[r_idx]) - 1:
        row = layout[r_idx]
        row[c_idx], row[c_idx + 1] = row[c_idx + 1], row[c_idx]
    elif direction == "join_up" and r_idx > 0 and len(layout[r_idx - 1]) < 3:
        layout[r_idx].pop(c_idx)
        layout[r_idx - 1].append(btn_key)
    elif direction == "split_row" and len(layout[r_idx]) > 1:
        layout[r_idx].pop(c_idx)
        layout.insert(r_idx + 1, [btn_key])
    return [r for r in layout if r]


@bot.callback_query_handler(func=lambda c: c.data.startswith("cbtn_open:"))
@_guard("custom_btn_open")
def handle_custom_container_button_open(call):
    uid = str(call.from_user.id)
    u = get_user(uid) or ensure_user(call.from_user)
    cbtn_key = call.data.split(":", 1)[1].strip()
    cb_rec = get_custom_button(cbtn_key)
    if not cb_rec:
        bot.answer_callback_query(call.id, "এই বাটনটি পাওয়া যায়নি!", show_alert=True)
        return
    if cb_rec.get("side") == "admin" and not require_unlocked_admin_session(call):
        return
    l_key = cb_rec.get("destination_layout") or cb_rec["layout_key"]
    m_key = cb_rec["msg_key"]
    # Detect actual current parent layout if container was moved across pages or into a nested folder
    locs = locate_button_across_all_layouts(cbtn_key)
    parent_l_key = (locs[0]["layout_key"] if locs else cb_rec.get("parent_layout")) or ("admin_home" if cb_rec.get("side") == "admin" else "user_home")
    kb = build_dynamic_page_inline_keyboard(l_key, uid=uid, u_obj=u, msg_key=m_key)
    if str(parent_l_key).startswith("custom_page_"):
        parent_cbtn = str(parent_l_key)[len("custom_page_"):]
        if parent_cbtn and parent_cbtn != cbtn_key and get_custom_button(parent_cbtn):
            back_cb = f"cbtn_open:{parent_cbtn}"
        else:
            back_cb = "admin_hub" if cb_rec.get("side") == "admin" else "umenu:cancel_home"
    else:
        back_cb = "admin_hub" if str(parent_l_key).startswith("admin") else "umenu:cancel_home"
    kb.row(make_btn("🔙 ফিরে যান", callback_data=back_cb, style="danger"))
    txt = get_msg(m_key, name=esc(u.get("name", "")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid)
    if not txt.strip():
        txt = f"📂 <b>{esc(cb_rec.get('label', cbtn_key))}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের বাটনগুলো থেকে আপনার কাঙ্ক্ষিত অপশন নির্বাচন করুন:"
    safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=kb, menu_id=l_key)
    bot.answer_callback_query(call.id)


def _render_custom_button_final_preview(chat_id, uid: str, st: dict, edit_message_id: int = None):
    """Renders the Final Preview and Confirm Button for a pending Custom Button draft before DB Transaction."""
    cbtn_key = st.get("cbtn_key") or generate_unique_custom_button_id()
    st["cbtn_key"] = cbtn_key
    side = st.get("side", "user")
    parent_lk = resolve_layout_key(st.get("parent_layout") or ("admin_home" if side == "admin" else "user_home"))
    dest_lk = resolve_layout_key(st.get("destination_layout") or f"custom_page_{cbtn_key}")
    pos_mode = st.get("pos_mode", "bot")
    r_idx = int(st.get("row_index", 0) or 0)
    c_idx = int(st.get("col_index", 0) or 0)
    lbl = st.get("label") or "কাস্টম বাটন"
    em_id = st.get("custom_emoji_id", "")
    sub_btns = list(st.get("sub_buttons") or [])
    status_msg = st.get("status_msg") or f"📂 <b>{esc(lbl)}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের অপশনগুলো থেকে নির্বাচন করুন:"

    sub_names = [get_btn_raw_label(k) for k in sub_btns]
    sub_summary = ", ".join(sub_names) if sub_names else "(কোনো সাব-বাটন নির্বাচন করা হয়নি)"
    parent_title = LAYOUT_PAGE_TITLES.get(parent_lk, parent_lk)
    dest_title = LAYOUT_PAGE_TITLES.get(dest_lk, f"📂 {lbl} ({dest_lk})")

    txt = get_msg(
        "custom_button_preview_confirm_msg",
        cbtn_key=esc(cbtn_key),
        label=esc(lbl),
        side_label="👑 অ্যাডমিন সাইড (Admin)" if side == "admin" else "📱 ইউজার সাইড (User)",
        parent_page_title=esc(parent_title),
        dest_page_title=esc(dest_title),
        row_num=r_idx + 1,
        col_num=c_idx + 1,
        position_mode=esc(pos_mode.upper()),
        sub_count=len(sub_btns),
        sub_buttons_summary=esc(sub_summary),
        status_msg_preview=status_msg
    )

    kb = types.InlineKeyboardMarkup()
    # Live Interactive Preview of the button itself
    kb.row(
        make_btn(
            f"👁️ বাটন প্রিভিউ: {lbl}",
            callback_data="adm_cbw_prev",
            style="primary" if side == "admin" else "success",
            icon_custom_emoji_id=(em_id or None)
        )
    )
    kb.row(
        make_btn("✅ Confirm & Save Button (ডাটাবেসে যুক্ত করুন)", callback_data="adm_cbw_confirm", style="success")
    )
    kb.row(
        make_btn("📲 সাব-বাটন নির্বাচন/পরিবর্তন করুন", callback_data=f"adm_cbw_pick:{side}:0", style="primary"),
        make_btn("📐 প্যারেন্ট পেজ/পজিশন বদলান", callback_data=f"adm_cbn:{side}", style="primary")
    )
    kb.row(make_btn("❌ বাতিল করুন", callback_data="adm_cbl", style="danger"))

    if edit_message_id:
        safe_edit(chat_id, edit_message_id, txt, reply_markup=kb)
    else:
        safe_send(chat_id, txt, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: (
    c.data in ("adm_adv_hub", "adm_btn_editor_hub", "adm_msg_hub", "adm_bpos_hub", "adm_cbl", "adm_cbw_prev", "adm_cbw_confirm", "adm_cbw_skip_msg", "adm_lb_customizer") or
    c.data.startswith("adm_lb_style:") or
    c.data.startswith("adm_lb_rank:") or
    c.data.startswith("adm_brestore_norm_em:") or
    c.data.startswith("adm_ball_list:") or
    c.data.startswith("adm_msg_page:") or
    c.data.startswith("adm_elayout:") or
    c.data.startswith("adm_rlayout:") or
    c.data.startswith("adm_bitem:") or
    c.data.startswith("adm_bmove:") or
    c.data.startswith("adm_bmp:") or
    c.data.startswith("adm_bdp:") or
    c.data.startswith("adm_bde:") or
    c.data.startswith("adm_bdi:") or
    c.data.startswith("adm_bme:") or
    c.data.startswith("adm_bmove_page_pick:") or
    c.data.startswith("adm_bmove_page_exec:") or
    c.data.startswith("adm_cbn:") or
    c.data.startswith("adm_cbw_") or
    c.data.startswith("adm_cbv:") or
    c.data.startswith("adm_cbp:") or
    c.data.startswith("adm_cbt:") or
    c.data.startswith("adm_cbd:") or
    c.data.startswith("adm_bcol:") or
    c.data.startswith("adm_bdesign:") or
    c.data.startswith("adm_bren:") or
    c.data.startswith("adm_bemoji:") or
    c.data.startswith("adm_bstrip_em:") or
    c.data.startswith("adm_bvis:") or
    c.data.startswith("adm_breset:") or
    c.data.startswith("adm_emsg:") or
    c.data.startswith("adm_emsg_hist:") or
    c.data.startswith("adm_emsg_rb:") or
    c.data.startswith("adm_emsg_reset:") or
    c.data.startswith("adm_emsg_bmode:") or
    c.data.startswith("adm_emsg_badd:") or
    c.data.startswith("adm_emsg_bdel:")
))
@_guard("admin_ui_message_editors")
def handle_dynamic_ui_and_message_editors(call):
    if not require_unlocked_admin_session(call):
        return
    uid = str(call.from_user.id)
    uid = str(call.from_user.id)
    if call.data == "adm_adv_hub":
        # Part 1, Item 3: Separate Advanced Settings Hub rendered dynamically from `admin_advanced_settings`
        kb = build_dynamic_page_inline_keyboard("admin_advanced_settings", uid=uid, msg_key="admin_advanced_settings_msg")
        kb.row(make_btn("⚙️ সেটিংস ও কন্ট্রোল হাবে যান", callback_data="adm_settings_hub", style="primary"))
        safe_edit(call.message.chat.id, call.message.message_id, get_msg("admin_advanced_settings_msg"), reply_markup=kb, menu_id="admin_advanced_settings")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_btn_editor_hub":
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("📱 ইউজার সাইডের সকল বাটন তালিকা (১০টি/পেজ)", callback_data="adm_ball_list:user:0", style="success"))
        kb.row(make_btn("👑 অ্যাডমিন সাইডের সকল বাটন তালিকা (১০টি/পেজ)", callback_data="adm_ball_list:admin:0", style="primary"))
        kb.row(
            make_btn("➕ নতুন বাটন তৈরি (ইউজার সাইড)", callback_data="adm_cbn:user", style="success"),
            make_btn("➕ নতুন বাটন তৈরি (অ্যাডমিন সাইড)", callback_data="adm_cbn:admin", style="primary")
        )
        kb.row(make_btn("📂 তৈরি করা নতুন/কাস্টম বাটনসমূহ ও ভেতরের বাটন পরিচালনা", callback_data="adm_cbl", style="success"))
        kb.row(make_btn("📐 বাটনের অবস্থান ও পেজ পরিবর্তন করুন", callback_data="adm_bpos_hub", style="success"))
        kb.row(
            make_btn("🎨 ইউজার গ্লোবাল কালার থিম", callback_data="adm_set_theme:user", style="success"),
            make_btn("🎨 এডমিন গ্লোবাল কালার থিম", callback_data="adm_set_theme:admin", style="danger")
        )
        kb.row(
            make_btn("🔙 অ্যাডভান্সড সেটিংসে যান", callback_data="adm_adv_hub", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🎛️ <b>Button Name, Color &amp; Premium Custom Emoji Editor:</b>\n{FULL_WIDTH_DIVIDER}\n"
            "ইউজার সাইড এবং অ্যাডমিন সাইডের প্রতিটি বাটন (উপরের মেসেজ বক্স বাটন ও নিচের ইনলাইন/মেনু বাটন) এডিট করুন, কালার (সবুজ/লাল/নীল) পরিবর্তন করুন, প্রিমিয়াম কাস্টম ইমোজি যুক্ত করুন এবং যেকোনো পেজে স্থানান্তর করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_ball_list:"):
        # Paginated list of ALL User or Admin buttons (10 per page)
        parts = call.data.split(":")
        scope = parts[1] if len(parts) > 1 else "user"
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        per_p = 10
        prefix = "a_" if scope == "admin" else "u_"
        def_l_key = "admin_home" if scope == "admin" else "user_home"
        all_b_keys = [k for k in DEFAULT_BUTTON_LABELS.keys() if k.startswith(prefix)]
        p_meta = paginate_items(all_b_keys, page=page, per_page=per_p)

        kb = types.InlineKeyboardMarkup()
        for bk in p_meta["items"]:
            cur_l_key = find_button_current_layout(bk, def_l_key)
            sc = short_layout_code(cur_l_key)
            disp_lbl = apply_button_text_design(get_btn_raw_label(bk), get_btn_design(bk))
            kb.row(
                make_btn(
                    f"{disp_lbl} [{bk}]",
                    callback_data=f"adm_bitem:{bk}:{sc}",
                    style=get_btn_style(bk),
                    icon_custom_emoji_id=get_btn_emoji(bk),
                    btn_key=bk
                )
            )
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, f"adm_ball_list:{scope}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(make_btn("🔙 বাটন এডিটর হাবে ফিরে যান", callback_data="adm_btn_editor_hub", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🎛️ <b>{'অ্যাডমিন' if scope=='admin' else 'ইউজার'} প্যানেলের সকল বাটন তালিকা (পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']} — মোট {p_meta['total_items']}টি বাটন):</b>\n{FULL_WIDTH_DIVIDER}\n"
            "যেকোনো বাটনে ক্লিক করে নাম, ডিজাইন, কালার (Green/Red/Blue), প্রিমিয়াম ইমোজি বা যেকোনো পেজে অবস্থান পরিবর্তন করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_bpos_hub":
        # Part 1, Items 10–13: Button Position Change, Visual Drop Mover & Custom Container Hub
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("➕ নতুন বাটন তৈরি (ইউজার সাইড)", callback_data="adm_cbn:user", style="success"),
            make_btn("➕ নতুন বাটন তৈরি (অ্যাডমিন সাইড)", callback_data="adm_cbn:admin", style="primary")
        )
        kb.row(make_btn("📂 কাস্টম বাটনসমূহ ও ভেতরের বাটন সাজান", callback_data="adm_cbl", style="success"))
        for l_key in get_all_active_layout_keys():
            sc = short_layout_code(l_key)
            p_title = LAYOUT_PAGE_TITLES.get(l_key, l_key)
            btn_cnt = sum(len(r) for r in get_layout(l_key))
            kb.row(make_btn(f"{p_title} ({btn_cnt}টি বাটন)", callback_data=f"adm_elayout:{sc}", style="primary" if l_key.startswith("admin") else "success"))
        kb.row(
            make_btn("🔙 অ্যাডভান্সড সেটিংসে যান", callback_data="adm_adv_hub", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📐 <b>Button Position Change / বাটনের জায়গা পরিবর্তন করুন:</b>\n{FULL_WIDTH_DIVIDER}\n"
            "যেকোনো পেজ সিলেক্ট করে সেই পেজের বাটন ডানে, বামে, উপরে, নিচে, একই লাইনে বা আলাদা লাইনে সাজান অথবা এক পেজ থেকে যেকোনো পেজে বাটন স্থানান্তর করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_rlayout:"):
        raw_lk = call.data.split(":", 1)[1]
        l_key = resolve_layout_key(raw_lk)
        if l_key in DEFAULT_LAYOUTS:
            set_layout(l_key, json.loads(json.dumps(DEFAULT_LAYOUTS[l_key])))
            bot.answer_callback_query(call.id, "🔄 পেজের বাটন লেআউট ডিফল্টে রিসেট করা হয়েছে!", show_alert=True)
        call.data = f"adm_elayout:{short_layout_code(l_key)}"

    if call.data.startswith("adm_elayout:"):
        raw_lk = call.data.split(":", 1)[1]
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        layout = get_layout(l_key)
        p_title = LAYOUT_PAGE_TITLES.get(l_key, l_key)
        kb = types.InlineKeyboardMarkup()
        layout_preview_lines = []
        for r_idx, row in enumerate(layout, start=1):
            r_btns = []
            row_names = []
            for bk in row:
                disp_lbl = apply_button_text_design(get_btn_raw_label(bk), get_btn_design(bk))
                row_names.append(f"[{disp_lbl}]")
                r_btns.append(
                    make_btn(
                        disp_lbl,
                        callback_data=f"adm_bitem:{bk}:{sc}",
                        style=get_btn_style(bk),
                        icon_custom_emoji_id=get_btn_emoji(bk),
                        btn_key=bk
                    )
                )
            if r_btns:
                kb.row(*r_btns)
            if row_names:
                layout_preview_lines.append(f"Row {r_idx}: " + "  ".join(row_names))
        kb.row(
            make_btn("🔄 ডিফল্ট লেআউটে রিসেট", callback_data=f"adm_rlayout:{sc}", style="danger"),
            make_btn("📐 অন্য পেজ সিলেক্ট করুন", callback_data="adm_bpos_hub", style="primary")
        )
        kb.row(make_btn("🔙 অ্যাডভান্সড সেটিংসে ফিরে যান", callback_data="adm_adv_hub", style="danger"))
        preview_block = "\n".join(layout_preview_lines) if layout_preview_lines else "(কোনো বাটন নেই)"
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🎛️ <b>পেজ লেআউট ও লাইভ প্রিভিউ: {esc(p_title)}</b> (<code>{esc(l_key)}</code>)\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"👁️ <b>বর্তমান পেজ বাটন স্ট্রাকচার প্রিভিউ:</b>\n<code>{esc(preview_block)}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "👇 নিচের যেকোনো বাটনের উপর ক্লিক করে নাম, ডিজাইন, কালার, প্রিমিয়াম ইমোজি, অবস্থান বা পেজ পরিবর্তন করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_cbl":
        cbtns = get_all_custom_buttons()
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("➕ নতুন বাটন তৈরি (ইউজার সাইড)", callback_data="adm_cbn:user", style="success"),
            make_btn("➕ নতুন বাটন তৈরি (অ্যাডমিন সাইড)", callback_data="adm_cbn:admin", style="primary")
        )
        for cb_item in cbtns:
            bk = cb_item["btn_key"]
            side_lbl = "👑 অ্যাডমিন" if cb_item.get("side") == "admin" else "📱 ইউজার"
            child_cnt = sum(len(r) for r in get_layout(cb_item["layout_key"]))
            kb.row(
                make_btn(
                    f"📂 [{side_lbl}] {cb_item['label']} ({child_cnt}টি ভেতরের বাটন)",
                    callback_data=f"adm_cbv:{bk}",
                    style=cb_item.get("style", "primary"),
                    icon_custom_emoji_id=cb_item.get("custom_emoji_id") or None
                )
            )
        kb.row(
            make_btn("🎛️ বাটন এডিটর হাবে যান", callback_data="adm_btn_editor_hub", style="primary"),
            make_btn("🔙 অ্যাডভান্সড সেটিংসে যান", callback_data="adm_adv_hub", style="danger")
        )
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📂 <b>কাস্টম ফোল্ডার / কন্টেইনার বাটন ম্যানেজার (মোট {len(cbtns)}টি):</b>\n{FULL_WIDTH_DIVIDER}\n"
            "এখান থেকে ইউজার সাইড বা অ্যাডমিন সাইডে নতুন বাটন তৈরি করে তার ভেতরে যেকোনো কার্যকর বাটন (প্লে-স্টোর বা অ্যাপ ফোল্ডারের মতো) সাজিয়ে রাখতে পারবেন এবং উপরে কাস্টম স্ট্যাটাস মেসেজ সেট করতে পারবেন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbn:"):
        side = call.data.split(":", 1)[1].strip()
        if side not in ("user", "admin"):
            side = "user"
        default_parent = "admin_home" if side == "admin" else "user_home"
        existing_st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = existing_st.get("cbtn_key") if str(existing_st.get("cbtn_key", "")).startswith("cbtn_") else generate_unique_custom_button_id()
        user_memory_states[uid] = {
            "admin_action": "create_cbtn_name",
            "cbtn_key": cbtn_uid,
            "side": side,
            "parent_layout": existing_st.get("parent_layout") or default_parent,
            "destination_layout": existing_st.get("destination_layout") or f"custom_page_{cbtn_uid}",
            "parent_container_key": existing_st.get("parent_container_key") or "",
            "pos_mode": existing_st.get("pos_mode") or "bot",
            "row_index": int(existing_st.get("row_index", len(get_layout(default_parent))) or 0),
            "col_index": int(existing_st.get("col_index", 0) or 0),
            "label": existing_st.get("label") or "",
            "custom_emoji_id": existing_st.get("custom_emoji_id") or "",
            "status_msg": existing_st.get("status_msg") or "",
            "sub_buttons": list(existing_st.get("sub_buttons") or [])
        }
        kb = types.InlineKeyboardMarkup()
        # Allow switching Side, Parent Page, or Nested Container right here, OR typing the name immediately
        kb.row(
            make_btn(f"{'✅ ' if side=='user' else ''}📱 ইউজার সাইড", callback_data="adm_cbn:user", style="success"),
            make_btn(f"{'✅ ' if side=='admin' else ''}👑 অ্যাডমিন সাইড", callback_data="adm_cbn:admin", style="primary")
        )
        for cand_lk in get_all_active_layout_keys():
            is_cand_adm = cand_lk.startswith("admin")
            is_cand_cbtn = cand_lk.startswith("custom_page_")
            if not is_cand_cbtn and ((side == "admin" and not is_cand_adm) or (side == "user" and is_cand_adm)):
                continue
            sc_c = short_layout_code(cand_lk)
            p_t = LAYOUT_PAGE_TITLES.get(cand_lk, cand_lk)
            tag_c = "📂 Nested Container" if is_cand_cbtn else "📄 Parent Page"
            kb.row(
                make_btn(
                    f"📍 [{tag_c}] {p_t}-এ স্থান ও লাইন নির্বাচন করুন",
                    callback_data=f"adm_cbw_parent:{side}:{sc_c}",
                    style="primary" if is_cand_adm else "success"
                )
            )
        kb.row(make_btn("🔙 বাতিল করুন", callback_data="adm_cbl", style="danger"))
        safe_send(
            call.message.chat.id,
            f"➕ <b>নতুন কাস্টম বাটন তৈরি উইজার্ড ({'অ্যাডমিন সাইড' if side=='admin' else 'ইউজার সাইড'}):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• ইউনিক বাটন আইডি (UUID): <code>{esc(cbtn_uid)}</code>\n"
            f"• বর্তমান প্যারেন্ট পেজ: <b>{esc(LAYOUT_PAGE_TITLES.get(user_memory_states[uid]['parent_layout'], user_memory_states[uid]['parent_layout']))}</b>\n\n"
            "১️⃣ নিচের বাটন থেকে <b>Parent Page</b>, <b>Nested Container</b>, <b>Row</b> এবং <b>Position</b> নির্বাচন করতে পারেন; অথবা\n"
            "২️⃣ সরাসরি নতুন বাটনটির <b>নাম</b> লিখে পাঠান (সাথে যেকোনো <b>Telegram Premium Custom Emoji</b> যুক্ত করতে পারেন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbw_parent:"):
        _, side, p_sc = call.data.split(":", 2)
        parent_lk = resolve_layout_key(p_sc)
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        parent_container_k = parent_lk[len("custom_page_"):] if parent_lk.startswith("custom_page_") else ""
        p_rows = get_layout(parent_lk)
        st.update({
            "admin_action": "create_cbtn_name",
            "cbtn_key": cbtn_uid,
            "side": side,
            "parent_layout": parent_lk,
            "parent_container_key": parent_container_k,
            "row_index": len(p_rows),
            "col_index": 0,
            "pos_mode": "bot"
        })
        user_memory_states[uid] = st

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("📥 [একদম উপরে ১ম লাইনে (Row #1, Pos #1) বসান]", callback_data=f"adm_cbw_pos:{side}:{p_sc}:top:0:0", style="success"))
        for r_idx, row in enumerate(p_rows):
            row_lbls = ", ".join(get_btn_raw_label(k)[:14] for k in row)
            kb.row(
                make_btn(
                    f"📍 Row #{r_idx+1}-এর সাথে বসান (Pos #{len(row)+1}: {row_lbls[:24]})",
                    callback_data=f"adm_cbw_pos:{side}:{p_sc}:row:{r_idx}:{len(row)}",
                    style="primary"
                ),
                make_btn(
                    f"⬆️ Row #{r_idx+1}-এর আগে নতুন লাইন",
                    callback_data=f"adm_cbw_pos:{side}:{p_sc}:before:{r_idx}:0",
                    style="success"
                )
            )
        kb.row(make_btn(f"📥 [একদম নিচে নতুন লাইনে (Row #{len(p_rows)+1}, Pos #1) বসান]", callback_data=f"adm_cbw_pos:{side}:{p_sc}:bot:{len(p_rows)}:0", style="success"))
        kb.row(make_btn("🎯 Destination Page নির্বাচন করুন (ঐচ্ছিক)", callback_data=f"adm_cbw_dest:{side}:{p_sc}", style="primary"))
        kb.row(make_btn("🔙 আগের ধাপে ফিরে যান", callback_data=f"adm_cbn:{side}", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📐 <b>প্যারেন্ট পেজে লাইন (Row) ও পজিশন (Position) নির্বাচন করুন:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• নির্বাচিত প্যারেন্ট পেজ/কন্টেইনার: <b>{esc(LAYOUT_PAGE_TITLES.get(parent_lk, parent_lk))}</b>\n"
            f"• গন্তব্য পেজ (Destination): <code>{esc(st.get('destination_layout') or f'custom_page_{cbtn_uid}')}</code>\n\n"
            "👇 কোন লাইনে (Row) এবং কোন পজিশনে (Position) নতুন বাটনটি বসাতে চান তা সিলেক্ট করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbw_dest:"):
        _, side, p_sc = call.data.split(":", 2)
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                f"✅ নতুন নিজস্ব ফোল্ডার পেজ (custom_page_{cbtn_uid})",
                callback_data=f"adm_cbw_setdest:{side}:{p_sc}:own",
                style="success"
            )
        )
        for cand_lk in get_all_active_layout_keys():
            sc_c = short_layout_code(cand_lk)
            p_t = LAYOUT_PAGE_TITLES.get(cand_lk, cand_lk)
            kb.row(make_btn(f"🎯 {p_t} ({cand_lk})", callback_data=f"adm_cbw_setdest:{side}:{p_sc}:{sc_c}", style="primary"))
        kb.row(make_btn("🔙 ফিরে যান", callback_data=f"adm_cbw_parent:{side}:{p_sc}", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🎯 <b>Destination Page (বাটনে চাপ দিলে কোন পেজ খুলবে) নির্বাচন করুন:</b>\n{FULL_WIDTH_DIVIDER}\n"
            "ডিফল্টভাবে নতুন বাটনটির জন্য একটি স্বতন্ত্র কাস্টম পেজ তৈরি হয়, অথবা আপনি যেকোনো নির্দিষ্ট পেজ নির্বাচন করতে পারেন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbw_setdest:"):
        _, side, p_sc, dest_sc = call.data.split(":", 3)
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        st["destination_layout"] = f"custom_page_{cbtn_uid}" if dest_sc == "own" else resolve_layout_key(dest_sc)
        user_memory_states[uid] = st
        bot.answer_callback_query(call.id, f"✅ Destination Page সেট হয়েছে: {st['destination_layout']}")
        call.data = f"adm_cbw_parent:{side}:{p_sc}"
        return handle_dynamic_ui_and_message_editors(call)

    if call.data.startswith("adm_cbw_pos:"):
        _, side, p_sc, pos_mode, r_s, c_s = call.data.split(":", 5)
        parent_lk = resolve_layout_key(p_sc)
        r_idx = int(r_s) if r_s.isdigit() else 0
        c_idx = int(c_s) if c_s.isdigit() else 0
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        st.update({
            "admin_action": "create_cbtn_name",
            "cbtn_key": cbtn_uid,
            "side": side,
            "parent_layout": parent_lk,
            "parent_container_key": parent_lk[len("custom_page_"):] if parent_lk.startswith("custom_page_") else "",
            "pos_mode": pos_mode,
            "row_index": r_idx,
            "col_index": c_idx
        })
        user_memory_states[uid] = st
        if st.get("label"):
            _render_custom_button_final_preview(call.message.chat.id, uid, st, edit_message_id=call.message.message_id)
            bot.answer_callback_query(call.id, "✅ পজিশন আপডেট হয়েছে!")
            return
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 প্যারেন্ট পেজ পরিবর্তনে ফিরে যান", callback_data=f"adm_cbn:{side}", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"✅ <b>অবস্থান নির্ধারণ সম্পন্ন!</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• প্যারেন্ট পেজ: <b>{esc(LAYOUT_PAGE_TITLES.get(parent_lk, parent_lk))}</b>\n"
            f"• নির্ধারিত লাইন ও পজিশন: <b>Row #{r_idx+1}, Position #{c_idx+1} ({esc(pos_mode.upper())})</b>\n\n"
            "✍️ এখন নতুন বাটনটির <b>নাম</b> লিখে পাঠান (সাথে যেকোনো <b>Telegram Premium Custom Emoji</b> বা ইমোজি যুক্ত করতে পারেন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_cbw_skip_msg":
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        lbl = st.get("label") or "কাস্টম বাটন"
        st["status_msg"] = f"📂 <b>{esc(lbl)}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের অপশনগুলো থেকে আপনার কাঙ্ক্ষিত বাটন নির্বাচন করুন:"
        st["admin_action"] = "create_cbtn_preview"
        user_memory_states[uid] = st
        call.data = f"adm_cbw_pick:{st.get('side', 'user')}:0"

    if call.data.startswith("adm_cbw_tog:"):
        _, target_k, scope, pg_s = call.data.split(":", 3)
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        dest_lk = st.get("destination_layout") or f"custom_page_{cbtn_uid}"
        sub_list = list(st.get("sub_buttons") or [])
        if target_k in sub_list:
            sub_list.remove(target_k)
            bot.answer_callback_query(call.id, f"➖ '{get_btn_raw_label(target_k)}' তালিকা থেকে সরানো হয়েছে।")
        else:
            with db_lock:
                conn_cy = get_connection()
                is_cyc = would_create_container_cycle(target_k, dest_lk, conn=conn_cy)
                conn_cy.close()
            if is_cyc or target_k == cbtn_uid:
                bot.answer_callback_query(call.id, "⛔ Circular Reference প্রতিরোধ করা হয়েছে: এই কন্টেইনারটি ভেতরে নেওয়া যাবে না!", show_alert=True)
            else:
                sub_list.append(target_k)
                bot.answer_callback_query(call.id, f"✅ '{get_btn_raw_label(target_k)}' সাব-বাটন হিসেবে নির্বাচিত হয়েছে!")
        st["sub_buttons"] = sub_list
        user_memory_states[uid] = st
        call.data = f"adm_cbw_pick:{scope}:{pg_s}"

    if call.data.startswith("adm_cbw_pick:"):
        _, scope, pg_s = call.data.split(":", 2)
        page = int(pg_s) if pg_s.isdigit() else 0
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        cbtn_uid = st.get("cbtn_key") or generate_unique_custom_button_id()
        sub_set = set(st.get("sub_buttons") or [])
        prefix = "a_" if scope == "admin" else "u_"
        cand_keys = [k for k in DEFAULT_BUTTON_LABELS.keys() if (k.startswith(prefix) or k.startswith("cbtn_")) and k != cbtn_uid]
        p_meta = paginate_items(cand_keys, page=page, per_page=10)
        kb = types.InlineKeyboardMarkup()
        for ck in p_meta["items"]:
            mark = "✅ [নির্বাচিত]" if ck in sub_set else "⬜ [যুক্ত করুন]"
            st_c = "success" if ck in sub_set else "primary"
            kb.row(make_btn(f"{mark} {get_btn_raw_label(ck)}", callback_data=f"adm_cbw_tog:{ck}:{scope}:{p_meta['page']}", style=st_c))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], 10, f"adm_cbw_pick:{scope}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(
            make_btn("📱 ইউজার বাটন দেখুন", callback_data="adm_cbw_pick:user:0", style="success"),
            make_btn("👑 অ্যাডমিন বাটন দেখুন", callback_data="adm_cbw_pick:admin:0", style="primary")
        )
        kb.row(make_btn(f"👁️ Final Preview & Confirm ({len(sub_set)}টি সাব-বাটন)", callback_data="adm_cbw_prev", style="success"))
        kb.row(make_btn("❌ বাতিল করুন", callback_data="adm_cbl", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📲 <b>নতুন বাটন '{esc(st.get('label', cbtn_uid))}'-এর ভেতরে সাব-বাটন বা নেস্টেড বাটন নির্বাচন করুন:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• নির্বাচিত সাব-বাটন সংখ্যা: <b>{len(sub_set)}টি</b>\n"
            "👇 যেকোনো বাটনে ট্যাপ করে নির্বাচন শেষ হলে নিচের <b>👁️ Final Preview &amp; Confirm</b> বাটনে ক্লিক করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_cbw_prev":
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        if not st.get("label"):
            bot.answer_callback_query(call.id, "⚠️ আগে বাটনের নাম প্রদান করুন!", show_alert=True)
            return
        _render_custom_button_final_preview(call.message.chat.id, uid, st, edit_message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_cbw_confirm":
        st = user_memory_states.get(uid) if isinstance(user_memory_states.get(uid), dict) else {}
        if not st or not st.get("label"):
            bot.answer_callback_query(call.id, "⚠️ কনফার্ম করার মতো কোনো পেন্ডিং কাস্টম বাটন পাওয়া যায়নি!", show_alert=True)
            return
        cbtn_key = st.get("cbtn_key") or generate_unique_custom_button_id()
        side = st.get("side", "user")
        parent_lk = resolve_layout_key(st.get("parent_layout") or ("admin_home" if side == "admin" else "user_home"))
        dest_lk = resolve_layout_key(st.get("destination_layout") or f"custom_page_{cbtn_key}")
        parent_cont = st.get("parent_container_key") or (parent_lk[len("custom_page_"):] if parent_lk.startswith("custom_page_") else "")
        pos_mode = st.get("pos_mode", "bot")
        r_idx = int(st.get("row_index", 0) or 0)
        c_idx = int(st.get("col_index", 0) or 0)
        if pos_mode == "top":
            r_idx, c_idx = 0, 0
        elif pos_mode == "bot":
            r_idx, c_idx = len(get_layout(parent_lk)), 0
        lbl = st["label"]
        em_id = st.get("custom_emoji_id", "")
        status_msg = st.get("status_msg") or f"📂 <b>{esc(lbl)}</b>\n{FULL_WIDTH_DIVIDER}\nনিচের অপশনগুলো থেকে আপনার কাঙ্ক্ষিত বাটন নির্বাচন করুন:"
        raw_msg_txt = st.get("raw_status_msg") or lbl
        msg_ents = st.get("status_msg_entities")
        sub_btns = list(st.get("sub_buttons") or [])

        try:
            with db_lock:
                conn = get_connection()
                try:
                    tx_res = create_custom_button_transactional(
                        side=side,
                        parent_layout=parent_lk,
                        label=lbl,
                        style="success" if side == "user" else "primary",
                        design_style="normal",
                        custom_emoji_id=em_id,
                        msg_content=status_msg,
                        raw_msg_text=raw_msg_txt,
                        msg_entities=msg_ents,
                        destination_layout=dest_lk,
                        row_index=r_idx,
                        col_index=c_idx,
                        parent_container_key=parent_cont,
                        sub_button_keys=sub_btns,
                        btn_key=cbtn_key,
                        updated_by=uid,
                        conn=conn
                    )
                finally:
                    conn.close()
        except Exception as exc:
            bot.answer_callback_query(call.id, f"⚠️ বাটন তৈরিতে সমস্যা হয়েছে: {str(exc)[:120]}", show_alert=True)
            return

        cbtn_key = tx_res["btn_key"]
        user_memory_states.pop(uid, None)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, f"🎉 '{lbl}' বাটনটি Database Transaction-এর মাধ্যমে সফলভাবে যুক্ত হয়েছে!", show_alert=True)
        call.data = f"adm_cbv:{cbtn_key}"

    if call.data.startswith("adm_cbv:"):
        bk = call.data.split(":", 1)[1].strip()
        cb_rec = get_custom_button(bk)
        if not cb_rec:
            bot.answer_callback_query(call.id, "বাটনটি পাওয়া যায়নি!", show_alert=True)
            return
        l_key = cb_rec.get("destination_layout") or cb_rec["layout_key"]
        m_key = cb_rec["msg_key"]
        locs = locate_button_across_all_layouts(bk)
        parent_lk = (locs[0]["layout_key"] if locs else cb_rec.get("parent_layout")) or ("admin_home" if cb_rec.get("side") == "admin" else "user_home")
        sc = short_layout_code(l_key)
        p_sc = short_layout_code(parent_lk)
        child_rows = get_layout(l_key)
        child_names = [get_btn_raw_label(k) for r in child_rows for k in r]
        child_summary = ", ".join(child_names) if child_names else "(এখনো কোনো বাটন ভেতরে রাখা হয়নি)"
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                f"👁️ প্রিভিউ ও ওপেন করুন: {cb_rec['label']}",
                callback_data=f"cbtn_open:{bk}",
                style=get_btn_style(bk),
                icon_custom_emoji_id=get_btn_emoji(bk) or None
            )
        )
        kb.row(
            make_btn("📲 ভেতরে ইউজার/কাস্টম বাটন যুক্ত বা রিমুভ", callback_data=f"adm_cbp:{bk}:user:0", style="success"),
            make_btn("👑 ভেতরে অ্যাডমিন/কাস্টম বাটন যুক্ত বা রিমুভ", callback_data=f"adm_cbp:{bk}:admin:0", style="primary")
        )
        kb.row(
            make_btn("📐 ভেতরের বাটনগুলোর লাইন/অবস্থান সাজান", callback_data=f"adm_elayout:{sc}", style="success"),
            make_btn("✏️ উপরের স্ট্যাটাস মেসেজ এডিট করুন", callback_data=f"adm_emsg:{m_key}", style="primary")
        )
        kb.row(
            make_btn("🎛️ এই বাটনের নাম/কালার/ইমোজি/স্থান বদলান", callback_data=f"adm_bitem:{bk}:{p_sc}", style="primary"),
            make_btn("🗑️ এই কাস্টম বাটনটি মুছে ফেলুন", callback_data=f"adm_cbd:{bk}", style="danger")
        )
        kb.row(make_btn("🔙 কাস্টম বাটন তালিকায় ফিরে যান", callback_data="adm_cbl", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📂 <b>কাস্টম বাটন কন্ট্রোল প্যানেল: {esc(cb_rec['label'])}</b> (<code>{esc(bk)}</code>)\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• বর্তমান অবস্থান (Current Parent Page): <b>{esc(LAYOUT_PAGE_TITLES.get(parent_lk, parent_lk))}</b>\n"
            f"• ভেতরে রাখা কার্যকর বাটনসমূহ ({len(child_names)}টি): <b>{esc(child_summary)}</b>\n"
            f"• উপরের স্ট্যাটাস মেসেজ টেমপ্লেট: <code>{esc(m_key)}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "👇 নিচের অপশন থেকে এই বাটনের ভেতরে কোন কোন বাটন বা নেস্টেড ফোল্ডার রাখতে চান তা সিলেক্ট করুন অথবা স্ট্যাটাস মেসেজ ও ডিজাইন কাস্টমাইজ করুন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbt:"):
        # Toggle a functional or nested custom button inside custom button `bk`
        _, bk, target_k, scope, pg_s = call.data.split(":", 4)
        cb_rec = get_custom_button(bk)
        if cb_rec:
            l_key = cb_rec.get("destination_layout") or cb_rec["layout_key"]
            cur_rows = [list(r) for r in get_layout(l_key) if isinstance(r, list)]
            already_in = any(target_k in r for r in cur_rows)
            if already_in:
                # Restore `target_k` back to the EXACT original layout, row_index, and col_index it was taken from!
                with db_lock:
                    conn = get_connection()
                    try:
                        rest_res = restore_button_to_original_placement(target_k, from_container_layout=l_key, conn=conn)
                    finally:
                        conn.close()
                sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
                rest_lk = rest_res.get("restored_to_layout", "user_home")
                bot.answer_callback_query(
                    call.id,
                    f"➖ '{get_btn_raw_label(target_k)}' বাটনটি সরিয়ে তার পূর্বের মূল জায়গায় ({LAYOUT_PAGE_TITLES.get(rest_lk, rest_lk)}, Row #{int(rest_res.get('restored_row_index', 0))+1}) ফিরিয়ে দেওয়া হয়েছে!"
                )
            else:
                with db_lock:
                    conn_chk = get_connection()
                    has_cycle = would_create_container_cycle(target_k, l_key, conn=conn_chk)
                    conn_chk.close()
                if has_cycle:
                    bot.answer_callback_query(
                        call.id,
                        "⛔ Circular Reference প্রতিরোধ করা হয়েছে: একটি ফোল্ডারকে তার নিজের বা সাব-ফোল্ডারের ভেতরে ঢোকানো যাবে না!",
                        show_alert=True
                    )
                else:
                    src_lk = find_button_current_layout(target_k, "admin_home" if target_k.startswith("a_") else "user_home")
                    move_button_across_pages(src_lk, l_key, target_k, drop_mode="bot")
                    bot.answer_callback_query(call.id, f"✅ '{get_btn_raw_label(target_k)}' বাটনটি '{cb_rec['label']}'-এর ভেতরে রাখা হয়েছে!")
        call.data = f"adm_cbp:{bk}:{scope}:{pg_s}"

    if call.data.startswith("adm_cbp:"):
        # Play Store / Folder Style Functional & Nested Custom Button Selector for Custom Button `bk`
        _, bk, scope, pg_s = call.data.split(":", 3)
        page = int(pg_s) if pg_s.isdigit() else 0
        cb_rec = get_custom_button(bk)
        if not cb_rec:
            bot.answer_callback_query(call.id, "কাস্টম বাটনটি পাওয়া যায়নি!", show_alert=True)
            return
        l_key = cb_rec.get("destination_layout") or cb_rec["layout_key"]
        cur_rows = get_layout(l_key)
        inside_set = {k for r in cur_rows for k in r}
        prefix = "a_" if scope == "admin" else "u_"
        cand_keys = [
            k for k in DEFAULT_BUTTON_LABELS.keys()
            if (k.startswith(prefix) or k.startswith("cbtn_")) and k != bk and not k.endswith("_direct")
        ]
        p_meta = paginate_items(cand_keys, page=page, per_page=10)
        kb = types.InlineKeyboardMarkup()
        for ck in p_meta["items"]:
            mark = "✅ [ভেতরে আছে]" if ck in inside_set else "⬜ [ভেতরে নিন]"
            st_c = "success" if ck in inside_set else "primary"
            folder_tag = "📂 " if ck.startswith("cbtn_") else ""
            kb.row(make_btn(f"{mark} {folder_tag}{get_btn_raw_label(ck)}", callback_data=f"adm_cbt:{bk}:{ck}:{scope}:{p_meta['page']}", style=st_c))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], 10, f"adm_cbp:{bk}:{scope}")
        if nav_row:
            kb.row(*nav_row)
        kb.row(
            make_btn("📱 ইউজার ও কাস্টম বাটন দেখুন", callback_data=f"adm_cbp:{bk}:user:0", style="success"),
            make_btn("👑 অ্যাডমিন ও কাস্টম বাটন দেখুন", callback_data=f"adm_cbp:{bk}:admin:0", style="primary")
        )
        kb.row(make_btn("🔙 কাস্টম বাটন কন্ট্রোলে ফিরে যান", callback_data=f"adm_cbv:{bk}", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📲 <b>'{esc(cb_rec['label'])}' বাটনের ভেতরে কার্যকর বাটন বা নেস্টেড ফোল্ডার যোগ/রিমুভ করুন (পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']}):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "যেকোনো বাটনে ট্যাপ করলে সেটি এই বাটনের ভেতরে চলে আসবে (আবার ট্যাপ করলে বের হয়ে ঠিক যে জায়গা থেকে নেওয়া হয়েছিল সেই মূল স্থানে ফিরে যাবে):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_cbd:"):
        bk = call.data.split(":", 1)[1].strip()
        cb_rec = get_custom_button(bk)
        if cb_rec:
            with db_lock:
                conn = get_connection()
                try:
                    del_res = delete_custom_button_transactional(bk, conn=conn)
                finally:
                    conn.close()
            sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
            rest_cnt = len(del_res.get("restored_buttons") or [])
            bot.answer_callback_query(
                call.id,
                f"🗑️ কাস্টম বাটনটি মুছে ফেলা হয়েছে এবং ভেতরের {rest_cnt}টি বাটন তাদের পূর্বের মূল অবস্থানে ফিরিয়ে দেওয়া হয়েছে!",
                show_alert=True
            )
        call.data = "adm_cbl"
        return handle_dynamic_ui_and_message_editors(call)

    if call.data.startswith("adm_bmp:") or call.data.startswith("adm_bmove_page_pick:"):
        # Interactive Visual Page & Container Picker: choose which page or button to move `b_key` into!
        _, raw_from_lk, b_key = call.data.split(":", 2)
        from_l_key = find_button_current_layout(b_key, resolve_layout_key(raw_from_lk))
        from_sc = short_layout_code(from_l_key)
        kb = types.InlineKeyboardMarkup()
        b_is_adm = b_key.startswith("a_") or (b_key.startswith("cbtn_") and (get_custom_button(b_key) or {}).get("side") == "admin")
        for cand_l_key in get_all_active_layout_keys():
            cand_is_adm = cand_l_key.startswith("admin") or (cand_l_key.startswith("custom_page_") and (get_custom_button(cand_l_key[len("custom_page_"):]) or {}).get("side") == "admin")
            if b_is_adm != cand_is_adm:
                continue
            cand_sc = short_layout_code(cand_l_key)
            p_title = LAYOUT_PAGE_TITLES.get(cand_l_key, cand_l_key)
            side_tag = "👑 অ্যাডমিন" if cand_is_adm else ("📂 কাস্টম বাটন" if cand_l_key.startswith("custom_page_") else "📱 ইউজার")
            btn_st = "primary" if cand_is_adm else "success"
            cur_tag = " (বর্তমান পেজ)" if cand_l_key == from_l_key else ""
            kb.row(
                make_btn(
                    f"📍 [{side_tag}] {p_title}{cur_tag}-এ জায়গা বেছে নিন",
                    callback_data=f"adm_bdp:{from_sc}:{cand_sc}:{b_key}",
                    style=btn_st
                )
            )
        kb.row(make_btn("🔙 বাটন কাস্টমাইজারে ফিরে যান", callback_data=f"adm_bitem:{b_key}:{from_sc}", style="danger"))
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"📤 <b>বাটনের জায়গা পরিবর্তন বা অন্য বাটনের ভেতরে স্থানান্তর করুন:</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"• নির্বাচিত বাটন: <b>{esc(get_btn_raw_label(b_key))}</b> (<code>{esc(b_key)}</code>)\n"
            f"• বর্তমান পেজ: <b>{esc(LAYOUT_PAGE_TITLES.get(from_l_key, from_l_key))}</b>\n\n"
            "👇 কোন পেজে বা কোন কাস্টম বাটনের ভেতরে এটি নিয়ে বসাতে চান তা সিলেক্ট করুন। পেজ সিলেক্ট করলে সেই পেজের বাটনগুলো নরমালি দেখাবে এবং আপনি ঠিক কোন জায়গায় বা কোন বাটনের ভেতরে মুভ করে ছাড়তে চান তার বাটন পাবেন:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_bdp:"):
        # Interactive Visual Drop View on Target Page: shows the target page's normal layout with
        # `📥 এখানে বাটনটি মুভ করে বসান` at top/rows/bottom AND `📂 এই বাটনের ভেতরে ঢুকিয়ে রাখুন` on each button!
        _, from_sc, to_sc, b_key = call.data.split(":", 3)
        from_l_key = resolve_layout_key(from_sc)
        to_l_key = resolve_layout_key(to_sc)
        p_title = LAYOUT_PAGE_TITLES.get(to_l_key, to_l_key)
        moving_lbl = get_btn_raw_label(b_key)
        target_rows = get_layout(to_l_key)

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"📥 [একদম উপরে ১ম লাইনে '{moving_lbl}' মুভ করে বসান]", callback_data=f"adm_bde:{from_sc}:{to_sc}:{b_key}:top:0", style="success"))
        for r_idx, row in enumerate(target_rows):
            # Show existing buttons in this row normally so the admin sees the exact visual layout
            normal_row_btns = []
            for tk in row:
                t_lbl = apply_button_text_design(get_btn_raw_label(tk), get_btn_design(tk))
                normal_row_btns.append(
                    make_btn(
                        f"🔘 {t_lbl}",
                        callback_data=f"adm_bdi:{from_sc}:{tk}:{b_key}",
                        style=get_btn_style(tk),
                        icon_custom_emoji_id=get_btn_emoji(tk) or None
                    )
                )
            if normal_row_btns:
                kb.row(*normal_row_btns)
            # Action row right below: drop in same line or put inside button
            act_row = [
                make_btn(f"📍 লাইন #{r_idx+1}-এর সাথে বসান", callback_data=f"adm_bde:{from_sc}:{to_sc}:{b_key}:row:{r_idx}", style="primary")
            ]
            if row and row[0] != b_key:
                first_tk = row[0]
                act_row.append(
                    make_btn(f"📂 '{get_btn_raw_label(first_tk)[:14]}'-এর ভেতরে ঢোকান", callback_data=f"adm_bdi:{from_sc}:{first_tk}:{b_key}", style="success")
                )
            kb.row(*act_row)

        kb.row(make_btn(f"📥 [একদম নিচে নতুন লাইনে '{moving_lbl}' মুভ করে বসান]", callback_data=f"adm_bde:{from_sc}:{to_sc}:{b_key}:bot:0", style="success"))
        kb.row(
            make_btn("🔙 অন্য পেজ বেছে নিন", callback_data=f"adm_bmp:{from_sc}:{b_key}", style="primary"),
            make_btn("🔙 বাটন কাস্টমাইজারে যান", callback_data=f"adm_bitem:{b_key}:{from_sc}", style="danger")
        )
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🎯 <b>কোথায় '{esc(moving_lbl)}' বাটনটি মুভ করে বসাতে চান?</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• গন্তব্য পেজ: <b>{esc(p_title)}</b>\n"
            f"• মুভ হতে যাওয়া বাটন: <b>{esc(moving_lbl)}</b>\n\n"
            "💡 <b>নির্দেশনা:</b>\n"
            "১. নিচে পেজের বাটনগুলো নরমালি যেভাবে থাকে ঠিক সেভাবেই দেখাচ্ছে।\n"
            "২. <b>📥 উপরে/নিচে মুভ করে বসান</b> বা <b>📍 লাইন #X-এর সাথে বসান</b> বাটনে চাপ দিলে ঠিক সেই জায়গায় বাটনটি বসে যাবে।\n"
            "৩. কোনো বাটনের উপর বা <b>📂 ভেতরে ঢোকান</b> বাটনে চাপ দিলে ওই বাটনের ভেতরে এই বাটনটি ঢুকে যাবে!",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_bde:"):
        _, from_sc, to_sc, b_key, drop_mode, r_idx_s = call.data.split(":", 5)
        from_l_key = resolve_layout_key(from_sc)
        to_l_key = resolve_layout_key(to_sc)
        r_idx = int(r_idx_s) if r_idx_s.isdigit() else 0
        mv_res = move_button_across_pages(from_l_key, to_l_key, b_key, drop_mode=drop_mode, row_index=r_idx)
        if not mv_res.get("ok"):
            bot.answer_callback_query(call.id, mv_res.get("reason", "স্থানান্তর ব্যর্থ!"), show_alert=True)
            return
        bot.answer_callback_query(
            call.id,
            f"✅ '{get_btn_raw_label(b_key)}' সফলভাবে {LAYOUT_PAGE_TITLES.get(to_l_key, to_l_key)}-এর নির্ধারিত জায়গায় বসানো হয়েছে!",
            show_alert=True
        )
        call.data = f"adm_elayout:{short_layout_code(to_l_key)}"
        return handle_dynamic_ui_and_message_editors(call)

    if call.data.startswith("adm_bdi:"):
        _, from_sc, target_bk, b_key = call.data.split(":", 3)
        from_l_key = resolve_layout_key(from_sc)
        mv_res = move_button_into_target_button(from_l_key, target_bk, b_key)
        if not mv_res.get("ok"):
            bot.answer_callback_query(call.id, mv_res.get("reason", "স্থানান্তর ব্যর্থ!"), show_alert=True)
            return
        dest_lk = mv_res.get("to_layout_key", "user_home")
        bot.answer_callback_query(
            call.id,
            f"✅ '{get_btn_raw_label(b_key)}' বাটনটি সফলভাবে '{get_btn_raw_label(target_bk)}' বাটনের ভেতরে রাখা হয়েছে!",
            show_alert=True
        )
        call.data = f"adm_elayout:{short_layout_code(dest_lk)}"
        return handle_dynamic_ui_and_message_editors(call)

    if call.data.startswith("adm_bme:") or call.data.startswith("adm_bmove_page_exec:"):
        _, raw_from_lk, raw_to_lk, b_key = call.data.split(":", 3)
        from_l_key = resolve_layout_key(raw_from_lk)
        to_l_key = resolve_layout_key(raw_to_lk)
        mv_res = move_button_across_pages(from_l_key, to_l_key, b_key)
        if not mv_res.get("ok"):
            bot.answer_callback_query(call.id, mv_res.get("reason", "স্থানান্তর ব্যর্থ!"), show_alert=True)
            return
        bot.answer_callback_query(
            call.id,
            f"✅ বাটনটি সফলভাবে {LAYOUT_PAGE_TITLES.get(to_l_key, to_l_key)}-এ স্থানান্তর করা হয়েছে!",
            show_alert=True
        )
        call.data = f"adm_elayout:{short_layout_code(to_l_key)}"
        return handle_dynamic_ui_and_message_editors(call)

    if call.data.startswith("adm_bdesign:"):
        _, b_key, raw_lk, d_style = call.data.split(":", 3)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        set_btn_design_val(b_key, d_style)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, f"✨ বাটনের লেখার ডিজাইন '{BUTTON_TEXT_DESIGN_STYLES.get(d_style, d_style)}' সেট করা হয়েছে!")
        call.data = f"adm_bitem:{b_key}:{sc}"

    if call.data.startswith("adm_bstrip_em:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        cur_raw = get_btn_raw_label(b_key)
        stripped_lbl = strip_leading_default_emojis(cur_raw)
        set_btn_label_val(b_key, stripped_lbl)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, f"✅ নরমাল/ডিফল্ট ইমোজি সরানো হয়েছে: '{stripped_lbl}'")
        call.data = f"adm_bitem:{b_key}:{sc}"

    if call.data.startswith("adm_bvis:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        new_vis = not get_btn_visibility(b_key)
        set_btn_visibility_val(b_key, new_vis)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, f"✅ বাটন ভিজিবিলিটি: {'দৃশ্যমান (Visible)' if new_vis else 'লুকানো (Hidden)'}")
        call.data = f"adm_bitem:{b_key}:{sc}"

    if call.data.startswith("adm_brestore_norm_em:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        def_lbl = DEFAULT_BUTTON_LABELS.get(b_key, "")
        def_em = extract_leading_default_emojis(def_lbl)
        cur_stripped = strip_leading_default_emojis(get_btn_raw_label(b_key))
        restored_lbl = f"{def_em} {cur_stripped}".strip() if def_em else (def_lbl or cur_stripped)
        set_btn_emoji_val(b_key, "")
        set_btn_label_val(b_key, restored_lbl)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, f"✅ নরমাল ডিফল্ট ইমোজি ফিরিয়ে আনা হয়েছে: '{restored_lbl}'")
        call.data = f"adm_bitem:{b_key}:{sc}"

    if call.data.startswith("adm_breset:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        reset_single_button_to_default(b_key)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, "🔄 বাটনটি ডিফল্ট কনফিগারেশনে রিসেট করা হয়েছে!")
        call.data = f"adm_bitem:{b_key}:{sc}"

    if call.data.startswith("adm_bitem:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = find_button_current_layout(b_key, resolve_layout_key(raw_lk))
        sc = short_layout_code(l_key)
        raw_lbl = get_btn_raw_label(b_key)
        cur_des = get_btn_design(b_key)
        styled_lbl = apply_button_text_design(raw_lbl, cur_des)
        cur_em = get_btn_emoji(b_key) or "None"
        cur_col = get_btn_style(b_key)

        kb = types.InlineKeyboardMarkup()
        # Top row: Live Interactive Preview Button!
        kb.row(
            make_btn(
                f"👁️ প্রিভিউ: {styled_lbl}",
                callback_data=f"adm_bitem:{b_key}:{sc}",
                style=cur_col,
                icon_custom_emoji_id=(cur_em if cur_em != "None" else None),
                btn_key=b_key,
                design_style="normal"
            )
        )
        # Single unified button for Button Name (including bold/stylish text) & Premium Custom Emoji / Sticker!
        kb.row(
            make_btn("✏️✨ বাটনের নাম ও প্রিমিয়াম কাস্টম ইমোজি সেট করুন", callback_data=f"adm_bren:{b_key}:{sc}", style="success")
        )
        kb.row(
            make_btn("🧹 নরমাল ইমোজি সরান", callback_data=f"adm_bstrip_em:{b_key}:{sc}", style="primary"),
            make_btn("🔄 নরমাল ডিফল্ট ইমোজি", callback_data=f"adm_brestore_norm_em:{b_key}:{sc}", style="success")
        )
        kb.row(
            make_btn("🔄 ডিফল্ট বাটনে রিসেট করুন", callback_data=f"adm_breset:{b_key}:{sc}", style="danger")
        )
        # Position controls
        kb.row(make_btn("⬆️ উপরে নিন", callback_data=f"adm_bmove:{sc}:{b_key}:up", style="success"), make_btn("⬇️ নিচে নিন", callback_data=f"adm_bmove:{sc}:{b_key}:down", style="success"))
        kb.row(make_btn("⬅️ বামে নিন", callback_data=f"adm_bmove:{sc}:{b_key}:left", style="primary"), make_btn("➡️ ডানে নিন", callback_data=f"adm_bmove:{sc}:{b_key}:right", style="primary"))
        kb.row(make_btn("↗️ একই লাইনে যুক্ত করুন", callback_data=f"adm_bmove:{sc}:{b_key}:join_up", style="success"), make_btn("⤵️ আলাদা লাইনে নামান", callback_data=f"adm_bmove:{sc}:{b_key}:split_row", style="danger"))
        kb.row(make_btn("📤 অন্য পেজে বা বাটনের ভেতরে নিন", callback_data=f"adm_bmp:{sc}:{b_key}", style="primary"))
        kb.row(
            make_btn("🟢 সবুজ (Green)", callback_data=f"adm_bcol:{b_key}:{sc}:success", style="success"),
            make_btn("🔴 লাল (Red)", callback_data=f"adm_bcol:{b_key}:{sc}:danger", style="danger"),
            make_btn("🔵 নীল (Blue)", callback_data=f"adm_bcol:{b_key}:{sc}:primary", style="primary")
        )
        kb.row(
            make_btn("📐 পেজ লেআউটে যান", callback_data=f"adm_elayout:{sc}", style="primary"),
            make_btn("🔙 বাটন তালিকায় ফিরে যান", callback_data=f"adm_ball_list:{'admin' if b_key.startswith('a_') else 'user'}:0", style="primary")
        )
        kb.row(
            make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger")
        )
        rich_preview_disp = (
            f'<tg-emoji emoji-id="{cur_em}">{_resolve_custom_emoji_fallback_char(cur_em, "❤️")}</tg-emoji> <b>{esc(styled_lbl)}</b>'
            if cur_em != "None" else f"<b>{esc(styled_lbl)}</b>"
        )
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"🔘 <b>বাটন কাস্টমাইজার ও লাইভ প্রিভিউ:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• Button Key: <code>{esc(b_key)}</code>\n"
            f"• বর্তমান পেজ: <b>{esc(LAYOUT_PAGE_TITLES.get(l_key, l_key))}</b>\n"
            f"• মূল নাম (Raw Text): <b>{esc(raw_lbl)}</b>\n"
            f"• লেখার ডিজাইন (Style): <b>{esc(BUTTON_TEXT_DESIGN_STYLES.get(cur_des, cur_des))}</b>\n"
            f"• বর্তমান লাইভ প্রিভিউ: {rich_preview_disp}\n"
            f"• বাটন কালার (উপরে ও নিচে উভয় মেনুতে): <b>{esc(cur_col)}</b>\n"
            f"• Custom Emoji ID: <code>{esc(cur_em)}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "💡 <i>উপরের প্রথম বাটনটিতে বাটনের বর্তমান লাইভ প্রিভিউ দেখা যাচ্ছে। এই কালার ও কাস্টম ইমোজি উপরের বাটন এবং নিচের ইনলাইন/মেনু বাটন—উভয় স্থানেই একসাথে কাজ করবে!</i>",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_bmove:"):
        _, raw_lk, b_key, direction = call.data.split(":", 3)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        updated = move_button_in_layout(get_layout(l_key), b_key, direction)
        set_layout(l_key, updated)
        bot.answer_callback_query(call.id, "✅ বাটনের স্থান পরিবর্তন হয়েছে! নিচে প্রিভিউ দেখুন।")
        call.data = f"adm_elayout:{sc}"
        handle_dynamic_ui_and_message_editors(call)
        return

    if call.data.startswith("adm_bcol:"):
        _, b_key, raw_lk, col = call.data.split(":", 3)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        BUTTON_RUNTIME_CAPS["allow_style"] = True
        set_btn_style(b_key, col)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=call.message.chat.id)
        with db_lock:
            conn_c = get_connection()
            with conn_c:
                conn_c.execute("UPDATE users SET user_btn_style = '' WHERE user_id = ?", (uid,))
            conn_c.close()
        bot.answer_callback_query(call.id, "✅ বাটনের কালার (উপরের ও নিচের উভয় মেনুতে) আপডেট হয়েছে!")
        call.data = f"adm_bitem:{b_key}:{sc}"
        handle_dynamic_ui_and_message_editors(call)
        return

    if call.data.startswith("adm_bren:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        cur_lbl = get_btn_raw_label(b_key)
        user_memory_states[uid] = {"admin_action": "rename_btn", "b_key": b_key, "l_key": l_key}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 বাটন কাস্টমাইজারে ফিরে যান", callback_data=f"adm_bitem:{b_key}:{sc}", style="danger"))
        safe_send(
            call.message.chat.id,
            f"✍️ <b>বাটনের নাম পরিবর্তন ও প্রিভিউ:</b> (<code>{esc(b_key)}</code>)\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"📋 <b>বর্তমান নাম (কপি করতে ট্যাপ করুন):</b>\n<code>{esc(cur_lbl)}</code>\n\n"
            "👇 এখন বাটনের নতুন নাম লিখে পাঠান (সাথে যেকোনো Telegram Premium Custom Emoji বা ইমোজি যুক্ত করতে পারেন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_bemoji:"):
        _, b_key, raw_lk = call.data.split(":", 2)
        l_key = resolve_layout_key(raw_lk)
        sc = short_layout_code(l_key)
        user_memory_states[uid] = {"admin_action": "set_btn_emoji", "b_key": b_key, "l_key": l_key}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 বাটন কাস্টমাইজারে ফিরে যান", callback_data=f"adm_bitem:{b_key}:{sc}", style="danger"))
        safe_send(
            call.message.chat.id,
            f"✨ <b>{esc(get_btn_raw_label(b_key))}</b> বাটনের জন্য একটি <b>Telegram Premium Custom Emoji / Live Sticker</b> পাঠান অথবা সরাসরি সংখ্যার <code>custom_emoji_id</code> লিখে পাঠান (মুছে ফেলতে <code>none</code> লিখুন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_lb_style:"):
        st_choice = call.data.split(":", 1)[1].strip()
        if st_choice in BUTTON_TEXT_DESIGN_STYLES:
            set_setting("leaderboard_name_style", st_choice)
            bot.answer_callback_query(call.id, f"✅ লিডারবোর্ডে ইউজারের নামের স্টাইল '{BUTTON_TEXT_DESIGN_STYLES[st_choice]}' সেট করা হয়েছে!")
        call.data = "adm_lb_customizer"

    if call.data.startswith("adm_lb_rank:"):
        rk_num = int(call.data.split(":", 1)[1])
        cur_b = get_setting(f"leaderboard_rank_{rk_num}_badge", f"#{rk_num} Top {rk_num}")
        user_memory_states[uid] = {"admin_action": "set_lb_rank_badge", "rank_num": rk_num}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 লিডারবোর্ড কাস্টমাইজারে ফিরে যান", callback_data="adm_lb_customizer", style="danger"))
        safe_send(
            call.message.chat.id,
            f"🏆 <b>লিডারবোর্ড Top #{rk_num} র‍্যাঙ্ক ব্যাজ ও কাস্টম ইমোজি পরিবর্তন:</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• বর্তমান ব্যাজ: {cur_b}\n\n"
            "✍️ এখন নতুন র‍্যাঙ্ক লেবেল / ব্যাজ লিখে পাঠান (যেকোনো <b>Telegram Premium Custom Emoji</b> এবং বোল্ড/স্টাইলিশ ফন্ট ব্যবহার করতে পারবেন):",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_lb_customizer":
        cur_st = get_setting("leaderboard_name_style", "bold_sans") or "bold_sans"
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("✏️ লিডারবোর্ড মেইন মেসেজ টেমপ্লেট এডিট করুন", callback_data="adm_emsg:leaderboard_msg", style="success"))
        kb.row(
            make_btn(f"{'✅ ' if cur_st=='normal' else ''}Normal Name", callback_data="adm_lb_style:normal", style="primary"),
            make_btn(f"{'✅ ' if cur_st=='bold_sans' else ''}𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀", callback_data="adm_lb_style:bold_sans", style="success"),
            make_btn(f"{'✅ ' if cur_st=='bold_serif' else ''}𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟", callback_data="adm_lb_style:bold_serif", style="primary")
        )
        kb.row(
            make_btn(f"{'✅ ' if cur_st=='bracket' else ''}【Bracket】", callback_data="adm_lb_style:bracket", style="primary"),
            make_btn(f"{'✅ ' if cur_st=='star' else ''}✦ Star ✦", callback_data="adm_lb_style:star", style="success"),
            make_btn(f"{'✅ ' if cur_st=='diamond' else ''}❖ Diamond ❖", callback_data="adm_lb_style:diamond", style="primary")
        )
        medals_def = ["🥇 Top 1", "🥈 Top 2", "🥉 Top 3", "4️⃣ Top 4", "5️⃣ Top 5", "6️⃣ Top 6", "7️⃣ Top 7", "8️⃣ Top 8", "9️⃣ Top 9", "🔟 Top 10"]
        preview_ranks = []
        for r_i in range(1, 11, 2):
            b1 = strip_tg_emoji_tags(get_setting(f"leaderboard_rank_{r_i}_badge", medals_def[r_i-1]))
            b2 = strip_tg_emoji_tags(get_setting(f"leaderboard_rank_{r_i+1}_badge", medals_def[r_i]))
            kb.row(
                make_btn(f"✏️ #{r_i}: {b1[:18]}", callback_data=f"adm_lb_rank:{r_i}", style="success" if r_i <= 3 else "primary"),
                make_btn(f"✏️ #{r_i+1}: {b2[:18]}", callback_data=f"adm_lb_rank:{r_i+1}", style="success" if (r_i+1) <= 3 else "primary")
            )
        for r_i in range(1, 11):
            b_html = get_setting(f"leaderboard_rank_{r_i}_badge", medals_def[r_i-1])
            preview_ranks.append(f"• Rank #{r_i}: {b_html}")
        kb.row(
            make_btn("🔙 অ্যাডভান্সড সেটিংসে ফিরে যান", callback_data="adm_adv_hub", style="primary"),
            make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger")
        )
        sample_name = apply_button_text_design("Monir Ahmed", cur_st)
        safe_edit(
            call.message.chat.id,
            call.message.message_id,
            f"🏆 <b>লিডারবোর্ড কাস্টমাইজার (Top 1–10 র‍্যাঙ্ক ব্যাজ ও ইউজার নামের ফন্ট স্টাইল):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• ইউজারের নামের বর্তমান স্টাইল: <b>{esc(BUTTON_TEXT_DESIGN_STYLES.get(cur_st, cur_st))}</b> (উদাহরণ: <b>{esc(sample_name)}</b>)\n"
            f"• নোট: লিডারবোর্ডে কখনোই @username দেখানো হবে না; শুধুমাত্র ইউজারের নাম দেখানো হবে।\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            + "\n".join(preview_ranks),
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_msg_hub" or call.data.startswith("adm_msg_page:"):
        page = int(call.data.split(":", 1)[1]) if ":" in call.data else 0
        per_p = 10
        with db_lock:
            conn = get_connection()
            existing_keys = [r["msg_key"] for r in conn.execute("SELECT msg_key FROM dynamic_messages ORDER BY msg_key").fetchall()]
            conn.close()
        all_keys = list(dict.fromkeys(list(DEFAULT_MESSAGES.keys()) + existing_keys))
        p_meta = paginate_items(all_keys, page=page, per_page=per_p)

        kb = types.InlineKeyboardMarkup()
        for mk in p_meta["items"]:
            title = MESSAGE_TEMPLATE_LABELS.get(mk, "✏️ " + mk.replace("_", " ").strip().title())
            kb.row(make_btn(title, callback_data=f"adm_emsg:{mk}", style="primary"))
        nav_row = build_pagination_row(p_meta["page"], p_meta["total_items"], per_p, "adm_msg_page")
        if nav_row:
            kb.row(*nav_row)
        kb.row(
            make_btn("🔙 অ্যাডভান্সড সেটিংসে ফিরে যান", callback_data="adm_adv_hub", style="primary"),
            make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger")
        )
        safe_edit(
            call.message.chat.id, call.message.message_id,
            f"✏️ <b>Message, Status &amp; Premium Custom Emoji Editor (পৃষ্ঠা {p_meta['page']+1}/{p_meta['total_pages']} — মোট {p_meta['total_items']}টি মেসেজ)</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "প্রয়োজনীয় মেসেজ টেমপ্লেট বেছে নিন। ক্লিক করলে বর্তমান মেসেজটি সম্পূর্ণভাবে সামনে আসবে—সেটি কপি করে Premium Custom Emoji দিয়ে সাজিয়ে পাঠালে লাইভ প্রিভিউসহ সাথে সাথে সেভ হবে:",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_emsg_reset:"):
        mk = call.data.split(":", 1)[1]
        def_content = DEFAULT_MESSAGES.get(mk, "")
        if def_content:
            set_msg(mk, def_content, raw_text=def_content, entities=[], updated_by=uid)
        bot.answer_callback_query(call.id, "🔄 মেসেজটি ডিফল্ট টেমপ্লেটে রিসেট করা হয়েছে!", show_alert=True)
        call.data = f"adm_emsg:{mk}"

    if call.data.startswith("adm_emsg_rb:"):
        _, mk, hid_s = call.data.split(":")
        with db_lock:
            rb_res = rollback_dynamic_message(mk, int(hid_s), actor_id=uid)
        if rb_res.get("ok"):
            CACHE_MESSAGES[mk] = rb_res["content"]
            bot.answer_callback_query(call.id, "♻️ পূর্ববর্তী ভার্সন সফলভাবে রোলব্যাক ও রিস্টোর হয়েছে!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, rb_res.get("reason", "রোলব্যাক ব্যর্থ!"), show_alert=True)
        call.data = f"adm_emsg:{mk}"

    if call.data.startswith("adm_emsg_hist:"):
        mk = call.data.split(":", 1)[1]
        with db_lock:
            h_list = get_dynamic_message_history(mk, limit=8)
        kb = types.InlineKeyboardMarkup()
        lines = [f"📜 <b>পূর্বে কী মেসেজ সেট করা ছিল ও রোলব্যাক</b> (<code>{esc(mk)}</code>):\n{FULL_WIDTH_DIVIDER}"]
        for h_item in h_list:
            kb.row(make_btn(f"♻️ পূর্বের মেসেজটি রিস্টোর করুন ({h_item['saved_at']})", callback_data=f"adm_emsg_rb:{mk}:{h_item['id']}", style="success"))
        if not h_list:
            lines.append("📭 এই টেমপ্লেটের কোনো পূর্ববর্তী কাস্টম ভার্সন নেই (বর্তমানে ডিফল্ট মেসেজ সেট করা আছে)।")
        kb.row(make_btn("🔙 মেসেজ এডিট ভিউতে ফিরে যান", callback_data=f"adm_emsg:{mk}", style="danger"))
        safe_edit(call.message.chat.id, call.message.message_id, "\n\n".join(lines), reply_markup=kb)
        if h_list:
            safe_send(call.message.chat.id, h_list[0]["content"])
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_emsg_bmode:"):
        _, mk, b_mode = call.data.split(":", 2)
        b_mode = b_mode.strip().lower()
        if b_mode not in ("default", "custom", "none"):
            b_mode = "default"
        with db_lock:
            set_dynamic_message_button_config(mk, button_mode=b_mode, updated_by=uid)
        CACHE_MESSAGE_BUTTON_MODES[mk] = b_mode
        mode_lbl = {"default": "ডিফল্ট বাটন (Default)", "none": "বাটন ছাড়া মেসেজ (Buttonless)", "custom": "কাস্টম বাটন (Custom Buttons)"}.get(b_mode, b_mode)
        bot.answer_callback_query(call.id, f"✅ মেসেজ বাটন মোড সেট হয়েছে: {mode_lbl}")
        call.data = f"adm_emsg:{mk}"

    if call.data.startswith("adm_emsg_bdel:"):
        mk = call.data.split(":", 1)[1]
        with db_lock:
            set_dynamic_message_button_config(mk, button_mode="default", custom_buttons=[], updated_by=uid)
        CACHE_MESSAGE_BUTTON_MODES[mk] = "default"
        CACHE_MESSAGE_CUSTOM_BUTTONS[mk] = []
        bot.answer_callback_query(call.id, "🗑️ এই মেসেজের কাস্টম বাটন মুছে ডিফল্ট করা হয়েছে!")
        call.data = f"adm_emsg:{mk}"

    if call.data.startswith("adm_emsg_badd:"):
        mk = call.data.split(":", 1)[1]
        user_memory_states[uid] = {"admin_action": "add_msg_custom_btn", "msg_key": mk}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 মেসেজ এডিটরে ফিরে যান", callback_data=f"adm_emsg:{mk}", style="danger"))
        safe_send(
            call.message.chat.id,
            f"➕ <b>মেসেজের নিচে কাস্টম বাটন যুক্ত করুন</b> (<code>{esc(mk)}</code>):\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "নিচের ফরম্যাটে বাটনের তথ্য লিখে পাঠান (এক বা একাধিক লাইনে):\n"
            "<code>বাটনের নাম | লিংক বা Callback বা ButtonKey | কালার (success/danger/primary)</code>\n\n"
            "📌 <b>উদাহরণ ১ (লিংক বাটন):</b>\n"
            "<code>📢 অফিশিয়াল চ্যানেল | https://t.me/battleclubcreator | success</code>\n"
            "📌 <b>উদাহরণ ২ (বট পেজ বাটন):</b>\n"
            "<code>📊 ড্যাশবোর্ডে যান | u_dashboard | primary</code>\n"
            "💡 সাথে যেকোনো <b>Telegram Premium Custom Emoji</b> ব্যবহার করলে সেটিও বাটনে যুক্ত হয়ে যাবে!",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("adm_emsg:"):
        mk = call.data.split(":", 1)[1]
        user_memory_states[uid] = {"admin_action": "save_custom_msg", "msg_key": mk}
        cur_txt = get_msg(mk)
        rec = get_dynamic_message_record(mk)
        has_prev = bool(str(rec.get("prev_content") or "").strip())
        cur_bmode = CACHE_MESSAGE_BUTTON_MODES.get(mk, rec.get("button_mode", "default"))
        cur_cbtns = CACHE_MESSAGE_CUSTOM_BUTTONS.get(mk, rec.get("custom_buttons", []))
        cbtn_cnt = sum(len(r) for r in (cur_cbtns or []) if isinstance(r, list))
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(f"📜 আগে কী মেসেজ ছিল দেখুন {'(Available)' if has_prev else ''}", callback_data=f"adm_emsg_hist:{mk}", style="primary"),
            make_btn("🔄 ডিফল্টে রিসেট করুন", callback_data=f"adm_emsg_reset:{mk}", style="danger")
        )
        kb.row(
            make_btn(f"{'✅ ' if cur_bmode == 'default' else ''}🔘 ডিফল্ট বাটন মোড", callback_data=f"adm_emsg_bmode:{mk}:default", style="success" if cur_bmode == "default" else "primary"),
            make_btn(f"{'✅ ' if cur_bmode == 'none' else ''}🚫 বাটন ছাড়া মেসেজ (No Button)", callback_data=f"adm_emsg_bmode:{mk}:none", style="danger" if cur_bmode == "none" else "primary")
        )
        kb.row(
            make_btn(f"➕ মেসেজের নিচে কাস্টম বাটন যুক্ত করুন ({cbtn_cnt}টি)", callback_data=f"adm_emsg_badd:{mk}", style="success"),
            make_btn("🗑️ কাস্টম বাটন মুছুন", callback_data=f"adm_emsg_bdel:{mk}", style="danger")
        )
        kb.row(make_btn("🔙 মেসেজ তালিকায় ফিরে যান", callback_data="adm_msg_hub", style="danger"))
        safe_send(
            call.message.chat.id,
            f"✏️ <b>মেসেজ ও প্রিমিয়াম ইমোজি এডিটর</b> (<code>{esc(mk)}</code>):\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• বর্তমান বাটন মোড: <b>{esc(cur_bmode.upper())}</b> (সংযুক্ত কাস্টম বাটন: <b>{cbtn_cnt}টি</b>)\n"
            "⬇️ <b>নিচে বর্তমানে বটে দেখানো সম্পূর্ণ মেসেজটি হুবহু কপি/ফরওয়ার্ড করার জন্য পাঠানো হয়েছে।</b>\n"
            "📋 আপনি নিচের মেসেজটি কপি করে আপনার পছন্দমতো <b>Premium Custom Emoji</b> ও লেখায় সাজিয়ে পাঠান—পাঠানোর সাথে সাথেই নতুন মেসেজ সেভ হবে এবং <b>লাইভ প্রিভিউ (Live Preview)</b> দেখানো হবে!",
            reply_markup=kb
        )
        safe_send(call.message.chat.id, cur_txt)
        bot.answer_callback_query(call.id)


# ==============================================================================
# MASTER MESSAGE INPUT HANDLER & BOTTOM MENU TEXT ROUTER
# ==============================================================================
def _match_bottom_menu_button_action(uid: str, u: dict, txt: str) -> dict:
    """
    Matches incoming text against:
    1) The user's active sub-page or main-page Bottom Keyboard map (`USER_ACTIVE_BOTTOM_BUTTON_MAP[uid]`),
       supporting disambiguated duplicate button labels (`Label [2]`, `Label [3]`) so duplicate labels
       never overwrite each other's callbacks!
    2) Global User/Admin/Custom button labels (`GLOBAL_BUTTON_CALLBACK_MAP`), including admin buttons with dynamic count suffixes.
    Returns `{"callback_data": ..., "url": ..., "from_active_map": bool}` or `{}`.
    """
    clean_t = str(txt or "").strip()
    if not clean_t:
        return {}
    uid_s = str(uid or "").strip()

    # 1. Check active sub-page / current-page bottom keyboard map first (exact match including `[2]`, `[3]`)
    active_map = USER_ACTIVE_BOTTOM_BUTTON_MAP.get(uid_s) or {}
    if clean_t in active_map and isinstance(active_map[clean_t], dict):
        item = active_map[clean_t]
        return {
            "callback_data": item.get("callback_data"),
            "url": item.get("url"),
            "btn_key": item.get("btn_key"),
            "from_active_map": True
        }

    # Check if `clean_t` has a `[N]` duplicate index suffix matching `__multi__:<base_label>`
    m_dup = re.match(r"^(.*?)\s*\[(\d+)\]$", clean_t)
    if m_dup:
        base_lbl = m_dup.group(1).strip()
        dup_idx = int(m_dup.group(2)) - 1
        multi_list = active_map.get(f"__multi__:{base_lbl}")
        if isinstance(multi_list, list) and 0 <= dup_idx < len(multi_list):
            item = multi_list[dup_idx]
            return {
                "callback_data": item.get("callback_data"),
                "url": item.get("url"),
                "btn_key": item.get("btn_key"),
                "from_active_map": True
            }

    if clean_t == "👑 সুপার এডমিন প্যানেল" and is_authorized_admin(uid_s):
        return {"callback_data": "admin_hub", "url": None, "from_active_map": True}

    stripped_cnt_t = re.sub(r"\s*\(\d+\)\s*$", "", clean_t).strip()
    u_lang = (u.get("language", "bn") if u else "bn") or "bn"
    sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
    grp_url = get_setting("group_link", "https://t.me/battleclubcreator")

    matched_keys = []
    for k in DEFAULT_BUTTON_LABELS.keys():
        raw_l = get_btn_raw_label(k, lang=u_lang)
        des_l = apply_button_text_design(raw_l, get_btn_design(k))
        candidates = (raw_l, des_l, DEFAULT_BUTTON_LABELS.get(k, ""), DEFAULT_BUTTON_LABELS_EN.get(k, ""))
        if clean_t in candidates or stripped_cnt_t in candidates or (m_dup and m_dup.group(1).strip() in candidates):
            if k.startswith("a_") and not is_authorized_admin(uid_s):
                continue
            matched_keys.append(k)

    if matched_keys:
        chosen_k = matched_keys[0]
        if m_dup and len(matched_keys) >= int(m_dup.group(2)):
            chosen_k = matched_keys[int(m_dup.group(2)) - 1]
        if chosen_k == "u_support":
            return {"callback_data": None, "url": sup_url, "from_active_map": False}
        if chosen_k == "u_group":
            return {"callback_data": None, "url": grp_url, "from_active_map": False}
        cb = GLOBAL_BUTTON_CALLBACK_MAP.get(chosen_k)
        if cb:
            return {"callback_data": cb, "url": None, "btn_key": chosen_k, "from_active_map": False}
    return {}


def _dispatch_synthetic_callback(syn_c):
    """Routes a synthetic callback object from a Bottom Menu button press to its exact callback handler."""
    cb = str(getattr(syn_c, "data", "") or "")
    if not cb:
        return
    # 1. Check real pyTelegramBotAPI callback_query_handlers if present
    handlers = getattr(bot, "callback_query_handlers", None) or []
    for h in handlers:
        try:
            flt = h.get("filters", {}).get("func") if isinstance(h, dict) else getattr(h, "filters", {}).get("func")
            fn = h.get("function") if isinstance(h, dict) else getattr(h, "function", None)
            if callable(flt) and callable(fn) and flt(syn_c):
                return fn(syn_c)
        except Exception:
            continue

    # 2. Check offline test _FallbackTeleBot callback_handlers if present
    fb_handlers = getattr(bot, "callback_handlers", None) or []
    for h in fb_handlers:
        try:
            flt = h.get("func")
            fn = h.get("handler")
            if callable(flt) and callable(fn) and flt(syn_c):
                return fn(syn_c)
        except Exception:
            continue

    # 3. Direct fallback routing table
    if cb.startswith("umenu:"):
        return handle_user_menu_callbacks(syn_c)
    if cb in ("uprof_name_menu", "uprof_wd_num_menu") or cb.startswith("uprof_edit:"):
        return handle_user_profile_edit_prompt(syn_c)
    if cb.startswith("umyvid_plat:") or cb.startswith("umyvid_acc:"):
        return handle_my_videos_hierarchy(syn_c)
    if cb.startswith("upay_wd:") or cb.startswith("upay_plat:") or cb.startswith("upay_ledger:"):
        return handle_user_payment_list_subviews(syn_c)
    if cb.startswith("usub_plat:") or cb.startswith("usub_acc:"):
        return handle_video_submit_start(syn_c)
    if cb.startswith("ulink_act:"):
        return handle_link_more_platform_start(syn_c)
    if cb.startswith("uwd_method:") or cb.startswith("uwd_fast_dest:") or cb == "uwd_other_go" or cb.startswith("uwd_other_plat:"):
        return handle_withdraw_method_pick(syn_c)
    if cb.startswith("uset_color:"):
        return handle_user_color_set(syn_c)
    if cb in ("udel_step2", "uconfirm_del_acc") or cb.startswith("uman_code_prompt:") or cb.startswith("umyvid_item:") or cb.startswith("u_refresh_vid:"):
        return handle_user_delete_and_manual_code_actions(syn_c)
    if cb.startswith("reg_pay_toggle:") or cb == "reg_pay_confirm":
        return handle_onboarding_payment_selection(syn_c)
    if cb.startswith("reg_toggle:") or cb == "reg_confirm_selection":
        return handle_onboarding_selection(syn_c)
    if cb == "u_unfreeze_req" or cb.startswith("u_recheck_vcode:"):
        return handle_unfreeze_request(syn_c)
    if cb.startswith("cbtn_open:"):
        return handle_custom_container_button_open(syn_c)
    if cb in ("admin_hub", "adm_view_metrics", "adm_logout", "adm_toggle_bottom_menu"):
        return handle_admin_master_dashboard(syn_c)
    if cb.startswith("adm_vsec") or cb.startswith("adm_perm_") or cb.startswith("adm_vrej_") or cb.startswith("adm_vrereview:") or cb.startswith("adm_trash_move:"):
        return handle_admin_video_approval_sections(syn_c)
    if cb.startswith("adm_ulist:") or cb == "adm_usearch":
        return handle_admin_user_list(syn_c)
    if cb.startswith(("adm_uview:", "adm_ustat_menu:", "adm_uset_st:", "adm_udel_", "adm_uimp:", "adm_upwd:", "adm_ubal:", "adm_uact_log:", "adm_uedit_info:", "adm_uref_hist:")):
        return handle_admin_user_profile_control(syn_c)
    if cb.startswith(("adm_uvplat:", "adm_vitem:", "adm_vdecision:", "vd:", "adm_all_vids:")):
        return handle_admin_user_and_all_videos(syn_c)
    if cb == "adm_wd_reports_hub" or cb.startswith(("adm_uwd_hub:", "adm_wd_")):
        return handle_admin_wd_reports_system(syn_c)
    if cb.startswith("adm_fin_history:") or cb.startswith("adm_audit_history:"):
        return handle_admin_financial_history(syn_c)
    if cb.startswith("adm_trash"):
        return handle_admin_trash_system(syn_c)
    if cb.startswith(("adm_traffic:", "adm_tr_item:", "ext_act:")):
        return handle_admin_traffic_and_external_links(syn_c)
    if cb in ("adm_adv_hub", "adm_btn_editor_hub", "adm_msg_hub", "adm_bpos_hub", "adm_cbl", "adm_cbw_prev", "adm_cbw_confirm", "adm_cbw_skip_msg") or cb.startswith((
        "adm_ball_list:", "adm_msg_page:", "adm_elayout:", "adm_rlayout:", "adm_bitem:",
        "adm_bmove:", "adm_bmp:", "adm_bdp:", "adm_bde:", "adm_bdi:", "adm_bme:", "adm_cbn:", "adm_cbw_", "adm_cbv:", "adm_cbp:", "adm_cbt:", "adm_cbd:", "adm_bmove_page_pick:", "adm_bmove_page_exec:",
        "adm_bcol:", "adm_bdesign:", "adm_bren:", "adm_bemoji:", "adm_bstrip_em:", "adm_brestore_norm_em:", "adm_bvis:", "adm_breset:", "adm_emsg", "adm_lb_"
    )):
        return handle_dynamic_ui_and_message_editors(syn_c)
    return handle_admin_settings_and_limits(syn_c)


@bot.message_handler(func=lambda m: True, content_types=['text', 'sticker', 'photo', 'video', 'audio', 'voice', 'document', 'animation', 'video_note'])
def handle_all_incoming_messages(message):
    uid = str(message.from_user.id)
    txt = (message.text or "").strip()
    u = ensure_user(message.from_user)
    st_peek = user_memory_states.get(uid) or {}
    if st_peek.get("admin_action") != "broadcast_msg":
        cleanup_user_ui_messages(message.chat.id, uid, min_age_sec=0.05)
        if getattr(message, "message_id", None) and (st_peek.get("step") or st_peek.get("admin_action")):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass

    if is_authorized_admin(message.from_user) and (
        st_peek.get("step") == "awaiting_admin_password"
        or (txt and verify_admin_secret(txt, ADMIN_PASSWORD))
    ):
        allowed_adm_rl, retry_adm_s = check_rate_limit(uid, "admin_login", max_calls=5, window_sec=60)
        if not allowed_adm_rl:
            safe_send(message.chat.id, f"⏳ অতিরিক্ত ভুল চেষ্টা! অনুগ্রহ করে {int(retry_adm_s)} সেকেন্ড পর আবার চেষ্টা করুন।")
            return
        if get_failed_login_count(f"admin:{uid}") >= 5:
            safe_send(message.chat.id, "🔒 অতিরিক্ত ভুল পাসওয়ার্ডের কারণে অ্যাডমিন লগইন সাময়িক লক করা হয়েছে! কিছুক্ষণ পর চেষ্টা করুন।")
            return
        if txt and verify_admin_secret(txt, ADMIN_PASSWORD):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass
            ttl_sec = max(60, int(get_setting("admin_session_timeout_sec", "3600") or 3600))
            unlock_admin_session(uid, ttl_sec=ttl_sec)
            admin_unlocked_sessions[uid] = time.time()
            reset_failed_login(f"admin:{uid}")
            pending_cb = str(st_peek.get("pending_admin_cb") or "").strip()
            user_memory_states.pop(uid, None)
            with db_lock:
                conn = get_connection()
                with conn:
                    log_audit_event(uid, "Admin Panel Unlock", "Unlocked Super Admin Panel", target_user_id=uid, conn=conn)
                conn.close()
            safe_send(message.chat.id, get_msg("admin_welcome_msg"), reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
            if pending_cb and pending_cb.startswith(("adm", "vd:", "ext_act:")) and pending_cb != "admin_hub":
                try:
                    class _SynUnlockMsg:
                        def __init__(self, chat_obj):
                            self.chat = chat_obj
                            self.message_id = None
                    class _SynUnlockCall:
                        def __init__(self, u_obj, msg_obj, data_str):
                            self.id = f"cmd_{int(time.time()*1000)}"
                            self.from_user = u_obj
                            self.message = msg_obj
                            self.data = data_str
                    _dispatch_synthetic_callback(_SynUnlockCall(message.from_user, _SynUnlockMsg(message.chat), pending_cb))
                except Exception:
                    pass
            return
        else:
            fail_adm_cnt = record_failed_login(f"admin:{uid}")
            safe_send(
                message.chat.id,
                f"❌ <b>ভুল অ্যাডমিন পাসওয়ার্ড! ({fail_adm_cnt}/5)</b>\nসুপার অ্যাডমিন প্যানেলে প্রবেশ করতে সঠিক গোপন অ্যাডমিন পাসওয়ার্ড লিখে পাঠান:"
            )
            return

    st = user_memory_states.get(uid, {})

    # Check if the user/admin clicked a navigation/action button on their active Bottom Menu
    _adm_editing_ui = bool(
        is_authorized_admin(message.from_user)
        and st.get("admin_action") in ("rename_btn", "set_btn_emoji", "save_custom_msg", "add_msg_custom_btn", "create_cbtn_name", "create_cbtn_msg", "broadcast_msg")
        and not (getattr(message, "entities", None) is None and txt in ("🔙 হোমপেজে ফিরে যান (Back to Home)", "🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান"))
    )
    if txt and not _adm_editing_ui:
        bm_match = _match_bottom_menu_button_action(uid, u, txt)
        if bm_match and (bm_match.get("from_active_map") or (not st.get("step") and not st.get("admin_action"))):
            if bm_match.get("url"):
                safe_send(
                    message.chat.id,
                    f"🔗 <b>{esc(txt)}:</b>\n👉 <a href=\"{html.escape(bm_match['url'])}\">{esc(bm_match['url'])}</a>",
                    disable_preview=False
                )
                return
            matched_cb = bm_match.get("callback_data")
            if matched_cb:
                if matched_cb.startswith(("adm_", "vd:", "ext_act:", "admin_hub")):
                    if not require_unlocked_admin_session(message):
                        return

                class _SyntheticBottomMsg:
                    def __init__(self, chat_obj):
                        self.chat = chat_obj
                        self.message_id = None

                class _SyntheticMenuCall:
                    def __init__(self, u_obj, msg_obj, data_str):
                        self.id = f"cmd_{int(time.time()*1000)}"
                        self.from_user = u_obj
                        self.message = msg_obj
                        self.data = data_str

                syn_c = _SyntheticMenuCall(message.from_user, _SyntheticBottomMsg(message.chat), matched_cb)
                _dispatch_synthetic_callback(syn_c)
                return

    if is_authorized_admin(message.from_user) and st.get("admin_action"):
        if not require_unlocked_admin_session(message):
            return
        process_admin_text_input(message, st)
        return

    if u.get("status") == "banned" and not is_authorized_admin(uid):
        safe_send(message.chat.id, get_msg("ch_banned_msg"))
        return
    # Note: Inactive users can do everything except Withdraw; Frozen users can do everything except Withdraw & Video Submit!
    is_froz_msg = bool(int(u.get("bio_frozen") or 0) == 1 or str(u.get("status") or "").lower() == "frozen")
    is_inact_msg = bool(str(u.get("status") or "").lower() == "inactive" and not is_froz_msg)
    if is_froz_msg and st.get("step") in ("awaiting_video_link", "awaiting_wd_amount", "awaiting_wd_phone", "awaiting_wd_other_method_name", "awaiting_wd_other_dest", "awaiting_wd_other_amount"):
        user_memory_states.pop(uid, None)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔄 বায়ো ও ভিডিও কোড রি-চেক এবং আনফ্রিজ করুন", callback_data="u_unfreeze_req", style="success"))
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_send(message.chat.id, get_msg("ch_frozen_msg"), reply_markup=kb)
        return
    if is_inact_msg and st.get("step") in ("awaiting_wd_amount", "awaiting_wd_phone", "awaiting_wd_other_method_name", "awaiting_wd_other_dest", "awaiting_wd_other_amount"):
        user_memory_states.pop(uid, None)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("💬 অফিসিয়াল সাপোর্টে যোগাযোগ করুন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
        kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_send(message.chat.id, get_msg("ch_inactive_msg"), reply_markup=kb)
        return



    if st.get("step") == "awaiting_session_password":
        allowed_login, retry_s = check_rate_limit(uid, "session_login", max_calls=8, window_sec=30)
        if not allowed_login:
            safe_send(message.chat.id, f"⏳ অতিরিক্ত ভুল চেষ্টা! অনুগ্রহ করে {retry_s} সেকেন্ড পর আবার চেষ্টা করুন।")
            return
        pwd_saved = u.get("password_plain", "")
        if verify_password(u.get("password_hash", ""), txt) or (pwd_saved and txt == pwd_saved):
            clear_failed_login_attempts(uid)
            new_hash = u.get("password_hash", "")
            if not new_hash or not new_hash.startswith("pbkdf2_sha256$"):
                new_hash = hash_password(txt)
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute(
                        "UPDATE users SET password_hash = ?, password_plain = '', session_logged_out = 0, timeout_notified = 0, last_active_ts = ?, login_count = COALESCE(login_count, 0) + 1 WHERE user_id = ?",
                        (new_hash, time.time(), uid)
                    )
                    log_audit_event(uid, "Session Login", "Unlocked dashboard with password", target_user_id=uid, conn=conn)
                conn.close()
            user_memory_states.pop(uid, None)
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass
            safe_send(message.chat.id, "✅ <b>পাসওয়ার্ড সঠিক! আপনার ড্যাশবোর্ড আনলক হয়েছে।</b>")
            top_yt = get_setting("home_youtube_link", "")
            u_fresh = get_user(uid)
            safe_send(
                message.chat.id,
                attach_top_youtube_preview(get_msg("welcome_msg", name=esc(u_fresh.get("name")), balance=f"{float(u_fresh.get('balance', 0)):.2f}", user_id=uid), top_yt),
                reply_markup=build_user_home_keyboard(uid, u_fresh),
                top_yt_url=top_yt,
                menu_id="user_home"
            )
        else:
            fail_cnt = record_failed_login_attempt(uid)
            if fail_cnt >= 4:
                sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
                kb = types.InlineKeyboardMarkup()
                kb.row(make_btn("💬 সরাসরি অ্যাডমিনের সাথে কথা বলে পাসওয়ার্ড চেঞ্জ করুন", url=sup_url, style="danger"))
                safe_send(
                    message.chat.id,
                    get_msg("login_failed_support_msg", attempt_count=fail_cnt, support_link=esc(sup_url)),
                    reply_markup=kb
                )
            else:
                safe_send(message.chat.id, f"❌ <b>ভুল পাসওয়ার্ড ({fail_cnt}/5)!</b> সঠিক পাসওয়ার্ডটি লিখে পাঠান:")
        return



    if st.get("step") == "awaiting_profile_edit_random_code":
        field = st.get("field", "bkash_number")
        field_labels = {
            "bkash_number": "🌸 বিকাশ (bKash) নাম্বার",
            "nagad_number": "🍊 নগদ (Nagad) নাম্বার",
            "rocket_number": "🚀 রকেট (Rocket) নাম্বার",
            "channel_name": "📺 চ্যানেল / প্রোফাইলের নাম"
        }
        f_lbl = field_labels.get(str(field).split(":")[0], field)
        with db_lock:
            chk_res = verify_and_consume_profile_edit_random_code(uid, txt)
        if not chk_res.get("ok"):
            sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("💬 অ্যাডমিনের থেকে র‍্যান্ডম কোড নিন", url=sup_url, style="primary"))
            kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
            safe_send(message.chat.id, f"❌ {esc(chk_res.get('reason', 'র‍্যান্ডম কোডটি সঠিক নয়!'))}", reply_markup=kb)
            return

        user_memory_states[uid] = {"step": "awaiting_profile_update", "field": field}
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
        safe_send(
            message.chat.id,
            get_msg("profile_random_code_verified_msg", field_label=f_lbl),
            reply_markup=kb
        )
        return

    def _is_active_manual_code_input(raw_s: str) -> bool:
        cand_s = str(raw_s or "").strip().upper().split()[0] if str(raw_s or "").strip() else ""
        if not re.fullmatch(r"(?:BC|MVR)-[A-Z0-9]{6,10}", cand_s):
            return False
        with db_lock:
            conn_chk = get_connection()
            row_chk = conn_chk.execute("SELECT 1 FROM manual_verification_codes WHERE UPPER(code) = ? LIMIT 1", (cand_s,)).fetchone()
            conn_chk.close()
        return bool(row_chk)

    if st.get("step") == "awaiting_user_manual_verify_code" or (
        not st.get("step", "").startswith("awaiting_profile") and _is_active_manual_code_input(txt)
    ):
        plat = (
            st.get("platform")
            or (st.get("queue", [])[0] if st.get("queue") else "")
            or str(u.get("last_failed_platform") or "")
            or "youtube"
        ).lower()
        if plat not in ("youtube", "tiktok"):
            plat = "youtube"
        parts_in = txt.split()
        code_in = parts_in[0].strip().upper() if parts_in else ""
        prof_url_in = (
            parts_in[1].strip()
            if len(parts_in) > 1
            else (st.get("failed_url") or str(u.get("last_failed_url") or "").strip())
        )
        if not prof_url_in and txt.startswith("http"):
            st["failed_url"] = txt
            user_memory_states[uid] = st
            with db_lock:
                conn_u = get_connection()
                with conn_u:
                    conn_u.execute("UPDATE users SET last_failed_url = ?, last_failed_platform = ? WHERE user_id = ?", (txt, plat, uid))
                conn_u.close()
            safe_send(message.chat.id, "✅ প্রোফাইল লিংক সংরক্ষিত হয়েছে। এখন অ্যাডমিনের দেওয়া ওয়ান-টাইম র‍্যান্ডম কোডটি (যেমন <code>BC-XXXXXX</code>) লিখে পাঠান:")
            return
        if st.get("pending_mvr_code") and txt.startswith("http"):
            code_in = st.get("pending_mvr_code")
            prof_url_in = txt
        if not prof_url_in and re.fullmatch(r"(?:BC|MVR)-[A-Z0-9]{6,10}", code_in):
            st["step"] = "awaiting_user_manual_verify_code"
            st["pending_mvr_code"] = code_in
            st["platform"] = plat
            user_memory_states[uid] = st
            safe_send(
                message.chat.id,
                f"⚠️ <b>প্রোফাইল লিংক পাওয়া যায়নি!</b>\nআপনার <b>{PLATFORMS[plat]['title']}</b> চ্যানেল বা প্রোফাইল লিংকটি নিচে পেস্ট করে পাঠান (অথবা <code>{esc(code_in)} https://...</code> একসাথে পাঠান):"
            )
            return

        auto_bind_ok = True
        # Verify Bio Code or Verification Link is present on the profile when network is reachable
        if prof_url_in.startswith("http") and f"@user_{uid}" not in prof_url_in:
            p_crit = get_platform_criteria(plat)
            v_link = p_crit.get("verification_link") or get_setting("verification_link", "")
            b_chk = verify_bio_code_only(plat, prof_url_in, u.get("bio_verify_code", ""), verification_link=v_link)
            if b_chk.get("network_ok") and not b_chk.get("bio_found"):
                kb = types.InlineKeyboardMarkup()
                kb.row(make_btn("🔄 পুনরায় চেষ্টা করুন (Retry)", callback_data="reg_confirm_selection", style="primary"))
                kb.row(make_btn("💬 অ্যাডমিনকে মেসেজ করে র‍্যান্ডম কোড নিন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
                kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
                safe_send(
                    message.chat.id,
                    f"❌ <b>ম্যানুয়াল ভেরিফিকেশনের পূর্বে বায়োতে কোড থাকা আবশ্যক!</b>\n"
                    f"আপনার {PLATFORMS[plat]['title']} প্রোফাইলের বায়োতে ভেরিফিকেশন কোড (<code>{esc(u.get('bio_verify_code'))}</code>) পাওয়া যায়নি। বায়োতে কোড বসিয়ে পুনরায় ম্যানুয়াল কোডটি পাঠান:",
                    reply_markup=kb
                )
                return
            if not b_chk.get("network_ok"):
                auto_bind_ok = False

        with db_lock:
            chk_c = consume_admin_manual_verify_code(
                code=code_in,
                user_id=uid,
                platform=plat,
                profile_url=prof_url_in,
                bio_code=u.get("bio_verify_code", ""),
                auto_bind=auto_bind_ok
            )
        if not chk_c.get("ok"):
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔄 পুনরায় চেষ্টা করুন (Retry)", callback_data="reg_confirm_selection", style="primary"))
            kb.row(make_btn("💬 অ্যাডমিনকে মেসেজ করে র‍্যান্ডম কোড নিন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
            kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
            safe_send(message.chat.id, f"❌ {esc(chk_c.get('reason', 'কোডটি সঠিক নয়!'))}", reply_markup=kb)
            return
        if not chk_c.get("auto_approved", True):
            user_memory_states.pop(uid, None)
            safe_send(message.chat.id, get_msg("manual_verify_submitted_msg"))
            return

        p_t = PLATFORMS.get(plat, {}).get("title", plat.upper())
        # Notify admins of the completed one-time manual code verification
        for adm_id in get_all_admin_ids():
            try:
                safe_send(
                    adm_id,
                    f"✅ <b>ম্যানুয়াল র‍্যান্ডম কোড ব্যবহৃত ও ভেরিফাইড!</b>\n"
                    f"{FULL_WIDTH_DIVIDER}\n"
                    f"👤 ইউজার: <b>{esc(get_user_label(u))}</b> (ID: <code>{esc(uid)}</code>)\n"
                    f"🌐 প্ল্যাটফর্ম: <b>{esc(p_t)}</b>\n"
                    f"🔑 ব্যবহৃত ওয়ান-টাইম কোড: <code>{esc(code_in)}</code> (লক করা হয়েছে)\n"
                    f"🔗 প্রোফাইল: <code>{esc(prof_url_in)}</code>"
                )
            except Exception:
                pass

        # If the user is in onboarding (not yet registered), immediately proceed through the exact same onboarding steps as Auto-Verification!
        if not int(u.get("registered") or 0):
            ver_list = list(st.get("verified_platforms") or [])
            if plat not in ver_list:
                ver_list.append(plat)
            rem_queue = [pk for pk in (st.get("queue") or []) if pk != plat and pk in ("youtube", "tiktok")]
            if rem_queue:
                next_p = rem_queue[0]
                n_crit = get_platform_criteria(next_p)
                n_tot_v = int(n_crit["min_views"]) * int(n_crit["qualifying_videos"])
                user_memory_states[uid] = {
                    "step": "reg_platform_input",
                    "queue": rem_queue,
                    "verified_platforms": ver_list,
                    "primary_url": st.get("primary_url") or prof_url_in,
                    "primary_subs": 200
                }
                safe_send(
                    message.chat.id,
                    f"✅ <b>অ্যাডমিন ম্যানুয়াল কোডে আপনার {esc(p_t)} অ্যাকাউন্ট সফলভাবে ভেরিফাইড হয়েছে!</b>\n\n"
                    + get_msg(
                        "reg_code_prompt_msg",
                        platform_title=PLATFORMS[next_p]["title"],
                        bio_code=u["bio_verify_code"],
                        min_subs=n_crit["min_subs"],
                        min_total_vids=n_crit.get("min_total_videos", 8),
                        qual_vids=n_crit["qualifying_videos"],
                        min_views=n_crit["min_views"],
                        total_req_views=n_tot_v
                    )
                )
                return

            new_st = {
                "step": "reg_app_uid",
                "verified_platforms": ver_list,
                "primary_url": st.get("primary_url") or prof_url_in,
                "primary_subs": 200,
                "selected_pay_methods": ["bKash", "BattleClub_UID"],
                "pay_queue": ["bKash"],
                "ver_summary_html": (
                    f"✅ <b>অ্যাডমিনের ওয়ান-টাইম র‍্যান্ডম কোড (<code>{esc(code_in)}</code>) দ্বারা আপনার {esc(p_t)} অ্যাকাউন্ট সফলভাবে ভেরিফাইড (VERIFIED) হয়েছে!</b>"
                )
            }
            user_memory_states[uid] = new_st
            start_step2_mandatory_uid_flow(
                message.chat.id,
                uid,
                new_st,
                verification_summary=new_st["ver_summary_html"]
            )
            return

        # If already registered (adding an extra platform via Link More)
        user_memory_states.pop(uid, None)
        safe_send(
            message.chat.id,
            f"✅ <b>অ্যাডমিনের ওয়ান-টাইম র‍্যান্ডম কোড (<code>{esc(code_in)}</code>) দ্বারা আপনার নতুন {esc(p_t)} অ্যাকাউন্ট সফলভাবে ভেরিফাইড ও যুক্ত হয়েছে!</b>",
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return

    if not u.get("registered"):
        process_strict_onboarding_steps(message, u, st)
        return

    if not check_user_session_lock(message.chat.id, message.from_user):
        return

    step = st.get("step")
    if step == "awaiting_video_link":
        process_strict_video_submission(message, u, st)
        return
    if step == "awaiting_extra_platform_link":
        process_strict_extra_platform_link(message, u, st)
        return
    if step == "awaiting_wd_amount":
        process_wd_amount_step(message, u, st)
        return
    # Part 8, Items 80–82: Another Method 3-step sequence:
    # 1) awaiting_wd_other_method_name -> 2) awaiting_wd_other_dest -> 3) awaiting_wd_other_amount
    if step == "awaiting_wd_other_method_name":
        custom_m = re.sub(r"\s+", " ", txt).strip()
        if len(custom_m) < 2:
            kb = types.InlineKeyboardMarkup()
            kb.row(
                make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
                make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
            )
            safe_send(message.chat.id, "⚠️ অনুগ্রহ করে পেমেন্ট মাধ্যমের সঠিক নাম লিখে পাঠান (যেমন: উপায়, ট্রাস্ট ব্যাংক, রকেট ইত্যাদি):", reply_markup=kb)
            return
        st["method"] = custom_m
        st["is_other_way"] = True
        st["step"] = "awaiting_wd_other_dest"
        user_memory_states[uid] = st
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔄 মাধ্যমের নাম পরিবর্তন করুন", callback_data="uwd_other_go", style="primary"))
        kb.row(
            make_btn("✖️ বাতিল করুন (Cancel)", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
        )
        append_page_edit_tools(kb, uid, msg_key="withdraw_other_way_input_msg")
        safe_send(
            message.chat.id,
            get_msg("withdraw_other_way_input_msg", method=esc(custom_m)),
            reply_markup=kb
        )
        return
    if step == "awaiting_wd_other_dest":
        norm_ph = normalize_bd_payment_number(normalize_digits(txt), allow_rocket_12=True)
        clean_dest = norm_ph or re.sub(r"\s+", " ", txt).strip()
        if len(re.sub(r"[^0-9A-Za-z]", "", clean_dest)) < 4:
            kb = types.InlineKeyboardMarkup()
            kb.row(
                make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
                make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
            )
            safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"), reply_markup=kb)
            return
        st["other_dest"] = clean_dest
        st["step"] = "awaiting_wd_other_amount"
        user_memory_states[uid] = st
        bal = float(u.get("balance", 0.0))
        min_w = float(get_setting("min_withdraw", "100.0"))
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("✖️ বাতিল করুন (Cancel)", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger")
        )
        append_page_edit_tools(kb, uid, msg_key="withdraw_other_way_amount_prompt_msg")
        safe_send(
            message.chat.id,
            get_msg(
                "withdraw_other_way_amount_prompt_msg",
                method=esc(st.get("method", "Other")),
                dest=esc(clean_dest),
                balance=f"{bal:.2f}",
                minimum=f"{min_w:.2f}"
            ),
            reply_markup=kb
        )
        return
    if step == "awaiting_wd_other_amount":
        process_wd_other_amount_step(message, u, st)
        return
    if step == "awaiting_wd_phone":
        process_wd_phone_step(message, u, st)
        return
    if step == "awaiting_redeem_code":
        process_redeem_step(message, u)
        return
    if step == "awaiting_profile_update":
        field = str(st.get("field", "name") or "name")
        base_f = field.split(":")[0] if not field.startswith("platform_acc_name:") else "channel_name"
        if base_f not in ("name", "app_uid", "channel_name", "bkash_number", "nagad_number", "rocket_number", "phone"):
            user_memory_states.pop(uid, None)
            return
        with db_lock:
            upd_res = update_user_payment_and_profile_info(uid, field, txt)
        if not upd_res.get("ok"):
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 প্রোফাইলে ফিরে যান", callback_data="umenu:profile", style="danger"))
            safe_send(message.chat.id, f"❌ {esc(upd_res.get('reason', 'আপডেট করা যায়নি!'))}\nআবার সঠিকভাবে লিখে পাঠান:", reply_markup=kb)
            return
        user_memory_states.pop(uid, None)
        if base_f in ("bkash_number", "nagad_number", "rocket_number"):
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute("UPDATE users SET profile_edit_unlocked_until = 0 WHERE user_id = ?", (uid,))
                conn.close()
        p_txt, p_kb = render_user_profile_view(uid, get_user(uid))
        safe_send(message.chat.id, f"✅ আপনার <b>{esc(field)}</b> সফলভাবে আপডেট হয়ে <code>{esc(upd_res.get('value', txt))}</code> সেট করা হয়েছে!\n\n" + p_txt, reply_markup=p_kb)
        return
    if step == "awaiting_old_user_pwd":
        pwd_saved = u.get("password_plain", "")
        if verify_password(u.get("password_hash", ""), txt) or (pwd_saved and txt == pwd_saved):
            clear_failed_login_attempts(uid)
            user_memory_states[uid] = {"step": "awaiting_new_user_pwd"}
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass
            kb = types.InlineKeyboardMarkup()
            append_page_edit_tools(kb, uid, msg_key="pwd_change_new_prompt_msg")
            kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
            safe_send(
                message.chat.id,
                get_msg("pwd_change_new_prompt_msg"),
                reply_markup=kb
            )
        else:
            fail_cnt = record_failed_login_attempt(uid)
            sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("💬 সরাসরি অ্যাডমিনের সাথে কথা বলে পাসওয়ার্ড চেঞ্জ করুন", url=sup_url, style="danger"))
            kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="primary"))
            safe_send(
                message.chat.id,
                get_msg("forgot_password_support_msg", support_link=esc(sup_url))
                + f"\n\n❌ <b>বর্তমান পাসওয়ার্ডটি সঠিক নয় ({fail_cnt} বার ভুল চেষ্টা)!</b>",
                reply_markup=kb
            )
        return

    if step == "awaiting_new_user_pwd":
        if len(txt) < 4:
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
            safe_send(message.chat.id, "⚠️ নতুন পাসওয়ার্ড কমপক্ষে ৪ অক্ষরের হতে হবে! আবার নতুন পাসওয়ার্ডটি লিখে পাঠান:", reply_markup=kb)
            return
        user_memory_states[uid] = {"step": "awaiting_confirm_user_pwd", "new_pwd_candidate": txt}
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        kb = types.InlineKeyboardMarkup()
        append_page_edit_tools(kb, uid, msg_key="pwd_change_confirm_prompt_msg")
        kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
        safe_send(
            message.chat.id,
            get_msg("pwd_change_confirm_prompt_msg"),
            reply_markup=kb
        )
        return

    if step == "awaiting_confirm_user_pwd":
        cand_pwd = st.get("new_pwd_candidate", "")
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        if not cand_pwd or txt != cand_pwd:
            user_memory_states[uid] = {"step": "awaiting_new_user_pwd"}
            kb = types.InlineKeyboardMarkup()
            append_page_edit_tools(kb, uid, msg_key="pwd_change_mismatch_msg")
            kb.row(make_btn("🔙 বাতিল করুন", callback_data="umenu:cancel_home", style="danger"))
            safe_send(message.chat.id, get_msg("pwd_change_mismatch_msg"), reply_markup=kb)
            return
        new_h = hash_password(txt)
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET password_plain = '', password_hash = ? WHERE user_id = ?", (new_h, uid))
                log_audit_event(uid, "Password Changed", "User updated account password (3-step verified)", target_user_id=uid, conn=conn)
            conn.close()
        user_memory_states.pop(uid, None)
        safe_send(
            message.chat.id,
            get_msg("pwd_change_success_msg"),
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return

    top_yt = get_setting("home_youtube_link", "")
    safe_send(
        message.chat.id,
        attach_top_youtube_preview(get_msg("welcome_msg", name=esc(u.get("name")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid), top_yt),
        reply_markup=build_user_home_keyboard(uid, u),
        top_yt_url=top_yt,
        menu_id="user_home"
    )


# ==============================================================================
# PART 2 & 3: STRICT ONBOARDING, ITEMIZED CHECKLIST & VIDEO SUBMISSION PROCESSORS
# ==============================================================================
def process_strict_onboarding_steps(message, u, st):
    uid = str(message.from_user.id)
    step = st.get("step")
    txt = (message.text or "").strip()

    if step == "reg_platform_input":
        # Bio verification code (`bio_verify_code`) is permanent per user and never expires.

        plat = st.get("queue", ["youtube"])[0].lower()
        if plat not in ("youtube", "tiktok"):
            plat = "youtube"
        crit = get_platform_criteria(plat)
        min_s = int(crit["min_subs"])
        min_tot_v = int(crit.get("min_total_videos", 8))
        min_v = int(crit["min_views"])
        qual_v = int(crit["qualifying_videos"])
        total_req_v = min_v * qual_v
        bio_code = u["bio_verify_code"]
        ver_link = crit.get("verification_link") or get_setting("verification_link", "")

        wait_m = safe_send(
            message.chat.id,
            get_msg("verification_busy_msg", platform_title=PLATFORMS[plat]["title"])
        )

        try:
            res = verify_profile_strict(
                plat, txt, bio_code,
                min_subs=min_s, min_views=min_v,
                min_qualifying_vids=qual_v, min_total_vids=min_tot_v,
                verification_link=ver_link
            )
        except Exception as _v_exc:
            res = {
                "eligible": False,
                "title": PLATFORMS[plat]["title"],
                "handle": "",
                "subs": 0,
                "qualifying_vids": 0,
                "qualifying_views_total": 0,
                "qualifying_views_list": [],
                "total_vids": 0,
                "checklist_report_html": "",
                "reason": f"যাচাইয়ের সময় সাময়িক ত্রুটি হয়েছে ({str(_v_exc)[:80]})। অনুগ্রহ করে আবার চেষ্টা করুন।"
            }
        if not res["eligible"]:
            st["failed_url"] = txt
            st["failed_reason"] = res["reason"]
            st["platform"] = plat
            user_memory_states[uid] = st
            with db_lock:
                conn_f = get_connection()
                with conn_f:
                    conn_f.execute("UPDATE users SET last_failed_url = ?, last_failed_platform = ? WHERE user_id = ?", (txt, plat, uid))
                conn_f.close()
            # Part 2, Items 19–22: Show itemized pass/fail (`✅ পূরণ হয়েছে` vs `❌ পূরণ হয়নি`) checklist + Retry & Home buttons!
            chk_html = res.get("checklist_report_html") or f"• {esc(res['reason'])}"
            fail_msg = get_msg(
                "reg_fail_eligibility_msg",
                reason=chk_html,
                min_subs=min_s,
                qual_vids=qual_v,
                total_req_views=total_req_v
            )
            rej_kb = types.InlineKeyboardMarkup()
            rej_kb.row(make_btn("🔄 পুনরায় চেষ্টা করুন (Retry)", callback_data="reg_confirm_selection", style="primary"))
            rej_kb.row(make_btn("🔑 অ্যাডমিন ম্যানুয়াল ভেরিফিকেশন কোড দিন", callback_data=f"uman_code_prompt:{plat}", style="success"))
            rej_kb.row(make_btn("💬 অ্যাডমিনকে মেসেজ করে র‍্যান্ডম কোড নিন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
            rej_kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
            safe_edit(message.chat.id, getattr(wait_m, 'message_id', None), fail_msg, reply_markup=rej_kb)
            return

        ok, err = add_verified_user_platform(
            uid, plat, txt, res["handle"], res["title"], int(res["subs"]), bio_code,
            total_videos_count=int(res.get("total_vids") or 0),
            qualifying_vids_count=int(res.get("qualifying_vids") or 0),
            qualifying_views_total=int(res.get("qualifying_views_total") or 0),
            qualifying_views_list=res.get("qualifying_views_list") or []
        )
        if not ok:
            safe_edit(message.chat.id, getattr(wait_m, 'message_id', None), f"❌ <b>ভেরিফিকেশন রিজেক্টেড!</b>\n{esc(err)}")
            send_onboarding_home(message.chat.id, uid, u)
            return

        st.pop("manual_wait_started_ts", None)
        if not st.get("primary_url"):
            st["primary_url"] = txt
            st["primary_subs"] = int(res["subs"])

        ver_list = list(st.get("verified_platforms") or [])
        if plat not in ver_list:
            ver_list.append(plat)
        st["verified_platforms"] = ver_list

        ver_hist_block = res.get("verification_summary") or (
            f"📊 <b>ভেরিফিকেশন হিস্ট্রি ({PLATFORMS[plat]['title']}):</b>\n"
            f"├ 📺 প্রোফাইল/চ্যানেল: <b>{esc(res['title'])}</b>\n"
            f"├ 👥 সাবস্ক্রাইবার/ফলোয়ার: <b>{res['subs']}</b>\n"
            f"├ 📹 মোট পাবলিক ভিডিও: <b>{res.get('total_vids', 0)}টি</b>\n"
            f"├ 🎬 যোগ্যতা ভিডিও: <b>{res.get('qualifying_vids', 0)}টি</b> (মোট ভিউজ: <b>{res.get('qualifying_views_total', 0)}</b>)\n"
            f"└ 🧬 ভেরিফিকেশন কোড: <code>{esc(bio_code)}</code> <b>(Verified ✅)</b>"
        )

        st["queue"].pop(0)
        if st["queue"]:
            next_p = st["queue"][0]
            n_crit = get_platform_criteria(next_p)
            n_tot_v = int(n_crit["min_views"]) * int(n_crit["qualifying_videos"])
            safe_edit(
                message.chat.id, getattr(wait_m, 'message_id', None),
                f"✅ <b>{PLATFORMS[plat]['title']} ({esc(res['title'])}) শর্ত অনুযায়ী ১০০% যাচাই ও লক হয়েছে!</b>\n"
                f"{ver_hist_block}\n\n" +
                get_msg(
                    "reg_code_prompt_msg",
                    platform_title=PLATFORMS[next_p]["title"],
                    bio_code=bio_code,
                    min_subs=n_crit["min_subs"],
                    min_total_vids=n_crit.get("min_total_videos", 8),
                    qual_vids=n_crit["qualifying_videos"],
                    min_views=n_crit["min_views"],
                    total_req_views=n_tot_v
                )
            )
            return

        summary_hdr = (
            f"✅ <b>অভিনন্দন! আপনার {PLATFORMS[plat]['title']} প্রোফাইল ({esc(res['title'])}) সফলভাবে ভেরিফাইড হয়েছে!</b>\n"
            f"{ver_hist_block}"
        )
        # Part 3, Items 27–30: Immediately after channel verification, ask for Mandatory Battle Club UID FIRST!
        start_step2_mandatory_uid_flow(
            message.chat.id,
            uid,
            st,
            verification_summary=summary_hdr,
            edit_message_id=getattr(wait_m, 'message_id', None)
        )
        return

    # Step 2: Mandatory Battle Club UID FIRST
    if step == "reg_app_uid":
        disp_uid = format_display_app_uid(txt)
        if len(re.sub(r"[^0-9A-Z]", "", disp_uid)) < 2:
            safe_send(message.chat.id, "⚠️ সঠিক Battle Club অ্যাপ UID হ্যাশট্যাগ ও সংখ্যা (যেমন <code>#1007</code> অথবা <code>#107</code>) সহ লিখুন (UID ছাড়া পরবর্তী ধাপে যাওয়া যাবে না):")
            return
        with db_lock:
            lock_ok, lock_msg = check_and_lock_user_identity(uid, app_uid=disp_uid, commit_lock=False)
        if not lock_ok:
            safe_send(message.chat.id, f"❌ {lock_msg}\nআপনার নিজস্ব UID দিন:")
            return
        st["app_uid"] = disp_uid
        user_memory_states[uid] = st
        start_step3_payment_selection_flow(message.chat.id, uid, st)
        return

    if step == "reg_phone_select":
        safe_send(message.chat.id, "👇 অনুগ্রহ করে উপরের বাটন থেকে আপনার পেমেন্ট মেথড (বিকাশ/নগদ/রকেট) সিলেক্ট করে <b>কনফার্ম</b> বাটনে ক্লিক করুন।")
        return

    # Step 3: Payment Numbers Input (1 number per selected method: bKash, Nagad, Rocket)
    if step == "reg_phone":
        pay_q = list(st.get("pay_queue") or ["bKash"])
        curr_m = pay_q[0] if pay_q else "bKash"
        allow_12 = (curr_m == "Rocket")
        clean_ph = normalize_bd_payment_number(txt, allow_rocket_12=allow_12)
        if not clean_ph:
            m_lbl = PAYMENT_PLATFORM_LABELS.get(curr_m, curr_m)
            safe_send(message.chat.id, f"⚠️ সঠিক {m_lbl} মোবাইল পেমেন্ট নাম্বার (<code>01XXXXXXXXX</code>) লিখে পাঠান (প্রতি মাধ্যমে ১টি নাম্বার):")
            return
        with db_lock:
            lock_ok, lock_msg = check_and_lock_user_identity(uid, phone=clean_ph, commit_lock=False)
        if not lock_ok:
            safe_send(message.chat.id, f"❌ {lock_msg}\nআপনার নিজের সচল নাম্বার দিন:")
            return

        if curr_m == "bKash":
            st["bkash_number"] = clean_ph
        elif curr_m == "Nagad":
            st["nagad_number"] = clean_ph
        elif curr_m == "Rocket":
            st["rocket_number"] = clean_ph

        if not st.get("phone"):
            st["phone"] = clean_ph

        if pay_q:
            pay_q.pop(0)
        st["pay_queue"] = pay_q

        if pay_q:
            next_m = pay_q[0]
            next_lbl = PAYMENT_PLATFORM_LABELS.get(next_m, next_m)
            user_memory_states[uid] = st
            safe_send(message.chat.id, get_msg("reg_payment_number_input_msg", method_title=next_lbl))
            return

        # Step 4: User Account Name
        st["step"] = "reg_name"
        user_memory_states[uid] = st
        safe_send(message.chat.id, get_msg("reg_name_input_msg"))
        return

    # Step 4: User Account Name -> Step 5: Verified Platform Account Name(s)
    if step == "reg_name":
        if len(txt) < 2:
            safe_send(message.chat.id, "⚠️ অনুগ্রহ করে আপনার সঠিক নাম লিখে পাঠান:")
            return
        st["name"] = txt
        plats_db = get_user_platforms(uid)
        ver_p_list = []
        for p in plats_db:
            pk = str(p.get("platform") or "").lower()
            if pk in ("youtube", "tiktok") and pk not in ver_p_list:
                ver_p_list.append(pk)
        for pk in list(st.get("verified_platforms") or []):
            pk_low = str(pk or "").lower()
            if pk_low in ("youtube", "tiktok") and pk_low not in ver_p_list:
                ver_p_list.append(pk_low)
        if not ver_p_list:
            ver_p_list = ["youtube"]

        st["channel_name_queue"] = list(ver_p_list)
        st["step"] = "reg_channel_name"
        user_memory_states[uid] = st

        first_plat = ver_p_list[0]
        if first_plat == "youtube":
            safe_send(message.chat.id, get_msg("reg_yt_channel_name_input_msg"))
        elif first_plat == "tiktok":
            safe_send(message.chat.id, get_msg("reg_tt_channel_name_input_msg"))
        else:
            safe_send(message.chat.id, get_msg("reg_channel_name_input_msg", platform_title=PLATFORMS.get(first_plat, {}).get("title", first_plat.upper())))
        return

    # Step 5: Per-Platform Account Name(s) (1 if 1 platform verified; separate YouTube & TikTok if 2 platforms verified)
    if step == "reg_channel_name":
        if len(txt) < 2:
            safe_send(message.chat.id, "⚠️ অনুগ্রহ করে চ্যানেল/অ্যাকাউন্টের সঠিক নাম লিখে পাঠান:")
            return
        ch_q = list(st.get("channel_name_queue") or ["youtube"])
        curr_p = ch_q.pop(0) if ch_q else "youtube"
        st["channel_name_queue"] = ch_q

        if curr_p == "youtube":
            st["youtube_channel_name"] = txt
        elif curr_p == "tiktok":
            st["tiktok_channel_name"] = txt

        if not st.get("channel_name"):
            st["channel_name"] = txt
        else:
            st["channel_name"] = f"{st['channel_name']} | {txt}"

        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute(
                    "UPDATE user_platforms SET display_name = ? WHERE user_id = ? AND LOWER(platform) = ?",
                    (txt[:60], uid, curr_p)
                )
            conn.close()

        if ch_q:
            next_p = ch_q[0]
            user_memory_states[uid] = st
            if next_p == "tiktok":
                safe_send(message.chat.id, get_msg("reg_tt_channel_name_input_msg"))
            else:
                safe_send(message.chat.id, get_msg("reg_yt_channel_name_input_msg"))
            return

        # Step 6: Create Strong Password
        st["step"] = "reg_password"
        user_memory_states[uid] = st
        safe_send(message.chat.id, get_msg("reg_password_input_msg"))
        return

    # Step 6: Create Strong Password -> Step 7: Confirm Password a Second Time
    if step == "reg_password":
        if len(txt) < 4:
            safe_send(message.chat.id, "⚠️ পাসওয়ার্ড কমপক্ষে ৪ অক্ষরের হতে হবে! একটি শক্তিশালী পাসওয়ার্ড লিখে পাঠান:")
            return
        st["password_candidate"] = txt
        st["step"] = "reg_confirm_password"
        user_memory_states[uid] = st
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        safe_send(message.chat.id, get_msg("reg_password_confirm_input_msg"))
        return

    # Step 7: Confirm Password -> Step 8: Grant Dashboard Access
    if step == "reg_confirm_password":
        cand_pwd = st.get("password_candidate", "")
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        if not cand_pwd or txt != cand_pwd:
            st["step"] = "reg_password"
            user_memory_states[uid] = st
            safe_send(
                message.chat.id,
                "❌ <b>দুটি পাসওয়ার্ড মেলেনি!</b>\nনিরাপত্তার জন্য আবার নতুন পাসওয়ার্ডটি লিখে পাঠান:"
            )
            return

        pwd_hash = hash_password(cand_pwd)
        app_u = format_display_app_uid(st.get("app_uid") or "")
        if not app_u or len(re.sub(r"[^0-9A-Z]", "", app_u)) < 2:
            st["step"] = "reg_app_uid"
            user_memory_states[uid] = st
            safe_send(message.chat.id, get_msg("reg_uid_input_msg", verification_summary=st.get("ver_summary_html", "✅ প্ল্যাটফর্ম যাচাই সম্পন্ন!")))
            return

        bk_u = str(st.get("bkash_number") or "").strip()
        ng_u = str(st.get("nagad_number") or "").strip()
        rk_u = str(st.get("rocket_number") or "").strip()
        ph_u = str(st.get("phone") or bk_u or ng_u or rk_u or "").strip()
        if not bk_u and ph_u and "bKash" in (st.get("selected_pay_methods") or ["bKash"]):
            bk_u = ph_u
        sel_methods = list(st.get("selected_pay_methods") or ["bKash", "BattleClub_UID"])
        if "BattleClub_UID" not in sel_methods:
            sel_methods.append("BattleClub_UID")

        yt_ch_name = str(st.get("youtube_channel_name") or "").strip()
        tt_ch_name = str(st.get("tiktok_channel_name") or "").strip()
        comb_ch_name = str(st.get("channel_name") or yt_ch_name or tt_ch_name or "").strip()

        with db_lock:
            conn = get_connection()
            with conn:
                for cand_num in [n for n in (ph_u, bk_u, ng_u, rk_u) if n]:
                    lock_ok, lock_msg = check_and_lock_user_identity(uid, phone=cand_num, commit_lock=True, conn=conn)
                    if not lock_ok:
                        conn.close()
                        safe_send(message.chat.id, f"❌ {lock_msg}")
                        send_onboarding_home(message.chat.id, uid, u)
                        return
                lock_ok_u, lock_msg_u = check_and_lock_user_identity(uid, app_uid=app_u, commit_lock=True, conn=conn)
                if not lock_ok_u:
                    conn.close()
                    safe_send(message.chat.id, f"❌ {lock_msg_u}")
                    send_onboarding_home(message.chat.id, uid, u)
                    return

                conn.execute("""
                    UPDATE users SET
                        phone = ?, bkash_number = ?, nagad_number = ?, rocket_number = ?,
                        selected_payment_methods = ?,
                        password_plain = '', password_hash = ?, name = ?,
                        channel_name = ?, youtube_channel_name = ?, tiktok_channel_name = ?,
                        channel_url = ?, channel_subs = ?, app_uid = ?,
                        registered = 1, session_logged_out = 0, timeout_notified = 0, last_active_ts = ?
                    WHERE user_id = ?
                """, (
                    ph_u, bk_u, ng_u, rk_u,
                    json.dumps(sel_methods),
                    pwd_hash, st.get("name", ""),
                    comb_ch_name, yt_ch_name, tt_ch_name,
                    st.get("primary_url", ""), int(st.get("primary_subs", 200)),
                    app_u, time.time(), uid
                ))
            conn.close()

        u_fresh = get_user(uid)
        if u_fresh.get("ref_by") and not u_fresh.get("redeemed_ref"):
            if get_setting("ref_unlock_on_first_video", "0") != "1":
                process_referral_credit(uid, u_fresh["ref_by"])

        user_memory_states.pop(uid, None)
        pay_sum = format_user_payment_numbers_summary(u_fresh)
        safe_send(
            message.chat.id,
            get_msg(
                "reg_complete_msg",
                app_uid=esc(app_u),
                payment_methods_summary=esc(pay_sum),
                bio_code=esc(u_fresh["bio_verify_code"]),
                unique_code=esc(u_fresh["active_video_code"])
            )
        )
        top_yt = get_setting("home_youtube_link", "")
        safe_send(
            message.chat.id,
            attach_top_youtube_preview(get_msg("welcome_msg", name=esc(u_fresh.get("name")), balance=f"{float(u_fresh.get('balance', 0)):.2f}", user_id=uid), top_yt),
            reply_markup=build_user_home_keyboard(uid, u_fresh),
            top_yt_url=top_yt,
            menu_id="user_home"
        )
        return

    send_onboarding_home(message.chat.id, uid, u)


def process_strict_extra_platform_link(message, u, st):
    uid = str(message.from_user.id)
    txt = (message.text or "").strip()
    plat = st.get("platform", "youtube").lower()
    if plat not in ("youtube", "tiktok"):
        plat = "youtube"
    user_memory_states.pop(uid, None)

    debt_b = float(u.get("debt_balance", 0.0) or 0.0)
    bal_b = float(u.get("balance", 0.0) or 0.0)
    if debt_b > 0 or bal_b < 0:
        eff_debt = max(debt_b, abs(min(0.0, bal_b)))
        safe_send(
            message.chat.id,
            get_msg("debt_bind_block_msg", debt_balance=f"{eff_debt:.2f}"),
            reply_markup=build_user_home_keyboard(uid, u),
            menu_id="user_home"
        )
        return

    crit = get_platform_criteria(plat)
    max_acc = int(crit["max_accounts"])
    existing = get_user_platforms(uid, plat)
    if len(existing) >= max_acc:
        lim_txt = get_msg("account_limit_reached_msg", platform_title=PLATFORMS[plat]["title"], max_accounts=max_acc)
        safe_send(message.chat.id, lim_txt, reply_markup=build_user_home_keyboard(uid, u), menu_id="user_home")
        return

    min_s = int(crit["min_subs"])
    min_tot_v = int(crit.get("min_total_videos", 8))
    min_v = int(crit["min_views"])
    qual_v = int(crit["qualifying_videos"])
    total_req_v = min_v * qual_v
    bio_code = st.get("extra_bio_code") or u["bio_verify_code"]
    ver_link = crit.get("verification_link") or get_setting("verification_link", "")

    wait_m = safe_send(
        message.chat.id,
        get_msg("verification_busy_msg", platform_title=PLATFORMS[plat]["title"])
    )
    res = verify_profile_strict(
        plat, txt, bio_code,
        min_subs=min_s, min_views=min_v,
        min_qualifying_vids=qual_v, min_total_vids=min_tot_v,
        verification_link=ver_link
    )
    if not res.get("eligible") and bio_code != u.get("bio_verify_code") and u.get("bio_verify_code"):
        alt_res = verify_profile_strict(
            plat, txt, u["bio_verify_code"],
            min_subs=min_s, min_views=min_v,
            min_qualifying_vids=qual_v, min_total_vids=min_tot_v,
            verification_link=ver_link
        )
        if alt_res.get("eligible"):
            res = alt_res
            bio_code = u["bio_verify_code"]
    if not res["eligible"]:
        user_memory_states[uid] = {
            "step": "awaiting_extra_platform_link",
            "platform": plat,
            "failed_url": txt,
            "failed_reason": res["reason"],
            "manual_wait_started_ts": time.time()
        }
        chk_html = res.get("checklist_report_html") or f"• {esc(res['reason'])}"
        fail_msg = get_msg(
            "reg_fail_eligibility_msg",
            reason=chk_html,
            min_subs=min_s,
            qual_vids=qual_v,
            total_req_views=total_req_v
        )
        rej_kb = types.InlineKeyboardMarkup()
        rej_kb.row(make_btn("🔄 পুনরায় চেষ্টা করুন (Retry)", callback_data=f"ulink_act:{plat}", style="primary"))
        rej_kb.row(make_btn("🔑 অ্যাডমিন ম্যানুয়াল ভেরিফিকেশন কোড দিন", callback_data=f"uman_code_prompt:{plat}", style="success"))
        rej_kb.row(make_btn("💬 অ্যাডমিনকে মেসেজ করে র‍্যান্ডম কোড নিন", url=get_setting("support_link", "https://t.me/battleclubsupport"), style="primary"))
        rej_kb.row(make_btn("🔙 হোমপেজে ফিরে যান", callback_data="umenu:cancel_home", style="danger"))
        safe_edit(message.chat.id, getattr(wait_m, 'message_id', None), fail_msg, reply_markup=rej_kb)
        return

    ok, err = add_verified_user_platform(
        uid, plat, txt, res["handle"], res["title"], int(res["subs"]), bio_code,
        total_videos_count=int(res.get("total_vids") or 0),
        qualifying_vids_count=int(res.get("qualifying_vids") or 0),
        qualifying_views_total=int(res.get("qualifying_views_total") or 0),
        qualifying_views_list=res.get("qualifying_views_list") or [],
        allow_same_user_reverify=False
    )
    if not ok:
        safe_edit(message.chat.id, getattr(wait_m, 'message_id', None), f"❌ <b>ব্যর্থ:</b> {esc(err)}", reply_markup=build_user_home_keyboard(uid, u), menu_id="user_home")
        return

    ver_hist = res.get("verification_summary") or ""
    safe_edit(
        message.chat.id, getattr(wait_m, 'message_id', None),
        f"✅ <b>অভিনন্দন! আপনার নতুন {PLATFORMS[plat]['title']} অ্যাকাউন্ট ({esc(res['title'])}) ১০০% শর্ত পূরণ করে সফলভাবে ভেরিফাইড ও যুক্ত হয়েছে!</b>\n\n{ver_hist}",
        reply_markup=build_user_home_keyboard(uid, get_user(uid)),
        menu_id="user_home"
    )


def apply_strike_and_cooldown(uid: str, u: dict, strike_field: str, reason_msg: str) -> str:
    allowed_cols = {"duplicate_strikes", "wrong_submit_strikes"}
    col = strike_field if strike_field in allowed_cols else "wrong_submit_strikes"
    strike_lim = max(1, int(get_setting("strike_limit", "3")))
    strikes = int(u.get(col, 0) or 0) + 1
    u_name = u.get("name") or get_user_label(u)
    reached_limit = (strikes >= strike_lim)
    with db_lock:
        conn = get_connection()
        try:
            with conn:
                log_audit_event(uid, f"Strike {strikes}/{strike_lim} ({col})", reason_msg, target_user_id=uid, conn=conn)
                if reached_limit:
                    cd_until = time.time() + 86400
                    conn.execute(
                        f"UPDATE users SET {col} = 0, cooldown_until_ts = ?, status = 'inactive', bio_frozen = 1 WHERE user_id = ?",
                        (cd_until, uid)
                    )
                else:
                    conn.execute(f"UPDATE users SET {col} = ? WHERE user_id = ?", (strikes, uid))
        finally:
            conn.close()

    if reached_limit:
        for adm_id in get_all_admin_ids():
            safe_send(
                adm_id,
                f"🚨 <b>{strike_lim}-স্ট্রাইক ভায়োলেশন অ্যাকশন (Account INACTIVE & FROZEN)!</b>\n{FULL_WIDTH_DIVIDER}\n"
                f"👤 ইউজারের নাম: <b>{esc(u_name)}</b> ({esc(get_user_label(u))})\n"
                f"🆔 User ID: <code>{uid}</code>\n"
                f"⚠️ কারণ: পরপর {strike_lim} বার নিয়ম ভঙ্গ / ডুপ্লিকেট বা ভুল ভিডিও সাবমিশন ({esc(reason_msg)}) করায় অ্যাকাউন্টটি স্বয়ংক্রিয়ভাবে INACTIVE ও FROZEN করা হয়েছে!"
            )
        sup_link = get_setting("support_link", "https://t.me/battleclubsupport")
        return (
            f"\n\n❄️ <b>চূড়ান্ত ব্যবস্থা ({strike_lim}/{strike_lim} স্ট্রাইক):</b> পরপর {strike_lim} বার ডুপ্লিকেট বা ভুল ভিডিও সাবমিট করায় "
            f"আপনার অ্যাকাউন্টটি স্বয়ংক্রিয়ভাবে <b>INACTIVE / FROZEN</b> করা হয়েছে! সমাধানের জন্য সাপোর্টে যোগাযোগ করুন: {esc(sup_link)}"
        )
    return f"\n\n⚠️ <b>সতর্কবার্তা ({strikes}/{strike_lim} Warning):</b> অন্যের চ্যানেল বা ডুপ্লিকেট/ভুল ভিডিও সাবমিট করবেন না! {strike_lim} বার হলে অ্যাকাউন্ট ফ্রিজ/ইনঅ্যাক্টিভ করা হবে।"


def process_strict_video_submission(message, u, st):
    uid = str(message.from_user.id)
    txt = (message.text or "").strip()
    plat = st.get("platform", "youtube").lower()
    if plat not in ("youtube", "tiktok"):
        plat = "youtube"
    user_memory_states.pop(uid, None)

    is_cd, cd_txt = check_user_cooldown(u)
    if is_cd:
        safe_send(message.chat.id, cd_txt, reply_markup=build_user_home_keyboard(uid, u), menu_id="user_home")
        return

    all_user_plats = get_user_platforms(uid, plat)
    if not all_user_plats:
        safe_send(
            message.chat.id,
            f"⚠️ আপনার এই প্ল্যাটফর্মে ({PLATFORMS[plat]['title']}) কোনো ভেরিফাইড চ্যানেল বা অ্যাকাউন্ট যুক্ত নেই! আগে অ্যাকাউন্ট ভেরিফাই করুন।",
            reply_markup=build_user_home_keyboard(uid, u),
            menu_id="user_home"
        )
        return
    sel_pid = int(st.get("selected_platform_id") or 0)
    if sel_pid:
        matched_plats = [p for p in all_user_plats if int(p.get("id") or 0) == sel_pid]
        if not matched_plats:
            safe_send(message.chat.id, "⛔ অবৈধ বা অননুমোদিত অ্যাকাউন্ট আইডি! অনুগ্রহ করে আপনার নিজস্ব ভেরিফাইড অ্যাকাউন্ট সিলেক্ট করুন।", reply_markup=build_user_home_keyboard(uid, u), menu_id="user_home")
            return
        user_plats = matched_plats
    else:
        user_plats = [all_user_plats[0]] if len(all_user_plats) == 1 else all_user_plats
        if user_plats:
            sel_pid = int(user_plats[0].get("id") or 0)
    canon_id = canonicalize_video_id(plat, txt)

    with db_lock:
        conn = get_connection()
        dup = is_video_submitted_globally(plat, canon_id, video_url=txt, conn=conn)
        conn.close()

    if dup:
        strike_note = apply_strike_and_cooldown(uid, u, "duplicate_strikes", "Duplicate Video Submission")
        safe_send(
            message.chat.id,
            f"⚠️ <b>ডুপ্লিকেট ভিডিও রিজেক্টেড!</b> এই ভিডিও লিংকটি ইতিমধ্যে একবার সাবমিট করা হয়েছে (একই ভিডিও কোনো একাউন্ট বা প্ল্যাটফর্ম থেকে দ্বিতীয়বার সাবমিট করা যায় না)।{strike_note}",
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return

    crit = get_platform_criteria(plat)
    v_code = u.get("active_video_code", "")
    app_u = format_display_app_uid(u.get("app_uid", ""))
    g_code = get_setting("global_required_code", "#BattleClub")
    ver_link = crit.get("verification_link") or get_setting("verification_link", "")
    req_link_cfg = get_setting("required_link_config", "all_public")
    enf_72h = get_setting("enforce_72h_rule", "1") == "1"
    upload_win_hrs = int(crit.get("submission_window_hours") or get_setting("submission_window_hours", "72"))
    qualification_win_hrs = int(crit.get("qualification_window_hours") or get_setting("qualification_window_hours", "120"))
    min_init_v = int(crit.get("min_initial_views") or get_setting("min_initial_views", "1000"))
    min_dur_sec = int(get_setting("min_video_duration_sec", "10"))
    vel_thr = float(get_setting("view_velocity_threshold", "15000"))
    eng_thr = float(get_setting("engagement_threshold_ratio", "0.0005"))
    auto_rej_susp = get_setting("suspicious_auto_reject", "1") == "1"

    req_uid_flag = get_setting("require_app_uid_in_video", "0") == "1"
    eff_app_uid_req = app_u if req_uid_flag else ""
    yt_oauth = get_setting("youtube_oauth_access_token", "")
    tt_oauth = get_setting("tiktok_oauth_access_token", "")
    eff_oauth_tok = yt_oauth if plat == "youtube" else tt_oauth

    wait_m = safe_send(message.chat.id, get_msg("video_verification_busy_msg"))
    res = verify_video_submission_strict(
        plat, txt, user_plats, v_code, eff_app_uid_req, g_code,
        enforce_72h=enf_72h, max_hours=upload_win_hrs, min_duration_sec=min_dur_sec,
        min_initial_views=min_init_v, velocity_threshold=vel_thr,
        engagement_threshold=eng_thr, auto_reject_suspicious=auto_rej_susp,
        verification_link=ver_link,
        oauth_access_token=eff_oauth_tok,
        enforce_app_uid=req_uid_flag,
        required_link_config=req_link_cfg
    )

    resolved_canon_id = str(res.get("canonical_id") or canon_id).strip()
    if resolved_canon_id and resolved_canon_id != canon_id:
        with db_lock:
            conn = get_connection()
            dup_after = is_video_submitted_globally(plat, resolved_canon_id, video_url=txt, conn=conn)
            conn.close()
        if dup_after:
            strike_note = apply_strike_and_cooldown(uid, u, "duplicate_strikes", "Duplicate Video Submission (Resolved Short Link)")
            safe_edit(
                message.chat.id, getattr(wait_m, 'message_id', None),
                f"⚠️ <b>ডুপ্লিকেট ভিডিও রিজেক্টেড!</b> এই ভিডিও লিংকটি ইতিমধ্যে একবার সাবমিট করা হয়েছে (একই ভিডিও কোনো একাউন্ট বা প্ল্যাটফর্ম থেকে দ্বিতীয়বার সাবমিট করা যায় না)।{strike_note}",
                reply_markup=build_user_home_keyboard(uid, get_user(uid)),
                menu_id="user_home"
            )
            return
    canon_id = resolved_canon_id or canon_id
    if int(res.get("matched_platform_id") or 0) > 0:
        sel_pid = int(res["matched_platform_id"])

    if not res["ok"] and not res.get("auto_rejected_suspicious"):
        err_cat = str(res.get("error_category") or "")
        if err_cat in ("network_failure", "rate_limited"):
            # Never auto-reject or penalize user due to API/Network/Rate-Limit failure!
            safe_edit(
                message.chat.id, getattr(wait_m, 'message_id', None),
                f"⚠️ <b>সাময়িক নেটওয়ার্ক বা প্ল্যাটফর্ম রেট-লিমিট সমস্যা:</b>\n{esc(res['reason'])}",
                reply_markup=build_user_home_keyboard(uid, get_user(uid)),
                menu_id="user_home"
            )
            return
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET videos_rejected = videos_rejected + 1 WHERE user_id = ?", (uid,))
            conn.close()
        strike_note = apply_strike_and_cooldown(uid, u, "wrong_submit_strikes", res["reason"])
        safe_edit(
            message.chat.id, getattr(wait_m, 'message_id', None),
            get_msg("video_submission_fail_msg", reason=esc(res["reason"])) + strike_note,
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return

    sub_id = f"V{int(time.time()*1000)}_{uid[-4:]}_{secrets.token_hex(2).upper()}"
    cur_views = int(res.get("views") or 0)
    ytdlp_v = res.get("ytdlp_views")
    page_v = res.get("public_page_views")
    dual_ok = 1 if res.get("dual_source_verified") else 0
    single_ok = 1 if res.get("single_source_verified") else 0
    ver_mode = str(res.get("verification_mode") or ("DUAL_SOURCE_VERIFIED" if dual_ok else ("SINGLE_SOURCE_VERIFIED" if single_ok else "UNVERIFIED")))
    dur_known = 1 if res.get("duration_known", res.get("duration_sec") is not None) else 0
    pub_known = 1 if res.get("publish_date_known", res.get("publish_ts") is not None) else 0
    dur_s = int(res.get("duration_sec")) if (dur_known and res.get("duration_sec") is not None) else None
    pub_ts_v = float(res.get("publish_ts")) if (pub_known and res.get("publish_ts") is not None) else None
    pub_date_v = str(res.get("publish_date") or "Unknown") if pub_known else "Unknown"
    comments_ver = 1 if res.get("comments_verified") else 0
    org_status = str(res.get("organic_status") or "pending_snapshots")
    views_known = bool(res.get("views_known"))
    is_susp = bool(res.get("suspicious") or res.get("auto_rejected_suspicious"))
    review_required = bool(res.get("review_required") or not dur_known or not pub_known)
    risk_reason = str(res.get("review_reason") or res.get("risk_reason") or res.get("reason") or "")
    traffic_info = res.get("traffic_breakdown") or {}
    tr_avail = 1 if traffic_info.get("traffic_data_available") else 0
    tr_status = str(traffic_info.get("traffic_source_status") or "Unknown / Unavailable")
    ext_links_list = res.get("external_links") or []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    now_ts = time.time()

    auto_app_enabled = get_setting("auto_approve", "1") == "1"
    qualifies_now = bool(
        views_known
        and cur_views >= min_init_v
        and not is_susp
        and not review_required
        and res.get("organic_verified") is True
    )
    if res.get("auto_rejected_suspicious"):
        bot_st_val = "rejected"
        admin_st_val = "rejected"
        status_val = "rejected"
    else:
        bot_st_val = "manual_review" if (is_susp or review_required) else ("approved" if (qualifies_now and auto_app_enabled) else "waiting_views")
        admin_st_val = "pending"
        status_val = "manual_review" if bot_st_val == "manual_review" else ("bot_approved" if bot_st_val == "approved" else "waiting_views")
    with db_lock:
        conn_vc = get_connection()
        with conn_vc:
            conn_vc.execute(
                "INSERT OR REPLACE INTO used_random_codes (code, code_type, user_id, ref_id, created_at) VALUES (?, 'video_locked', ?, ?, ?)",
                (str(v_code or ""), uid, sub_id, now_str)
            )
            new_next_vid_code = generate_unique_bc_code("video_submit", user_id=uid, ref_id=sub_id, conn=conn_vc)
        conn_vc.close()
    deadline_ts = now_ts + max(1, qualification_win_hrs) * 3600
    initial_credited_amt = 0.0
    saved_ext_links = []

    try:
        with db_lock:
            conn = get_connection()
            try:
                with begin_immediate_transaction(conn):
                    conn.execute("""
                        INSERT INTO videos (
                            sub_id, platform, platform_account_id, video_id, canonical_video_id, user_id, url, video_url, title,
                            unique_code, global_code, app_uid, status, bot_status, admin_status,
                            rejection_reason, rejection_date,
                            current_views, ytdlp_views, public_page_views, dual_source_verified, single_source_verified, verification_mode,
                            video_duration_sec, duration_known,
                            publish_ts, publish_date, publish_date_known,
                            comments_verified, organic_status, traffic_data_available, traffic_source_status,
                            previous_views, flagged_suspicious,
                            risk_reason, submitted_at_ts, submitted_at, qualification_deadline_ts,
                            view_metrics_known, view_metrics_source
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sub_id, plat, sel_pid, res.get("canonical_id") or canon_id, res.get("canonical_id") or canon_id, uid, txt, txt, res.get("title") or "Video",
                        v_code, g_code, app_u, status_val, bot_st_val, admin_st_val,
                        risk_reason if status_val == "rejected" else "", now_str if status_val == "rejected" else "",
                        cur_views, ytdlp_v, page_v, dual_ok, single_ok, ver_mode,
                        dur_s, dur_known,
                        pub_ts_v, pub_date_v, pub_known,
                        comments_ver, org_status, tr_avail, tr_status,
                        cur_views, 1 if is_susp else 0,
                        risk_reason, now_ts, now_str, deadline_ts,
                        1 if views_known else 0, str(res.get("metrics_source") or "public-page")[:40]
                    ))
                    register_video_submission_lock(plat, res.get("canonical_id") or canon_id, txt, uid, sub_id=sub_id, conn=conn)
                    saved_ext_links = save_video_traffic_and_external_links(
                        sub_id=sub_id,
                        user_id=uid,
                        platform=plat,
                        traffic_breakdown=traffic_info,
                        external_links=ext_links_list,
                        conn=conn
                    )
                    if status_val == "rejected":
                        conn.execute("UPDATE users SET videos_submitted = videos_submitted + 1, videos_rejected = videos_rejected + 1, active_video_code = ? WHERE user_id = ?", (new_next_vid_code, uid))
                    else:
                        conn.execute("UPDATE users SET videos_submitted = videos_submitted + 1, wrong_submit_strikes = 0, active_video_code = ? WHERE user_id = ?", (new_next_vid_code, uid))
                    conn.execute("""
                        INSERT OR IGNORE INTO video_view_snapshots
                            (sub_id, views, likes, comments, source, recorded_at_ts)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (sub_id, cur_views, int(res.get("likes") or 0), int(res.get("comments") or 0), str(res.get("metrics_source") or "public-page")[:40], now_ts))
                    if bot_st_val == "approved":
                        credited_now, _ = process_bot_approval_credit(conn, sub_id, uid, cur_views)
                        initial_credited_amt = float(credited_now or 0.0)
            finally:
                conn.close()
    except sqlite3.IntegrityError:
        safe_edit(
            message.chat.id, getattr(wait_m, 'message_id', None),
            get_msg("video_submission_fail_msg", reason="এই ভিডিও লিংকটি আগেই জমা হয়েছে। একই ভিডিও দ্বিতীয়বার জমা দেওয়া যাবে না।"),
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return
    except Exception as exc:
        safe_edit(
            message.chat.id, getattr(wait_m, 'message_id', None),
            get_msg("video_submission_fail_msg", reason=f"সাবমিশন সংরক্ষণ করা যায়নি: {esc(str(exc)[:180])}"),
            reply_markup=build_user_home_keyboard(uid, get_user(uid)),
            menu_id="user_home"
        )
        return

    if saved_ext_links:
        _notify_admins_of_external_links(u, sub_id, plat, cur_views, traffic_info, saved_ext_links)

    if is_susp or review_required:
        alert_txt = get_msg(
            "suspicious_video_alert_msg",
            user_label=esc(get_user_label(u)),
            user_id=uid,
            sub_id=sub_id,
            platform=PLATFORMS[plat]["title"],
            views=cur_views,
            reason=esc(risk_reason or "অর্গানিক ভিউ বা মেটাডেটা যাচাই হয়নি; ম্যানুয়াল রিভিউ প্রয়োজন")
        )
        adm_kb = types.InlineKeyboardMarkup()
        adm_kb.row(make_btn("🔗 Open Link (ভিডিও দেখুন)", url=txt, style="primary"))
        target_s = "rejected" if status_val == "rejected" else "bot_approve"
        adm_kb.row(make_btn("✅ অ্যাপ্রুভ / Re-Accept করুন", callback_data=video_decision_callback("reaccept" if status_val == "rejected" else "approve", sub_id, target_s, "all"), style="success"), make_btn("❌ রিজেক্ট করুন", callback_data=video_decision_callback("reject", sub_id, target_s, "all"), style="danger"))
        for adm_id in get_all_admin_ids():
            safe_send(adm_id, alert_txt, reply_markup=adm_kb)

    if tr_avail:
        ch_p_sub = float(traffic_info.get("channel_page_pct") or 0.0)
        sr_p_sub = float(traffic_info.get("search_pct") or 0.0)
        ex_p_sub = float(traffic_info.get("external_pct") or 0.0)
        ch_lbl_sub = "🎵 TikTok প্রোফাইল/পেজ" if plat == "tiktok" else "📺 YouTube চ্যানেল/পেজ"
        sr_lbl_sub = "🔍 সার্চ (Search)"
        if ex_p_sub > 0 or saved_ext_links:
            tr_sub_note = (
                f"\n📊 <b>ভিউ সোর্স:</b> {ch_lbl_sub}: <b>{ch_p_sub:.1f}%</b> | {sr_lbl_sub}: <b>{sr_p_sub:.1f}%</b> | ⚠️ এক্সটার্নাল লিংক: <b>{ex_p_sub:.1f}%</b>"
            )
        else:
            tr_sub_note = (
                f"\n📊 <b>ভিউ সোর্স:</b> {ch_lbl_sub}: <b>{ch_p_sub:.1f}%</b> | {sr_lbl_sub}: <b>{sr_p_sub:.1f}%</b>"
            )
    else:
        tr_sub_note = "\n📊 <b>ভিউ সোর্স:</b> <i>Unknown / Unavailable</i>"

    if status_val == "rejected":
        user_text = get_msg("video_rejected_msg", title=esc(res.get("title", "Video")[:35]), reason=esc(risk_reason), reversed="0.00") + tr_sub_note
    elif bot_st_val == "approved":
        _unlock_referral_on_first_video_approval(uid)
        user_text = (
            get_msg("video_bot_approved_msg", views=cur_views, credited=f"{initial_credited_amt:.2f}")
            + tr_sub_note
            + f"\n🔐 পরের ভিডিও কোড: <code>{new_next_vid_code}</code>"
        )
    elif bot_st_val == "manual_review":
        user_text = get_msg("verification_manual_review_msg") + (
            f"\n\n🎬 দেখা ভিউ: <b>{cur_views if views_known else 'উপলভ্য নয়'}</b>\n"
            f"📋 স্ট্যাটাস: <b>Pending Review / Unverified ({esc(risk_reason or 'রিভিউ প্রয়োজন')})</b>"
            + tr_sub_note + "\n"
            "💰 রিভিউ শেষ না হওয়া পর্যন্ত কোনো ব্যালেন্স যোগ হবে না।"
        )
    elif bot_st_val == "waiting_views":
        progress_note = "ভিউ সীমা পূর্ণ হলে স্বয়ংক্রিয়ভাবে বট অ্যাপ্রুভ ও ব্যালেন্সে টাকা যোগ হবে।"
        user_text = (
            get_msg("video_views_pending_msg", views=cur_views if views_known else "এখনও পাওয়া যায়নি", minimum=min_init_v, hours=qualification_win_hrs)
            + tr_sub_note
            + f"\n{esc(progress_note)}\n🔐 পরের ভিডিও কোড: <code>{new_next_vid_code}</code>"
        )
    else:
        user_text = get_msg("video_review_needed_msg", reason="অজানা ভিডিও স্ট্যাটাস; admin review দরকার।")
    safe_edit(message.chat.id, getattr(wait_m, 'message_id', None), user_text, reply_markup=build_user_home_keyboard(uid, get_user(uid)), menu_id="user_home")


def process_wd_other_amount_step(message, u, st):
    """Step 3 of 'Another Method' withdrawal: validates amount and submits withdrawal using `st['method']` & `st['other_dest']`."""
    uid = str(message.from_user.id)
    raw_amount = normalize_digits(message.text or "").strip()
    if "," in raw_amount and not re.fullmatch(r"[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?", raw_amount):
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return
    txt = raw_amount.replace(",", "")
    if not re.fullmatch(r"[0-9]{1,10}(?:\.[0-9]{1,2})?", txt):
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return

    amt = round(float(txt), 2)
    bal = float(u.get("balance", 0.0))
    min_w = float(get_setting("min_withdraw", "100.0"))
    max_single_w = float(get_setting("max_single_withdraw", "5000.0"))
    max_d_amt = float(get_setting("max_daily_wd_amount", "5000.0"))
    today_s = datetime.now().strftime("%Y-%m-%d")
    d_amt = float(u.get("daily_wd_amount", 0.0)) if u.get("daily_wd_date") == today_s else 0.0
    rem_amt = max(0.0, round(max_d_amt - d_amt, 2))

    if amt > bal:
        kb_ins = types.InlineKeyboardMarkup()
        kb_ins.row(
            make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
        )
        safe_send(
            message.chat.id,
            f"❌ <b>দুঃখিত! আপনার পর্যাপ্ত পরিমাণে ব্যালেন্স নেই।</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"💰 আপনার বর্তমান ব্যালেন্স: <b>{bal:.2f} টাকা</b>\n"
            f"💸 আপনার অনুরোধকৃত পরিমাণ: <b>{amt:.2f} টাকা</b>\n\n"
            f"অনুগ্রহ করে আপনার বর্তমান ব্যালেন্সের ({bal:.2f}৳) মধ্যে সঠিক পরিমাণ লিখে পাঠান:",
            reply_markup=kb_ins
        )
        return
    if amt <= 0 or amt < min_w or amt > max_single_w or amt > rem_amt:
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return

    st["amount"] = amt
    st["is_other_way"] = True
    dest_val = str(st.get("other_dest") or "").strip()

    class _SyntheticDestMsg:
        def __init__(self, u_obj, c_obj, txt_v):
            self.from_user = u_obj
            self.chat = c_obj
            self.text = txt_v

    process_wd_phone_step(_SyntheticDestMsg(message.from_user, message.chat, dest_val), u, st)


def process_wd_amount_step(message, u, st):
    uid = str(message.from_user.id)
    raw_amount = normalize_digits(message.text or "").strip()
    if "," in raw_amount and not re.fullmatch(r"[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?", raw_amount):
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return
    txt = raw_amount.replace(",", "")
    if not re.fullmatch(r"[0-9]{1,10}(?:\.[0-9]{1,2})?", txt):
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return

    amt = round(float(txt), 2)
    if amt <= 0:
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return
    bal = float(u.get("balance", 0.0))
    min_w = float(get_setting("min_withdraw", "100.0"))
    max_single_w = float(get_setting("max_single_withdraw", "5000.0"))
    max_d_amt = float(get_setting("max_daily_wd_amount", "5000.0"))
    today_s = datetime.now().strftime("%Y-%m-%d")
    d_amt = float(u.get("daily_wd_amount", 0.0)) if u.get("daily_wd_date") == today_s else 0.0
    rem_amt = max(0.0, round(max_d_amt - d_amt, 2))

    if amt > bal:
        kb_ins = types.InlineKeyboardMarkup()
        kb_ins.row(
            make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
            make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
        )
        safe_send(
            message.chat.id,
            f"❌ <b>দুঃখিত! আপনার পর্যাপ্ত পরিমাণে ব্যালেন্স নেই।</b>\n{FULL_WIDTH_DIVIDER}\n"
            f"💰 আপনার বর্তমান ব্যালেন্স: <b>{bal:.2f} টাকা</b>\n"
            f"💸 আপনার অনুরোধকৃত পরিমাণ: <b>{amt:.2f} টাকা</b>\n\n"
            f"অনুগ্রহ করে আপনার বর্তমান ব্যালেন্সের ({bal:.2f}৳) মধ্যে সঠিক পরিমাণ লিখে পাঠান:",
            reply_markup=kb_ins
        )
        return
    if amt < min_w or amt > max_single_w or amt > rem_amt:
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg"))
        return

    st["amount"] = amt
    method = st.get("method", "bKash")

    st["step"] = "awaiting_wd_phone"
    user_memory_states[uid] = st
    prompt_key = "withdraw_uid_prompt_msg" if method == "BattleClub_UID" else "withdraw_destination_prompt_msg"
    prompt = get_msg(prompt_key, method=esc(method))
    kb = types.InlineKeyboardMarkup()
    saved_list = get_user_saved_numbers_list(u, method)
    if method == "BattleClub_UID" and saved_list:
        for s_idx, s_val in enumerate(saved_list):
            lbl_s = f"✅ আপনার যুক্ত UID ব্যবহার করুন ({s_val})" if len(saved_list) == 1 else f"✅ #{s_idx+1} যুক্ত UID ব্যবহার করুন ({s_val})"
            kb.row(make_btn(lbl_s, callback_data=f"uwd_fast_dest:uid:{s_idx}", style="success"))
    elif method != "BattleClub_UID" and saved_list:
        for s_idx, s_val in enumerate(saved_list):
            lbl_s = f"✅ আপনার যুক্ত {method} নাম্বার ব্যবহার করুন ({s_val})" if len(saved_list) == 1 else f"✅ #{s_idx+1} যুক্ত {method} নাম্বার ব্যবহার করুন ({s_val})"
            kb.row(make_btn(lbl_s, callback_data=f"uwd_fast_dest:phone:{s_idx}", style="success"))
    kb.row(make_btn("🔄 অন্য উপায় (Another Method)", callback_data="uwd_other_go", style="primary"))
    kb.row(
        make_btn("✖️ বাতিল করুন", callback_data="umenu:withdraw", style="primary"),
        make_btn("🔙 হোমপেজে যান", callback_data="umenu:cancel_home", style="danger")
    )
    safe_send(message.chat.id, prompt, reply_markup=kb)


def process_wd_phone_step(message, u, st):
    uid = str(message.from_user.id)
    txt = normalize_digits(message.text or "").strip()
    amt = float(st.get("amount", 0.0))
    method = st.get("method", "bKash")
    is_other_way = bool(st.get("is_other_way"))

    if not is_other_way and method not in ("bKash", "Nagad", "Rocket", "BattleClub_UID"):
        safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
        return

    saved_uids_list = get_user_saved_numbers_list(u, "BattleClub_UID")
    app_uid = saved_uids_list[0] if saved_uids_list else format_display_app_uid(u.get("app_uid") or "")
    if method == "BattleClub_UID":
        dest_norm = format_display_app_uid(txt)
        dest_canon = canonicalize_app_uid(txt)
        allowed_canons = {canonicalize_app_uid(x) for x in saved_uids_list if x}
        if not dest_norm or len(re.sub(r"[^0-9A-Z]", "", dest_norm)) < 2:
            safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
            return
        if not is_other_way and allowed_canons and dest_canon not in allowed_canons:
            safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
            return
        txt = dest_norm
        app_uid = dest_norm
    elif method in ("bKash", "Nagad", "Rocket"):
        allow_12 = (method == "Rocket")
        phone = normalize_bd_payment_number(txt, allow_rocket_12=allow_12)
        if not phone:
            safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
            return
        if not is_other_way:
            valid_saved_nums = set()
            for m_iter in ("bKash", "Nagad", "Rocket"):
                valid_saved_nums.update(get_user_saved_numbers_list(u, m_iter))
            if u.get("phone"):
                for p_x in parse_multi_payment_numbers(str(u.get("phone") or ""), allow_rocket_12=True, max_items=4):
                    valid_saved_nums.add(p_x)
            valid_saved_nums.discard("")
            if valid_saved_nums and phone not in valid_saved_nums:
                safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
                return
        txt = phone
    else:
        norm_ph = normalize_bd_payment_number(txt, allow_rocket_12=True)
        clean_dest = norm_ph or re.sub(r"\s+", " ", txt).strip()
        if len(re.sub(r"[^0-9A-Za-z]", "", clean_dest)) < 4:
            safe_send(message.chat.id, get_msg("withdraw_invalid_destination_msg"))
            return
        txt = clean_dest

    wd_id = f"WD_{int(time.time()*1000)}_{uid[-4:]}_{secrets.token_hex(3).upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_s = datetime.now().strftime("%Y-%m-%d")
    max_d_cnt = int(get_setting("max_daily_wd_count", "2"))
    max_d_amt = float(get_setting("max_daily_wd_amount", "5000.0"))
    max_single_w = float(get_setting("max_single_withdraw", "5000.0"))
    try:
        with db_lock:
            conn = get_connection()
            try:
                with begin_immediate_transaction(conn):
                    fresh_min = float(get_setting("min_withdraw", "100.0"))
                    if not (0 < amt <= max_single_w + 1e-9) or amt + 1e-9 < fresh_min:
                        raise ValueError(f"উইথড্র পরিমাণ {fresh_min:.2f}৳ হতে {max_single_w:.2f}৳-এর মধ্যে হতে হবে।")
                    fresh = conn.execute("SELECT balance, daily_wd_date, daily_wd_count, daily_wd_amount FROM users WHERE user_id = ?", (uid,)).fetchone()
                    if not fresh:
                        raise ValueError("অ্যাকাউন্ট পাওয়া যায়নি।")
                    count_today = int(fresh["daily_wd_count"] or 0) if fresh["daily_wd_date"] == today_s else 0
                    amount_today = float(fresh["daily_wd_amount"] or 0.0) if fresh["daily_wd_date"] == today_s else 0.0
                    if float(fresh["balance"] or 0.0) + 1e-9 < amt:
                        raise ValueError("ব্যালেন্স পরিবর্তিত হয়েছে। নতুন পরিমাণ দিয়ে আবার চেষ্টা করুন।")
                    if count_today >= max_d_cnt or amount_today + amt > max_d_amt + 1e-9:
                        raise ValueError("দৈনিক উইথড্র সীমা পূর্ণ হয়েছে।")
                    get_or_create_ledger_entry(
                        conn, uid, "Withdraw Reserve", amt,
                        details=f"Withdraw {wd_id} ({method}{' - Other Way' if is_other_way else ''})",
                        idempotency_key=f"WD_RES:{wd_id}",
                        reference_id=wd_id
                    )
                    conn.execute("""
                        INSERT INTO withdrawals (wd_id, user_id, amount, original_amount, method, dest, app_uid, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                    """, (wd_id, uid, amt, amt, method, txt, app_uid, now_str))
                    conn.execute(
                        "UPDATE users SET daily_wd_date = ?, daily_wd_count = ?, daily_wd_amount = ? WHERE user_id = ?",
                        (today_s, count_today + 1, round(amount_today + amt, 2), uid)
                    )
            finally:
                conn.close()
    except Exception as exc:
        st["step"] = "awaiting_wd_other_amount" if is_other_way else "awaiting_wd_amount"
        user_memory_states[uid] = st
        safe_send(message.chat.id, get_msg("withdraw_invalid_amount_msg") + "\n" + esc(str(exc)))
        return

    user_memory_states.pop(uid, None)
    safe_send(
        message.chat.id,
        get_msg("withdraw_success_msg", amount=f"{amt:.2f}", method=esc(method), dest=esc(txt), app_uid=esc(app_uid), wd_eta=esc(get_setting("wd_eta_text", "১২ থেকে ২৪ ঘণ্টার মধ্যে"))),
        reply_markup=build_user_home_keyboard(uid, get_user(uid)),
        menu_id="user_home"
    )


def _unlock_referral_on_first_video_approval(user_id: str):
    u = get_user(user_id)
    if not u or not u.get("ref_by") or u.get("ref_bonus_credited"):
        return
    process_referral_credit(str(user_id), str(u["ref_by"]), force_unlock=True)


def process_referral_credit(new_uid: str, ref_input: str, force_unlock: bool = False) -> tuple:
    raw_in = str(ref_input or "").strip()
    if not raw_in:
        return False, "সঠিক রেফার কোড দিন!"
    with db_lock:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ? OR UPPER(referral_code) = UPPER(?) OR UPPER(unique_code) = UPPER(?)",
            (raw_in, raw_in, raw_in)
        ).fetchone()
        conn.close()
    if not row:
        return False, "সঠিক রেফার কোড পাওয়া যায়নি!"
    ref_u = dict(row)
    ref_uid = str(ref_u["user_id"])
    if str(new_uid) == ref_uid:
        return False, "নিজের রেফার কোড নিজেকে রিডিম করা যাবে না!"

    if get_setting("ref_unlock_on_first_video", "0") == "1" and not force_unlock:
        with db_lock:
            conn = get_connection()
            app_cnt = conn.execute(
                "SELECT COUNT(*) as c FROM videos WHERE user_id = ? AND (bot_status = 'approved' OR admin_status = 'approved') AND admin_status != 'rejected'",
                (str(new_uid),)
            ).fetchone()["c"]
            if app_cnt == 0:
                with conn:
                    conn.execute("UPDATE users SET ref_by = ? WHERE user_id = ? AND redeemed_ref = 0", (ref_uid, str(new_uid)))
                conn.close()
                return False, "রেফার কোডটি আপনার একাউন্টে সংরক্ষিত হয়েছে! আপনার ১ম ভিডিও অ্যাপ্রুভ হলেই রেফার ও রিডিম বোনাস স্বয়ংক্রিয়ভাবে আনলক হবে।"
            conn.close()

    today_s = datetime.now().strftime("%Y-%m-%d")
    max_d = int(get_setting("max_daily_referrals", "5"))
    ref_bonus = float(get_setting("ref_bonus", "10.0"))
    redeem_bonus = float(get_setting("redeem_bonus", "5.0"))
    failure = ""
    with db_lock:
        conn = get_connection()
        try:
            with conn:
                chk_u = conn.execute("SELECT redeemed_ref FROM users WHERE user_id = ?", (str(new_uid),)).fetchone()
                ref_current = conn.execute("SELECT daily_ref_date, daily_ref_count FROM users WHERE user_id = ?", (ref_uid,)).fetchone()
                if not chk_u:
                    failure = "ইউজার অ্যাকাউন্ট পাওয়া যায়নি।"
                elif chk_u["redeemed_ref"]:
                    failure = "আপনি ইতিমধ্যে একবার রেফার কোড রিডিম করেছেন!"
                elif not ref_current:
                    failure = "রেফারকারী অ্যাকাউন্ট পাওয়া যায়নি।"
                else:
                    d_cnt = int(ref_current["daily_ref_count"] or 0) if ref_current["daily_ref_date"] == today_s else 0
                    if d_cnt >= max_d:
                        failure = f"এই রেফারকারীর আজকের দৈনিক রেফারেল লিমিট ({max_d} জন) পূর্ণ হয়ে গেছে!"
                    else:
                        cur = conn.execute(
                            "UPDATE users SET redeemed_ref = 1, ref_bonus_credited = 1, ref_by = ? WHERE user_id = ? AND redeemed_ref = 0",
                            (ref_uid, str(new_uid))
                        )
                        if cur.rowcount != 1:
                            failure = "আপনি ইতিমধ্যে একবার রেফার কোড রিডিম করেছেন!"
                        else:
                            if ref_bonus > 0:
                                get_or_create_ledger_entry(conn, ref_uid, "Referral Bonus", ref_bonus, details=f"Referral from {new_uid}", idempotency_key=f"REF_BONUS:{ref_uid}:{new_uid}", reference_id=new_uid)
                            if redeem_bonus > 0:
                                get_or_create_ledger_entry(conn, str(new_uid), "Redeem Bonus", redeem_bonus, details=f"Redeemed code of {ref_uid}", idempotency_key=f"REDEEM_BONUS:{new_uid}", reference_id=ref_uid)
                            conn.execute("UPDATE users SET ref_count = ref_count + 1, daily_ref_date = ?, daily_ref_count = ? WHERE user_id = ?", (today_s, d_cnt + 1, ref_uid))
        finally:
            conn.close()
    if failure:
        return False, failure
    try:
        safe_send(int(ref_uid), f"🎉 <b>নতুন রেফারেল বোনাস!</b>\nইউজার <code>{new_uid}</code> আপনার রেফার কোড রিডিম করায় আপনার ব্যালেন্সে <b>{ref_bonus:.2f} টাকা</b> যোগ হয়েছে!")
    except Exception:
        pass
    return True, f"সফলভাবে রেফার কোড রিডিম হয়েছে! আপনার ব্যালেন্সে <b>{redeem_bonus:.2f}৳</b> রিডিম বোনাস এবং রেফারকারীর ব্যালেন্সে <b>{ref_bonus:.2f}৳</b> যোগ হয়েছে।"


def process_redeem_step(message, u):
    uid = str(message.from_user.id)
    ref_cand = (message.text or "").strip()
    user_memory_states.pop(uid, None)
    if u.get("redeemed_ref"):
        safe_send(message.chat.id, "⚠️ আপনি ইতিমধ্যে রেফার কোড রিডিম করেছেন!", reply_markup=build_user_home_keyboard(uid, u), menu_id="user_home")
        return
    ok, msg = process_referral_credit(uid, ref_cand)
    safe_send(message.chat.id, ("✅ " if ok else "❌ ") + msg, reply_markup=build_user_home_keyboard(uid, get_user(uid)), menu_id="user_home")


def _polite_api_delay(delay_sec: float = None):
    d = float(delay_sec if delay_sec is not None else BATCH_REQUEST_DELAY_SEC)
    if d <= 0:
        return
    if getattr(bot.send_message, "__name__", "") not in ("_patched_send_message", "send_message"):
        return
    if os.getenv("UNITTEST_MODE") == "1":
        return
    time.sleep(min(2.0, max(0.05, d)))


def _execute_broadcast_queue_delivery(chat_id, uid: str, q_list: list):
    """Delivers all queued broadcast messages (1 or multiple) to all users with 5-pass automatic retry."""
    if not q_list:
        return
    first_ctype = str(q_list[0].get("content_type") or "text")
    with db_lock:
        bc_job = create_broadcast_job(admin_id=uid, content_type=first_ctype, max_retries=5)
    job_id = bc_job["job_id"]

    for pass_num in range(1, 6):
        with db_lock:
            pending_targets = sync_and_get_pending_broadcast_targets(job_id, max_retries=5)
        if not pending_targets:
            break
        for b_start in range(0, len(pending_targets), 10):
            batch = pending_targets[b_start:b_start + 10]
            for target in batch:
                t_uid_str = str(target["user_id"])
                if not t_uid_str.isdigit():
                    with db_lock:
                        record_broadcast_delivery_attempt(job_id, t_uid_str, False, "Invalid numeric chat_id")
                    continue
                t_chat = int(t_uid_str)
                try:
                    for m_item in q_list:
                        mc_type = m_item.get("content_type", "text")
                        m_rich = m_item.get("rich_html", "")
                        if m_rich and mc_type == "text":
                            safe_send(t_chat, m_rich, track_ui=False, auto_clean_prev=False)
                        else:
                            bot.copy_message(chat_id=t_chat, from_chat_id=m_item.get("from_chat_id", chat_id), message_id=m_item.get("message_id"))
                    with db_lock:
                        record_broadcast_delivery_attempt(job_id, t_uid_str, True, "")
                except Exception as bc_err:
                    with db_lock:
                        record_broadcast_delivery_attempt(job_id, t_uid_str, False, str(bc_err))
                _polite_api_delay(BATCH_REQUEST_DELAY_SEC)
            if b_start + 10 < len(pending_targets):
                _polite_api_delay(BATCH_REQUEST_DELAY_SEC)

    with db_lock:
        final_stats = finalize_broadcast_job(job_id)

    kb = types.InlineKeyboardMarkup()
    kb.row(make_btn("📢 আরও ব্রডকাস্ট পাঠান", callback_data="adm_broadcast_prompt", style="primary"))
    kb.row(make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
    safe_send(
        chat_id,
        f"📢 <b>ব্রডকাস্ট মেসেজ ডেলিভারি রিপোর্ট ({len(q_list)}টি মেসেজ — ৫ ধাপ স্বয়ংক্রিয় রিট্রাই সম্পন্ন)!</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        f"• পাঠানো মেসেজের সংখ্যা: <b>{len(q_list)} টি</b>\n"
        f"• মোট টার্গেট ইউজার: <b>{final_stats['total']} জন</b>\n"
        f"• সফলভাবে মেসেজ পেয়েছেন: <b>{final_stats['sent']} জন</b>\n"
        f"• প্রথমবার ব্যর্থ হওয়ার পর পুনরায় চেষ্টায় সফল: <b>{final_stats['retried_ok']} জন</b>\n"
        f"• ৫ বার চেষ্টার পরও ব্যর্থ/ব্লকড: <b>{final_stats['failed']} জন</b>",
        reply_markup=kb
    )


def process_admin_text_input(message, st):
    uid = str(message.from_user.id)
    act = st.get("admin_action")
    txt = (message.text or "").strip()
    user_memory_states.pop(uid, None)

    if act == "wd_paid_trx_note":
        wid = st.get("wd_id")
        command = txt.strip().upper()
        if command == "CANCEL":
            safe_send(message.chat.id, f"✖️ উইথড্র <code>{esc(wid)}</code>-এর পেমেন্ট অ্যাকশন বাতিল করা হয়েছে।")
            return
        trx_val = "SKIP" if (not txt or command == "SKIP") else txt
        with db_lock:
            conn = get_connection()
            w = conn.execute("SELECT * FROM withdrawals WHERE wd_id = ?", (wid,)).fetchone()
            if not w or w["status"] != "pending":
                conn.close()
                safe_send(message.chat.id, "⚠️ উইথড্র রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে!")
                return
            amt = float(w["amount"])
            t_uid = w["user_id"]
            with conn:
                res_paid = admin_mark_withdrawal_paid(conn, wd_id=wid, admin_id=uid, trx_id=trx_val, payment_note=trx_val)
            conn.close()
        try:
            note_disp = f"\n🧾 TrxID/Note: <code>{esc(res_paid['trx_id'])}</code>" if res_paid.get("trx_id") else ""
            safe_send(int(t_uid), get_msg("withdraw_paid_msg", amount=f"{amt:.2f}", method=esc(w["method"]), dest=esc(w["dest"])) + note_disp)
        except Exception:
            pass
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔎 উইথড্র কার্ডে ফিরে যান", callback_data=f"adm_wd_detail:{wid}", style="primary"))
        safe_send(message.chat.id, f"✅ উইথড্র <code>{esc(wid)}</code> সফলভাবে <b>PAID</b> মার্ক করা হয়েছে! (TrxID/Note: <code>{esc(res_paid.get('trx_id') or 'SKIP')}</code>)", reply_markup=kb)
        return

    if act == "custom_reject_video_reason":
        sub_id = st.get("sub_id")
        command = txt.strip().upper()
        if command == "CANCEL":
            safe_send(message.chat.id, f"✖️ ভিডিও <code>{esc(sub_id)}</code>-এর রিজেক্ট বাতিল করা হয়েছে।")
            return
        if command == "SKIP":
            txt = "অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি / শর্ত পূরণ হয়নি।"
        elif not txt:
            user_memory_states[uid] = st
            safe_send(message.chat.id, "⚠️ কারণ লিখুন, <code>SKIP</code> লিখে ডিফল্ট কারণ দিন, অথবা <code>CANCEL</code> লিখে বাতিল করুন।")
            return
        with db_lock:
            conn = get_connection()
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
            if not v:
                conn.close()
                return
            with conn:
                rej_info = admin_reject_video_with_reversal(conn, sub_id=sub_id, rejection_reason=txt, admin_id=uid, force_admin_clawback=True)
            conn.close()
        if rej_info.get("permanent_protected"):
            safe_send(message.chat.id, "🔒 <b>সুরক্ষিত (Permanent Approved):</b> এই ভিডিওটি Permanent Approve স্টেজে লক রয়েছে, তাই ইউজারের ব্যালেন্স অক্ষত রাখা হয়েছে এবং কোনো টাকা কাটা হয়নি।")
            return
        fin_note = _build_rejection_financial_summary_note(rej_info, v["user_id"])
        rich_reason = extract_rich_html_text(message) if (command != "SKIP" and (getattr(message, "entities", None) or getattr(message, "caption_entities", None))) else esc(txt)
        try:
            safe_send(int(v["user_id"]), get_msg("video_rejected_msg", title=esc(v["title"][:35]), reason=rich_reason, reversed=f"{float(rej_info.get('reversed_amount', 0.0)):.2f}") + fin_note)
        except Exception:
            pass
        safe_send(message.chat.id, get_msg("video_rejection_admin_msg", sub_id=esc(sub_id), reversed=f"{float(rej_info.get('reversed_amount', 0.0)):.2f}"))
        return

    if act == "search_user":
        q = f"%{txt}%"
        with db_lock:
            conn = get_connection()
            rows = conn.execute("SELECT * FROM users WHERE user_id LIKE ? OR username LIKE ? OR name LIKE ? OR phone LIKE ? OR bkash_number LIKE ? OR nagad_number LIKE ? OR rocket_number LIKE ? OR app_uid LIKE ? LIMIT 20", (q, q, q, q, q, q, q, q)).fetchall()
            conn.close()
        kb = types.InlineKeyboardMarkup()
        for r in rows:
            u_d = dict(r)
            kb.row(make_btn(f"👤 {get_user_label(u_d)} — {float(u_d['balance']):.1f}৳", callback_data=f"adm_uview:{u_d['user_id']}", style="success"))
        kb.row(make_btn("🔙 ইউজার লিস্টে যান", callback_data="adm_ulist:0", style="danger"))
        safe_send(message.chat.id, f"🔍 <b>সার্চ ফলাফল ({len(rows)} জন পাওয়া গেছে):</b>\n{FULL_WIDTH_DIVIDER}", reply_markup=kb)
        return

    if act == "change_user_pwd":
        t_uid = st["target_uid"]
        new_h = hash_password(txt)
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET password_plain = '', password_hash = ? WHERE user_id = ?", (new_h, t_uid))
                log_audit_event(uid, "Admin Change Password", "Changed user password", target_user_id=t_uid, conn=conn)
            conn.close()
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে যান", callback_data=f"adm_uview:{t_uid}", style="primary"))
        safe_send(message.chat.id, "✅ ইউজারের পাসওয়ার্ড সফলভাবে পরিবর্তন ও সুরক্ষিত করা হয়েছে!", reply_markup=kb)
        return

    if act == "update_crit":
        try:
            field = st["field"]
            if field == "verification_link":
                val = "" if txt.strip().lower() in ("none", "nane", "0", "off") else txt.strip()
            else:
                clean_txt = normalize_digits(txt).strip().lower()
                if field in ("submission_window_hours", "qualification_window_hours") and clean_txt.endswith("d"):
                    val = int(round(float(clean_txt[:-1].strip()) * 24))
                else:
                    val = float(clean_txt) if "." in clean_txt else int(clean_txt)
            update_platform_criteria(st["plat"], field, val)
            if field == "verification_link":
                set_setting("verification_link", val)
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 প্ল্যাটফর্ম শর্তে ফিরে যান", callback_data=f"adm_crit:view:{st['plat']}", style="primary"))
            safe_send(message.chat.id, f"✅ <b>{PLATFORMS[st['plat']]['title']}</b>-এর <b>{field}</b> সফলভাবে <b>{esc(str(val or 'none'))}</b> সেট করা হয়েছে!", reply_markup=kb)
        except Exception as e:
            safe_send(message.chat.id, f"❌ ভুল মান: {e}")
        return

    if act == "adjust_user_balance":
        t_uid = st["target_uid"]
        mode = st["mode"]
        try:
            amt = round(float(normalize_digits(txt)), 2)
            with db_lock:
                conn = get_connection()
                with conn:
                    tx_t = "Admin Credit" if mode == "add" else "Admin Debit"
                    get_or_create_ledger_entry(
                        conn, t_uid, tx_t, amt,
                        details=f"Admin {uid} balance adjustment ({mode})",
                        idempotency_key=f"ADMIN_BAL:{t_uid}:{mode}:{amt}:{int(time.time()*1000)}",
                        admin_id=uid
                    )
                conn.close()
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 ইউজার প্রোফাইলে যান", callback_data=f"adm_uview:{t_uid}", style="primary"))
            safe_send(message.chat.id, f"✅ ইউজারের ব্যালেন্স সফলভাবে <b>{amt:.2f}৳ ({mode.upper()})</b> সমন্বয় করা হয়েছে!", reply_markup=kb)
        except Exception as e:
            safe_send(message.chat.id, f"❌ ভুল সংখ্যা: {e}")
        return

    if act == "edit_user_field":
        t_uid = st["target_uid"]
        with db_lock:
            conn = get_connection()
            with conn:
                conn.execute("UPDATE users SET name = ? WHERE user_id = ?", (txt, t_uid))
                log_audit_event(uid, "Admin Profile Edit", f"Updated name to {txt}", target_user_id=t_uid, conn=conn)
            conn.close()
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ইউজার প্রোফাইলে ফিরে যান", callback_data=f"adm_uview:{t_uid}", style="primary"))
        safe_send(message.chat.id, f"✅ ইউজারের তথ্য সফলভাবে (<b>{esc(txt)}</b>) আপডেট করা হয়েছে!", reply_markup=kb)
        return

    if act == "set_setting_num":
        if st.get("key") == "wd_eta_text":
            rich_eta = extract_rich_html_text(message) or esc(txt)
            set_setting("wd_eta_text", rich_eta)
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 ফিরে যান", callback_data=st.get("back", "adm_settings_hub"), style="primary"))
            safe_send(message.chat.id, f"✅ উইথড্র পেমেন্ট পাওয়ার সম্ভাব্য সময় সফলভাবে <b>{rich_eta}</b> সেট করা হয়েছে!", reply_markup=kb)
            return
        try:
            clean_txt = normalize_digits(txt).strip().lower()
            if st.get("key") in ("submission_window_hours", "qualification_window_hours") and clean_txt.endswith("d"):
                clean_txt = str(int(round(float(clean_txt[:-1].strip()) * 24)))
            set_setting(st["key"], clean_txt)
            kb = types.InlineKeyboardMarkup()
            kb.row(make_btn("🔙 ফিরে যান", callback_data=st.get("back", "adm_settings_hub"), style="primary"))
            safe_send(message.chat.id, f"✅ <b>{st['key']}</b> সফলভাবে <b>{clean_txt}</b> আপডেট করা হয়েছে!", reply_markup=kb)
        except Exception as e:
            safe_send(message.chat.id, f"❌ কনফিগারেশন ত্রুটি: {e}")
        return

    if act == "set_hashtags":
        set_setting("global_required_code", txt)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:hashtag_yt", style="primary"))
        safe_send(message.chat.id, f"✅ বাধ্যতামূলক হ্যাশট্যাগ আপডেট হয়েছে:\n<code>{esc(txt)}</code>", reply_markup=kb)
        return

    if act == "set_ver_link":
        val = "" if txt.lower() in ("none", "nane", "0", "off") else txt.strip()
        set_setting("verification_link", val)
        for pk in ("youtube", "tiktok"):
            try:
                update_platform_criteria(pk, "verification_link", val)
            except Exception:
                pass
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:hashtag_yt", style="primary"))
        safe_send(message.chat.id, f"✅ বায়ো ও ভিডিও ভেরিফিকেশন লিংক আপডেট করা হয়েছে:\n<code>{esc(val or 'none')}</code>", reply_markup=kb)
        return

    if act == "set_top_yt":
        val = "" if txt.lower() in ("none", "nane") else txt
        set_setting("home_youtube_link", val)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:hashtag_yt", style="primary"))
        safe_send(message.chat.id, "✅ স্টার্ট ও হোমপেজ টপ ইউটিউব ভিডিও লিংক আপডেট করা হয়েছে!", reply_markup=kb)
        return

    if act == "set_req_link_config":
        set_setting("required_link_config", txt)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:hashtag_yt", style="primary"))
        safe_send(message.chat.id, f"✅ Required Link Configuration আপডেট করা হয়েছে: <code>{esc(txt)}</code>", reply_markup=kb)
        return

    if act == "set_support_link":
        set_setting("support_link", txt)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:support_group", style="primary"))
        safe_send(message.chat.id, f"✅ সাপোর্ট লিংক আপডেট করা হয়েছে: <code>{esc(txt)}</code>", reply_markup=kb)
        return

    if act == "set_group_link":
        set_setting("group_link", txt)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 ফিরে যান", callback_data="adm_shub:support_group", style="primary"))
        safe_send(message.chat.id, f"✅ গ্রুপ লিংক আপডেট করা হয়েছে: <code>{esc(txt)}</code>", reply_markup=kb)
        return

    if act == "create_cbtn_name":
        side = st.get("side", "user")
        parent_lk = st.get("parent_layout") or ("admin_home" if side == "admin" else "user_home")
        raw_ents = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or serialize_message_entities(message)
        st_obj = getattr(message, "sticker", None)
        st_em = str(getattr(st_obj, "emoji", "") or "").strip() if st_obj else ""
        st_cid = str(getattr(st_obj, "custom_emoji_id", "") or "").strip() if st_obj else ""
        clean_lbl, em_id = normalize_button_label_and_extract_emoji(
            txt,
            entities=raw_ents,
            sticker_emoji=st_em,
            sticker_custom_emoji_id=st_cid,
            keep_fallback_in_text=False
        )
        if not clean_lbl and st_obj:
            clean_lbl = "কাস্টম বাটন" if em_id else ensure_visible_emoji_presentation(f"{st_em or '📂'} কাস্টম বাটন")
        if not clean_lbl:
            safe_send(message.chat.id, "⚠️ অনুগ্রহ করে নতুন বাটনটির একটি বৈধ নাম লিখে পাঠান:")
            return
        cbtn_id = st.get("cbtn_key") if str(st.get("cbtn_key", "")).startswith("cbtn_") else generate_unique_custom_button_id()
        st.update({
            "admin_action": "create_cbtn_msg",
            "cbtn_key": cbtn_id,
            "side": side,
            "parent_layout": parent_lk,
            "destination_layout": st.get("destination_layout") or f"custom_page_{cbtn_id}",
            "label": clean_lbl,
            "custom_emoji_id": em_id
        })
        user_memory_states[uid] = st
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("⏭️ ডিফল্ট স্ট্যাটাস মেসেজ রাখুন ও সাব-বাটন নির্বাচন করুন", callback_data="adm_cbw_skip_msg", style="success"))
        kb.row(make_btn("🔙 বাতিল করুন", callback_data="adm_cbl", style="danger"))
        rich_name_preview = (
            f'<tg-emoji emoji-id="{em_id}">{_resolve_custom_emoji_fallback_char(em_id, "❤️")}</tg-emoji> <b>{esc(clean_lbl)}</b>'
            if em_id else f"<b>{esc(clean_lbl)}</b>"
        )
        safe_send(
            message.chat.id,
            f"✅ নতুন বাটনের নাম সেট হয়েছে: {rich_name_preview} (ID: <code>{esc(cbtn_id)}</code>)\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"📝 <b>ধাপ ২ — বাটনের উপরের স্ট্যাটাস / টেমপ্লেট মেসেজ দিন:</b>\n"
            f"এই বাটনের ভেতরে ঢুকলে উপরে কী মেসেজ বা স্ট্যাটাস দেখাবে তা <b>Premium Custom Emoji</b> সহ লিখে পাঠান (অথবা নিচের Skip বাটনে চাপ দিন):",
            reply_markup=kb
        )
        return

    if act == "create_cbtn_msg":
        cbtn_key = st.get("cbtn_key") or generate_unique_custom_button_id()
        side = st.get("side", "user")
        parent_lk = st.get("parent_layout") or ("admin_home" if side == "admin" else "user_home")
        lbl = st.get("label", "কাস্টম বাটন")
        rich_msg = extract_rich_html_text(message) or txt or f"📂 <b>{esc(lbl)}</b>"
        ents = serialize_message_entities(message)
        st.update({
            "admin_action": "create_cbtn_preview",
            "cbtn_key": cbtn_key,
            "side": side,
            "parent_layout": parent_lk,
            "destination_layout": st.get("destination_layout") or f"custom_page_{cbtn_key}",
            "status_msg": rich_msg,
            "raw_status_msg": txt,
            "status_msg_entities": ents
        })
        user_memory_states[uid] = st
        # Show Final Preview and Confirm Button BEFORE writing to database!
        _render_custom_button_final_preview(message.chat.id, uid, st)
        return

    if act == "set_lb_rank_badge":
        rk_num = int(st.get("rank_num") or 1)
        rich_b = extract_rich_html_text(message) or esc(txt)
        set_setting(f"leaderboard_rank_{rk_num}_badge", rich_b)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 লিডারবোর্ড কাস্টমাইজারে যান", callback_data="adm_lb_customizer", style="success"))
        kb.row(make_btn("🏠 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger"))
        safe_send(message.chat.id, f"✅ <b>লিডারবোর্ড Rank #{rk_num} ব্যাজ সফলভাবে আপডেট হয়েছে:</b>\n{rich_b}", reply_markup=kb)
        return

    if act == "rename_btn":
        b_key = st["b_key"]
        l_key = resolve_layout_key(st.get("l_key", "user_home"))
        sc = short_layout_code(l_key)
        old_lbl = get_btn_raw_label(b_key)
        BUTTON_RUNTIME_CAPS["allow_custom_emoji"] = True
        BUTTON_RUNTIME_CAPS["allow_style"] = True

        raw_ents = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or serialize_message_entities(message)
        st_obj = getattr(message, "sticker", None)
        st_em = str(getattr(st_obj, "emoji", "") or "").strip() if st_obj else ""
        st_cid = str(getattr(st_obj, "custom_emoji_id", "") or "").strip() if st_obj else ""

        # Allow clearing custom emoji by typing 'none' or 'clear', or setting raw numeric custom_emoji_id
        if txt.lower() in ("none", "clear"):
            set_btn_emoji_val(b_key, "")
            clean_new_lbl = strip_leading_default_emojis(old_lbl)
            extracted_em_id = ""
        elif re.fullmatch(r"[0-9]{12,25}", normalize_digits(txt)):
            extracted_em_id = normalize_digits(txt)
            set_btn_emoji_val(b_key, extracted_em_id)
            clean_new_lbl = strip_leading_default_emojis(old_lbl)
        else:
            clean_new_lbl, extracted_em_id = normalize_button_label_and_extract_emoji(
                txt,
                entities=raw_ents,
                sticker_emoji=st_em,
                sticker_custom_emoji_id=st_cid,
                keep_fallback_in_text=False
            )
            if extracted_em_id:
                set_btn_emoji_val(b_key, extracted_em_id)
                if not clean_new_lbl:
                    # Admin sent only a Custom Emoji/Sticker -> strip leading default emoji from old label without re-adding a normal emoji!
                    clean_new_lbl = strip_leading_default_emojis(old_lbl)
            elif not clean_new_lbl and st_obj and st_em:
                vis_st_em = ensure_visible_emoji_presentation(st_em)
                stripped_old = strip_leading_default_emojis(old_lbl)
                clean_new_lbl = f"{vis_st_em} {stripped_old}".strip()

        if clean_new_lbl:
            set_btn_label_val(b_key, clean_new_lbl)

        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=message.chat.id)
        new_Preview_lbl = apply_button_text_design(get_btn_raw_label(b_key), get_btn_design(b_key))
        active_em_id = get_btn_emoji(b_key)
        rich_after_change = (
            f'<tg-emoji emoji-id="{active_em_id}">{_resolve_custom_emoji_fallback_char(active_em_id, "✨")}</tg-emoji> <b>{esc(new_Preview_lbl)}</b>'
            if active_em_id else f"<b>{esc(new_Preview_lbl)}</b>"
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                new_Preview_lbl,
                callback_data=f"adm_bitem:{b_key}:{sc}",
                style=get_btn_style(b_key),
                icon_custom_emoji_id=(active_em_id or None),
                btn_key=b_key,
                design_style="normal"
            )
        )
        kb.row(
            make_btn("🎛️ বাটন কাস্টমাইজারে যান", callback_data=f"adm_bitem:{b_key}:{sc}", style="success"),
            make_btn("🔙 পেজ লেআউটে যান", callback_data=f"adm_elayout:{sc}", style="primary")
        )
        safe_send(
            message.chat.id,
            f"✅ <b>বাটনের নাম ও প্রিমিয়াম ইমোজি সফলভাবে আপডেট হয়েছে! (লাইভ প্রিভিউ):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• আগের নাম: <code>{esc(old_lbl)}</code>\n"
            f"• পরিবর্তন করার পর (After Change): {rich_after_change}\n"
            f"• Custom Emoji ID: <code>{esc(active_em_id or 'None')}</code>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            "👇 নিচের প্রথম বাটনটিতে নতুন নামের লাইভ প্রিভিউ দেখুন (এটি উপরের ও নিচের উভয় বাটনে কাজ করবে):",
            reply_markup=kb
        )
        return

    if act == "set_btn_emoji":
        b_key = st["b_key"]
        l_key = resolve_layout_key(st.get("l_key", "user_home"))
        sc = short_layout_code(l_key)
        BUTTON_RUNTIME_CAPS["allow_custom_emoji"] = True
        BUTTON_RUNTIME_CAPS["allow_style"] = True
        raw_ents = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or serialize_message_entities(message)
        st_obj = getattr(message, "sticker", None)
        st_em = str(getattr(st_obj, "emoji", "") or "").strip() if st_obj else ""
        st_cid = str(getattr(st_obj, "custom_emoji_id", "") or "").strip() if st_obj else ""
        _, custom_id = normalize_button_label_and_extract_emoji(
            txt,
            entities=raw_ents,
            sticker_emoji=st_em,
            sticker_custom_emoji_id=st_cid,
            keep_fallback_in_text=False
        )
        if not custom_id and txt.lower() not in ("none", "clear", "0"):
            digits_only = re.sub(r"[^0-9]", "", normalize_digits(txt))
            if len(digits_only) >= 10:
                custom_id = digits_only
        if txt.lower() in ("none", "clear", "0"):
            custom_id = ""
        set_btn_emoji_val(b_key, custom_id)
        if custom_id:
            # If the button still had its uncustomized default label (with a default leading emoji),
            # automatically strip that default leading emoji so the old default emoji never remains alongside the custom emoji!
            cur_raw_l = get_btn_raw_label(b_key)
            if not is_btn_label_admin_customized(b_key) or cur_raw_l == DEFAULT_BUTTON_LABELS.get(b_key, ""):
                stripped_lbl = strip_leading_default_emojis(cur_raw_l)
                if stripped_lbl:
                    set_btn_label_val(b_key, stripped_lbl)
        sync_all_menus_after_button_change(trigger_uid=uid, notify_chat_id=message.chat.id)
        disp_lbl = apply_button_text_design(get_btn_raw_label(b_key), get_btn_design(b_key))
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn(
                disp_lbl,
                callback_data=f"adm_bitem:{b_key}:{sc}",
                style=get_btn_style(b_key),
                icon_custom_emoji_id=(custom_id or None),
                btn_key=b_key,
                design_style="normal"
            )
        )
        kb.row(
            make_btn("🔙 বাটন কাস্টমাইজারে ফিরে যান", callback_data=f"adm_bitem:{b_key}:{sc}", style="primary"),
            make_btn("🔙 পেজ লেআউটে যান", callback_data=f"adm_elayout:{sc}", style="success")
        )
        rich_em_prev = (
            f'<tg-emoji emoji-id="{custom_id}">{_resolve_custom_emoji_fallback_char(custom_id, st_em or "✨")}</tg-emoji> '
            if custom_id else ""
        )
        safe_send(
            message.chat.id,
            f"✅ {rich_em_prev}বাটনের <code>icon_custom_emoji_id</code> সফলভাবে <code>{esc(custom_id or 'Cleared')}</code> সেট করা হয়েছে! (উপরের ও নিচের উভয় বাটনে কার্যকর হবে)\nনিচে লাইভ প্রিভিউ দেখুন:",
            reply_markup=kb
        )
        return

    if act == "add_msg_custom_btn":
        mk = st["msg_key"]
        raw_t = (message.text or message.caption or "").strip()
        raw_ents = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or serialize_message_entities(message)
        _, msg_em_id = normalize_button_label_and_extract_emoji(raw_t, entities=raw_ents, keep_fallback_in_text=False)
        new_rows = list(CACHE_MESSAGE_CUSTOM_BUTTONS.get(mk) or [])
        added_cnt = 0
        for line in raw_t.splitlines():
            line_s = line.strip()
            if not line_s or "|" not in line_s:
                continue
            parts = [p.strip() for p in line_s.split("|")]
            if len(parts) < 2:
                continue
            b_lbl_raw = parts[0]
            b_target = parts[1]
            b_col = parts[2].lower() if len(parts) > 2 and parts[2].lower() in ("success", "danger", "primary") else "primary"
            b_em = parts[3] if len(parts) > 3 else (msg_em_id or "")
            b_lbl_clean, line_em = normalize_button_label_and_extract_emoji(b_lbl_raw, keep_fallback_in_text=False)
            eff_em = re.sub(r"[^0-9]", "", str(line_em or b_em or ""))
            new_rows.append([{
                "text": b_lbl_clean or b_lbl_raw,
                "target": b_target,
                "style": b_col,
                "icon_custom_emoji_id": eff_em
            }])
            added_cnt += 1
        if added_cnt == 0:
            safe_send(message.chat.id, "⚠️ সঠিক ফরম্যাটে লিখুন: <code>বাটনের নাম | লিংক বা Callback | success/danger/primary</code>")
            return
        with db_lock:
            set_dynamic_message_button_config(mk, button_mode="custom", custom_buttons=new_rows, updated_by=uid)
        CACHE_MESSAGE_BUTTON_MODES[mk] = "custom"
        CACHE_MESSAGE_CUSTOM_BUTTONS[mk] = new_rows
        user_memory_states.pop(uid, None)
        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn("🔙 মেসেজ এডিটরে ফিরে যান", callback_data=f"adm_emsg:{mk}", style="primary"))
        safe_send(
            message.chat.id,
            f"✅ <b>মেসেজ <code>{esc(mk)}</code>-এর নিচে {added_cnt}টি কাস্টম বাটন সফলভাবে যুক্ত হয়েছে!</b>",
            reply_markup=kb
        )
        return

    if act == "save_custom_msg":
        mk = st["msg_key"]
        raw_t = message.text or message.caption or ""
        rich_html = extract_rich_html_text(message)
        ents = serialize_message_entities(message)
        set_msg(mk, rich_html, raw_text=raw_t, entities=ents, updated_by=uid)
        kb = types.InlineKeyboardMarkup()
        kb.row(
            make_btn("📜 পূর্ববর্তী মেসেজ দেখুন / রোলব্যাক", callback_data=f"adm_emsg_hist:{mk}", style="primary"),
            make_btn("🔄 ডিফল্টে রিসেট করুন", callback_data=f"adm_emsg_reset:{mk}", style="danger")
        )
        kb.row(make_btn("🔙 মেসেজ এডিটরে যান", callback_data="adm_msg_hub", style="danger"))
        # Part 1, Item 8: Show Live Preview of the saved message immediately!
        safe_send(
            message.chat.id,
            f"✅ <b>মেসেজটি সব ফরম্যাটিং ও প্রিমিয়াম কাস্টম ইমোজি অক্ষুণ্ণ রেখে সেভ হয়েছে!</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"👁️ <b>লাইভ প্রিভিউ (Live Preview — ইউজাররা যেভাবে দেখবে):</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"{get_msg(mk)}",
            reply_markup=kb
        )
        return

    if act == "broadcast_msg":
        c_type = str(getattr(message, "content_type", "text") or "text")
        raw_b = message.text or message.caption or ""
        if c_type == "text" and raw_b.strip().upper() in ("DONE", "SEND", "ডান", "পাঠান") and st.get("queue"):
            q_list = list(st.get("queue") or [])
            _execute_broadcast_queue_delivery(message.chat.id, uid, q_list)
            return
        rich_b = extract_rich_html_text(message) if raw_b else ""
        q_list = list(st.get("queue") or [])
        q_list.append({
            "content_type": c_type,
            "raw_text": raw_b,
            "rich_html": rich_b,
            "from_chat_id": message.chat.id,
            "message_id": getattr(message, "message_id", None)
        })
        st["queue"] = q_list
        user_memory_states[uid] = st

        # If caller explicitly requested immediate single-message broadcast (e.g. legacy test), execute immediately
        if st.get("immediate"):
            user_memory_states.pop(uid, None)
            _execute_broadcast_queue_delivery(message.chat.id, uid, q_list)
            return

        kb = types.InlineKeyboardMarkup()
        kb.row(make_btn(f"✅ ডান / সব পাঠান ({len(q_list)}টি মেসেজ)", callback_data="adm_bc_done", style="success"))
        kb.row(
            make_btn("🗑️ কিউ ক্লিয়ার করুন", callback_data="adm_bc_clear", style="primary"),
            make_btn("🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান", callback_data="admin_hub", style="danger")
        )
        safe_send(
            message.chat.id,
            f"📥 <b>ব্রডকাস্ট কিউতে মেসেজ #{len(q_list)} যুক্ত হয়েছে ({esc(c_type.upper())})!</b>\n"
            f"{FULL_WIDTH_DIVIDER}\n"
            f"• আপনি চাইলে আরও মেসেজ (টেক্সট, ভয়েস, অডিও, ভিডিও, ফটো, কাস্টম ইমোজি) পাঠাতে পারেন।\n"
            f"• সব মেসেজ দেওয়া শেষ হলে নিচের <b>✅ ডান / সব পাঠান ({len(q_list)}টি মেসেজ)</b> বাটনে চাপ দিন:",
            reply_markup=kb
        )
        return


# ==============================================================================
# BACKGROUND DAEMONS: SESSION WATCHER, 5-MIN MANUAL CODE EXPIRY, BIO WATCHDOG & VIEW TRACKER
# ==============================================================================
def run_session_and_manual_code_expiry_pass(now_ts=None):
    now_ts = float(now_ts if now_ts is not None else time.time())
    try:
        cleanup_security_caches(now_ts)
    except Exception:
        pass
    timeout_limit = int(get_setting("user_session_timeout_sec", "600"))

    if len(user_memory_states) > 2500:
        for k_st in list(user_memory_states.keys())[:1000]:
            user_memory_states.pop(k_st, None)

    with db_lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT user_id, username, last_active_ts FROM users WHERE registered = 1 AND session_logged_out = 0 AND timeout_notified = 0"
        ).fetchall()
        conn.close()

    for r in rows:
        uid = str(r["user_id"])
        if is_admin_unlocked(uid):
            continue
        last_ts = float(r["last_active_ts"] or 0)
        if last_ts > 0 and (now_ts - last_ts) >= timeout_limit:
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute("UPDATE users SET session_logged_out = 1, timeout_notified = 1 WHERE user_id = ?", (uid,))
                conn.close()
            user_memory_states.pop(uid, None)
            try:
                safe_send(int(uid), get_msg("session_logout_msg"))
            except Exception:
                pass


def background_10min_session_watcher():
    while True:
        try:
            time.sleep(20)
            run_session_and_manual_code_expiry_pass()
        except Exception:
            time.sleep(30)


def background_24h_bio_retention_watchdog():
    while True:
        try:
            chk_interval = max(60, int(get_setting("verification_interval_sec", "3600") or 3600))
            time.sleep(chk_interval)
            now_ts = time.time()
            chk_interval = max(60, int(get_setting("verification_interval_sec", "3600") or 3600))
            v_link_global = get_setting("verification_link", "")
            with db_lock:
                conn = get_connection()
                active_platforms = conn.execute("SELECT * FROM user_platforms WHERE verified = 1 AND LOWER(platform) IN ('youtube', 'tiktok')").fetchall()
                active_vids = conn.execute(
                    "SELECT * FROM videos WHERE (admin_status = 'approved' OR bot_status = 'approved' OR COALESCE(permanent_approved, 0) = 1) "
                    "AND admin_status != 'rejected' AND bot_status != 'rejected' AND status != 'rejected' "
                    "AND COALESCE(is_trashed, 0) = 0 AND LOWER(platform) IN ('youtube', 'tiktok')"
                ).fetchall()
                conn.close()

            for p in active_platforms:
                last_chk = float(p["last_bio_check_ts"] or 0)
                if (now_ts - last_chk) < chk_interval:
                    continue

                u_owner = get_user(p["user_id"])
                if not u_owner or u_owner.get("status") != "active":
                    continue

                b_code = p["bio_code_used"] or u_owner["bio_verify_code"]
                p_crit = get_platform_criteria(p["platform"])
                v_link = p_crit.get("verification_link") or v_link_global
                chk = verify_bio_code_only(p["platform"], p["profile_url"], b_code, verification_link=v_link)
                if not chk["network_ok"]:
                    continue

                with db_lock:
                    conn = get_connection()
                    with conn:
                        if not chk["bio_found"]:
                            conn.execute("UPDATE user_platforms SET bio_missing_flag = 1 WHERE id = ?", (p["id"],))
                            conn.execute("UPDATE users SET bio_frozen = 1, status = 'inactive' WHERE user_id = ?", (p["user_id"],))
                            log_audit_event("SYSTEM_WATCHDOG", "Bio Code Removed", f"Platform {p['platform']} missing {b_code}", target_user_id=p["user_id"], conn=conn)
                            try:
                                kb = types.InlineKeyboardMarkup()
                                kb.row(make_btn("🔄 কোড বসিয়ে ভেরিফাই ও একাউন্ট সচল করুন", callback_data="u_unfreeze_req", style="success"))
                                safe_send(
                                    int(p["user_id"]),
                                    f"❄️ <b>জরুরি নোটিশ — অ্যাকাউন্ট ইনঅ্যাক্টিভ ও ফ্রিজ করা হয়েছে!</b>\n{FULL_WIDTH_DIVIDER}\n"
                                    f"অটো চেকিংয়ে আপনার <b>{PLATFORMS.get(p['platform'], {}).get('title', p['platform'])}</b> চ্যানেলের বায়োতে ভেরিফিকেশন কোড (<code>{esc(b_code)}</code>) পাওয়া যায়নি!\n\n"
                                    f"⚠️ এখন আপনি কোনো ভিডিও সাবমিট বা উইথড্র করতে পারবেন না। বায়োতে কোডটি পুনরায় বসিয়ে নিচের ভেরিফাই বাটনে চাপ দিন:",
                                    reply_markup=kb
                                )
                            except Exception:
                                pass
                        else:
                            conn.execute("UPDATE user_platforms SET last_bio_check_ts = ?, bio_missing_flag = 0 WHERE id = ?", (now_ts, p["id"]))
                    conn.close()

            for v in active_vids:
                last_v_chk = float(v["last_code_check_ts"] or 0)
                if (now_ts - last_v_chk) < chk_interval:
                    continue
                u_owner = get_user(v["user_id"])
                if not u_owner or u_owner.get("status") != "active":
                    continue
                vchk = verify_video_code_only(v["platform"], v["url"], v["unique_code"], "", "", verification_link=v_link_global)
                if not vchk["network_ok"]:
                    continue
                with db_lock:
                    conn = get_connection()
                    with conn:
                        if not vchk["codes_found"]:
                            warn_ts = float(v["code_missing_warning_ts"] or 0.0) if "code_missing_warning_ts" in v.keys() else 0.0
                            if warn_ts <= 0:
                                conn.execute(
                                    "UPDATE videos SET code_missing_flag = 1, code_missing_warning_ts = ?, last_code_check_ts = ? WHERE sub_id = ?",
                                    (now_ts, now_ts, v["sub_id"])
                                )
                                log_audit_event("SYSTEM_WATCHDOG", "Video Code 24h Warning Issued", f"Video {v['sub_id']} missing {v['unique_code']}", target_user_id=v["user_id"], conn=conn)
                                try:
                                    kb = types.InlineKeyboardMarkup()
                                    kb.row(make_btn("🔄 কোড পুনরায় বসিয়েছি — এখন যাচাই করুন", callback_data=f"u_recheck_vcode:{v['sub_id']}", style="success"))
                                    safe_send(
                                        int(v["user_id"]),
                                        f"⚠️ <b>জরুরি ওয়ার্নিং — ভিডিও থেকে ভেরিফিকেশন কোড সরানো হয়েছে (২৪ ঘণ্টার সময়সীমা)!</b>\n{FULL_WIDTH_DIVIDER}\n"
                                        f"আপনার সাবমিট করা ভিডিও (<b>{esc(v['title'][:35])}</b>) থেকে ভেরিফিকেশন কোড (<code>{esc(v['unique_code'])}</code>) পাওয়া যায়নি!\n\n"
                                        f"⏳ আগামী <b>২৪ ঘণ্টার মধ্যে</b> আপনার ভেরিফাইড অ্যাকাউন্টের উক্ত ভিডিওতে <code>{esc(v['unique_code'])}</code> কোডটি পুনরায় বসিয়ে নিচের বাটনে চাপ দিয়ে যাচাই করুন।\n"
                                        f"💡 <i>বি.দ্র.: কোডটি পুনরায় বসিয়ে যাচাই করলে আপনার ভিডিওর অতিবাহিত সময় বা অর্জিত টাকা কোনোটিই রিসেট হবে না!</i>",
                                        reply_markup=kb
                                    )
                                except Exception:
                                    pass
                            elif (now_ts - warn_ts) >= 86400:
                                conn.execute("UPDATE videos SET code_missing_flag = 1, last_code_check_ts = ? WHERE sub_id = ?", (now_ts, v["sub_id"]))
                                conn.execute("UPDATE users SET bio_frozen = 1, status = 'inactive' WHERE user_id = ?", (v["user_id"],))
                                try:
                                    kb = types.InlineKeyboardMarkup()
                                    kb.row(make_btn("🔄 কোড পুনরায় বসিয়েছি — এখন যাচাই করুন", callback_data=f"u_recheck_vcode:{v['sub_id']}", style="success"))
                                    safe_send(
                                        int(v["user_id"]),
                                        f"❄️ <b>২৪ ঘণ্টা অতিক্রান্ত — ভিডিওতে কোড না বসানোয় অ্যাকাউন্ট সাময়িক ফ্রিজ করা হয়েছে!</b>\n{FULL_WIDTH_DIVIDER}\n"
                                        f"ভিডিওতে (<b>{esc(v['title'][:35])}</b>) কোড <code>{esc(v['unique_code'])}</code> পুনরায় বসিয়ে নিচের বাটনে চাপ দিন (সময় বা টাকা রিসেট হবে না):",
                                        reply_markup=kb
                                    )
                                except Exception:
                                    pass
                        else:
                            conn.execute("UPDATE videos SET last_code_check_ts = ?, code_missing_flag = 0, code_missing_warning_ts = 0 WHERE sub_id = ?", (now_ts, v["sub_id"]))
                    conn.close()
        except Exception:
            time.sleep(60)


def run_video_monitoring_pass(now_ts=None, metadata_fetcher=None):
    now_ts = float(now_ts if now_ts is not None else time.time())
    use_platform_fetcher = metadata_fetcher is None
    metadata_fetcher = metadata_fetcher or fetch_video_public_metadata
    vel_thr = float(get_setting("view_velocity_threshold", "15000"))
    eng_thr = float(get_setting("engagement_threshold_ratio", "0.0005"))
    auto_rej_susp = get_setting("suspicious_auto_reject", "1") == "1"

    with db_lock:
        conn = get_connection()
        vids = conn.execute("""
            SELECT * FROM videos
            WHERE COALESCE(is_trashed, 0) = 0
              AND COALESCE(permanent_approved, 0) = 0
              AND LOWER(platform) IN ('youtube', 'tiktok')
              AND (
                  (admin_status = 'pending' AND bot_status IN ('waiting_views', 'manual_review', 'approved'))
                  OR (admin_status = 'approved' AND flagged_suspicious = 0)
              )
        """).fetchall()
        conn.close()

    for row in vids:
        v = dict(row)
        admin_approved = v.get("admin_status") == "approved"
        is_perm = int(v.get("permanent_approved") or 0) == 1
        end_ts = float(v.get("earning_end_ts") or 0)
        window_expired = bool(end_ts > 0 and now_ts >= end_ts)
        if not end_ts:
            base_start_ts = float(v.get("publish_ts") or 0) if int(v.get("publish_date_known") or 0) == 1 else 0.0
            if base_start_ts <= 0 or base_start_ts > now_ts + 86400 or base_start_ts < now_ts - (365 * 86400):
                base_start_ts = float(v.get("submitted_at_ts") or 0)
            if base_start_ts > 0:
                with db_lock:
                    conn_d = get_connection()
                    track_days_cfg = get_video_tracking_days(conn_d, sub_id=v["sub_id"], platform=v["platform"])
                    conn_d.close()
                if now_ts >= base_start_ts + (track_days_cfg * 86400):
                    window_expired = True

        try:
            if use_platform_fetcher:
                info = metadata_fetcher(v["platform"], v["url"])
            else:
                info = metadata_fetcher(v["url"], playlist_items="1", flat=True)
        except Exception:
            info = None

        is_deleted_or_private = bool(
            isinstance(info, dict) and (
                info.get("is_deleted")
                or (info.get("privacy_status") and str(info.get("privacy_status")).lower() not in ("public", ""))
            )
        )
        if is_deleted_or_private and not is_perm:
            sup_url = get_setting("support_link", "https://t.me/battleclubsupport")
            plat_title = PLATFORMS.get(v["platform"], {}).get("title", v["platform"].upper())
            del_reason = info.get("delete_reason") or f"ট্র্যাকিং চলাকালীন {plat_title} থেকে ভিডিওটি ডিলিট বা প্রাইভেট করে দেওয়া হয়েছে!"
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute(
                        "UPDATE videos SET flagged_suspicious=1, bot_status='manual_review', status='manual_review', risk_reason=?, last_checked_ts=? WHERE sub_id=?",
                        (del_reason, now_ts, v["sub_id"])
                    )
                    conn.execute(
                        "UPDATE users SET bio_frozen = 1, status = 'inactive' WHERE user_id = ?",
                        (v["user_id"],)
                    )
                    log_audit_event("SYSTEM_MONITOR", "Video Deleted Penalty (Account Frozen)", f"Video {v['sub_id']} deleted/private on {v['platform']}", target_user_id=v["user_id"], conn=conn)
                conn.close()
            try:
                del_kb = types.InlineKeyboardMarkup()
                del_kb.row(make_btn("💬 অফিসিয়াল সাপোর্টে যোগাযোগ করুন", url=sup_url, style="danger"))
                safe_send(
                    int(v["user_id"]),
                    get_msg(
                        "video_deleted_freeze_msg",
                        title=esc(v["title"][:40]),
                        platform=esc(plat_title),
                        support_link=esc(sup_url)
                    ),
                    reply_markup=del_kb
                )
            except Exception:
                pass
            continue

        metrics_known = isinstance(info, dict) and any(info.get(k) is not None for k in ("view_count", "play_count"))
        deadline = float(v.get("qualification_deadline_ts") or 0)
        if not metrics_known:
            # Enterprise v9.0 Fix: Never auto-reject a video as Low Views when metrics_known is False
            # due to API, Rate Limit, or Network Failure! Record check timestamp and defer until metrics are reachable.
            with db_lock:
                conn = get_connection()
                with conn:
                    conn.execute(
                        "UPDATE videos SET last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                        (datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S"), now_ts, v["sub_id"])
                    )
                conn.close()
            if (admin_approved or v.get("bot_status") == "approved") and window_expired:
                with db_lock:
                    conn = get_connection()
                    with conn:
                        now_str_p = datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S")
                        conn.execute(
                            "UPDATE videos SET admin_status = 'approved', status = 'permanent_approved', permanent_approved = 1, "
                            "permanent_approved_at = COALESCE(NULLIF(permanent_approved_at, ''), ?), "
                            "permanent_approved_by = COALESCE(NULLIF(permanent_approved_by, ''), 'AUTO_WINDOW_COMPLETE') WHERE sub_id = ?",
                            (now_str_p, v["sub_id"])
                        )
                    conn.close()
            continue

        scraped_v = max(0, parse_human_number(info.get("view_count") if info.get("view_count") is not None else info.get("play_count")))
        cur_v = max(int(v.get("current_views") or 0), scraped_v) if scraped_v == 0 else scraped_v
        cur_l = max(0, parse_human_number(info.get("like_count") or 0))
        cur_c = max(0, parse_human_number(info.get("comment_count") or 0))
        source = str(info.get("metric_source") or ("yt-dlp" if info.get("view_count") is not None or info.get("play_count") is not None else "public-page"))
        v_link_mon = get_platform_criteria(v["platform"]).get("verification_link") or get_setting("verification_link", "")

        traffic_info = analyze_video_traffic_sources(
            platform_key=v["platform"],
            video_url=v["url"],
            caption_text=str(info.get("description") or v.get("title") or ""),
            cur_views=cur_v,
            cur_likes=cur_l,
            cur_comments=cur_c,
            ytdlp_info=info,
            verification_link=v_link_mon
        )
        saved_ext_links = []

        with db_lock:
            conn = get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT OR IGNORE INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (v["sub_id"], cur_v, cur_l, cur_c, source, now_ts))
                prior_rows = conn.execute(
                    "SELECT views, likes, comments, source, recorded_at_ts FROM video_view_snapshots WHERE sub_id=? ORDER BY recorded_at_ts DESC LIMIT 20",
                    (v["sub_id"],)
                ).fetchall()
                prior_snaps = [dict(s) for s in reversed(prior_rows)]
                risk = assess_organic_view_risk(
                    prior_snaps,
                    cur_v,
                    cur_l,
                    cur_c,
                    velocity_threshold=vel_thr,
                    engagement_threshold=eng_thr,
                    auto_reject_enabled=auto_rej_susp,
                    traffic_breakdown=traffic_info
                )
                org_status_now = str(risk.get("organic_status") or ("verified_organic" if risk.get("organic_verified") else "pending_snapshots"))
                with conn:
                    conn.execute("""
                        UPDATE videos SET previous_views=current_views, current_views=?, organic_status=?, view_metrics_known=1,
                            view_metrics_source=?, last_checked_at=?, last_checked_ts=?
                        WHERE sub_id=?
                    """, (cur_v, org_status_now, source, datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S"), now_ts, v["sub_id"]))
                    saved_ext_links = save_video_traffic_and_external_links(
                        sub_id=v["sub_id"],
                        user_id=v["user_id"],
                        platform=v["platform"],
                        traffic_breakdown=traffic_info,
                        external_links=traffic_info.get("external_links", []),
                        conn=conn
                    )

                    if (risk.get("suspicious") or risk["risk_score"] >= 0.75) and not is_perm:
                        if auto_rej_susp:
                            rej_res = admin_reject_video_with_reversal(
                                conn,
                                sub_id=v["sub_id"],
                                rejection_reason=f"অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি: {risk['reason']}",
                                admin_id="BOT_ANTI_FRAUD"
                            )
                            v["_auto_rejected_reversal"] = float(rej_res.get("reversed_amount", 0.0))
                            v["_auto_rejected_reason"] = f"অর্গানিক ভিউ না — অর্গানিক ভিউ যাচাই হয়নি: {risk['reason']}"
                            v["_auto_rejected_res"] = rej_res
                        else:
                            conn.execute(
                                "UPDATE videos SET flagged_suspicious=1, bot_status=CASE WHEN admin_status='pending' THEN 'manual_review' ELSE bot_status END, status=CASE WHEN admin_status='pending' THEN 'manual_review' ELSE status END, risk_reason=? WHERE sub_id=?",
                                (risk["reason"], v["sub_id"])
                            )
                    elif not admin_approved and v.get("bot_status") in ("waiting_views", "manual_review") and not int(v.get("flagged_suspicious") or 0):
                        min_views = get_video_payment_rates(conn, sub_id=v["sub_id"])[2]
                        ded_v = int(v.get("deducted_external_views") or 0)
                        net_v = max(0, cur_v - ded_v)
                        dur_ok_m = bool(int(v.get("duration_known") if v.get("duration_known") is not None else 1) == 1)
                        pub_ok_m = bool(int(v.get("publish_date_known") if v.get("publish_date_known") is not None else 1) == 1)
                        if not dur_ok_m and isinstance(info, dict) and info.get("duration"):
                            d_sec_m = int(float(info.get("duration") or 0))
                            if d_sec_m >= int(get_setting("min_video_duration_sec", "10")):
                                dur_ok_m = True
                                conn.execute("UPDATE videos SET video_duration_sec = ?, duration_known = 1 WHERE sub_id = ?", (d_sec_m, v["sub_id"]))
                        if not pub_ok_m and isinstance(info, dict) and (info.get("timestamp") or info.get("release_timestamp")):
                            p_ts_m = float(info.get("timestamp") or info.get("release_timestamp") or 0)
                            if p_ts_m > 0:
                                pub_ok_m = True
                                conn.execute("UPDATE videos SET publish_ts = ?, publish_date_known = 1 WHERE sub_id = ?", (p_ts_m, v["sub_id"]))
                        ver_mode_m = str(v.get("verification_mode") or "").upper()
                        code_miss_m = int(v.get("code_missing_flag") or 0) == 1
                        meta_complete_m = bool(dur_ok_m and pub_ok_m and ver_mode_m != "SOURCE_CONFLICT" and not code_miss_m)
                        # Enforce strict qualification_deadline_ts cutoff BEFORE granting any initial credit (P0-07 & P1-11)!
                        if (deadline and now_ts > deadline) or window_expired:
                            exp_reason = f"নির্ধারিত যোগ্যতা সময়সীমায় প্রয়োজনীয় {min_views} ভিউ পূরণ হয়নি (মেয়াদ উত্তীর্ণ — ০ টাকা)।"
                            exp_res = transition_expired_pending_video(
                                conn,
                                v["sub_id"],
                                reason=exp_reason,
                                expiry_action=get_setting("pending_expiry_action", "permanent_approve_zero_pay"),
                                now_ts=now_ts
                            )
                            if exp_res.get("ok"):
                                v["_expired_reason"] = exp_reason
                        elif meta_complete_m and net_v >= min_views and risk.get("organic_verified") is True:
                            credited, _ = process_bot_approval_credit(conn, v["sub_id"], v["user_id"], cur_v, now_ts=now_ts)
                            if float(credited or 0.0) > 0:
                                conn.execute(
                                    "UPDATE videos SET flagged_suspicious=0, risk_reason=? WHERE sub_id=?",
                                    ("দুই বা তার বেশি পাবলিক metric snapshot-এ threshold পূরণ; অর্গানিক ভিউ যাচাই সম্পন্ন।", v["sub_id"])
                                )
                                eff_cap_w = get_max_payable_views_setting(conn, sub_id=v["sub_id"])
                                if window_expired or (eff_cap_w > 0 and net_v >= eff_cap_w):
                                    now_str_p = datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S")
                                    p_by = "AUTO_MAX_CAP_REACHED" if (eff_cap_w > 0 and net_v >= eff_cap_w) else "AUTO_WINDOW_COMPLETE"
                                    conn.execute(
                                        "UPDATE videos SET admin_status = 'approved', status = 'permanent_approved', permanent_approved = 1, permanent_approved_at = ?, permanent_approved_by = ? WHERE sub_id = ?",
                                        (now_str_p, p_by, v["sub_id"])
                                    )
                                    v["_completed_permanent_now"] = True
                                v["_new_bot_credit"] = float(credited or 0.0)
                conn.close()
            except Exception:
                conn.close()
                continue

        if saved_ext_links:
            u_owner = get_user(v["user_id"]) or {"user_id": v["user_id"]}
            _notify_admins_of_external_links(u_owner, v["sub_id"], v["platform"], cur_v, traffic_info, saved_ext_links)

        if v.get("_new_bot_credit") is not None:
            credited = float(v["_new_bot_credit"])
            _unlock_referral_on_first_video_approval(v["user_id"])
            try:
                safe_send(int(v["user_id"]), get_msg("video_bot_approved_msg", views=cur_v, credited=f"{credited:.2f}"), track_ui=False, auto_clean_prev=False)
                if v.get("_completed_permanent_now"):
                    safe_send(
                        int(v["user_id"]),
                        get_msg("video_counting_completed_msg", title=esc(str(v.get("title") or "Video")[:40]), views=cur_v, credited=f"{credited:.2f}"),
                        track_ui=False,
                        auto_clean_prev=False
                    )
            except Exception:
                pass
        elif v.get("_auto_rejected_reason"):
            rev_v = float(v.get("_auto_rejected_reversal", 0.0))
            fin_note = _build_rejection_financial_summary_note(v.get("_auto_rejected_res") or {}, v["user_id"])
            try:
                safe_send(
                    int(v["user_id"]),
                    get_msg("video_rejected_msg", title=esc(v["title"][:35]), reason=esc(v["_auto_rejected_reason"]), reversed=f"{rev_v:.2f}") + fin_note
                )
            except Exception:
                pass
        elif v.get("_expired_reason"):
            try:
                safe_send(int(v["user_id"]), get_msg("video_qualification_expired_msg"))
            except Exception:
                pass
        elif risk["risk_score"] >= 0.75 and not is_perm:
            if not admin_approved:
                try:
                    safe_send(int(v["user_id"]), get_msg("video_review_needed_msg", reason=esc(risk["reason"])))
                except Exception:
                    pass
            u_o = get_user(v["user_id"])
            alert_txt = get_msg(
                "suspicious_video_alert_msg",
                user_label=esc(get_user_label(u_o)), user_id=v["user_id"], sub_id=v["sub_id"],
                platform=PLATFORMS.get(v["platform"], {}).get("title", v["platform"]),
                views=cur_v, reason=esc(risk["reason"])
            )
            adm_kb = types.InlineKeyboardMarkup()
            adm_kb.row(make_btn("🔗 ভিডিও দেখুন", url=v["url"], style="primary"))
            if admin_approved:
                adm_kb.row(make_btn("❌ রিজেক্ট ও রিভার্স", callback_data=video_decision_callback("reject", v["sub_id"], "admin_approve", "all"), style="danger"))
            for adm_id in get_all_admin_ids():
                safe_send(adm_id, alert_txt, reply_markup=adm_kb)
        elif admin_approved or v.get("bot_status") == "approved":
            milestone_credited = 0.0
            new_elig_v = 0
            with db_lock:
                conn = get_connection()
                try:
                    with conn:
                        milestone_credited, new_elig_v = process_idempotent_milestone_payout(
                            conn, v["sub_id"], v["user_id"], cur_v, int(v.get("paid_views") or v.get("eligible_views") or 0), now_ts=now_ts
                        )
                        eff_cap = get_max_payable_views_setting(conn, sub_id=v["sub_id"])
                        ded_ext = int(v.get("deducted_external_views") or 0)
                        net_cur_v = max(0, cur_v - ded_ext)
                        if window_expired or (eff_cap > 0 and net_cur_v >= eff_cap):
                            now_str_perm = datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S")
                            perm_reason = "AUTO_MAX_CAP_REACHED" if (eff_cap > 0 and net_cur_v >= eff_cap) else "AUTO_WINDOW_COMPLETE"
                            conn.execute(
                                "UPDATE videos SET admin_status = 'approved', status = 'permanent_approved', permanent_approved = 1, "
                                "permanent_approved_at = COALESCE(NULLIF(permanent_approved_at, ''), ?), "
                                "permanent_approved_by = COALESCE(NULLIF(permanent_approved_by, ''), ?) WHERE sub_id = ?",
                                (now_str_perm, perm_reason, v["sub_id"])
                            )
                            v["_completed_permanent_now"] = True
                finally:
                    conn.close()
            if float(milestone_credited or 0.0) > 0:
                try:
                    safe_send(
                        int(v["user_id"]),
                        f"📈 <b>ভিউ মাইলস্টোন বোনাস যুক্ত হয়েছে!</b>\n{FULL_WIDTH_DIVIDER}\n"
                        f"🎬 ভিডিও: <b>{esc(str(v.get('title') or 'Video')[:40])}</b>\n"
                        f"👁️ বর্তমান ভিউ: <b>{cur_v}</b> (পেইড ভিউ: <b>{new_elig_v}</b>)\n"
                        f"💰 নতুন যুক্ত হওয়া আয়: <b>+{float(milestone_credited):.2f} টাকা</b>",
                        track_ui=False,
                        auto_clean_prev=False
                    )
                except Exception:
                    pass
            if v.get("_completed_permanent_now"):
                try:
                    with db_lock:
                        conn_fc = get_connection()
                        v_fc = conn_fc.execute("SELECT credited_amount, reward FROM videos WHERE sub_id = ?", (v["sub_id"],)).fetchone()
                        conn_fc.close()
                    tot_cred_fc = float((v_fc["credited_amount"] or v_fc["reward"] or 0.0) if v_fc else (v.get("credited_amount") or 0.0))
                    safe_send(
                        int(v["user_id"]),
                        get_msg(
                            "video_counting_completed_msg",
                            title=esc(str(v.get("title") or "Video")[:40]),
                            views=cur_v,
                            credited=f"{tot_cred_fc:.2f}"
                        ),
                        track_ui=False,
                        auto_clean_prev=False
                    )
                except Exception:
                    pass


def background_view_step_analyzer():
    while True:
        try:
            run_video_monitoring_pass()
            time.sleep(max(60, int(get_setting("view_checking_interval_sec", "3600") or 3600)))
        except Exception:
            time.sleep(60)


@bot.callback_query_handler(func=lambda c: True)
@_guard("fallback_callback")
def handle_unmatched_legacy_callbacks(call):
    uid = str(call.from_user.id)
    cb_str = str(call.data or "")
    if cb_str.startswith(("adm", "vd:", "ext_act:", "admin_hub")):
        if not require_unlocked_admin_session(call):
            return
        bot.answer_callback_query(call.id, "🔄 অ্যাডমিন মেনু রিফ্রেশ করা হয়েছে!")
        txt = render_admin_master_metrics_text()
        safe_edit(call.message.chat.id, call.message.message_id, txt, reply_markup=build_admin_dashboard_keyboard(uid), menu_id="admin_home")
        return
    u = get_user(uid) or ensure_user(call.from_user)
    bot.answer_callback_query(call.id, "🔄 মেনু আপডেট করা হয়েছে!")
    if not u.get("registered") and not is_admin_unlocked(uid):
        send_onboarding_home(call.message.chat.id, uid, u)
        return
    top_yt = get_setting("home_youtube_link", "")
    u_lang = (u.get("language") or "bn").lower()
    w_txt = attach_top_youtube_preview(get_msg("welcome_msg", lang=u_lang, name=esc(u.get("name")), balance=f"{float(u.get('balance', 0)):.2f}", user_id=uid), top_yt)
    safe_edit(call.message.chat.id, call.message.message_id, w_txt, reply_markup=build_user_home_keyboard(uid, u), top_yt_url=top_yt, menu_id="user_home")


# ==============================================================================
# GITHUB, VERCEL SERVERLESS WEBHOOK & CLOUD SERVER DEPLOYMENT ENGINE
# ==============================================================================
_RUNTIME_INITIALIZED = False
_RUNTIME_INIT_LOCK = threading.RLock()


def ensure_bot_runtime_initialized():
    """Idempotently initializes SQLite schema and in-memory caches for both Polling and Serverless Webhook modes."""
    global _RUNTIME_INITIALIZED
    if _RUNTIME_INITIALIZED:
        return
    with _RUNTIME_INIT_LOCK:
        if _RUNTIME_INITIALIZED:
            return
        init_db()
        preload_all_caches()
        _RUNTIME_INITIALIZED = True


def process_webhook_update(raw_body: str, secret_header: str = "") -> dict:
    """
    Processes an incoming Telegram Webhook JSON payload (for Vercel Serverless `/api/webhook` or Cloud HTTP server).
    """
    ensure_bot_runtime_initialized()
    expected_secret = os.getenv("WEBHOOK_SECRET_TOKEN", "").strip()
    if expected_secret and str(secret_header or "").strip() != expected_secret:
        return {"ok": False, "status": 403, "error": "Invalid webhook secret token"}
    if not raw_body or not str(raw_body).strip():
        return {"ok": False, "status": 400, "error": "Empty request body"}
    try:
        update_dict = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        if hasattr(types, "Update") and hasattr(types.Update, "de_json"):
            upd = types.Update.de_json(update_dict)
            if upd is not None and hasattr(bot, "process_new_updates"):
                bot.process_new_updates([upd])
        return {"ok": True, "status": 200}
    except Exception as exc:
        return {"ok": False, "status": 500, "error": str(exc)}


def run_serverless_cron_cycle() -> dict:
    """
    Executes one non-blocking monitoring & session maintenance cycle when triggered by Vercel Cron (`/api/cron`)
    or GitHub Actions scheduled workflow.
    """
    ensure_bot_runtime_initialized()
    run_session_and_manual_code_expiry_pass()
    run_video_monitoring_pass()
    return {
        "ok": True,
        "status": 200,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _start_builtin_webhook_http_server(host: str = "0.0.0.0", port: int = 8080, webhook_url: str = ""):
    """
    Starts a built-in multi-threaded HTTP server for Cloud Platforms (Render, Railway, Koyeb, Fly.io, Heroku, VPS)
    that require binding to `$PORT` and/or receiving Telegram Webhooks.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class _BotWebhookHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path_clean = self.path.split("?")[0].rstrip("/") or "/"
            if path_clean in ("/", "/health", "/api/health"):
                body = json.dumps({
                    "ok": True,
                    "service": "Battle Club Creator Sponsorship Bot",
                    "mode": "webhook" if webhook_url else "polling+health",
                    "threads": BOT_NUM_THREADS,
                    "view_checking_interval_sec": get_setting("view_checking_interval_sec", "3600"),
                    "verification_interval_sec": get_setting("verification_interval_sec", "3600")
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path_clean in ("/cron", "/api/cron"):
                res = run_serverless_cron_cycle()
                body = json.dumps(res).encode("utf-8")
                self.send_response(int(res.get("status", 200)))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            path_clean = self.path.split("?")[0].rstrip("/") or "/"
            if path_clean in ("/", "/webhook", "/api/webhook", "/api/index"):
                length = int(self.headers.get("Content-Length", "0") or 0)
                raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""
                sec_hdr = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
                res = process_webhook_update(raw, secret_header=sec_hdr)
                body = json.dumps(res).encode("utf-8")
                self.send_response(int(res.get("status", 200)))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, format_str, *args):
            return

    srv = ThreadingHTTPServer((host, int(port)), _BotWebhookHandler)
    print(f"🌐 HTTP Health/Webhook server listening on {host}:{port}")
    srv.serve_forever()


# ==============================================================================
# MAIN ENTRYPOINT (TERMUX, GITHUB CLOUD SERVER, RAILWAY, RENDER & VERCEL)
# ==============================================================================
if __name__ == "__main__":
    print("🔥 Battle Club creator sponsorship bot is starting (Enterprise Anti-Spam & Cloud Ready)...")
    ensure_bot_runtime_initialized()

    threading.Thread(target=background_10min_session_watcher, daemon=True).start()
    threading.Thread(target=background_24h_bio_retention_watchdog, daemon=True).start()
    threading.Thread(target=background_view_step_analyzer, daemon=True).start()

    webhook_url = (
        os.getenv("WEBHOOK_URL", "").strip()
        or (f"https://{os.getenv('VERCEL_URL').strip()}/api/webhook" if os.getenv("VERCEL_URL", "").strip() else "")
    )
    bot_mode = os.getenv("BOT_MODE", "auto").strip().lower()
    http_port = int(os.getenv("PORT", "0") or 0)

    if bot_mode == "webhook" or (webhook_url and bot_mode != "polling"):
        clean_wh_url = webhook_url.rstrip("/")
        if not clean_wh_url.endswith(("/webhook", "/api/webhook", "/api/index")):
            clean_wh_url = clean_wh_url + "/api/webhook"
        try:
            bot.remove_webhook()
            time.sleep(0.5)
            secret_tok = os.getenv("WEBHOOK_SECRET_TOKEN", "").strip() or None
            if secret_tok:
                bot.set_webhook(url=clean_wh_url, secret_token=secret_tok, allowed_updates=["message", "edited_message", "callback_query"])
            else:
                bot.set_webhook(url=clean_wh_url, allowed_updates=["message", "edited_message", "callback_query"])
            print(f"✅ Webhook registered at: {clean_wh_url}")
        except Exception as wh_err:
            print(f"[WEBHOOK SETUP WARNING]: {wh_err}")
        _start_builtin_webhook_http_server(host="0.0.0.0", port=http_port or 8080, webhook_url=clean_wh_url)
    else:
        if http_port > 0:
            threading.Thread(
                target=_start_builtin_webhook_http_server,
                kwargs={"host": "0.0.0.0", "port": http_port, "webhook_url": ""},
                daemon=True
            ).start()
        try:
            bot.remove_webhook()
        except Exception:
            pass

        print(f"✅ Bot is online and listening with {BOT_NUM_THREADS} worker threads & anti-spam rate limiting.")
        while True:
            try:
                bot.infinity_polling(
                    timeout=20,
                    long_polling_timeout=10,
                    skip_pending=False,
                    allowed_updates=["message", "edited_message", "callback_query"]
                )
            except Exception as poll_err:
                print(f"[POLLING RETRY]: {poll_err}")
                time.sleep(5)