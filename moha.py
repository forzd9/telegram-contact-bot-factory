# Colored by • 𝗠َِ𝗢َِ𝗛َِ𝗔َ | مــــووحــــا • (@mouhamed_ma)
# -*- coding: utf-8 -*-
# 𝗠َِ𝗢َِ𝗨َِ𝗛َِ𝗔َِ𝗠َِ𝗘َِ𝗗َِ 𝗠َِ𝗔🇮🇹   @mouhamed_ma
import sys
import subprocess
import importlib

REQUIRED_PACKAGES = {
    "telebot": "pyTelegramBotAPI",
    "requests": "requests",
    "psutil": "psutil",
}

for module, package in REQUIRED_PACKAGES.items():
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"📦 جاري تثبيت {package}...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            package
        ])

print("✅ تم تجهيز جميع المكتبات المطلوبة.")
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
import requests
import time
import sys
import os
import psutil
import signal
import json
import threading
import random
import string
from datetime import datetime
from typing import Dict, Set, List, Optional, Tuple, Any

# ========== الثوابت والهوية ==========
_CREDIT = "𝗠َِ𝗢َِ𝗨َِ𝗛َِ𝗔َِ𝗠َِ𝗘َِ𝗗َِ 𝗠َِ𝗔🇮🇹"
_FACTORY_USERNAME = "moha_ma_bot"
_MASTER_TOKEN = "8807664301:AAHwVEe2LpwMwLIbi9uiKY2WhPAtgI5KIdU"
_MASTER_ID = 6891530912
_DATA_FILE = "bots_data.json"
_LOCK_FILE = "bot.lock"
_SESSION_STORE: Dict[int, Dict[str, Any]] = {}

# قنوات الاشتراك الإجباري للمصنع (تضاف افتراضياً)
DEFAULT_FACTORY_CHANNELS = ["forzd9", "mouhamed_maa", "mouhamed_maaaa", "Illegal_tools"]

# الصورة الموحدة للواجهة (للمصنع وجميع البوتات)
DEFAULT_WELCOME_PHOTO = "https://a.top4top.io/p_38428earr0.png"

# قناة الإثباتات (إرسال إشعارات إنشاء البوتات الجديدة)
PROOF_CHANNEL = "@mouhamed_maa"

# التأثيرات المتاحة
_AVAILABLE_EFFECTS = {
    "👍": "5107584321108051014",
    "👎": "5104858069142078462",
    "❤️": "5159385139981059251",
    "🔥": "5104841245755180586",
    "🎉": "5046509860389126442",
    "💩": "5046589136895476101"
}

# أنواع الوسائط الممنوعة
_MEDIA_TYPES_MAP = {
    'audio': 'الملفات الصوتية',
    'document': 'المستندات',
    'sticker': 'الملصقات',
    'video': 'مقاطع الفيديو',
    'voice': 'الرسائل الصوتية',
    'contact': 'جهات الاتصال',
    'forward': 'الرسائل المُعاد توجيهها',
    'all_link': 'جميع الروابط',
    'telegram_link': 'روابط تيليجرام'
}

_BANNED_MEDIA_KEYS = [
    'audio', 'document', 'sticker', 'video', 'voice',
    'contact', 'forward', 'all_link', 'telegram_link'
]

# ========== دوال مساعدة ==========
def _format_timestamp(ts: Optional[float] = None) -> str:
    dt = datetime.fromtimestamp(ts) if ts else datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _generate_request_id(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def _extract_message_info(m) -> Dict[str, Any]:
    user = m.from_user
    uid = user.id
    first_name = user.first_name or "غير متوفر"
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    username = f"@{user.username}" if user.username else "لا يوجد"
    if m.text:
        msg_type = "نص"
    elif m.photo:
        msg_type = "صورة"
    elif m.video:
        msg_type = "فيديو"
    elif m.document:
        msg_type = "ملف"
    elif m.audio:
        msg_type = "ملف صوتي"
    elif m.voice:
        msg_type = "رسالة صوتية"
    elif m.sticker:
        msg_type = "ملصق"
    else:
        msg_type = "نوع آخر"
    timestamp = _format_timestamp(m.date)
    language = user.language_code or "غير محدد"
    is_premium = "نعم" if getattr(user, 'is_premium', False) else "لا"
    return {
        'uid': uid,
        'full_name': full_name,
        'username': username,
        'message_type': msg_type,
        'timestamp': timestamp,
        'language': language,
        'is_premium': is_premium,
        'first_name': first_name,
        'last_name': last_name
    }

# ========== فئة بيانات البوت ==========
class BotData:
    __slots__ = (
        'owner_id', 'token', 'admin_id', 'channel_username',
        'developer_username', 'bot_name', 'bot_username',
        'banned_users', 'muted_users', 'registered_users',
        'users_counter', 'active_effect_id', 'welcome_photo_id',
        'is_running', 'sub_admins', 'auto_forward', 'typing_indicator',
        'reply_mode', 'receipt_message', 'welcome_caption',
        'banned_media_types', 'creation_time'
    )

    def __init__(self, owner_id: int, token: str, admin_id: int,
                 channel: str = "", developer: str = "",
                 bot_name: str = "", bot_username: str = ""):
        self.owner_id = owner_id
        self.token = token
        self.admin_id = admin_id or owner_id
        self.channel_username = channel or "mouhamed_maa"
        self.developer_username = developer
        self.bot_name = bot_name
        self.bot_username = bot_username
        self.banned_users: Set[int] = set()
        self.muted_users: Set[int] = set()
        self.registered_users: Set[int] = set()
        self.users_counter = 0
        self.active_effect_id = "5104841245755180586"
        self.welcome_photo_id = DEFAULT_WELCOME_PHOTO
        self.is_running = False
        self.sub_admins: Set[int] = set()
        self.auto_forward = True
        self.typing_indicator = True
        self.reply_mode = True
        self.receipt_message = "تم استلام رسالتك بنجاح، سيتم الرد عليك في أقرب وقت."
        self.welcome_caption = ""
        self.banned_media_types: List[str] = []
        self.creation_time = datetime.now().isoformat()

# ========== فئة تشغيل البوت ==========
class BotInstance:
    def __init__(self, data: BotData, factory=None):
        self.data = data
        self.bot = telebot.TeleBot(data.token)
        self._stop_event = threading.Event()
        self._factory = factory

    def _back_button(self, callback_data: str) -> List[InlineKeyboardButton]:
        return [InlineKeyboardButton("⬅️ رجوع", callback_data=callback_data, style="primary")]  # تمت إضافة الإيموجي

    def _persist(self) -> None:
        if self._factory:
            self._factory._save_all_data()

    def _clear_inline_keyboard(self, msg, user_id: int, action: str) -> None:
        try:
            self.bot.edit_message_reply_markup(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                reply_markup=InlineKeyboardMarkup()
            )
            self.bot.send_message(
                msg.chat.id,
                f"<blockquote>✅ تم تنفيذ الإجراء: <b>{action}</b> للمستخدم <code>{user_id}</code></blockquote>",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"markup update error: {e}")

    def _is_admin(self, user_id: int) -> bool:
        return (user_id == self.data.admin_id or
                user_id == self.data.owner_id or
                user_id in self.data.sub_admins)

    def _is_message_banned(self, message) -> bool:
        if not self.data.banned_media_types:
            return False
        if 'forward' in self.data.banned_media_types and message.forward_from:
            return True
        if message.photo and 'photo' in self.data.banned_media_types:
            return True
        if message.video and 'video' in self.data.banned_media_types:
            return True
        if message.audio and 'audio' in self.data.banned_media_types:
            return True
        if message.voice and 'voice' in self.data.banned_media_types:
            return True
        if message.document and 'document' in self.data.banned_media_types:
            return True
        if message.sticker and 'sticker' in self.data.banned_media_types:
            return True
        if message.contact and 'contact' in self.data.banned_media_types:
            return True
        if 'all_link' in self.data.banned_media_types and message.text:
            if 'http://' in message.text or 'https://' in message.text:
                return True
        if 'telegram_link' in self.data.banned_media_types and message.text:
            if 't.me/' in message.text or 'telegram.me/' in message.text:
                return True
        return False

    def _send_typing(self, chat_id: int) -> None:
        if self.data.typing_indicator:
            try:
                self.bot.send_chat_action(chat_id, 'typing')
            except Exception:
                pass

    def _get_user_photo(self, user_id: int) -> Optional[str]:
        try:
            photos = self.bot.get_user_profile_photos(user_id, limit=1)
            if photos.total_count > 0:
                return photos.photos[0][-1].file_id
        except Exception:
            pass
        return None

    def _register_handlers(self) -> None:
        bot = self.bot
        data = self.data
        instance = self

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            data.users_counter += 1
            user_id = message.from_user.id
            is_new_user = user_id not in data.registered_users
            if is_new_user:
                data.registered_users.add(user_id)
                instance._persist()

                admin_id = data.admin_id
                try:
                    user_photo = instance._get_user_photo(user_id)
                    info = _extract_message_info(message)
                    caption = (
                        f"<blockquote>🆕 <b>مستخدم جديد سجّل في البوت</b>\n\n"
                        f"🆔 الآيدي: <code>{info['uid']}</code>\n"
                        f"👤 الاسم: {info['full_name']}\n"
                        f"🔗 اليوزر: {info['username']}\n"
                        f"⭐ بريميوم: {info['is_premium']}\n"
                        f"⏰ الوقت: {_format_timestamp()}\n"
                        f"👥 إجمالي المستخدمين: {len(data.registered_users)}</blockquote>"
                    )
                    if user_photo:
                        bot.send_photo(admin_id, user_photo, caption=caption, parse_mode="HTML")
                    else:
                        bot.send_message(admin_id, caption, parse_mode="HTML")
                except Exception as e:
                    print(f"Admin notification error: {e}")

            channel_url = f"https://t.me/{data.channel_username}" if data.channel_username else "https://t.me/telegram"
            developer_url = f"https://t.me/{data.developer_username}" if data.developer_username else "https://t.me/telegram"
            factory_url = f"https://t.me/{_FACTORY_USERNAME}"

            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.row(
                InlineKeyboardButton("📢 القناة الرسمية", url=channel_url, style="danger"),
                InlineKeyboardButton("👨‍💻 المطور", url=developer_url, style="danger")
            )
            keyboard.row(
                InlineKeyboardButton("🤖 إنشاء بوت تواصل خاص", url=factory_url, style="primary")
            )
            keyboard.row(
                InlineKeyboardButton("🆘 الدعم", callback_data="bot_support", style="success"),
                InlineKeyboardButton("❓ استفسار", callback_data="bot_inquiry", style="success")
            )
            keyboard.row(
                InlineKeyboardButton("📖 المساعدة", callback_data="bot_help", style="danger"),
                InlineKeyboardButton("📜 القوانين", callback_data="bot_rules", style="danger")
            )
            keyboard.row(
                InlineKeyboardButton("👤 حسابي", callback_data="bot_account", style="primary")
            )
            if instance._is_admin(user_id):
                keyboard.row(
                    InlineKeyboardButton("⚙️ لوحة الإدارة", callback_data="admin_panel", style="success")
                )

            first_name = message.from_user.first_name or "المستخدم"
            caption = data.welcome_caption if data.welcome_caption else (
                f"<blockquote>👋 مرحباً بك <b>{first_name}</b> في نظام التواصل الآلي.\n"
                f"يمكنك إرسال رسالتك الآن وسيتم توجيهها إلى الإدارة.</blockquote>"
            )

            bot.send_photo(
                chat_id=message.chat.id,
                photo=data.welcome_photo_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard,
                message_effect_id=data.active_effect_id
            )

        @bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
        def handle_admin_panel_callback(callback):
            user_id = callback.from_user.id
            if not instance._is_admin(user_id):
                bot.answer_callback_query(callback.id, "❌ غير مصرح.")
                return
            bot.answer_callback_query(callback.id)
            instance._send_admin_main(callback.message.chat.id)

        @bot.callback_query_handler(func=lambda c: c.data in ("bot_support", "bot_inquiry", "bot_help", "bot_rules", "bot_account"))
        def handle_bot_buttons(callback):
            user_id = callback.from_user.id
            action = callback.data

            if action in ("bot_support", "bot_inquiry"):
                bot.answer_callback_query(callback.id, "📩 أرسل رسالتك")
                prompt = bot.send_message(callback.message.chat.id, "<blockquote>📩 أرسل رسالتك وسيتم إرسالها إلى فريق الدعم.</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._handle_support_inquiry)

            elif action == "bot_help":
                bot.answer_callback_query(callback.id)
                help_text = (
                    "<blockquote>📖 <b>المساعدة</b>\n\n"
                    "• يمكنك إرسال رسالتك وسيتم توجيهها للإدارة.\n"
                    "• استخدم زر <b>الدعم</b> للتواصل مع فريق الدعم.\n"
                    "• استخدم زر <b>استفسار</b> لطرح أي سؤال.\n"
                    "• لمشاهدة بياناتك، استخدم زر <b>حسابي</b>.\n"
                    "• للاطلاع على القوانين، استخدم زر <b>القوانين</b>.\n\n"
                    "شكراً لاستخدامك البوت.</blockquote>"
                )
                bot.send_message(callback.message.chat.id, help_text, parse_mode="HTML")

            elif action == "bot_rules":
                bot.answer_callback_query(callback.id)
                rules_text = (
                    "<blockquote>📜 <b>القوانين</b>\n\n"
                    "1. الاحترام المتبادل بين جميع المستخدمين.\n"
                    "2. عدم إرسال محتوى غير لائق أو مسيء.\n"
                    "3. الالتزام بالتعليمات الصادرة من الإدارة.\n"
                    "4. يمنع نشر الروابط الضارة أو المزعجة.\n"
                    "5. يمنع التكرار أو الإزعاج.\n\n"
                    "نشكر التزامكم بالقوانين.</blockquote>"
                )
                bot.send_message(callback.message.chat.id, rules_text, parse_mode="HTML")

            elif action == "bot_account":
                bot.answer_callback_query(callback.id)
                user = callback.from_user
                account_text = (
                    f"<blockquote>👤 <b>حسابي</b>\n\n"
                    f"🆔 الآيدي: <code>{user.id}</code>\n"
                    f"👤 الاسم: {user.first_name or 'غير متوفر'}\n"
                    f"🔗 اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
                    f"⭐ بريميوم: {'نعم' if getattr(user, 'is_premium', False) else 'لا'}\n"
                    f"🌐 اللغة: {user.language_code or 'غير محدد'}\n"
                    f"📅 تاريخ التسجيل: {_format_timestamp()}\n\n"
                    f"📊 إجمالي المستخدمين: {len(data.registered_users)}</blockquote>"
                )
                bot.send_message(callback.message.chat.id, account_text, parse_mode="HTML")

        def _handle_support_inquiry(self, message):
            user_id = message.from_user.id
            admin_id = self.data.admin_id
            try:
                forward_text = (
                    f"<blockquote>📩 <b>رسالة دعم / استفسار</b>\n"
                    f"من: {message.from_user.first_name}\n"
                    f"🆔: <code>{user_id}</code>\n"
                    f"الرسالة:\n{message.text}</blockquote>"
                )
                self.bot.send_message(admin_id, forward_text, parse_mode="HTML")
                self.bot.reply_to(message, "<blockquote>✅ تم إرسال رسالتك، سيتم الرد عليك قريباً.</blockquote>", parse_mode="HTML")
            except Exception as e:
                self.bot.reply_to(message, f"<blockquote>❌ حدث خطأ: {e}</blockquote>", parse_mode="HTML")

        @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_main_") or
              c.data.startswith("adm_fwd_") or c.data.startswith("adm_bc_") or
              c.data.startswith("adm_settings_") or c.data.startswith("adm_banned_") or
              c.data.startswith("adm_banmute_") or c.data.startswith("adm_effects_") or
              c.data.startswith("adm_photo_") or c.data.startswith("adm_admins_"))
        def handle_admin_menus(callback):
            if not instance._is_admin(callback.message.chat.id):
                bot.answer_callback_query(callback.id, "غير مصرح.")
                return

            action = callback.data
            chat_id = callback.message.chat.id
            msg_id = callback.message.message_id

            if action == "adm_main_stats":
                bot.answer_callback_query(callback.id)
                stats_text = (
                    "<blockquote>📊 <b>إحصائيات النظام</b>\n\n"
                    f"👥 عدد المستخدمين: {len(data.registered_users)}\n"
                    f"🚫 المحظورون: {len(data.banned_users)}\n"
                    f"🔇 المكتومون: {len(data.muted_users)}\n"
                    f"⏰ الوقت: {_format_timestamp()}</blockquote>"
                )
                kb = InlineKeyboardMarkup(row_width=1)
                kb.add(*instance._back_button("adm_main_back"))
                bot.send_message(chat_id, stats_text, parse_mode="HTML", reply_markup=kb)

            elif action == "adm_main_fwd":
                instance._send_fwd_menu(chat_id, msg_id)

            elif action == "adm_main_bc":
                instance._send_bc_menu(chat_id, msg_id)

            elif action == "adm_main_settings":
                instance._send_settings_menu(chat_id, msg_id)

            elif action == "adm_main_effects":
                bot.answer_callback_query(callback.id)
                instance._send_effects_panel(chat_id, msg_id)

            elif action == "adm_main_photo":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🖼️ أرسل الصورة الجديدة للواجهة:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._change_photo_step)

            elif action == "adm_main_admins":
                instance._send_admins_menu(chat_id, msg_id)

            elif action == "adm_main_banmute":
                instance._send_banmute_menu(chat_id, msg_id)

            elif action == "adm_main_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action == "adm_fwd_toggle":
                data.auto_forward = not data.auto_forward
                instance._persist()
                bot.answer_callback_query(callback.id, f"التوجيه {'مفعل' if data.auto_forward else 'معطل'}")
                instance._send_fwd_menu(chat_id, msg_id)

            elif action == "adm_fwd_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action == "adm_bc_text":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>📤 أرسل الرسالة النصية للإذاعة:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._broadcast_message)

            elif action == "adm_bc_forward":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>📨 أرسل أي رسالة لإعادة توجيهها.</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._broadcast_forward)

            elif action == "adm_bc_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action == "adm_settings_typing":
                data.typing_indicator = not data.typing_indicator
                instance._persist()
                bot.answer_callback_query(callback.id, f"مؤشر الكتابة: {'مفعل' if data.typing_indicator else 'معطل'}")
                instance._send_settings_menu(chat_id, msg_id)

            elif action == "adm_settings_reply":
                data.reply_mode = not data.reply_mode
                instance._persist()
                bot.answer_callback_query(callback.id, f"الرد التلقائي: {'مفعل' if data.reply_mode else 'معطل'}")
                instance._send_settings_menu(chat_id, msg_id)

            elif action == "adm_settings_receipt":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>📝 أرسل رسالة الاستلام الجديدة:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._set_receipt_message)

            elif action == "adm_settings_welcome":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🎈 أرسل رسالة الترحيب الجديدة:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._set_welcome_message)

            elif action == "adm_settings_banned":
                bot.answer_callback_query(callback.id)
                instance._send_banned_media_menu(chat_id, msg_id)

            elif action == "adm_settings_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action.startswith("adm_banned_toggle_"):
                media_key = action.replace("adm_banned_toggle_", "")
                if media_key in data.banned_media_types:
                    data.banned_media_types.remove(media_key)
                else:
                    data.banned_media_types.append(media_key)
                instance._persist()
                bot.answer_callback_query(callback.id, "تم التحديث")
                instance._send_banned_media_menu(chat_id, msg_id)

            elif action == "adm_banned_back":
                instance._send_settings_menu(chat_id, msg_id)

            elif action == "adm_banmute_ban":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🚫 أرسل معرف المستخدم لحظره:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._ban_user_step)

            elif action == "adm_banmute_unban":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>✅ أرسل معرف المستخدم لرفع الحظر:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._unban_user_step)

            elif action == "adm_banmute_mute":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🔇 أرسل معرف المستخدم لكتمه:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._mute_user_step)

            elif action == "adm_banmute_unmute":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🔊 أرسل معرف المستخدم لرفع الكتم:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._unmute_user_step)

            elif action == "adm_banmute_banned":
                bot.answer_callback_query(callback.id)
                if data.banned_users:
                    ban_list = "\n".join([f"• <code>{uid}</code>" for uid in data.banned_users])
                    bot.send_message(chat_id, f"<blockquote>🚫 <b>المحظورون:</b>\n\n{ban_list}</blockquote>", parse_mode="HTML")
                else:
                    bot.send_message(chat_id, "<blockquote>🚫 لا يوجد محظورون.</blockquote>", parse_mode="HTML")

            elif action == "adm_banmute_muted":
                bot.answer_callback_query(callback.id)
                if data.muted_users:
                    mute_list = "\n".join([f"• <code>{uid}</code>" for uid in data.muted_users])
                    bot.send_message(chat_id, f"<blockquote>🔇 <b>المكتومون:</b>\n\n{mute_list}</blockquote>", parse_mode="HTML")
                else:
                    bot.send_message(chat_id, "<blockquote>🔇 لا يوجد مكتومون.</blockquote>", parse_mode="HTML")

            elif action == "adm_banmute_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action == "adm_admins_add":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>👤 أرسل معرف المشرف الجديد:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, instance._add_admin_step)

            elif action == "adm_admins_list":
                bot.answer_callback_query(callback.id)
                all_admins = [data.admin_id] + list(data.sub_admins)
                admin_lines = "\n".join([
                    f"• <code>{uid}</code>" + (" (رئيسي)" if uid == data.admin_id else "")
                    for uid in all_admins
                ])
                bot.send_message(chat_id, f"<blockquote>👥 <b>قائمة المشرفين:</b>\n\n{admin_lines}</blockquote>", parse_mode="HTML")

            elif action == "adm_admins_back":
                instance._send_admin_main(chat_id, msg_id)

            elif action.startswith("eff_"):
                effect_id = action.replace("eff_", "")
                data.active_effect_id = effect_id
                instance._persist()
                selected_emoji = next((k for k, v in _AVAILABLE_EFFECTS.items() if v == effect_id), "")
                bot.answer_callback_query(callback.id, f"تم تغيير التأثير إلى {selected_emoji}")
                instance._send_effects_panel(chat_id, msg_id)

        @bot.callback_query_handler(func=lambda c: c.data.startswith(('ban_', 'reply_')))
        def handle_quick_actions(callback):
            if not instance._is_admin(callback.message.chat.id):
                bot.answer_callback_query(callback.id, "غير مصرح.")
                return
            try:
                action_type, user_id_str = callback.data.split('_', 1)
                target_user_id = int(user_id_str)

                if action_type == 'ban':
                    data.banned_users.add(target_user_id)
                    instance._persist()
                    bot.answer_callback_query(callback.id, f"تم حظر المستخدم {target_user_id}")
                    instance._clear_inline_keyboard(callback.message, target_user_id, "حظر")
                elif action_type == 'reply':
                    bot.answer_callback_query(callback.id, "أرسل ردك الآن")
                    prompt = bot.send_message(
                        data.admin_id,
                        f"<blockquote>✏️ أرسل الرد إلى المستخدم <code>{target_user_id}</code>:</blockquote>",
                        parse_mode="HTML"
                    )
                    bot.register_next_step_handler(
                        prompt,
                        lambda msg: instance._send_reply_to_user(msg, target_user_id)
                    )
            except Exception as e:
                bot.answer_callback_query(callback.id, "حدث خطأ")
                print(f"quick action error: {e}")

        @bot.message_handler(content_types=[
            'text', 'photo', 'video', 'document',
            'audio', 'voice', 'sticker', 'contact'
        ])
        def handle_incoming_message(message):
            user_id = message.chat.id

            if user_id in data.banned_users:
                bot.reply_to(message, "<blockquote>🚫 عذراً، أنت محظور من استخدام النظام.</blockquote>", parse_mode="HTML")
                return
            if user_id in data.muted_users:
                return
            if instance._is_admin(user_id):
                return
            if instance._is_message_banned(message):
                bot.reply_to(message, "<blockquote>⛔ هذا النوع من المحتوى غير مسموح به.</blockquote>", parse_mode="HTML")
                return

            if data.auto_forward:
                info = _extract_message_info(message)
                instance._forward_message_to_admin(message, info)

            if data.reply_mode:
                instance._send_typing(user_id)
                bot.reply_to(message, f"<blockquote>✅ {data.receipt_message}</blockquote>", parse_mode="HTML")

    # ========== لوحة الأدمن الرئيسية ==========
    def _send_admin_main(self, chat_id: int, msg_id: Optional[int] = None) -> None:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("📊 الإحصائيات", callback_data="adm_main_stats", style="success"),
            InlineKeyboardButton("📤 التوجيه", callback_data="adm_main_fwd", style="success")
        )
        kb.row(
            InlineKeyboardButton("📢 الإذاعة", callback_data="adm_main_bc", style="danger"),
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="adm_main_settings", style="danger")
        )
        kb.row(
            InlineKeyboardButton("✨ التأثيرات", callback_data="adm_main_effects", style="primary"),
            InlineKeyboardButton("🖼️ تغيير الصورة", callback_data="adm_main_photo", style="primary")
        )
        kb.row(
            InlineKeyboardButton("👥 المشرفين", callback_data="adm_main_admins", style="success"),
            InlineKeyboardButton("🔨 الحظر والكتم", callback_data="adm_main_banmute", style="success")
        )
        text = "<blockquote>🎛️ <b>لوحة التحكم الإدارية</b>\n\nاختر القسم المطلوب:</blockquote>"
        if msg_id:
            try:
                self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)
                return
            except Exception:
                pass
        self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)

    # ========== إعدادات التوجيه ==========
    def _send_fwd_menu(self, chat_id: int, msg_id: int) -> None:
        status = "مفعل" if self.data.auto_forward else "معطل"
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(f"🔄 التوجيه التلقائي: {status}", callback_data="adm_fwd_toggle"))
        kb.add(*self._back_button("adm_main_back"))
        text = "<blockquote>📤 <b>إعدادات إعادة التوجيه</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== الإذاعة ==========
    def _send_bc_menu(self, chat_id: int, msg_id: int) -> None:
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("📨 إذاعة رسالة", callback_data="adm_bc_text", style="success"))
        kb.add(InlineKeyboardButton("📎 إذاعة توجيه", callback_data="adm_bc_forward", style="danger"))
        kb.add(*self._back_button("adm_main_back"))
        text = "<blockquote>📢 <b>قسم الإذاعة</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== الإعدادات العامة ==========
    def _send_settings_menu(self, chat_id: int, msg_id: int) -> None:
        typing_status = "مفعل" if self.data.typing_indicator else "معطل"
        reply_status = "مفعل" if self.data.reply_mode else "معطل"
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(f"⌨️ مؤشر الكتابة: {typing_status}", callback_data="adm_settings_typing"))
        kb.add(InlineKeyboardButton(f"💬 الرد التلقائي: {reply_status}", callback_data="adm_settings_reply"))
        kb.add(InlineKeyboardButton("📩 رسالة الاستلام", callback_data="adm_settings_receipt", style="primary"))
        kb.add(InlineKeyboardButton("🎉 رسالة الترحيب", callback_data="adm_settings_welcome", style="success"))
        kb.add(InlineKeyboardButton("🚫 المحتويات الممنوعة", callback_data="adm_settings_banned", style="danger"))
        kb.add(*self._back_button("adm_main_back"))
        text = "<blockquote>⚙️ <b>الإعدادات العامة</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== المحتويات الممنوعة ==========
    def _send_banned_media_menu(self, chat_id: int, msg_id: int) -> None:
        kb = InlineKeyboardMarkup(row_width=1)
        for key in _BANNED_MEDIA_KEYS:
            status = "مسموح" if key not in self.data.banned_media_types else "ممنوع"
            label = f"{_MEDIA_TYPES_MAP.get(key, key)}: {status}"
            # إضافة إيموجي مناسب لكل نوع
            emoji_map = {
                'audio': '🎵', 'document': '📄', 'sticker': '🖼️', 'video': '🎬',
                'voice': '🎤', 'contact': '📇', 'forward': '↩️', 'all_link': '🔗',
                'telegram_link': '📎'
            }
            emoji = emoji_map.get(key, '🚫')
            kb.add(InlineKeyboardButton(f"{emoji} {label}", callback_data=f"adm_banned_toggle_{key}"))
        kb.add(*self._back_button("adm_settings_back"))
        text = "<blockquote>🚫 <b>إدارة المحتويات الممنوعة</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== الحظر والكتم ==========
    def _send_banmute_menu(self, chat_id: int, msg_id: int) -> None:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("🚫 حظر", callback_data="adm_banmute_ban", style="primary"),
            InlineKeyboardButton("✅ رفع الحظر", callback_data="adm_banmute_unban", style="primary")
        )
        kb.row(
            InlineKeyboardButton("🔇 كتم", callback_data="adm_banmute_mute", style="success"),
            InlineKeyboardButton("🔊 رفع الكتم", callback_data="adm_banmute_unmute", style="success")
        )
        kb.row(
            InlineKeyboardButton("📋 قائمة المحظورين", callback_data="adm_banmute_banned", style="danger"),
            InlineKeyboardButton("📋 قائمة المكتومين", callback_data="adm_banmute_muted", style="danger")
        )
        kb.add(*self._back_button("adm_main_back"))
        text = "<blockquote>🔨 <b>إدارة الحظر والكتم</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== إدارة المشرفين ==========
    def _send_admins_menu(self, chat_id: int, msg_id: int) -> None:
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("➕ إضافة مشرف", callback_data="adm_admins_add", style="success"))
        kb.add(InlineKeyboardButton("📋 قائمة المشرفين", callback_data="adm_admins_list", style="danger"))
        kb.add(*self._back_button("adm_main_back"))
        text = "<blockquote>👥 <b>إدارة المشرفين</b></blockquote>"
        self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ========== لوحة التأثيرات ==========
    def _build_effects_keyboard(self) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = []
        for emoji_name, effect_id in _AVAILABLE_EFFECTS.items():
            label = f"{emoji_name} ✔️" if effect_id == self.data.active_effect_id else emoji_name
            buttons.append(InlineKeyboardButton(label, callback_data=f"eff_{effect_id}"))
        for i in range(0, len(buttons), 3):
            kb.row(*buttons[i:i+3])
        return kb

    def _send_effects_panel(self, chat_id: int, msg_id: Optional[int] = None) -> None:
        keyboard = self._build_effects_keyboard()
        keyboard.add(*self._back_button("adm_main_back"))
        text = "<blockquote>✨ <b>اختر التأثير المناسب للواجهة:</b></blockquote>"
        if msg_id:
            try:
                self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML", reply_markup=keyboard)
                return
            except Exception:
                pass
        self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=keyboard)

    # ========== تغيير رسالة الاستلام ==========
    def _set_receipt_message(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        self.data.receipt_message = message.text or ""
        self._persist()
        self.bot.reply_to(message, "<blockquote>✅ تم تحديث رسالة الاستلام.</blockquote>", parse_mode="HTML")

    # ========== تغيير رسالة الترحيب ==========
    def _set_welcome_message(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        self.data.welcome_caption = message.text or ""
        self._persist()
        self.bot.reply_to(message, "<blockquote>✅ تم تحديث رسالة الترحيب.</blockquote>", parse_mode="HTML")

    # ========== توجيه الرسالة للإدارة ==========
    def _forward_message_to_admin(self, message, info: Dict[str, Any]) -> None:
        admin_id = self.data.admin_id
        header = (
            "<blockquote>📨 <b>رسالة جديدة</b>\n\n"
            f"👤 المرسل: {info['full_name']}\n"
            f"🔗 اليوزر: {info['username']}\n"
            f"🆔 المعرف: <code>{info['uid']}</code>\n"
            f"⭐ بريميوم: {info['is_premium']}\n"
            f"🌐 اللغة: {info['language']}\n"
            f"📎 نوع المحتوى: {info['message_type']}\n"
            f"⏰ الوقت: {info['timestamp']}\n\n"
            "<b>المحتوى:</b>\n"
        )
        action_keyboard = InlineKeyboardMarkup(row_width=2)
        action_keyboard.row(
            InlineKeyboardButton("🚫 حظر", callback_data=f"ban_{info['uid']}", style="primary"),
            InlineKeyboardButton("📩 رد", callback_data=f"reply_{info['uid']}", style="primary")
        )

        try:
            if message.text:
                self.bot.send_message(admin_id, header + message.text + "</blockquote>", parse_mode="HTML", reply_markup=action_keyboard)
            elif message.photo:
                caption = header + (message.caption or "") + "</blockquote>"
                self.bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption, parse_mode="HTML", reply_markup=action_keyboard)
            elif message.video:
                caption = header + (message.caption or "") + "</blockquote>"
                self.bot.send_video(admin_id, message.video.file_id, caption=caption, parse_mode="HTML", reply_markup=action_keyboard)
            elif message.document:
                caption = header + (message.caption or "") + "</blockquote>"
                self.bot.send_document(admin_id, message.document.file_id, caption=caption, parse_mode="HTML", reply_markup=action_keyboard)
            elif message.audio:
                caption = header + (message.caption or "") + "</blockquote>"
                self.bot.send_audio(admin_id, message.audio.file_id, caption=caption, parse_mode="HTML", reply_markup=action_keyboard)
            elif message.voice:
                self.bot.send_voice(admin_id, message.voice.file_id, caption=header + "</blockquote>", parse_mode="HTML", reply_markup=action_keyboard)
            elif message.sticker:
                self.bot.send_sticker(admin_id, message.sticker.file_id, reply_markup=action_keyboard)
                self.bot.send_message(admin_id, header + "</blockquote>", parse_mode="HTML")
            elif message.contact:
                contact_text = f"جهة اتصال:\n{message.contact.phone_number}\n{message.contact.first_name} {message.contact.last_name or ''}"
                self.bot.send_message(admin_id, header + contact_text + "</blockquote>", parse_mode="HTML", reply_markup=action_keyboard)
            else:
                self.bot.forward_message(admin_id, message.chat.id, message.message_id)
                self.bot.send_message(admin_id, header + "</blockquote>", parse_mode="HTML")
        except Exception as e:
            print(f"msg forward error: {e}")

    # ========== الإذاعة النصية ==========
    def _broadcast_message(self, original_message) -> None:
        if not self._is_admin(original_message.chat.id):
            return
        admin_id = self.data.admin_id
        success_count = 0
        fail_count = 0
        progress_msg = self.bot.send_message(admin_id, "<blockquote>⏳ جاري الإذاعة...</blockquote>", parse_mode="HTML")
        for user_id in list(self.data.registered_users):
            try:
                if original_message.text:
                    self.bot.send_message(user_id, original_message.text, parse_mode="HTML")
                elif original_message.photo:
                    self.bot.send_photo(user_id, original_message.photo[-1].file_id, caption=original_message.caption or "", parse_mode="HTML")
                elif original_message.video:
                    self.bot.send_video(user_id, original_message.video.file_id, caption=original_message.caption or "", parse_mode="HTML")
                elif original_message.document:
                    self.bot.send_document(user_id, original_message.document.file_id, caption=original_message.caption or "", parse_mode="HTML")
                elif original_message.audio:
                    self.bot.send_audio(user_id, original_message.audio.file_id, caption=original_message.caption or "", parse_mode="HTML")
                elif original_message.voice:
                    self.bot.send_voice(user_id, original_message.voice.file_id)
                elif original_message.sticker:
                    self.bot.send_sticker(user_id, original_message.sticker.file_id)
                else:
                    self.bot.forward_message(user_id, original_message.chat.id, original_message.message_id)
                success_count += 1
                if success_count % 30 == 0:
                    try:
                        self.bot.edit_message_text(
                            chat_id=admin_id, message_id=progress_msg.message_id,
                            text=f"<blockquote>⏳ جاري الإذاعة...\n✅ نجاح: {success_count}\n❌ فشل: {fail_count}</blockquote>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
            except Exception:
                fail_count += 1
        result_text = f"<blockquote>✅ اكتملت الإذاعة.\n\n✅ نجاح: {success_count}\n❌ فشل: {fail_count}</blockquote>"
        try:
            self.bot.edit_message_text(chat_id=admin_id, message_id=progress_msg.message_id, text=result_text, parse_mode="HTML")
        except Exception:
            self.bot.send_message(admin_id, result_text, parse_mode="HTML")

    # ========== الإذاعة بالتوجيه ==========
    def _broadcast_forward(self, original_message) -> None:
        if not self._is_admin(original_message.chat.id):
            return
        admin_id = self.data.admin_id
        success_count = 0
        fail_count = 0
        progress_msg = self.bot.send_message(admin_id, "<blockquote>⏳ جاري إذاعة التوجيه...</blockquote>", parse_mode="HTML")
        for user_id in list(self.data.registered_users):
            try:
                self.bot.forward_message(user_id, original_message.chat.id, original_message.message_id)
                success_count += 1
                if success_count % 30 == 0:
                    self.bot.edit_message_text(
                        chat_id=admin_id, message_id=progress_msg.message_id,
                        text=f"<blockquote>⏳ جاري الإذاعة...\n✅ نجاح: {success_count}\n❌ فشل: {fail_count}</blockquote>",
                        parse_mode="HTML"
                    )
            except Exception:
                fail_count += 1
        result_text = f"<blockquote>✅ اكتملت إذاعة التوجيه.\n\n✅ نجاح: {success_count}\n❌ فشل: {fail_count}</blockquote>"
        try:
            self.bot.edit_message_text(chat_id=admin_id, message_id=progress_msg.message_id, text=result_text, parse_mode="HTML")
        except Exception:
            self.bot.send_message(admin_id, result_text, parse_mode="HTML")

    # ========== الرد على المستخدم ==========
    def _send_reply_to_user(self, admin_message, target_user_id: int) -> None:
        try:
            if admin_message.text:
                self.bot.send_message(target_user_id, admin_message.text, parse_mode="HTML")
            elif admin_message.photo:
                self.bot.send_photo(target_user_id, admin_message.photo[-1].file_id, caption=admin_message.caption or "", parse_mode="HTML")
            elif admin_message.video:
                self.bot.send_video(target_user_id, admin_message.video.file_id, caption=admin_message.caption or "", parse_mode="HTML")
            elif admin_message.document:
                self.bot.send_document(target_user_id, admin_message.document.file_id, caption=admin_message.caption or "", parse_mode="HTML")
            elif admin_message.audio:
                self.bot.send_audio(target_user_id, admin_message.audio.file_id, caption=admin_message.caption or "", parse_mode="HTML")
            elif admin_message.voice:
                self.bot.send_voice(target_user_id, admin_message.voice.file_id)
            elif admin_message.sticker:
                self.bot.send_sticker(target_user_id, admin_message.sticker.file_id)
            else:
                self.bot.forward_message(target_user_id, admin_message.chat.id, admin_message.message_id)
            self.bot.send_message(self.data.admin_id, "<blockquote>✅ تم إرسال الرد بنجاح.</blockquote>", parse_mode="HTML")
        except Exception as e:
            self.bot.send_message(self.data.admin_id, f"<blockquote>❌ فشل الإرسال: {e}</blockquote>", parse_mode="HTML")

    # ========== خطوات الحظر والكتم ==========
    def _ban_user_step(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        try:
            target_id = int(message.text.strip())
            self.data.banned_users.add(target_id)
            self._persist()
            self.bot.reply_to(message, f"<blockquote>✅ تم حظر المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    def _unban_user_step(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        try:
            target_id = int(message.text.strip())
            self.data.banned_users.discard(target_id)
            self._persist()
            self.bot.reply_to(message, f"<blockquote>✅ تم رفع الحظر عن المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    def _mute_user_step(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        try:
            target_id = int(message.text.strip())
            self.data.muted_users.add(target_id)
            self._persist()
            self.bot.reply_to(message, f"<blockquote>✅ تم كتم المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    def _unmute_user_step(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        try:
            target_id = int(message.text.strip())
            self.data.muted_users.discard(target_id)
            self._persist()
            self.bot.reply_to(message, f"<blockquote>✅ تم رفع الكتم عن المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    # ========== تغيير صورة الواجهة ==========
    def _change_photo_step(self, message) -> None:
        if not self._is_admin(message.chat.id):
            return
        if message.photo:
            self.data.welcome_photo_id = message.photo[-1].file_id
            self._persist()
            self.bot.reply_to(message, "<blockquote>✅ تم تحديث صورة الواجهة بنجاح.</blockquote>", parse_mode="HTML")
        else:
            self.bot.reply_to(message, "<blockquote>❌ يرجى إرسال صورة فقط.</blockquote>", parse_mode="HTML")

    # ========== إضافة مشرف ==========
    def _add_admin_step(self, message) -> None:
        if message.chat.id != self.data.admin_id and message.chat.id != self.data.owner_id:
            return
        try:
            target_id = int(message.text.strip())
            self.data.sub_admins.add(target_id)
            self._persist()
            self.bot.reply_to(message, f"<blockquote>✅ تمت إضافة المشرف <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    # ========== إيقاف البوت ==========
    def stop(self) -> None:
        try:
            self.data.is_running = False
            self._stop_event.set()
            self.bot.stop_polling()
        except Exception as e:
            print(f"stop error: {e}")

    # ========== تشغيل البوت ==========
    def run(self) -> None:
        try:
            self._register_handlers()
            print(f"✅ Bot started: {self.data.bot_username}")
            while self.data.is_running and not self._stop_event.is_set():
                try:
                    self.bot.polling(none_stop=False, timeout=60, long_polling_timeout=60)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as net_err:
                    print(f"Network error for {self.data.bot_username}: {net_err}. Retrying in 10s...")
                    time.sleep(10)
                    continue
                except ApiTelegramException as api_error:
                    if api_error.error_code == 401:
                        print(f"❌ Bot {self.data.bot_username} token unauthorized – stopping")
                        self.stop()
                        if self._factory:
                            self._factory._handle_token_failure(self.data.bot_username)
                        break
                    else:
                        if self.data.is_running and not self._stop_event.is_set():
                            print(f"polling API error: {api_error}")
                            time.sleep(3)
                except Exception as ex:
                    if self.data.is_running and not self._stop_event.is_set():
                        print(f"polling error: {ex}")
                        time.sleep(3)
                    else:
                        break
        except Exception as e:
            print(f"run error: {e}")
        finally:
            self.data.is_running = False


# ========== فئة المصنع الرئيسي ==========
class FactoryBot:
    def __init__(self):
        self.bot = telebot.TeleBot(_MASTER_TOKEN)
        self.instances: Dict[str, BotInstance] = {}
        self.banned_users: Set[int] = set()
        self.all_users: Set[int] = set()
        self.maintenance_mode = False
        self.factory_channels: List[str] = []
        self._load_data()
        if not self.factory_channels:
            self.factory_channels = DEFAULT_FACTORY_CHANNELS.copy()
            self._save_all_data()

    def _load_data(self) -> None:
        try:
            if os.path.exists(_DATA_FILE):
                with open(_DATA_FILE, 'r', encoding='utf-8') as file:
                    raw_data = json.load(file)
                bots_data = raw_data.get('bots', {})
                factory_meta = raw_data.get('factory_data', {})
                self.banned_users = set(factory_meta.get('banned_users', []))
                self.all_users = set(factory_meta.get('users', []))
                self.maintenance_mode = factory_meta.get('maintenance_mode', False)
                self.factory_channels = factory_meta.get('factory_channels', [])
                for bot_id, bot_info in bots_data.items():
                    bot_data = BotData(
                        bot_info['owner_id'],
                        bot_info['bot_token'],
                        bot_info['admin_id'],
                        bot_info.get('channel_username', "mouhamed_maa"),
                        bot_info.get('developer_username', ""),
                        bot_info.get('bot_name', ""),
                        bot_info.get('bot_username', bot_id)
                    )
                    bot_data.banned_users = set(bot_info.get('banned_users', []))
                    bot_data.muted_users = set(bot_info.get('muted_users', []))
                    bot_data.registered_users = set(bot_info.get('registered_users', []))
                    bot_data.users_counter = bot_info.get('users_counter', 0)
                    bot_data.active_effect_id = bot_info.get('message_effect_id', "5104841245755180586")
                    bot_data.welcome_photo_id = bot_info.get('welcome_photo', DEFAULT_WELCOME_PHOTO)
                    bot_data.sub_admins = set(bot_info.get('sub_admins', []))
                    bot_data.auto_forward = bot_info.get('auto_forward', True)
                    bot_data.typing_indicator = bot_info.get('typing_indicator', True)
                    bot_data.reply_mode = bot_info.get('reply_mode', True)
                    bot_data.receipt_message = bot_info.get('receipt_message', "تم استلام رسالتك بنجاح، سيتم الرد عليك في أقرب وقت.")
                    bot_data.welcome_caption = bot_info.get('welcome_caption', "")
                    bot_data.banned_media_types = bot_info.get('banned_media_types', [])
                    bot_data.creation_time = bot_info.get('creation_time', datetime.now().isoformat())
                    self.instances[bot_id] = BotInstance(bot_data, self)
                print(f"✅ Loaded {len(self.instances)} bots")
        except Exception as e:
            print(f"load error: {e}")

    def _save_all_data(self) -> None:
        try:
            serialized_bots = {}
            for bot_id, instance in self.instances.items():
                data = instance.data
                serialized_bots[bot_id] = {
                    'owner_id': data.owner_id,
                    'bot_token': data.token,
                    'admin_id': data.admin_id,
                    'channel_username': data.channel_username,
                    'developer_username': data.developer_username,
                    'bot_name': data.bot_name,
                    'bot_username': data.bot_username,
                    'banned_users': list(data.banned_users),
                    'muted_users': list(data.muted_users),
                    'registered_users': list(data.registered_users),
                    'users_counter': data.users_counter,
                    'message_effect_id': data.active_effect_id,
                    'welcome_photo': data.welcome_photo_id,
                    'sub_admins': list(data.sub_admins),
                    'auto_forward': data.auto_forward,
                    'typing_indicator': data.typing_indicator,
                    'reply_mode': data.reply_mode,
                    'receipt_message': data.receipt_message,
                    'welcome_caption': data.welcome_caption,
                    'banned_media_types': data.banned_media_types,
                    'creation_time': data.creation_time
                }
            factory_meta = {
                'banned_users': list(self.banned_users),
                'users': list(self.all_users),
                'maintenance_mode': self.maintenance_mode,
                'factory_channels': self.factory_channels
            }
            with open(_DATA_FILE, 'w', encoding='utf-8') as file:
                json.dump(
                    {'bots': serialized_bots, 'factory_data': factory_meta},
                    file,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            print(f"save error: {e}")

    def _validate_bot_token(self, token: str) -> Tuple[bool, Any]:
        try:
            test_bot = telebot.TeleBot(token)
            bot_info = test_bot.get_me()
            return True, (bot_info.first_name or "Bot", bot_info.username or "unknown")
        except Exception as e:
            return False, str(e)

    def _create_new_bot(self, owner_id: int, token: str, admin_id: int,
                        channel: str = "", developer: str = "") -> Tuple[bool, Any]:
        if not admin_id:
            admin_id = owner_id
        if not channel:
            channel = "mouhamed_maa"
        is_valid, result = self._validate_bot_token(token)
        if not is_valid:
            return False, f"توكن غير صحيح: {result}"
        bot_name, bot_username = result
        bot_data = BotData(owner_id, token, admin_id, channel, developer, bot_name, bot_username)
        bot_data.welcome_photo_id = DEFAULT_WELCOME_PHOTO
        instance = BotInstance(bot_data, self)
        self.instances[bot_username] = instance
        self._save_all_data()
        self._start_bot_instance(bot_username)

        # إرسال إشعار إلى قناة الإثباتات
        try:
            request_id = _generate_request_id()
            running_count = sum(1 for i in self.instances.values() if i.data.is_running)
            proof_msg = (
                f"<blockquote>🚀 <b>تم إنشاء بوت جديد</b>\n\n"
                f"📄 اسم البوت: <b>{bot_name}</b>\n"
                f"👤 المالك: <code>{owner_id}</code>\n"
                f"🤖 يوزر البوت: @{bot_username}\n"
                f"🆔 رقم الطلب: <code>{request_id}</code>\n"
                f"⏳ عدد البوتات قيد التشغيل: {running_count}\n"
                f"⏰ الوقت: {_format_timestamp()}</blockquote>"
            )
            self.bot.send_message(PROOF_CHANNEL, proof_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Proof channel notification error: {e}")

        return True, (bot_name, bot_username)

    def _start_bot_instance(self, bot_id: str) -> bool:
        if bot_id in self.instances:
            instance = self.instances[bot_id]
            if not instance.data.is_running:
                instance.data.is_running = True
                thread = threading.Thread(target=instance.run, daemon=True)
                thread.start()
                return True
        return False

    def _stop_bot_instance(self, bot_id: str) -> bool:
        if bot_id in self.instances:
            instance = self.instances[bot_id]
            if instance.data.is_running:
                instance.stop()
                return True
        return False

    def _delete_bot_instance(self, bot_id: str) -> bool:
        if bot_id in self.instances:
            self._stop_bot_instance(bot_id)
            time.sleep(1)
            del self.instances[bot_id]
            self._save_all_data()
            return True
        return False

    def _handle_token_failure(self, bot_id: str) -> None:
        if bot_id in self.instances:
            instance = self.instances[bot_id]
            try:
                self.bot.send_message(
                    instance.data.admin_id,
                    f"<blockquote>⚠️ تم إيقاف بوتك @{bot_id} بسبب مشكلة في التوكن (401 Unauthorized).\nيرجى التحقق من التوكن أو إعادة إنشاء البوت.</blockquote>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            self._stop_bot_instance(bot_id)

    def _get_user_bots(self, user_id: int) -> List[Dict[str, Any]]:
        result = []
        for bot_id, instance in self.instances.items():
            if instance.data.owner_id == user_id:
                result.append({
                    'id': bot_id,
                    'running': instance.data.is_running,
                    'users': len(instance.data.registered_users),
                    'name': instance.data.bot_name,
                    'admin_id': instance.data.admin_id,
                    'channel': instance.data.channel_username,
                    'developer': instance.data.developer_username,
                    'creation_time': instance.data.creation_time
                })
        return result

    def _check_factory_subscription(self, user_id: int) -> bool:
        if not self.factory_channels:
            return True
        for channel in self.factory_channels:
            try:
                member = self.bot.get_chat_member(f"@{channel}", user_id)
                if not member or member.status not in ('member', 'administrator', 'creator'):
                    return False
            except Exception:
                return False
        return True

    def _send_factory_subscription_prompt(self, chat_id: int) -> None:
        keyboard = InlineKeyboardMarkup()
        for channel in self.factory_channels:
            keyboard.add(InlineKeyboardButton(
                f"📢 اشترك في @{channel}",
                url=f"https://t.me/{channel}"
            ))
        keyboard.add(InlineKeyboardButton(
            "✅ تأكيد الاشتراك",
            callback_data="fac_check_sub"
        ))
        self.bot.send_message(
            chat_id,
            "<blockquote>🔐 يرجى الاشتراك في القنوات التالية للمتابعة:</blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # ========== لوحة المطور المتطورة ==========
    def _build_factory_admin_keyboard(self) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("📊 الإحصائيات", callback_data="fac_adm_stats", style="primary"),
            InlineKeyboardButton("📈 إحصائيات متقدمة", callback_data="fac_adm_advanced_stats", style="primary")
        )
        kb.row(
            InlineKeyboardButton("📢 الإذاعة", callback_data="fac_adm_broadcast", style="success"),
            InlineKeyboardButton("🤖 إدارة البوتات", callback_data="fac_adm_manage_bots", style="success")
        )
        kb.row(
            InlineKeyboardButton("🚫 حظر مستخدم", callback_data="fac_adm_ban", style="danger"),
            InlineKeyboardButton("✅ رفع الحظر", callback_data="fac_adm_unban", style="danger")
        )
        kb.row(
            InlineKeyboardButton("🗑️ حذف بوت", callback_data="fac_adm_del_bot", style="primary"),
            InlineKeyboardButton("📋 جميع البوتات", callback_data="fac_adm_all_bots", style="primary")
        )
        kb.row(
            InlineKeyboardButton("📌 إدارة القنوات", callback_data="fac_adm_channels", style="success"),
            InlineKeyboardButton("➕ إضافة قناة", callback_data="fac_adm_add_ch", style="success")
        )
        kb.row(
            InlineKeyboardButton("🔄 إعادة تشغيل الكل", callback_data="fac_adm_restart_all", style="danger"),
            InlineKeyboardButton("♻️ تحديث البوتات", callback_data="fac_adm_refresh", style="danger")
        )
        maintenance_label = "🔓 فتح المصنع" if self.maintenance_mode else "🔧 وضع الصيانة"
        kb.row(InlineKeyboardButton(maintenance_label, callback_data="fac_adm_maintenance"))
        kb.row(
            InlineKeyboardButton("💾 نسخ احتياطي", callback_data="fac_adm_backup", style="success"),
            InlineKeyboardButton("📨 إرسال للكل", callback_data="fac_adm_send_all", style="success")
        )
        return kb

    def _send_factory_admin_panel(self, chat_id: int, message_id: Optional[int] = None) -> None:
        keyboard = self._build_factory_admin_keyboard()
        text = "<blockquote>🎛️ <b>لوحة تحكم المطور المتقدمة</b>\n\nاختر الإجراء:</blockquote>"
        if message_id:
            try:
                self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="HTML", reply_markup=keyboard)
                return
            except Exception:
                pass
        self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=keyboard)

    # ========== أزرار المصنع ==========
    def _build_owner_panel_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("🤖 إنشاء بوت", callback_data="fac_create", style="danger"),
            InlineKeyboardButton("📂 بوتاتي", callback_data="fac_my_bots", style="danger")
        )
        kb.row(
            InlineKeyboardButton("🆘 الدعم", callback_data="fac_support", style="primary"),
            InlineKeyboardButton("❓ استفسار", callback_data="fac_inquiry", style="primary")
        )
        kb.row(
            InlineKeyboardButton("📖 المساعدة", callback_data="fac_help", style="success"),
            InlineKeyboardButton("📜 القوانين", callback_data="fac_rules", style="success")
        )
        kb.row(
            InlineKeyboardButton("👤 حسابي", callback_data="fac_account", style="danger"),
            InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{_FACTORY_USERNAME}", style="danger")
        )
        kb.row(
            InlineKeyboardButton("🤖 إنشاء بوتك الخاص", url="https://t.me/moha_ma_bot", style="primary")
        )
        if user_id == _MASTER_ID:
            kb.row(InlineKeyboardButton("🛠️ لوحة المطور", callback_data="fac_admin_panel", style="success"))
        return kb

    def _register_factory_handlers(self) -> None:
        bot = self.bot
        factory = self

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            user_id = message.from_user.id
            factory.all_users.add(user_id)
            factory._save_all_data()

            if user_id in factory.banned_users:
                bot.send_message(message.chat.id, "<blockquote>🚫 عذراً، أنت محظور من استخدام هذا النظام.</blockquote>", parse_mode="HTML")
                return
            if factory.maintenance_mode and user_id != _MASTER_ID:
                bot.send_message(message.chat.id, "<blockquote>🔧 النظام في وضع الصيانة حالياً، يُرجى المحاولة لاحقاً.</blockquote>", parse_mode="HTML")
                return
            if factory.factory_channels and not factory._check_factory_subscription(user_id):
                factory._send_factory_subscription_prompt(message.chat.id)
                return

            keyboard = factory._build_owner_panel_keyboard(user_id)
            first_name = message.from_user.first_name or "المستخدم"
            caption = (
                f"<blockquote>👋 مرحباً بك <b>{first_name}</b> في مصنع بوتات التواصل.\n"
                f"هذا النظام مُقدم من <b>{_CREDIT}</b>.\n"
                "يمكنك إدارة بوتاتك الخاصة من خلال القائمة أدناه.</blockquote>"
            )
            bot.send_photo(
                chat_id=message.chat.id,
                photo=DEFAULT_WELCOME_PHOTO,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )

        @bot.callback_query_handler(func=lambda c: c.data == "fac_check_sub")
        def handle_factory_check_sub(callback):
            user_id = callback.from_user.id
            if factory._check_factory_subscription(user_id):
                bot.answer_callback_query(callback.id, "✅ تم التحقق.")
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
                handle_start(callback.message)
            else:
                bot.answer_callback_query(callback.id, "❌ لم تكتمل الاشتراكات.", show_alert=True)

        @bot.callback_query_handler(func=lambda c: c.data in ("fac_support", "fac_inquiry", "fac_help", "fac_rules", "fac_account"))
        def handle_factory_buttons(callback):
            user_id = callback.from_user.id
            action = callback.data

            if action in ("fac_support", "fac_inquiry"):
                bot.answer_callback_query(callback.id, "📩 أرسل رسالتك")
                prompt = bot.send_message(callback.message.chat.id, "<blockquote>📩 أرسل رسالتك وسيتم إرسالها إلى فريق الدعم.</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._handle_factory_support_inquiry)

            elif action == "fac_help":
                bot.answer_callback_query(callback.id)
                help_text = (
                    "<blockquote>📖 <b>المساعدة</b>\n\n"
                    "• يمكنك إنشاء بوت تواصل خاص بك.\n"
                    "• استخدم زر <b>الدعم</b> للتواصل مع فريق الدعم.\n"
                    "• استخدم زر <b>استفسار</b> لطرح أي سؤال.\n"
                    "• لمشاهدة بياناتك، استخدم زر <b>حسابي</b>.\n"
                    "• للاطلاع على القوانين، استخدم زر <b>القوانين</b>.\n\n"
                    "شكراً لاستخدامك المصنع.</blockquote>"
                )
                bot.send_message(callback.message.chat.id, help_text, parse_mode="HTML")

            elif action == "fac_rules":
                bot.answer_callback_query(callback.id)
                rules_text = (
                    "<blockquote>📜 <b>القوانين</b>\n\n"
                    "1. الاحترام المتبادل بين جميع المستخدمين.\n"
                    "2. عدم إرسال محتوى غير لائق أو مسيء.\n"
                    "3. الالتزام بالتعليمات الصادرة من الإدارة.\n"
                    "4. يمنع نشر الروابط الضارة أو المزعجة.\n"
                    "5. يمنع إنشاء بوتات لأغراض غير قانونية.\n\n"
                    "نشكر التزامكم بالقوانين.</blockquote>"
                )
                bot.send_message(callback.message.chat.id, rules_text, parse_mode="HTML")

            elif action == "fac_account":
                bot.answer_callback_query(callback.id)
                user = callback.from_user
                account_text = (
                    f"<blockquote>👤 <b>حسابي</b>\n\n"
                    f"🆔 الآيدي: <code>{user.id}</code>\n"
                    f"👤 الاسم: {user.first_name or 'غير متوفر'}\n"
                    f"🔗 اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
                    f"⭐ بريميوم: {'نعم' if getattr(user, 'is_premium', False) else 'لا'}\n"
                    f"🌐 اللغة: {user.language_code or 'غير محدد'}\n"
                    f"📅 التاريخ: {_format_timestamp()}\n\n"
                    f"📊 إجمالي المستخدمين: {len(factory.all_users)}</blockquote>"
                )
                bot.send_message(callback.message.chat.id, account_text, parse_mode="HTML")

        def _handle_factory_support_inquiry(self, message):
            user_id = message.from_user.id
            try:
                forward_text = (
                    f"<blockquote>📩 <b>رسالة دعم / استفسار</b>\n"
                    f"من: {message.from_user.first_name}\n"
                    f"🆔: <code>{user_id}</code>\n"
                    f"الرسالة:\n{message.text}</blockquote>"
                )
                self.bot.send_message(_MASTER_ID, forward_text, parse_mode="HTML")
                self.bot.reply_to(message, "<blockquote>✅ تم إرسال رسالتك، سيتم الرد عليك قريباً.</blockquote>", parse_mode="HTML")
            except Exception as e:
                self.bot.reply_to(message, f"<blockquote>❌ حدث خطأ: {e}</blockquote>", parse_mode="HTML")

        # ===== لوحة المطور =====
        @bot.callback_query_handler(func=lambda c: c.data == "fac_admin_panel")
        def handle_admin_panel(callback):
            if callback.from_user.id != _MASTER_ID:
                bot.answer_callback_query(callback.id, "غير مصرح.")
                return
            bot.answer_callback_query(callback.id)
            factory._send_factory_admin_panel(callback.message.chat.id)

        @bot.callback_query_handler(func=lambda c: c.data.startswith("fac_adm_"))
        def handle_factory_admin_actions(callback):
            if callback.from_user.id != _MASTER_ID:
                bot.answer_callback_query(callback.id, "غير مصرح.")
                return
            action = callback.data
            chat_id = callback.message.chat.id

            if action == "fac_adm_stats":
                bot.answer_callback_query(callback.id)
                running_count = sum(1 for i in factory.instances.values() if i.data.is_running)
                stats_text = (
                    "<blockquote>📊 <b>إحصائيات المصنع</b>\n\n"
                    f"👥 المستخدمون: {len(factory.all_users)}\n"
                    f"🤖 البوتات: {len(factory.instances)}\n"
                    f"🟢 النشطة: {running_count}\n"
                    f"🔴 المتوقفة: {len(factory.instances) - running_count}\n"
                    f"🚫 المحظورون: {len(factory.banned_users)}\n"
                    f"📌 القنوات الإجبارية: {len(factory.factory_channels)}\n"
                    f"🔧 حالة الصيانة: {'مفعلة' if factory.maintenance_mode else 'معطلة'}\n"
                    f"⏰ الوقت: {_format_timestamp()}</blockquote>"
                )
                bot.send_message(chat_id, stats_text, parse_mode="HTML")

            elif action == "fac_adm_advanced_stats":
                bot.answer_callback_query(callback.id)
                total_users = 0
                total_banned = 0
                total_muted = 0
                for inst in factory.instances.values():
                    total_users += len(inst.data.registered_users)
                    total_banned += len(inst.data.banned_users)
                    total_muted += len(inst.data.muted_users)
                adv_stats = (
                    "<blockquote>📈 <b>إحصائيات متقدمة</b>\n\n"
                    f"👥 إجمالي مستخدمي البوتات: {total_users}\n"
                    f"🚫 إجمالي المحظورين في البوتات: {total_banned}\n"
                    f"🔇 إجمالي المكتومين في البوتات: {total_muted}\n"
                    f"📊 متوسط المستخدمين لكل بوت: {total_users // len(factory.instances) if factory.instances else 0}\n"
                    f"📅 وقت التحديث: {_format_timestamp()}</blockquote>"
                )
                bot.send_message(chat_id, adv_stats, parse_mode="HTML")

            elif action == "fac_adm_manage_bots":
                bot.answer_callback_query(callback.id)
                if not factory.instances:
                    bot.send_message(chat_id, "<blockquote>❌ لا توجد بوتات لإدارتها.</blockquote>", parse_mode="HTML")
                    return
                kb = InlineKeyboardMarkup(row_width=1)
                for bid, inst in factory.instances.items():
                    status = "🟢" if inst.data.is_running else "🔴"
                    kb.add(InlineKeyboardButton(
                        f"{status} @{bid} | 👥 {len(inst.data.registered_users)}",
                        callback_data=f"fac_adm_bot_detail_{bid}"
                    ))
                kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="fac_admin_panel", style="success"))
                bot.send_message(chat_id, "<blockquote>🤖 <b>إدارة البوتات</b>\nاختر بوتاً لعرض تفاصيله:</blockquote>", parse_mode="HTML", reply_markup=kb)

            elif action.startswith("fac_adm_bot_detail_"):
                bot_id = action.replace("fac_adm_bot_detail_", "")
                if bot_id in factory.instances:
                    inst = factory.instances[bot_id]
                    d = inst.data
                    detail = (
                        f"<blockquote>🤖 <b>تفاصيل @{bot_id}</b>\n\n"
                        f"📌 الاسم: {d.bot_name}\n"
                        f"👤 المالك: <code>{d.owner_id}</code>\n"
                        f"👤 المشرف: <code>{d.admin_id}</code>\n"
                        f"📢 القناة: @{d.channel_username}\n"
                        f"👨‍💻 المطور: @{d.developer_username}\n"
                        f"👥 المستخدمون: {len(d.registered_users)}\n"
                        f"🚫 المحظورون: {len(d.banned_users)}\n"
                        f"🔇 المكتومون: {len(d.muted_users)}\n"
                        f"📌 الحالة: {'🟢 نشط' if d.is_running else '🔴 متوقف'}\n"
                        f"📅 تاريخ الإنشاء: {d.creation_time}\n"
                        f"📊 المستخدمين الإجمالي: {d.users_counter}</blockquote>"
                    )
                    kb = InlineKeyboardMarkup(row_width=2)
                    kb.row(
                        InlineKeyboardButton("🔄 إيقاف" if d.is_running else "▶️ تشغيل", callback_data=f"fac_adm_toggle_{bot_id}"),
                        InlineKeyboardButton("🗑️ حذف", callback_data=f"fac_adm_del_bot_{bot_id}", style="danger")
                    )
                    kb.row(InlineKeyboardButton("⬅️ رجوع", callback_data="fac_adm_manage_bots", style="primary"))
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text=detail, parse_mode="HTML", reply_markup=kb)
                else:
                    bot.answer_callback_query(callback.id, "البوت غير موجود")

            elif action.startswith("fac_adm_toggle_"):
                bot_id = action.replace("fac_adm_toggle_", "")
                if bot_id in factory.instances:
                    inst = factory.instances[bot_id]
                    if inst.data.is_running:
                        factory._stop_bot_instance(bot_id)
                        status = "تم إيقاف البوت"
                    else:
                        factory._start_bot_instance(bot_id)
                        status = "تم تشغيل البوت"
                    bot.answer_callback_query(callback.id, status)
                    callback.data = f"fac_adm_bot_detail_{bot_id}"
                    handle_factory_admin_actions(callback)
                else:
                    bot.answer_callback_query(callback.id, "البوت غير موجود")

            elif action.startswith("fac_adm_del_bot_"):
                bot_id = action.replace("fac_adm_del_bot_", "")
                if bot_id in factory.instances:
                    factory._delete_bot_instance(bot_id)
                    bot.answer_callback_query(callback.id, f"تم حذف @{bot_id}")
                    callback.data = "fac_adm_manage_bots"
                    handle_factory_admin_actions(callback)
                else:
                    bot.answer_callback_query(callback.id, "البوت غير موجود")

            elif action == "fac_adm_broadcast":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>📢 أرسل الرسالة للإذاعة:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_broadcast)

            elif action == "fac_adm_ban":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🚫 أرسل معرف المستخدم لحظره:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_ban_user)

            elif action == "fac_adm_unban":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>✅ أرسل معرف المستخدم لرفع الحظر:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_unban_user)

            elif action == "fac_adm_del_bot":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>🗑️ أرسل @معرف البوت أو التوكن لحذفه:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_delete_bot)

            elif action == "fac_adm_all_bots":
                bot.answer_callback_query(callback.id)
                if not factory.instances:
                    bot.send_message(chat_id, "<blockquote>❌ لا توجد بوتات.</blockquote>", parse_mode="HTML")
                else:
                    lines = []
                    for bid, inst in factory.instances.items():
                        status_icon = "🟢" if inst.data.is_running else "🔴"
                        lines.append(f"{status_icon} @{bid} | 👥 {len(inst.data.registered_users)} | 👤 <code>{inst.data.owner_id}</code>")
                    bot.send_message(chat_id, f"<blockquote>📋 <b>قائمة البوتات:</b>\n\n" + "\n".join(lines) + "</blockquote>", parse_mode="HTML")

            elif action == "fac_adm_channels":
                bot.answer_callback_query(callback.id)
                if factory.factory_channels:
                    kb = InlineKeyboardMarkup()
                    for ch in factory.factory_channels:
                        kb.add(InlineKeyboardButton(f"🗑️ حذف @{ch}", callback_data=f"fac_rmch_{ch}"))
                    channels_list = "\n".join([f"• @{c}" for c in factory.factory_channels])
                    bot.send_message(chat_id, f"<blockquote>📌 <b>القنوات الإجبارية:</b>\n{channels_list}</blockquote>", parse_mode="HTML", reply_markup=kb)
                else:
                    bot.send_message(chat_id, "<blockquote>❌ لا توجد قنوات إجبارية.</blockquote>", parse_mode="HTML")

            elif action == "fac_adm_add_ch":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>➕ أرسل معرف القناة (@username):</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_add_channel)

            elif action == "fac_adm_restart_all":
                bot.answer_callback_query(callback.id, "جاري إعادة التشغيل...")
                for bid in list(factory.instances.keys()):
                    factory._stop_bot_instance(bid)
                time.sleep(2)
                for bid in list(factory.instances.keys()):
                    factory._start_bot_instance(bid)
                bot.send_message(chat_id, "<blockquote>✅ تم إعادة تشغيل جميع البوتات.</blockquote>", parse_mode="HTML")

            elif action == "fac_adm_refresh":
                bot.answer_callback_query(callback.id, "تم التحديث")
                bot.send_message(chat_id, "<blockquote>🔄 تم تحديث البيانات.</blockquote>", parse_mode="HTML")

            elif action == "fac_adm_maintenance":
                factory.maintenance_mode = not factory.maintenance_mode
                factory._save_all_data()
                status_text = "تم تفعيل وضع الصيانة" if factory.maintenance_mode else "تم إلغاء وضع الصيانة"
                bot.answer_callback_query(callback.id, status_text)
                bot.send_message(chat_id, f"<blockquote>🔧 {status_text}</blockquote>", parse_mode="HTML")

            elif action == "fac_adm_backup":
                bot.answer_callback_query(callback.id, "جاري إنشاء النسخة الاحتياطية...")
                factory._send_backup(chat_id)

            elif action == "fac_adm_send_all":
                bot.answer_callback_query(callback.id)
                prompt = bot.send_message(chat_id, "<blockquote>📨 أرسل الرسالة لإرسالها لكل المستخدمين:</blockquote>", parse_mode="HTML")
                bot.register_next_step_handler(prompt, factory._factory_send_all)

        @bot.callback_query_handler(func=lambda c: c.data.startswith("fac_rmch_"))
        def handle_factory_remove_channel(callback):
            if callback.from_user.id != _MASTER_ID:
                bot.answer_callback_query(callback.id, "غير مصرح.")
                return
            ch = callback.data.replace("fac_rmch_", "")
            if ch in factory.factory_channels:
                factory.factory_channels.remove(ch)
                factory._save_all_data()
                bot.answer_callback_query(callback.id, f"تم حذف @{ch}")
                bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=InlineKeyboardMarkup())
            else:
                bot.answer_callback_query(callback.id, "غير موجودة")

        # ===== إنشاء البوت =====
        @bot.callback_query_handler(func=lambda c: c.data == "fac_create")
        def handle_create_bot(callback):
            user_id = callback.from_user.id
            if user_id in factory.banned_users:
                bot.answer_callback_query(callback.id, "محظور من استخدام النظام.")
                return
            if factory.maintenance_mode and user_id != _MASTER_ID:
                bot.answer_callback_query(callback.id, "النظام في وضع الصيانة.")
                return
            if factory.factory_channels and not factory._check_factory_subscription(user_id):
                factory._send_factory_subscription_prompt(callback.message.chat.id)
                bot.answer_callback_query(callback.id, "يجب الاشتراك في القنوات أولاً.")
                return
            bot.answer_callback_query(callback.id)
            prompt = bot.send_message(callback.message.chat.id, "<blockquote>🤖 أرسل توكن البوت الجديد من @BotFather:</blockquote>", parse_mode="HTML")
            _SESSION_STORE[callback.message.chat.id] = {'step': 'token', 'owner_id': user_id}
            bot.register_next_step_handler(prompt, factory._creation_step_token)

        @bot.callback_query_handler(func=lambda c: c.data == "fac_my_bots")
        def handle_my_bots(callback):
            bot.answer_callback_query(callback.id)
            user_id = callback.message.chat.id
            user_bots = factory._get_user_bots(user_id)
            if not user_bots:
                bot.send_message(user_id, "<blockquote>❌ لا تملك أي بوتات حالياً.</blockquote>", parse_mode="HTML")
                return
            for b in user_bots:
                kb = InlineKeyboardMarkup(row_width=2)
                kb.row(
                    InlineKeyboardButton("⚙️ إعدادات البوت", callback_data=f"fac_bot_settings_{b['id']}", style="danger"),
                    InlineKeyboardButton("🗑️ حذف البوت", callback_data=f"fac_del_{b['id']}", style="danger")
                )
                status_text = "🟢 نشط" if b['running'] else "🔴 متوقف"
                info_text = f"<blockquote>🤖 <b>@{b['id']}</b>\n👥 المستخدمون: {b['users']}\n📌 الحالة: {status_text}</blockquote>"
                bot.send_message(user_id, info_text, parse_mode="HTML", reply_markup=kb)

        @bot.callback_query_handler(func=lambda c: c.data.startswith("fac_bot_settings_"))
        def handle_bot_settings(callback):
            bot.answer_callback_query(callback.id)
            user_id = callback.message.chat.id
            target_bot_id = callback.data.replace("fac_bot_settings_", "")
            if target_bot_id in factory.instances:
                inst = factory.instances[target_bot_id]
                if inst.data.owner_id == user_id:
                    d = inst.data
                    settings_text = (
                        f"<blockquote>⚙️ <b>إعدادات @{target_bot_id}</b>\n\n"
                        f"👤 المشرف: <code>{d.admin_id}</code>\n"
                        f"📢 القناة: @{d.channel_username}\n"
                        f"👨‍💻 المطور: @{d.developer_username}\n"
                        f"👥 المستخدمون: {len(d.registered_users)}\n"
                        f"🚫 المحظورون: {len(d.banned_users)}\n"
                        f"🔇 المكتومون: {len(d.muted_users)}\n"
                        f"📌 الحالة: {'🟢 نشط' if d.is_running else '🔴 متوقف'}</blockquote>"
                    )
                    bot.send_message(user_id, settings_text, parse_mode="HTML")
                else:
                    bot.send_message(user_id, "<blockquote>❌ لا تملك صلاحية الوصول لهذا البوت.</blockquote>", parse_mode="HTML")

        @bot.callback_query_handler(func=lambda c: c.data.startswith("fac_del_"))
        def handle_delete_bot(callback):
            bot.answer_callback_query(callback.id)
            user_id = callback.message.chat.id
            target_bot_id = callback.data.replace("fac_del_", "")
            if target_bot_id in factory.instances:
                inst = factory.instances[target_bot_id]
                if inst.data.owner_id == user_id:
                    kb = InlineKeyboardMarkup(row_width=2)
                    kb.row(
                        InlineKeyboardButton("✅ نعم، احذف", callback_data=f"fac_confirm_del_{target_bot_id}", style="primary"),
                        InlineKeyboardButton("❌ إلغاء", callback_data="fac_cancel_del", style="primary")
                    )
                    bot.send_message(user_id, f"<blockquote>⚠️ تأكيد حذف @{target_bot_id}؟\nلا يمكن التراجع عن هذا الإجراء.</blockquote>", parse_mode="HTML", reply_markup=kb)
                else:
                    bot.send_message(user_id, "<blockquote>❌ لا تملك صلاحية حذف هذا البوت.</blockquote>", parse_mode="HTML")
            else:
                bot.send_message(user_id, "<blockquote>❌ البوت غير موجود.</blockquote>", parse_mode="HTML")

        @bot.callback_query_handler(func=lambda c: c.data.startswith("fac_confirm_del_"))
        def handle_confirm_delete(callback):
            bot.answer_callback_query(callback.id)
            user_id = callback.message.chat.id
            target_bot_id = callback.data.replace("fac_confirm_del_", "")
            if target_bot_id in factory.instances:
                inst = factory.instances[target_bot_id]
                if inst.data.owner_id == user_id:
                    if factory._delete_bot_instance(target_bot_id):
                        bot.edit_message_text(chat_id=user_id, message_id=callback.message.message_id, text=f"<blockquote>✅ تم حذف @{target_bot_id} بنجاح.</blockquote>", parse_mode="HTML")
                    else:
                        bot.send_message(user_id, "<blockquote>❌ فشل الحذف.</blockquote>", parse_mode="HTML")
                else:
                    bot.send_message(user_id, "<blockquote>❌ لا تملك الصلاحية.</blockquote>", parse_mode="HTML")
            else:
                bot.send_message(user_id, "<blockquote>❌ البوت غير موجود.</blockquote>", parse_mode="HTML")

        @bot.callback_query_handler(func=lambda c: c.data == "fac_cancel_del")
        def handle_cancel_delete(callback):
            bot.answer_callback_query(callback.id, "تم الإلغاء.")
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="<blockquote>❌ تم إلغاء الحذف.</blockquote>", parse_mode="HTML")

    # ========== خطوات إنشاء البوت ==========
    def _creation_step_token(self, message) -> None:
        user_id = message.chat.id
        token = message.text.strip()
        is_valid, result = self._validate_bot_token(token)
        if not is_valid:
            self.bot.send_message(user_id, f"<blockquote>❌ التوكن غير صحيح:\n{result}</blockquote>", parse_mode="HTML")
            prompt = self.bot.send_message(user_id, "<blockquote>🤖 أرسل التوكن الصحيح:</blockquote>", parse_mode="HTML")
            self.bot.register_next_step_handler(prompt, self._creation_step_token)
            return
        bot_name, bot_username = result
        session = _SESSION_STORE.get(user_id, {})
        session['token'] = token
        session['bot_name'] = bot_name
        session['bot_username'] = bot_username
        session['admin_id'] = user_id
        session['step'] = 'channel'
        prompt = self.bot.send_message(
            user_id,
            f"<blockquote>✅ تم التحقق من التوكن.\n"
            f"📌 الاسم: <b>{bot_name}</b>\n"
            f"🔗 اليوزر: @{bot_username}\n\n"
            f"👤 تم تعيينك كمشرف افتراضي (المعرف: <code>{user_id}</code>).\n\n"
            "📢 أرسل الآن معرف قناتك الرئيسية (@username) أو اكتب <b>تخطي</b> (سيتم تعيين القناة الافتراضية @mouhamed_maa):</blockquote>",
            parse_mode="HTML"
        )
        self.bot.register_next_step_handler(prompt, self._creation_step_complete)

    def _creation_step_complete(self, message) -> None:
        user_id = message.chat.id
        channel_username = message.text.strip().lstrip('@')
        if channel_username.lower() == "تخطي":
            channel_username = "mouhamed_maa"
        session = _SESSION_STORE.get(user_id, {})
        developer_username = message.from_user.username or f"user_{user_id}"
        token = session.get('token', '')
        admin_id = session.get('admin_id', user_id)
        owner_id = session.get('owner_id', user_id)
        success, result = self._create_new_bot(owner_id, token, admin_id, channel_username, developer_username)
        if success:
            bot_name, bot_username = result
            success_msg = (
                f"<blockquote>✅ تم إنشاء البوت بنجاح!\n\n"
                f"📌 الاسم: <b>{bot_name}</b>\n"
                f"🔗 اليوزر: @{bot_username}\n"
                f"👤 المشرف: <code>{admin_id}</code>\n"
                f"📢 القناة: @{channel_username}\n"
                f"👨‍💻 المطور: @{developer_username}</blockquote>"
            )
            self.bot.send_message(user_id, success_msg, parse_mode="HTML")
            if user_id != _MASTER_ID:
                try:
                    ui = message.from_user
                    notif = (
                        "<blockquote>🆕 <b>بوت جديد</b>\n\n"
                        f"👤 المالك: {ui.first_name or 'غير معروف'}\n"
                        f"🆔 معرفه: <code>{user_id}</code>\n"
                        f"🤖 البوت: {bot_name} (@{bot_username})\n"
                        f"📢 القناة: @{channel_username}\n"
                        f"👨‍💻 المطور: @{developer_username}</blockquote>"
                    )
                    self.bot.send_message(_MASTER_ID, notif, parse_mode="HTML")
                except Exception:
                    pass
        else:
            self.bot.send_message(user_id, f"<blockquote>❌ فشل إنشاء البوت:\n{result}</blockquote>", parse_mode="HTML")
        if user_id in _SESSION_STORE:
            del _SESSION_STORE[user_id]

    # ========== إذاعة المصنع ==========
    def _factory_broadcast(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        sc = 0
        fc = 0
        pm = self.bot.send_message(_MASTER_ID, "<blockquote>⏳ جاري الإذاعة...</blockquote>", parse_mode="HTML")
        for uid in list(self.all_users):
            if uid == _MASTER_ID:
                continue
            try:
                if message.text:
                    self.bot.send_message(uid, message.text, parse_mode="HTML")
                elif message.photo:
                    self.bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.video:
                    self.bot.send_video(uid, message.video.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.document:
                    self.bot.send_document(uid, message.document.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.audio:
                    self.bot.send_audio(uid, message.audio.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.voice:
                    self.bot.send_voice(uid, message.voice.file_id)
                elif message.sticker:
                    self.bot.send_sticker(uid, message.sticker.file_id)
                else:
                    self.bot.forward_message(uid, message.chat.id, message.message_id)
                sc += 1
            except Exception:
                fc += 1
        result = f"<blockquote>✅ اكتملت الإذاعة.\n\n✅ نجاح: {sc}\n❌ فشل: {fc}</blockquote>"
        try:
            self.bot.edit_message_text(chat_id=_MASTER_ID, message_id=pm.message_id, text=result, parse_mode="HTML")
        except Exception:
            self.bot.send_message(_MASTER_ID, result, parse_mode="HTML")

    # ========== إرسال للكل ==========
    def _factory_send_all(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        sc = 0
        fc = 0
        pm = self.bot.send_message(_MASTER_ID, "<blockquote>⏳ جاري الإرسال...</blockquote>", parse_mode="HTML")
        for uid in list(self.all_users):
            if uid == _MASTER_ID:
                continue
            try:
                if message.text:
                    self.bot.send_message(uid, message.text, parse_mode="HTML")
                elif message.photo:
                    self.bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.video:
                    self.bot.send_video(uid, message.video.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.document:
                    self.bot.send_document(uid, message.document.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.audio:
                    self.bot.send_audio(uid, message.audio.file_id, caption=message.caption or "", parse_mode="HTML")
                elif message.voice:
                    self.bot.send_voice(uid, message.voice.file_id)
                elif message.sticker:
                    self.bot.send_sticker(uid, message.sticker.file_id)
                else:
                    self.bot.forward_message(uid, message.chat.id, message.message_id)
                sc += 1
            except Exception:
                fc += 1
        result = f"<blockquote>✅ اكتمل الإرسال.\n\n✅ نجاح: {sc}\n❌ فشل: {fc}</blockquote>"
        try:
            self.bot.edit_message_text(chat_id=_MASTER_ID, message_id=pm.message_id, text=result, parse_mode="HTML")
        except Exception:
            self.bot.send_message(_MASTER_ID, result, parse_mode="HTML")

    # ========== إدارة حظر المصنع ==========
    def _factory_ban_user(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        try:
            target_id = int(message.text.strip())
            self.banned_users.add(target_id)
            self._save_all_data()
            self.bot.reply_to(message, f"<blockquote>✅ تم حظر المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    def _factory_unban_user(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        try:
            target_id = int(message.text.strip())
            self.banned_users.discard(target_id)
            self._save_all_data()
            self.bot.reply_to(message, f"<blockquote>✅ تم رفع الحظر عن المستخدم <code>{target_id}</code></blockquote>", parse_mode="HTML")
        except ValueError:
            self.bot.reply_to(message, "<blockquote>❌ معرف غير صحيح.</blockquote>", parse_mode="HTML")

    # ========== حذف بوت من المصنع ==========
    def _factory_delete_bot(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        input_text = message.text.strip()
        target = None
        if input_text.startswith('@'):
            bu = input_text[1:]
            if bu in self.instances:
                target = bu
        else:
            for bid, inst in self.instances.items():
                if inst.data.token == input_text:
                    target = bid
                    break
            if not target and input_text in self.instances:
                target = input_text
        if target:
            inst = self.instances[target]
            bn = inst.data.bot_name
            if self._delete_bot_instance(target):
                self.bot.reply_to(message, f"<blockquote>✅ تم حذف البوت {bn} (@{target})</blockquote>", parse_mode="HTML")
            else:
                self.bot.reply_to(message, "<blockquote>❌ فشل الحذف.</blockquote>", parse_mode="HTML")
        else:
            self.bot.reply_to(message, "<blockquote>❌ لم يتم العثور على البوت.</blockquote>", parse_mode="HTML")

    # ========== إدارة قنوات المصنع ==========
    def _factory_add_channel(self, message) -> None:
        if message.chat.id != _MASTER_ID:
            return
        ch = message.text.strip().lstrip('@')
        if ch not in self.factory_channels:
            self.factory_channels.append(ch)
            self._save_all_data()
            self.bot.reply_to(message, f"<blockquote>✅ تمت إضافة القناة @{ch}</blockquote>", parse_mode="HTML")
        else:
            self.bot.reply_to(message, f"<blockquote>⚠️ القناة @{ch} موجودة مسبقاً.</blockquote>", parse_mode="HTML")

    # ========== النسخ الاحتياطي ==========
    def _send_backup(self, chat_id: int) -> None:
        try:
            self._save_all_data()
            if os.path.exists(_DATA_FILE):
                with open(_DATA_FILE, 'rb') as f:
                    self.bot.send_document(
                        chat_id,
                        f,
                        caption=f"<blockquote>💾 <b>نسخة احتياطية</b>\n⏰ الوقت: {_format_timestamp()}</blockquote>",
                        parse_mode="HTML"
                    )
                self.bot.send_message(chat_id, "<blockquote>✅ تم إرسال النسخة الاحتياطية بنجاح.</blockquote>", parse_mode="HTML")
            else:
                self.bot.send_message(chat_id, "<blockquote>❌ لا يوجد ملف بيانات لإرساله.</blockquote>", parse_mode="HTML")
        except Exception as e:
            self.bot.send_message(chat_id, f"<blockquote>❌ فشل إنشاء النسخة الاحتياطية: {e}</blockquote>", parse_mode="HTML")

    # ========== تشغيل جميع البوتات ==========
    def _start_all_bots(self) -> None:
        for bid in list(self.instances.keys()):
            self._start_bot_instance(bid)
        print(f"✅ Started {len(self.instances)} bots")

    # ========== تشغيل المصنع ==========
    def run(self) -> None:
        self._register_factory_handlers()
        self._start_all_bots()
        print("🚀 Factory is running...")
        while True:
            try:
                self.bot.infinity_polling(timeout=60, long_polling_timeout=60)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as net_err:
                print(f"Factory network error: {net_err}. Retrying in 10s...")
                time.sleep(10)
            except Exception as ex:
                print(f"Factory polling exception: {ex}. Retrying in 5s...")
                time.sleep(5)


# ========== إدارة القفل ==========
def _acquire_process_lock() -> bool:
    try:
        if os.path.exists(_LOCK_FILE):
            with open(_LOCK_FILE, 'r') as lock_file:
                existing_pid = int(lock_file.read().strip())
            if psutil.pid_exists(existing_pid):
                print(f"⚠️ Already running (PID {existing_pid})")
                return False
            os.remove(_LOCK_FILE)
        with open(_LOCK_FILE, 'w') as lock_file:
            lock_file.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"lock error: {e}")
        return False

def _release_process_lock() -> None:
    try:
        if os.path.exists(_LOCK_FILE):
            os.remove(_LOCK_FILE)
    except Exception as e:
        print(f"unlock error: {e}")

def _handle_shutdown_signal(signum, frame) -> None:
    print("\n📢 Shutting down...")
    _release_process_lock()
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_shutdown_signal)
signal.signal(signal.SIGTERM, _handle_shutdown_signal)

# ========== نقطة الدخول ==========
if __name__ == "__main__":
    if not _acquire_process_lock():
        print("❌ Cannot run another instance")
        sys.exit(1)

    factory_instance = None
    try:
        factory_instance = FactoryBot()
        factory_instance.run()
    except Exception as e:
        print(f"fatal error: {e}")
    finally:
        if factory_instance:
            factory_instance._save_all_data()
        _release_process_lock()