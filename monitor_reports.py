#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مراقب البلاغات - مشاهدة البلاغات المرسلة في الوقت الفعلي
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def monitor_reports():
    """مراقبة البلاغات المرسلة"""
    
    print("📊 مراقب البلاغات - KEVIN BOT")
    print("=" * 50)
    
    # قراءة ملف الجلسات لمعرفة الحسابات النشطة
    try:
        with open("sessions.json", 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        sessions = sessions_data.get("sessions", {})
        print(f"👥 الحسابات المتاحة: {len(sessions)}")
        
        for session_id, session_info in sessions.items():
            status = session_info.get("status", "unknown")
            reports_sent = session_info.get("reports_sent", 0)
            phone = session_info.get("phone", "غير محدد")
            
            print(f"   📱 {session_id}: {phone} - {reports_sent} بلاغ - {status}")
        
    except FileNotFoundError:
        print("⚠️ لا توجد جلسات محفوظة")
    except Exception as e:
        print(f"❌ خطأ في قراءة الجلسات: {e}")
    
    print("\n" + "=" * 50)
    
    # مراقبة السجلات
    log_file = "kevin_bot.log"
    
    if not os.path.exists(log_file):
        print(f"⚠️ ملف السجل غير موجود: {log_file}")
        return
    
    print(f"📋 مراقبة السجلات من: {log_file}")
    print("🔄 اضغط Ctrl+C للإيقاف")
    print("-" * 50)
    
    try:
        # قراءة آخر السجلات
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # عرض آخر 20 سطر
            recent_lines = lines[-20:] if len(lines) > 20 else lines
            
            print("📜 آخر السجلات:")
            for line in recent_lines:
                if any(keyword in line.lower() for keyword in ['بلاغ', 'report', 'error', 'success']):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {line.strip()}")
        
        # مراقبة مستمرة
        print("\n🔍 مراقبة مستمرة للبلاغات الجديدة...")
        
        # متابعة الملف للتحديثات الجديدة
        with open(log_file, 'r', encoding='utf-8') as f:
            # الانتقال لنهاية الملف
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    if any(keyword in line.lower() for keyword in ['بلاغ', 'report', 'error', 'success']):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] {line.strip()}")
                else:
                    # انتظار قصير قبل المحاولة مرة أخرى
                    asyncio.sleep(0.5)
                    
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف المراقبة")
    except Exception as e:
        print(f"❌ خطأ في المراقبة: {e}")

def show_report_statistics():
    """عرض إحصائيات البلاغات"""
    
    print("\n📊 إحصائيات البلاغات")
    print("=" * 30)
    
    try:
        # قراءة ملف الجلسات
        with open("sessions.json", 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        sessions = sessions_data.get("sessions", {})
        
        total_reports = 0
        active_sessions = 0
        
        for session_id, session_info in sessions.items():
            reports_sent = session_info.get("reports_sent", 0)
            status = session_info.get("status", "unknown")
            
            total_reports += reports_sent
            
            if status == "active":
                active_sessions += 1
        
        print(f"📱 إجمالي الحسابات: {len(sessions)}")
        print(f"🟢 الحسابات النشطة: {active_sessions}")
        print(f"📡 إجمالي البلاغات المرسلة: {total_reports}")
        
        if len(sessions) > 0:
            avg_reports = total_reports / len(sessions)
            print(f"📈 متوسط البلاغات لكل حساب: {avg_reports:.1f}")
        
    except FileNotFoundError:
        print("⚠️ لا توجد بيانات إحصائية")
    except Exception as e:
        print(f"❌ خطأ في قراءة الإحصائيات: {e}")

def main():
    """الدالة الرئيسية"""
    
    print("🔍 مراقب البلاغات - KEVIN BOT")
    print("=" * 40)
    print("1. مراقبة البلاغات المباشرة")
    print("2. عرض الإحصائيات")
    print("3. الخروج")
    
    while True:
        choice = input("\n🔢 اختر (1-3): ").strip()
        
        if choice == "1":
            monitor_reports()
            break
        elif choice == "2":
            show_report_statistics()
        elif choice == "3":
            print("👋 وداعاً!")
            break
        else:
            print("❌ اختيار غير صحيح")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")