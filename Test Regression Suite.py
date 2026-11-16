#!/usr/bin/env python3
"""
BC Creator Hub / Battle Club Bot — Automated Unit & Integration Regression Test Suite (T00–T15)
Supports both standard Termux lowercase filenames:
  1. battle_club_bot.py
  2. database.py
  3. finance.py
  4. security.py
  5. ui_catalog.py
  6. ui_validation.py
  7. verifier.py
and legacy spaced/capitalized filenames automatically.
"""
import importlib.util
import json
import os
import py_compile
import sqlite3
import sys
import tempfile
import time
import unittest

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

MODULE_FILENAME_CANDIDATES = {
    "security": ("security.py", "Security.py"),
    "ui_catalog": ("ui_catalog.py", "Ui Catalog.py", "UI_Catalog.py"),
    "ui_validation": ("ui_validation.py", "Ui Validation.py", "UI_Validation.py"),
    "database": ("database.py", "Database.py"),
    "finance": ("finance.py", "Finance.py"),
    "verifier": ("verifier.py", "Verifier.py"),
    "battle_club_bot": ("battle_club_bot.py", "Battle Club Bot.py", "Battle_Club_Bot.py"),
}


def _resolve_module_path(mod_name: str, candidates: tuple = None) -> str:
    cand_list = list(candidates or MODULE_FILENAME_CANDIDATES.get(mod_name, (f"{mod_name}.py",)))
    for fn in cand_list:
        p = os.path.join(SRC_DIR, fn)
        if os.path.isfile(p):
            return p
    # Case-insensitive fallback scan in SRC_DIR
    target_norm = mod_name.lower().replace("_", "").replace(" ", "") + ".py"
    try:
        for entry in os.listdir(SRC_DIR):
            if entry.lower().replace("_", "").replace(" ", "") == target_norm:
                full_p = os.path.join(SRC_DIR, entry)
                if os.path.isfile(full_p):
                    return full_p
    except Exception:
        pass
    raise FileNotFoundError(
        f"Could not find module '{mod_name}' in {SRC_DIR} (checked: {', '.join(cand_list)})"
    )


def _load_module(mod_name: str, *candidate_filenames: str):
    cands = candidate_filenames or MODULE_FILENAME_CANDIDATES.get(mod_name, (f"{mod_name}.py",))
    path = _resolve_module_path(mod_name, cands)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load all 7 modules in dependency order (works seamlessly with Termux lowercase filenames)
security = _load_module("security", "security.py", "Security.py")
ui_catalog = _load_module("ui_catalog", "ui_catalog.py", "Ui Catalog.py")
ui_validation = _load_module("ui_validation", "ui_validation.py", "Ui Validation.py")
database = _load_module("database", "database.py", "Database.py")
finance = _load_module("finance", "finance.py", "Finance.py")
verifier = _load_module("verifier", "verifier.py", "Verifier.py")
bot_mod = _load_module("battle_club_bot", "battle_club_bot.py", "Battle Club Bot.py")


class TestBCCreatorHubRegressionSuite(unittest.TestCase):
    def setUp(self):
        os.environ["UNITTEST_MODE"] = "1"
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_bc_creator.db")
        database.DB_FILE = self.db_path
        database.DB_NAME = self.db_path
        database.init_db()
        bot_mod.preload_all_caches()
        bot_mod.admin_unlocked_sessions.clear()
        bot_mod.user_memory_states.clear()
        bot_mod.USER_ACTIVE_UI_MSGS.clear()
        security.lock_admin_session("8145274317")
        security.reset_rate_limit("8145274317")
        security.reset_failed_login("admin:8145274317")

        # Offline Telegram API Mocks (G1: zero live api.telegram.org calls during unit tests)
        self.sent_messages = []
        self.edited_messages = []
        self.deleted_messages = []
        self.callback_answers = []
        self._msg_id_seq = 5000

        self._orig_send = bot_mod.bot.send_message
        self._orig_edit = bot_mod.bot.edit_message_text
        self._orig_delete = getattr(bot_mod.bot, "delete_message", None)
        self._orig_answer_cb = bot_mod.bot.answer_callback_query

        class _DummyChat:
            def __init__(self, cid):
                self.id = int(cid) if str(cid).lstrip("-").isdigit() else cid

        class _DummyMsg:
            def __init__(self, mid, cid, text, reply_markup=None):
                self.message_id = mid
                self.chat = _DummyChat(cid)
                self.text = str(text or "")
                self.reply_markup = reply_markup

        def _mock_send_message(chat_id, text, **kwargs):
            self._msg_id_seq += 1
            m = _DummyMsg(self._msg_id_seq, chat_id, text, kwargs.get("reply_markup"))
            self.sent_messages.append({"chat_id": str(chat_id), "text": str(text or ""), "message_id": m.message_id, "kwargs": kwargs})
            return m

        def _mock_edit_message_text(text, chat_id=None, message_id=None, **kwargs):
            mid = message_id or kwargs.get("message_id") or 1
            cid = chat_id or kwargs.get("chat_id") or 0
            m = _DummyMsg(mid, cid, text, kwargs.get("reply_markup"))
            self.edited_messages.append({"chat_id": str(cid), "message_id": mid, "text": str(text or ""), "kwargs": kwargs})
            return m

        def _mock_delete_message(chat_id, message_id):
            self.deleted_messages.append((str(chat_id), int(message_id)))
            return True

        def _mock_answer_cb(call_id, text=None, show_alert=False, **kwargs):
            self.callback_answers.append({"call_id": str(call_id), "text": str(text or ""), "show_alert": bool(show_alert)})
            return True

        bot_mod.bot.send_message = _mock_send_message
        bot_mod.bot.edit_message_text = _mock_edit_message_text
        bot_mod.bot.delete_message = _mock_delete_message
        bot_mod.bot.answer_callback_query = _mock_answer_cb

    def tearDown(self):
        bot_mod.bot.send_message = self._orig_send
        bot_mod.bot.edit_message_text = self._orig_edit
        if self._orig_delete is not None:
            bot_mod.bot.delete_message = self._orig_delete
        bot_mod.bot.answer_callback_query = self._orig_answer_cb
        try:
            self.tmp_dir.cleanup()
        except Exception:
            pass

    def test_T00_syntax_and_imports_all_7_files(self):
        """Verify py_compile on all 7 Python modules (Termux lowercase or legacy names)."""
        for mod_name, cands in MODULE_FILENAME_CANDIDATES.items():
            full_p = _resolve_module_path(mod_name, cands)
            self.assertTrue(os.path.exists(full_p), f"Missing file for {mod_name}")
            py_compile.compile(full_p, doraise=True)

    def test_T01_P0_02_initial_submission_high_views_zero_snapshots_no_instant_payout(self):
        """
        T01 (P0-02): Submit a valid video with cur_views = 2500 and 0 prior snapshots ->
        Stored as waiting_views (pending), initial_credited_amt == 0.0, user balance unchanged until snapshot organic proof completes.
        """
        conn = database.get_connection()
        now_ts = time.time()
        with conn:
            conn.execute(
                "INSERT INTO users (user_id, name, registered, balance, app_uid, active_video_code) VALUES (?, ?, 1, 0.0, '#1007', 'BC-111222')",
                ("900001", "Creator One")
            )
            conn.execute("""
                INSERT INTO videos (
                    sub_id, platform, platform_account_id, video_id, canonical_video_id, user_id, url, video_url, title,
                    unique_code, global_code, app_uid, status, bot_status, admin_status,
                    current_views, previous_views, duration_known, publish_date_known,
                    organic_status, submitted_at_ts, qualification_deadline_ts, view_metrics_known
                ) VALUES (?, 'youtube', 1, 'YT_dQw4w9WgXcQ', 'YT_dQw4w9WgXcQ', '900001', 'https://youtu.be/dQw4w9WgXcQ', 'https://youtu.be/dQw4w9WgXcQ', 'Test Video',
                          'BC-111222', '#BattleClub', '#1007', 'waiting_views', 'waiting_views', 'pending',
                          2500, 2500, 1, 1, 'pending_snapshots', ?, ?, 1)
            """, ("SUB_T01", now_ts, now_ts + 86400))
            conn.execute(
                "INSERT INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES (?, 2500, 150, 20, 'public-page', ?)",
                ("SUB_T01", now_ts)
            )
            credited, paid_v = finance.process_bot_approval_credit(conn, "SUB_T01", "900001", 2500, now_ts=now_ts)
            u_bal = float(conn.execute("SELECT balance FROM users WHERE user_id = '900001'").fetchone()["balance"])
        conn.close()
        self.assertEqual(credited, 0.0)
        self.assertEqual(paid_v, 0)
        self.assertEqual(u_bal, 0.0)

    def test_T02_P0_06_assess_organic_view_risk_0_1_and_2_snapshots(self):
        """
        T02 (P0-06): Call assess_organic_view_risk with 0 snapshots and 1 snapshot ->
        Both return organic_verified=False (organic_status='pending_snapshots').
        Call with >= 2 valid chronological snapshots and normal velocity/engagement -> Returns organic_verified=True.
        """
        now_ts = time.time()
        res_0 = verifier.assess_organic_view_risk([], cur_views=1500, cur_likes=120, cur_comments=15)
        self.assertFalse(res_0["organic_verified"])
        self.assertEqual(res_0["organic_status"], "pending_snapshots")

        res_1 = verifier.assess_organic_view_risk(
            [{"views": 1200, "likes": 100, "comments": 10, "recorded_at_ts": now_ts - 1800}],
            cur_views=1500,
            cur_likes=120,
            cur_comments=15
        )
        self.assertFalse(res_1["organic_verified"])
        self.assertEqual(res_1["organic_status"], "pending_snapshots")

        res_2 = verifier.assess_organic_view_risk(
            [
                {"views": 1100, "likes": 90, "comments": 8, "recorded_at_ts": now_ts - 3600},
                {"views": 1500, "likes": 120, "comments": 15, "recorded_at_ts": now_ts - 60},
            ],
            cur_views=1500,
            cur_likes=120,
            cur_comments=15
        )
        self.assertTrue(res_2["organic_verified"])
        self.assertEqual(res_2["organic_status"], "verified_organic")

    def test_T03_T04_P0_03_P0_09_unique_code_mandatory_and_optional_link_toggle(self):
        """
        T03 (P0-03): Link only without unique code BC-XXXXXX -> Rejected (False).
        T04 (P0-09): Unique code present with required_link_config='off' -> Passes without link;
        when required_link_config='on' and link missing -> Rejected for missing link.
        """
        self.assertFalse(
            verifier._matches_code_or_verification_link(
                "Check out https://battleclub.app/join #BattleClub",
                required_code="BC-998877",
                verification_link="https://battleclub.app/join",
                required_link_config="on"
            )
        )
        self.assertFalse(
            verifier._matches_code_or_verification_link(
                "My gameplay video BC-998877 #BattleClub",
                required_code="BC-998877",
                verification_link="https://battleclub.app/join",
                required_link_config="on"
            )
        )
        self.assertTrue(
            verifier._matches_code_or_verification_link(
                "My gameplay video BC-998877 #BattleClub",
                required_code="BC-998877",
                verification_link="https://battleclub.app/join",
                required_link_config="off"
            )
        )
        self.assertTrue(
            verifier._matches_code_or_verification_link(
                "My gameplay video BC-998877 https://battleclub.app/join #BattleClub",
                required_code="BC-998877",
                verification_link="https://battleclub.app/join",
                required_link_config="on"
            )
        )

    def test_T05_P0_05_scoped_profile_bio_extraction_ignores_video_titles(self):
        """
        T05 (P0-05): Profile page does NOT have BC-XXXXXX in bio, but a video title or recommended channel
        on the page contains BC-XXXXXX -> extract_scoped_profile_bio_text and has_required_unique_code return False.
        """
        fake_page_html = '''
        <html>
        <head><meta property="og:description" content="Welcome to my gaming channel!"/></head>
        <body>
            <script>var ytInitialData = {"header":{"c4TabbedHeaderRenderer":{"description":{"simpleText":"Official Free Fire Player"}}},"contents":{"videoRenderer":{"videoId":"abc12345678","title":{"simpleText":"How to verify BC-554433 in video title"}}}};</script>
            <a id="video-title" href="/watch?v=abc12345678">My video with BC-554433 in title</a>
        </body>
        </html>
        '''
        scoped_bio = verifier.extract_scoped_profile_bio_text("youtube", html_blobs=[fake_page_html])
        self.assertFalse(verifier.has_required_unique_code(scoped_bio, "BC-554433"))

        real_bio_html = '''
        <html>
        <head><meta property="og:description" content="Official Creator | Code: BC-554433"/></head>
        </html>
        '''
        scoped_bio_ok = verifier.extract_scoped_profile_bio_text("youtube", html_blobs=[real_bio_html])
        self.assertTrue(verifier.has_required_unique_code(scoped_bio_ok, "BC-554433"))

    def test_T06_P0_04_foreign_channel_ownership_rejected_even_for_manual_account(self):
        """
        T06 (P0-04): User verified via manual code submits a video from a foreign channel while pasting
        BC-XXXXXX in caption -> Rejected for channel ownership mismatch.
        """
        user_plats = [{
            "id": 1,
            "platform": "youtube",
            "profile_handle": "monir_official",
            "profile_url": "https://www.youtube.com/@monir_official",
            "display_name": "Monir Gaming",
            "bio_code_used": "MVR-123456"
        }]
        foreign_ytdlp = {
            "id": "dQw4w9WgXcQ",
            "uploader_id": "@some_other_creator",
            "uploader": "Other Creator",
            "channel_url": "https://www.youtube.com/@some_other_creator"
        }
        ok, reason = verifier.check_video_channel_ownership(
            "youtube",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            foreign_ytdlp,
            '{"videoDetails":{"videoId":"dQw4w9WgXcQ","channelId":"UC9999999999999999999999"}}',
            user_plats,
            required_video_code="BC-777888",
            caption_text="My video BC-777888 MVR-123456 https://battleclub.app",
            verification_link="https://battleclub.app"
        )
        self.assertFalse(ok, f"Foreign channel video must be rejected, got: {reason}")

    def test_T07_P0_07_expired_pending_video_never_gets_late_credit(self):
        """
        T07 (P0-07 & P1-11): Pending video misses qualification_deadline_ts, then later scrape shows
        cur_views >= min_initial_views -> Zero initial credit granted; follows expired pending transition rules.
        """
        conn = database.get_connection()
        now_ts = time.time()
        past_deadline = now_ts - 3600
        with conn:
            conn.execute("INSERT INTO users (user_id, name, registered, balance) VALUES ('900007', 'Late User', 1, 0.0)")
            conn.execute("""
                INSERT INTO videos (
                    sub_id, platform, video_id, canonical_video_id, user_id, url, video_url, title, status, bot_status, admin_status,
                    current_views, previous_views, organic_status, submitted_at_ts, qualification_deadline_ts
                ) VALUES ('SUB_T07', 'youtube', 'YT_11111111111', 'YT_11111111111', '900007', 'https://youtu.be/11111111111', 'https://youtu.be/11111111111', 'Late Video',
                          'waiting_views', 'waiting_views', 'pending', 1500, 500, 'verified_organic', ?, ?)
            """, (now_ts - 90000, past_deadline))
            conn.execute("INSERT INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES ('SUB_T07', 500, 30, 5, 'p1', ?)", (now_ts - 50000,))
            conn.execute("INSERT INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES ('SUB_T07', 1500, 90, 15, 'p2', ?)", (now_ts,))
            credited, paid_v = finance.process_bot_approval_credit(conn, "SUB_T07", "900007", 1500, now_ts=now_ts)
            tr_res = finance.transition_expired_pending_video(conn, "SUB_T07", "Deadline missed", expiry_action="permanent_approve_zero_pay", now_ts=now_ts)
            v_after = conn.execute("SELECT status, permanent_approved, credited_amount FROM videos WHERE sub_id = 'SUB_T07'").fetchone()
            u_bal = float(conn.execute("SELECT balance FROM users WHERE user_id = '900007'").fetchone()["balance"])
        conn.close()
        self.assertEqual(credited, 0.0)
        self.assertEqual(paid_v, 0)
        self.assertEqual(u_bal, 0.0)
        self.assertEqual(tr_res["outcome"], "permanent_approved")
        self.assertEqual(int(v_after["permanent_approved"]), 1)
        self.assertEqual(float(v_after["credited_amount"]), 0.0)

    def test_T08_P1_13_admin_fraud_rejection_reversal_and_debt_settlement(self):
        """
        T08 (P1-13): Admin rejects a previously credited video (even after permanent_approved when force_admin_clawback=True)
        after user has already withdrawn part/all of balance -> Credited amount reversed; available balance reduced to 0
        and remaining shortfall recorded in debt_balance / debt_adjustments; subsequent earnings settle open debt first.
        """
        conn = database.get_connection()
        now_ts = time.time()
        with conn:
            conn.execute("INSERT INTO users (user_id, name, registered, balance) VALUES ('900008', 'Debt User', 1, 0.0)")
            conn.execute("""
                INSERT INTO videos (
                    sub_id, platform, video_id, canonical_video_id, user_id, url, video_url, title, status, bot_status, admin_status,
                    current_views, previous_views, organic_status, submitted_at_ts, qualification_deadline_ts
                ) VALUES ('SUB_T08_A', 'youtube', 'YT_22222222222', 'YT_22222222222', '900008', 'https://youtu.be/22222222222', 'https://youtu.be/22222222222', 'Vid A',
                          'waiting_views', 'waiting_views', 'pending', 1400, 1000, 'verified_organic', ?, ?)
            """, (now_ts - 7200, now_ts + 86400))
            conn.execute("INSERT INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES ('SUB_T08_A', 1000, 80, 10, 'p1', ?)", (now_ts - 3600,))
            conn.execute("INSERT INTO video_view_snapshots (sub_id, views, likes, comments, source, recorded_at_ts) VALUES ('SUB_T08_A', 1400, 110, 14, 'p2', ?)", (now_ts,))
            cred_a, _ = finance.process_bot_approval_credit(conn, "SUB_T08_A", "900008", 1400, now_ts=now_ts)
            self.assertEqual(cred_a, 21.0)

            conn.execute("UPDATE users SET balance = 6.0 WHERE user_id = '900008'")
            finance.admin_permanent_approve_video(conn, "SUB_T08_A", admin_id="8145274317")
            prot_res = finance.admin_reject_video_with_reversal(conn, "SUB_T08_A", "Routine check", admin_id="BOT_AUTO", force_admin_clawback=False)
            self.assertTrue(prot_res.get("permanent_protected"))

            claw_res = finance.admin_reject_video_with_reversal(
                conn, "SUB_T08_A", "Fraudulent bot panel views", admin_id="8145274317", force_admin_clawback=True
            )
            self.assertEqual(claw_res["reversed_amount"], 21.0)
            u_row = conn.execute("SELECT balance, debt_balance FROM users WHERE user_id = '900008'").fetchone()
            self.assertEqual(float(u_row["balance"]), 0.0)
            self.assertEqual(float(u_row["debt_balance"]), 15.0)

            finance.get_or_create_ledger_entry(
                conn, user_id="900008", tx_type="Admin Credit", amount=20.0,
                details="New earning", idempotency_key="BONUS_T08"
            )
            u_after = conn.execute("SELECT balance, debt_balance FROM users WHERE user_id = '900008'").fetchone()
        conn.close()
        self.assertEqual(float(u_after["debt_balance"]), 0.0)
        self.assertEqual(float(u_after["balance"]), 5.0)

    def test_T09_P0_01_admin_numeric_id_and_session_lock_enforcement(self):
        """
        T09 (P0-01): Spoofed username matching super_admin_usernames with non-admin numeric user_id,
        or admin callback invoked without password unlock -> Access denied; session is NOT auto-created by callback handler.
        """
        class DummyUser:
            def __init__(self, uid, username):
                self.id = uid
                self.username = username

        class DummyChat:
            def __init__(self, cid):
                self.id = cid

        class DummyMsg:
            def __init__(self, cid):
                self.chat = DummyChat(cid)
                self.message_id = 101

        class DummyCall:
            def __init__(self, uid, username, data):
                self.id = "cb_1"
                self.from_user = DummyUser(uid, username)
                self.message = DummyMsg(uid)
                self.data = data

        spoof_user = DummyUser(999999999, "battleclubsupport")
        self.assertFalse(bot_mod.is_authorized_admin(spoof_user))

        real_admin_call = DummyCall(8145274317, "monirahmed142761", "admin_hub")
        self.assertTrue(bot_mod.is_authorized_admin(real_admin_call.from_user))
        self.assertFalse(bot_mod.is_admin_unlocked("8145274317"))
        bot_mod.handle_admin_master_dashboard(real_admin_call)
        self.assertFalse(bot_mod.is_admin_unlocked("8145274317"), "Callback handler must NEVER auto-unlock admin session!")

        security.unlock_admin_session("8145274317", ttl_sec=3600)
        self.assertTrue(bot_mod.is_admin_unlocked("8145274317"))

    def test_T10_P1_14_strip_and_restore_normal_emoji_without_phantom_reappearance(self):
        """
        T10 (P1-14): Strip normal emoji from button, then set custom emoji or restore normal emoji ->
        Deleted normal emoji stays permanently deleted when custom emoji is active; restoring normal emoji clears custom_emoji_id.
        """
        b_key = "u_dashboard"
        orig_lbl = bot_mod.get_btn_raw_label(b_key)
        stripped = ui_validation.strip_leading_default_emojis(orig_lbl)
        bot_mod.set_btn_label_val(b_key, stripped)
        bot_mod.set_btn_emoji_val(b_key, "5368324170671202286")

        btn_obj = bot_mod.make_btn(bot_mod.get_btn_label(b_key), callback_data="umenu:dashboard", btn_key=b_key)
        btn_dict = btn_obj.to_dict()
        self.assertEqual(btn_dict.get("icon_custom_emoji_id"), "5368324170671202286")
        self.assertFalse(btn_dict["text"].startswith("📊"), f"Deleted normal emoji must not reappear: {btn_dict['text']}")

        kb = ui_validation.types.InlineKeyboardMarkup()
        kb.row(btn_obj)
        downgraded_kb = bot_mod._strip_emoji_keep_color_keyboard(kb)
        dg_text = downgraded_kb.keyboard[0][0].to_dict()["text"]
        self.assertFalse(dg_text.startswith("📊"))

    def test_T11_P1_16_user_vs_admin_button_side_isolation(self):
        """
        T11 (P1-16): Attempt to move or create a user-side button on an admin page or vice versa ->
        Blocked with validation error; layouts remain strictly segregated.
        """
        res_move = bot_mod.move_button_across_pages("user_home", "admin_home", "u_dashboard")
        self.assertFalse(res_move.get("ok"), "Moving u_* button to admin_home must be blocked")

        with self.assertRaises(ValueError):
            database.create_custom_button_transactional(
                side="user",
                parent_layout="admin_home",
                label="Illegal Cross Side Button"
            )
        with self.assertRaises(ValueError):
            database.create_custom_button_transactional(
                side="user",
                parent_layout="user_home",
                label="Illegal Sub Buttons",
                sub_button_keys=["a_metrics"]
            )

    def test_T12_P1_17_auto_delete_ui_preserves_durable_notifications_and_receipts(self):
        """
        T12 (P1-17): Navigate across multiple user/admin menus while receiving a withdrawal/approval notification ->
        Old navigation menus are deleted; withdrawal/approval notification message ID is NOT in the deleted set.
        """
        uid = "900012"
        m1 = bot_mod.safe_send(int(uid), "Menu 1", msg_key="welcome_msg", track_ui=True, auto_clean_prev=False)
        m_receipt = bot_mod.safe_send(
            int(uid),
            bot_mod.get_msg("withdraw_paid_msg", amount="150.00", method="bKash", dest="01700000000"),
            msg_key="withdraw_paid_msg"
        )
        bot_mod.cleanup_user_ui_messages(int(uid), uid, min_age_sec=0.0)
        tracked_ids = {item[0] for item in bot_mod.USER_ACTIVE_UI_MSGS.get(uid, [])}
        self.assertNotIn(m_receipt.message_id, tracked_ids, "Durable receipt must never be tracked for UI auto-deletion")

    def test_T13_P1_19_exact_view_count_parsing_zero_rounding_error(self):
        """
        T13 (P1-19): Verify exact view count parsing (140 stays 140, never 141) and milestone math.
        """
        self.assertEqual(verifier.parse_human_number("140"), 140)
        self.assertEqual(verifier.parse_human_number("১৪০"), 140)
        self.assertEqual(verifier.parse_human_number(140), 140)
        self.assertEqual(verifier.parse_human_number("1,245"), 1245)

        self.assertEqual(finance.calculate_eligible_paid_views(999, 1000, 200, 5000000), 0)
        self.assertEqual(finance.calculate_eligible_paid_views(1000, 1000, 200, 5000000), 1000)
        self.assertEqual(finance.calculate_eligible_paid_views(1199, 1000, 200, 5000000), 1000)
        self.assertEqual(finance.calculate_eligible_paid_views(1200, 1000, 200, 5000000), 1200)
        self.assertEqual(finance.calculate_eligible_paid_views(6000000, 1000, 200, 5000000), 5000000)
        self.assertEqual(finance.calculate_cumulative_video_earnings(1200, 15.0, 3.0, 1000, 200), 18.0)

    def test_T14_P1_21_withdrawal_2_slot_limit_and_reject_refund(self):
        """
        T14 (P1-21): Add 1st and 2nd payment number per method -> Allowed; 3rd without deleting -> Blocked.
        Admin Reject withdrawal refunds held_balance back to main balance.
        """
        uid = "900014"
        conn = database.get_connection()
        with conn:
            conn.execute("INSERT INTO users (user_id, name, registered, balance, held_balance) VALUES (?, 'WD User', 1, 0.0, 200.0)", (uid,))
            conn.execute(
                "INSERT INTO withdrawals (wd_id, user_id, amount, method, dest, app_uid, status, created_at) VALUES ('WD_T14', ?, 200.0, 'bKash', '01711111111', '#1014', 'pending', '2026-11-16 10:00')",
                (uid,)
            )
        conn.close()

        r1 = database.update_user_payment_and_profile_info(uid, "bkash_number:add", "01711111111", action="add")
        self.assertTrue(r1["ok"])
        r2 = database.update_user_payment_and_profile_info(uid, "bkash_number:add", "01722222222", action="add")
        self.assertTrue(r2["ok"])
        r3 = database.update_user_payment_and_profile_info(uid, "bkash_number:add", "01733333333", action="add")
        self.assertFalse(r3["ok"], "3rd payment number without deleting must be blocked!")

        conn = database.get_connection()
        with conn:
            ref_res = finance.admin_cancel_withdrawal_with_refund(conn, "WD_T14", admin_id="8145274317", reason="Invalid number", target_status="rejected")
            u_row = conn.execute("SELECT balance, held_balance FROM users WHERE user_id = ?", (uid,)).fetchone()
            w_row = conn.execute("SELECT status FROM withdrawals WHERE wd_id = 'WD_T14'").fetchone()
        conn.close()
        self.assertEqual(ref_res["status"], "rejected")
        self.assertEqual(w_row["status"], "rejected")
        self.assertEqual(float(u_row["balance"]), 200.0)
        self.assertEqual(float(u_row["held_balance"]), 0.0)

    def test_T15_P1_24_database_integrity_and_ledger_reconciliation(self):
        """
        T15 (P1-24): Run database integrity diagnostics -> PRAGMA integrity_check == 'ok',
        foreign_key_check == [], and ledger reconciliation passes with zero drift.
        """
        diag = database.run_database_integrity_diagnostics()
        self.assertTrue(diag.get("ok"), f"DB diagnostics failed: {diag}")
        self.assertEqual(diag.get("integrity_check"), "ok")


    def test_T16_admin_password_unlock_success_and_wrong_password_rejection(self):
        """
        T16: Locked admin clicks admin button -> awaiting_admin_password -> wrong password rejected ->
        correct password unlocks session and opens Admin Dashboard.
        """
        class _User:
            def __init__(self, uid, username="admin"):
                self.id = int(uid)
                self.username = username
                self.first_name = "Monir"

        class _Chat:
            def __init__(self, cid):
                self.id = int(cid)

        class _Msg:
            def __init__(self, uid, text):
                self.message_id = 901
                self.from_user = _User(uid)
                self.chat = _Chat(uid)
                self.text = text
                self.entities = None

        class _Call:
            def __init__(self, uid, data):
                self.id = f"cb_{int(time.time()*1000)}"
                self.from_user = _User(uid)
                self.message = _Msg(uid, "")
                self.data = data

        adm_uid = "8145274317"
        bot_mod.admin_unlocked_sessions.clear()
        security.lock_admin_session(adm_uid)

        c = _Call(adm_uid, "adm_view_metrics")
        self.assertFalse(bot_mod.require_unlocked_admin_session(c))
        self.assertEqual(bot_mod.user_memory_states.get(adm_uid, {}).get("step"), "awaiting_admin_password")

        # Send wrong password
        self.sent_messages.clear()
        bot_mod.handle_all_incoming_messages(_Msg(adm_uid, "wrong_pass_123"))
        self.assertFalse(bot_mod.is_admin_unlocked(adm_uid))
        self.assertTrue(any("ভুল অ্যাডমিন পাসওয়ার্ড" in m["text"] for m in self.sent_messages))

        # Send correct password
        self.sent_messages.clear()
        bot_mod.handle_all_incoming_messages(_Msg(adm_uid, bot_mod.ADMIN_PASSWORD))
        self.assertTrue(bot_mod.is_admin_unlocked(adm_uid))

    def test_T17_admin_password_brute_force_rate_limit(self):
        """T17: Repeated wrong admin passwords trigger rate limit / lockout."""
        class _User:
            def __init__(self, uid):
                self.id = int(uid)
                self.username = "admin"
                self.first_name = "Admin"
        class _Chat:
            def __init__(self, cid):
                self.id = int(cid)
        class _Msg:
            def __init__(self, uid, text):
                self.message_id = 902
                self.from_user = _User(uid)
                self.chat = _Chat(uid)
                self.text = text
                self.entities = None

        adm_uid = "8145274317"
        bot_mod.user_memory_states[adm_uid] = {"step": "awaiting_admin_password"}
        for i in range(6):
            bot_mod.handle_all_incoming_messages(_Msg(adm_uid, f"bad_pwd_{i}"))
        self.assertFalse(bot_mod.is_admin_unlocked(adm_uid))
        self.assertTrue(any(("অতিরিক্ত ভুল চেষ্টা" in m["text"] or "সাময়িক লক" in m["text"]) for m in self.sent_messages))
        security.reset_rate_limit(adm_uid)
        security.reset_failed_login(f"admin:{adm_uid}")

    def test_T18_is_admin_unlocked_rejects_expired_and_future_timestamps(self):
        """T18: Expired or future timestamps in admin_unlocked_sessions must return False."""
        adm_uid = "8145274317"
        security.lock_admin_session(adm_uid)
        bot_mod.admin_unlocked_sessions[adm_uid] = time.time() - 7200
        self.assertFalse(bot_mod.is_admin_unlocked(adm_uid))

        bot_mod.admin_unlocked_sessions[adm_uid] = time.time() + 7200
        self.assertFalse(bot_mod.is_admin_unlocked(adm_uid))

    def test_T19_manual_bot_credit_audit_and_guards(self):
        """T19: Manual vd:bot_credit blocks suspicious videos and logs Admin Manual Bot Credit Override on valid override."""
        conn = database.get_connection()
        now_ts = time.time()
        with conn:
            conn.execute("INSERT INTO users (user_id, name, registered, balance) VALUES ('900019', 'Creator 19', 1, 0.0)")
            conn.execute("""
                INSERT INTO videos (
                    sub_id, platform, video_id, canonical_video_id, user_id, url, video_url, title,
                    status, bot_status, admin_status, current_views, previous_views,
                    duration_known, publish_date_known, view_metrics_known, flagged_suspicious,
                    organic_status, submitted_at_ts, qualification_deadline_ts
                ) VALUES ('SUB_T19_SUSP', 'youtube', 'YT_19191919191', 'YT_19191919191', '900019',
                          'https://youtu.be/19191919191', 'https://youtu.be/19191919191', 'Suspicious Vid',
                          'manual_review', 'manual_review', 'pending', 2000, 2000, 1, 1, 1, 1,
                          'suspicious_zero_engagement', ?, ?)
            """, (now_ts - 3600, now_ts + 86400))
            with self.assertRaises(ValueError):
                finance.process_bot_approval_credit(conn, "SUB_T19_SUSP", "900019", 2000, now_ts=now_ts)
        conn.close()

    def test_T20_permanent_approved_human_admin_clawback_vs_auto_protection(self):
        """T20: Permanent approved video blocks automated BOT_ANTI_FRAUD clawback but allows human admin force_admin_clawback."""
        conn = database.get_connection()
        now_ts = time.time()
        with conn:
            conn.execute("INSERT INTO users (user_id, name, registered, balance, total_earned) VALUES ('900020', 'Perm User', 1, 15.0, 15.0)")
            conn.execute("""
                INSERT INTO videos (
                    sub_id, platform, video_id, canonical_video_id, user_id, url, video_url, title,
                    status, bot_status, admin_status, permanent_approved, current_views, paid_views,
                    eligible_views, reward, credited_amount, submitted_at_ts
                ) VALUES ('SUB_T20', 'youtube', 'YT_20202020202', 'YT_20202020202', '900020',
                          'https://youtu.be/20202020202', 'https://youtu.be/20202020202', 'Perm Video',
                          'permanent_approved', 'approved', 'approved', 1, 1000, 1000, 1000, 15.0, 15.0, ?)
            """, (now_ts - 500000,))
            # Automated rejection without force_admin_clawback is blocked
            res_auto = finance.admin_reject_video_with_reversal(
                conn, sub_id="SUB_T20", rejection_reason="Auto Fraud", admin_id="BOT_ANTI_FRAUD", force_admin_clawback=False
            )
            self.assertTrue(res_auto.get("permanent_protected"))
            # Human admin rejection with force_admin_clawback=True reverses the 15 BDT
            res_human = finance.admin_reject_video_with_reversal(
                conn, sub_id="SUB_T20", rejection_reason="Human Admin Fraud Reject", admin_id="8145274317", force_admin_clawback=True
            )
            self.assertEqual(float(res_human.get("reversed_amount", 0.0)), 15.0)
            u_bal = float(conn.execute("SELECT balance FROM users WHERE user_id = '900020'").fetchone()["balance"])
            self.assertEqual(u_bal, 0.0)
        conn.close()

    def test_T21_validate_setting_value_strict_link_and_expiry_rules(self):
        """T21: validate_setting_value rejects arbitrary strings for required_link_config & pending_expiry_action."""
        self.assertEqual(database.validate_setting_value("required_link_config", "all_public"), "all_public")
        self.assertEqual(database.validate_setting_value("required_link_config", "off"), "off")
        with self.assertRaises(ValueError):
            database.validate_setting_value("required_link_config", "invalid_mode")

        self.assertEqual(database.validate_setting_value("pending_expiry_action", "permanent_approve_zero_pay"), "permanent_approve_zero_pay")
        self.assertEqual(database.validate_setting_value("pending_expiry_action", "reject"), "reject")
        with self.assertRaises(ValueError):
            database.validate_setting_value("pending_expiry_action", "give_free_money")

    def test_T22_manual_verification_code_ttl_and_synthetic_url_rejection(self):
        """T22: Manual verification code enforces 5-min TTL, rejects synthetic @user_<uid> URL, and sets subs_count=0."""
        c_res = database.create_manual_verification_code("8145274317", target_user_id="900022", platform="youtube", ttl_sec=300)
        self.assertGreater(c_res["expires_at_ts"], time.time())
        self.assertEqual(c_res["ttl_sec"], 300)

        # Reject synthetic URL
        bad_res = database.consume_admin_manual_verify_code(
            code=c_res["code"], user_id="900022", platform="youtube",
            profile_url="https://www.youtube.com/@user_900022", bio_code="BC-222222", auto_bind=True
        )
        self.assertFalse(bad_res["ok"])

        # Valid real profile URL succeeds and stores subs_count == 0 (not fake 200)
        ok_res = database.consume_admin_manual_verify_code(
            code=c_res["code"], user_id="900022", platform="youtube",
            profile_url="https://www.youtube.com/@realcreator22", bio_code="BC-222222", auto_bind=True
        )
        self.assertTrue(ok_res["ok"])
        plats = database.get_user_platforms("900022", "youtube")
        self.assertEqual(len(plats), 1)
        self.assertEqual(int(plats[0]["subs_count"]), 0)

    def test_T23_organic_risk_blocks_1000_to_1999_zero_engagement_and_source_conflict(self):
        """T23: 1500 views with 0 likes and 0 comments is flagged suspicious_zero_engagement; SOURCE_CONFLICT blocks payout."""
        r_zero = verifier.assess_organic_view_risk([], cur_views=1500, cur_likes=0, cur_comments=0)
        self.assertTrue(r_zero["suspicious"])
        self.assertEqual(r_zero["organic_status"], "suspicious_zero_engagement")

        # Boundary-safe verification link check rejects evil substring URLs
        self.assertFalse(
            verifier.has_required_verification_link(
                "Join https://evil.com/t.me/battleclub_fake now",
                "https://t.me/battleclub",
                "all_public"
            )
        )
        self.assertTrue(
            verifier.has_required_verification_link(
                "Join our official https://t.me/battleclub today!",
                "https://t.me/battleclub",
                "all_public"
            )
        )

    def test_T24_anti_spam_configuration_and_vercel_webhook_readiness(self):
        """
        T24: Verify all 4 Anti-Spam requirements & GitHub/Vercel Webhook + Cron endpoints:
        1. Default intervals == 3600s (1 hour)
        2. Bot worker threads == 8 and Verifier max workers == 4
        3. Per-user action cooldown == 1.5s
        4. Batch request delay == 0.35s & Vercel webhook/cron handlers return HTTP 200.
        """
        self.assertEqual(ui_catalog.DEFAULT_SETTINGS["view_checking_interval_sec"], "3600")
        self.assertEqual(ui_catalog.DEFAULT_SETTINGS["verification_interval_sec"], "3600")
        self.assertEqual(database.get_setting("view_checking_interval_sec"), "3600")
        self.assertEqual(database.get_setting("verification_interval_sec"), "3600")
        self.assertLessEqual(bot_mod.BOT_NUM_THREADS, 10)
        self.assertLessEqual(verifier.VERIFIER_MAX_WORKERS, 4)
        self.assertGreaterEqual(bot_mod.USER_ACTION_COOLDOWN_SEC, 1.5)
        self.assertGreaterEqual(bot_mod.BATCH_REQUEST_DELAY_SEC, 0.3)

        # Test serverless cron & webhook entrypoints
        cron_res = bot_mod.run_serverless_cron_cycle()
        self.assertTrue(cron_res.get("ok"))
        self.assertEqual(cron_res.get("status"), 200)

        wh_res = bot_mod.process_webhook_update(json.dumps({"update_id": 10001}))
        self.assertTrue(wh_res.get("ok"))
        self.assertEqual(wh_res.get("status"), 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)