#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إعادة تعيين الجلسات
حذف جميع الجلسات المحفوظة لبدء جديد
"""

import os
import json
import sys

def reset_sessions():
    """حذف جميع الجلسات المحفوظة"""
    
    print("🔄 إعادة تعيين جلسات KEVIN BOT...")
    
    # مسارات الملفات
    sessions_file = "sessions.json"
    sessions_dir = "sessions"
    
    try:
        # حذف ملف الجلسات
        if os.path.exists(sessions_file):
            os.remove(sessions_file)
            print(f"✅ تم حذف {sessions_file}")
        else:
            print(f"⚠️ {sessions_file} غير موجود")
        
        # حذف مجلد الجلسات
        if os.path.exists(sessions_dir):
            import shutil
            shutil.rmtree(sessions_dir)
            print(f"✅ تم حذف مجلد {sessions_dir}")
        else:
            print(f"⚠️ مجلد {sessions_dir} غير موجود")
        
        # إنشاء ملف جلسات فارغ
        empty_sessions = {
            "sessions": {},
            "metadata": {
                "created": "2025-01-01",
                "version": "1.0"
            }
        }
        
        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump(empty_sessions, f, indent=2, ensure_ascii=False)
        
        print("✅ تم إنشاء ملف جلسات جديد فارغ")
        
        # إنشاء مجلد جلسات جديد
        os.makedirs(sessions_dir, exist_ok=True)
        print("✅ تم إنشاء مجلد جلسات جديد")
        
        print("\n🎉 تم إعادة تعيين الجلسات بنجاح!")
        print("📝 الآن يمكنك إضافة session strings جديدة عبر البوت")
        
    except Exception as e:
        print(f"❌ خطأ في إعادة التعيين: {e}")

def main():
    print("🔧 أداة إعادة تعيين جلسات KEVIN BOT")
    print("=" * 50)
    
    confirm = input("⚠️ هل تريد حذف جميع الجلسات المحفوظة؟ (y/n): ").strip().lower()
    
    if confirm in ['y', 'yes', 'نعم']:
        reset_sessions()
    else:
        print("❌ تم إلغاء العملية")

if __name__ == "__main__":
    main()