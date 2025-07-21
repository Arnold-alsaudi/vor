#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KEVIN BOT - بوت تليجرام احترافي للبلاغات
"""

import asyncio
import logging
import sys
import os
from threading import Thread
from flask import Flask
from telethon import TelegramClient
from telethon.errors import AuthKeyError, RPCError

# إعداد المسار للوحدات المحلية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from handlers import BotHandlers
from session_manager import SessionManager

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kevin_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# --------- إضافة Flask لتشغيل البوت على Railway ---------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ KEVIN BOT IS RUNNING!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# ----------------------------------------------------------

class KevinBot:
    def __init__(self):
        self.client = None
        self.handlers = None
        self.is_running = False

    async def initialize(self):
        try:
            if not config.validate_config():
                logger.error("❌ فشل في التحقق من التكوين")
                return False

            config.create_directories()

            self.client = TelegramClient(
                'kevin_bot',
                config.API_ID,
                config.API_HASH
            )

            await self.client.start(bot_token=config.BOT_TOKEN)

            bot_info = await self.client.get_me()
            logger.info(f"✅ تم تسجيل الدخول كـ: {bot_info.username}")

            session_manager = SessionManager()

            self.handlers = BotHandlers(self.client)
            self.handlers.set_session_manager(session_manager)

            logger.info("🚀 تم تهيئة KEVIN BOT بنجاح")
            return True

        except AuthKeyError:
            logger.error("❌ خطأ في مفاتيح API")
            return False
        except RPCError as e:
            logger.error(f"❌ خطأ في API: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ خطأ في التهيئة: {e}")
            return False

    async def start(self):
        if not await self.initialize():
            logger.error("❌ فشل في تهيئة البوت")
            return

        self.is_running = True
        logger.info("🟢 KEVIN BOT يعمل الآن...")

        try:
            await self.send_startup_message()
            await self.client.run_until_disconnected()

        except KeyboardInterrupt:
            logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
        except Exception as e:
            logger.error(f"❌ خطأ في التشغيل: {e}")
        finally:
            await self.stop()

    async def stop(self):
        if self.is_running:
            self.is_running = False
            logger.info("🔴 جاري إيقاف KEVIN BOT...")
            if self.client:
                await self.client.disconnect()
            logger.info("✅ تم إيقاف KEVIN BOT")

    async def send_startup_message(self):
        try:
            if config.OWNER_ID in (0, 123456789):
                logger.info("⚠️ OWNER_ID غير صحيح - لن يتم إرسال رسالة بدء التشغيل")
                return

            startup_message = f"""
🤖 **KEVIN BOT - تم بدء التشغيل**
✅ البوت يعمل الآن بنجاح
🕐 وقت البدء: {asyncio.get_event_loop().time()}
🔧 **الإعدادات:**
• المالك: {config.OWNER_ID}
• الحد الأقصى للبلاغات: {config.MAX_REPORTS_PER_SESSION}
• التأخير: {config.DEFAULT_DELAY_BETWEEN_REPORTS}s
📝 استخدم /start للبدء
            """

            await self.client.send_message(config.OWNER_ID, startup_message)
            logger.info("✅ تم إرسال رسالة البدء")
        except Exception as e:
            logger.warning(f"⚠️ فشل إرسال الرسالة: {e}")

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                      🤖 KEVIN BOT بدأ العمل                  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 أو أحدث مطلوب")
        sys.exit(1)

async def main():
    print_banner()
    check_python_version()

    logger.info("🚀 بدء تشغيل KEVIN BOT...")

    # تشغيل Flask keep-alive
    keep_alive()

    bot = KevinBot()
    try:
        await bot.start()
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)
