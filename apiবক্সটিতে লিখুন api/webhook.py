# -*- coding: utf-8 -*-
"""
BATTLE CLUB CREATOR BOT — VERCEL SERVERLESS WEBHOOK & CRON ENTRYPOINT (`api/index.py`)
Supports:
- POST `/api/webhook` or `/api/index` or `/` -> Telegram Webhook Update Handler
- GET  `/api/cron` -> Scheduled Video View Monitoring & Session Cleanup Pass
- GET  `/api/set_webhook` -> One-Click Telegram Webhook Registration Helper
- GET  `/` or `/api/health` -> Bot Health & Anti-Spam Configuration Status
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import battle_club_bot as bot_mod


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(int(status_code))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path_clean = parsed.path.rstrip("/") or "/"
        qs = dict(parse_qsl(parsed.query))

        if path_clean in ("/api/cron", "/cron"):
            res = bot_mod.run_serverless_cron_cycle()
            self._send_json(int(res.get("status", 200)), res)
            return

        if path_clean in ("/api/set_webhook", "/set_webhook"):
            bot_mod.ensure_bot_runtime_initialized()
            host_hdr = self.headers.get("x-forwarded-host") or self.headers.get("host") or os.getenv("VERCEL_URL", "")
            base_url = os.getenv("WEBHOOK_URL", "").strip() or (f"https://{host_hdr}" if host_hdr else "")
            if not base_url:
                self._send_json(400, {"ok": False, "error": "Missing WEBHOOK_URL or Host header"})
                return
            wh_target = base_url.rstrip("/")
            if not wh_target.endswith(("/api/webhook", "/webhook", "/api/index")):
                wh_target = wh_target + "/api/webhook"
            try:
                bot_mod.bot.remove_webhook()
                secret_tok = os.getenv("WEBHOOK_SECRET_TOKEN", "").strip() or None
                if secret_tok:
                    bot_mod.bot.set_webhook(url=wh_target, secret_token=secret_tok, allowed_updates=["message", "edited_message", "callback_query"])
                else:
                    bot_mod.bot.set_webhook(url=wh_target, allowed_updates=["message", "edited_message", "callback_query"])
                self._send_json(200, {"ok": True, "webhook_url": wh_target, "message": "Telegram Webhook successfully registered!"})
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc), "webhook_url": wh_target})
            return

        bot_mod.ensure_bot_runtime_initialized()
        self._send_json(200, {
            "ok": True,
            "service": "Battle Club Creator Sponsorship Bot",
            "platform": "Vercel / GitHub Cloud Ready",
            "num_threads": bot_mod.BOT_NUM_THREADS,
            "user_cooldown_sec": bot_mod.USER_ACTION_COOLDOWN_SEC,
            "batch_delay_sec": bot_mod.BATCH_REQUEST_DELAY_SEC,
            "view_checking_interval_sec": bot_mod.get_setting("view_checking_interval_sec", "3600"),
            "verification_interval_sec": bot_mod.get_setting("verification_interval_sec", "3600")
        })

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""
        sec_hdr = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        res = bot_mod.process_webhook_update(raw_body, secret_header=sec_hdr)
        self._send_json(int(res.get("status", 200)), res)

    def log_message(self, format_str, *args):
        return
