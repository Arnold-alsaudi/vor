# KEVIN BOT Configuration
# تكوين بوت كيفن للبلاغات

import os
from typing import Optional

# معلومات البوت الأساسية
BOT_TOKEN: str = "7957882848:AAE2pTaAeYVFG1ktxphgL7uXyBobZbUkq1I"  # توكن البوت من @BotFather
API_ID: int = 24832079  # API ID من my.telegram.org
API_HASH: str = "32a07aa2a643d8182272dc072973cfde"  # API Hash من my.telegram.org

# معرف المالك الوحيد المسموح له باستخدام البوت
OWNER_ID: int = 7199265775  # ضع معرف التليجرام الخاص بك هنا (قيمة مؤقتة للاختبار)

# إعدادات البلاغات
DEFAULT_DELAY_BETWEEN_REPORTS: int = 30  # الوقت الافتراضي بين البلاغات (ثانية)
MAX_REPORTS_PER_SESSION: int = 5000  # الحد الأقصى للبلاغات لكل جلسة
SESSION_TIMEOUT: int = 300  # مهلة انتظار الجلسة (ثانية)

# مسارات الملفات
SESSIONS_DIR: str = "sessions"
SESSIONS_JSON: str = "sessions.json"

# رسائل البوت
WELCOME_MESSAGE = """
🤖 مرحباً بك في KEVIN BOT

🔰 بوت احترافي لإرسال البلاغات الحقيقية ضد القنوات المخالفة

⚠️ تحذير: استخدم البوت فقط ضد القنوات التي تنتهك قوانين تليجرام بوضوح

👤 المالك: فقط المستخدم المصرح له يمكنه استخدام هذا البوت
"""

UNAUTHORIZED_MESSAGE = """
❌ غير مصرح لك باستخدام هذا البوت

🔒 هذا البوت مخصص للمالك فقط
"""

# التحقق من صحة التكوين
def validate_config() -> bool:
    """التحقق من صحة إعدادات التكوين"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ خطأ: يجب تعيين BOT_TOKEN في config.py")
        return False
    
    if not API_ID or API_ID == 0:
        print("❌ خطأ: يجب تعيين API_ID في config.py")
        return False
    
    if not API_HASH or API_HASH == "YOUR_API_HASH_HERE":
        print("❌ خطأ: يجب تعيين API_HASH في config.py")
        return False
    
    if not OWNER_ID or OWNER_ID == 0:
        print("❌ خطأ: يجب تعيين OWNER_ID في config.py")
        return False
    
    return True

# إنشاء المجلدات المطلوبة
def create_directories():
    """إنشاء المجلدات المطلوبة للبوت"""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
        print(f"✅ تم إنشاء مجلد {SESSIONS_DIR}")