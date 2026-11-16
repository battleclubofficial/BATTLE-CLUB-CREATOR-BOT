# -*- coding: utf-8 -*-
"""
BATTLE CLUB TELEGRAM BOT - IMMUTABLE LEDGER & ATOMIC FINANCIAL ENGINE (ENTERPRISE v9.0)
- SQLite `BEGIN IMMEDIATE` Write Locks + Savepoints + Thread-Safe RLock + Database-Level UNIQUE Idempotency
- Zero Double-Credit, Zero Double-Deduction & Zero Double-Withdrawal Under Any Concurrency Scenario
- View-Based Earning with 50,00,000 (50 Lakh) Default View Cap & 5-Day Default Tracking Window:
  * First Target Views (default 1,000) = Configurable Initial Payment (e.g., 15 Taka)
  * Every Additional Step Views (default 200) = Configurable Step Payment (e.g., 3 Taka)
  * Zero Payment Before Reaching Target Views (`min_initial_views`)
  * Strict High-Water Mark (`paid_views`) & Idempotency Key (`MILESTONE:{sub_id}:{prev_paid}->{eligible_views}`)
  * Final Payout Before Permanent Approval: Credits all eligible views up to the cap/window first,
    then immediately transitions to PERMANENT APPROVE (`permanent_approved = 1`, `status = 'permanent_approved'`).
- Strict Zero Double-Credit on Admin Approve (`admin_accept_bot_approved_video`)
- External Traffic Link Approve / Reset / Reject Engine (`resolve_external_link_financial_action` & `reset_external_link_video_earnings`)
- Full Financial Reversal & Debt Recovery Workflow (Pending Withdraw Auto-Cancel + Completed Withdraw Debt Tracking & Auto-Deduction)
"""

import os
import re
import json
import time
import secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime

_finance_lock = threading.RLock()


@contextmanager
def _atomic_immediate_tx(conn: sqlite3.Connection):
    """
    Ensures every financial mutation runs inside a SQLite `BEGIN IMMEDIATE` transaction
    (acquiring a database-level reserved write lock immediately) or an atomic `SAVEPOINT`
    if the connection is already inside a transaction.
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
        sp = f"fin_sp_{secrets.token_hex(4)}"
        conn.execute(f"SAVEPOINT {sp}")
        try:
            yield conn
            conn.execute(f"RELEASE SAVEPOINT {sp}")
        except Exception:
            conn.execute(f"ROLLBACK TO SAVEPOINT {sp}")
            conn.execute(f"RELEASE SAVEPOINT {sp}")
            raise


def _ensure_ledger_unique_index(conn: sqlite3.Connection) -> None:
    """
    Ensures `idx_ledger_idempotency_key_unique` exists on `ledger_transactions(idempotency_key)`.
    Never swallows exceptions silently: if legacy duplicate or empty `idempotency_key` rows exist,
    reconciles them deterministically without data loss and enforces the database-level UNIQUE index.
    """
    idx_rows = conn.execute("PRAGMA index_list(ledger_transactions)").fetchall()
    for r in idx_rows:
        idx_name = r["name"] if isinstance(r, sqlite3.Row) else r[1]
        is_uniq = r["unique"] if isinstance(r, sqlite3.Row) else r[2]
        if str(idx_name) == "idx_ledger_idempotency_key_unique" and int(is_uniq or 0) == 1:
            return

    with _atomic_immediate_tx(conn):
        conn.execute("UPDATE ledger_transactions SET idempotency_key = NULL WHERE idempotency_key = ''")
        dup_groups = conn.execute("""
            SELECT idempotency_key, COUNT(*) as cnt
            FROM ledger_transactions
            WHERE idempotency_key IS NOT NULL
            GROUP BY idempotency_key
            HAVING COUNT(*) > 1
        """).fetchall()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for dg in dup_groups:
            idem_k = str(dg["idempotency_key"] if isinstance(dg, sqlite3.Row) else dg[0])
            rows = conn.execute(
                "SELECT rowid, tx_id, user_id FROM ledger_transactions WHERE idempotency_key = ? ORDER BY rowid ASC",
                (idem_k,)
            ).fetchall()
            for idx, dup_row in enumerate(rows[1:], start=2):
                rid = dup_row["rowid"] if isinstance(dup_row, sqlite3.Row) else dup_row[0]
                tx_id = str((dup_row["tx_id"] if isinstance(dup_row, sqlite3.Row) else dup_row[1]) or f"ROW_{rid}")
                u_id = str((dup_row["user_id"] if isinstance(dup_row, sqlite3.Row) else dup_row[2]) or "")
                new_key = f"{idem_k}__LEGACY_DUP_{idx}_{tx_id}"
                conn.execute("UPDATE ledger_transactions SET idempotency_key = ? WHERE rowid = ?", (new_key, rid))
                _record_audit_log(
                    conn,
                    "SYSTEM_FINANCE_INDEX",
                    u_id,
                    "Legacy Ledger Duplicate Key Reconciled",
                    f"Reconciled duplicate idempotency_key '{idem_k}' on tx {tx_id} -> '{new_key}'",
                    now_str
                )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_ledger_idempotency_key_unique ON ledger_transactions(idempotency_key)"
        )

    verify_rows = conn.execute("PRAGMA index_list(ledger_transactions)").fetchall()
    has_uniq = any(
        str(r["name"] if isinstance(r, sqlite3.Row) else r[1]) == "idx_ledger_idempotency_key_unique"
        and int((r["unique"] if isinstance(r, sqlite3.Row) else r[2]) or 0) == 1
        for r in verify_rows
    )
    if not has_uniq:
        raise sqlite3.IntegrityError("Failed to enforce UNIQUE index idx_ledger_idempotency_key_unique on ledger_transactions")


def _extract_sub_id(text: str, explicit_sub_id: str = "") -> str:
    if explicit_sub_id and str(explicit_sub_id).strip():
        return str(explicit_sub_id).strip()
    m = re.search(r"\b(V[0-9]+_[A-Za-z0-9_]+|SUB_[A-Za-z0-9_]+|VID_[A-Za-z0-9_]+)\b", str(text or ""))
    if m:
        return m.group(1)
    return ""


def get_max_payable_views_setting(
    conn: sqlite3.Connection = None,
    explicit_cap: int = None,
    sub_id: str = "",
    platform: str = ""
) -> int:
    if explicit_cap is not None:
        return max(0, int(explicit_cap))

    global_cap = None
    if conn is not None:
        for tbl in ("dynamic_settings", "settings"):
            try:
                row = conn.execute(
                    f"SELECT value FROM {tbl} WHERE key = 'max_payable_views' LIMIT 1"
                ).fetchone()
                if row is not None:
                    val = row["value"] if isinstance(row, sqlite3.Row) else row[0]
                    if val is not None and str(val).strip() != "":
                        global_cap = max(0, int(float(str(val).strip())))
                        break
            except Exception:
                pass

        plat = str(platform or "").lower().strip()
        if not plat and sub_id:
            try:
                v_row = conn.execute(
                    "SELECT platform FROM videos WHERE sub_id = ? LIMIT 1",
                    (str(sub_id),)
                ).fetchone()
                if v_row:
                    plat = str((v_row["platform"] if isinstance(v_row, sqlite3.Row) else v_row[0]) or "").lower().strip()
            except Exception:
                plat = ""

        if plat:
            try:
                p_row = conn.execute(
                    "SELECT max_payable_views, custom_overrides_json FROM platform_criteria WHERE platform = ? LIMIT 1",
                    (plat,)
                ).fetchone()
                if p_row is not None:
                    p_val = p_row["max_payable_views"]
                    try:
                        ov = json.loads(p_row["custom_overrides_json"] or "{}")
                    except Exception:
                        ov = {}
                    if p_val is not None and str(p_val).strip() != "":
                        p_cap = max(0, int(float(str(p_val).strip())))
                        if ov.get("max_payable_views") or p_cap != 5000000 or global_cap is None:
                            return p_cap
            except Exception:
                pass

        if global_cap is not None:
            return global_cap

    env_val = os.getenv("MAX_PAYABLE_VIEWS", "").strip()
    if env_val:
        try:
            return max(0, int(float(env_val)))
        except Exception:
            pass

    return 5000000


def get_video_tracking_days(
    conn: sqlite3.Connection = None,
    sub_id: str = "",
    platform: str = "",
    explicit_days: int = None
) -> int:
    if explicit_days is not None:
        return max(1, int(explicit_days))

    global_days = None
    if conn is not None:
        for tbl in ("dynamic_settings", "settings"):
            try:
                r = conn.execute(
                    f"SELECT value FROM {tbl} WHERE key IN ('earning_duration_days', 'view_tracking_days') ORDER BY key ASC LIMIT 1"
                ).fetchone()
                if r and r["value"] is not None and str(r["value"]).strip() != "":
                    global_days = max(1, int(float(str(r["value"]).strip())))
                    break
            except Exception:
                pass

        plat = str(platform or "").lower().strip()
        if not plat and sub_id:
            try:
                v_row = conn.execute("SELECT platform FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
                if v_row:
                    plat = str(v_row["platform"] or "").lower().strip()
            except Exception:
                plat = ""

        if plat:
            try:
                p_row = conn.execute(
                    "SELECT earning_duration_days, custom_overrides_json FROM platform_criteria WHERE platform = ? LIMIT 1",
                    (plat,)
                ).fetchone()
                if p_row and p_row["earning_duration_days"] is not None:
                    p_days = max(1, int(float(p_row["earning_duration_days"])))
                    try:
                        ov = json.loads(p_row["custom_overrides_json"] or "{}")
                    except Exception:
                        ov = {}
                    if ov.get("earning_duration_days") or p_days != 5 or global_days is None:
                        return p_days
            except Exception:
                pass

    return global_days if global_days is not None else 5


def get_video_payment_rates(
    conn: sqlite3.Connection = None,
    sub_id: str = "",
    explicit_first_1k: float = None,
    explicit_every_200: float = None,
    platform: str = ""
) -> tuple:
    first_1k = float(explicit_first_1k) if explicit_first_1k is not None else None
    every_200 = float(explicit_every_200) if explicit_every_200 is not None else None
    min_init = None
    step_sz = None
    global_first = None
    global_every = None
    global_min_init = None
    global_step_sz = None

    if conn is not None:
        for tbl in ("dynamic_settings", "settings"):
            try:
                rows = conn.execute(
                    f"SELECT key, value FROM {tbl} WHERE key IN "
                    "('first_1000_views_payment', 'rate_per_1k', 'every_200_views_payment', 'min_initial_views', 'view_step_size')"
                ).fetchall()
                kv = {r["key"]: r["value"] for r in rows if r["value"] is not None and str(r["value"]).strip() != ""}
                if global_first is None:
                    if "first_1000_views_payment" in kv:
                        global_first = float(kv["first_1000_views_payment"])
                    elif "rate_per_1k" in kv:
                        global_first = float(kv["rate_per_1k"])
                if global_every is None and "every_200_views_payment" in kv:
                    global_every = float(kv["every_200_views_payment"])
                if global_min_init is None and "min_initial_views" in kv:
                    global_min_init = max(1, int(float(kv["min_initial_views"])))
                if global_step_sz is None and "view_step_size" in kv:
                    global_step_sz = max(1, int(float(kv["view_step_size"])))
            except Exception:
                continue

        plat = str(platform or "").lower().strip()
        if not plat and sub_id:
            try:
                v_row = conn.execute("SELECT platform FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
                if v_row:
                    plat = str(v_row["platform"] or "").lower().strip()
            except Exception:
                plat = ""
        if plat:
            try:
                p_row = conn.execute(
                    "SELECT * FROM platform_criteria WHERE platform = ? LIMIT 1",
                    (plat,)
                ).fetchone()
                if p_row:
                    p_dict = dict(p_row)
                    try:
                        ov = json.loads(p_dict.get("custom_overrides_json") or "{}")
                    except Exception:
                        ov = {}
                    if explicit_first_1k is None:
                        if p_dict.get("rate_per_1k") is not None and (ov.get("rate_per_1k") or global_first is None or float(p_dict["rate_per_1k"]) != 15.0):
                            first_1k = float(p_dict["rate_per_1k"])
                        elif global_first is not None:
                            first_1k = global_first
                        elif p_dict.get("rate_per_1k") is not None:
                            first_1k = float(p_dict["rate_per_1k"])
                    if explicit_every_200 is None:
                        if p_dict.get("every_200_views_payment") is not None and (ov.get("every_200_views_payment") or global_every is None or float(p_dict["every_200_views_payment"]) != 3.0):
                            every_200 = float(p_dict["every_200_views_payment"])
                        elif global_every is not None:
                            every_200 = global_every
                        elif p_dict.get("every_200_views_payment") is not None:
                            every_200 = float(p_dict["every_200_views_payment"])
                    if p_dict.get("min_initial_views") is not None:
                        p_min_init = max(1, int(float(p_dict["min_initial_views"])))
                        if ov.get("min_initial_views") or p_min_init != 1000 or global_min_init is None:
                            min_init = p_min_init
                    if p_dict.get("step_size") is not None:
                        p_step = max(1, int(float(p_dict["step_size"])))
                        if ov.get("step_size") or p_step != 200 or global_step_sz is None:
                            step_sz = p_step
            except Exception:
                pass

    if first_1k is None:
        first_1k = global_first if global_first is not None else 15.0
    if min_init is None:
        min_init = global_min_init if global_min_init is not None else 1000
    if step_sz is None:
        step_sz = global_step_sz if global_step_sz is not None else 200
    if every_200 is None:
        if global_every is not None:
            every_200 = global_every
        else:
            every_200 = round((first_1k / float(min_init)) * step_sz, 4)

    return round(first_1k, 4), round(every_200, 4), max(1, int(min_init)), max(1, int(step_sz))


def _sync_video_counters(conn: sqlite3.Connection, user_id: str) -> None:
    counts = conn.execute("""
        SELECT
            COUNT(*) AS submitted,
            SUM(CASE WHEN (bot_status = 'approved' OR admin_status = 'approved' OR COALESCE(permanent_approved, 0) = 1)
                      AND bot_status != 'rejected' AND admin_status != 'rejected' AND status != 'rejected'
                     THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN admin_status = 'rejected' OR bot_status = 'rejected' OR status = 'rejected'
                     THEN 1 ELSE 0 END) AS rejected
        FROM videos WHERE user_id = ? AND COALESCE(is_trashed, 0) = 0
    """, (str(user_id),)).fetchone()
    if counts:
        conn.execute(
            "UPDATE users SET videos_submitted = ?, videos_approved = ?, videos_rejected = ? WHERE user_id = ?",
            (int(counts["submitted"] or 0), int(counts["approved"] or 0), int(counts["rejected"] or 0), str(user_id))
        )


def _settle_open_debts(conn: sqlite3.Connection, uid: str, deduct_amt: float) -> None:
    rem_to_clear = round(float(deduct_amt or 0.0), 2)
    if rem_to_clear <= 0:
        return
    conn.execute("""
        CREATE TABLE IF NOT EXISTS debt_adjustments (
            adj_id TEXT PRIMARY KEY,
            user_id TEXT,
            sub_id TEXT DEFAULT '',
            total_clawback REAL DEFAULT 0.0,
            deducted_from_balance REAL DEFAULT 0.0,
            remaining_debt REAL DEFAULT 0.0,
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT ''
        )
    """)
    open_debts = conn.execute(
        "SELECT adj_id, deducted_from_balance, remaining_debt FROM debt_adjustments "
        "WHERE user_id = ? AND status = 'open' ORDER BY rowid ASC",
        (uid,)
    ).fetchall()
    for od in open_debts:
        if rem_to_clear <= 0:
            break
        adj_id = od["adj_id"]
        cur_rem = round(float(od["remaining_debt"] or 0.0), 2)
        cur_ded = round(float(od["deducted_from_balance"] or 0.0), 2)

        if cur_rem <= 0:
            conn.execute("UPDATE debt_adjustments SET status = 'resolved' WHERE adj_id = ?", (adj_id,))
            continue

        pay_now = round(min(cur_rem, rem_to_clear), 2)
        new_rem = round(cur_rem - pay_now, 2)
        new_ded = round(cur_ded + pay_now, 2)
        rem_to_clear = round(rem_to_clear - pay_now, 2)
        new_status = "resolved" if new_rem <= 0.001 else "open"

        conn.execute(
            "UPDATE debt_adjustments SET deducted_from_balance = ?, remaining_debt = ?, status = ? WHERE adj_id = ?",
            (new_ded, max(0.0, new_rem), new_status, adj_id)
        )


def _insert_ledger_row(
    conn: sqlite3.Connection,
    tx_id: str,
    idempotency_key: str,
    user_id: str,
    video_id: str,
    tx_type: str,
    amount: float,
    before_balance: float,
    after_balance: float,
    reference_id: str,
    details: str,
    admin_id: str,
    now_str: str
):
    conn.execute("""
        INSERT INTO ledger_transactions (
            tx_id, idempotency_key, user_id, video_id, sub_id,
            type, transaction_type, amount,
            before_balance, previous_balance, after_balance, new_balance,
            reference_id, details, admin_id, created_at, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tx_id,
        idempotency_key if (idempotency_key and str(idempotency_key).strip()) else None,
        str(user_id),
        str(video_id or ""),
        str(video_id or ""),
        str(tx_type),
        str(tx_type),
        round(float(amount), 2),
        round(float(before_balance), 2),
        round(float(before_balance), 2),
        round(float(after_balance), 2),
        round(float(after_balance), 2),
        str(reference_id or tx_id),
        str(details or ""),
        str(admin_id or ""),
        now_str,
        now_str
    ))


def _record_audit_log(conn: sqlite3.Connection, actor_id: str, target_user_id: str, action: str, details: str, now_str: str):
    try:
        conn.execute("""
            INSERT INTO audit_logs (actor_id, target_user_id, action, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (str(actor_id or "SYSTEM"), str(target_user_id or ""), str(action), str(details), now_str))
    except Exception:
        pass


def get_or_create_ledger_entry(
    conn: sqlite3.Connection,
    user_id: str,
    tx_type: str,
    amount: float,
    details: str = "",
    idempotency_key: str = None,
    admin_id: str = "",
    sub_id: str = "",
    reference_id: str = "",
    allow_partial_wd_cancel: bool = False
) -> dict:
    """
    Executes an atomic financial ledger operation inside a SQLite `BEGIN IMMEDIATE` transaction
    with database-level `idempotency_key` uniqueness, negative-balance / debt tracking,
    and Pending Withdrawal conflict resolution.
    """
    with _finance_lock:
        uid = str(user_id)
        amt = round(float(amount or 0.0), 2)
        if amt < 0:
            raise ValueError("Amount must be non-negative")

        clean_idem = str(idempotency_key).strip() if (idempotency_key and str(idempotency_key).strip()) else None
        _ensure_ledger_unique_index(conn)

        try:
            with _atomic_immediate_tx(conn):
                if clean_idem:
                    existing = conn.execute(
                        "SELECT * FROM ledger_transactions WHERE idempotency_key = ?",
                        (clean_idem,)
                    ).fetchone()
                    if existing:
                        return dict(existing)

                u = conn.execute(
                    "SELECT balance, held_balance, debt_balance, total_earned FROM users WHERE user_id = ?",
                    (uid,)
                ).fetchone()
                if not u:
                    raise ValueError(f"User {uid} not found")

                before_bal = round(float(u["balance"] or 0.0), 2)
                held_bal = round(float(u["held_balance"] or 0.0), 2)
                debt_bal = round(float(u["debt_balance"] or 0.0), 2)
                tot_earned = round(float(u["total_earned"] or 0.0), 2)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tx_id = f"TX_{int(time.time()*1000)}_{secrets.token_hex(4).upper()}"
                clean_sub_id = _extract_sub_id(details, sub_id)
                ref_id = str(reference_id or clean_sub_id or tx_id)

                after_bal = before_bal
                signed_amt = amt
                auto_cancelled_wds = []
                remainder_debt_added = 0.0
                debt_paid_from_income = 0.0

                if tx_type in ("Video Milestone", "Bot Approval Credit", "Reward Credit", "Referral Bonus", "Redeem Bonus", "Admin Credit", "Deposit"):
                    tot_earned = round(tot_earned + amt, 2)
                    if debt_bal > 0 and amt > 0:
                        debt_paid_from_income = round(min(debt_bal, amt), 2)
                        net_credit = round(amt - debt_paid_from_income, 2)
                        new_debt = round(debt_bal - debt_paid_from_income, 2)
                        after_bal = round(before_bal + net_credit, 2)
                        signed_amt = net_credit

                        conn.execute(
                            "UPDATE users SET balance = ?, debt_balance = ?, total_earned = ? WHERE user_id = ?",
                            (after_bal, new_debt, tot_earned, uid)
                        )
                        _settle_open_debts(conn, uid, debt_paid_from_income)
                        details = f"{details} | Gross: +{amt:.2f}৳, Auto Debt Paid: -{debt_paid_from_income:.2f}৳, Net Credited: +{net_credit:.2f}৳"
                    else:
                        after_bal = round(before_bal + amt, 2)
                        signed_amt = amt
                        conn.execute(
                            "UPDATE users SET balance = ?, total_earned = ? WHERE user_id = ?",
                            (after_bal, tot_earned, uid)
                        )

                elif tx_type in ("Video Reversal Restore", "Earnings Restoration"):
                    cash_to_restore = amt
                    debt_cancelled = 0.0
                    if clean_sub_id:
                        open_v_debts = conn.execute(
                            "SELECT adj_id, deducted_from_balance, remaining_debt FROM debt_adjustments "
                            "WHERE user_id = ? AND sub_id = ? AND status = 'open' ORDER BY rowid ASC",
                            (uid, clean_sub_id)
                        ).fetchall()
                        if open_v_debts:
                            cash_to_restore = 0.0
                            for od in open_v_debts:
                                r_debt = round(float(od["remaining_debt"] or 0.0), 2)
                                d_bal = round(float(od["deducted_from_balance"] or 0.0), 2)
                                debt_cancelled = round(debt_cancelled + r_debt, 2)
                                cash_to_restore = round(cash_to_restore + d_bal, 2)
                                conn.execute(
                                    "UPDATE debt_adjustments SET remaining_debt = 0.0, status = 'restored' WHERE adj_id = ?",
                                    (od["adj_id"],)
                                )
                            cash_to_restore = min(amt, round(cash_to_restore, 2))

                    new_debt = max(0.0, round(debt_bal - debt_cancelled, 2))
                    after_bal = round(before_bal + cash_to_restore, 2)
                    tot_earned = round(tot_earned + amt, 2)
                    signed_amt = cash_to_restore

                    conn.execute(
                        "UPDATE users SET balance = ?, debt_balance = ?, total_earned = ? WHERE user_id = ?",
                        (after_bal, new_debt, tot_earned, uid)
                    )
                    if debt_cancelled > 0:
                        details = f"{details} | Restored Cash: +{cash_to_restore:.2f}৳, Debt Cancelled: {debt_cancelled:.2f}৳"

                elif tx_type == "Withdraw Reserve":
                    if debt_bal > 0:
                        raise ValueError("বকেয়া ঋণ (Debt Balance) পরিশোধ না হওয়া পর্যন্ত নতুন উইথড্র করা যাবে না।")
                    if before_bal + 1e-9 < amt or amt <= 0:
                        raise ValueError("Insufficient balance for withdrawal reservation")
                    after_bal = max(0.0, round(before_bal - amt, 2))
                    new_held = round(held_bal + amt, 2)
                    signed_amt = -amt
                    cur_w = conn.execute(
                        "UPDATE users SET balance = ?, held_balance = ? WHERE user_id = ? AND balance + 1e-9 >= ? AND COALESCE(debt_balance, 0) <= 0",
                        (after_bal, new_held, uid, amt)
                    )
                    if cur_w.rowcount != 1:
                        raise ValueError("Insufficient balance or active debt during atomic withdrawal reservation")

                elif tx_type == "Withdraw Paid":
                    if held_bal + 0.01 < amt:
                        raise ValueError(f"Insufficient held balance ({held_bal:.2f}৳) to mark {amt:.2f}৳ as paid")
                    new_held = max(0.0, round(held_bal - amt, 2))
                    after_bal = before_bal
                    signed_amt = -amt
                    conn.execute(
                        "UPDATE users SET held_balance = ? WHERE user_id = ?",
                        (new_held, uid)
                    )

                elif tx_type in ("Withdraw Cancelled", "Withdraw Refund"):
                    if held_bal + 0.009 < amt:
                        raise ValueError(
                            f"Held withdrawal balance is short ({held_bal:.2f}৳ < {amt:.2f}৳); reconcile this request before refunding."
                        )
                    actual_refund = amt
                    new_held = max(0.0, round(held_bal - actual_refund, 2))
                    after_bal = round(before_bal + actual_refund, 2)
                    signed_amt = actual_refund
                    conn.execute(
                        "UPDATE users SET balance = ?, held_balance = ? WHERE user_id = ?",
                        (after_bal, new_held, uid)
                    )

                elif tx_type in ("Video Clawback", "Video Reversal", "Reward Reversal", "External Link Clawback", "External Link Reset", "Admin Debit"):
                    if before_bal + 1e-9 < amt:
                        min_wd_val = 100.0
                        try:
                            mw_row = conn.execute("SELECT value FROM dynamic_settings WHERE key = 'min_withdraw' LIMIT 1").fetchone()
                            if mw_row and mw_row["value"]:
                                min_wd_val = float(mw_row["value"])
                        except Exception:
                            pass

                        pend_wds = conn.execute(
                            "SELECT wd_id, amount, original_amount, method, dest FROM withdrawals WHERE user_id = ? AND status = 'pending' ORDER BY rowid DESC",
                            (uid,)
                        ).fetchall()
                        for pw in pend_wds:
                            if before_bal + 1e-9 >= amt:
                                break
                            w_id = pw["wd_id"]
                            w_amt = round(float(pw["amount"] or 0.0), 2)
                            orig_amt = round(float(pw["original_amount"] or w_amt), 2)
                            if w_amt <= 0:
                                continue

                            shortfall = round(amt - before_bal, 2)
                            if allow_partial_wd_cancel and (w_amt - shortfall) >= min_wd_val:
                                refund_amt = shortfall
                                rem_wd_amt = round(w_amt - refund_amt, 2)
                                prev_b = before_bal
                                before_bal = round(before_bal + refund_amt, 2)
                                held_bal = max(0.0, round(held_bal - refund_amt, 2))

                                conn.execute(
                                    "UPDATE withdrawals SET amount = ?, original_amount = ?, "
                                    "decision_reason = 'Partially adjusted due to video rejection reversal' WHERE wd_id = ?",
                                    (rem_wd_amt, orig_amt, w_id)
                                )
                                cancel_tx_id = f"TX_{int(time.time()*1000)}_{secrets.token_hex(4).upper()}"
                                _insert_ledger_row(
                                    conn=conn,
                                    tx_id=cancel_tx_id,
                                    idempotency_key=f"AUTO_PARTIAL_WD:{w_id}:{tx_id}",
                                    user_id=uid,
                                    video_id=clean_sub_id,
                                    tx_type="Withdraw Partial Refund",
                                    amount=refund_amt,
                                    before_balance=prev_b,
                                    after_balance=before_bal,
                                    reference_id=w_id,
                                    details=f"Partially cancelled pending withdrawal {w_id} (-{refund_amt:.2f}৳, remaining {rem_wd_amt:.2f}৳) to cover {tx_type}",
                                    admin_id=admin_id,
                                    now_str=now_str
                                )
                                auto_cancelled_wds.append({"wd_id": w_id, "amount": refund_amt, "mode": "partial"})
                                _record_audit_log(
                                    conn, admin_id or "SYSTEM", uid, "Withdraw Partial Cancel",
                                    f"WD {w_id} reduced by {refund_amt:.2f} BDT for {tx_type}", now_str
                                )
                            else:
                                prev_b = before_bal
                                before_bal = round(before_bal + w_amt, 2)
                                held_bal = max(0.0, round(held_bal - w_amt, 2))

                                conn.execute(
                                    "UPDATE withdrawals SET status = 'cancelled', processed_at = ?, "
                                    "decision_reason = 'Auto-cancelled due to video rejection clawback' WHERE wd_id = ?",
                                    (now_str, w_id)
                                )
                                cancel_tx_id = f"TX_{int(time.time()*1000)}_{secrets.token_hex(4).upper()}"
                                _insert_ledger_row(
                                    conn=conn,
                                    tx_id=cancel_tx_id,
                                    idempotency_key=f"AUTO_CANCEL_WD:{w_id}:{tx_id}",
                                    user_id=uid,
                                    video_id=clean_sub_id,
                                    tx_type="Withdraw Cancelled",
                                    amount=w_amt,
                                    before_balance=prev_b,
                                    after_balance=before_bal,
                                    reference_id=w_id,
                                    details=f"Auto-cancelled pending withdrawal {w_id} to cover {tx_type}",
                                    admin_id=admin_id,
                                    now_str=now_str
                                )
                                auto_cancelled_wds.append({"wd_id": w_id, "amount": w_amt, "mode": "full"})
                                _record_audit_log(
                                    conn, admin_id or "SYSTEM", uid, "Withdraw Auto-Cancelled",
                                    f"WD {w_id} ({w_amt:.2f} BDT) cancelled & refunded to cover {tx_type}", now_str
                                )

                        conn.execute(
                            "UPDATE users SET balance = ?, held_balance = ? WHERE user_id = ?",
                            (before_bal, held_bal, uid)
                        )
                        if auto_cancelled_wds:
                            today_s = datetime.now().strftime("%Y-%m-%d")
                            u_wd_row = conn.execute("SELECT daily_wd_date, daily_wd_count, daily_wd_amount FROM users WHERE user_id = ?", (uid,)).fetchone()
                            if u_wd_row and str(u_wd_row["daily_wd_date"] or "") == today_s:
                                full_canc_cnt = sum(1 for item in auto_cancelled_wds if item.get("mode") == "full")
                                tot_canc_amt = sum(float(item.get("amount") or 0.0) for item in auto_cancelled_wds)
                                new_d_cnt = max(0, int(u_wd_row["daily_wd_count"] or 0) - full_canc_cnt)
                                new_d_amt = max(0.0, round(float(u_wd_row["daily_wd_amount"] or 0.0) - tot_canc_amt, 2))
                                conn.execute(
                                    "UPDATE users SET daily_wd_count = ?, daily_wd_amount = ? WHERE user_id = ?",
                                    (new_d_cnt, new_d_amt, uid)
                                )

                    deducted = round(min(before_bal, amt), 2)
                    remainder_debt_added = round(amt - deducted, 2)
                    after_bal = max(0.0, round(before_bal - deducted, 2))
                    new_debt = round(debt_bal + remainder_debt_added, 2)
                    new_earned = max(0.0, round(tot_earned - amt, 2))
                    signed_amt = -deducted

                    conn.execute(
                        "UPDATE users SET balance = ?, debt_balance = ?, total_earned = ? WHERE user_id = ?",
                        (after_bal, new_debt, new_earned, uid)
                    )
                    if remainder_debt_added > 0:
                        adj_id = f"ADJ_{int(time.time()*1000)}_{secrets.token_hex(3).upper()}"
                        conn.execute("""
                            INSERT INTO debt_adjustments (
                                adj_id, user_id, sub_id, total_clawback, deducted_from_balance, remaining_debt, reason, status, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
                        """, (adj_id, uid, clean_sub_id, amt, deducted, remainder_debt_added, details, now_str))
                        details = f"{details} | Deducted: {deducted:.2f}৳, Debt Recorded: {remainder_debt_added:.2f}৳"
                else:
                    raise ValueError(f"Unsupported transaction type: {tx_type}")

                _insert_ledger_row(
                    conn=conn,
                    tx_id=tx_id,
                    idempotency_key=clean_idem,
                    user_id=uid,
                    video_id=clean_sub_id,
                    tx_type=tx_type,
                    amount=signed_amt,
                    before_balance=before_bal,
                    after_balance=after_bal,
                    reference_id=ref_id,
                    details=details,
                    admin_id=admin_id,
                    now_str=now_str
                )
                _record_audit_log(
                    conn, admin_id or "SYSTEM", uid, tx_type,
                    f"TxID: {tx_id} | Video: {clean_sub_id or 'N/A'} | Amt: {signed_amt:.2f} | Bal: {before_bal:.2f} -> {after_bal:.2f}",
                    now_str
                )

                return {
                    "tx_id": tx_id,
                    "idempotency_key": clean_idem,
                    "user_id": uid,
                    "video_id": clean_sub_id,
                    "type": tx_type,
                    "transaction_type": tx_type,
                    "amount": signed_amt,
                    "before_balance": before_bal,
                    "previous_balance": before_bal,
                    "after_balance": after_bal,
                    "new_balance": after_bal,
                    "auto_cancelled_wds": auto_cancelled_wds,
                    "remainder_debt_added": remainder_debt_added,
                    "debt_paid_from_income": debt_paid_from_income,
                    "reference_id": ref_id,
                    "details": details,
                    "created_at": now_str,
                    "timestamp": now_str
                }
        except sqlite3.IntegrityError:
            if clean_idem:
                existing = conn.execute(
                    "SELECT * FROM ledger_transactions WHERE idempotency_key = ?",
                    (clean_idem,)
                ).fetchone()
                if existing:
                    return dict(existing)
            raise


def calculate_eligible_paid_views(
    current_views: int,
    min_initial_views: int = 1000,
    step_size: int = 200,
    max_payable_views: int = 5000000
) -> int:
    cur = int(current_views or 0)
    min_init = max(1, int(min_initial_views or 1000))
    step = max(1, int(step_size or 200))
    max_cap = int(max_payable_views if max_payable_views is not None else 5000000)

    if max_cap > 0 and cur > max_cap:
        cur = max_cap

    if cur < min_init:
        return 0
    extra_steps = (cur - min_init) // step
    return min_init + (extra_steps * step)


def calculate_cumulative_video_earnings(
    eligible_views: int,
    first_1000_views_payment: float = 15.0,
    every_200_views_payment: float = None,
    min_initial_views: int = 1000,
    step_size: int = 200
) -> float:
    elig = int(eligible_views or 0)
    min_init = max(1, int(min_initial_views or 1000))
    step = max(1, int(step_size or 200))
    if elig < min_init:
        return 0.0
    first_pay = float(first_1000_views_payment if first_1000_views_payment is not None else 15.0)
    step_pay = (
        float(every_200_views_payment)
        if every_200_views_payment is not None
        else round((first_pay / float(min_init)) * step, 4)
    )
    extra_steps = (elig - min_init) // step
    return round(first_pay + (extra_steps * step_pay), 2)


def verify_video_finance_eligibility(
    conn: sqlite3.Connection,
    v_row,
    now_ts: float = None,
    is_initial_bot_approval: bool = False,
    require_organic: bool = True
) -> tuple:
    """
    Centralized transactional financial eligibility gate (P0-02, P0-07, P0-10):
    Blocks credit for rejected, trashed, permanently locked, suspicious, code-missing,
    unverified-organic, or deadline-expired videos.
    """
    if not v_row:
        return False, "video_not_found"
    check_ts = float(now_ts if now_ts is not None else time.time())
    keys = v_row.keys() if hasattr(v_row, "keys") else ()
    if int(v_row["is_trashed"] or 0) == 1 if "is_trashed" in keys else False:
        return False, "video_trashed"
    if int(v_row["permanent_approved"] or 0) == 1 if "permanent_approved" in keys else False:
        return False, "permanent_approved_locked"
    if (
        str(v_row["admin_status"] or "") == "rejected"
        or str(v_row["bot_status"] or "") == "rejected"
        or str(v_row["status"] or "") == "rejected"
    ):
        return False, "video_rejected"
    if "flagged_suspicious" in keys and int(v_row["flagged_suspicious"] or 0) == 1:
        return False, "flagged_suspicious"
    if "code_missing_flag" in keys and int(v_row["code_missing_flag"] or 0) == 1:
        return False, "code_missing_flag"

    already_approved = bool(
        str(v_row["admin_status"] or "") == "approved"
        or str(v_row["bot_status"] or "") == "approved"
        or ("initial_reward_paid" in keys and int(v_row["initial_reward_paid"] or 0) == 1)
        or ("paid_views" in keys and int(v_row["paid_views"] or 0) > 0)
    )
    if is_initial_bot_approval and not already_approved:
        qual_dl = float(v_row["qualification_deadline_ts"] or 0.0) if "qualification_deadline_ts" in keys else 0.0
        if qual_dl > 0 and check_ts > qual_dl:
            return False, "qualification_deadline_expired"

    if "verification_mode" in keys and str(v_row["verification_mode"] or "").strip().upper() == "SOURCE_CONFLICT":
        if str(v_row["admin_status"] or "") != "approved":
            return False, "source_conflict_unresolved"

    if require_organic and str(v_row["admin_status"] or "") != "approved":
        org_st = str(v_row["organic_status"] or "").strip().lower() if "organic_status" in keys else ""
        if org_st in ("suspicious_zero_engagement", "suspicious_low_engagement", "suspicious_bot_pattern", "suspicious_velocity_spike", "suspicious_traffic_source"):
            return False, "non_organic_suspicious"
        if is_initial_bot_approval and not already_approved:
            sub_id_s = str(v_row["sub_id"]) if "sub_id" in keys else ""
            snap_cnt = 0
            if sub_id_s:
                try:
                    snap_cnt = int(conn.execute("SELECT COUNT(*) as c FROM video_view_snapshots WHERE sub_id = ?", (sub_id_s,)).fetchone()["c"] or 0)
                except Exception:
                    snap_cnt = 0
            if org_st == "admin_override":
                has_override_audit = False
                if sub_id_s:
                    try:
                        aud_r = conn.execute(
                            "SELECT 1 FROM audit_logs WHERE (action LIKE '%Manual Bot Credit%' OR action LIKE '%Bot Credit Override%') AND details LIKE ? LIMIT 1",
                            (f"%{sub_id_s}%",)
                        ).fetchone()
                        has_override_audit = bool(aud_r)
                    except Exception:
                        has_override_audit = False
                if not has_override_audit and snap_cnt < 2:
                    return False, "unverified_admin_override"
            elif org_st == "verified_organic":
                if snap_cnt < 2:
                    return False, "pending_multi_snapshot_organic_proof"
            elif org_st == "pending_snapshots":
                return False, "pending_multi_snapshot_organic_proof"
            else:
                return False, "organic_not_verified"
    return True, "ok"


def transition_expired_pending_video(
    conn: sqlite3.Connection,
    sub_id: str,
    reason: str = "",
    expiry_action: str = None,
    now_ts: float = None
) -> dict:
    """
    Handles pending videos that did not reach `min_initial_views` before `qualification_deadline_ts` (P0-07 & P1-11).
    Supports both configurable outcomes with STRICT 0 BDT payout:
    - 'permanent_approve_zero_pay' / 'permanent_approved' (Requirement B default: moves to permanent_approved with 0 BDT, stops view counting)
    - 'reject' / 'rejected' (Requirement A option: moves to rejected with 0 BDT)
    """
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            check_ts = float(now_ts if now_ts is not None else time.time())
            now_str = datetime.fromtimestamp(check_ts).strftime("%Y-%m-%d %H:%M:%S")
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                return {"ok": False, "reason": "not_found", "credited_amount": 0.0}
            eff_action = str(expiry_action or "").strip().lower()
            if not eff_action:
                row_s = conn.execute("SELECT value FROM settings WHERE key = 'pending_expiry_action' LIMIT 1").fetchone()
                eff_action = str(row_s["value"] if row_s and row_s["value"] else "permanent_approve_zero_pay").strip().lower()
            if eff_action not in ("permanent_approve_zero_pay", "permanent_approved", "reject", "rejected"):
                raise ValueError(f"Invalid pending_expiry_action: {eff_action}")
            v_keys = v.keys() if hasattr(v, "keys") else ()
            if eff_action in ("permanent_approve_zero_pay", "permanent_approved"):
                if (
                    str(v["bot_status"] or "") == "manual_review"
                    or str(v["status"] or "") == "manual_review"
                    or ("flagged_suspicious" in v_keys and int(v["flagged_suspicious"] or 0) == 1)
                    or ("code_missing_flag" in v_keys and int(v["code_missing_flag"] or 0) == 1)
                ):
                    return {
                        "ok": False,
                        "outcome": "manual_review_held",
                        "reason": "manual_review_or_incomplete_verification",
                        "credited_amount": 0.0
                    }
            clean_reason = str(reason or "নির্ধারিত পেন্ডিং সময়সীমায় টার্গেট ভিউ পূরণ হয়নি (০ টাকা)।").strip()
            if eff_action in ("reject", "rejected"):
                conn.execute(
                    "UPDATE videos SET admin_status = 'rejected', bot_status = 'rejected', status = 'rejected', "
                    "permanent_approved = 0, credited_amount = 0.0, reward = 0.0, paid_views = 0, eligible_views = 0, "
                    "rejection_reason = ?, rejection_date = ?, last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                    (clean_reason, now_str, now_str, check_ts, str(sub_id))
                )
                _sync_video_counters(conn, str(v["user_id"]))
                return {"ok": True, "outcome": "rejected", "credited_amount": 0.0, "reason": clean_reason}
            else:
                conn.execute(
                    "UPDATE videos SET admin_status = 'approved', bot_status = 'expired_zero_pay', status = 'permanent_approved', "
                    "permanent_approved = 1, permanent_approved_at = ?, permanent_approved_by = 'AUTO_PENDING_EXPIRED_ZERO_PAY', "
                    "credited_amount = 0.0, reward = 0.0, paid_views = 0, eligible_views = 0, "
                    "risk_reason = ?, last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                    (now_str, clean_reason, now_str, check_ts, str(sub_id))
                )
                _sync_video_counters(conn, str(v["user_id"]))
                return {"ok": True, "outcome": "permanent_approved", "credited_amount": 0.0, "reason": clean_reason}


def process_idempotent_milestone_payout(
    conn: sqlite3.Connection,
    sub_id: str,
    user_id: str,
    current_views: int,
    previous_paid_views: int = None,
    rate_per_1k: float = None,
    min_initial_views: int = None,
    step_size: int = None,
    max_payable_views: int = None,
    every_200_views_payment: float = None,
    tx_type: str = "Video Milestone",
    now_ts: float = None
) -> tuple:
    with _finance_lock:
        if current_views is None or int(current_views) < 0:
            return 0.0, int(previous_paid_views or 0)

        with _atomic_immediate_tx(conn):
            cur_v = int(current_views)
            now_ts = float(now_ts if now_ts is not None else time.time())
            now_str = datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S")

            v_row = conn.execute(
                "SELECT * FROM videos WHERE sub_id = ? LIMIT 1",
                (str(sub_id),)
            ).fetchone()

            db_paid = int(v_row["paid_views"] or v_row["eligible_views"] or 0) if v_row else 0
            prev_paid = max(int(previous_paid_views or 0), db_paid)
            old_cur_v = int(v_row["current_views"] or 0) if v_row else prev_paid
            deducted_ext_v = int(v_row["deducted_external_views"] or 0) if v_row else 0

            if v_row:
                elig_ok, _elig_reason = verify_video_finance_eligibility(
                    conn, v_row, now_ts=now_ts, is_initial_bot_approval=(prev_paid == 0), require_organic=True
                )
                if not elig_ok:
                    return 0.0, prev_paid

            first_1k, every_200, db_min_init, db_step_sz = get_video_payment_rates(
                conn, sub_id=sub_id, explicit_first_1k=rate_per_1k, explicit_every_200=every_200_views_payment
            )
            eff_min_init = int(db_min_init if min_initial_views is None else min_initial_views)
            eff_step = int(db_step_sz if step_size is None else step_size)
            effective_cap = get_max_payable_views_setting(conn, max_payable_views, sub_id=sub_id)

            net_organic_views = max(0, cur_v - deducted_ext_v)
            eligible_views = calculate_eligible_paid_views(
                net_organic_views,
                min_initial_views=eff_min_init,
                step_size=eff_step,
                max_payable_views=effective_cap
            )

            end_ts = float(v_row["earning_end_ts"] or 0) if v_row else 0.0
            if not end_ts and v_row:
                pub_ts_w = float(v_row["publish_ts"] or 0) if ("publish_ts" in v_row.keys() and int(v_row["publish_date_known"] or 0) == 1) else 0.0
                if pub_ts_w <= 0 or pub_ts_w > now_ts + 86400 or pub_ts_w < now_ts - (365 * 86400):
                    pub_ts_w = 0.0
                base_st_ts = float(v_row["earning_start_ts"] or 0) or pub_ts_w or float(v_row["submitted_at_ts"] or 0)
                if base_st_ts > 0:
                    t_days = get_video_tracking_days(conn, sub_id=sub_id, platform=str(v_row["platform"] or ""))
                    end_ts = base_st_ts + (t_days * 86400)
            window_expired = bool(end_ts > 0 and now_ts > end_ts)
            if window_expired and prev_paid >= eff_min_init:
                conn.execute(
                    "UPDATE videos SET previous_views = ?, current_views = ?, admin_status = 'approved', permanent_approved = 1, "
                    "status = 'permanent_approved', "
                    "permanent_approved_at = CASE WHEN permanent_approved_at = '' OR permanent_approved_at IS NULL THEN ? ELSE permanent_approved_at END, "
                    "permanent_approved_by = CASE WHEN permanent_approved_by = '' OR permanent_approved_by IS NULL THEN 'AUTO_WINDOW_COMPLETE' ELSE permanent_approved_by END, "
                    "last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                    (old_cur_v, cur_v, now_str, now_str, now_ts, str(sub_id))
                )
                return 0.0, prev_paid
            reached_max_cap = bool(effective_cap > 0 and net_organic_views >= effective_cap and eligible_views >= eff_min_init)
            should_perm_lock = bool(reached_max_cap or (end_ts > 0 and now_ts >= end_ts and eligible_views >= eff_min_init))
            perm_by_reason = "AUTO_MAX_CAP_REACHED" if reached_max_cap else ("AUTO_WINDOW_COMPLETE" if should_perm_lock else "")

            if eligible_views <= prev_paid:
                if should_perm_lock:
                    conn.execute(
                        "UPDATE videos SET previous_views = ?, current_views = ?, admin_status = 'approved', permanent_approved = 1, "
                        "status = 'permanent_approved', "
                        "permanent_approved_at = CASE WHEN permanent_approved_at = '' OR permanent_approved_at IS NULL THEN ? ELSE permanent_approved_at END, "
                        "permanent_approved_by = CASE WHEN permanent_approved_by = '' OR permanent_approved_by IS NULL THEN ? ELSE permanent_approved_by END, "
                        "last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                        (old_cur_v, cur_v, now_str, perm_by_reason, now_str, now_ts, str(sub_id))
                    )
                else:
                    conn.execute(
                        "UPDATE videos SET previous_views = ?, current_views = ?, last_checked_at = ?, last_checked_ts = ? WHERE sub_id = ?",
                        (old_cur_v, cur_v, now_str, now_ts, str(sub_id))
                    )
                return 0.0, prev_paid

            if prev_paid < eff_min_init:
                extra_steps = (eligible_views - eff_min_init) // eff_step
                reward_delta = round(float(first_1k) + (extra_steps * float(every_200)), 2)
            else:
                delta_steps = (eligible_views - prev_paid) // eff_step
                reward_delta = round(delta_steps * float(every_200), 2)

            if reward_delta <= 0:
                return 0.0, prev_paid

            idem_key = f"MILESTONE:{sub_id}:{prev_paid}->{eligible_views}"
            existing = conn.execute(
                "SELECT tx_id FROM ledger_transactions WHERE idempotency_key = ?",
                (idem_key,)
            ).fetchone()
            if existing:
                return 0.0, eligible_views

            delta_views = eligible_views - prev_paid
            cap_note = f" (Capped at {effective_cap} max views)" if reached_max_cap else (" (Window completed -> Permanent Approve)" if window_expired else "")
            get_or_create_ledger_entry(
                conn,
                user_id=user_id,
                tx_type=tx_type,
                amount=reward_delta,
                details=f"Video {sub_id} views {prev_paid} -> {eligible_views} (+{delta_views} views){cap_note}",
                idempotency_key=idem_key,
                sub_id=sub_id,
                reference_id=f"{sub_id}:{eligible_views}"
            )
            conn.execute("""
                UPDATE videos
                SET previous_views = ?,
                    current_views = ?,
                    paid_views = ?,
                    eligible_views = ?,
                    initial_reward_paid = 1,
                    reward = ROUND(reward + ?, 2),
                    credited_amount = ROUND(credited_amount + ?, 2),
                    admin_status = CASE WHEN ? = 1 THEN 'approved' ELSE admin_status END,
                    status = CASE WHEN ? = 1 THEN 'permanent_approved' ELSE status END,
                    permanent_approved = CASE WHEN ? = 1 THEN 1 ELSE permanent_approved END,
                    permanent_approved_at = CASE WHEN ? = 1 AND (permanent_approved_at IS NULL OR permanent_approved_at = '') THEN ? ELSE permanent_approved_at END,
                    permanent_approved_by = CASE WHEN ? = 1 AND (permanent_approved_by IS NULL OR permanent_approved_by = '') THEN ? ELSE permanent_approved_by END,
                    last_checked_at = ?,
                    last_checked_ts = ?
                WHERE sub_id = ?
            """, (
                old_cur_v, cur_v, eligible_views, eligible_views, reward_delta, reward_delta,
                1 if should_perm_lock else 0,
                1 if should_perm_lock else 0,
                1 if should_perm_lock else 0,
                1 if should_perm_lock else 0, now_str,
                1 if should_perm_lock else 0, perm_by_reason,
                now_str, now_ts, str(sub_id)
            ))
            return reward_delta, eligible_views


def reset_external_link_video_earnings(
    conn: sqlite3.Connection,
    sub_id: str,
    admin_id: str = "ADMIN"
) -> dict:
    """
    Executes the `🔄 Reset` action on an External Link / Traffic Source video inside `BEGIN IMMEDIATE`:
    - Reverses any previously credited earnings on the video via the ledger (`External Link Reset`),
    - Resets external link flags and paid/credited counters so the video can be re-evaluated cleanly.
    """
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")
            uid = str(v["user_id"])
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            credited = round(float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0)), 2)
            paid_v = int(v["paid_views"] or v["eligible_views"] or 0)
            tx_res = None
            if credited > 0:
                rst_cnt = conn.execute(
                    "SELECT COUNT(*) as c FROM ledger_transactions WHERE video_id = ? AND type IN ('External Link Reset', 'External Link Clawback')",
                    (str(sub_id),)
                ).fetchone()["c"]
                idem_key = f"EXT_RESET:{sub_id}:CYCLE_{rst_cnt + 1}:PAID_{paid_v}:{credited:.2f}"
                tx_res = get_or_create_ledger_entry(
                    conn=conn,
                    user_id=uid,
                    tx_type="External Link Reset",
                    amount=credited,
                    details=f"Reset external link video {sub_id}",
                    idempotency_key=idem_key,
                    admin_id=admin_id,
                    sub_id=sub_id,
                    reference_id=str(sub_id)
                )

            conn.execute("""
                UPDATE videos
                SET bot_status = 'waiting_views',
                    admin_status = 'pending',
                    status = 'waiting_views',
                    permanent_approved = 0,
                    flagged_suspicious = 0,
                    deducted_external_views = COALESCE(current_views, 0),
                    paid_views = 0,
                    eligible_views = 0,
                    initial_reward_paid = 0,
                    credited_amount = 0.0,
                    reward = 0.0,
                    reversed_amount = ROUND(COALESCE(reversed_amount, 0.0) + ?, 2)
                WHERE sub_id = ?
            """, (credited, str(sub_id)))
            conn.execute("UPDATE video_external_links SET status = 'reset', admin_id = ?, decision_at = ? WHERE sub_id = ?", (str(admin_id), now_str, str(sub_id)))
            _sync_video_counters(conn, uid)
            _record_audit_log(
                conn, admin_id, uid, "Reset External Traffic Video",
                f"Reset video {sub_id}. Reversed credit: {credited:.2f} BDT", now_str
            )
            return {
                "ok": True,
                "sub_id": str(sub_id),
                "user_id": uid,
                "reversed_amount": credited,
                "auto_cancelled_wds": tx_res.get("auto_cancelled_wds", []) if tx_res else [],
                "remainder_debt_added": float(tx_res.get("remainder_debt_added", 0.0)) if tx_res else 0.0,
                "ledger_tx": tx_res
            }


def resolve_external_link_financial_action(
    conn: sqlite3.Connection,
    ext_id: str,
    decision: str,
    admin_id: str = "ADMIN",
    reject_full_video: bool = True
) -> dict:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            ext_row = conn.execute("SELECT * FROM video_external_links WHERE ext_id = ? LIMIT 1", (str(ext_id),)).fetchone()
            if not ext_row:
                raise ValueError(f"External link {ext_id} not found")

            sub_id = str(ext_row["sub_id"])
            uid = str(ext_row["user_id"])
            link_views = max(0, int(ext_row["views_count"] or 0))
            link_pct = round(float(ext_row["views_pct"] or 0.0), 2)
            src_url = str(ext_row["source_url"] or "")
            dom = str(ext_row["domain"] or src_url)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dec = str(decision or "approve").lower().strip()

            if dec == "reset":
                res_rst = reset_external_link_video_earnings(conn, sub_id=sub_id, admin_id=admin_id)
                res_rst["domain"] = dom
                res_rst["views_pct"] = link_pct
                res_rst["views_count"] = link_views
                res_rst["decision"] = "reset"
                return res_rst

            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (sub_id,)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")

            if dec == "approve":
                conn.execute(
                    "UPDATE video_external_links SET status = 'approved', admin_id = ?, decision_at = ? WHERE ext_id = ?",
                    (str(admin_id), now_str, str(ext_id))
                )
                rej_sum_row = conn.execute(
                    "SELECT COALESCE(SUM(views_count), 0) as s FROM video_external_links WHERE sub_id = ? AND status = 'rejected'",
                    (sub_id,)
                ).fetchone()
                new_deducted = max(0, int(rej_sum_row["s"] or 0))

                existing_cred = round(float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0)), 2)
                was_uncredited_review = bool(
                    v["bot_status"] in ("manual_review", "waiting_views", "pending")
                    and int(v["paid_views"] or 0) == 0
                    and existing_cred <= 0
                )
                conn.execute(
                    """
                    UPDATE videos
                    SET deducted_external_views = ?,
                        flagged_suspicious = 0,
                        bot_status = 'approved',
                        admin_status = 'approved',
                        status = CASE WHEN COALESCE(permanent_approved, 0) = 1 THEN 'permanent_approved'
                                      ELSE 'admin_approved' END,
                        approval_date = COALESCE(NULLIF(approval_date, ''), ?)
                    WHERE sub_id = ?
                    """,
                    (new_deducted, now_str, sub_id)
                )
                if was_uncredited_review:
                    _, _, min_init, _ = get_video_payment_rates(conn, sub_id=sub_id)
                    cur_v = int(v["current_views"] or 0)
                    if cur_v >= min_init:
                        process_bot_approval_credit(conn, sub_id=sub_id, user_id=uid, current_views=cur_v)

                v_after = conn.execute("SELECT credited_amount, reward FROM videos WHERE sub_id = ?", (sub_id,)).fetchone()
                final_credited = round(float((v_after["credited_amount"] or v_after["reward"] or 0.0) if v_after else existing_cred), 2)
                additional_credit = max(0.0, round(final_credited - existing_cred, 2))
                _sync_video_counters(conn, uid)
                _record_audit_log(
                    conn, admin_id, uid, "Approve External Traffic Link",
                    f"Approved external link {dom} ({link_pct}% / {link_views} views) on video {sub_id}; additional_credit={additional_credit:.2f} BDT", now_str
                )
                return {
                    "ok": True,
                    "ext_id": str(ext_id),
                    "sub_id": sub_id,
                    "user_id": uid,
                    "decision": "approved",
                    "domain": dom,
                    "source_url": src_url,
                    "views_pct": link_pct,
                    "views_count": link_views,
                    "reversed_amount": 0.0,
                    "additional_credit": additional_credit,
                    "credited_amount": final_credited,
                    "admin_status": "approved"
                }

            conn.execute(
                "UPDATE video_external_links SET status = 'rejected', admin_id = ?, decision_at = ? WHERE ext_id = ?",
                (str(admin_id), now_str, str(ext_id))
            )
            rej_sum_row = conn.execute(
                "SELECT COALESCE(SUM(views_count), 0) as s FROM video_external_links WHERE sub_id = ? AND status = 'rejected'",
                (sub_id,)
            ).fetchone()
            total_deducted_views = max(link_views, int(rej_sum_row["s"] or 0))
            cur_v = max(0, int(v["current_views"] or 0))
            rem_organic_views = max(0, cur_v - total_deducted_views)

            is_human_admin = str(admin_id or "").strip().upper() not in ("BOT_AUTO", "BOT_ANTI_FRAUD", "SYSTEM", "SYSTEM_MONITOR", "SYSTEM_WATCHDOG")
            if reject_full_video and dec != "deduct_link_only":
                conn.execute("UPDATE videos SET deducted_external_views = ? WHERE sub_id = ?", (total_deducted_views, sub_id))
                rej_reason = f"অর্গানিক ভিউ না — এক্সটার্নাল প্ল্যাটফর্ম/লিংক ({dom} — {link_pct}% / {link_views} ভিউ) থেকে ফেক/উল্টাপাল্টা ভিউ আসায় ভিডিওটি রিজেক্ট করা হয়েছে।"
                rej_res = admin_reject_video_with_reversal(
                    conn=conn,
                    sub_id=sub_id,
                    rejection_reason=rej_reason,
                    admin_id=admin_id,
                    force_admin_clawback=is_human_admin
                )
                if rej_res.get("permanent_protected"):
                    return {
                        "ok": False,
                        "permanent_protected": True,
                        "ext_id": str(ext_id),
                        "sub_id": sub_id,
                        "user_id": uid,
                        "decision": "protected",
                        "domain": dom,
                        "source_url": src_url,
                        "views_pct": link_pct,
                        "views_count": link_views,
                        "remaining_organic_views": rem_organic_views,
                        "video_fully_rejected": False,
                        "reversed_amount": 0.0,
                        "auto_cancelled_wds": [],
                        "remainder_debt_added": 0.0,
                        "new_credited_amount": float(v["credited_amount"] or v["reward"] or 0.0),
                        "ledger_tx": None
                    }
                return {
                    "ok": True,
                    "ext_id": str(ext_id),
                    "sub_id": sub_id,
                    "user_id": uid,
                    "decision": "rejected",
                    "domain": dom,
                    "source_url": src_url,
                    "views_pct": link_pct,
                    "views_count": link_views,
                    "remaining_organic_views": rem_organic_views,
                    "video_fully_rejected": True,
                    "reversed_amount": float(rej_res.get("reversed_amount", 0.0)),
                    "auto_cancelled_wds": rej_res.get("auto_cancelled_wds", []),
                    "remainder_debt_added": float(rej_res.get("remainder_debt_added", 0.0)),
                    "new_credited_amount": 0.0,
                    "ledger_tx": rej_res.get("ledger_tx")
                }

            first_1k, every_200, min_init, step_sz = get_video_payment_rates(conn, sub_id=sub_id)
            eff_cap = get_max_payable_views_setting(conn, sub_id=sub_id)
            new_elig_views = calculate_eligible_paid_views(rem_organic_views, min_init, step_sz, eff_cap)
            allowed_earnings = calculate_cumulative_video_earnings(new_elig_views, first_1k, every_200, min_init, step_sz)

            cur_credited = round(float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0)), 2)
            clawback_amt = max(0.0, round(cur_credited - allowed_earnings, 2))
            tx_res = None

            if clawback_amt > 0:
                idem_key = f"EXT_REJ:{ext_id}:{total_deducted_views}:{clawback_amt:.2f}"
                tx_res = get_or_create_ledger_entry(
                    conn=conn,
                    user_id=uid,
                    tx_type="External Link Clawback",
                    amount=clawback_amt,
                    details=f"Rejected external link {dom} (-{link_views} views / {link_pct}%) on video {sub_id}",
                    idempotency_key=idem_key,
                    admin_id=admin_id,
                    sub_id=sub_id,
                    reference_id=str(ext_id)
                )

            new_credited = max(0.0, round(cur_credited - clawback_amt, 2))
            new_reversed = round(float(v["reversed_amount"] or 0.0) + clawback_amt, 2)
            video_fully_rejected = (rem_organic_views < min_init)

            if video_fully_rejected:
                rej_reason = f"এক্সটার্নাল লিংক ({dom} — {link_pct}% / {link_views} ভিউ) রিজেক্ট করার পর অর্গানিক ভিউ ({rem_organic_views}) ন্যূনতম সীমার ({min_init}) নিচে নেমে গেছে।"
                conn.execute("""
                    UPDATE videos
                    SET deducted_external_views = ?,
                        paid_views = ?,
                        eligible_views = ?,
                        credited_amount = ?,
                        reward = ?,
                        reversed_amount = ?,
                        admin_status = 'rejected',
                        status = 'rejected',
                        rejection_reason = ?,
                        rejection_date = ?
                    WHERE sub_id = ?
                """, (total_deducted_views, new_elig_views, new_elig_views, new_credited, new_credited, new_reversed, rej_reason, now_str, sub_id))
            else:
                conn.execute("""
                    UPDATE videos
                    SET deducted_external_views = ?,
                        paid_views = ?,
                        eligible_views = ?,
                        credited_amount = ?,
                        reward = ?,
                        reversed_amount = ?
                    WHERE sub_id = ?
                """, (total_deducted_views, new_elig_views, new_elig_views, new_credited, new_credited, new_reversed, sub_id))

            _sync_video_counters(conn, uid)
            _record_audit_log(
                conn, admin_id, uid, "Reject External Traffic Link",
                f"Rejected external link {dom} (-{link_views} views / {link_pct}%) on video {sub_id}. Reversed: {clawback_amt:.2f} BDT",
                now_str
            )
            return {
                "ok": True,
                "ext_id": str(ext_id),
                "sub_id": sub_id,
                "user_id": uid,
                "decision": "rejected",
                "domain": dom,
                "source_url": src_url,
                "views_pct": link_pct,
                "views_count": link_views,
                "remaining_organic_views": rem_organic_views,
                "video_fully_rejected": video_fully_rejected,
                "reversed_amount": clawback_amt,
                "auto_cancelled_wds": tx_res.get("auto_cancelled_wds", []) if tx_res else [],
                "remainder_debt_added": float(tx_res.get("remainder_debt_added", 0.0)) if tx_res else 0.0,
                "new_credited_amount": new_credited,
                "ledger_tx": tx_res
            }


def process_bot_approval_credit(
    conn: sqlite3.Connection,
    sub_id: str,
    user_id: str,
    current_views: int,
    rate_per_1k: float = None,
    every_200_views_payment: float = None,
    min_initial_views: int = None,
    step_size: int = None,
    now_ts: float = None
) -> tuple:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            now_ts = float(now_ts if now_ts is not None else time.time())
            now_str = datetime.fromtimestamp(now_ts).strftime("%Y-%m-%d %H:%M:%S")
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")

            if v["admin_status"] == "rejected" or v["bot_status"] == "rejected" or v["status"] == "rejected":
                raise ValueError("রিজেক্টেড ভিডিওতে বট ক্রেডিট দেওয়া যাবে না।")
            if int(v["flagged_suspicious"] or 0):
                raise ValueError("সন্দেহজনক ফেক ভিউ ভিডিও ম্যানুয়াল রিভিউ ছাড়া বট ক্রেডিট পাবে না।")
            elig_ok, elig_reason = verify_video_finance_eligibility(
                conn, v, now_ts=now_ts, is_initial_bot_approval=True, require_organic=True
            )
            if not elig_ok:
                return 0.0, int(v["paid_views"] or 0)
            min_required = min_initial_views if min_initial_views is not None else get_video_payment_rates(conn, sub_id=sub_id)[2]
            ded_ext = int(v["deducted_external_views"] or 0) if "deducted_external_views" in v.keys() else 0
            if max(0, int(current_views or 0) - ded_ext) < int(min_required):
                raise ValueError(f"Bot approval credit-এর আগে কমপক্ষে {min_required} ভিউ দরকার।")

            track_days = get_video_tracking_days(conn, sub_id=sub_id)
            pub_ts_v = float(v["publish_ts"] or 0) if ("publish_ts" in v.keys() and int(v["publish_date_known"] or 0) == 1) else 0.0
            if pub_ts_v <= 0 or pub_ts_v > now_ts + 86400 or pub_ts_v < now_ts - (365 * 86400):
                pub_ts_v = 0.0
            start_ts = float(v["earning_start_ts"] or 0) or pub_ts_v or float(v["submitted_at_ts"] or 0) or now_ts
            start_str = v["earning_start_date"] or (datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S") if pub_ts_v else (v["submitted_at"] or now_str))
            end_ts = float(v["earning_end_ts"] or 0) or (start_ts + (int(track_days) * 86400))
            end_str = v["earning_end_date"] or datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")

            prev_paid = int(v["paid_views"] or 0)
            conn.execute("""
                UPDATE videos
                SET bot_status = 'approved',
                    admin_status = CASE WHEN admin_status = 'approved' THEN 'approved' ELSE 'pending' END,
                    status = CASE WHEN COALESCE(permanent_approved, 0) = 1 THEN 'permanent_approved'
                                  WHEN admin_status = 'approved' THEN 'admin_approved'
                                  ELSE 'bot_approved' END,
                    approval_date = COALESCE(NULLIF(approval_date, ''), ?),
                    approved_at_ts = CASE WHEN approved_at_ts > 0 THEN approved_at_ts ELSE ? END,
                    earning_start_date = ?,
                    earning_start_ts = ?,
                    earning_end_date = ?,
                    earning_end_ts = ?,
                    last_checked_at = ?,
                    last_checked_ts = ?
                WHERE sub_id = ?
            """, (now_str, now_ts, start_str, start_ts, end_str, end_ts, now_str, now_ts, str(sub_id)))

            credited_amt, elig_views = process_idempotent_milestone_payout(
                conn=conn,
                sub_id=sub_id,
                user_id=user_id,
                current_views=current_views,
                previous_paid_views=prev_paid,
                rate_per_1k=rate_per_1k,
                min_initial_views=min_initial_views,
                step_size=step_size,
                every_200_views_payment=every_200_views_payment,
                tx_type="Video Milestone",
                now_ts=now_ts
            )
            _sync_video_counters(conn, user_id)
            return credited_amt, elig_views


def admin_accept_bot_approved_video(
    conn: sqlite3.Connection,
    sub_id: str,
    admin_id: str = "ADMIN",
    earning_duration_days: int = None,
    permanent: bool = False
) -> dict:
    """
    Moves a video from BOT APPROVE to ADMIN APPROVE (or PERMANENT APPROVE when `permanent=True`).
    Strictly guarantees ZERO duplicate credit or bonus when Admin approves a Bot-Approved video.
    """
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")

            if v["admin_status"] == "rejected" or v["status"] == "rejected":
                res = admin_reaccept_rejected_video(conn, sub_id, admin_id=admin_id, earning_duration_days=earning_duration_days)
                if permanent:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute(
                        "UPDATE videos SET status = 'permanent_approved', permanent_approved = 1, permanent_approved_at = ?, permanent_approved_by = ? WHERE sub_id = ?",
                        (now_str, str(admin_id), str(sub_id))
                    )
                    res["permanent_approved"] = 1
                    res["status"] = "permanent_approved"
                return res

            _, _, min_init, _ = get_video_payment_rates(conn, sub_id=sub_id)
            cur_v = int(v["current_views"] or 0)
            paid_v = int(v["paid_views"] or v["eligible_views"] or 0)
            existing_cred = round(float(v["credited_amount"] or v["reward"] or 0.0), 2)
            if v["bot_status"] in ("pending", "waiting_views", "manual_review") and cur_v < min_init and paid_v < min_init:
                raise ValueError(f"টার্গেট ভিউ ({min_init} ভিউ) পূরণ না হওয়া পেন্ডিং ভিডিও অ্যাপ্রুভ বা পার্মানেন্ট অ্যাপ্রুভ করা যাবে না।")

            now_ts = time.time()
            now_dt = datetime.now()
            now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

            eff_days = get_video_tracking_days(conn, sub_id=sub_id, explicit_days=earning_duration_days)
            pub_ts_v = float(v["publish_ts"] or 0) if ("publish_ts" in v.keys() and int(v["publish_date_known"] or 0) == 1) else 0.0
            if pub_ts_v <= 0 or pub_ts_v > now_ts + 86400 or pub_ts_v < now_ts - (365 * 86400):
                pub_ts_v = 0.0
            start_ts = float(v["earning_start_ts"] or 0) or pub_ts_v or float(v["submitted_at_ts"] or 0) or now_ts
            start_str = v["earning_start_date"] or (datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S") if pub_ts_v else (v["submitted_at"] or now_str))
            end_ts = float(v["earning_end_ts"] or 0) or (start_ts + (int(eff_days) * 86400))
            end_str = v["earning_end_date"] or datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")

            was_already_bot_or_admin_approved = bool(
                v["bot_status"] == "approved"
                or v["admin_status"] == "approved"
                or int(v["initial_reward_paid"] or 0) == 1
                or paid_v > 0
                or existing_cred > 0
            )

            if (permanent or not was_already_bot_or_admin_approved) and cur_v >= min_init and int(v["permanent_approved"] or 0) == 0:
                process_idempotent_milestone_payout(
                    conn=conn,
                    sub_id=sub_id,
                    user_id=str(v["user_id"]),
                    current_views=cur_v,
                    previous_paid_views=paid_v,
                    tx_type="Video Milestone"
                )

            perm_val = 1 if (permanent or int(v["permanent_approved"] or 0) == 1) else 0
            perm_at = now_str if perm_val else ""
            perm_by = str(admin_id) if perm_val else ""
            new_status = "permanent_approved" if perm_val else "admin_approved"

            conn.execute("""
                UPDATE videos
                SET bot_status = 'approved',
                    admin_status = 'approved',
                    status = ?,
                    permanent_approved = ?,
                    permanent_approved_at = CASE WHEN ? = 1 AND (permanent_approved_at IS NULL OR permanent_approved_at = '') THEN ? ELSE permanent_approved_at END,
                    permanent_approved_by = CASE WHEN ? = 1 AND (permanent_approved_by IS NULL OR permanent_approved_by = '') THEN ? ELSE permanent_approved_by END,
                    flagged_suspicious = 0,
                    code_missing_flag = 0,
                    approval_date = COALESCE(NULLIF(approval_date, ''), ?),
                    approved_at_ts = CASE WHEN approved_at_ts > 0 THEN approved_at_ts ELSE ? END,
                    earning_start_date = ?,
                    earning_start_ts = ?,
                    earning_end_date = ?,
                    earning_end_ts = ?
                WHERE sub_id = ?
            """, (new_status, perm_val, perm_val, perm_at, perm_val, perm_by, now_str, now_ts, start_str, start_ts, end_str, end_ts, str(sub_id)))

            _sync_video_counters(conn, str(v["user_id"]))

            v_after = conn.execute("SELECT credited_amount, reward, permanent_approved, status FROM videos WHERE sub_id = ?", (str(sub_id),)).fetchone()
            final_credited = round(float((v_after["credited_amount"] or v_after["reward"] or 0.0) if v_after else 0.0), 2)
            additional_credit = max(0.0, round(final_credited - existing_cred, 2))
            action_title = "Permanent Approve Video" if perm_val else "Admin Approve Video (Zero Extra Credit)"
            _record_audit_log(
                conn, admin_id, str(v["user_id"]),
                action_title,
                f"Video {sub_id} approved (permanent={perm_val}). Existing credit: {existing_cred:.2f} BDT ({additional_credit:.2f} extra added)",
                now_str
            )

            return {
                "sub_id": str(sub_id),
                "user_id": str(v["user_id"]),
                "bot_status": "approved",
                "admin_status": "approved",
                "status": str(v_after["status"] if v_after else new_status),
                "permanent_approved": int(v_after["permanent_approved"] if v_after else perm_val),
                "additional_credit": additional_credit,
                "credited_amount": final_credited,
                "earning_start_date": start_str,
                "earning_end_date": end_str
            }


def admin_permanent_approve_video(
    conn: sqlite3.Connection,
    sub_id: str,
    admin_id: str = "ADMIN",
    earning_duration_days: int = None
) -> dict:
    return admin_accept_bot_approved_video(
        conn=conn,
        sub_id=sub_id,
        admin_id=admin_id,
        earning_duration_days=earning_duration_days,
        permanent=True
    )


def admin_reject_video_with_reversal(
    conn: sqlite3.Connection,
    sub_id: str,
    rejection_reason: str = "Admin Rejected",
    admin_id: str = "ADMIN",
    allow_partial_wd_cancel: bool = False,
    force_admin_clawback: bool = False
) -> dict:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")

            uid = str(v["user_id"])
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reason_clean = str(rejection_reason or "Admin Rejected").strip()

            if int(v["permanent_approved"] or 0) == 1 and not force_admin_clawback:
                return {
                    "sub_id": str(sub_id),
                    "user_id": uid,
                    "permanent_protected": True,
                    "reversed_amount": 0.0,
                    "auto_cancelled_wds": [],
                    "remainder_debt_added": 0.0,
                    "rejection_reason": "Permanent Approved ভিডিওর ব্যালেন্স স্থায়ীভাবে লক করা রয়েছে; কোনো টাকা কাটা যাবে না।"
                }

            if v["admin_status"] == "rejected" or v["status"] == "rejected":
                conn.execute(
                    "UPDATE videos SET rejection_reason = ? WHERE sub_id = ?",
                    (reason_clean, str(sub_id))
                )
                return {
                    "sub_id": str(sub_id),
                    "user_id": uid,
                    "already_rejected": True,
                    "reversed_amount": float(v["reversed_amount"] or 0.0),
                    "auto_cancelled_wds": [],
                    "remainder_debt_added": 0.0,
                    "rejection_reason": reason_clean
                }

            credited = round(float(v["credited_amount"] if v["credited_amount"] is not None and float(v["credited_amount"]) > 0 else (v["reward"] or 0.0)), 2)
            cur = conn.execute("""
                UPDATE videos
                SET admin_status = 'rejected',
                    bot_status = 'rejected',
                    status = 'rejected',
                    permanent_approved = 0,
                    rejection_reason = ?,
                    rejection_date = ?,
                    reversed_amount = ROUND(COALESCE(reversed_amount, 0.0) + ?, 2),
                    credited_amount = 0.0,
                    reward = 0.0
                WHERE sub_id = ? AND admin_status != 'rejected' AND status != 'rejected'
            """, (reason_clean, now_str, credited, str(sub_id)))

            if cur.rowcount != 1:
                return {
                    "sub_id": str(sub_id),
                    "user_id": uid,
                    "already_rejected": True,
                    "reversed_amount": float(v["reversed_amount"] or 0.0),
                    "auto_cancelled_wds": [],
                    "remainder_debt_added": 0.0,
                    "rejection_reason": reason_clean
                }

            tx_res = None
            if credited > 0:
                rev_count = conn.execute(
                    "SELECT COUNT(*) as c FROM ledger_transactions WHERE video_id = ? AND type IN ('Video Clawback', 'Video Reversal')",
                    (str(sub_id),)
                ).fetchone()["c"]
                idem_key = f"REVERSAL:{sub_id}:CYCLE_{rev_count + 1}:{credited:.2f}"
                tx_res = get_or_create_ledger_entry(
                    conn=conn,
                    user_id=uid,
                    tx_type="Video Clawback",
                    amount=credited,
                    details=f"Rejected video {sub_id} ({reason_clean})",
                    idempotency_key=idem_key,
                    admin_id=admin_id,
                    sub_id=sub_id,
                    reference_id=sub_id,
                    allow_partial_wd_cancel=allow_partial_wd_cancel
                )

            _sync_video_counters(conn, uid)

            _record_audit_log(
                conn, admin_id, uid,
                "Admin Reject Video & Reversal",
                f"Video {sub_id} rejected. Reason: {reason_clean}. Reversed: {credited:.2f} BDT",
                now_str
            )

            return {
                "sub_id": str(sub_id),
                "user_id": uid,
                "bot_status": "rejected",
                "admin_status": "rejected",
                "status": "rejected",
                "reversed_amount": credited,
                "auto_cancelled_wds": tx_res.get("auto_cancelled_wds", []) if tx_res else [],
                "remainder_debt_added": float(tx_res.get("remainder_debt_added", 0.0)) if tx_res else 0.0,
                "rejection_reason": reason_clean,
                "rejection_date": now_str,
                "ledger_tx": tx_res
            }


def admin_reaccept_rejected_video(
    conn: sqlite3.Connection,
    sub_id: str,
    admin_id: str = "ADMIN",
    earning_duration_days: int = None
) -> dict:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            v = conn.execute("SELECT * FROM videos WHERE sub_id = ? LIMIT 1", (str(sub_id),)).fetchone()
            if not v:
                raise ValueError(f"Video {sub_id} not found")

            uid = str(v["user_id"])
            if v["admin_status"] == "approved" and v["status"] in ("admin_approved", "permanent_approved"):
                return {
                    "sub_id": str(sub_id),
                    "user_id": uid,
                    "already_approved": True,
                    "restored_amount": 0.0,
                    "credited_amount": float(v["credited_amount"] or v["reward"] or 0.0)
                }

            now_ts = time.time()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rev_amt = round(float(v["reversed_amount"] or 0.0), 2)
            paid_v = int(v["paid_views"] or v["eligible_views"] or 0)
            cur_v = int(v["current_views"] or 0)

            f_1k, ev_200, m_init, st_sz = get_video_payment_rates(conn, sub_id=sub_id)
            eff_cap = get_max_payable_views_setting(conn, sub_id=sub_id)

            if rev_amt <= 0:
                if paid_v > 0:
                    rev_amt = calculate_cumulative_video_earnings(paid_v, f_1k, ev_200, m_init, st_sz)
                elif cur_v >= m_init:
                    paid_v = calculate_eligible_paid_views(cur_v, m_init, st_sz, eff_cap)
                    rev_amt = calculate_cumulative_video_earnings(paid_v, f_1k, ev_200, m_init, st_sz)

            eff_days = get_video_tracking_days(conn, sub_id=sub_id, explicit_days=earning_duration_days)
            pub_ts_v = float(v["publish_ts"] or 0) if ("publish_ts" in v.keys() and int(v["publish_date_known"] or 0) == 1) else 0.0
            if pub_ts_v <= 0 or pub_ts_v > now_ts + 86400 or pub_ts_v < now_ts - (365 * 86400):
                pub_ts_v = 0.0
            start_ts = float(v["earning_start_ts"] or 0) or pub_ts_v or float(v["submitted_at_ts"] or 0) or now_ts
            start_str = v["earning_start_date"] or (datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S") if pub_ts_v else (v["submitted_at"] or now_str))
            end_ts = float(v["earning_end_ts"] or 0) or (start_ts + (int(eff_days) * 86400))
            end_str = v["earning_end_date"] or datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")

            if paid_v == 0 and rev_amt > 0:
                paid_v = calculate_eligible_paid_views(cur_v, m_init, st_sz, eff_cap)

            cur = conn.execute("""
                UPDATE videos
                SET bot_status = 'approved',
                    admin_status = 'approved',
                    status = 'admin_approved',
                    flagged_suspicious = 0,
                    deducted_external_views = 0,
                    initial_reward_paid = CASE WHEN ? > 0 THEN 1 ELSE initial_reward_paid END,
                    credited_amount = ?,
                    reward = ?,
                    reversed_amount = 0.0,
                    paid_views = ?,
                    eligible_views = ?,
                    approval_date = COALESCE(NULLIF(approval_date, ''), ?),
                    approved_at_ts = CASE WHEN approved_at_ts > 0 THEN approved_at_ts ELSE ? END,
                    earning_start_date = ?,
                    earning_start_ts = ?,
                    earning_end_date = ?,
                    earning_end_ts = ?
                WHERE sub_id = ? AND (admin_status = 'rejected' OR status = 'rejected' OR bot_status = 'rejected')
            """, (rev_amt, rev_amt, rev_amt, paid_v, paid_v, now_str, now_ts, start_str, start_ts, end_str, end_ts, str(sub_id)))

            if cur.rowcount != 1:
                return {
                    "sub_id": str(sub_id),
                    "user_id": uid,
                    "already_approved": True,
                    "restored_amount": 0.0,
                    "credited_amount": float(v["credited_amount"] or v["reward"] or 0.0)
                }

            tx_res = None
            if rev_amt > 0:
                restore_count = conn.execute(
                    "SELECT COUNT(*) as c FROM ledger_transactions WHERE video_id = ? AND type IN ('Video Reversal Restore', 'Earnings Restoration')",
                    (str(sub_id),)
                ).fetchone()["c"]
                idem_key = f"RESTORE:{sub_id}:CYCLE_{restore_count + 1}:{rev_amt:.2f}"
                tx_res = get_or_create_ledger_entry(
                    conn=conn,
                    user_id=uid,
                    tx_type="Video Reversal Restore",
                    amount=rev_amt,
                    details=f"Re-accepted rejected video {sub_id} (Restored {rev_amt:.2f}৳)",
                    idempotency_key=idem_key,
                    admin_id=admin_id,
                    sub_id=sub_id,
                    reference_id=sub_id
                )

            conn.execute("UPDATE video_external_links SET status = 'approved' WHERE sub_id = ? AND status IN ('rejected', 'reset')", (str(sub_id),))
            _sync_video_counters(conn, uid)

            _record_audit_log(
                conn, admin_id, uid,
                "Admin Re-Accept Rejected Video",
                f"Video {sub_id} moved from REJECTED VIDEOS to ADMIN APPROVE. Restored: {rev_amt:.2f} BDT",
                now_str
            )

            return {
                "sub_id": str(sub_id),
                "user_id": uid,
                "bot_status": "approved",
                "admin_status": "approved",
                "status": "admin_approved",
                "restored_amount": rev_amt,
                "credited_amount": rev_amt,
                "paid_views": paid_v,
                "ledger_tx": tx_res
            }


def admin_mark_withdrawal_paid(
    conn: sqlite3.Connection,
    wd_id: str,
    admin_id: str = "ADMIN",
    trx_id: str = "",
    payment_note: str = ""
) -> dict:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            w = conn.execute("SELECT * FROM withdrawals WHERE wd_id = ? LIMIT 1", (str(wd_id),)).fetchone()
            if not w:
                raise ValueError(f"Withdrawal {wd_id} not found")
            if w["status"] != "pending":
                return {"wd_id": str(wd_id), "already_processed": True, "status": w["status"]}

            amt = round(float(w["amount"] or 0.0), 2)
            t_uid = str(w["user_id"])
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            clean_trx = "" if str(trx_id or "").strip().upper() == "SKIP" else str(trx_id or "").strip()
            clean_note = "" if str(payment_note or "").strip().upper() == "SKIP" else str(payment_note or "").strip()
            note_summary = f"TrxID: {clean_trx}" if clean_trx else (clean_note or "Paid")

            cur = conn.execute("""
                UPDATE withdrawals
                SET status = 'paid',
                    admin_id = ?,
                    trx_id = ?,
                    payment_note = ?,
                    decision_reason = ?,
                    processed_at = ?
                WHERE wd_id = ? AND status = 'pending'
            """, (str(admin_id), clean_trx, clean_note or note_summary, note_summary, now_str, str(wd_id)))
            if cur.rowcount != 1:
                return {"wd_id": str(wd_id), "already_processed": True, "status": "paid"}

            tx_res = get_or_create_ledger_entry(
                conn,
                t_uid,
                "Withdraw Paid",
                amt,
                details=f"Withdrawal {wd_id} paid ({note_summary})",
                admin_id=admin_id,
                reference_id=str(wd_id),
                idempotency_key=f"WD_PAID:{wd_id}"
            )

            return {
                "wd_id": str(wd_id),
                "user_id": t_uid,
                "amount": amt,
                "status": "paid",
                "trx_id": clean_trx,
                "payment_note": clean_note or note_summary,
                "ledger_tx": tx_res
            }


def admin_cancel_withdrawal_with_refund(
    conn: sqlite3.Connection,
    wd_id: str,
    admin_id: str = "ADMIN",
    reason: str = "Admin Cancelled",
    target_status: str = "cancelled"
) -> dict:
    with _finance_lock:
        with _atomic_immediate_tx(conn):
            w = conn.execute("SELECT * FROM withdrawals WHERE wd_id = ? LIMIT 1", (str(wd_id),)).fetchone()
            if not w:
                raise ValueError(f"Withdrawal {wd_id} not found")
            if w["status"] != "pending":
                return {"wd_id": str(wd_id), "already_processed": True, "status": w["status"], "refunded_amount": 0.0}

            amt = round(float(w["amount"] or 0.0), 2)
            t_uid = str(w["user_id"])
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            clean_reason = "" if str(reason or "").strip().upper() == "SKIP" else (str(reason or "Admin Cancelled").strip() or "Admin Cancelled")
            eff_st = "rejected" if str(target_status).lower() == "rejected" else "cancelled"

            cur = conn.execute("""
                UPDATE withdrawals
                SET status = ?,
                    admin_id = ?,
                    decision_reason = ?,
                    processed_at = ?
                WHERE wd_id = ? AND status = 'pending'
            """, (eff_st, str(admin_id), clean_reason, now_str, str(wd_id)))
            if cur.rowcount != 1:
                return {"wd_id": str(wd_id), "already_processed": True, "status": eff_st, "refunded_amount": 0.0}

            tx_res = get_or_create_ledger_entry(
                conn,
                t_uid,
                "Withdraw Cancelled",
                amt,
                details=f"Withdrawal {wd_id} {eff_st} ({clean_reason})",
                admin_id=admin_id,
                reference_id=str(wd_id),
                idempotency_key=f"WD_REFUND:{wd_id}"
            )
            today_s = datetime.now().strftime("%Y-%m-%d")
            u_wd_row = conn.execute("SELECT daily_wd_date, daily_wd_count, daily_wd_amount FROM users WHERE user_id = ?", (t_uid,)).fetchone()
            if u_wd_row and str(u_wd_row["daily_wd_date"] or "") == today_s:
                new_d_cnt = max(0, int(u_wd_row["daily_wd_count"] or 0) - 1)
                new_d_amt = max(0.0, round(float(u_wd_row["daily_wd_amount"] or 0.0) - amt, 2))
                conn.execute(
                    "UPDATE users SET daily_wd_count = ?, daily_wd_amount = ? WHERE user_id = ?",
                    (new_d_cnt, new_d_amt, t_uid)
                )

            return {
                "wd_id": str(wd_id),
                "user_id": t_uid,
                "amount": amt,
                "refunded_amount": amt,
                "status": eff_st,
                "reason": clean_reason,
                "ledger_tx": tx_res
            }