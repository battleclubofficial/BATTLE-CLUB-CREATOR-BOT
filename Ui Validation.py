# -*- coding: utf-8 -*-
"""
BATTLE CLUB TELEGRAM BOT - UI VALIDATION, FULL-WIDTH TEMPLATE, STYLING & CUSTOM EMOJI ENGINE (v8.0)
- Validates Telegram Inline Buttons, Callback Data (<= 64 UTF-8 bytes) & Custom Emoji Icons
- Full-Width Message Template Formatter (`ensure_full_width_message`) Fixing Right-Side Gap on Mobile Bubble Width
- Button Text Design Formatter (`apply_button_text_design` — Bold Sans, Bold Serif, Bracket, Star, Diamond)
- Multi-Page Dynamic Layout Resolver (`user_home`, `user_settings_hub`, `user_dashboard`, `user_profile`, `admin_home`, `admin_settings_hub`, `admin_general_settings`)
- Universal Inline Pagination (`⬅️ আগের পৃষ্ঠা` / `পরের পৃষ্ঠা ➡️`)
- UTF-16 Telegram Premium Custom Emoji Parser (`extract_rich_html_text`, `parse_telegram_html`)
"""

import os
import re
import sys
import html
import json
import importlib.util


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

try:
    import telebot
    from telebot import types
except ImportError:
    class _FallbackInlineKeyboardButton:
        def __init__(self, text, callback_data=None, url=None, **kwargs):
            self.text = str(text)
            self.callback_data = callback_data
            self.url = url
            self.extra = kwargs

        def to_dict(self):
            d = {"text": self.text}
            if self.callback_data is not None:
                d["callback_data"] = self.callback_data
            if self.url is not None:
                d["url"] = self.url
            d.update(self.extra)
            return d

    class _FallbackInlineKeyboardMarkup:
        def __init__(self, row_width=3):
            self.row_width = row_width
            self.keyboard = []

        def row(self, *args):
            if args:
                self.keyboard.append(list(args))
            return self

        def add(self, *args):
            if args:
                self.keyboard.append(list(args))
            return self

        def to_dict(self):
            return {"inline_keyboard": [[b.to_dict() for b in r] for r in self.keyboard]}

    class _FallbackKeyboardButton:
        def __init__(self, text, **kwargs):
            self.text = str(text)
            self.extra = kwargs

        def to_dict(self):
            return {"text": self.text, **self.extra}

    class _FallbackReplyKeyboardMarkup:
        def __init__(self, resize_keyboard=True, one_time_keyboard=False, **kwargs):
            self.resize_keyboard = resize_keyboard
            self.one_time_keyboard = one_time_keyboard
            self.keyboard = []

        def row(self, *args):
            if args:
                self.keyboard.append([a if hasattr(a, "text") else _FallbackKeyboardButton(str(a)) for a in args])
            return self

        def add(self, *args):
            return self.row(*args)

        def to_dict(self):
            return {
                "keyboard": [[b.to_dict() if hasattr(b, "to_dict") else {"text": str(b)} for b in r] for r in self.keyboard],
                "resize_keyboard": self.resize_keyboard,
                "one_time_keyboard": self.one_time_keyboard
            }

    class _FallbackReplyKeyboardRemove:
        def __init__(self, selective=False):
            self.selective = selective

        def to_dict(self):
            return {"remove_keyboard": True, "selective": self.selective}

    class _FallbackMessageEntity:
        def __init__(self, type, offset, length, url=None, language=None, custom_emoji_id=None):
            self.type = type
            self.offset = int(offset)
            self.length = int(length)
            self.url = url
            self.language = language
            self.custom_emoji_id = custom_emoji_id

        def to_dict(self):
            d = {"type": self.type, "offset": self.offset, "length": self.length}
            if self.url:
                d["url"] = self.url
            if self.language:
                d["language"] = self.language
            if self.custom_emoji_id:
                d["custom_emoji_id"] = self.custom_emoji_id
            return d

    class _FallbackTypes:
        InlineKeyboardButton = _FallbackInlineKeyboardButton
        InlineKeyboardMarkup = _FallbackInlineKeyboardMarkup
        KeyboardButton = _FallbackKeyboardButton
        ReplyKeyboardMarkup = _FallbackReplyKeyboardMarkup
        ReplyKeyboardRemove = _FallbackReplyKeyboardRemove
        MessageEntity = _FallbackMessageEntity

    types = _FallbackTypes()

try:
    if hasattr(types, "MessageEntity") and hasattr(types.MessageEntity, "de_json"):
        _orig_me_de_json = types.MessageEntity.de_json

        @classmethod
        def _patched_me_de_json(cls, json_string):
            ent = _orig_me_de_json(json_string)
            if ent is not None and not getattr(ent, "custom_emoji_id", None):
                try:
                    raw_d = json.loads(json_string) if isinstance(json_string, str) else json_string
                    if isinstance(raw_d, dict) and raw_d.get("custom_emoji_id"):
                        ent.custom_emoji_id = str(raw_d["custom_emoji_id"])
                except Exception:
                    pass
            return ent

        types.MessageEntity.de_json = _patched_me_de_json
except Exception:
    pass

from ui_catalog import (
    FULL_WIDTH_DIVIDER,
    ALLOWED_DYNAMIC_LAYOUT_KEYS,
    DEFAULT_LAYOUTS,
    MAIN_ADMIN_BUTTON_KEYS,
    SETTINGS_ONLY_BUTTON_KEYS,
    LAYOUT_SHORT_CODE_MAP,
    SHORT_CODE_LAYOUT_MAP
)


BUTTON_RUNTIME_CAPS = {
    "allow_style": True,
    "allow_custom_emoji": True
}

_BOLD_SANS_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
)

_BOLD_SERIF_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
)


_MONO_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝗠𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
)
_SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)



# BMP symbols and hearts that require U+FE0F Variation Selector-16 for color emoji presentation on Android/OriginOS
_HEART_VARIANTS_RE = re.compile(r"([\u2764\u2665\u2661\u2763\u2765])(?![\ufe0f\u200d])")
_BMP_EMOJI_SYMBOLS_RE = re.compile(
    r"([\u2600\u2601\u260e\u2611\u2614\u2615\u261d\u2620\u2622\u2623\u2626\u262a\u262e\u262f"
    r"\u2638\u2639\u263a\u2648-\u2653\u2660\u2663\u2665\u2666\u2668\u267b\u267f\u2692-\u2697"
    r"\u2699\u269b\u269c\u26a0\u26a1\u26b0\u26b1\u26bd\u26be\u26c4\u26c5\u26c8\u26ce\u26cf"
    r"\u26d1\u26d3\u26d4\u26e9\u26ea\u26f0-\u26f5\u26f7-\u26fa\u26fd\u2702\u2708\u2709\u270c"
    r"\u270d\u270f\u2712\u2714\u2716\u271d\u2721\u2733\u2734\u2744\u2747\u2757\u2763\u2764"
    r"\u27a1\u2934\u2935\u2b05-\u2b07\u25b6\u25c0\u2139\u3030\u303d\u3297\u3299])(?![\ufe0f\ufe0e\u200d\u20e3])"
)
_INVISIBLE_OR_BLANK_PLACEHOLDER_RE = re.compile(
    r"^[\s\u200b-\u200f\u202a-\u202e\u2060-\u206f\u2800\u3164\ufeff\ufffc\ufffd_\-\.\,\:\;\*\+\~\`\|\\\/]+$"
)


def ensure_visible_emoji_presentation(text: str) -> str:
    """
    Ensures all heart/love emojis (`❤`, `♥`, `♡`, `❣`, `❥`) and BMP symbols have explicit
    U+FE0F Variation Selector-16 (`❤️`) so they never become invisible or monochrome on colored
    Telegram buttons on Android / OriginOS / iOS.
    """
    if not text:
        return ""
    s = str(text)
    # Convert monochrome heart suits/outlines (♥, ♡, ❣, ❥, ❤) without FE0F/ZWJ into full-color red heart ❤️ (❤️)
    s = re.sub(r"[\u2665\u2661](?![\ufe0f\u200d])", "\u2764\ufe0f", s)
    s = _HEART_VARIANTS_RE.sub(lambda m: ("\u2764\ufe0f" if m.group(1) in ("\u2764", "\u2765") else m.group(1) + "\ufe0f"), s)
    s = _BMP_EMOJI_SYMBOLS_RE.sub(lambda m: m.group(1) + "\ufe0f", s)
    # Deduplicate any accidental double ️️
    s = re.sub(r"\ufe0f{2,}", "\ufe0f", s)
    return s


def _is_visible_emoji_or_symbol_chunk(chunk: str) -> bool:
    """Checks if a custom_emoji UTF-16 slice in message.text contains a visibly renderable emoji/character."""
    s = str(chunk or "").strip()
    if not s or _INVISIBLE_OR_BLANK_PLACEHOLDER_RE.match(s):
        return False
    for ch in s:
        cp = ord(ch)
        if cp >= 0x1F000 or (0x2100 <= cp <= 0x27BF) or (0x2B00 <= cp <= 0x2BFF) or cp in (0x203C, 0x2049, 0x3030, 0x303D, 0x3297, 0x3299):
            return True
    return False


_LEADING_EMOJI_PREFIX_RE = re.compile(
    r"^[\s\u200b-\u200f\ufe0e\ufe0f\u20e3"
    r"\u2190-\u21ff\u2300-\u27bf\u2b00-\u2bff\u3030\u303d\u3297\u3299"
    r"\U0001F000-\U0001FAFF]+"
)


def strip_leading_default_emojis(text: str) -> str:
    """
    Strips leading normal/default Unicode emojis and variation selectors from a button label
    (e.g. turning '📊 ড্যাশবোর্ড' into 'ড্যাশবোর্ড') while keeping all main text intact.
    If the string consists ONLY of emojis, returns the trimmed string unchanged.
    """
    s = str(text or "").strip()
    if not s:
        return ""
    stripped = _LEADING_EMOJI_PREFIX_RE.sub("", s).strip()
    return stripped if stripped else s


def extract_leading_default_emojis(text: str) -> str:
    """Extracts any leading default normal emoji prefix from `text` so it can be restored on demand."""
    s = str(text or "").strip()
    if not s:
        return ""
    m = _LEADING_EMOJI_PREFIX_RE.match(s)
    if m:
        return ensure_visible_emoji_presentation(m.group(0).strip())
    return ""


def supports_button_custom_emoji(button_type: str = "inline", has_url: bool = False) -> bool:
    """
    Checks whether a Telegram button type genuinely supports `icon_custom_emoji_id`.
    Never claims false Premium Emoji support when `BUTTON_RUNTIME_CAPS['allow_custom_emoji']` is disabled.
    """
    if not BUTTON_RUNTIME_CAPS.get("allow_custom_emoji", True):
        return False
    b_type = str(button_type or "inline").lower().strip()
    return b_type in ("inline", "reply", "callback", "url")


def normalize_button_label_and_extract_emoji(
    raw_text: str,
    entities: list = None,
    fallback_emoji_char: str = "",
    sticker_emoji: str = "",
    sticker_custom_emoji_id: str = "",
    keep_fallback_in_text: bool = False
) -> tuple:
    """
    Extracts `custom_emoji_id` and produces a clean button label WITHOUT forcing a default or fallback
    normal emoji back into the button text when a Premium Custom Emoji is set:
    - When `custom_emoji` entities or `<tg-emoji emoji-id="...">...</tg-emoji>` tags are present alongside
      text (e.g., `<tg-emoji emoji-id="5368324170671202286">📊</tg-emoji> ড্যাশবোর্ড`), extracts
      `5368324170671202286` as `icon_custom_emoji_id` and removes the custom emoji's placeholder character
      from `clean_lbl` so the old default/base emoji (`📊` or `❤️`) does NOT appear next to the custom emoji!
    - If the user sent ONLY a custom emoji or sticker with no text at all, `clean_lbl` returns `""`
      so the caller can preserve the existing stripped text label without injecting a fake normal emoji.
    - Returns `(clean_visible_label, extracted_custom_emoji_id)`.
    """
    txt = str(raw_text or "")
    extracted_id = str(sticker_custom_emoji_id or "").strip()
    eff_fallback = ensure_visible_emoji_presentation(str(fallback_emoji_char or sticker_emoji or "").strip())

    # Check inline <tg-emoji emoji-id="..."> tags if present in raw_text
    if not extracted_id:
        m_tg = re.search(r"emoji-id=[\x22\x27]?([0-9]{10,25})[\x22\x27]?", txt)
        if m_tg:
            extracted_id = m_tg.group(1)

    ent_list = list(entities or [])
    ce_spans = []
    for ent in ent_list:
        etype = ent.get("type", "") if isinstance(ent, dict) else getattr(ent, "type", "")
        c_id = ent.get("custom_emoji_id", "") if isinstance(ent, dict) else getattr(ent, "custom_emoji_id", "")
        if not c_id and hasattr(ent, "__dict__"):
            c_id = ent.__dict__.get("custom_emoji_id", "")
        if etype == "custom_emoji" and c_id:
            c_id_s = str(c_id).strip()
            if not extracted_id:
                extracted_id = c_id_s
            off = int(ent.get("offset", 0) if isinstance(ent, dict) else getattr(ent, "offset", 0))
            ln = int(ent.get("length", 0) if isinstance(ent, dict) else getattr(ent, "length", 0))
            if ln > 0:
                ce_spans.append((off, off + ln, c_id_s))

    if txt and ce_spans:
        utf16_bytes = txt.encode("utf-16-le")
        total_u = len(utf16_bytes) // 2
        ce_spans.sort(key=lambda x: x[0])
        rebuilt = []
        last_u = 0
        for s_u, e_u, _cid in ce_spans:
            s_u = max(0, min(total_u, s_u))
            e_u = max(0, min(total_u, e_u))
            if e_u <= s_u or s_u < last_u:
                continue
            if s_u > last_u:
                rebuilt.append(utf16_bytes[last_u * 2:s_u * 2].decode("utf-16-le", errors="ignore"))
            if keep_fallback_in_text:
                slice_str = utf16_bytes[s_u * 2:e_u * 2].decode("utf-16-le", errors="ignore")
                norm_slice = ensure_visible_emoji_presentation(slice_str)
                if not _is_visible_emoji_or_symbol_chunk(norm_slice):
                    norm_slice = eff_fallback
                rebuilt.append(norm_slice)
            last_u = e_u
        if last_u < total_u:
            rebuilt.append(utf16_bytes[last_u * 2:].decode("utf-16-le", errors="ignore"))
        txt = "".join(rebuilt)

    def _replace_tg_emoji_tag(m):
        if not keep_fallback_in_text:
            return ""
        inner = ensure_visible_emoji_presentation(m.group(2) or "")
        if not _is_visible_emoji_or_symbol_chunk(inner):
            inner = eff_fallback
        return inner

    txt = re.sub(
        r"<tg-emoji\s+emoji-id=[\x22\x27]([0-9]+)[\x22\x27]>(.*?)</tg-emoji>",
        _replace_tg_emoji_tag,
        txt,
        flags=re.IGNORECASE | re.DOTALL
    )
    clean_lbl = ensure_visible_emoji_presentation(strip_tg_emoji_tags(txt)).strip()
    if extracted_id and keep_fallback_in_text and clean_lbl and eff_fallback and not any(_is_visible_emoji_or_symbol_chunk(ch) for ch in clean_lbl):
        clean_lbl = f"{eff_fallback} {clean_lbl}".strip()
    return clean_lbl, extracted_id


def apply_button_text_design(text: str, design_style: str = "normal") -> str:
    """Applies non-destructive visual text styling/design to a button label without affecting callbacks."""
    s = ensure_visible_emoji_presentation(str(text or "").strip())
    if not s or not design_style or design_style == "normal":
        return s
    st = str(design_style).lower().strip()
    if st in ("bold", "bold_sans"):
        return s.translate(_BOLD_SANS_MAP)
    if st in ("serif_bold", "bold_serif"):
        return s.translate(_BOLD_SERIF_MAP)
    if st == "monospace":
        return s.translate(_MONO_MAP)
    if st == "small_caps":
        return s.translate(_SMALL_CAPS_MAP)
    if st in ("bracket", "brackets", "bracketed"):
        if not (s.startswith("【") and s.endswith("】")):
            return f"【 {s} 】"
        return s
    if st == "star":
        if not (s.startswith("✦") and s.endswith("✦")):
            return f"✦ {s} ✦"
        return s
    if st == "sparkle":
        if not (s.startswith("✨") and s.endswith("✨")):
            return f"✨ {s} ✨"
        return s
    if st == "diamond":
        if not (s.startswith("❖") and s.endswith("❖")):
            return f"❖ {s} ❖"
        return s
    if st == "double_bar":
        if not (s.startswith("⟦") and s.endswith("⟧")):
            return f"⟦ {s} ⟧"
        return s
    return s


def ensure_full_width_message(html_text: str, has_buttons: bool = True) -> str:
    """
    Fixes the narrow message bubble gap shown in Screenshot 40929.jpg (Requirement 37):
    - Expands any short horizontal divider (`━{10,28}`) to a 30-character full-width divider (`FULL_WIDTH_DIVIDER`)
      so the Telegram message bubble stretches across the full width of the 2-column inline buttons.
    - If a message has inline buttons attached (`has_buttons=True`) and contains no full-width divider line,
      appends `FULL_WIDTH_DIVIDER` at the bottom so the message bubble always matches the full width of its buttons!
    """
    txt = str(html_text or "").strip()
    if not txt:
        return txt
    txt = re.sub(r"━{10,29}", FULL_WIDTH_DIVIDER, txt)
    if has_buttons and FULL_WIDTH_DIVIDER not in txt and "───" not in txt:
        txt = f"{txt}\n{FULL_WIDTH_DIVIDER}"
    return txt


class StyledInlineButton(types.InlineKeyboardButton):
    """
    InlineKeyboardButton supporting custom color style ('success', 'danger', 'primary')
    and Telegram Premium Button Custom Emoji ('icon_custom_emoji_id').
    """
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kwargs):
        norm_text = ensure_visible_emoji_presentation(str(text or ""))
        super().__init__(text=norm_text, **kwargs)
        self.text = norm_text
        self.style = style if style in ("success", "danger", "primary") else None
        clean_em = re.sub(r"[^0-9]", "", str(icon_custom_emoji_id or "").strip())
        self.icon_custom_emoji_id = clean_em if len(clean_em) >= 10 else None

    def to_dict(self):
        d = super().to_dict()
        d["text"] = ensure_visible_emoji_presentation(str(self.text or d.get("text", "")))
        if BUTTON_RUNTIME_CAPS.get("allow_style", True) and self.style and self.style in ("success", "danger", "primary"):
            d["style"] = self.style
        else:
            d.pop("style", None)
        if BUTTON_RUNTIME_CAPS.get("allow_custom_emoji", True) and self.icon_custom_emoji_id:
            d["icon_custom_emoji_id"] = str(self.icon_custom_emoji_id)
        else:
            d.pop("icon_custom_emoji_id", None)
        return d


class StyledKeyboardButton(types.KeyboardButton):
    """
    KeyboardButton (for ReplyKeyboardMarkup bottom menus) supporting custom color style
    ('success', 'danger', 'primary') and Telegram Premium Button Custom Emoji ('icon_custom_emoji_id').
    """
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kwargs):
        norm_text = ensure_visible_emoji_presentation(str(text or ""))
        super().__init__(text=norm_text, **kwargs)
        self.text = norm_text
        self.style = style if style in ("success", "danger", "primary") else None
        clean_em = re.sub(r"[^0-9]", "", str(icon_custom_emoji_id or "").strip())
        self.icon_custom_emoji_id = clean_em if len(clean_em) >= 10 else None

    def to_dict(self):
        d = super().to_dict()
        d["text"] = ensure_visible_emoji_presentation(str(self.text or d.get("text", "")))
        if BUTTON_RUNTIME_CAPS.get("allow_style", True) and self.style and self.style in ("success", "danger", "primary"):
            d["style"] = self.style
        else:
            d.pop("style", None)
        if BUTTON_RUNTIME_CAPS.get("allow_custom_emoji", True) and self.icon_custom_emoji_id:
            d["icon_custom_emoji_id"] = str(self.icon_custom_emoji_id)
        else:
            d.pop("icon_custom_emoji_id", None)
        return d


def make_reply_btn(text, style=None, icon_custom_emoji_id=None):
    """Creates a StyledKeyboardButton with color style and custom emoji support for Bottom Menu."""
    return StyledKeyboardButton(
        text=str(text),
        style=style,
        icon_custom_emoji_id=icon_custom_emoji_id
    )


def short_layout_code(layout_key: str) -> str:
    k = str(layout_key or "").strip()
    if k in SHORT_CODE_LAYOUT_MAP:
        return k
    if k.startswith("custom_page_cbtn_"):
        return "cbc_" + k[len("custom_page_cbtn_"):]
    if k.startswith("custom_page_"):
        return "cp_" + k.replace("custom_page_", "")
    if k.startswith(("cp_", "cbc_")):
        return k
    return LAYOUT_SHORT_CODE_MAP.get(k, "uh")


def resolve_layout_key(key_or_code: str) -> str:
    k = str(key_or_code or "").strip()
    if k in ALLOWED_DYNAMIC_LAYOUT_KEYS:
        return k
    if k.startswith("custom_page_"):
        return k
    if k.startswith("cbc_"):
        return "custom_page_cbtn_" + k[4:]
    if k.startswith("cp_"):
        return "custom_page_" + k[3:]
    return SHORT_CODE_LAYOUT_MAP.get(k, "user_home")



def validate_callback_data(callback_data: str) -> str:
    """Ensures callback_data is non-empty and strictly within Telegram's 64-byte UTF-8 limit."""
    cb = str(callback_data or "").strip()
    if not cb:
        raise ValueError("Telegram callback_data cannot be empty")
    raw_bytes = cb.encode("utf-8")
    if len(raw_bytes) > 64:
        raise ValueError(f"Telegram callback_data exceeds 64 UTF-8 bytes ({len(raw_bytes)} bytes): {cb}")
    return cb


def make_btn(text, callback_data=None, url=None, style=None, icon_custom_emoji_id=None):
    """Creates a validated StyledInlineButton with optional style and icon_custom_emoji_id."""
    if url:
        return StyledInlineButton(
            text=str(text),
            url=str(url),
            style=style,
            icon_custom_emoji_id=icon_custom_emoji_id
        )
    valid_cb = validate_callback_data(callback_data)
    return StyledInlineButton(
        text=str(text),
        callback_data=valid_cb,
        style=style,
        icon_custom_emoji_id=icon_custom_emoji_id
    )


def strip_legacy_action_routes(text: str) -> str:
    if not text:
        return ""
    cleaned = str(text)
    cleaned = re.sub(
        r"^\s*⤵️\s*(?:<b>)?বর্তমান মেসেজ টেমপ্লেট[^<\n]*(?:</b>)?\s*(?:<code>[a-zA-Z0-9_]+</code>)?\s*:?\s*\n+",
        "",
        cleaned
    )
    cleaned = re.sub(r"(?m)^\s*/action\b.*$", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def sanitize_admin_home_layout(raw_layout: list) -> list:
    seen = set()
    cleaned_rows = []
    if isinstance(raw_layout, list):
        for row in raw_layout:
            if not isinstance(row, list):
                continue
            new_row = []
            for key in row:
                k = str(key or "").strip()
                if not k or k in seen:
                    continue
                if k == "a_fin_history":
                    continue
                seen.add(k)
                new_row.append(k)
            if new_row:
                cleaned_rows.append(new_row)

    if not cleaned_rows:
        return json.loads(json.dumps(DEFAULT_LAYOUTS["admin_home"]))
    return cleaned_rows


def resolve_menu_layout(menu_id: str, cached_layouts: dict = None, default_layouts: dict = None) -> list:
    explicit_key = resolve_layout_key(str(menu_id or "").strip())
    if explicit_key not in ALLOWED_DYNAMIC_LAYOUT_KEYS and not explicit_key.startswith("custom_page_"):
        return []

    layouts_source = cached_layouts if isinstance(cached_layouts, dict) else {}
    defaults_source = default_layouts if isinstance(default_layouts, dict) else DEFAULT_LAYOUTS

    raw = layouts_source.get(explicit_key)
    if not raw or not isinstance(raw, list):
        raw = defaults_source.get(explicit_key, [])

    layout_copy = json.loads(json.dumps(raw))
    if explicit_key == "admin_home":
        return sanitize_admin_home_layout(layout_copy)
    return [r for r in layout_copy if isinstance(r, list) and r]


def paginate_items(items: list, page: int = 0, per_page: int = 10) -> dict:
    seq = list(items or [])
    total = len(seq)
    per_p = max(1, int(per_page or 10))
    total_pages = max(1, (total + per_p - 1) // per_p)
    safe_page = max(0, min(int(page or 0), total_pages - 1))
    start = safe_page * per_p
    end = start + per_p
    return {
        "items": seq[start:end],
        "page": safe_page,
        "per_page": per_p,
        "total_items": total,
        "total_pages": total_pages,
        "has_prev": safe_page > 0,
        "has_next": (safe_page + 1) < total_pages,
        "prev_page": max(0, safe_page - 1),
        "next_page": min(total_pages - 1, safe_page + 1)
    }


def build_pagination_row(
    page: int,
    total_items: int,
    per_page: int,
    callback_prefix: str,
    style: str = "primary"
) -> list:
    meta = paginate_items(range(max(0, int(total_items or 0))), page=page, per_page=per_page)
    pref = str(callback_prefix or "").rstrip(":") + ":"
    nav_btns = []
    if meta["has_prev"]:
        nav_btns.append(make_btn("⬅️ আগের পৃষ্ঠা (Previous)", callback_data=f"{pref}{meta['prev_page']}", style=style))
    if meta["has_next"]:
        nav_btns.append(make_btn("পরের পৃষ্ঠা (Next) ➡️", callback_data=f"{pref}{meta['next_page']}", style=style))
    return nav_btns


def unescape_allowed_html_tags(escaped_str: str) -> str:
    patterns = [
        (r"&lt;(/?(?:b|i|u|s|code|pre|blockquote|tg-spoiler))&gt;", r"<\1>"),
        (r"&lt;blockquote\s+expandable&gt;", r"<blockquote expandable>"),
        (r"&lt;pre&gt;&lt;code\s+class=(?:&quot;|&#x27;)([^&]+?)(?:&quot;|&#x27;)&gt;", r'<pre><code class="\1">'),
        (r"&lt;code\s+class=(?:&quot;|&#x27;)([^&]+?)(?:&quot;|&#x27;)&gt;", r'<code class="\1">'),
        (r"&lt;tg-emoji\s+emoji-id=(?:&quot;|&#x27;)?([0-9]+)(?:&quot;|&#x27;)?&gt;", r'<tg-emoji emoji-id="\1">'),
        (r"&lt;/tg-emoji&gt;", r"</tg-emoji>"),
        (r"&lt;a\s+href=(?:&quot;|&#x27;)([^&]+?)(?:&quot;|&#x27;)&gt;", r'<a href="\1">'),
        (r"&lt;/a&gt;", r"</a>"),
    ]
    out = str(escaped_str or "")
    for pat, rep in patterns:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    # Collapse any nested <tg-emoji> tags (even if outer and inner IDs differ, keep inner or outer cleanly)
    out = re.sub(
        r'(<tg-emoji\s+emoji-id=["\x27]([0-9]+)["\x27]>)\s*<tg-emoji\s+emoji-id=["\x27][0-9]+["\x27]>(.*?)</tg-emoji>\s*(</tg-emoji>)',
        r"\1\3\4",
        out,
        flags=re.IGNORECASE | re.DOTALL
    )
    # Fix crossed tags around <tg-emoji>
    out = re.sub(
        r'<(b|i|u|s|tg-spoiler)>(<tg-emoji\s+emoji-id=[^>]+>)(.*?)</\1>(</tg-emoji>)',
        r"<\1>\2\3\4</\1>",
        out,
        flags=re.IGNORECASE | re.DOTALL
    )
    out = re.sub(
        r'(<tg-emoji\s+emoji-id=[^>]+>)<(b|i|u|s|tg-spoiler)>(.*?)(</tg-emoji>)</\2>',
        r"<\2>\1\3\4</\2>",
        out,
        flags=re.IGNORECASE | re.DOTALL
    )
    # Move any inline style accidentally nested completely inside <tg-emoji> outside of <tg-emoji>
    out = re.sub(
        r'(<tg-emoji\s+emoji-id=[^>]+>)<(b|i|u|s|tg-spoiler)>(.*?)</\2>(</tg-emoji>)',
        r"<\2>\1\3\4</\2>",
        out,
        flags=re.IGNORECASE | re.DOTALL
    )
    return ensure_visible_emoji_presentation(out)


def serialize_message_entities(message) -> list:
    entities = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or []
    out = []
    for ent in entities:
        if isinstance(ent, dict):
            item = {
                "type": str(ent.get("type", "")),
                "offset": int(ent.get("offset", 0)),
                "length": int(ent.get("length", 0))
            }
            if ent.get("url"):
                item["url"] = str(ent["url"])
            if ent.get("language"):
                item["language"] = str(ent["language"])
            if ent.get("custom_emoji_id"):
                item["custom_emoji_id"] = str(ent["custom_emoji_id"])
            out.append(item)
            continue
        item = {
            "type": getattr(ent, "type", ""),
            "offset": int(getattr(ent, "offset", 0)),
            "length": int(getattr(ent, "length", 0))
        }
        if getattr(ent, "url", None):
            item["url"] = str(ent.url)
        if getattr(ent, "language", None):
            item["language"] = str(ent.language)
        c_id = getattr(ent, "custom_emoji_id", None)
        if not c_id and hasattr(ent, "__dict__"):
            c_id = ent.__dict__.get("custom_emoji_id")
        if c_id:
            item["custom_emoji_id"] = str(c_id)
        out.append(item)
    return out


def reconstruct_html_from_raw_and_entities(raw_text: str, entities: list) -> str:
    """
    UTF-16 Grapheme-Aware & Strict LIFO Stack-Based Telegram Rich HTML Serializer:
    - Converts `raw_text` and `entities` (`MessageEntity` objects or dicts) into valid Telegram HTML.
    - Never splits multi-codepoint emojis (`❤️`, `1️⃣`, `🛡️`, `❤️‍🔥`) across tag boundaries.
    - Never places `<tg-emoji>` inside `<code>` or `<pre>` (automatically splits `<code>`/`<pre>` around `<tg-emoji>`).
    - Never places `<b>`/`<i>`/`<u>`/`<s>` inside `<tg-emoji>` (`<tg-emoji>` is always the innermost leaf tag).
    - Guarantees 0% crossed HTML tags even when Telegram Android sends partially overlapping entities.
    """
    if not raw_text:
        return ""
    if not entities:
        return strip_legacy_action_routes(unescape_allowed_html_tags(html.escape(ensure_visible_emoji_presentation(raw_text))))

    utf16_bytes = raw_text.encode("utf-16-le")
    total_units = len(utf16_bytes) // 2
    if total_units == 0:
        return ""

    def _u16_code(u_idx: int) -> int:
        if 0 <= u_idx < total_units:
            return int.from_bytes(utf16_bytes[u_idx * 2:(u_idx + 1) * 2], "little")
        return 0

    # 1. Extract and normalize custom_emoji spans first (expanding to include trailing FE0F/20E3/ZWJ if needed)
    ce_spans = []
    other_raw_spans = []
    for ent in entities:
        etype = ent.get("type", "") if isinstance(ent, dict) else getattr(ent, "type", "")
        off = int(ent.get("offset", 0) if isinstance(ent, dict) else getattr(ent, "offset", 0))
        ln = int(ent.get("length", 0) if isinstance(ent, dict) else getattr(ent, "length", 0))
        start = max(0, min(total_units, off))
        end = max(0, min(total_units, off + ln))
        if end <= start:
            continue
        # Never start or end in the middle of a UTF-16 surrogate pair
        if 0xDC00 <= _u16_code(start) <= 0xDFFF and start > 0:
            start -= 1
        if 0xD800 <= _u16_code(end - 1) <= 0xDBFF and end < total_units:
            end += 1

        if etype == "custom_emoji":
            c_id = ent.get("custom_emoji_id", "") if isinstance(ent, dict) else getattr(ent, "custom_emoji_id", None)
            if not c_id and hasattr(ent, "__dict__"):
                c_id = ent.__dict__.get("custom_emoji_id")
            if c_id:
                # If immediately followed by U+FE0F or U+20E3 not covered by another custom_emoji, include it
                while end < total_units and _u16_code(end) in (0xFE0F, 0xFE0E, 0x20E3):
                    end += 1
                ce_spans.append((start, end, str(c_id).strip()))
        else:
            url = (ent.get("url") if isinstance(ent, dict) else getattr(ent, "url", None)) or ""
            lang = (ent.get("language") if isinstance(ent, dict) else getattr(ent, "language", None)) or ""
            other_raw_spans.append((etype, start, end, str(url), str(lang)))

    # Deduplicate/resolve overlapping custom_emoji spans
    ce_spans.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    clean_ce_spans = []
    last_ce_end = 0
    for s_u, e_u, cid in ce_spans:
        if s_u < last_ce_end:
            continue
        clean_ce_spans.append((s_u, e_u, cid))
        last_ce_end = e_u

    # Also detect `{placeholder}` spans in raw_text so formatting tags never split `{nam</b>e}` in half!
    placeholder_spans = []
    for pm in re.finditer(r"\{[a-zA-Z0-9_]+\}", raw_text):
        p_s = len(raw_text[:pm.start()].encode("utf-16-le")) // 2
        p_e = len(raw_text[:pm.end()].encode("utf-16-le")) // 2
        placeholder_spans.append((p_s, p_e))

    # 2. Snap non-custom_emoji boundaries so they never split a custom_emoji span or `{placeholder}` span,
    #    and split `code`/`pre` spans around `custom_emoji` spans so <tg-emoji> is never inside <code>/<pre>!
    normalized_spans = []
    for s_u, e_u, cid in clean_ce_spans:
        normalized_spans.append({
            "etype": "custom_emoji",
            "start": s_u,
            "end": e_u,
            "open_tag": f'<tg-emoji emoji-id="{cid}">',
            "close_tag": "</tg-emoji>",
            "rank": 100
        })

    rank_map = {
        "blockquote": 10,
        "expandable_blockquote": 10,
        "pre": 20,
        "code": 25,
        "text_link": 30,
        "bold": 40,
        "italic": 50,
        "underline": 60,
        "strikethrough": 70,
        "spoiler": 80,
    }

    for etype, s_u, e_u, url, lang in other_raw_spans:
        if etype not in rank_map:
            continue
        # Snap s_u and e_u if they fall strictly inside any custom_emoji span or {placeholder} span
        for ce_s, ce_e, _ in clean_ce_spans:
            if ce_s < s_u < ce_e:
                s_u = ce_s
            if ce_s < e_u < ce_e:
                e_u = ce_e
        for ph_s, ph_e in placeholder_spans:
            if ph_s < s_u < ph_e:
                s_u = ph_s
            if ph_s < e_u < ph_e:
                e_u = ph_e
        if e_u <= s_u:
            continue

        if etype in ("code", "pre"):
            # Split [s_u, e_u) around all custom_emoji spans
            segments = [(s_u, e_u)]
            for ce_s, ce_e, _ in clean_ce_spans:
                next_segs = []
                for seg_s, seg_e in segments:
                    if ce_e <= seg_s or ce_s >= seg_e:
                        next_segs.append((seg_s, seg_e))
                    else:
                        if seg_s < ce_s:
                            next_segs.append((seg_s, ce_s))
                        if ce_e < seg_e:
                            next_segs.append((ce_e, seg_e))
                segments = next_segs
            for seg_s, seg_e in segments:
                if seg_e <= seg_s:
                    continue
                if etype == "code":
                    o_t, c_t = "<code>", "</code>"
                else:
                    o_t = f'<pre><code class="language-{html.escape(lang)}">' if lang else "<pre>"
                    c_t = "</code></pre>" if lang else "</pre>"
                normalized_spans.append({
                    "etype": etype,
                    "start": seg_s,
                    "end": seg_e,
                    "open_tag": o_t,
                    "close_tag": c_t,
                    "rank": rank_map[etype]
                })
        else:
            # Also split inline styles around `code`/`pre` spans later via _split_inline_styles_around_code
            if etype == "bold":
                o_t, c_t = "<b>", "</b>"
            elif etype == "italic":
                o_t, c_t = "<i>", "</i>"
            elif etype == "underline":
                o_t, c_t = "<u>", "</u>"
            elif etype == "strikethrough":
                o_t, c_t = "<s>", "</s>"
            elif etype == "spoiler":
                o_t, c_t = "<tg-spoiler>", "</tg-spoiler>"
            elif etype == "expandable_blockquote":
                o_t, c_t = "<blockquote expandable>", "</blockquote>"
            elif etype == "blockquote":
                o_t, c_t = "<blockquote>", "</blockquote>"
            elif etype == "text_link":
                if not url:
                    continue
                o_t, c_t = f'<a href="{html.escape(url)}">', "</a>"
            else:
                continue
            normalized_spans.append({
                "etype": etype,
                "start": s_u,
                "end": e_u,
                "open_tag": o_t,
                "close_tag": c_t,
                "rank": rank_map[etype]
            })

    # Assign unique IDs to spans
    for idx_sp, sp in enumerate(normalized_spans):
        sp["id"] = idx_sp

    starts_at = {i: [] for i in range(total_units + 1)}
    ends_at = {i: [] for i in range(total_units + 1)}
    for sp in normalized_spans:
        starts_at[sp["start"]].append(sp)
        ends_at[sp["end"]].append(sp)

    # Sort starts: outer rank first (smaller rank number first, then longer span first)
    for idx in range(total_units + 1):
        starts_at[idx].sort(key=lambda sp: (sp["rank"], -(sp["end"] - sp["start"]), sp["id"]))

    out = []
    active_stack = []  # list of active span dicts in open order

    pos = 0
    while pos <= total_units:
        # 1. Close spans ending at `pos` (if an inner span is still active on top of it, close inner first and reopen it)
        ending_ids = {sp["id"] for sp in ends_at[pos]}
        if ending_ids and active_stack:
            # Find lowest index in active_stack that is ending at `pos`
            first_idx = None
            for i_st, sp in enumerate(active_stack):
                if sp["id"] in ending_ids:
                    first_idx = i_st
                    break
            if first_idx is not None:
                to_reopen = []
                while len(active_stack) > first_idx:
                    top_sp = active_stack.pop()
                    out.append(top_sp["close_tag"])
                    if top_sp["id"] not in ending_ids and top_sp["end"] > pos:
                        to_reopen.append(top_sp)
                for sp_re in reversed(to_reopen):
                    out.append(sp_re["open_tag"])
                    active_stack.append(sp_re)

        if pos == total_units:
            break

        # 2. Open spans starting at `pos` while maintaining rank hierarchy (tg-emoji rank=100 is always innermost)
        if starts_at[pos]:
            for new_sp in starts_at[pos]:
                # Avoid duplicate identical tag type already in active_stack
                if any(s["etype"] == new_sp["etype"] and s["open_tag"] == new_sp["open_tag"] for s in active_stack):
                    continue
                # If active_stack has spans with higher rank (e.g. custom_emoji=100) than new_sp, pop them temporarily
                temp_popped = []
                while active_stack and active_stack[-1]["rank"] > new_sp["rank"]:
                    top_sp = active_stack.pop()
                    out.append(top_sp["close_tag"])
                    temp_popped.append(top_sp)
                out.append(new_sp["open_tag"])
                active_stack.append(new_sp)
                for sp_re in reversed(temp_popped):
                    out.append(sp_re["open_tag"])
                    active_stack.append(sp_re)

        # 3. Emit character (handling UTF-16 surrogate pairs)
        code_unit = _u16_code(pos)
        if 0xD800 <= code_unit <= 0xDBFF and (pos + 1) < total_units and (0xDC00 <= _u16_code(pos + 1) <= 0xDFFF):
            char_str = utf16_bytes[pos * 2:(pos + 2) * 2].decode("utf-16-le", errors="ignore")
            out.append(html.escape(char_str))
            pos += 2
        else:
            char_str = utf16_bytes[pos * 2:(pos + 1) * 2].decode("utf-16-le", errors="ignore")
            out.append(html.escape(char_str))
            pos += 1

    while active_stack:
        top_sp = active_stack.pop()
        out.append(top_sp["close_tag"])

    rendered = _split_inline_styles_around_code(unescape_allowed_html_tags("".join(out)))
    return strip_legacy_action_routes(rendered)


def extract_rich_html_text(message) -> str:
    raw_text = getattr(message, "text", None) or getattr(message, "caption", None) or ""
    entities = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or []
    if not raw_text:
        if getattr(message, "sticker", None):
            st_em = ensure_visible_emoji_presentation(str(getattr(message.sticker, "emoji", "") or "❤️"))
            st_cid = str(getattr(message.sticker, "custom_emoji_id", "") or "").strip()
            if st_cid:
                return f'<tg-emoji emoji-id="{st_cid}">{html.escape(st_em)}</tg-emoji>'
            return html.escape(st_em)
        return ""
    return reconstruct_html_from_raw_and_entities(raw_text, entities)


def _make_safe_entity(type: str, offset: int, length: int, url: str = None, language: str = None, custom_emoji_id: str = None):
    try:
        ent = types.MessageEntity(
            type=type,
            offset=int(offset),
            length=int(length),
            url=url,
            language=language,
            custom_emoji_id=custom_emoji_id
        )
    except TypeError:
        ent = types.MessageEntity(type=type, offset=int(offset), length=int(length))
        if url:
            ent.url = url
        if language:
            ent.language = language
        if custom_emoji_id:
            ent.custom_emoji_id = str(custom_emoji_id)
    if custom_emoji_id and not getattr(ent, "custom_emoji_id", None):
        try:
            ent.custom_emoji_id = str(custom_emoji_id)
        except Exception:
            pass
    return ent


def _split_inline_styles_around_code(html_text: str) -> str:
    """
    Telegram Bot API rules enforced here:
    1. `<code>` and `<pre>` cannot be nested inside `<b>`, `<i>`, `<u>`, `<s>`, `<tg-spoiler>`, or `<a>`.
    2. `<tg-emoji>` CANNOT be nested inside `<code>` or `<pre>` (Telegram rejects `<code><tg-emoji>...</tg-emoji></code>` with 400 Bad Request!).
       Whenever `<tg-emoji ...>...</tg-emoji>` appears inside `<code>...</code>` or `<pre>...</pre>`, we automatically close `</code>`/`</pre>`
       before `<tg-emoji>` and reopen `<code>`/`<pre>` immediately after `</tg-emoji>`!
    3. No inline tags (`<b>`, `<i>`, `<u>`, `<s>`, `<tg-spoiler>`) may remain inside `<tg-emoji>...</tg-emoji>`.
    """
    if not html_text:
        return ""
    s = str(html_text)
    # Strip any formatting tags accidentally placed inside <tg-emoji>...</tg-emoji> while keeping them outside
    def _clean_inside_tg_emoji(m):
        open_tg = m.group(1)
        inner = m.group(2)
        close_tg = m.group(3)
        outer_opens = []
        outer_closes = []
        for st_name in ("b", "i", "u", "s", "tg-spoiler"):
            if re.search(rf"<{st_name}>", inner, flags=re.IGNORECASE) and not re.search(rf"</{st_name}>", inner, flags=re.IGNORECASE):
                outer_opens.append(f"<{st_name}>")
            elif re.search(rf"</{st_name}>", inner, flags=re.IGNORECASE) and not re.search(rf"<{st_name}>", inner, flags=re.IGNORECASE):
                outer_closes.append(f"</{st_name}>")
            elif re.search(rf"<{st_name}>.*?</{st_name}>", inner, flags=re.IGNORECASE | re.DOTALL):
                outer_opens.append(f"<{st_name}>")
                outer_closes.insert(0, f"</{st_name}>")
        clean_inner = re.sub(r"<[^>]+>", "", inner)
        clean_inner = ensure_visible_emoji_presentation(html.unescape(clean_inner))
        if not _is_visible_emoji_or_symbol_chunk(clean_inner):
            clean_inner = "✨"
        return "".join(outer_opens) + open_tg + html.escape(clean_inner) + close_tg + "".join(outer_closes)

    s = re.sub(
        r'(<tg-emoji\s+emoji-id=["\x27][0-9]+["\x27]>)(.*?)(</tg-emoji>)',
        _clean_inside_tg_emoji,
        s,
        flags=re.IGNORECASE | re.DOTALL
    )

    if "<code" not in s.lower() and "<pre" not in s.lower():
        return s

    token_re = re.compile(
        r'(<tg-emoji\s+emoji-id=["\x27][0-9]+["\x27]>.*?</tg-emoji>|<(/?)(b|i|u|s|tg-spoiler|code|pre)(?:\s+[^>]*)?>)',
        re.IGNORECASE | re.DOTALL
    )
    out = []
    pos = 0
    active_styles = []
    in_code_or_pre = None
    in_code_open_tag = "<code>"

    for m in token_re.finditer(s):
        out.append(s[pos:m.start()])
        full_tag = m.group(1)

        if full_tag.lower().startswith("<tg-emoji"):
            if in_code_or_pre is not None:
                # Close code/pre before <tg-emoji>, emit active_styles if any, emit <tg-emoji>, close active_styles, reopen code/pre
                out.append("</code></pre>" if (in_code_or_pre == "pre" and "<code" in in_code_open_tag.lower()) else f"</{in_code_or_pre}>")
                for st in active_styles:
                    out.append(f"<{st}>")
                out.append(full_tag)
                for st in reversed(active_styles):
                    out.append(f"</{st}>")
                out.append(in_code_open_tag)
            else:
                out.append(full_tag)
            pos = m.end()
            continue

        is_close = bool(m.group(2))
        t_name = (m.group(3) or "").lower()

        if t_name in ("code", "pre"):
            if not is_close and in_code_or_pre is None:
                if active_styles:
                    for st in reversed(active_styles):
                        out.append(f"</{st}>")
                out.append(full_tag)
                in_code_or_pre = t_name
                in_code_open_tag = full_tag
            elif is_close and in_code_or_pre == t_name:
                out.append(full_tag)
                in_code_or_pre = None
                if active_styles:
                    for st in active_styles:
                        out.append(f"<{st}>")
            else:
                # Ignore nested <code> inside <pre> or stray close
                if not is_close and in_code_or_pre == "pre" and t_name == "code":
                    in_code_open_tag = "<pre>" + full_tag
                    out.append(full_tag)
                elif is_close and in_code_or_pre == "pre" and t_name == "code":
                    out.append(full_tag)
        else:
            if not is_close:
                if t_name not in active_styles:
                    active_styles.append(t_name)
                if in_code_or_pre is None:
                    out.append(full_tag)
            else:
                if t_name in active_styles:
                    for idx in range(len(active_styles) - 1, -1, -1):
                        if active_styles[idx] == t_name:
                            active_styles.pop(idx)
                            break
                if in_code_or_pre is None:
                    out.append(full_tag)
        pos = m.end()

    out.append(s[pos:])
    res = "".join(out)
    # Remove any empty <code></code> or <pre></pre> pairs created by splitting around <tg-emoji> at the start/end of code
    res = re.sub(r"<code>\s*</code>", "", res, flags=re.IGNORECASE)
    res = re.sub(r"<pre>\s*</pre>", "", res, flags=re.IGNORECASE)
    return res


def html_to_plain_and_telegram_entities(html_text: str) -> tuple:
    html_text = _split_inline_styles_around_code(unescape_allowed_html_tags(str(html_text or "")))
    tag_re = re.compile(
        r'(<tg-emoji\s+emoji-id=["\x27]([0-9]+)["\x27]>|</tg-emoji>|<b>|</b>|<i>|</i>|<u>|</u>|<s>|</s>|<code(?:\s+[^>]*)?>|</code>|<pre(?:\s+[^>]*)?>|</pre>|<tg-spoiler>|</tg-spoiler>|<blockquote(?:\s+expandable)?>|</blockquote>|<a\s+href=["\x27]([^"\x27]+)["\x27]>|</a>)',
        re.IGNORECASE
    )
    pos = 0
    plain_chunks = []
    utf16_len = 0
    stack = []
    entities = []

    for m in tag_re.finditer(str(html_text or "")):
        before = html_text[pos:m.start()]
        if before:
            unesc = ensure_visible_emoji_presentation(html.unescape(before))
            plain_chunks.append(unesc)
            utf16_len += len(unesc.encode("utf-16-le")) // 2
        tag = m.group(1)
        t_low = tag.lower()
        if t_low.startswith("<tg-emoji"):
            stack.append(("custom_emoji", utf16_len, {"custom_emoji_id": m.group(2)}))
        elif t_low == "</tg-emoji>":
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == "custom_emoji":
                    etype, start_u, extra = stack.pop(idx)
                    if utf16_len == start_u:
                        fallback_ch = "✨"
                        plain_chunks.append(fallback_ch)
                        utf16_len += len(fallback_ch.encode("utf-16-le")) // 2
                    if utf16_len > start_u:
                        entities.append(
                            _make_safe_entity(
                                type=etype,
                                offset=start_u,
                                length=utf16_len - start_u,
                                custom_emoji_id=extra["custom_emoji_id"]
                            )
                        )
                    break
        elif t_low in ("<b>", "<i>", "<u>", "<s>", "<tg-spoiler>", "<blockquote>") or t_low.startswith(("<pre", "<code", "<blockquote")):
            if t_low.startswith("<pre"):
                stack.append(("pre", utf16_len, {}))
            elif t_low.startswith("<code"):
                if not any(s[0] == "pre" for s in stack):
                    stack.append(("code", utf16_len, {}))
            elif t_low.startswith("<blockquote"):
                b_type = "expandable_blockquote" if "expandable" in t_low else "blockquote"
                stack.append((b_type, utf16_len, {}))
            else:
                map_t = {
                    "<b>": "bold", "<i>": "italic", "<u>": "underline", "<s>": "strikethrough",
                    "<tg-spoiler>": "spoiler"
                }
                stack.append((map_t[t_low], utf16_len, {}))
        elif t_low in ("</b>", "</i>", "</u>", "</s>", "</code>", "</pre>", "</tg-spoiler>", "</blockquote>"):
            map_c = {
                "</b>": ("bold",), "</i>": ("italic",), "</u>": ("underline",), "</s>": ("strikethrough",),
                "</code>": ("code",), "</pre>": ("pre",), "</tg-spoiler>": ("spoiler",),
                "</blockquote>": ("blockquote", "expandable_blockquote")
            }
            target_types = map_c[t_low]
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] in target_types:
                    etype, start_u, _ = stack.pop(idx)
                    if utf16_len > start_u:
                        entities.append(
                            _make_safe_entity(
                                type=etype,
                                offset=start_u,
                                length=utf16_len - start_u
                            )
                        )
                    break
        elif t_low.startswith("<a "):
            stack.append(("text_link", utf16_len, {"url": html.unescape(m.group(3) or "")}))
        elif t_low == "</a>":
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == "text_link":
                    etype, start_u, extra = stack.pop(idx)
                    if utf16_len > start_u:
                        entities.append(
                            _make_safe_entity(
                                type=etype,
                                offset=start_u,
                                length=utf16_len - start_u,
                                url=extra.get("url")
                            )
                        )
                    break
        pos = m.end()

    tail = str(html_text or "")[pos:]
    if tail:
        unesc = ensure_visible_emoji_presentation(html.unescape(tail))
        plain_chunks.append(unesc)

    entities.sort(key=lambda e: (e.offset, -e.length))
    return "".join(plain_chunks), entities


def parse_telegram_html(rendered_html: str) -> tuple:
    cleaned_html = repair_or_fallback_html(strip_legacy_action_routes(str(rendered_html or "")))
    plain_text, entities = html_to_plain_and_telegram_entities(cleaned_html)
    has_custom_emoji = any(getattr(e, "type", "") == "custom_emoji" for e in entities)
    return plain_text, entities, has_custom_emoji


def strip_tg_emoji_tags(html_text: str) -> str:
    if not html_text:
        return ""
    out = re.sub(r"<tg-emoji\s+emoji-id=[\x22\x27][0-9]+[\x22\x27]>", "", str(html_text), flags=re.IGNORECASE)
    out = re.sub(r"</tg-emoji>", "", out, flags=re.IGNORECASE)
    return ensure_visible_emoji_presentation(out)


def validate_bio_verification_code_format(code: str) -> bool:
    c = str(code or "").strip().upper()
    return bool(re.fullmatch(r"BC-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{6}", c))


def validate_channel_criteria_payload(
    platform: str,
    bio_found: bool,
    bio_code: str,
    subs_count: int,
    total_videos: int,
    qualifying_videos_count: int,
    min_subs: int,
    min_total_videos: int,
    req_qualifying_videos: int,
    min_views_per_video: int,
    qualifying_views_total: int = 0
) -> dict:
    p_title = str(platform or "Platform").upper()
    req_total_views = int(min_views_per_video or 0) * int(req_qualifying_videos or 0)
    eff_qual_views = int(qualifying_views_total or (int(qualifying_videos_count or 0) * int(min_views_per_video or 0)))

    failed_reasons = []
    if not bio_found:
        failed_reasons.append(f"বায়োতে ভেরিফিকেশন কোড পাওয়া যায়নি ({bio_code})")
    if int(subs_count or 0) < int(min_subs or 0):
        failed_reasons.append(f"ন্যূনতম {min_subs} ফলোয়ার/সাবস্ক্রাইবার প্রয়োজন কিন্তু আছে {subs_count}")
    if int(total_videos or 0) < int(min_total_videos or 0):
        failed_reasons.append(f"প্রোফাইলে ন্যূনতম {min_total_videos}টি পাবলিক ভিডিও প্রয়োজন কিন্তু আছে {total_videos}টি")
    if int(qualifying_videos_count or 0) < int(req_qualifying_videos or 0) or eff_qual_views < req_total_views:
        failed_reasons.append(
            f"ন্যূনতম {req_qualifying_videos}টি যোগ্য ভিডিওতে প্রতিটিতে {min_views_per_video}+ করে মোট {req_total_views}+ ভিউজ নেই "
            f"(পাওয়া গেছে {qualifying_videos_count}টি যোগ্য ভিডিও, মোট ভিউজ: {eff_qual_views})"
        )

    if failed_reasons:
        return {
            "eligible": False,
            "reason": " | ".join(failed_reasons)
        }
    return {
        "eligible": True,
        "reason": (
            f"{p_title} প্রোফাইলের বায়ো কোড ({bio_code}), ফলোয়ার ({subs_count}), "
            f"মোট পাবলিক ভিডিও ({total_videos}টি), যোগ্য ভিডিও ({qualifying_videos_count}টি) "
            f"ও মোট ভিউজ ({eff_qual_views}) সফলভাবে যাচাই হয়েছে।"
        )
    }


def repair_or_fallback_html(candidate_html: str, fallback_html: str = "") -> str:
    """
    Non-Destructive Stack-Balancing HTML Sanitizer & Auto-Recovery System for Dynamic Messages:
    - Guarantees that 100% of `<tg-emoji emoji-id="...">...</tg-emoji>` tags in admin-edited status
      and notification messages are preserved and NEVER degraded into normal emojis!
    - Automatically repairs crossed tags (`<b>...<tg-emoji>...</b></tg-emoji>`), unclosed tags,
      stray closing tags, unknown `<...>` brackets, and `<tg-emoji>` nested inside `<code>`/`<pre>`.
    """
    raw_cand = str(candidate_html or "").strip()
    if not raw_cand:
        return str(fallback_html or "")

    text = _split_inline_styles_around_code(unescape_allowed_html_tags(raw_cand))

    valid_tag_re = re.compile(
        r"^<(?:"
        r"(/?)(b|i|u|s|code|pre|blockquote|tg-spoiler)|"
        r"(blockquote)\s+expandable|"
        r"(code)\s+class=[\x22\x27][^\x22\x27]+[\x22\x27]|"
        r"(tg-emoji)\s+emoji-id=[\x22\x27]?([0-9]+)[\x22\x27]?|"
        r"(/)?(tg-emoji)|"
        r"(a)\s+href=[\x22\x27]([^\x22\x27]+)[\x22\x27]|"
        r"(/)?(a)"
        r")>$",
        re.IGNORECASE
    )

    out = []
    open_stack = []  # list of (tag_name, canonical_open_tag, canonical_close_tag)
    pos = 0

    for m in re.finditer(r"<[^>]*>", text):
        if m.start() > pos:
            out.append(text[pos:m.start()])
        full_tag = m.group(0)
        pos = m.end()

        vm = valid_tag_re.match(full_tag)
        if not vm:
            # Escape unknown `<...>` brackets so Telegram HTML parser never fails, without losing the rest of the message
            out.append(html.escape(full_tag))
            continue

        t_low = full_tag.lower()
        is_closing = t_low.startswith("</")

        if is_closing:
            t_name = re.sub(r"^</\s*|\s*>$", "", t_low)
            # Check if t_name is in open_stack
            match_idx = None
            for idx in range(len(open_stack) - 1, -1, -1):
                if open_stack[idx][0] == t_name:
                    match_idx = idx
                    break
            if match_idx is None:
                # Stray closing tag: drop it cleanly without corrupting the message
                continue
            # Pop inner tags above match_idx, close target tag, and reopen inner tags (except tg-emoji)
            to_reopen = []
            while len(open_stack) > match_idx:
                top_name, top_open, top_close = open_stack.pop()
                out.append(top_close)
                if len(open_stack) >= match_idx and top_name != t_name and top_name != "tg-emoji":
                    to_reopen.append((top_name, top_open, top_close))
            for item_re in reversed(to_reopen):
                out.append(item_re[1])
                open_stack.append(item_re)
        else:
            if t_low.startswith("<tg-emoji"):
                em_m = re.search(r"emoji-id=[\x22\x27]?([0-9]+)[\x22\x27]?", full_tag, flags=re.IGNORECASE)
                if not em_m:
                    continue
                em_id = em_m.group(1)
                canon_open = f'<tg-emoji emoji-id="{em_id}">'
                canon_close = "</tg-emoji>"
                t_name = "tg-emoji"
            elif t_low.startswith("<a "):
                href_m = re.search(r"href=[\x22\x27]([^\x22\x27]+)[\x22\x27]", full_tag, flags=re.IGNORECASE)
                href_val = html.escape(html.unescape(href_m.group(1)), quote=True) if href_m else ""
                canon_open = f'<a href="{href_val}">'
                canon_close = "</a>"
                t_name = "a"
            elif t_low.startswith("<blockquote"):
                canon_open = "<blockquote expandable>" if "expandable" in t_low else "<blockquote>"
                canon_close = "</blockquote>"
                t_name = "blockquote"
            elif t_low.startswith("<code"):
                cls_m = re.search(r"class=[\x22\x27]([^\x22\x27]+)[\x22\x27]", full_tag, flags=re.IGNORECASE)
                canon_open = f'<code class="{cls_m.group(1)}">' if cls_m else "<code>"
                canon_close = "</code>"
                t_name = "code"
            elif t_low.startswith("<pre"):
                canon_open = "<pre>"
                canon_close = "</pre>"
                t_name = "pre"
            else:
                t_name = t_low[1:-1].strip()
                canon_open = f"<{t_name}>"
                canon_close = f"</{t_name}>"

            # Never open any tag inside an open <tg-emoji>; close <tg-emoji> first if unclosed
            if open_stack and open_stack[-1][0] == "tg-emoji":
                _, _, tg_close = open_stack.pop()
                out.append(tg_close)

            out.append(canon_open)
            open_stack.append((t_name, canon_open, canon_close))

    if pos < len(text):
        out.append(text[pos:])

    while open_stack:
        t_name, _, top_close = open_stack.pop()
        if t_name == "tg-emoji" and out and out[-1].startswith("<tg-emoji"):
            out.append("✨")
        out.append(top_close)

    repaired = "".join(out)
    # Ensure no empty <tg-emoji emoji-id="..."></tg-emoji>
    repaired = re.sub(
        r'(<tg-emoji\s+emoji-id=["\x27][0-9]+["\x27]>)\s*(</tg-emoji>)',
        r"\1✨\2",
        repaired,
        flags=re.IGNORECASE
    )
    return _split_inline_styles_around_code(ensure_visible_emoji_presentation(repaired))