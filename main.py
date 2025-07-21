#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEVIN BOT - بوت تليجرام احترافي للبلاغات
نظام متقدم لإرسال البلاغات الحقيقية ضد القنوات المخالفة

المطور: تم تطويره باستخدام Telethon
الهدف: مكافحة المحتوى المخالف على تليجرام
"""

import asyncio
import logging
import sys
import os
from telethon import TelegramClient
from telethon.errors import AuthKeyError, RPCError

# إعداد المسار للوحدات المحلية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from handlers import BotHandlers
from session_manager import SessionManager

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kevin_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class KevinBot:
    """الفئة الرئيسية لبوت كيفن"""
    
    def __init__(self):
        self.client = None
        self.handlers = None
        self.is_running = False
    
    async def initialize(self):
        """تهيئة البوت"""
        try:
            # التحقق من صحة التكوين
            if not config.validate_config():
                logger.error("❌ فشل في التحقق من التكوين")
                return False
            
            # إنشاء المجلدات المطلوبة
            config.create_directories()
            
            # إنشاء عميل التليجرام
            self.client = TelegramClient(
                'kevin_bot',
                config.API_ID,
                config.API_HASH
            )
            
            # بدء العميل
            await self.client.start(bot_token=config.BOT_TOKEN)
            
            # التحقق من صحة البوت
            bot_info = await self.client.get_me()
            logger.info(f"✅ تم تسجيل الدخول كـ: {bot_info.username}")
            
            # إعداد مدير الجلسات
            session_manager = SessionManager()
            
            # إعداد معالجات الأحداث
            self.handlers = BotHandlers(self.client)
            self.handlers.set_session_manager(session_manager)
            
            logger.info("🚀 تم تهيئة KEVIN BOT بنجاح")
            return True
            
        except AuthKeyError:
            logger.error("❌ خطأ في مفاتيح API - تحقق من API_ID و API_HASH")
            return False
        except RPCError as e:
            if "API_ID_INVALID" in str(e):
                logger.error("❌ API_ID غير صحيح")
            elif "API_HASH_INVALID" in str(e):
                logger.error("❌ API_HASH غير صحيح")
            else:
                logger.error(f"❌ خطأ في API: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة البوت: {e}")
            return False
    
    async def start(self):
        """بدء تشغيل البوت"""
        if not await self.initialize():
            logger.error("❌ فشل في تهيئة البوت")
            return
        
        self.is_running = True
        logger.info("🟢 KEVIN BOT يعمل الآن...")
        
        try:
            # إرسال رسالة للمالك عند بدء التشغيل
            await self.send_startup_message()
            
            # تشغيل البوت
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """إيقاف البوت"""
        if self.is_running:
            self.is_running = False
            logger.info("🔴 جاري إيقاف KEVIN BOT...")
            
            if self.client:
                await self.client.disconnect()
            
            logger.info("✅ تم إيقاف KEVIN BOT بنجاح")
    
    async def send_startup_message(self):
        """إرسال رسالة بدء التشغيل للمالك"""
        try:
            # التحقق من صحة OWNER_ID
            if config.OWNER_ID == 0 or config.OWNER_ID == 123456789:
                logger.info("⚠️ OWNER_ID غير مكوّن بشكل صحيح - تخطي رسالة بدء التشغيل")
                return
            
            startup_message = f"""
🤖 **KEVIN BOT - تم بدء التشغيل**

✅ البوت يعمل الآن بنجاح
🕐 وقت البدء: {asyncio.get_event_loop().time()}

🔧 **الإعدادات:**
• المالك: {config.OWNER_ID}
• الحد الأقصى للبلاغات: {config.MAX_REPORTS_PER_SESSION}
• التأخير الافتراضي: {config.DEFAULT_DELAY_BETWEEN_REPORTS}s

📝 استخدم /start للبدء
            """
            
            await self.client.send_message(config.OWNER_ID, startup_message)
            logger.info("✅ تم إرسال رسالة بدء التشغيل للمالك")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في إرسال رسالة بدء التشغيل: {e}")
            logger.info("💡 تأكد من تحديث OWNER_ID في config.py بمعرف التليجرام الصحيح")

def print_banner():
    """طباعة شعار البوت"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗  ██╗███████╗██╗   ██╗██╗███╗   ██╗    ██████╗  ██████╗████████╗    ║
║    ██║ ██╔╝██╔════╝██║   ██║██║████╗  ██║    ██╔══██╗██╔═══██╗╚══██╔══╝    ║
║    █████╔╝ █████╗  ██║   ██║██║██╔██╗ ██║    ██████╔╝██║   ██║   ██║       ║
║    ██╔═██╗ ██╔══╝  ╚██╗ ██╔╝██║██║╚██╗██║    ██╔══██╗██║   ██║   ██║       ║
║    ██║  ██╗███████╗ ╚████╔╝ ██║██║ ╚████║    ██████╔╝╚██████╔╝   ██║       ║
║    ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═══╝    ╚═════╝  ╚═════╝    ╚═╝       ║
║                                                              ║
║                    🤖 بوت البلاغات الاحترافي                   ║
║                                                              ║
║  📡 نظام متقدم لإرسال البلاغات الحقيقية ضد القنوات المخالفة    ║
║  🔒 آمن ومحمي - للاستخدام المسؤول فقط                         ║
║  ⚡ مطور باستخدام Telethon                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 7):
        print("❌ خطأ: يتطلب Python 3.7 أو أحدث")
        sys.exit(1)

async def main():
    """الدالة الرئيسية"""
    print_banner()
    check_python_version()
    
    logger.info("🚀 بدء تشغيل KEVIN BOT...")
    
    # إنشاء مثيل البوت
    bot = KevinBot()
    
    try:
        # بدء تشغيل البوت
        await bot.start()
    except Exception as e:
        logger.error(f"❌ خطأ فادح في البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # تشغيل البوت
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)