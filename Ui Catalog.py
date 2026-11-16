# -*- coding: utf-8 -*-
"""
BATTLE CLUB TELEGRAM BOT - DYNAMIC UI, MESSAGE & COMMAND CATALOG (v8.0)
- Strictly YouTube & TikTok Only Platform Catalog
- Centralizes ALL Button Labels (Main + Nested Sub-Buttons), Custom Emoji IDs, Text Designs, Color Themes & Multi-Page Layouts
- Full Support for Advanced Settings (Button Name & Emoji Editor, Message & Status Editor, Button Position & Cross-Page Mover, Live Previews)
- Full-Width Message Dividers (30-char `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`) Eliminating Right-Side Empty Space on All Pages
- Default View Tracking Duration Set to 5 Days & Max Payable Views Set to 50,00,000 (50 Lakh)
- Mandatory Battle Club UID First in Onboarding + 1/2/3 Payment Method Selection (bKash, Nagad, Rocket) + Per-Platform Channel Name + Double Password Confirmation
- Preserves 100% of Telegram Premium Custom Emoji `<tg-emoji emoji-id="...">` formatting
"""

FULL_WIDTH_DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

COLOR_PALETTE = {
    "success": "সবুজ (Success - Green)",
    "danger": "লাল (Danger - Red)",
    "primary": "নীল (Primary - Blue)",
    "default": "ডিফল্ট (Default)"
}

BUTTON_TEXT_DESIGNS = {
    "normal": "সাধারণ (Standard Text)",
    "bold_sans": "বোল্ড স্যান্স (𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀)",
    "bold_serif": "বোল্ড সেরিফ (𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟)",
    "bracket": "ব্র্যাকেট স্টাইল (【Button】)",
    "star": "স্টার প্রিমিয়াম (✦ Button ✦)",
    "diamond": "ডায়মন্ড স্টাইল (❖ Button ❖)"
}

ALLOWED_DYNAMIC_LAYOUT_KEYS = (
    "user_home",
    "user_settings_hub",
    "user_dashboard",
    "user_profile",
    "admin_home",
    "admin_settings_hub",
    "admin_platform_settings",
    "admin_general_settings",
    "admin_advanced_settings"
)

PAGE_LAYOUT_TITLES = {
    "user_home": "🏠 ইউজার হোম মেনু (User Home Page)",
    "user_settings_hub": "⚙️ ইউজার সেটিংস হাব (User Settings Hub)",
    "user_dashboard": "📊 ইউজার ড্যাশবোর্ড পেজ (User Dashboard)",
    "user_profile": "👤 ইউজার প্রোফাইল পেজ (User Profile)",
    "admin_home": "👑 অ্যাডমিন মেইন প্যানেল (Admin Main Panel)",
    "admin_settings_hub": "🛠️ অ্যাডমিন কন্ট্রোল সেটিংস হাব (Control Settings Hub)",
    "admin_general_settings": "⚙️ অ্যাডমিন জেনারেল সেটিংস (General Settings)"
}

DEFAULT_SETTINGS = {
    "rate_per_1k": "15.0",
    "first_1000_views_payment": "15.0",
    "every_200_views_payment": "3.0",
    "min_withdraw": "100.0",
    "max_daily_wd_count": "2",
    "max_daily_wd_amount": "5000.0",
    "max_single_withdraw": "5000.0",
    "ref_bonus": "10.0",
    "redeem_bonus": "5.0",
    "max_daily_referrals": "5",
    "ref_unlock_on_first_video": "0",
    "wd_eta_text": "১২ থেকে ২৪ ঘণ্টার মধ্যে",
    "min_initial_views": "1000",
    "auto_approve": "1",
    "enforce_72h_rule": "1",
    "submission_window_hours": "72",
    "qualification_window_hours": "120",
    "view_tracking_days": "5",
    "earning_duration_days": "5",
    "view_step_size": "200",
    "view_checking_interval_sec": "3600",
    "verification_interval_sec": "3600",
    "user_session_timeout_sec": "600",
    "max_payable_views": "5000000",
    "suspicious_auto_reject": "1",
    "min_video_duration_sec": "10",
    "view_velocity_threshold": "15000",
    "engagement_threshold_ratio": "0.0005",
    "strike_limit": "3",
    "global_required_code": "#BattleClub #BattleClubApp #BattleClubEarn",
    "verification_link": "",
    "home_youtube_link": "",
    "required_link_config": "all_public",
    "pending_expiry_action": "permanent_approve_zero_pay",
    "admin_session_timeout_sec": "3600",
    "support_link": "https://t.me/battleclubsupport",
    "group_link": "https://t.me/battleclubcreator",
    "global_user_theme": "success",
    "global_admin_theme": "primary",
    "super_admin_usernames": "battleclubsupport",
    "admins": "8145274317"
}

CRITERIA_FIELD_EXPLANATIONS = {
    "min_subs": {
        "title": "👥 ন্যূনতম সাবস্ক্রাইবার / ফলোয়ার (Subscriber / Follower Requirement)",
        "unit": "জন",
        "impact": "এটি পরিবর্তন করলে ইউজার যখন নতুন YouTube বা TikTok চ্যানেল ভেরিফিকেশন করবে, তখন তার চ্যানেলে কমপক্ষে এই সংখ্যক সাবস্ক্রাইবার/ফলোয়ার থাকতে হবে। এর কম থাকলে বট কারণ দেখিয়ে ভেরিফিকেশন রিজেক্ট করবে।"
    },
    "min_total_videos": {
        "title": "📹 ন্যূনতম পাবলিক ভিডিও সংখ্যা (Minimum Public Videos)",
        "unit": "টি ভিডিও",
        "impact": "এটি পরিবর্তন করলে ইউজারের চ্যানেল বা প্রোফাইলে মোট কমপক্ষে কতটি পাবলিক ভিডিও আপলোড করা থাকতে হবে তা নির্ধারিত হবে। নতুন বা খালি চ্যানেল আটকানোর জন্য এটি ব্যবহৃত হয়।"
    },
    "qualifying_videos": {
        "title": "🎬 ন্যূনতম যোগ্যতা ভিডিও সংখ্যা (Required Qualified Videos)",
        "unit": "টি যোগ্য ভিডিও",
        "impact": "এটি পরিবর্তন করলে ইউজারের পাবলিক ভিডিওগুলোর মধ্যে কমপক্ষে কয়টি ভিডিওতে নির্ধারিত টার্গেট ভিউ (min_views) থাকতে হবে তা ঠিক হবে।"
    },
    "min_views": {
        "title": "👁️ প্রতিটি যোগ্য ভিডিওর ন্যূনতম ভিউ শর্ত (Minimum Views Per Qualified Video)",
        "unit": "ভিউ",
        "impact": "এটি পরিবর্তন করলে চ্যানেল ভেরিফিকেশনের সময় প্রতিটি যোগ্য ভিডিওতে কমপক্ষে কত ভিউ থাকতে হবে (যেমন ৩টি ভিডিওতে ১,০০০ করে ভিউ) তা সাথে সাথে আপডেট হবে।"
    },
    "verification_link": {
        "title": "🔗 নির্ধারিত ভেরিফিকেশন লিংক (Mandatory Verification Link alongside Code)",
        "unit": "লিংক",
        "impact": "এখানে একটি নির্দিষ্ট Verification Link বসালে এবং Required Link Configuration চালু (ON) থাকলে ইউজারকে তার YouTube Description বা TikTok Bio-তে এবং ভিডিওর Title/Description/Comment-এ বাধ্যতামূলক র‍্যান্ডম ইউনিক কোডের (BC-XXXXXX) পাশাপাশি এই লিংকটিও যুক্ত রাখতে হবে (লিংক কখনোই ইউনিক কোডের বিকল্প নয়)। খালি করতে চাইলে none লিখুন।"
    },
    "max_accounts": {
        "title": "📱 সর্বোচ্চ অ্যাকাউন্ট যুক্ত করার লিমিট (Max Accounts Limit)",
        "unit": "টি অ্যাকাউন্ট",
        "impact": "এটি পরিবর্তন করলে একজন ইউজার '➕ নতুন অ্যাকাউন্ট যোগ করুন' অপশন থেকে একটি প্ল্যাটফর্মে সর্বোচ্চ কয়টি ভেরিফাইড চ্যানেল যুক্ত করতে পারবে তা নির্ধারিত হবে।"
    },
    "min_initial_views": {
        "title": "🎯 প্রথম পেমেন্টের টার্গেট ভিউ (First View Target)",
        "unit": "ভিউ",
        "impact": "এটি পরিবর্তন করলে সাবমিট করা ভিডিওতে কত ভিউ পূর্ণ হলে ইউজার প্রথম পেমেন্ট পাবে এবং ভিডিওটি Pending থেকে Bot Approved-এ যাবে তা নির্ধারিত হবে। এই ভিউ পূর্ণ হওয়ার আগে ০ টাকা যোগ হবে।"
    },
    "rate_per_1k": {
        "title": "💸 প্রথম টার্গেট ভিউ পূরণে পেমেন্ট (First Target Payment)",
        "unit": "টাকা",
        "impact": "এটি পরিবর্তন করলে ইউজারের সাবমিট করা ভিডিওতে প্রথম টার্গেট ভিউ (যেমন ১,০০০ ভিউ) পূর্ণ হওয়ার সাথে সাথে তার ব্যালেন্সে কত টাকা যোগ হবে তা নির্ধারিত হবে।"
    },
    "step_size": {
        "title": "🔢 পরবর্তী ভিউ স্টেপ সাইজ (Next View Step)",
        "unit": "ভিউ",
        "impact": "এটি পরিবর্তন করলে প্রথম টার্গেট ভিউ পূর্ণ হওয়ার পর পরবর্তী প্রতি কত ভিউ বৃদ্ধিতে (যেমন প্রতি ২০০ ভিউ) ইউজারের একাউন্টে অতিরিক্ত টাকা যোগ হবে তা নির্ধারিত হবে।"
    },
    "every_200_views_payment": {
        "title": "💵 প্রতি স্টেপ ভিউ বৃদ্ধিতে পেমেন্ট (Payment Per Next Step)",
        "unit": "টাকা",
        "impact": "এটি পরিবর্তন করলে প্রথম টার্গেট ভিউয়ের পর প্রতি স্টেপ (যেমন প্রতি ২০০ ভিউ) পূর্ণ হলে ইউজারের একাউন্টে কত টাকা করে যোগ হবে তা নির্ধারিত হবে।"
    },
    "earning_duration_days": {
        "title": "📅 ভিডিওর ভিউ কাউন্ট মেয়াদ (View Counting Duration)",
        "unit": "দিন",
        "impact": "এটি পরিবর্তন করলে একটি ভিডিও সাবমিট করার পর মোট কতদিন পর্যন্ত সেটির ভিউ গণনা করে টাকা যোগ করা হবে তা ঠিক হবে। এই দিন শেষ হলেই চূড়ান্ত পাওনা টাকা যোগ করে ভিডিওটি স্বয়ংক্রিয়ভাবে Permanent Approved হয়ে যাবে এবং আর কোনো ভিউ বা টাকা যোগ হবে না।"
    },
    "qualification_window_hours": {
        "title": "⏳ পেন্ডিং ম্যাপ / পেন্ডিং ভিডিওর সময়সীমা (Pending Map / Pending Video Duration)",
        "unit": "ঘণ্টা",
        "impact": "Pending Map হলো নতুন সাবমিট করা ভিডিও কতদিন বা কত ঘণ্টা পর্যন্ত Pending অবস্থায় প্রথম ভিউ টার্গেট (যেমন ১,০০০ ভিউ) পূরণের জন্য অপেক্ষা করবে তার সময়সীমা। উদাহরণস্বরূপ ৫ দিন (১২০ ঘণ্টা) নির্ধারণ করা থাকলে, এই সময়ের মধ্যে ন্যূনতম ভিউ পূরণ হলে ভিডিওটি Bot Approved হবে; আর সময় শেষ হয়ে গেলেও ভিউ পূরণ না হলে ভিডিওটি স্বয়ংক্রিয়ভাবে Rejected হয়ে যাবে এবং তার View Checking বন্ধ হয়ে যাবে।"
    },
    "submission_window_hours": {
        "title": "📤 ভিডিও পাবলিক হওয়ার পর সাবমিট সময়সীমা (Video Submission Time Limit)",
        "unit": "ঘণ্টা",
        "impact": "এটি পরিবর্তন করলে চ্যানেলে ভিডিও পাবলিক করার পর সর্বোচ্চ কত ঘণ্টার (যেমন ৭২ ঘণ্টা) মধ্যে বটে লিংক সাবমিট করতে হবে তা ঠিক হবে। এই সময় পার হয়ে গেলে পুরাতন ভিডিও সাবমিট নিলে বট সাথে সাথে কারণ দেখিয়ে রিজেক্ট করে দেবে।"
    },
    "max_payable_views": {
        "title": "🔒 সর্বোচ্চ পেমেন্টযোগ্য ভিউ ক্যাপ (Maximum View Cap)",
        "unit": "ভিউ",
        "impact": "এটি পরিবর্তন করলে একটি ভিডিওতে সর্বোচ্চ কত ভিউ পর্যন্ত (যেমন ৫০ লাখ = ৫০০০০০০ ভিউ) টাকা দেওয়া হবে তা ঠিক হবে। ভিডিওর ভিউ এই সীমায় পৌঁছালে চূড়ান্ত পেমেন্ট যোগ করে সাথে সাথে ভিডিওটি Permanent Approved হয়ে যাবে এবং এর উপরের ভিউয়ের জন্য আর কোনো টাকা যোগ হবে না।"
    }
}

SETTING_FIELD_EXPLANATIONS = {
    "first_1000_views_payment": "সাবমিট করা ভিডিওতে প্রথম টার্গেট ভিউ (যেমন ১,০০০ ভিউ) পূর্ণ হলে ইউজারের ব্যালেন্সে কত টাকা যোগ হবে তা নির্ধারণ করে।",
    "rate_per_1k": "সাবমিট করা ভিডিওতে প্রথম ১,০০০ ভিউ পূর্ণ হলে ইউজারের ব্যালেন্সে কত টাকা যোগ হবে তা নির্ধারণ করে।",
    "every_200_views_payment": "প্রথম টার্গেট ভিউ পূর্ণ হওয়ার পর পরবর্তী প্রতি স্টেপ ভিউ (যেমন প্রতি ২০০ ভিউ) পূর্ণ হলে কত টাকা করে ব্যালেন্সে যোগ হবে তা নির্ধারণ করে।",
    "view_step_size": "প্রথম টার্গেট ভিউয়ের পর প্রতি কত ভিউ অন্তর অন্তর ইউজারের একাউন্টে টাকা যোগ হবে (যেমন ২০০ ভিউ) তা নির্ধারণ করে।",
    "min_initial_views": "ভিডিও সাবমিট করার পর ন্যূনতম কত ভিউ পূর্ণ না হওয়া পর্যন্ত কোনো টাকা যোগ হবে না (Pending থাকবে) এবং পূর্ণ হলেই ১ম পেমেন্ট পাবে তা নির্ধারণ করে।",
    "max_payable_views": "একটি ভিডিওতে সর্বোচ্চ কত ভিউ পর্যন্ত (ডিফল্ট ৫০ লাখ = ৫০০০০০০) ভিউ গণনা ও পেমেন্ট করা হবে তা নির্ধারণ করে। এর উপরে ভিউ গেলেই ভিডিওটি সাথে সাথে Permanent Approved হয়ে যাবে।",
    "earning_duration_days": "ভিডিও সাবমিট করার পর সর্বোচ্চ কতদিন পর্যন্ত ভিউ গণনা চলবে (যেমন ৫ দিন) তা নির্ধারণ করে। এই সময় শেষ হলেই ভিডিওটি Permanent Approved হয়ে যাবে এবং আর ভিউ গণনা হবে না।",
    "qualification_window_hours": "Pending Map / Pending Video Duration: নতুন সাবমিট করা Pending ভিডিও কত ঘণ্টার মধ্যে (যেমন ৫ দিন = ১২০ ঘণ্টা) প্রথম টার্গেট ভিউ পূরণ করতে হবে তা নির্ধারণ করে। নির্ধারিত সময়ের মধ্যে ভিউ পূরণ না হলে ভিডিওটি Rejected হবে এবং View Checking বন্ধ হয়ে যাবে।",
    "submission_window_hours": "ইউটিউব বা টিকটকে ভিডিও পাবলিক করার পর সর্বোচ্চ কত ঘণ্টার মধ্যে বটে লিংক সাবমিট করতে হবে (যেমন ৭২ ঘণ্টা) তা নির্ধারণ করে। এর পরে সাবমিট করলে কারণসহ রিজেক্ট হবে।",
    "enforce_72h_rule": "এটি চালু (ON) থাকলে নির্ধারিত সময়ের (যেমন ৭২ ঘণ্টা) আগের পুরাতন পাবলিক ভিডিও কেউ সাবমিট করতে পারবে না।",
    "view_checking_interval_sec": "বট কত সেকেন্ড পর পর স্বয়ংক্রিয়ভাবে সব চলমান ও পেন্ডিং ভিডিওর নতুন ভিউ, ভেরিফিকেশন কোড/লিংক, হ্যাশট্যাগ এবং অর্গানিক স্ট্যাটাস চেক করবে তা নির্ধারণ করে (ডিফল্ট ৩৬০০ সেকেন্ড = ১ ঘণ্টা)।",
    "verification_interval_sec": "বট কত সেকেন্ড পর পর ব্যাকগ্রাউন্ডে ভেরিফাইড অ্যাকাউন্টের বায়ো কোড ও অনুমোদিত ভিডিওর কোড রি-চেক করবে তা নির্ধারণ করে (ডিফল্ট ৩৬০০ সেকেন্ড = ১ ঘণ্টা)।",
    "user_session_timeout_sec": "কোনো ইউজার কত সেকেন্ড নিষ্ক্রিয় থাকলে নিরাপত্তার স্বার্থে স্বয়ংক্রিয়ভাবে লগআউট হয়ে যাবে তা নির্ধারণ করে।",
    "min_video_duration_sec": "সাবমিট করা স্পন্সর ভিডিও কমপক্ষে কত সেকেন্ড দীর্ঘ হতে হবে তা নির্ধারণ করে। এর ছোট ভিডিও সাবমিট করলে রিজেক্ট হবে।",
    "view_velocity_threshold": "প্রতি ঘণ্টায় কী পরিমাণ অস্বাভাবিক ভিউ স্পাইক হলে বট সেটিকে ফেক/বট প্যানেল ভিউ হিসেবে সন্দেহ করবে তা নির্ধারণ করে।",
    "engagement_threshold_ratio": "ভিউয়ের বিপরীতে ন্যূনতম কত শতাংশ (Ratio) লাইক/কমেন্ট না থাকলে বট সেটিকে ফেক ভিউ হিসেবে শনাক্ত করবে তা নির্ধারণ করে।",
    "strike_limit": "একজন ইউজার পরপর কতবার ডুপ্লিকেট বা অন্য চ্যানেলের ভুল ভিডিও সাবমিট করলে তার একাউন্ট স্বয়ংক্রিয়ভাবে ফ্রিজ/ইনঅ্যাক্টিভ হবে তা নির্ধারণ করে।",
    "min_withdraw": "একজন ইউজারের অ্যাকাউন্টে ন্যূনতম কত টাকা থাকলে Withdraw Request করতে পারবে (যেমন ১০০ টাকা) তা নির্ধারণ করে। এর কম ব্যালেন্স থাকলে নোটিফিকেশন ও স্ট্যাটাস মেসেজ দেখাবে।",
    "max_daily_wd_count": "একজন ইউজার একদিনে (২৪ ঘণ্টায়) সর্বোচ্চ কতবার উইথড্র রিকোয়েস্ট পাঠাতে পারবে (Daily Withdraw Request Count) তা নির্ধারণ করে।",
    "max_daily_wd_amount": "একজন ইউজার একদিনে (২৪ ঘণ্টায়) সর্বমোট সর্বোচ্চ কত টাকা উইথড্র রিকোয়েস্ট দিতে পারবে (Daily Withdraw Limit) তা নির্ধারণ করে।",
    "max_single_withdraw": "একবারে একটি সিঙ্গেল উইথড্র রিকোয়েস্টে সর্বোচ্চ কত টাকা উত্তোলন করা যাবে (Maximum Withdraw Amount) তা নির্ধারণ করে।",
    "wd_eta_text": "উইথড্র রিকোয়েস্ট দেওয়ার পর ইউজারকে পেমেন্ট পাওয়ার যে সম্ভাব্য সময় (যেমন: ১২ থেকে ২৪ ঘণ্টার মধ্যে) দেখানো হয় তা নির্ধারণ করে।",
    "ref_bonus": "সফলভাবে কাউকে রেফার করলে রেফারকারী ইউজার প্রতি রেফারে কত টাকা Referral Reward পাবে তা নির্ধারণ করে।",
    "redeem_bonus": "নতুন ইউজার অন্য কারো রেফার কোড রিডিম করলে সাথে সাথে কত টাকা Redeem Reward পাবে তা নির্ধারণ করে।",
    "max_daily_referrals": "একজন ইউজার দৈনিক সর্বোচ্চ কতবার Referral করতে পারবে (Daily Referral Limit) তা নির্ধারণ করে।",
    "ref_unlock_on_first_video": "এটি চালু (ON) থাকলে নতুন ইউজার একাউন্ট খোলার সাথে সাথে রেফার বোনাস আনলক হবে না; বরং তার ১ম স্পন্সর ভিডিও অ্যাপ্রুভ হলেই রেফার ও রিডিম বোনাস আনলক হবে। বন্ধ (OFF) থাকলে ভেরিফিকেশনের সাথে সাথেই বোনাস যোগ হবে।",
    "suspicious_auto_reject": "এটি চালু (ON) থাকলে বট ফেক বা প্যানেল ভিউ শনাক্ত করার সাথে সাথে ভিডিওটি অটো-রিজেক্ট করবে এবং অর্জিত টাকা কেটে নেবে। বন্ধ (OFF) থাকলে অটো-রিজেক্ট না করে পেমেন্ট ব্লক রেখে অ্যাডমিন ম্যানুয়াল রিভিউতে পাঠাবে।",
    "verification_link": "ভেরিফিকেশন কোডের পরিবর্তে বা পাশাপাশি ইউজার তার YouTube Description বা TikTok Bio-তে এবং ভিডিওতে যে নির্দিষ্ট Verification Link বসাতে পারবে তা নির্ধারণ করে।",
    "require_app_uid_in_video": "এটি চালু (1) করলে ইউজারের সাবমিট করা ভিডিওর Title, Description বা Comment-এ ইউনিক কোডের পাশাপাশি ইউজারের Battle Club UID থাকা বাধ্যতামূলক হবে।"
}

DEFAULT_BUTTON_LABELS = {
    # User Home & Settings Hub Buttons
    "u_dashboard": "📊 ড্যাশবোর্ড",
    "u_profile": "👤 প্রোফাইল",
    "u_submit": "📹 ভিডিও সাবমিট",
    "u_my_videos": "🎬 আমার ভিডিওসমূহ",
    "u_withdraw": "💸 উইথড্র রিকোয়েস্ট",
    "u_wd_list": "📋 উইথড্র লিস্ট",
    "u_history": "💳 পেমেন্ট লিস্ট",
    "u_link_more": "➕ নতুন অ্যাকাউন্ট যোগ করুন",
    "u_leaderboard": "🏆 লিডারবোর্ড",
    "u_settings_hub": "⚙️ সেটিংস (Settings)",
    "u_referral": "🎁 রেফার করুন (Refer)",
    "u_redeem": "🎟️ রেফার রিডিম (Redeem)",
    "u_activity": "📜 একাউন্ট অ্যাক্টিভিটি",
    "u_pwd_change": "🔑 পাসওয়ার্ড চেঞ্জ",
    "u_color": "🎨 বাটন কালার",
    "u_lang": "🌐 ভাষা পরিবর্তন (Language)",
    "u_bottom_toggle": "⌨️ নিচের মেনু মোড (Bottom Menu)",
    "u_delete_acc": "🗑️ একাউন্ট ডিলিট",
    "u_logout": "🔒 লগ আউট",
    "u_how_to_work": "🎥 কিভাবে কাজ করবেন",
    "u_support": "💬 সাপোর্ট",
    "u_group": "👥 গ্রুপ জয়েন",

    # User Sub-Page & Navigation Buttons (Profile, Dashboard, Submit, Withdraw, My Videos, Onboarding)
    "u_back_home": "🔙 হোমপেজে ফিরে যান (Back to Home)",
    "u_back_dashboard": "📊 ড্যাশবোর্ডে ফিরে যান (Back to Dashboard)",
    "u_back_prev": "🔙 আগের পেজে ফিরে যান (Back)",
    "u_cancel": "✖️ বাতিল করুন (Cancel)",
    "u_plat_youtube": "📺 YouTube",
    "u_plat_tiktok": "🎵 TikTok",
    "u_plat_both": "🌟 ২টি প্ল্যাটফর্মই সিলেক্ট করুন (YouTube & TikTok)",
    "u_plat_confirm": "🚀 সিলেকশন কনফার্ম করুন",
    "u_prof_change_name": "✏️ নাম পরিবর্তন করুন (Change Name)",
    "u_prof_change_acc_name": "✏️ নিজের অ্যাকাউন্টের নাম পরিবর্তন (Change Account Name)",
    "u_prof_change_uid": "🆔 Battle Club UID পরিবর্তন (Change Battle Club UID)",
    "u_prof_change_ch_name": "📺 চ্যানেল নাম পরিবর্তন করুন",
    "u_prof_change_wd": "📱 উইথড্র নাম্বার পরিবর্তন / যুক্ত করুন (Change Withdraw Number)",
    "u_wd_bkash": "🌸 বিকাশ (bKash)",
    "u_wd_nagad": "🍊 নগদ (Nagad)",
    "u_wd_rocket": "🚀 রকেট (Rocket)",
    "u_wd_uid": "🎮 Battle Club App UID",
    "u_wd_other": "🔄 অন্যান্য মাধ্যম (Another Method)",
    "u_myv_all": "📋 সব ভিডিও (All Videos)",
    "u_myv_pending": "⏳ পেন্ডিং ভিডিও (Pending Videos)",
    "u_myv_bot_app": "🤖 বট অ্যাপ্রুভ (Bot Approved)",
    "u_myv_adm_app": "👑 অ্যাডমিন অ্যাপ্রুভ (Admin Approved)",
    "u_myv_perm_app": "🔒 পার্মানেন্ট অ্যাপ্রুভ (Permanent Approved)",
    "u_myv_rejected": "❌ রিজেক্টেড ভিডিও (Rejected Videos)",

    # Admin Main Panel Buttons
    "a_metrics": "📊 ড্যাশবোর্ড ও মেট্রিক্স",
    "a_wd_reports": "📋 উইথড্র রিপোর্ট",
    "a_pending_vids": "⏳ পেন্ডিং (Pending)",
    "a_bot_approve": "🤖 বট অ্যাপ্রুভ",
    "a_admin_approve": "👑 অ্যাডমিন অ্যাপ্রুভড ভিডিও",
    "a_perm_approve": "🔒 PERMANENT APPROVE",
    "a_rejected_vids": "❌ রিজেক্টেড ভিডিও ও রিভার্সাল",
    "a_trash": "🗑️ Trash / রিসাইকেল বিন",
    "a_user_list": "👥 ইউজার লিস্ট ও হিস্ট্রি",
    "a_all_vids": "🎬 সকল সাবমিটকৃত ভিডিও",
    "a_traffic_hub": "🌐 ট্রাফিক সোর্স ও এক্সটার্নাল লিংক (YT/TT)",
    "a_broadcast": "📢 ব্রডকাস্ট মেসেজ",
    "a_settings": "⚙️ কন্ট্রোল সেটিংস হাব",
    "a_adv_settings": "🛠️ অ্যাডভান্সড সেটিংস (Advanced Settings)",
    "a_bottom_toggle": "⌨️ অ্যাডমিন বটম মেনু মোড",
    "a_logout": "🔒 অ্যাডমিন লগ আউট",
    "a_back_admin": "🔙 অ্যাডমিন ড্যাশবোর্ডে ফিরে যান",
    "a_user_home": "🏠 ইউজার হোমপেজ (User Home)",
    "a_super_admin_panel": "👑 সুপার এডমিন প্যানেল",

    # Admin Control Settings, General Settings & Advanced Settings Buttons
    "a_plat_settings": "🌐 মাল্টি-প্ল্যাটফর্ম ও ট্রাফিক সেটিংস (YT/TT)",
    "a_rate_settings": "📈 ভিউ রেট, পেন্ডিং ম্যাপ ও মেয়াদ সেটিংস",
    "a_wd_settings": "💸 উইথড্র লিমিট সেটিংস",
    "a_ref_settings": "🎁 রেফার ও রিডিম সেটিংস",
    "a_antifraud_settings": "🛡️ অ্যান্টি-ফ্রড ও অর্গানিক রিস্ক সেটিংস",
    "a_general_settings": "⚙️ জেনারেল সেটিংস (General Settings)",
    "a_man_ver": "🛠️ ম্যানুয়াল প্রসেসিং ও নাম্বার চেঞ্জ র‍্যান্ডম কোড",
    "a_mvr_gen": "🔑 নতুন র‍্যান্ডম কোড জেনারেট করুন (MVR)",
    "a_hashtag_yt": "🔐 হ্যাশট্যাগ ও ভেরিফিকেশন/ভিডিও লিংক সেটআপ",
    "a_support_group": "💬 সাপোর্ট ও গ্রুপ লিংক পরিবর্তন",
    "a_export_hub": "📂 ডেটাবেস CSV এক্সপোর্ট ও লেজার হিস্ট্রি",
    "a_export": "📥 ডেটাবেস CSV ফাইল ডাউনলোড করুন",
    "a_fin_history": "📜 ফিন্যান্সিয়াল লেজার ও অডিট হিস্ট্রি",
    "a_admin_guide": "🗺️ অ্যাডমিন গাইড ও ম্যাপ",
    "a_cmd_list": "⌨️ কমান্ড ও শর্টকাট তালিকা",
    "a_btn_editor": "🎛️ Button Name & Premium Custom Emoji Editor",
    "a_msg_hub": "✏️ Message, Status & Premium Custom Emoji Editor",
    "a_btn_pos_editor": "📐 Button Position Change / বাটনের জায়গা পরিবর্তন করুন",
    "a_tutorial_vid": "🎥 ভিডিও লিংক (How to Work Video)",
    "a_ext_open_video": "🔗 Open Video",
    "a_ext_reset": "🔄 Reset",
    "a_ext_accept": "✅ Accept / Admin Approve"
}

DEFAULT_BUTTON_EMOJIS = {k: "" for k in DEFAULT_BUTTON_LABELS}

MAIN_ADMIN_BUTTON_KEYS = (
    "a_metrics",
    "a_wd_reports",
    "a_pending_vids",
    "a_bot_approve",
    "a_admin_approve",
    "a_perm_approve",
    "a_rejected_vids",
    "a_trash",
    "a_user_list",
    "a_all_vids",
    "a_traffic_hub",
    "a_broadcast",
    "a_settings",
    "a_adv_settings",
    "a_bottom_toggle",
    "a_logout",
)

SETTINGS_ONLY_BUTTON_KEYS = (
    "a_msg_hub",
    "a_btn_editor",
    "a_btn_pos_editor",
    "a_tutorial_vid",
    "a_export",
    "a_fin_history",
    "a_admin_guide",
    "a_cmd_list",
)

DEFAULT_LAYOUTS = {
    "user_home": [
        ["u_dashboard", "u_profile"],
        ["u_submit", "u_link_more"],
        ["u_my_videos"],
        ["u_withdraw", "u_wd_list"],
        ["u_history", "u_leaderboard"],
        ["u_how_to_work"],
        ["u_settings_hub", "u_logout"],
        ["u_support", "u_group"]
    ],
    "user_settings_hub": [
        ["u_referral", "u_redeem"],
        ["u_activity", "u_pwd_change"],
        ["u_color", "u_lang"],
        ["u_bottom_toggle"],
        ["u_delete_acc"],
        ["u_back_home"]
    ],
    "user_dashboard": [
        ["u_leaderboard"],
        ["u_logout", "u_back_home"]
    ],
    "user_profile": [
        ["u_prof_change_name", "u_prof_change_wd"],
        ["u_link_more", "u_pwd_change"],
        ["u_how_to_work"],
        ["u_referral", "u_redeem"],
        ["u_back_home"]
    ],
    "admin_home": [
        ["a_metrics"],
        ["a_wd_reports"],
        ["a_pending_vids", "a_bot_approve"],
        ["a_admin_approve", "a_perm_approve"],
        ["a_rejected_vids", "a_trash"],
        ["a_user_list", "a_all_vids"],
        ["a_traffic_hub"],
        ["a_broadcast"],
        ["a_settings", "a_adv_settings"],
        ["a_bottom_toggle", "a_logout"]
    ],
    "admin_settings_hub": [
        ["a_plat_settings"],
        ["a_rate_settings"],
        ["a_wd_settings"],
        ["a_ref_settings"],
        ["a_antifraud_settings"],
        ["a_general_settings"],
        ["a_adv_settings"],
        ["a_back_admin"]
    ],
    "admin_general_settings": [
        ["a_man_ver"],
        ["a_mvr_gen"],
        ["a_hashtag_yt"],
        ["a_support_group"],
        ["a_export_hub"],
        ["a_admin_guide"],
        ["a_cmd_list"],
        ["a_back_admin"]
    ]
}

SETTINGS_CONTROL_HUB_SUBMENUS = [
    ("🌐 মাল্টি-প্ল্যাটফর্ম ও ট্রাফিক সোর্স সেটিংস (YT/TT)", "adm_crit:hub", "primary"),
    ("📈 ভিউ রেট, পেন্ডিং ম্যাপ ও মেয়াদ সেটিংস", "adm_edit_rate_days", "success"),
    ("💸 উইথড্র লিমিট সেটিংস", "adm_wd_limit_hub", "primary"),
    ("🎁 রেফার ও রিডিম সেটিংস", "adm_edit_ref_hub", "success"),
    ("🛡️ অ্যান্টি-ফ্রড ও অর্গানিক রিস্ক সেটিংস", "adm_shub:antifraud", "danger"),
    ("⚙️ জেনারেল সেটিংস (General Settings)", "adm_gen_settings_hub", "primary"),
    ("🛠️ অ্যাডভান্সড সেটিংস (Advanced Settings)", "adm_adv_hub", "success"),
]

DEFAULT_MESSAGES = {
    'welcome_msg': '<tg-emoji emoji-id="5195448447062251797">👋</tg-emoji> <b>স্বাগতম BATTLE CLUB CREATORS-এ!</b> <tg-emoji emoji-id="5317026657540780588">🎉</tg-emoji>\n\n<tg-emoji emoji-id="6237905016313615867">🌟</tg-emoji> আপনার ক্রিয়েটর জার্নি শুরু হোক BATTLE CLUB-এর সাথে।\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <b>নিচের মেনু থেকে আপনার পছন্দের অপশনটি নির্বাচন করুন এবং আমাদের সাথে এগিয়ে যান।</b> <tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji>\n\n<tg-emoji emoji-id="5406926593698312391">❤️</tg-emoji> ধন্যবাদ, আমাদের সাথে থাকার জন্য!',
    'notice_msg': '📢 <b>BATTLE CLUB | OFFICIAL NOTICE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 আমাদের স্পন্সরশিপ প্ল্যাটফর্মের সকল নিয়ম মেনে অর্গানিক ভিডিও সাবমিট করুন এবং নিয়মিত পেমেন্ট গ্রহণ করুন।',
    'notification_msg': '🔔 <b>BATTLE CLUB | NOTIFICATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{details}',
    'instruction_msg': '📘 <b>BATTLE CLUB | CREATOR INSTRUCTIONS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n১. প্রোফাইল বায়োতে ভেরিফিকেশন কোড বা নির্ধারিত লিংক যুক্ত রাখুন।\n২. প্রতিটি স্পন্সর ভিডিওতে ইউনিক কোড/লিংক এবং বাধ্যতামূলক হ্যাশট্যাগ ব্যবহার করুন।\n৩. ভিডিও পাবলিক করার নির্ধারিত সময়ের মধ্যে বটে লিংক সাবমিট করুন।',
    'user_settings_hub_msg': '⚙️ <b>BATTLE CLUB | USER SETTINGS HUB</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 ইউজার: <b>{user_label}</b>\n⌨️ বর্তমান মেনু মোড: <b>{menu_mode_status}</b>\n🌐 বর্তমান ভাষা: <b>{lang_status}</b>\n🎨 বাটন কালার থিম: <b>{color_status}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 <b>নিচের অপশনগুলো থেকে আপনার রেফারেল, পাসওয়ার্ড, বাটন কালার, ভাষা, মেনু মোড বা অ্যাকাউন্ট সেটিংস পরিচালনা করুন:</b>',
    'login_password_prompt_msg': '<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>আপনার অ্যাকাউন্ট সুরক্ষিত আছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> লগইন করতে নিচে আপনার <b>পাসওয়ার্ডটি</b> লিখে পাঠান:',
    'forgot_password_support_msg': '<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>একাধিকবার ভুল পাসওয়ার্ড প্রদান করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার পাসওয়ার্ড যদি মনে না থাকে, তবে নিচের বাটনে ক্লিক করে সরাসরি অ্যাডমিনের সাথে কথা বলে আপনার পাসওয়ার্ড চেঞ্জ করে নিন।\n\n<tg-emoji emoji-id="5303138782004924588">💬</tg-emoji> সাপোর্ট লিংক: {support_link}',
    'login_failed_support_msg': '<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>একাধিকবার ({attempt_count} বার) ভুল পাসওয়ার্ড প্রদান করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার পাসওয়ার্ড যদি মনে না থাকে, তবে নিচের বাটনে ক্লিক করে সরাসরি অ্যাডমিনের সাথে কথা বলে আপনার পাসওয়ার্ড চেঞ্জ করে নিন।\n\n<tg-emoji emoji-id="5303138782004924588">💬</tg-emoji> সাপোর্ট লিংক: {support_link}',
    'user_logout_confirm_msg': '<tg-emoji emoji-id="5231302159739395058">🔒</tg-emoji> <b>আপনার অ্যাকাউন্ট সম্পূর্ণভাবে লগআউট করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nপুনরায় লগইন করতে <code>/start</code> চাপুন অথবা যেকোনো মেসেজ পাঠিয়ে আপনার পাসওয়ার্ড দিন।',
    'reg_step1_yt_msg': '<tg-emoji emoji-id="5195448447062251797">👋</tg-emoji> <b>স্বাগতম BATTLE CLUB Sponsorship Platform-এ!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5463274047771000031">😵</tg-emoji> <b>আপনার প্ল্যাটফর্ম, আপনার স্পন্সরশিপ!</b>\n\nBATTLE CLUB অ্যাপের মাধ্যমে আপনি জনপ্রিয় ২টি সোশ্যাল মিডিয়া প্ল্যাটফর্মে (YouTube এবং TikTok) স্পন্সরশিপের সুযোগ পাবেন।\n\n<tg-emoji emoji-id="5282843764451195532">🖥</tg-emoji> <b>আমাদের স্পন্সরশিপ প্ল্যাটফর্মগুলো হলো:</b>\n\n<tg-emoji emoji-id="6266910244723498649">😍</tg-emoji> YouTube\n\n<tg-emoji emoji-id="6266799245588701516">😍</tg-emoji> TikTok\n\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>আপনার কাছে কোন কোন প্ল্যাটফর্মে অ্যাকাউন্ট বা চ্যানেল রয়েছে?</b>\n\nআপনার যেসব প্ল্যাটফর্ম রয়েছে, সেগুলো নির্বাচন করে কনফার্ম করুন।\n\n<tg-emoji emoji-id="6217685925191750376">✅</tg-emoji> ২টি প্ল্যাটফর্ম থাকলে ২টিই সিলেক্ট করুন।\n\n<tg-emoji emoji-id="6217685925191750376">✅</tg-emoji> ১টি থাকলে ১টি সিলেক্ট করুন।\n\n<b>আপনার সুবিধামতো YouTube অথবা TikTok বা উভয় প্ল্যাটফর্ম নির্বাচন করতে পারবেন।</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji> <b>BATTLE CLUB-এর সঙ্গে এগিয়ে যান স্পন্সরশিপের নতুন সম্ভাবনার পথে!</b>',
    'reg_code_prompt_msg': '<tg-emoji emoji-id="5463274047771000031">😵</tg-emoji> <b>BATTLE CLUB | ACCOUNT VERIFICATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>ভেরিফিকেশন ধাপ ({platform_title})</b>\nআপনার চ্যানেল বা প্রোফাইলটি যে সম্পূর্ণ আপনার নিজস্ব, তা নিশ্চিত করার জন্য নিচের <b>র\u200d্যান্ডম ভেরিফিকেশন কোডটি</b> (অথবা নির্ধারিত লিংক থাকলে সেটি) ব্যবহার করুন।\n\n<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>ধাপ ১: ভেরিফিকেশন কোড কপি করুন</b>\n\nনিচের কোডটি কপি করে আপনার <b>{platform_title}</b> অ্যাকাউন্টের Bio / Description-এ সুন্দরভাবে যুক্ত করুন এবং সেভ করুন।\n<pre>{bio_code}</pre>\n\n<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>বাধ্যতামূলক ভেরিফিকেশন শর্তাবলি</b>\n\nআপনার অ্যাকাউন্টটি ভেরিফাই হওয়ার জন্য নিচের সব শর্ত পূরণ করতে হবে।\n\n<tg-emoji emoji-id="5197397670724912036">1️⃣</tg-emoji> <b>Verification Code &amp; Link:</b> আপনার Bio / Description-এ অবশ্যই উপরে দেওয়া নির্দিষ্ট ভেরিফিকেশন কোডটি থাকতে হবে (এবং ভেরিফিকেশন লিংক চালু থাকলে কোডের পাশাপাশি নির্ধারিত লিংকটিও থাকতে হবে)।\n\n<tg-emoji emoji-id="5197250993296785376">2️⃣</tg-emoji> <b>Minimum Subscribers/Followers:</b> আপনার চ্যানেল বা প্রোফাইলে কমপক্ষে <b>{min_subs}+ সাবস্ক্রাইবার / ফলোয়ার</b> থাকতে হবে।\n\n<tg-emoji emoji-id="5195203805725084605">3️⃣</tg-emoji> <b>Public &amp; Qualifying Videos:</b> আপনার অ্যাকাউন্টে কমপক্ষে <b>{min_total_vids}+ পাবলিক ভিডিও</b> থাকতে হবে এবং যেকোনো <b>{qual_vids}টি যোগ্য ভিডিওতে</b> প্রতিটিতে কমপক্ষে <b>{min_views}+ ভিউ</b> থাকতে হবে (মোট দৃশ্যমান ভিউ কমপক্ষে <b>{total_req_views}+</b>)।\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5271604874419647061">🔗</tg-emoji> <b>ধাপ ২: প্রোফাইল / চ্যানেল লিংক জমা দিন</b>\n\nউপরের সব শর্ত পূরণ করার পর \n\nআপনার <b>{platform_title} প্রোফাইল অথবা চ্যানেলের লিংকটি</b> নিচে পেস্ট করে পাঠান।\n\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>মনে রাখবেন:</b> ভেরিফিকেশন সম্পন্ন না হওয়া পর্যন্ত Bio / Description থেকে কোডটি সরাবেন না।\n\n<tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji> <b>BATTLE CLUB-এর সঙ্গে স্পন্সরশিপের পরবর্তী ধাপে এগিয়ে যান!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<tg-emoji emoji-id="5267031043487051884">❤️</tg-emoji> <b>BATTLE CLUB | SPONSORSHIP PLATFORM</b>',
    'reg_fail_eligibility_msg': '<tg-emoji emoji-id="5438630285635757876">🔠</tg-emoji> <b>BATTLE CLUB | VERIFICATION REJECTED</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>দুঃখিত! আপনার অ্যাকাউন্টের ভেরিফিকেশন সম্পূর্ণ হয়নি।</b>\n\n<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>আপনার চ্যানেল/প্রোফাইলের বর্তমান তথ্য ও শর্ত যাচাই রিপোর্ট:</b>\n{reason}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>ভেরিফিকেশনের জন্য প্রয়োজনীয় শর্তাবলি:</b>\n\n<tg-emoji emoji-id="5197397670724912036">1️⃣</tg-emoji> <b>Minimum Subscribers/Followers:</b> কমপক্ষে <b>{min_subs}+ সাবস্ক্রাইবার / ফলোয়ার</b>।\n<tg-emoji emoji-id="5197250993296785376">2️⃣</tg-emoji> <b>Qualifying Videos &amp; Views:</b> কমপক্ষে <b>{qual_vids}টি যোগ্যতা ভিডিওতে</b> মোট <b>{total_req_views}+ ভিউ</b>।\n<tg-emoji emoji-id="5195203805725084605">3️⃣</tg-emoji> <b>Verification Code / Link:</b> Bio / Description-এ নির্ধারিত ভেরিফিকেশন কোড বা লিংক।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5226702984204797593">🔄</tg-emoji> <b>সমস্যাটি সংশোধন করে পুনরায় চেষ্টা করুন অথবা সাপোর্টে কথা বলে ম্যানুয়াল ভেরিফিকেশন কোড নিন।</b>',
    'reg_uid_input_msg': '<tg-emoji emoji-id="6150059526222516756">👛</tg-emoji> <b>BATTLE CLUB | MANDATORY APP UID (ধাপ ১/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{verification_summary}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>প্রথমে আপনার Battle Club অ্যাপের UID প্রদান করুন (বাধ্যতামূলক):</b>\n\nআপনার <b>Battle Club অ্যাপের UID</b> অবশ্যই হ্যাশট্যাগসহ নির্ধারিত ফরম্যাটে (যেমন <code>#107</code> অথবা <code>#1007</code>) নিচে লিখে পাঠান।\n\n⚠️ <i>UID না দিয়ে পরবর্তী ধাপে যাওয়া যাবে না।</i>',
    'reg_payment_methods_select_msg': '<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji> <b>BATTLE CLUB | PAYMENT METHOD SELECTION (ধাপ ২/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{verification_summary}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>বিকাশ, নগদ ও রকেট পেমেন্ট মাধ্যম নির্বাচন করুন:</b>\n\nআপনি কোন কোন মাধ্যমে পেমেন্ট ও উইথড্র নিতে চান তা নিচের বাটন থেকে সিলেক্ট করুন:\n• চাইলে <b>১টি মাধ্যম</b> (যেমন শুধু বিকাশ) সিলেক্ট করতে পারেন।\n• চাইলে <b>২টি মাধ্যম</b> (যেমন বিকাশ ও নগদ) সিলেক্ট করতে পারেন।\n• চাইলে <b>৩টি মাধ্যমই</b> (বিকাশ, নগদ ও রকেট) একসঙ্গে সিলেক্ট করতে পারেন!\n\n📌 <i>যে কয়টি মাধ্যম সিলেক্ট করবেন, পরবর্তী ধাপে ঠিক সেই কয়টি মাধ্যমেরই নাম্বার (প্রতি মাধ্যমে ১টি করে) চাওয়া হবে।</i>',
    'reg_payment_number_input_msg': '<tg-emoji emoji-id="5404350824501491839">📞</tg-emoji> <b>{method_title} পেমেন্ট নাম্বার প্রদান করুন (ধাপ ২/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji> আপনার সচল <b>{method_title}</b> নাম্বারটি (<code>01XXXXXXXXX</code>) নিচে লিখে পাঠান:\n\nℹ️ <i>প্রতিটি পেমেন্ট মাধ্যমে ১টি করে নাম্বার সংরক্ষণ করা যাবে।</i>',
    'reg_name_input_msg': '<tg-emoji emoji-id="5188552176988858899">😎</tg-emoji> <b>আপনার অ্যাকাউন্টের নাম প্রদান করুন (ধাপ ৩/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> আপনার বট অ্যাকাউন্টের নাম (আপনার পূর্ণ নাম) নিচে লিখে পাঠান:',
    'reg_channel_name_input_msg': '<tg-emoji emoji-id="5287575882108522821">📺</tg-emoji> <b>{platform_title} অ্যাকাউন্টের নাম প্রদান করুন (ধাপ ৪/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> আপনার ভেরিফাই করা <b>{platform_title}</b> চ্যানেল বা অ্যাকাউন্টের নাম নিচে লিখে পাঠান:',
    'reg_password_input_msg': '<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> <b>শক্তিশালী পাসওয়ার্ড তৈরি করুন (ধাপ ৫/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> আপনার অ্যাকাউন্টের নিরাপত্তার জন্য একটি <b>Strong Password</b> (কমপক্ষে ৪ অক্ষর) নিচে লিখে পাঠান:',
    'reg_password_confirm_input_msg': '<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> <b>পাসওয়ার্ড পুনরায় নিশ্চিত করুন (ধাপ ৬/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔄 নিশ্চিতকরণের জন্য আপনার দেওয়া <b>একই পাসওয়ার্ডটি দ্বিতীয়বার</b> হুবহু লিখে পাঠান:',
    'reg_password_mismatch_msg': '❌ <b>দুটি পাসওয়ার্ড মেলেনি!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚠️ আপনার প্রথম ও দ্বিতীয়বার দেওয়া পাসওয়ার্ড এক হয়নি। অনুগ্রহ করে আবার নতুন করে একটি <b>Strong Password (ধাপ ৫/৭)</b> লিখে পাঠান:',
    'reg_complete_msg': '<tg-emoji emoji-id="5317026657540780588">🎉</tg-emoji> <b>অভিনন্দন! আপনার রেজিস্ট্রেশন সম্পন্ন হয়ে Dashboard Access চালু হয়েছে! (ধাপ ৭/৭)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="6150059526222516756">👛</tg-emoji> স্থায়ী Battle Club UID: <code>{app_uid}</code>\n<tg-emoji emoji-id="5404350824501491839">📞</tg-emoji> সংরক্ষিত পেমেন্ট নাম্বারসমূহ:\n<b>{payment_methods_summary}</b>\n<tg-emoji emoji-id="5224607267797606837">☄️</tg-emoji> প্রোফাইল বায়ো কোড: <code>{bio_code}</code>\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> পরবর্তী ভিডিওর ভেরিফাই কোড: <code>{unique_code}</code>',
    'profile_edit_hub_msg': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>প্রোফাইল ও পেমেন্ট তথ্য এডিট প্যানেল</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="6217685925191750376">✅</tg-emoji> <b>সরাসরি পরিবর্তনযোগ্য:</b>\n• আপনার অ্যাকাউন্টের নাম (<b>{name}</b>) এবং Battle Club অ্যাপের UID (<code>{app_uid}</code>) যেকোনো সময় সরাসরি এডিট করে আপডেট করতে পারবেন।\n\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>পেমেন্ট নাম্বার পরিবর্তন ও সংযোজন:</b>\n• বিকাশ, নগদ ও রকেটের প্রতি মাধ্যমে সর্বোচ্চ ১টি নাম্বার সংরক্ষণ করা যাবে। পুরোনো নাম্বার পরিবর্তন করতে অথবা নতুন মাধ্যমের নাম্বার যুক্ত করতে নিচের বাটন ব্যবহার করুন।',
    'profile_random_code_prompt_msg': '<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> <b>নিরাপত্তা যাচাই — অ্যাডমিন র\u200d্যান্ডম কোড প্রদান করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনি আপনার অ্যাকাউন্টের <b>{field_label}</b> পরিবর্তন করতে চাচ্ছেন।\n\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> এটি যে সত্যিই আপনার অ্যাকাউন্ট তা নিশ্চিত করতে সরাসরি অ্যাডমিনের সাথে যোগাযোগ করে একটি <b>র\u200d্যান্ডম জেনারেট কোড (BC-XXXXXX)</b> সংগ্রহ করুন এবং নিচে লিখে পাঠান।',
    'profile_random_code_verified_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>ভেরিফিকেশন সফল!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> এখন আপনার নতুন <b>{field_label}</b> নিচে লিখে পাঠান:',
    'withdraw_insufficient_balance_msg': '⚠️ <b>পর্যাপ্ত ব্যালেন্স নেই — উইথড্র লক রয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 আপনার বর্তমান Available Balance: <b>{current_balance} টাকা</b>\n📉 উইথড্র করার জন্য ন্যূনতম প্রয়োজন: <b>{min_withdraw} টাকা</b>\n🎯 উইথড্র আনলক করতে আরও প্রয়োজন: <b>{needed_amount} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💡 <i>আপনার অ্যাকাউন্টে নির্ধারিত <b>{min_withdraw} টাকা</b> ব্যালেন্স পূর্ণ হলেই স্বয়ংক্রিয়ভাবে Withdraw Request করার সুযোগ চালু হবে!</i>',
    'withdraw_other_way_platform_msg': '<tg-emoji emoji-id="5226702984204797593">🔄</tg-emoji> <b>অন্যান্য মাধ্যম (Another Method) — ধাপ ১/৩: মাধ্যমের নাম</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✍️ আপনি কোন মাধ্যমে টাকা নিতে চান? প্রথমে সেই <b>পেমেন্ট মাধ্যমের নাম</b> নিচে লিখে পাঠান (যেমন: <b>Upay, Bank, Rocket, bKash</b> ইত্যাদি):',
    'withdraw_other_way_method_name_prompt_msg': '<tg-emoji emoji-id="5226702984204797593">🔄</tg-emoji> <b>অন্যান্য মাধ্যম (Another Method) — ধাপ ১/৩: মাধ্যমের নাম</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 আপনার বর্তমান উত্তোলনযোগ্য ব্যালেন্স: <b>{balance} টাকা</b>\n\n✍️ প্রথমে আপনি কোন মাধ্যমে টাকা নিতে চান, সেই <b>মাধ্যমের নাম</b> নিচে লিখে পাঠান (যেমন: <b>উপায়, ব্যাংক একাউন্ট, রকেট</b> ইত্যাদি):',
    'withdraw_other_way_input_msg': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>অন্যান্য মাধ্যম ({method}) — ধাপ ২/৩: অ্যাকাউন্ট তথ্য</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏦 নির্বাচিত মাধ্যম: <b>{method}</b>\n\n📱 এখন আপনার <b>{method}</b>-এর প্রয়োজনীয় <b>অ্যাকাউন্ট তথ্য / নাম্বার</b> সঠিকভাবে নিচে লিখে পাঠান:',
    'withdraw_other_way_amount_prompt_msg': '<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>অন্যান্য মাধ্যম ({method}) — ধাপ ৩/৩: টাকার পরিমাণ</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏦 নির্বাচিত মাধ্যম: <b>{method}</b>\n📱 অ্যাকাউন্ট তথ্য: <code>{dest}</code>\n💰 বর্তমান ব্যালেন্স: <b>{balance} টাকা</b> (সর্বনিম্ন: <b>{minimum} টাকা</b>)\n\n✍️ আপনি কত টাকা Withdraw করতে চান? সংখ্যায় লিখে পাঠান:',
    'manual_verify_code_prompt_msg': '<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> <b>ম্যানুয়াল ভেরিফিকেশন র\u200d্যান্ডম কোড প্রদান করুন ({platform_title})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার অ্যাকাউন্টে সঠিক Verification Code বা নির্ধারিত লিংক বসানো থাকা সত্ত্বেও স্বয়ংক্রিয় যাচাই ব্যর্থ হয়ে থাকলে, সাপোর্ট থেকে নেওয়া <b>র\u200d্যান্ডম জেনারেট কোড (BC-XXXXXX)</b> নিচে লিখে পাঠান (১টি কোড ১ বারই ব্যবহারযোগ্য)।',
    'manual_verify_code_input_prompt_msg': '<tg-emoji emoji-id="5307843983102204243">🔑</tg-emoji> <b>ম্যানুয়াল ভেরিফিকেশন র\u200d্যান্ডম কোড প্রদান করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nসাপোর্টে কথা বলে অ্যাডমিনের কাছ থেকে নেওয়া <b>র\u200d্যান্ডম জেনারেট কোড (BC-XXXXXX)</b> নিচে লিখে পাঠান (১টি কোড ১ বারই ব্যবহারযোগ্য)।\n\n⚠️ <b>মনে রাখবেন:</b> ম্যানুয়াল কোড ব্যবহারের আগেও আপনার অ্যাকাউন্টের Bio / Description-এ সঠিক Verification Code বা নির্ধারিত লিংক বসানো থাকতে হবে।',
    'manual_verify_submitted_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>আপনার র\u200d্যান্ডম কোডটি গৃহীত হয়েছে এবং ম্যানুয়ালি প্রসেসিংয়ে জমা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nঅ্যাডমিন প্যানেলের <b>প্ল্যাটফর্ম ম্যানুয়ালি প্রসেসিং</b> থেকে অ্যাডমিন অ্যাকসেপ্ট করলেই আপনার অ্যাকাউন্ট যথাযথভাবে Verified হিসেবে সংরক্ষিত হবে।',
    'manual_verify_approved_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>ম্যানুয়ালি ভেরিফিকেশন সম্পূর্ণ হয়েছে ({platform_title})!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার <b>{platform_title}</b> অ্যাকাউন্টটি যথাযথভাবে <b>Verified</b> হিসেবে সংরক্ষিত হয়েছে। এখন পরবর্তী রেজিস্ট্রেশন ধাপ সম্পন্ন করুন:',
    'manual_verify_timeout_msg': '<tg-emoji emoji-id="5386367538735104399">⌛</tg-emoji> <b>৫ মিনিটের সময়সীমা শেষ — ম্যানুয়াল ভেরিফিকেশন সময়োত্তীর্ণ!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n৫ মিনিটের মধ্যে বৈধ র\u200d্যান্ডম কোড প্রদান না করায় আপনার সেশনটি হোমপেজে ফিরিয়ে আনা হয়েছে। পুনরায় চেষ্টা করুন।',
    'dashboard_msg': '📊 <b>BATTLE CLUB | PREMIUM USER DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5188552176988858899">😎</tg-emoji> <b>ব্যক্তিগত ও অ্যাকাউন্ট তথ্য</b>\n├ 👤 অ্যাকাউন্টের নাম: <b>{name}</b>\n├ 🆔 প্রোফাইল UID: <code>{user_id}</code>\n├ 🎮 Battle Club UID: <code>{app_uid}</code>\n├ 📺 চ্যানেল / প্রোফাইল: <b>{channel_name}</b>\n└ 📞 সংরক্ষিত পেমেন্ট নম্বর: <code>{phone}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5226431245918942763">🏆</tg-emoji> <b>লিডারবোর্ড র\u200d্যাঙ্ক ও আর্নিং টার্গেট</b>\n{leaderboard_progress}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>আর্থিক হিসাব (Financial Summary)</b>\n├ 🤑 বর্তমান Available Balance: <b>{balance} টাকা</b>\n├ 🛡 হোল্ড ব্যালেন্স (Pending WD): <b>{held_balance} টাকা</b>\n├ 📉 ঋণ / Negative Balance: <b>{debt_balance} টাকা</b>\n├ 🏆 সর্বমোট আয় (Total Earned): <b>{total_earned} টাকা</b>\n├ 💳 মোট Withdraw Amount: <b>{wd_paid_amt} টাকা</b>\n└ 📌 Financial Status: <b>{financial_status}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="6235259956409408282">☄️</tg-emoji> <b>ভিডিও সাবমিশন পরিসংখ্যান</b>\n├ 📤 মোট সাবমিট ভিডিও: <b>{videos_submitted} টি</b>\n├ ⏳ Pending Videos: <b>{videos_pending} টি</b>\n├ 🤖 Bot Approved: <b>{videos_bot_approved} টি</b>\n├ 👑 Admin Approved: <b>{videos_admin_approved} টি</b>\n├ 🔒 Permanently Approved: <b>{videos_perm_approved} টি</b>\n└ ❌ Rejected Videos: <b>{videos_rejected} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💸 <b>উইথড্র পরিসংখ্যান (Withdraw Statistics)</b>\n├ 📋 মোট Withdraw Request: <b>{wd_total_cnt} টি ({wd_total_amt} টাকা)</b>\n├ ✅ Completed Withdraw: <b>{wd_paid_cnt} টি (সফল উইথড্র: {wd_paid_amt} টাকা)</b>\n├ ⏳ Pending Withdraw: <b>{wd_pend_cnt} টি ({wd_pend_amt} টাকা)</b>\n├ 🔄 Cancelled Withdraw: <b>{wd_canc_cnt} টি ({wd_canc_amt} টাকা)</b>\n└ ❌ Rejected Withdraw: <b>{wd_rej_cnt} টি ({wd_rej_amt} টাকা)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>ভেরিফিকেশন ও রেফারেল তথ্য</b>\n├ 📌 বাধ্যতামূলক Hashtag: <code>{global_code}</code>\n├ 🔝 পরবর্তী ভিডিওর Unique Code: <code>{unique_code}</code>\n├ ☄️ Profile Verification Code: <code>{bio_code}</code>\n└ 🎁 Referral Code: <code>{ref_code}</code> (রেফার: <b>{ref_count} জন</b>)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5267031043487051884">❤️</tg-emoji> <b>BATTLE CLUB | SPONSORSHIP PLATFORM</b>',
    'profile_msg': '<tg-emoji emoji-id="5188552176988858899">😎</tg-emoji> <b>BATTLE CLUB | USER PROFILE ({user_label})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 নিজের নাম (Account Name): <b>{name}</b>\n📺 প্ল্যাটফর্মের চ্যানেলের নাম: <b>{channel_name}</b>\n📞 সংরক্ষিত পেমেন্ট নম্বরসমূহ:\n<code>{phone}</code>\n🎮 Battle Club UID: <code>{app_uid}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌐 <b>ভেরিফাইড প্ল্যাটফর্মসমূহ:</b>\n<b>{platforms_summary}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🧬 Verification Bio Code: <code>{bio_code}</code>\n🔐 Next Video Code: <code>{unique_code}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'video_submit_msg': '<tg-emoji emoji-id="5445355530111437729">📤</tg-emoji> <b>BATTLE CLUB | SPONSOR VIDEO SUBMISSION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5224607267797606837">☄️</tg-emoji> <b>স্পন্সর ভিডিও লিংক সাবমিট করুন ({platform_title})</b>\n\n<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>বাধ্যতামূলক নিয়মাবলি (IMPORTANT RULES):</b>\n\n<tg-emoji emoji-id="5197397670724912036">1️⃣</tg-emoji> <b>প্রোফাইল Bio Verification:</b>\nআপনার ভেরিফাইড অ্যাকাউন্টের Bio / Description-এ ভেরিফিকেশন কোড বা নির্ধারিত লিংক থাকতে হবে:\n<code>{bio_code}</code>\n\n<tg-emoji emoji-id="5197250993296785376">2️⃣</tg-emoji> <b>ভিডিওর Title, Description অথবা Comment যাচাই:</b>\nভিডিওর Title, Description অথবা Comment—এই ৩টি জায়গার যেকোনো একটিতে নিচের <b>বাধ্যতামূলক Unique Verification Code (এবং ভেরিফিকেশন লিংক চালু থাকলে কোডের পাশাপাশি নির্ধারিত লিংকও)</b> এবং <b>বাধ্যতামূলক Hashtag</b> অবশ্যই থাকতে হবে:\n\n🔐 <b>Video Verification Code:</b>\n<code>{unique_code}</code>\n\n📌 <b>Mandatory Hashtag:</b>\n<code>{global_code}</code>\n\n<tg-emoji emoji-id="5195203805725084605">3️⃣</tg-emoji> <b>Verified Account Matching:</b>\nভিডিওটি অবশ্যই আপনার নির্বাচিত ও ভেরিফাই করা অ্যাকাউন্ট থেকেই প্রকাশিত হতে হবে।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>VIDEO EARNING &amp; PAYMENT SYSTEM:</b>\n• ১ম ভিউ টার্গেট পূরণে পেমেন্ট: <b>{rate} টাকা</b> (প্রথমে Pending-এ যাবে এবং টার্গেট ভিউ পূরণ হলে Bot Approved হয়ে ব্যালেন্স যোগ হবে)।\n• ভিউ ট্র্যাকিং মেয়াদ: <b>{track_days} দিন</b> (অথবা সর্বোচ্চ ভিউ ক্যাপ পূর্ণ হওয়া পর্যন্ত)।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5411563083908797492">🛫</tg-emoji> <b>আপনার {platform_title} ভিডিওর লিংকটি এখানে পেস্ট করে পাঠান:</b>',
    'referral_msg': '<tg-emoji emoji-id="6242498410822244114">🎁</tg-emoji> <b>BATTLE CLUB | REFERRAL &amp; INCOME PROGRAM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5317013291602553603">🤑</tg-emoji> প্রতি সফল ভেরিফাইড রেফারে আপনার আয়: <b>{bonus} টাকা</b>\n<tg-emoji emoji-id="6242498410822244114">🎁</tg-emoji> আপনার রেফারেল কোড ব্যবহারকারী পাবেন: <b>{redeem_bonus} টাকা ওয়েলকাম বোনাস!</b>\n<tg-emoji emoji-id="5231200819986047254">📊</tg-emoji> দৈনিক রেফারেল লিমিট: সর্বোচ্চ <b>{max_daily_ref} জন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5226431245918942763">🏆</tg-emoji> মোট সফল রেফারেল: <b>{ref_count} জন</b>\n<tg-emoji emoji-id="6237742262822901946">🤑</tg-emoji> আপনার ইউনিক রেফারেল কোড:\n<pre>{ref_code}</pre>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji> বন্ধুদের আপনার ইউনিক রেফারেল কোডটি শেয়ার করুন এবং অতিরিক্ত আয় করুন!',
    'redeem_msg': '<tg-emoji emoji-id="6244416495971996312">🔝</tg-emoji> <b>BATTLE CLUB | REFERRAL CODE REDEMPTION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> যিনি আপনাকে BATTLE CLUB-এ রেফার করেছেন, তাঁর ইউনিক <b>Referral Code (যেমন REF-XXXXXXX)</b> নিচে লিখে পাঠান।\n\n<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> নিজের রেফার কোড নিজে ব্যবহার করা যাবে না এবং একটি অ্যাকাউন্ট থেকে একবারই রেফার কোড রিডিম করা যাবে।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'leaderboard_msg': '<tg-emoji emoji-id="5226431245918942763">🏆</tg-emoji> <b>BATTLE CLUB — TOP 10 CREATORS LEADERBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="6237905016313615867">🌟</tg-emoji> <b>সর্বোচ্চ আয়কারী সেরা ১০ জন ক্রিয়েটর:</b>\n\n{leaderboard_rows}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n╭─── 📈 <b>LEADERBOARD PROGRESS BOX</b> ───╮\n{gap_notice}\n╰────────────────────────────────────╯\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'payment_list_hub_msg': '<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji> <b>BATTLE CLUB — PAYMENT &amp; EARNINGS LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>উইথড্রয়াল ও পেমেন্ট সারসংক্ষেপ:</b>\n├ 📋 মোট উইথড্র রিকোয়েস্ট: <b>{wd_total_cnt}টি ({wd_total_amt} টাকা)</b>\n├ ✅ Completed Payment (Paid): <b>{wd_paid_cnt}টি ({wd_paid_amt} টাকা)</b>\n├ ⏳ Pending Payment: <b>{wd_pend_cnt}টি ({wd_pend_amt} টাকা)</b>\n└ ❌ Rejected / Cancelled Payment: <b>{wd_rej_cnt}টি ({wd_rej_amt} টাকা)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎬 <b>প্ল্যাটফর্ম অনুযায়ী আয় ও উইথড্র হিসাব:</b>\n{platform_breakdown}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <b>নিচের বাটন থেকে Completed, Pending, Rejected পেমেন্ট অথবা লেজার হিস্ট্রি দেখুন:</b>',
    'payment_wd_status_msg': '<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji> <b>পেমেন্ট লিস্ট — {status_title} (পৃষ্ঠা {page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 মোট রেকর্ড: <b>{total_items}টি ({total_amount} টাকা)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{items_text}',
    'payment_platform_detail_msg': '<tg-emoji emoji-id="5282843764451195532">🖥</tg-emoji> <b>{platform_title} — ভিডিও পেমেন্ট ও আর্নিং রিপোর্ট (পৃষ্ঠা {page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎬 মোট সাবমিট ভিডিও: <b>{total_vids}টি</b> (✅ অনুমোদিত: <b>{approved_vids}টি</b> | ❌ রিজেক্টেড: <b>{rejected_vids}টি</b>)\n💰 এই প্ল্যাটফর্ম থেকে মোট আয়: <b>{earned_amount} টাকা</b>\n📉 রিজেক্ট/রিভার্সাল কর্তন: <b>{deducted_amount} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{items_text}',
    'payment_ledger_list_msg': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>সম্পূর্ণ ফিন্যান্সিয়াল লেজার লেনদেন হিস্ট্রি (পৃষ্ঠা {page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 বর্তমান ব্যালেন্স: <b>{balance} টাকা</b> | ⚠️ বকেয়া ঋণ (Debt): <b>{debt_balance} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{items_text}',
    'withdraw_list_msg': '📋 <b>আপনার উইথড্র রিকোয়েস্ট লিস্ট (পৃষ্ঠা {page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 মোট রিকোয়েস্ট: <b>{total_cnt}টি ({total_amt}৳)</b>\n✅ Completed: <b>{paid_cnt}টি ({paid_amt}৳)</b> | ⏳ Pending: <b>{pend_cnt}টি ({pend_amt}৳)</b>\n🔄 Cancelled: <b>{canc_cnt}টি ({canc_amt}৳)</b> | ❌ Rejected: <b>{rej_cnt}টি ({rej_amt}৳)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{items_text}',
    'user_activity_msg': '📜 <b>BATTLE CLUB | ACCOUNT ACTIVITY &amp; SECURITY STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n╭─── 🛡️ <b>অ্যাকাউন্ট নিরাপত্তা স্ট্যাটাস</b> ───╮\n│ • অ্যাকাউন্ট স্ট্যাটাস: <b>{account_status}</b>\n│ • মোট লগইন সংখ্যা: <b>{login_count} বার</b>\n│ • ফ্রিজ/সিকিউরিটি স্ট্যাটাস: <b>{freeze_status}</b>\n│ • ডুপ্লিকেট ভিডিও স্ট্রাইক: <b>{dup_strikes}/{strike_limit}</b>\n│ • ভুল সাবমিশন স্ট্রাইক: <b>{wrong_strikes}/{strike_limit}</b>\n╰────────────────────────────────╯\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📋 <b>সাম্প্রতিক কার্যক্রম বক্স লগ:</b>\n{activity_logs}',
    'account_limit_reached_msg': '<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>একাধিক অ্যাকাউন্ট যুক্ত করার সীমা পূর্ণ হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার ইতিমধ্যে <b>{platform_title}</b> প্ল্যাটফর্মে নির্ধারিত <b>{max_accounts}টি</b> অ্যাকাউন্ট যুক্ত আছে। অ্যাডমিন নির্ধারিত লিমিট অনুযায়ী সর্বোচ্চ <b>{max_accounts}টি</b> অ্যাকাউন্টই যুক্ত করা যাবে।',
    'delete_acc_confirm_msg': '<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>অ্যাকাউন্ট ডিলিট কনফার্মেশন (২য় ধাপ নিশ্চিতকরণ)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনি কি সত্যিই আপনার অ্যাকাউন্ট ডিলিট করতে চান?\n\n💰 বর্তমান ব্যালেন্স: <b>{balance} টাকা</b> (হোল্ড: <b>{held_balance} টাকা</b>)\n⚠️ <b>সতর্কতা:</b> ডিলিট করলে আপনার প্রোফাইল ও ব্যালেন্স মুছে যাবে, তবে আপনার পূর্বে সাবমিট করা ভিডিওগুলোর Duplicate Lock স্থায়ীভাবে থেকে যাবে (ওই ভিডিও দ্বিতীয়বার কেউ সাবমিট করতে পারবে না)।',
    'delete_acc_debt_block_msg': '<tg-emoji emoji-id="5240241223632954241">🚫</tg-emoji> <b>ঋণ থাকায় অ্যাকাউন্ট ডিলিট করা সম্ভব নয়!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার অ্যাকাউন্টে বর্তমানে <b>-{debt_balance} টাকা</b> ঋণ (Negative Balance / Debt) রয়েছে।\n\n📌 <b>আগে ঋণ পরিশোধ করুন, তারপর অ্যাকাউন্ট ডিলিট করতে পারবেন।</b>',
    'verification_msg': '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>প্রোফাইল ও ভিডিও ভেরিফিকেশন স্ট্যাটাস</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{details}',
    'error_msg': '<tg-emoji emoji-id="6242010768825391425">⚠️</tg-emoji> <b>ত্রুটি / সতর্কবার্তা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>কারণ:</b>\n{reason}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'success_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>সফলভাবে সম্পন্ন হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{details}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'suspicious_video_alert_msg': '<tg-emoji emoji-id="5395695537687123235">🚨</tg-emoji> <b>সন্দেহজনক ভিডিও পর্যবেক্ষণ অ্যালার্ট!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 ইউজার: <b>{user_label}</b> (ID: <code>{user_id}</code>)\n🎬 ভিডিও ID: <code>{sub_id}</code> ({platform})\n👁️ মোট ভিউ: <b>{views}</b>\n⚠️ সন্দেহের কারণ:\n<b>{reason}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'external_traffic_alert_msg': '🌐 <b>এক্সটার্নাল লিংক ভিউ অ্যালার্ট — সন্দেহজনক ট্রাফিক সোর্স!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 ইউজার: <b>{user_label}</b> (ID: <code>{user_id}</code>)\n🎬 ভিডিও ID: <code>{sub_id}</code> ({platform})\n👁️ মোট ভিউ: <b>{total_views}</b>\n\n📊 <b>ভিউ সোর্স ও পার্সেন্টেজ বিশ্লেষণ:</b>\n├ 📺 চ্যানেল / প্রোফাইল থেকে: <b>{channel_pct}% ({channel_views} ভিউ)</b>\n├ 🔍 সার্চ (Search) থেকে: <b>{search_pct}% ({search_views} ভিউ)</b>\n└ ⚠️ এক্সটার্নাল লিংক থেকে: <b>{external_pct}% ({external_views} ভিউ)</b>\n\n🔗 <b>শনাক্তকৃত এক্সটার্নাল লিংক:</b>\n<code>{source_url}</code> — <b>{link_pct}% ({link_views} ভিউ)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'withdraw_msg': '<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>BATTLE CLUB | WITHDRAW REQUEST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 বর্তমান Available Balance: <b>{balance} টাকা</b>\n📉 মিনিমাম উইথড্র লিমিট: <b>{min_withdraw} টাকা</b>\n⏳ আজকের বাকি উইথড্র সংখ্যা: <b>{daily_wd_rem} বার</b>\n💵 আজকের বাকি উইথড্র লিমিট: <b>{daily_amt_rem} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <b>আপনি কোন মাধ্যমে উইথড্র নিতে চান? নিচের মাধ্যমগুলো থেকে নির্বাচন করুন:</b>',
    'withdraw_success_msg': '✅ <b>আপনার উইথড্র রিকোয়েস্ট সফলভাবে জমা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💰 উত্তোলনের পরিমাণ: <b>{amount} টাকা ({method})</b>\n📱 পেমেন্ট তথ্য / গন্তব্য: <code>{dest}</code>\n🆔 Battle Club UID: <code>{app_uid}</code>\n🔒 হোল্ড স্ট্যাটাস: <b>{amount} টাকা Available Balance থেকে উইথড্র রিকোয়েস্টের অধীনে রাখা হয়েছে</b>\n⏳ সম্ভাব্য পেমেন্ট সময়: <b>{wd_eta}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'session_logout_msg': '<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>নিরাপত্তাজনিত স্বয়ংক্রিয় লগআউট!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5386367538735104399">⌛</tg-emoji> আপনার সেশন সময় শেষ হয়েছে। নিরাপত্তার স্বার্থে আপনাকে স্বয়ংক্রিয়ভাবে লগআউট করা হয়েছে। পুনরায় লগইন করতে <code>/start</code> চাপুন অথবা পাসওয়ার্ড পাঠান।',
    'ch_banned_msg': '<tg-emoji emoji-id="5240241223632954241">🚫</tg-emoji> <b>অ্যাকাউন্ট স্থায়ীভাবে নিষিদ্ধ (Banned)!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nদুঃখিত! নিয়ম ও নীতিমালা লঙ্ঘনের কারণে আপনার অ্যাকাউন্টটি স্থায়ীভাবে ব্যান করা হয়েছে।',
    'ch_inactive_msg': '<tg-emoji emoji-id="6242510612824332116">🕐</tg-emoji> <b>অ্যাকাউন্ট বর্তমানে নিষ্ক্রিয় (Inactive)!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার অ্যাকাউন্টটি বর্তমানে ইনঅ্যাক্টিভ অবস্থায় রয়েছে। পুনরায় সক্রিয় করতে সাপোর্ট টিমের সাথে যোগাযোগ করুন।',
    'ch_frozen_msg': '<tg-emoji emoji-id="5197581306346617713">🥶</tg-emoji> <b>অ্যাকাউন্ট সাময়িকভাবে ফ্রিজ করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nস্বয়ংক্রিয় নিরাপত্তা যাচাইয়ে আপনার চ্যানেলের বায়ো বা ভিডিওতে নির্ধারিত ভেরিফিকেশন কোড পাওয়া যায়নি। কোডটি পুনরায় যুক্ত করে নিচের আনফ্রিজ বাটনে ক্লিক করুন।',
    'verification_busy_msg': '<tg-emoji emoji-id="5231012545799666522">🔍</tg-emoji> <b>{platform_title} যাচাই প্রক্রিয়া চলমান!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n১) ভেরিফিকেশন কোড / নির্ধারিত লিংক যাচাই\n২) সাবস্ক্রাইবার / ফলোয়ার সংখ্যা যাচাই\n৩) মোট পাবলিক ভিডিও সংখ্যা গণনা\n৪) যোগ্যতা ভিডিও ও ন্যূনতম ভিউ যাচাই\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏳ অনুগ্রহ করে কয়েক সেকেন্ড অপেক্ষা করুন...',
    'verification_manual_review_msg': '<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> <b>ভিডিওটি পেন্ডিং / ম্যানুয়াল রিভিউয়ে রাখা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nপ্রয়োজনীয় তথ্য ও ভিউ শর্ত নিশ্চিত হওয়া সাপেক্ষে পরবর্তী আপডেট জানানো হবে।',
    'video_verification_busy_msg': '<tg-emoji emoji-id="5231012545799666522">🔍</tg-emoji> <b>স্পন্সর ভিডিও যাচাই প্রক্রিয়া চলমান!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n১) নির্বাচিত ভেরিফাইড অ্যাকাউন্ট মালিকানা যাচাই\n২) Title / Description / Comment-এ ভেরিফিকেশন কোড বা লিংক যাচাই\n৩) বাধ্যতামূলক Hashtag ও পাবলিশের সময়সীমা যাচাই\n৪) অর্গানিক ভিউ ও ট্রাফিক সোর্স বিশ্লেষণ\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏳ অনুগ্রহ করে অপেক্ষা করুন...',
    'video_submission_success_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>স্পন্সর ভিডিও সফলভাবে Pending তালিকায় জমা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👁️ বর্তমান ভিউ: <b>{views}</b>\n🔐 পরবর্তী ভিডিওর ভেরিফিকেশন কোড: <code>{next_code}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'video_submission_fail_msg': '<tg-emoji emoji-id="5438630285635757876">🔠</tg-emoji> <b>ভিডিও সাবমিশন রিজেক্ট হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 <b>রিজেক্ট হওয়ার বিস্তারিত কারণ:</b>\n{reason}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔄 প্রয়োজনীয় সংশোধন করে পুনরায় সাবমিট করুন।',
    'video_views_pending_msg': '<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> <b>স্পন্সর ভিডিও Pending Status-এ জমা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👁️ বর্তমান ভিউ: <b>{views} / {minimum}</b>\n⏳ পেন্ডিং সময়সীমা: <b>{hours} ঘণ্টা</b>\n📌 নির্ধারিত সময়ের মধ্যে প্রথম ভিউ টার্গেট পূরণ হলেই ভিডিওটি স্বয়ংক্রিয়ভাবে <b>Bot Approved</b>-এ যাবে এবং ব্যালেন্সে টাকা যুক্ত হবে।',
    'video_bot_approved_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>স্পন্সর ভিডিও Bot Approved হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👁️ পর্যবেক্ষিত ভিউ: <b>{views}</b>\n💰 যুক্ত হওয়া ১ম টার্গেট পেমেন্ট: <b>{credited} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📈 পরবর্তী প্রতি ভিউ স্টেপ পূরণে স্বয়ংক্রিয়ভাবে আপনার ব্যালেন্সে টাকা যুক্ত হতে থাকবে।',
    'video_qualification_expired_msg': '<tg-emoji emoji-id="5359319827569727155">☹️</tg-emoji> <b>পেন্ডিং ভিডিওর সময়সীমা শেষ — ভিডিওটি Rejected হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nনির্ধারিত পেন্ডিং সময়ের মধ্যে ন্যূনতম ভিউ টার্গেট পূরণ না হওয়ায় ভিডিওটি <b>Rejected Status</b>-এ গেছে এবং এর View Checking বন্ধ করা হয়েছে।',
    'video_review_needed_msg': '🕒 <b>ভিডিওটি পেন্ডিং / ম্যানুয়াল রিভিউয়ে রাখা হয়েছে</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nকারণ: {reason}',
    'video_rejected_msg': '<tg-emoji emoji-id="5438630285635757876">🔠</tg-emoji> <b>স্পন্সর ভিডিও রিজেক্ট করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 ভিডিওর নাম: <b>{title}</b>\n✍️ রিজেক্ট হওয়ার কারণ: <b>{reason}</b>\n💸 সমন্বয়কৃত / কর্তন করা ক্রেডিট: <b>{reversed} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'video_rejection_admin_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>ভিডিও রিজেকশন ও ব্যালেন্স/ঋণ সমন্বয় সম্পন্ন!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 ভিডিও ID: <code>{sub_id}</code>\n💸 সমন্বয়কৃত ক্রেডিট: <b>{reversed} টাকা</b>',
    'video_admin_approved_user_msg': '<tg-emoji emoji-id="5274225173837394638">👑</tg-emoji> <b>আপনার ভিডিওটি Admin Approved হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 ভিডিওর নাম: <b>{title}</b>\n⏳ ভিউ গণনার শেষ সময়: <b>{earning_end}</b>\nℹ️ স্ট্যাটাস পরিবর্তনের কারণে দ্বিতীয়বার প্রথম টার্গেটের টাকা যোগ করা হয়নি; আগের ভিউ ও পেমেন্ট গণনা স্বাভাবিকভাবে চলতে থাকবে।',
    'video_perm_approved_user_msg': '🔒 <b>আপনার ভিডিওটি Permanent Approved হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 ভিডিওর নাম: <b>{title}</b>\n💰 মোট অর্জিত আয়: <b>{credited} টাকা</b>\n✅ নির্ধারিত সময়সীমা / সর্বোচ্চ ভিউ ক্যাপ পূর্ণ হওয়ায় চূড়ান্ত পাওনা যোগ করে ভিডিওটি স্থায়ীভাবে অনুমোদিত হয়েছে।',
    'video_reaccepted_user_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>রিজেক্টেড ভিডিও পুনরায় Admin Approved হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 ভিডিওর নাম: <b>{title}</b>\n🤑 পুনরায় যুক্ত হওয়া ক্রেডিট: <b>{restored} টাকা</b>',
    'withdraw_amount_prompt_msg': '<tg-emoji emoji-id="5267300544094948794">💳</tg-emoji> <b>উইথড্র (টাকা উত্তোলন) পরিমাণ নির্ধারণ</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏦 নির্বাচিত মাধ্যম: <b>{method}</b>\n📱 সংরক্ষিত নাম্বার / UID: <code>{saved_dest}</code>\n💰 বর্তমান Available Balance: <b>{balance} টাকা</b>\n📌 সর্বনিম্ন উত্তোলন: <b>{minimum} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✍️ <b>আপনি কত টাকা উত্তোলন করতে চান? সংখ্যায় লিখে পাঠান:</b>',
    'withdraw_destination_prompt_msg': '<tg-emoji emoji-id="5404350824501491839">📞</tg-emoji> <b>পেমেন্ট নম্বর নিশ্চিত করুন ({method})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nনিচের বাটনে ক্লিক করে আপনার আগে থেকে সংরক্ষিত <b>{method}</b> নাম্বারে উইথড্র নিশ্চিত করুন অথবা নাম্বারটি লিখে পাঠান:',
    'withdraw_uid_prompt_msg': '<tg-emoji emoji-id="6264653011776185688">😍</tg-emoji> <b>Battle Club UID নিশ্চিত করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nনিচের বাটনে ক্লিক করে আপনার সংরক্ষিত <b>Battle Club UID</b> অনুযায়ী উইথড্র নিশ্চিত করুন অথবা UID লিখে পাঠান:',
    'withdraw_invalid_amount_msg': '<tg-emoji emoji-id="6217241670954520304">🫣</tg-emoji> <b>উত্তোলনের পরিমাণ সঠিক নয়!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার বর্তমান Available Balance এবং উইথড্র লিমিটের মধ্যে সঠিক টাকার পরিমাণ লিখুন।',
    'withdraw_invalid_destination_msg': '<tg-emoji emoji-id="6217241670954520304">🫣</tg-emoji> <b>পেমেন্ট নম্বর বা তথ্য সঠিক নয়!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nসঠিক ফরম্যাটে পেমেন্ট নম্বর (<code>01XXXXXXXXX</code>) অথবা Battle Club UID (<code>#1007</code>) প্রদান করুন।',
    'withdraw_rejected_msg': '<tg-emoji emoji-id="5438630285635757876">🔠</tg-emoji> <b>উইথড্র (Withdrawal) রিকোয়েস্ট বাতিল ও রিফান্ড হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💸 বাতিলকৃত পরিমাণ: <b>{amount} টাকা ({method})</b>\n✅ সম্পূর্ণ <b>{amount} টাকা</b> আপনার Available Balance-এ ফেরত দেওয়া হয়েছে।',
    'withdraw_paid_msg': '<tg-emoji emoji-id="6235478849417647339">✅</tg-emoji> <b>উইথড্র (Withdrawal) সফলভাবে Completed হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💸 পরিশোধিত পরিমাণ: <b>{amount} টাকা ({method})</b>\n📱 গন্তব্য: <code>{dest}</code>\n🏦 লেনদেনের অবস্থা: <b>Completed ✅</b>',
    'admin_welcome_msg': '<tg-emoji emoji-id="6235252066554484059">👑</tg-emoji> <b>সুপার অ্যাডমিন প্যানেল আনলক হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5317026657540780588">🎉</tg-emoji> স্বাগতম, সুপার অ্যাডমিন! নিচের মেনু থেকে <b>📊 ড্যাশবোর্ড ও মেট্রিক্স</b>, <b>⚙️ কন্ট্রোল সেটিংস হাব</b> অথবা <b>🛠️ অ্যাডভান্সড সেটিংস</b> নির্বাচন করুন।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_dashboard_msg': '<tg-emoji emoji-id="5274225173837394638">👑</tg-emoji> <b>BATTLE CLUB — SUPER ADMIN DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5453957997418004470">👥</tg-emoji> <b>USER STATISTICS | ইউজার পরিসংখ্যান</b>\n├ 👩‍💻 Total Users: <b>{total_users} জন</b>\n├ ✅ Verified Users: <b>{verified_users} জন</b>\n├ ⌛ Pending Verification: <b>{pending_users} জন</b>\n├ 🟢 Active Users (২৪ ঘণ্টায় সচল): <b>{active_users} জন</b>\n├ 🕐 Inactive Users (২৪ঘণ্টা নিষ্ক্রিয়: <b>{inactive_24h_users}</b> | ৩-৪+ দিন নিষ্ক্রিয়: <b>{inactive_3d_users}</b>): মোট <b>{inactive_users} জন</b>\n├ ⚠️ Negative / Problem-Inactive Users (ঋণ/ফ্রিজ/স্ট্রাইক): <b>{negative_activity_users} জন</b>\n└ 🚫 Banned / Deleted Users: <b>{banned_users} জন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5224607267797606837">☄️</tg-emoji> <b>VIDEO STATISTICS | ভিডিও পরিসংখ্যান</b>\n├ 📤 Total Submitted Videos: <b>{total_videos} টি</b>\n├ ⏳ Pending Videos: <b>{pending_videos} টি</b>\n├ 🤖 Bot Approved Videos: <b>{bot_approved_videos} টি</b>\n├ 👑 Admin Approved Videos: <b>{admin_approved_videos} টি</b>\n├ 🔒 Permanently Approved Videos: <b>{perm_approved_videos} টি</b>\n├ ❌ Rejected Videos: <b>{rejected_videos} টি</b>\n├ 🗑️ Trash Videos: <b>{trashed_videos} টি</b>\n└ 🚨 Suspicious / External Traffic Videos: <b>{suspicious_videos} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5260270009048906733">💸</tg-emoji> <b>FINANCIAL STATISTICS | আর্থিক পরিসংখ্যান</b>\n├ 🤑 Total User Earnings: <b>{total_earnings} টাকা</b>\n├ 💳 Total Available Balance: <b>{available_balance} টাকা</b>\n├ 🛡 Total Hold Balance: <b>{held_balance} টাকা</b>\n├ 📤 Total Withdraw Amount (সর্বমোট রিকোয়েস্ট): <b>{total_wd_amount} টাকা</b>\n├ ✅ Total Paid Amount (পরিশোধিত): <b>{paid_wd_amount} টাকা</b>\n└ 📉 Total Negative / Debt Balance (মোট ঋণ): <b>{debt_balance} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n<tg-emoji emoji-id="5332455502917949981">🏦</tg-emoji> <b>WITHDRAW STATISTICS | উত্তোলন পরিসংখ্যান</b>\n├ ✅ Completed (Paid): <b>{paid_wd_count} টি ({paid_wd_amount} টাকা)</b>\n├ ⏳ Pending Withdrawals: <b>{pending_wd_count} টি ({held_balance} টাকা)</b>\n├ 🔄 Cancelled Withdrawals: <b>{cancelled_only_wd_count} টি</b>\n└ ❌ Rejected Withdrawals: <b>{rejected_only_wd_count} টি</b> (মোট বাতিল/রিজেক্ট: <b>{cancelled_wd_count} টি</b>)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_withdrawal_report_msg': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>WITHDRAWAL REQUEST PAGE &amp; MANAGEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n├ ⏳ Pending Requests: <b>{pending_count} টি</b>\n├ ✅ Paid (Completed) Requests: <b>{paid_count} টি</b>\n├ 🔄 Cancelled Requests: <b>{cancelled_only_count} টি</b>\n└ ❌ Rejected Requests: <b>{rejected_only_count} টি</b> (মোট বাতিল/রিজেক্ট: <b>{cancelled_count} টি</b>)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 নিচের বাটন থেকে প্রতিটি ক্যাটাগরির রিকোয়েস্ট দেখুন ও পরিচালনা করুন:',
    'admin_pending_only_video_report_msg': '⏳ <b>PENDING VIDEOS — PLATFORM SELECTION &amp; LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট পেন্ডিং ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_waiting_video_report_msg': '⏳ <b>PENDING VIDEOS — PLATFORM SELECTION &amp; LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট পেন্ডিং ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_pending_video_report_msg': '<tg-emoji emoji-id="5226639745106330551">🧠</tg-emoji> <b>BOT APPROVED VIDEOS — PLATFORM SELECTION &amp; LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট Bot Approved ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_approved_video_report_msg': '<tg-emoji emoji-id="6235252066554484059">👑</tg-emoji> <b>ADMIN APPROVED VIDEOS — PLATFORM SELECTION &amp; LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট Admin Approved ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_permanent_video_report_msg': '<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>PERMANENT APPROVED VIDEOS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট Permanent Approved ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_rejected_video_report_msg': '<tg-emoji emoji-id="5438630285635757876">🔠</tg-emoji> <b>REJECTED VIDEOS &amp; REVERSAL MANAGEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🖥️ প্ল্যাটফর্ম ফিল্টার: <b>{platform_filter}</b> | 🎬 মোট Rejected ভিডিও: <b>{total_items} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_trash_report_msg': '🗑️ <b>TRASH &amp; RECYCLE BIN MANAGEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n☄️ মোট ট্র্যাশ ভিডিও: <b>{total_items} টি</b>\n📌 ট্র্যাশ থেকে ভিডিও ডিলিট করলেও ভিডিওর Original Identity / Duplicate Lock স্থায়ীভাবে থেকে যায়।\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_user_history_msg': '<tg-emoji emoji-id="5453957997418004470">👥</tg-emoji> <b>USER LIST &amp; ACTIVITY HISTORY</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 মোট নিবন্ধিত ইউজার: <b>{total_users} জন</b>\n🔵 <b>Blue:</b> Active | 🟢 <b>Green:</b> Inactive/Frozen | 🔴 <b>Red:</b> Deleted/Banned\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_financial_report_msg': '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> <b>FREELANCING LEDGER &amp; AUDIT HISTORY</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 মোট লেনদেন রেকর্ড: <b>{total_tx} টি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_settings_msg': '<tg-emoji emoji-id="5197288647275071607">🛡</tg-emoji> <b>CONTROL SETTINGS HUB (অ্যাডমিন কন্ট্রোল সেটিংস)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📌 <b>১. GLOBAL VERIFICATION:</b>\n├ বাধ্যতামূলক হ্যাশট্যাগ: <code>{global_code}</code>\n└ নির্ধারিত ভেরিফিকেশন লিংক: <code>{verification_link}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💸 <b>২. VIDEO EARNING &amp; TIMING SETTINGS:</b>\n├ ১ম টার্গেট ভিউ পেমেন্ট: <b>{first_1k}৳</b> | প্রতি স্টেপ পেমেন্ট: <b>{every_200}৳</b>\n└ সর্বোচ্চ ভিউ ক্যাপ: <b>{max_views} ভিউ</b> | ভিউ কাউন্ট মেয়াদ: <b>{earning_days} দিন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💳 <b>৩. WITHDRAW &amp; REFERRAL SETTINGS:</b>\n├ সর্বনিম্ন উত্তোলন: <b>{min_withdraw}৳</b> | দৈনিক সীমা: <b>{max_daily_wd_count} বার / {max_daily_wd_amount}৳</b>\n└ রেফার বোনাস: <b>{ref_bonus}৳</b> | রিডিম বোনাস: <b>{redeem_bonus}৳</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 নিচের বিভাগগুলো থেকে প্রয়োজনীয় সেটিংস পরিচালনা করুন:',
    'admin_general_settings_msg': '⚙️ <b>GENERAL SETTINGS (জেনারেল সেটিংস বিভাগ)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nএখান থেকে ম্যানুয়াল প্রসেসিং ও নাম্বার চেঞ্জ র‍্যান্ডম কোড, হ্যাশট্যাগ ও ভেরিফিকেশন লিংক, সাপোর্ট ও গ্রুপ লিংক, ডেটাবেস CSV এক্সপোর্ট (ও লেজার/অডিট হিস্ট্রি), অ্যাডমিন গাইড এবং কমান্ড শর্টকাট পরিচালনা করুন:',
    'admin_advanced_settings_msg': '🛠️ <b>ADVANCED SETTINGS (অ্যাডভান্সড কাস্টমাইজেশন হাব)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nএখান থেকে ইউজার সাইড ও অ্যাডমিন সাইডের প্রতিটি বাটনের নাম, লেখার ডিজাইন (Bold/Style), Premium Custom Emoji, সকল মেসেজ ও স্ট্যাটাস টেমপ্লেট, এবং বাটনের অবস্থান (ডানে, বামে, উপরে, নিচে বা এক পেজ থেকে অন্য পেজে স্থানান্তর) লাইভ প্রিভিউসহ পরিবর্তন করুন:',
    'profile_name_submenu_msg': '✏️ <b>নাম ও Battle Club UID পরিবর্তন (Change Name)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনি নিচের দুটি অপশন থেকে আপনার <b>অ্যাকাউন্টের নাম</b> এবং <b>Battle Club UID</b> আলাদাভাবে পরিবর্তন করতে পারবেন:',
    'profile_wd_num_submenu_msg': '📱 <b>উইথড্র নাম্বার পরিবর্তন ও সংযোজন (Withdraw Number Change / Add)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n╭─── 💳 <b>আপনার সংরক্ষিত পেমেন্ট নাম্বারসমূহ</b> ───╮\n{selected_methods_summary}\n╰────────────────────────────────────╯\n📌 <b>নিয়ম:</b> বিকাশ, নগদ এবং রকেটে সর্বোচ্চ ১টি করে নাম্বার সংরক্ষণ করা যাবে (একই মাধ্যমে ২য় নাম্বার যুক্ত করা যাবে না; তবে আগের নাম্বার পরিবর্তন বা ফাঁকা মাধ্যমে নতুন নাম্বার যুক্ত করা যাবে)।',
    'profile_name_edit_prompt_msg': '✏️ <b>Change Account Name (নিজের অ্যাকাউন্টের নাম পরিবর্তন)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✍️ আপনার নতুন <b>{field_label}</b> নিচে লিখে পাঠান:',
    'profile_uid_edit_prompt_msg': '🆔 <b>Change Battle Club UID (অ্যাপ UID পরিবর্তন)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✍️ আপনার নতুন <b>{field_label}</b> হ্যাশট্যাগসহ (যেমন <code>#107</code> বা <code>#1007</code>) নিচে লিখে পাঠান:',
    'video_submit_plat_select_msg': '📤 <b>BATTLE CLUB | VIDEO SUBMISSION PLATFORM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনি কোন প্ল্যাটফর্মে ভিডিও সাবমিট করতে চান? নিচের <b>YouTube</b> অথবা <b>TikTok</b> বাটন থেকে সিলেক্ট করুন:',
    'video_submit_acc_select_msg': '📺 <b>{platform_title} — সঠিক অ্যাকাউন্ট সিলেক্ট করুন ({account_count}টি যুক্ত অ্যাকাউন্ট)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার যুক্ত থাকা অ্যাকাউন্টগুলোর মধ্য থেকে কোন অ্যাকাউন্টের মাধ্যমে ভিডিও লিংক সাবমিট করতে চান তা সিলেক্ট করুন:',
    'my_videos_plat_select_msg': '🎬 <b>MY VIDEOS — প্ল্যাটফর্ম নির্বাচন করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার কোন প্ল্যাটফর্মের ভেরিফাইড অ্যাকাউন্টের ভিডিওগুলো দেখতে চান তা সিলেক্ট করুন:',
    'my_videos_acc_select_msg': '🎬 <b>MY VIDEOS ({platform_title}) — অ্যাকাউন্ট নির্বাচন করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার যুক্ত করা <b>{account_count}টি</b> অ্যাকাউন্ট নিচে ক্রমানুসারে (First Account, Second Account...) দেওয়া হলো। যেকোনো অ্যাকাউন্টে ক্লিক করে ভিডিওর ক্যাটাগরি দেখুন:',
    'my_videos_cat_select_msg': '🎬 <b>{account_ordinal} ({account_name}) — ভিডিও ক্যাটাগরি</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n├ 📋 All Videos: <b>{total_vids} টি</b>\n├ ⏳ Pending Videos: <b>{pending_cnt} টি</b>\n├ 🤖 Bot Approved: <b>{bot_approved_cnt} টি</b>\n├ 👑 Admin Approved: <b>{admin_approved_cnt} টি</b>\n├ 🔒 Permanent Approved: <b>{perm_approved_cnt} টি</b>\n├ ❌ Rejected Videos: <b>{rejected_cnt} টি</b>\n└ 💰 মোট অর্জিত আয়: <b>{total_earned} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 নিচের যেকোনো ক্যাটাগরি বাটনে ক্লিক করে সংশ্লিষ্ট ভিডিওগুলো দেখুন:',
    'my_videos_list_msg': '🎬 <b>আমার ভিডিওসমূহ ({filter_title} — পৃষ্ঠা {page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 মোট ভিডিও: <b>{total_vids}টি</b> | 💰 মোট আয়: <b>{total_earned} টাকা</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{items_hint}',
    'pwd_change_old_prompt_msg': '🔑 <b>পাসওয়ার্ড পরিবর্তন (ধাপ ১/৩ — বর্তমান পাসওয়ার্ড)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🛡️ নিরাপত্তা যাচাইয়ের জন্য প্রথমে আপনার <b>বর্তমান পাসওয়ার্ডটি</b> লিখে পাঠান:',
    'pwd_change_new_prompt_msg': '🔑 <b>পাসওয়ার্ড পরিবর্তন (ধাপ ২/৩ — নতুন পাসওয়ার্ড)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ বর্তমান পাসওয়ার্ড যাচাই সম্পন্ন! এখন আপনার <b>নতুন পাসওয়ার্ডটি</b> লিখে পাঠান:',
    'pwd_change_confirm_prompt_msg': '🔑 <b>পাসওয়ার্ড পরিবর্তন (ধাপ ৩/৩ — কনফার্ম পাসওয়ার্ড)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔄 নিশ্চিতকরণের জন্য আপনার <b>নতুন পাসওয়ার্ডটি দ্বিতীয়বার</b> হুবহু লিখে পাঠান:',
    'pwd_change_mismatch_msg': '❌ <b>নতুন পাসওয়ার্ড ও কনফার্ম পাসওয়ার্ড মেলেনি!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nঅনুগ্রহ করে আবার আপনার <b>নতুন পাসওয়ার্ডটি (ধাপ ২/৩)</b> সঠিকভাবে লিখে পাঠান:',
    'pwd_change_success_msg': '✅ <b>অভিনন্দন! আপনার অ্যাকাউন্টের পাসওয়ার্ড সফলভাবে পরিবর্তন ও সুরক্ষিত করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'debt_bind_block_msg': '🚫 <b>ঋণ থাকায় নতুন অ্যাকাউন্ট যুক্ত করা সম্ভব নয়!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nআপনার অ্যাকাউন্টে বর্তমানে <b>-{debt_balance} টাকা</b> বকেয়া ঋণ রয়েছে। আগে ঋণ পরিশোধ করুন।',
    'admin_user_activity_report_msg': '📋 <b>ইউজার সম্পূর্ণ কার্যক্রম ও নিরাপত্তা রিপোর্ট ({user_label})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n╭─── 📊 <b>অ্যাকাউন্ট ও স্ট্রাইক সামারি</b> ───╮\n│ • ইউজার ID: <code>{user_id}</code>\n│ • অ্যাকাউন্ট স্ট্যাটাস: <b>{account_status}</b>\n│ • মোট লগইন সংখ্যা: <b>{login_count} বার</b>\n│ • মোট ভিডিও সাবমিট: <b>{videos_submitted}টি</b> (✅ {videos_approved} | ❌ {videos_rejected})\n│ • ডুপ্লিকেট ভিডিও স্ট্রাইক: <b>{dup_strikes}/{strike_limit}</b>\n│ • ভুল সাবমিশন স্ট্রাইক: <b>{wrong_strikes}/{strike_limit}</b>\n│ • বায়ো/কোড ফ্রিজ স্ট্যাটাস: <b>{freeze_status}</b>\n╰────────────────────────────────╯\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🗂️ <b>সাম্প্রতিক কার্যক্রম বক্স লগ:</b>\n{activity_logs}',
    'admin_random_code_generated_msg': '🔑 <b>ওয়ান-টাইম র\u200d্যান্ডম জেনারেট কোড তৈরি হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n╭─── 🛡️ <b>র\u200d্যান্ডম কোড বিবরণ</b> ───╮\n│ • র\u200d্যান্ডম কোড: <code>{code}</code>\n│ • মেয়াদ: <b>৫ মিনিট ({expires_at} পর্যন্ত)</b>\n│ • ব্যবহারের সীমা: <b>১ বার (Single-Use)</b>\n╰──────────────────────────╯\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'admin_delete_user_debt_confirm_msg': '⚠️ <b>ঋণযুক্ত অ্যাকাউন্ট ডিলিট কনফার্মেশন!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 ইউজার: <b>{user_label}</b> (ID: <code>{user_id}</code>)\n📉 বর্তমান Debt / Negative Balance: <b>-{debt_balance} টাকা</b>\n💰 বর্তমান Available Balance: <b>{balance} টাকা</b>\n\n🚨 <b>আপনি কি Debt ({debt_balance} টাকা) থাকা অবস্থাতেই এই অ্যাকাউন্টটি Delete করতে চান?</b>\nনিচের <b>Confirm</b> অথবা <b>Cancel</b> বাটনে ক্লিক করুন:',
    'admin_logout_confirm_msg': '🔒 <b>অ্যাডমিন প্যানেল থেকে সফলভাবে লগআউট করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nপুনরায় অ্যাডমিন প্যানেলে প্রবেশ করতে আপনার অ্যাডমিন পাসওয়ার্ড পাঠান অথবা ইউজার মেনু ব্যবহার করতে <code>/start</code> চাপুন।',
    'admin_verification_report_msg': '<tg-emoji emoji-id="5224607267797606837">☄️</tg-emoji> <b>VERIFICATION &amp; ANTI-FRAUD REPORT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{details}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'video_deleted_freeze_msg': '❄️ <b>জরুরি নোটিশ — ভিডিও ডিলিট করার কারণে অ্যাকাউন্ট ফ্রিজ করা হয়েছে!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎬 ভিডিও: <b>{title}</b> ({platform})\n⚠️ ট্র্যাকিং চলাকালীন সোশ্যাল প্ল্যাটফর্ম থেকে আপনার সাবমিট করা ভিডিওটি ডিলিট বা প্রাইভেট করে দেওয়া হয়েছে। সমাধানের জন্য সাপোর্টে যোগাযোগ করুন: {support_link}'
}

# Add dynamic explanation message templates for every setting and criteria field so Admin can edit them too (Requirement 127 & 152)
for _ck, _cmeta in CRITERIA_FIELD_EXPLANATIONS.items():
    DEFAULT_MESSAGES[f"crit_exp_{_ck}"] = (
        f"⚙️ <b>{_cmeta['title']}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        f"📌 <b>এই সেটিংসের কাজ ও পরিবর্তনের প্রভাব:</b>\n{_cmeta['impact']}\n"
        f"{FULL_WIDTH_DIVIDER}"
    )

for _sk, _sexp in SETTING_FIELD_EXPLANATIONS.items():
    DEFAULT_MESSAGES[f"setting_exp_{_sk}"] = (
        f"⚙️ <b>সেটিংস বিবরণ: {_sk}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        f"📌 <b>এই সেটিংসের কাজ ও পরিবর্তনের প্রভাব:</b>\n{_sexp}\n"
        f"{FULL_WIDTH_DIVIDER}"
    )

MESSAGE_TEMPLATE_LABELS = {
    "welcome_msg": "👋 ইউজার হোমপেজ ওয়েলকাম মেসেজ (Welcome Message)",
    "notice_msg": "📢 অফিসিয়াল নোটিশ মেসেজ (Notice Message)",
    "notification_msg": "🔔 সাধারণ নোটিফিকেশন মেসেজ (Notification Message)",
    "instruction_msg": "📘 নির্দেশনামূলক মেসেজ (Instruction Message)",
    "user_settings_hub_msg": "⚙️ ইউজার সেটিংস হাব স্ট্যাটাস মেসেজ",
    "login_password_prompt_msg": "🔐 লগইন পাসওয়ার্ড প্রম্পট",
    "forgot_password_support_msg": "🆘 পাসওয়ার্ড ভুলে গেলে সাপোর্ট মেসেজ",
    "login_failed_support_msg": "⚠️ ভুল পাসওয়ার্ড সাপোর্ট অ্যালার্ট",
    "user_logout_confirm_msg": "🔒 ইউজার লগআউট কনফার্মেশন",
    "reg_step1_yt_msg": "🚀 স্টার্ট ও প্ল্যাটফর্ম সিলেকশন মেসেজ (YT & TT)",
    "reg_code_prompt_msg": "🧬 ভেরিফিকেশন নির্দেশনা মেসেজ (Verification Message)",
    "reg_fail_eligibility_msg": "❌ ভেরিফিকেশন রিজেক্টেড মেসেজ (Verification Rejected)",
    "reg_uid_input_msg": "🆔 বাধ্যতামূলক Battle Club UID রিকোয়েস্ট মেসেজ",
    "reg_payment_methods_select_msg": "💳 বিকাশ/নগদ/রকেট পেমেন্ট মাধ্যম সিলেকশন মেসেজ",
    "reg_payment_number_input_msg": "📞 পেমেন্ট নাম্বার রিকোয়েস্ট মেসেজ (Payment Number Request)",
    "reg_name_input_msg": "👤 ইউজারের অ্যাকাউন্ট নাম রিকোয়েস্ট মেসেজ",
    "reg_channel_name_input_msg": "📺 প্ল্যাটফর্ম অ্যাকাউন্টের নাম রিকোয়েস্ট মেসেজ",
    "reg_password_input_msg": "🔑 পাসওয়ার্ড তৈরি রিকোয়েস্ট মেসেজ (Password Request)",
    "reg_password_confirm_input_msg": "🔑 পাসওয়ার্ড পুনরায় নিশ্চিতকরণ মেসেজ",
    "reg_password_mismatch_msg": "❌ পাসওয়ার্ড অমিল সতর্কবার্তা",
    "reg_complete_msg": "🎉 ভেরিফিকেশন ও রেজিস্ট্রেশন সম্পন্ন মেসেজ (Verification Completed)",
    "profile_edit_hub_msg": "✏️ প্রোফাইল ও পেমেন্ট এডিট হাব মেসেজ",
    "profile_random_code_prompt_msg": "🔑 নাম্বার/চ্যানেল চেঞ্জ র‍্যান্ডম কোড প্রম্পট",
    "profile_random_code_verified_msg": "✅ র‍্যান্ডম কোড ভেরিফাইড এডিট প্রম্পট",
    "withdraw_insufficient_balance_msg": "⚠️ অপর্যাপ্ত ব্যালেন্স উইথড্র নোটিফিকেশন মেসেজ",
    "withdraw_other_way_platform_msg": "🔄 Another Method মাধ্যম নাম প্রম্পট",
    "withdraw_other_way_method_name_prompt_msg": "🔄 Another Method (ধাপ ১: মাধ্যমের নাম)",
    "withdraw_other_way_input_msg": "✍️ Another Method (ধাপ ২: অ্যাকাউন্ট তথ্য)",
    "withdraw_other_way_amount_prompt_msg": "💸 Another Method (ধাপ ৩: টাকার পরিমাণ)",
    "manual_verify_code_prompt_msg": "🔑 ম্যানুয়াল ভেরিফিকেশন কোড প্রম্পট",
    "manual_verify_code_input_prompt_msg": "🔑 ম্যানুয়াল কোড ইনপুট প্রম্পট",
    "manual_verify_submitted_msg": "✅ ম্যানুয়াল কোড সাবমিট মেসেজ",
    "manual_verify_approved_msg": "✅ ম্যানুয়াল ভেরিফিকেশন অনুমোদন মেসেজ",
    "manual_verify_timeout_msg": "⌛ ম্যানুয়াল কোড ৫-মিনিট টাইমআউট মেসেজ",
    "dashboard_msg": "📊 ইউজার ড্যাশবোর্ড স্ট্যাটাস মেসেজ (Status Message)",
    "profile_msg": "👤 ইউজার প্রোফাইল মেসেজ",
    "video_submit_msg": "📤 ভিডিও সাবমিশন মেসেজ (Video Submission Message)",
    "referral_msg": "🎁 রেফারেল মেসেজ",
    "redeem_msg": "🎟️ রিডিম মেসেজ",
    "leaderboard_msg": "🏆 লিডারবোর্ড মেসেজ টেমপ্লেট",
    "payment_list_hub_msg": "💳 পেমেন্ট লিস্ট মেইন মেসেজ টেমপ্লেট",
    "payment_wd_status_msg": "💳 পেমেন্ট লিস্ট উইথড্র স্ট্যাটাস টেমপ্লেট",
    "payment_platform_detail_msg": "💳 পেমেন্ট লিস্ট প্ল্যাটফর্ম বিস্তারিত টেমপ্লেট",
    "payment_ledger_list_msg": "💳 পেমেন্ট লিস্ট লেজার হিস্ট্রি টেমপ্লেট",
    "withdraw_list_msg": "📋 উইথড্র লিস্ট মেসেজ টেমপ্লেট",
    "user_activity_msg": "📜 একাউন্ট অ্যাক্টিভিটি মেসেজ টেমপ্লেট",
    "account_limit_reached_msg": "⚠️ একাধিক অ্যাকাউন্ট লিমিট নোটিশ",
    "delete_acc_confirm_msg": "🗑️ অ্যাকাউন্ট ডিলিট কনফার্মেশন",
    "delete_acc_debt_block_msg": "🚫 ঋণ থাকলে ডিলিট ব্লক মেসেজ",
    "verification_msg": "🛡️ ভেরিফিকেশন স্ট্যাটাস মেসেজ",
    "error_msg": "❌ এরর মেসেজ টেমপ্লেট",
    "success_msg": "✅ সাকসেস মেসেজ টেমপ্লেট",
    "suspicious_video_alert_msg": "🚨 অ্যাডমিন ভিডিও রিভিউ অ্যালার্ট",
    "external_traffic_alert_msg": "🌐 এক্সটার্নাল লিংক ভিউ অ্যালার্ট",
    "withdraw_msg": "💸 উইথড্র রিকোয়েস্ট ফরম মেসেজ",
    "withdraw_success_msg": "⏳ উইথড্র প্রসেসিং মেসেজ (Withdraw Processing)",
    "session_logout_msg": "🔒 সেশন অটো-লগআউট নোটিফিকেশন",
    "ch_banned_msg": "🚫 অ্যাকাউন্ট ব্যান মেসেজ",
    "ch_inactive_msg": "⏸️ অ্যাকাউন্ট ইনঅ্যাক্টিভ মেসেজ",
    "ch_frozen_msg": "❄️ বায়ো কোড ফ্রিজ মেসেজ",
    "video_deleted_freeze_msg": "❄️ ভিডিও ডিলিট পেনাল্টি ও সাপোর্ট নোটিশ",
    "verification_busy_msg": "🔍 ভেরিফিকেশন প্রসেসিং মেসেজ (Verification Processing)",
    "verification_manual_review_msg": "🕒 প্রোফাইল ম্যানুয়াল রিভিউ মেসেজ",
    "video_verification_busy_msg": "🎬 ভিডিও ভেরিফিকেশন প্রসেসিং মেসেজ",
    "video_submission_success_msg": "✅ ভিডিও জমা নিশ্চিতকরণ মেসেজ",
    "video_submission_fail_msg": "❌ ভিডিও যাচাই ব্যর্থ মেসেজ",
    "video_views_pending_msg": "⏳ পেন্ডিং ভিউ পর্যবেক্ষণ মেসেজ",
    "video_bot_approved_msg": "🤖 ভিডিও Bot Approval মেসেজ",
    "video_qualification_expired_msg": "⏰ ভিউ সময়সীমা শেষ রিজেক্ট নোটিফিকেশন",
    "video_review_needed_msg": "🕒 ভিডিও ম্যানুয়াল রিভিউ নোটিফিকেশন",
    "video_rejected_msg": "❌ ভিডিও Rejection মেসেজ (Video Rejected)",
    "video_rejection_admin_msg": "✅ অ্যাডমিন ভিডিও রিজেকশন কনফার্মেশন",
    "video_admin_approved_user_msg": "👑 ভিডিও Admin Approval মেসেজ",
    "video_perm_approved_user_msg": "🔒 ভিডিও Permanent Approval মেসেজ",
    "video_reaccepted_user_msg": "✅ রিজেক্টেড ভিডিও Re-accept মেসেজ",
    "withdraw_amount_prompt_msg": "💰 উইথড্র পরিমাণ ইনপুট মেসেজ",
    "withdraw_destination_prompt_msg": "📱 পেমেন্ট নম্বর ইনপুট মেসেজ",
    "withdraw_uid_prompt_msg": "🆔 Battle Club UID ইনপুট মেসেজ",
    "withdraw_invalid_amount_msg": "⚠️ উইথড্র পরিমাণে ভুল মেসেজ",
    "withdraw_invalid_destination_msg": "⚠️ নম্বর বা UID-তে ভুল মেসেজ",
    "withdraw_rejected_msg": "❌ উইথড্র Rejected মেসেজ (Withdraw Rejected)",
    "withdraw_paid_msg": "✅ উইথড্র Completed মেসেজ (Withdraw Completed)",
    "admin_welcome_msg": "👑 অ্যাডমিন ওয়েলকাম মেসেজ",
    "admin_dashboard_msg": "📊 অ্যাডমিন ড্যাশবোর্ড মেসেজ",
    "admin_withdrawal_report_msg": "📋 অ্যাডমিন উইথড্র রিকোয়েস্ট পেজ মেসেজ",
    "admin_pending_only_video_report_msg": "⏳ পেন্ডিং ভিডিও রিপোর্ট টেমপ্লেট",
    "admin_waiting_video_report_msg": "⏳ ওয়েটিং পেন্ডিং ভিডিও রিপোর্ট টেমপ্লেট",
    "admin_pending_video_report_msg": "🤖 বট অ্যাপ্রুভ রিপোর্ট টেমপ্লেট",
    "admin_approved_video_report_msg": "👑 অ্যাডমিন অ্যাপ্রুভড রিপোর্ট টেমপ্লেট",
    "admin_permanent_video_report_msg": "🔒 পার্মানেন্ট অ্যাপ্রুভ রিপোর্ট টেমপ্লেট",
    "admin_rejected_video_report_msg": "❌ রিজেক্টেড ভিডিও রিপোর্ট টেমপ্লেট",
    "admin_trash_report_msg": "🗑️ ট্র্যাশ রিপোর্ট টেমপ্লেট",
    "admin_user_history_msg": "👥 ইউজার হিস্ট্রি টেমপ্লেট",
    "admin_financial_report_msg": "📜 ফিন্যান্সিয়াল লেজার ও অডিট রিপোর্ট টেমপ্লেট",
    "admin_settings_msg": "⚙️ কন্ট্রোল সেটিংস হাব টেমপ্লেট",
    "admin_general_settings_msg": "🛠️ জেনারেল সেটিংস হাব টেমপ্লেট",
    "admin_advanced_settings_msg": "🎛️ অ্যাডভান্সড সেটিংস হাব টেমপ্লেট",
    "admin_verification_report_msg": "🛡️ ভেরিফিকেশন রিপোর্ট টেমপ্লেট",
    "profile_name_submenu_msg": "✏️ প্রোফাইল নাম পরিবর্তন সাব-মেনু মেসেজ",
    "profile_wd_num_submenu_msg": "📱 উইথড্র নাম্বার পরিবর্তন সাব-মেনু মেসেজ",
    "profile_name_edit_prompt_msg": "✏️ নিজের নাম পরিবর্তন প্রম্পট",
    "profile_uid_edit_prompt_msg": "🆔 Battle Club UID পরিবর্তন প্রম্পট",
    "video_submit_plat_select_msg": "📤 ভিডিও সাবমিট প্ল্যাটফর্ম সিলেকশন মেসেজ",
    "video_submit_acc_select_msg": "📺 ভিডিও সাবমিট মাল্টি-অ্যাকাউন্ট সিলেকশন মেসেজ",
    "my_videos_plat_select_msg": "🎬 My Videos প্ল্যাটফর্ম সিলেকশন মেসেজ",
    "my_videos_acc_select_msg": "🎬 My Videos অ্যাকাউন্ট সিলেকশন মেসেজ",
    "my_videos_cat_select_msg": "🎬 My Videos ক্যাটাগরি সিলেকশন মেসেজ",
    "my_videos_list_msg": "🎬 আমার ভিডিওসমূহ (My Videos) তালিকা মেসেজ",
    "pwd_change_old_prompt_msg": "🔑 পাসওয়ার্ড পরিবর্তন ১ম ধাপ (পুরাতন পাসওয়ার্ড)",
    "pwd_change_new_prompt_msg": "🔑 পাসওয়ার্ড পরিবর্তন ২য় ধাপ (নতুন পাসওয়ার্ড)",
    "pwd_change_confirm_prompt_msg": "🔑 পাসওয়ার্ড পরিবর্তন ৩য় ধাপ (কনফার্ম পাসওয়ার্ড)",
    "pwd_change_mismatch_msg": "❌ পাসওয়ার্ড অমিল সতর্কবার্তা",
    "pwd_change_success_msg": "✅ পাসওয়ার্ড পরিবর্তন সফল মেসেজ",
    "debt_bind_block_msg": "🚫 ঋণ থাকলে নতুন অ্যাকাউন্ট বাইন্ড ব্লক মেসেজ",
    "admin_user_activity_report_msg": "📋 অ্যাডমিন ইউজার কার্যক্রম বক্স রিপোর্ট টেমপ্লেট",
    "admin_random_code_generated_msg": "🔑 অ্যাডমিন র‍্যান্ডম কোড জেনারেটর মেসেজ টেমপ্লেট",
    "admin_delete_user_debt_confirm_msg": "⚠️ ঋণসহ ইউজার ডিলিট অ্যাডমিন কনফার্মেশন মেসেজ",
    "admin_logout_confirm_msg": "🔒 অ্যাডমিন প্যানেল লগআউট মেসেজ"
}

ADMIN_GUIDE_TEXT = (
    "🗺️ <b>ব্যাটেল ক্লাব — অ্যাডমিন গাইড ও নেভিগেশন ম্যাপ</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "<b>১. মেইন অ্যাডমিন প্যানেল:</b>\n"
    "• <b>📊 ড্যাশবোর্ড ও মেট্রিক্স:</b> ইউজার (Active, 24h/3-4d Inactive, Negative/Problem, Banned), ভিডিও (Pending, Bot/Admin/Permanent Approved, Rejected, Trash, Suspicious) ও ফিন্যান্সিয়াল লাইভ সামারি।\n"
    "• <b>📋 উইথড্র রিপোর্ট:</b> Pending, Paid, Cancelled এবং Rejected উইথড্র ম্যানেজমেন্ট।\n"
    "• <b>⏳ পেন্ডিং / 🤖 বট অ্যাপ্রুভ / 👑 অ্যাডমিন অ্যাপ্রুভ / 🔒 PERMANENT APPROVE / ❌ রিজেক্টেড:</b> প্রথমে YouTube ও TikTok বাটন দেখাবে এবং প্ল্যাটফর্ম সিলেক্ট করলে কোন ইউজার কতটি ভিডিও সাবমিট করেছেসহ তালিকা দেখাবে।\n"
    "• <b>🌐 ট্রাফিক সোর্স ও এক্সটার্নাল লিংক:</b> YouTube (YT) ও TikTok অনুযায়ী চ্যানেল, সার্চ ও এক্সটার্নাল লিংক পার্সেন্টেজ এবং Open Video, Reset ও Accept / Admin Approve বাটন।\n"
    "• <b>⚙️ কন্ট্রোল সেটিংস হাব:</b> Platform Settings, Video Earning, Withdraw Limit, Referral & Redeem, Anti-Fraud এবং General Settings (Database CSV Export ও Freelancing Ledger/Audit History সহ)।\n"
    "• <b>🛠️ অ্যাডভান্সড সেটিংস (Advanced Settings):</b> Button Name & Premium Emoji Editor, Message & Status Editor, এবং Button Position Change / Cross-Page Mover (লাইভ প্রিভিউসহ)।\n"
    f"{FULL_WIDTH_DIVIDER}"
)

COMMAND_SHORTCUT_CATEGORIES = {
    "admin": (
        "👑 <b>Admin Commands (অ্যাডমিন কমান্ড):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/admin</code> — অ্যাডমিন ওয়েলকাম ও মেইন প্যানেল ওপেন করুন\n"
        "• <code>/admin_guide</code> — অ্যাডমিন গাইড ও ম্যাপ দেখুন\n"
        "• <code>/commands</code> — সব কমান্ড ও শর্টকাট তালিকা দেখুন\n"
        "• <code>/metrics</code> — লাইভ ড্যাশবোর্ড মেট্রিক্স দেখুন"
    ),
    "users": (
        "👥 <b>User Management Commands (ইউজার ম্যানেজমেন্ট):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/users</code> — সকল ইউজার তালিকা দেখুন\n"
        "• <code>/user &lt;user_id&gt;</code> — নির্দিষ্ট ইউজারের প্রোফাইল ও কন্ট্রোল ওপেন করুন\n"
        "• <code>/search_user &lt;query&gt;</code> — নাম/নাম্বার/UID দিয়ে ইউজার খুঁজুন"
    ),
    "messages": (
        "✏️ <b>Message &amp; Button Editing Commands (মেসেজ ও বাটন এডিটিং):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/messages</code> — মেসেজ ও প্রিমিয়াম ইমোজি এডিটর ওপেন করুন\n"
        "• <code>/buttons</code> — ডায়নামিক বাটন ও পজিশন এডিটর ওপেন করুন\n"
        "• <code>/broadcast</code> — সকল ইউজারকে ব্রডকাস্ট পাঠান"
    ),
    "config": (
        "⚙️ <b>Configuration Commands (কনফিগারেশন কমান্ড):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/settings</code> — কন্ট্রোল সেটিংস হাব ওপেন করুন\n"
        "• <code>/platforms</code> — মাল্টি-প্ল্যাটফর্ম শর্ত ও রেট সেটিংস\n"
        "• <code>/rates</code> — ভিউ রেট, মেয়াদ ও ইন্টারভ্যাল সেটিংস"
    ),
    "finance": (
        "💰 <b>Financial Commands (ফিন্যান্সিয়াল ও উইথড্র কমান্ড):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/withdrawals</code> — উইথড্র রিপোর্ট (Pending/Paid/Cancelled/Rejected) দেখুন\n"
        "• <code>/ledger</code> — ফিন্যান্সিয়াল লেজার ও অডিট হিস্ট্রি দেখুন"
    ),
    "verification": (
        "🛡️ <b>Verification Commands (ভিডিও যাচাই ও অনুমোদন):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/pending</code> — পেন্ডিং ভিডিও তালিকা\n"
        "• <code>/bot_approve</code> — বট অ্যাপ্রুভ তালিকা\n"
        "• <code>/admin_approve</code> — অ্যাডমিন অ্যাপ্রুভড ভিডিও তালিকা\n"
        "• <code>/perm_approve</code> — স্থায়ী অনুমোদিত ভিডিও তালিকা\n"
        "• <code>/rejected</code> — রিজেক্টেড ভিডিও ও রিভার্সাল তালিকা"
    ),
    "database": (
        "📂 <b>Database Commands (ডেটাবেস ও ট্র্যাশ কমান্ড):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/trash</code> — রিসাইকেল বিন / ট্র্যাশ তালিকা দেখুন\n"
        "• <code>/export</code> — ডেটাবেস CSV এক্সপোর্ট ও লেজার হাব ওপেন করুন"
    ),
    "troubleshooting": (
        "🔧 <b>Troubleshooting Commands (সমস্যা সমাধান):</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "• <code>/start</code> — ইউজার ফ্লো ও লগইন প্রম্পট রিলোড করুন\n"
        "• <code>/run_monitor</code> — ম্যানুয়ালি ভিউ ও ভেরিফিকেশন মনিটরিং পাস রান করুন"
    )
}


def build_full_command_shortcut_text(category: str = "all") -> str:
    """Builds the formatted Command & Shortcut reference text by category or all categories."""
    cat = str(category or "all").lower().strip()
    if cat in COMMAND_SHORTCUT_CATEGORIES:
        return COMMAND_SHORTCUT_CATEGORIES[cat]
    header = (
        "⌨️ <b>ব্যাটেল ক্লাব — কমান্ড ও শর্টকাট তালিকা</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "প্রতিটি কাজের Direct Command এবং সংশ্লিষ্ট Button নিচে ক্যাটাগরি অনুযায়ী দেওয়া হলো:"
    )
    sections = [header] + list(COMMAND_SHORTCUT_CATEGORIES.values())
    return "\n\n".join(sections)


DEFAULT_BUTTON_LABELS_EN = {
    "u_dashboard": "📊 Dashboard",
    "u_profile": "👤 Profile",
    "u_submit": "📹 Submit Video",
    "u_my_videos": "🎬 My Videos",
    "u_withdraw": "💸 Withdraw Request",
    "u_wd_list": "📋 Withdrawal List",
    "u_history": "💳 Payment List",
    "u_link_more": "➕ Add New Account",
    "u_leaderboard": "🏆 Leaderboard",
    "u_settings_hub": "⚙️ Settings",
    "u_referral": "🎁 Refer",
    "u_redeem": "🎟️ Redeem",
    "u_activity": "📜 Account Activity",
    "u_pwd_change": "🔑 Change Password",
    "u_logout": "🔒 Logout",
    "u_color": "🎨 Button Color",
    "u_lang": "🌐 Change Language",
    "u_bottom_toggle": "⌨️ Bottom Menu Mode",
    "u_delete_acc": "🗑️ Delete Account",
    "u_how_to_work": "🎥 How to Work",
    "u_support": "💬 Support",
    "u_group": "👥 Group",
    "u_back_home": "🔙 Back to Home Page",
    "u_back_dashboard": "📊 Back to Dashboard",
    "u_prof_change_name": "✏️ Change Name",
    "u_prof_change_acc_name": "✏️ Change Account Name",
    "u_prof_change_uid": "🆔 Change Battle Club UID",
    "u_prof_change_wd": "📱 Change Withdraw Number",
    "a_metrics": "📊 Dashboard & Metrics",
    "a_wd_reports": "📋 Withdrawal Reports",
    "a_pending_vids": "⏳ Pending Videos",
    "a_bot_approve": "🤖 Bot Approved",
    "a_admin_approve": "👑 Admin Approved Videos",
    "a_perm_approve": "🔒 PERMANENT APPROVE",
    "a_rejected_vids": "❌ Rejected Videos & Reversals",
    "a_trash": "🗑️ Trash / Recycle Bin",
    "a_user_list": "👥 User List & History",
    "a_all_vids": "🎬 All Submitted Videos",
    "a_traffic_hub": "🌐 Traffic Source & External Links",
    "a_broadcast": "📢 Broadcast Message",
    "a_settings": "⚙️ Control Settings Hub",
    "a_adv_settings": "🛠️ Advanced Settings",
    "a_tutorial_vid": "🎥 Video Link (How to Work)",
    "a_bottom_toggle": "⌨️ Admin Bottom Menu",
    "a_logout": "🔒 Admin Logout",
    "a_user_home": "🏠 User Home Page",
    "a_super_admin_panel": "👑 Super Admin Panel"
}

DEFAULT_MESSAGES_EN = {
    "welcome_msg": (
        "👋 <b>Welcome to BATTLE CLUB CREATORS!</b> 🎉\n\n"
        "🌟 Start your creator journey with BATTLE CLUB.\n\n"
        f"{FULL_WIDTH_DIVIDER}\n\n"
        "👇 <b>Select your desired option from the menu below:</b> 🚀"
    ),
    "dashboard_msg": (
        "📊 <b>BATTLE CLUB | USER DASHBOARD ({user_label})</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "👤 Account Name: <b>{name}</b> | UID: <code>{user_id}</code>\n"
        "📺 Channel/Profile: <b>{channel_name}</b>\n"
        "🆔 Battle Club UID: <code>{app_uid}</code>\n"
        "📱 Payment Numbers: <code>{phone}</code>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "🏆 <b>Leaderboard & Target:</b>\n{leaderboard_progress}\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "💰 Available Balance: <b>{balance} BDT</b>\n"
        "🔒 Held Balance: <b>{held_balance} BDT</b>\n"
        "📉 Negative / Debt Balance: <b>{debt_balance} BDT</b>\n"
        "🏆 Total Earned: <b>{total_earned} BDT</b>\n"
        "💳 Total Withdraw Amount: <b>{wd_paid_amt} BDT</b>\n"
        "📌 Financial Status: <b>{financial_status}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "🎬 Submitted: <b>{videos_submitted}</b> | ⏳ Pending: <b>{videos_pending}</b>\n"
        "🤖 Bot Approved: <b>{videos_bot_approved}</b> | 👑 Admin Approved: <b>{videos_admin_approved}</b>\n"
        "🔒 Permanent Approved: <b>{videos_perm_approved}</b> | ❌ Rejected: <b>{videos_rejected}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "💸 Total WD Requests: <b>{wd_total_cnt} ({wd_total_amt} BDT)</b>\n"
        "✅ Completed: <b>{wd_paid_cnt} ({wd_paid_amt} BDT)</b> | ⏳ Pending: <b>{wd_pend_cnt} ({wd_pend_amt} BDT)</b>\n"
        "🔄 Cancelled: <b>{wd_canc_cnt}</b> | ❌ Rejected: <b>{wd_rej_cnt}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "📌 Mandatory Hashtag: <code>{global_code}</code>\n"
        "🔐 Next Video Code: <code>{unique_code}</code>\n"
        "🧬 Bio Verification Code: <code>{bio_code}</code>\n"
        "🎁 Referral Code: <code>{ref_code}</code>"
    ),
    "profile_msg": (
        "👤 <b>BATTLE CLUB | USER PROFILE ({user_label})</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "👤 Name: <b>{name}</b>\n"
        "📺 Channel/Profile: <b>{channel_name}</b>\n"
        "🆔 Battle Club UID: <code>{app_uid}</code>\n"
        "📱 Payment Numbers: <code>{phone}</code>\n"
        "🌐 Verified Platforms:\n<b>{platforms_summary}</b>\n"
        f"{FULL_WIDTH_DIVIDER}\n"
        "🧬 Bio Verification Code: <code>{bio_code}</code>\n"
        "🔐 Next Video Code: <code>{unique_code}</code>"
    )
}

# Missing message templates & aliases for 100% zero-mismatch coverage
DEFAULT_MESSAGES["my_videos_platform_select_msg"] = DEFAULT_MESSAGES["my_videos_plat_select_msg"]
DEFAULT_MESSAGES["my_videos_account_select_msg"] = DEFAULT_MESSAGES["my_videos_acc_select_msg"]
DEFAULT_MESSAGES["reg_yt_channel_name_input_msg"] = (
    '<tg-emoji emoji-id="5287575882108522821">📺</tg-emoji> <b>YouTube চ্যানেলের নাম প্রদান করুন (ধাপ ৪/৭)</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> আপনার ভেরিফাই করা <b>📺 YouTube</b> চ্যানেলের নাম নিচে লিখে পাঠান:'
)
DEFAULT_MESSAGES["reg_tt_channel_name_input_msg"] = (
    '<tg-emoji emoji-id="5287575882108522821">🎵</tg-emoji> <b>TikTok অ্যাকাউন্টের নাম প্রদান করুন (ধাপ ৪/৭)</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    '<tg-emoji emoji-id="5197269100878907942">✍️</tg-emoji> আপনার ভেরিফাই করা <b>🎵 TikTok</b> অ্যাকাউন্টের নাম নিচে লিখে পাঠান:'
)
DEFAULT_MESSAGES["admin_platform_settings_msg"] = (
    '🌐 <b>PLATFORM &amp; TRAFFIC SETTINGS (মাল্টি-প্ল্যাটফর্ম ও ট্রাফিক সোর্স সেটিংস)</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    'এখান থেকে <b>YouTube</b> এবং <b>TikTok</b> প্ল্যাটফর্মের ভেরিফিকেশন শর্ত (সাবস্ক্রাইবার/ফলোয়ার, পাবলিক ভিডিও, যোগ্য ভিডিও, ন্যূনতম ভিউ, ভেরিফিকেশন লিংক), ভিউ রেট ও পেন্ডিং ম্যাপ (Pending Map), এবং ট্রাফিক সোর্স ও এক্সটার্নাল লিংক বিশ্লেষণ পরিচালনা করুন:'
)
DEFAULT_MESSAGES["admin_db_export_hub_msg"] = (
    '📂 <b>DATABASE CSV EXPORT &amp; FINANCIAL LEDGER HUB</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    'এখান থেকে সম্পূর্ণ ইউজার ডাটাবেস CSV ফাইলে এক্সপোর্ট করুন এবং <b>Freelancing Financial Ledger History</b> ও <b>System Audit History</b> প্রতিটি লেনদেন আলাদা লম্বা দাগ ও স্পেসিংসহ পরিষ্কারভাবে দেখুন:'
)

MESSAGE_TEMPLATE_LABELS.update({
    "my_videos_platform_select_msg": "🎬 My Videos প্ল্যাটফর্ম সিলেকশন মেসেজ",
    "my_videos_account_select_msg": "🎬 My Videos অ্যাকাউন্ট সিলেকশন মেসেজ",
    "reg_yt_channel_name_input_msg": "📺 YouTube চ্যানেলের নাম ইনপুট মেসেজ",
    "reg_tt_channel_name_input_msg": "🎵 TikTok অ্যাকাউন্টের নাম ইনপুট মেসেজ",
    "admin_platform_settings_msg": "🌐 মাল্টি-প্ল্যাটফর্ম সেটিংস হাব মেসেজ",
    "admin_db_export_hub_msg": "📂 ডাটাবেস CSV ও লেজার হাব মেসেজ"
})

PAGE_LAYOUT_TITLES.update({
    "admin_platform_settings": "🌐 অ্যাডমিন প্ল্যাটফর্ম সেটিংস (Platform Settings)",
    "admin_advanced_settings": "🛠️ অ্যাডমিন অ্যাডভান্সড সেটিংস (Advanced Settings)"
})

DEFAULT_LAYOUTS["admin_platform_settings"] = [
    ["a_plat_settings"],
    ["a_rate_settings"],
    ["a_antifraud_settings"],
    ["a_back_admin"]
]
DEFAULT_LAYOUTS["admin_advanced_settings"] = [
    ["a_btn_editor"],
    ["a_msg_hub"],
    ["a_btn_pos_editor"],
    ["a_lb_customizer"],
    ["a_tutorial_vid"],
    ["a_back_admin"]
]

BUTTON_TEXT_DESIGN_STYLES = {
    "normal": "Normal (সাধারণ)",
    "bold": "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀 (গাঢ় স্টাইল)",
    "bold_sans": "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀 (গাঢ় স্যান্স)",
    "serif_bold": "𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟 (সেরিফ বোল্ড)",
    "bold_serif": "𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟 (সেরিফ বোল্ড)",
    "monospace": "𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎 (মনোস্পেস)",
    "small_caps": "ꜱᴍᴀʟʟ ᴄᴀᴘꜱ (স্মল ক্যাপস)",
    "bracket": "【 Bracket 】 (ব্র্যাকেট ডিজাইন)",
    "brackets": "【 Brackets 】 (ব্র্যাকেট ডিজাইন)",
    "bracketed": "【 Bracketed 】 (ব্র্যাকেট ডিজাইন)",
    "sparkle": "✨ Sparkle ✨ (স্পার্কল ডিজাইন)",
    "star": "✦ Star ✦ (স্টার ডিজাইন)",
    "diamond": "❖ Diamond ❖ (ডায়মন্ড ডিজাইন)",
    "double_bar": "⟦ Double Bar ⟧ (ডাবল বার)",
}
BUTTON_DESIGN_STYLES = BUTTON_TEXT_DESIGN_STYLES

_BOLD_SANS_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
)
_BOLD_SERIF_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
)
_MONO_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
)
_SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ",
)

import re as _re

_CATALOG_HEART_VARIANTS_RE = _re.compile(r"([\u2764\u2665\u2661\u2763\u2765])(?![\ufe0f\u200d])")
_CATALOG_BMP_EMOJI_SYMBOLS_RE = _re.compile(
    r"([\u2600\u2601\u260e\u2611\u2614\u2615\u261d\u2620\u2622\u2623\u2626\u262a\u262e\u262f"
    r"\u2638\u2639\u263a\u2648-\u2653\u2660\u2663\u2665\u2666\u2668\u267b\u267f\u2692-\u2697"
    r"\u2699\u269b\u269c\u26a0\u26a1\u26b0\u26b1\u26bd\u26be\u26c4\u26c5\u26c8\u26ce\u26cf"
    r"\u26d1\u26d3\u26d4\u26e9\u26ea\u26f0-\u26f5\u26f7-\u26fa\u26fd\u2702\u2708\u2709\u270c"
    r"\u270d\u270f\u2712\u2714\u2716\u271d\u2721\u2733\u2734\u2744\u2747\u2757\u2763\u2764"
    r"\u27a1\u2934\u2935\u2b05-\u2b07\u25b6\u25c0\u2139\u3030\u303d\u3297\u3299])(?![\ufe0f\ufe0e\u200d\u20e3])"
)


def ensure_visible_emoji_presentation(text: str) -> str:
    if not text:
        return ""
    s = str(text)
    s = _re.sub(r"[\u2665\u2661](?![\ufe0f\u200d])", "\u2764\ufe0f", s)
    s = _CATALOG_HEART_VARIANTS_RE.sub(lambda m: ("\u2764\ufe0f" if m.group(1) in ("\u2764", "\u2765") else m.group(1) + "\ufe0f"), s)
    s = _CATALOG_BMP_EMOJI_SYMBOLS_RE.sub(lambda m: m.group(1) + "\ufe0f", s)
    s = _re.sub(r"\ufe0f{2,}", "\ufe0f", s)
    return s


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

LAYOUT_PAGE_TITLES = PAGE_LAYOUT_TITLES

PLATFORM_SETTINGS_SUBMENUS = [
    ("📺 YouTube ও 🎵 TikTok ভেরিফিকেশন শর্ত ও রেট", "adm_crit:hub", "primary"),
    ("📈 ভিউ রেট, পেন্ডিং ম্যাপ ও মেয়াদ সেটিংস", "adm_edit_rate_days", "success"),
    ("🛡️ অ্যান্টি-ফ্রড ও অর্গানিক রিস্ক সেটিংস", "adm_shub:antifraud", "primary"),
]

GENERAL_SETTINGS_SUBMENUS = [
    ("🎁 রেফার ও রিডিম সেটিংস", "adm_edit_ref_hub", "success"),
    ("🛡️ অ্যান্টি-ফ্রড ও অর্গানিক রিস্ক সেটিংস", "adm_shub:antifraud", "danger"),
    ("🛠️ ম্যানুয়াল প্রসেসিং ও নাম্বার চেঞ্জ র‍্যান্ডম কোড", "adm_man_ver:hub", "primary"),
    ("🔐 হ্যাশট্যাগ, ভেরিফিকেশন লিংক ও ভিডিও লিংক সেটআপ", "adm_shub:hashtag_yt", "success"),
    ("💬 সাপোর্ট ও গ্রুপ লিংক পরিবর্তন", "adm_shub:support_group", "primary"),
    ("📂 ডেটাবেস CSV এক্সপোর্ট ও ফিন্যান্সিয়াল লেজার/অডিট হিস্ট্রি", "adm_db_export_hub", "success"),
    ("🗺️ অ্যাডমিন গাইড ও ম্যাপ", "adm_guide_map", "primary"),
    ("⌨️ কমান্ড ও শর্টকাট তালিকা", "adm_cmd_shortcuts", "success"),
]

ADVANCED_SETTINGS_SUBMENUS = [
    ("🎛️ Button Name & Premium Custom Emoji Editor", "adm_btn_editor_hub", "success"),
    ("✏️ Message, Status & Premium Custom Emoji Editor", "adm_msg_hub", "primary"),
    ("📐 Button Position Change / বাটনের জায়গা পরিবর্তন করুন", "adm_bpos_hub", "success"),
    ("🏆 লিডারবোর্ড কাস্টমাইজার (Rank 1-10 ও নামের স্টাইল)", "adm_lb_customizer", "primary"),
]


LAYOUT_SHORT_CODE_MAP = {
    "user_home": "uh",
    "user_settings_hub": "us",
    "user_dashboard": "ud",
    "user_profile": "up",
    "admin_home": "ah",
    "admin_settings_hub": "as",
    "admin_platform_settings": "ap",
    "admin_general_settings": "ag",
    "admin_advanced_settings": "aa",
}
SHORT_CODE_LAYOUT_MAP = {v: k for k, v in LAYOUT_SHORT_CODE_MAP.items()}


DEFAULT_MESSAGES["how_to_work_video_msg"] = (
    '🎥 <b>কিভাবে কাজ করবেন — সম্পূর্ণ টিউটোরিয়াল ভিডিও (HOW TO WORK)</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    'উপরে দেওয়া ভিডিওটি প্লে করে দেখুন কীভাবে অ্যাকাউন্ট ভেরিফিকেশন করবেন, স্পন্সর ভিডিও আপলোড ও সাবমিট করবেন এবং উইথড্র দিয়ে পেমেন্ট গ্রহণ করবেন।\n\n'
    '📌 <b>মূল নিয়মাবলি:</b>\n'
    '১. আপনার ভেরিফাইড YouTube বা TikTok অ্যাকাউন্টের Bio/Description-এ ভেরিফিকেশন কোড বা লিংক যুক্ত রাখুন।\n'
    '২. প্রতিটি স্পন্সর ভিডিওর Title/Description/Comment-এ র‍্যান্ডম ভিডিও কোড ও বাধ্যতামূলক হ্যাশট্যাগ ব্যবহার করুন।\n'
    '৩. ভিডিও পাবলিক করার নির্ধারিত সময়ের মধ্যে বটে লিংক সাবমিট করুন।'
)
DEFAULT_MESSAGES_EN["how_to_work_video_msg"] = (
    '🎥 <b>HOW TO WORK — COMPLETE TUTORIAL VIDEO</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    'Watch the tutorial video at the top of this message to learn step-by-step how to verify your channel, submit sponsor videos, track organic views, and withdraw your earnings.\n\n'
    '📌 <b>Key Rules:</b>\n'
    '1. Keep your verification code or link in your verified YouTube Description or TikTok Bio.\n'
    '2. Include the unique video code and mandatory hashtags in your video Title, Description, or Comment.\n'
    '3. Submit your public video link within the required submission time window.'
)
MESSAGE_TEMPLATE_LABELS["how_to_work_video_msg"] = "🎥 কিভাবে কাজ করবেন (How to Work) টিউটোরিয়াল মেসেজ"

# ==============================================================================
# ENTERPRISE v9.0 AUDIT FIX ADDITIONS (OAUTH, UID ENFORCEMENT & WIZARD TEMPLATES)
# ==============================================================================
DEFAULT_SETTINGS.setdefault("require_app_uid_in_video", "0")
DEFAULT_SETTINGS.setdefault("youtube_oauth_access_token", "")
DEFAULT_SETTINGS.setdefault("tiktok_oauth_access_token", "")

SETTING_FIELD_EXPLANATIONS.setdefault(
    "require_app_uid_in_video",
    "এটি চালু (1) করলে ইউজারের সাবমিট করা ভিডিওর Title, Description বা Comment-এ ইউনিক কোডের পাশাপাশি ইউজারের Battle Club UID থাকা বাধ্যতামূলক হবে।"
)

DEFAULT_MESSAGES.setdefault("custom_button_preview_confirm_msg", (
    "👁️ <b>নতুন কাস্টম বাটন ফাইনাল প্রিভিউ ও কনফার্মেশন (Final Preview)</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "• বাটন আইডি (UUID): <code>{cbtn_key}</code>\n"
    "• বাটনের নাম: <b>{label}</b>\n"
    "• সাইড (Side): <b>{side_label}</b>\n"
    "• প্যারেন্ট পেজ (Parent Page): <b>{parent_page_title}</b>\n"
    "• গন্তব্য পেজ (Destination Page): <b>{dest_page_title}</b>\n"
    "• নির্ধারিত লাইন ও পজিশন (Row &amp; Position): <b>Row #{row_num}, Col #{col_num} ({position_mode})</b>\n"
    "• ভেতরে নির্বাচিত সাব-বাটন ({sub_count}টি): <b>{sub_buttons_summary}</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "📝 <b>বাটনের উপরের স্ট্যাটাস মেসেজ প্রিভিউ:</b>\n{status_msg_preview}\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "✅ নিচের <b>Confirm &amp; Save Button</b>-এ ক্লিক করলেই কেবল Database Transaction-এর মাধ্যমে বাটনটি নির্ধারিত স্থানে যুক্ত হবে:"
))

# ==============================================================================
# ENTERPRISE v10.0 ADDITIONS (LEADERBOARD CUSTOMIZER, MULTI-WD NUMBERS & GROUP JOIN)
# ==============================================================================
DEFAULT_BUTTON_LABELS["a_lb_customizer"] = "🏆 লিডারবোর্ড কাস্টমাইজার (Rank 1-10 ও স্টাইল)"
DEFAULT_BUTTON_LABELS_EN["a_lb_customizer"] = "🏆 Leaderboard Customizer"
DEFAULT_BUTTON_EMOJIS["a_lb_customizer"] = ""
SETTINGS_ONLY_BUTTON_KEYS = tuple(list(SETTINGS_ONLY_BUTTON_KEYS) + ["a_lb_customizer"])

DEFAULT_SETTINGS.setdefault("leaderboard_name_style", "bold_sans")
for _rk_i, _rk_med in enumerate(["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"], start=1):
    DEFAULT_SETTINGS.setdefault(f"leaderboard_rank_{_rk_i}_badge", f"{_rk_med} Top {_rk_i}")

DEFAULT_MESSAGES["profile_name_submenu_msg"] = (
    "✏️ <b>নাম, Battle Club UID ও ভেরিফিকেশন অ্যাকাউন্টের নাম পরিবর্তন</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "আপনি নিচের ৩টি অপশন থেকে আপনার <b>নিজের অ্যাকাউন্টের নাম</b>, <b>Battle Club অ্যাপের UID</b> এবং <b>ভেরিফিকেশন অ্যাকাউন্টের / প্ল্যাটফর্মের নাম</b> পরিবর্তন করতে পারবেন:"
)

DEFAULT_MESSAGES["profile_wd_num_submenu_msg"] = (
    "📱 <b>উইথড্র নাম্বার ও UID পরিবর্তন / সংযোজন (Withdraw Number &amp; UID Manager)</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "╭─── 💳 <b>আপনার সংরক্ষিত পেমেন্ট নাম্বার ও UID সমূহ</b> ───╮\n"
    "{selected_methods_summary}\n"
    "╰────────────────────────────────────────╯\n"
    "📌 <b>নিয়ম:</b> বিকাশ (bKash), নগদ (Nagad), রকেট (Rocket) এবং Battle Club App UID—প্রতিটি মাধ্যমে <b>সর্বোচ্চ ২টি করে</b> নাম্বার বা UID সেট করা যাবে। ১টি সেট করা থাকলে পরবর্তীতে আরও ১টি যুক্ত করতে পারবেন; আর ২টি সেট করা হয়ে গেলে যেকোনো ১টি ডিলিট বা পরিবর্তন করে নতুন নাম্বার/UID সেট করতে পারবেন (২টির অধিক সেট করা যাবে না)।"
)

DEFAULT_MESSAGES["admin_user_history_msg"] = (
    '<tg-emoji emoji-id="5453957997418004470">👥</tg-emoji> <b>USER LIST &amp; ACTIVITY HISTORY</b>\n'
    f'{FULL_WIDTH_DIVIDER}\n'
    '📊 মোট নিবন্ধিত ইউজার: <b>{total_users} জন</b>\n'
    '🔵 <b>[AC]:</b> Active | 🟡 <b>[AN]:</b> Inactive | ❄️ <b>[FR]:</b> Frozen | 🔴 <b>[BN]:</b> Banned\n'
    f'{FULL_WIDTH_DIVIDER}'
)

DEFAULT_MESSAGES["video_deleted_freeze_msg"] = (
    "❄️ <b>জরুরি সতর্কবার্তা — আপনার সাবমিট করা ভিডিওটি কেন প্রাইভেট বা ডিলিট করেছেন?</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "🎬 ভিডিও: <b>{title}</b> ({platform})\n"
    "⚠️ ট্র্যাকিং চলাকালীন সোশ্যাল প্ল্যাটফর্ম থেকে আপনার সাবমিট করা ভিডিওটি ডিলিট অথবা প্রাইভেট করে দেওয়া হয়েছে!\n"
    "🛑 এই ভিডিওটির ভিউ গণনা এবং পেমেন্ট যোগ হওয়া তাৎক্ষণিকভাবে বন্ধ করা হয়েছে। কেন ভিডিওটি প্রাইভেট বা ডিলিট করা হয়েছে তা জানিয়ে সমাধানের জন্য সাপোর্টে যোগাযোগ করুন: {support_link}"
)

DEFAULT_MESSAGES.setdefault("video_submit_group_join_msg", (
    "📢 <b>ভিডিও সাবমিট করার পূর্বে আমাদের অফিসিয়াল টেলিগ্রাম গ্রুপে জয়েন করুন!</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "⚠️ স্পন্সর ভিডিও সাবমিট করার জন্য প্রথমে আমাদের অফিসিয়াল টেলিগ্রাম গ্রুপে জয়েন থাকা বাধ্যতামূলক।\n\n"
    "১️⃣ নিচের <b>👥 অফিসিয়াল গ্রুপে জয়েন করুন</b> বাটনে ক্লিক করে গ্রুপে জয়েন হন।\n"
    "২️⃣ জয়েন করার পর নিচের <b>✅ জয়েন করেছি — ভিডিও সাবমিটে যান</b> বাটনে ক্লিক করুন:"
))

DEFAULT_MESSAGES.setdefault("video_submit_expired_msg", (
    "⏰ <b>আপনার এই ভিডিওর সাবমিট করার মেয়াদ শেষ!</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "📌 ইউটিউব বা টিকটকে ভিডিও পাবলিক করার পর নির্ধারিত <b>{max_hours} ঘণ্টা ({max_days} দিন)</b> সময়সীমার মধ্যে বটে লিংক সাবমিট করতে হয়।\n"
    "⚠️ আপনার এই ভিডিওর সাবমিট করার মেয়াদ শেষ হয়ে যাওয়ায় এটি গ্রহণ করা সম্ভব হয়নি। নতুন পাবলিক করা ভিডিও সাবমিট করুন।"
))

DEFAULT_MESSAGES.setdefault("video_counting_completed_msg", (
    "🎉 <b>আপনার এই ভিডিওর ভিউজ গণনা করা কমপ্লিট!</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "🎬 ভিডিওর নাম: <b>{title}</b>\n"
    "👁️ চূড়ান্ত গণনাকৃত ভিউ: <b>{views} ভিউ</b>\n"
    "💰 মোট অর্জিত আয়: <b>{credited} টাকা</b>\n"
    "🔒 বর্তমান স্ট্যাটাস: <b>Permanent Approved ✅</b>\n"
    f"{FULL_WIDTH_DIVIDER}\n"
    "ℹ️ <b>আপনার এই ভিডিওর নির্ধারিত ভিউজ গণনা করার সময়সীমা / সর্বোচ্চ ভিউ ক্যাপ সম্পূর্ণ হয়েছে। এখন আর এই ভিডিওর ভিউজ গণনা করা হবে না এবং নতুন কোনো টাকা যুক্ত হবে না।</b>"
))

MESSAGE_TEMPLATE_LABELS.update({
    "video_submit_group_join_msg": "👥 ভিডিও সাবমিট গ্রুপ জয়েন নোটিফিকেশন মেসেজ",
    "video_submit_expired_msg": "⏰ ভিডিও সাবমিট করার মেয়াদ শেষ মেসেজ",
    "video_counting_completed_msg": "🎉 ভিডিওর ভিউজ গণনা কমপ্লিট (Permanent Approve) মেসেজ",
})