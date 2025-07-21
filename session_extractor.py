#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEVIN BOT - مستخرج Session Strings
أداة مساعدة لاستخراج session strings من حسابات تليجرام

هذا السكريبت يساعد في الحصول على session strings للحسابات
التي ستستخدم في إرسال البلاغات
"""

import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, RPCError
import config

class SessionExtractor:
    """مستخرج session strings للحسابات"""
    
    def __init__(self):
        self.client = None
    
    async def extract_session(self, phone_number: str) -> str:
        """استخراج session string لرقم هاتف معين"""
        
        print(f"🔄 بدء استخراج الجلسة للرقم: {phone_number}")
        
        # إنشاء عميل مؤقت باستخدام StringSession
        self.client = TelegramClient(
            StringSession(),
            config.API_ID,
            config.API_HASH
        )
        
        try:
            await self.client.connect()
            
            # إرسال كود التحقق
            print("📱 جاري إرسال كود التحقق...")
            sent_code = await self.client.send_code_request(phone_number)
            
            # طلب كود التحقق من المستخدم
            code = input("🔢 أدخل كود التحقق المرسل إليك: ").strip()
            
            try:
                # تسجيل الدخول بالكود
                await self.client.sign_in(phone_number, code)
                
            except SessionPasswordNeededError:
                # إذا كان هناك كلمة مرور ثنائية
                password = input("🔐 أدخل كلمة المرور الثنائية: ").strip()
                await self.client.sign_in(password=password)
            
            # التحقق من نجاح تسجيل الدخول
            if await self.client.is_user_authorized():
                # الحصول على معلومات المستخدم
                me = await self.client.get_me()
                print(f"✅ تم تسجيل الدخول بنجاح: {me.first_name}")
                
                # استخراج session string
                session_string = self.client.session.save()
                
                # التحقق من صحة session string
                if session_string and len(session_string) > 10:
                    print("✅ تم استخراج session string بنجاح!")
                else:
                    print("❌ فشل في استخراج session string صحيح")
                    return None
                
                print("🎉 تم استخراج Session String بنجاح!")
                print("=" * 60)
                print("📋 Session String:")
                print(session_string)
                print("=" * 60)
                print("⚠️ احتفظ بهذا النص في مكان آمن!")
                
                return session_string
            
            else:
                print("❌ فشل في تسجيل الدخول")
                return None
                
        except PhoneCodeInvalidError:
            print("❌ كود التحقق غير صحيح")
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
║              📱 KEVIN BOT - Session Extractor                ║
║                                                              ║
║                   مستخرج جلسات تليجرام                        ║
║                                                              ║
║  🔐 أداة آمنة لاستخراج session strings للحسابات              ║
║  📋 للاستخدام مع KEVIN BOT                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_phone_number(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والرموز غير المرغوبة
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # يجب أن يبدأ بـ + ويحتوي على أرقام فقط
    if not phone.startswith("+"):
        return False
    
    # إزالة + والتحقق من أن الباقي أرقام
    numbers_only = phone[1:]
    if not numbers_only.isdigit():
        return False
    
    # يجب أن يكون طوله بين 10 و 15 رقم
    if len(numbers_only) < 10 or len(numbers_only) > 15:
        return False
    
    return True

async def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # التحقق من التكوين
    if not config.validate_config():
        print("❌ خطأ في التكوين. تحقق من config.py")
        return
    
    print("🔧 مستخرج Session Strings لـ KEVIN BOT")
    print("=" * 50)
    
    extractor = SessionExtractor()
    
    while True:
        print("\n📱 أدخل رقم الهاتف (مع رمز البلد)")
        print("مثال: +1234567890")
        print("أو اكتب 'exit' للخروج")
        
        phone_input = input("📞 رقم الهاتف: ").strip()
        
        if phone_input.lower() in ['exit', 'quit', 'خروج']:
            print("👋 وداعاً!")
            break
        
        if not validate_phone_number(phone_input):
            print("❌ رقم الهاتف غير صحيح. تأكد من التنسيق: +1234567890")
            continue
        
        try:
            session_string = await extractor.extract_session(phone_input)
            
            if session_string:
                print("\n✅ تم استخراج الجلسة بنجاح!")
                print("📋 يمكنك الآن نسخ Session String واستخدامه في KEVIN BOT")
                
                # حفظ في ملف (اختياري)
                save_choice = input("\n💾 هل تريد حفظ Session String في ملف؟ (y/n): ").strip().lower()
                if save_choice in ['y', 'yes', 'نعم']:
                    filename = f"session_{phone_input.replace('+', '').replace(' ', '')}.txt"
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"Phone: {phone_input}\n")
                            f.write(f"Session String: {session_string}\n")
                            f.write(f"Generated by KEVIN BOT Session Extractor\n")
                        print(f"💾 تم حفظ الجلسة في: {filename}")
                    except Exception as e:
                        print(f"❌ خطأ في حفظ الملف: {e}")
            
            else:
                print("❌ فشل في استخراج الجلسة")
            
        except KeyboardInterrupt:
            print("\n⏹️ تم إلغاء العملية")
            break
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)