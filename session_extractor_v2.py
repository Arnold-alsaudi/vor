#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEVIN BOT - مستخرج Session Strings المحسن
نسخة محسنة لاستخراج session strings
"""

import asyncio
import sys
import os

# إضافة المسار للوحدات المحلية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, RPCError
import config

class SessionExtractorV2:
    """مستخرج session strings محسن"""
    
    def __init__(self):
        self.client = None
    
    async def extract_session(self, phone_number: str) -> str:
        """استخراج session string لرقم هاتف معين"""
        
        print(f"🔄 بدء استخراج الجلسة للرقم: {phone_number}")
        
        try:
            # إنشاء عميل باستخدام StringSession فارغة
            self.client = TelegramClient(
                StringSession(),
                config.API_ID,
                config.API_HASH
            )
            
            # الاتصال
            await self.client.connect()
            print("✅ تم الاتصال بخوادم تليجرام")
            
            # إرسال كود التحقق
            print("📱 جاري إرسال كود التحقق...")
            sent_code = await self.client.send_code_request(phone_number)
            
            # طلب كود التحقق
            code = input("🔢 أدخل كود التحقق المرسل إليك: ").strip()
            
            try:
                # تسجيل الدخول بالكود
                await self.client.sign_in(phone_number, code)
                
            except SessionPasswordNeededError:
                # إذا كان هناك تحقق ثنائي
                password = input("🔐 أدخل كلمة المرور الثنائية: ").strip()
                await self.client.sign_in(password=password)
            
            # التحقق من نجاح تسجيل الدخول
            if await self.client.is_user_authorized():
                # الحصول على معلومات المستخدم
                me = await self.client.get_me()
                print(f"✅ تم تسجيل الدخول بنجاح: {me.first_name}")
                
                # استخراج session string
                session_string = self.client.session.save()
                
                if session_string and len(session_string) > 50:
                    print("🎉 تم استخراج Session String بنجاح!")
                    print("=" * 60)
                    print("📋 Session String:")
                    print(session_string)
                    print("=" * 60)
                    print("⚠️ احتفظ بهذا النص في مكان آمن!")
                    
                    return session_string
                else:
                    print("❌ فشل في استخراج session string صحيح")
                    return None
            else:
                print("❌ فشل في تسجيل الدخول")
                return None
                
        except PhoneCodeInvalidError:
            print("❌ كود التحقق غير صحيح")
            return None
        except RPCError as e:
            print(f"❌ خطأ في API: {e}")
            return None
        except Exception as e:
            print(f"❌ خطأ في استخراج الجلسة: {e}")
            return None
        finally:
            if self.client:
                await self.client.disconnect()

def print_banner():
    """طباعة شعار مستخرج الجلسات"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🔑 KEVIN BOT - مستخرج Session Strings المحسن              ║
║                                                              ║
║  📱 استخراج session strings للحسابات                        ║
║  🔒 آمن ومحمي                                               ║
║  ⚡ نسخة محسنة                                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """الدالة الرئيسية"""
    print_banner()
    
    extractor = SessionExtractorV2()
    
    while True:
        print("\n📱 أدخل رقم الهاتف (مع رمز البلد)")
        print("مثال: +1234567890")
        print("أو اكتب 'exit' للخروج")
        
        phone = input("📞 رقم الهاتف: ").strip()
        
        if phone.lower() == 'exit':
            print("👋 وداعاً!")
            break
        
        if not phone:
            print("❌ يرجى إدخال رقم هاتف صحيح")
            continue
        
        if not phone.startswith('+'):
            print("❌ يرجى إدخال رقم الهاتف مع رمز البلد (مثال: +1234567890)")
            continue
        
        try:
            session_string = await extractor.extract_session(phone)
            
            if session_string:
                print("✅ تم استخراج الجلسة بنجاح!")
                
                # حفظ في ملف
                filename = f"session_{phone.replace('+', '').replace(' ', '')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(session_string)
                print(f"💾 تم حفظ session string في ملف: {filename}")
                
            else:
                print("❌ فشل في استخراج الجلسة")
                
        except KeyboardInterrupt:
            print("\n⏹️ تم إلغاء العملية")
            break
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
        
        print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)