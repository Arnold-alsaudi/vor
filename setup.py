#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEVIN BOT - سكريبت الإعداد السريع
أداة لإعداد البوت بسهولة وسرعة
"""

import os
import sys
import subprocess
import json

def print_banner():
    """طباعة شعار الإعداد"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ⚙️ KEVIN BOT - Quick Setup                      ║
║                                                              ║
║                   إعداد سريع للبوت                           ║
║                                                              ║
║  🚀 إعداد تلقائي لجميع متطلبات البوت                         ║
║  📋 تكوين سهل وسريع                                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 7):
        print("❌ خطأ: يتطلب Python 3.7 أو أحدث")
        print(f"الإصدار الحالي: {sys.version}")
        return False
    
    print(f"✅ إصدار Python مناسب: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📦 تثبيت المتطلبات...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت جميع المتطلبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False
    except FileNotFoundError:
        print("❌ ملف requirements.txt غير موجود")
        return False

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    print("\n📁 إنشاء المجلدات...")
    
    directories = ["sessions"]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ تم إنشاء مجلد: {directory}")
            else:
                print(f"📁 المجلد موجود بالفعل: {directory}")
        except Exception as e:
            print(f"❌ خطأ في إنشاء المجلد {directory}: {e}")
            return False
    
    return True

def create_sessions_json():
    """إنشاء ملف sessions.json"""
    print("\n📄 إنشاء ملف sessions.json...")
    
    try:
        if not os.path.exists("sessions.json"):
            with open("sessions.json", "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print("✅ تم إنشاء ملف sessions.json")
        else:
            print("📄 ملف sessions.json موجود بالفعل")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف sessions.json: {e}")
        return False

def setup_config():
    """إعداد ملف التكوين"""
    print("\n⚙️ إعداد التكوين...")
    
    print("يرجى إدخال المعلومات التالية:")
    print("(يمكنك تركها فارغة وتعديلها لاحقاً في config.py)")
    
    # قراءة المعلومات من المستخدم
    bot_token = input("🤖 Bot Token (من @BotFather): ").strip()
    api_id = input("🔑 API ID (من my.telegram.org): ").strip()
    api_hash = input("🔐 API Hash (من my.telegram.org): ").strip()
    owner_id = input("👤 Owner ID (معرف التليجرام الخاص بك): ").strip()
    
    # قراءة ملف config.py الحالي
    try:
        with open("config.py", "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # تحديث القيم إذا تم إدخالها
        if bot_token:
            config_content = config_content.replace(
                'BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"',
                f'BOT_TOKEN: str = "{bot_token}"'
            )
        
        if api_id and api_id.isdigit():
            config_content = config_content.replace(
                'API_ID: int = 0',
                f'API_ID: int = {api_id}'
            )
        
        if api_hash:
            config_content = config_content.replace(
                'API_HASH: str = "YOUR_API_HASH_HERE"',
                f'API_HASH: str = "{api_hash}"'
            )
        
        if owner_id and owner_id.isdigit():
            config_content = config_content.replace(
                'OWNER_ID: int = 0',
                f'OWNER_ID: int = {owner_id}'
            )
        
        # حفظ الملف المحدث
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print("✅ تم تحديث ملف التكوين")
        
        # التحقق من اكتمال التكوين
        if bot_token and api_id and api_hash and owner_id:
            print("🎉 التكوين مكتمل! يمكنك تشغيل البوت الآن")
        else:
            print("⚠️ بعض المعلومات مفقودة. يرجى تعديل config.py يدوياً")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث التكوين: {e}")
        return False

def show_next_steps():
    """عرض الخطوات التالية"""
    print("\n" + "="*60)
    print("🎯 الخطوات التالية:")
    print("="*60)
    
    print("\n1️⃣ تأكد من اكتمال التكوين في config.py:")
    print("   • BOT_TOKEN من @BotFather")
    print("   • API_ID و API_HASH من my.telegram.org")
    print("   • OWNER_ID (معرف التليجرام الخاص بك)")
    
    print("\n2️⃣ استخرج session strings للحسابات:")
    print("   python session_extractor.py")
    
    print("\n3️⃣ شغل البوت:")
    print("   python main.py")
    
    print("\n4️⃣ أرسل /start للبوت وابدأ الاستخدام")
    
    print("\n📚 للمساعدة الكاملة، اقرأ README.md")
    print("="*60)

def main():
    """الدالة الرئيسية للإعداد"""
    print_banner()
    
    print("🚀 بدء إعداد KEVIN BOT...")
    
    # التحقق من إصدار Python
    if not check_python_version():
        return False
    
    # تثبيت المتطلبات
    if not install_requirements():
        print("❌ فشل في تثبيت المتطلبات")
        return False
    
    # إنشاء المجلدات
    if not create_directories():
        print("❌ فشل في إنشاء المجلدات")
        return False
    
    # إنشاء ملف sessions.json
    if not create_sessions_json():
        print("❌ فشل في إنشاء ملف sessions.json")
        return False
    
    # إعداد التكوين
    setup_choice = input("\n❓ هل تريد إعداد التكوين الآن؟ (y/n): ").strip().lower()
    if setup_choice in ['y', 'yes', 'نعم']:
        setup_config()
    else:
        print("⚠️ تذكر تعديل config.py قبل تشغيل البوت")
    
    print("\n✅ تم الانتهاء من الإعداد بنجاح!")
    
    # عرض الخطوات التالية
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ فشل في الإعداد")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ تم إلغاء الإعداد")
    except Exception as e:
        print(f"\n❌ خطأ فادح في الإعداد: {e}")
        sys.exit(1)