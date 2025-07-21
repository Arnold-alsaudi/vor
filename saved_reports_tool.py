#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إدارة البلاغات المحفوظة - KEVIN BOT
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from saved_reports_manager import saved_reports_manager

def main():
    """الدالة الرئيسية"""
    
    print("💾 أداة إدارة البلاغات المحفوظة - KEVIN BOT")
    print("=" * 60)
    
    while True:
        print("\n📋 الخيارات المتاحة:")
        print("1. عرض جميع البلاغات المحفوظة")
        print("2. البحث عن بلاغ بالمعرف")
        print("3. عرض إحصائيات البلاغات")
        print("4. تنظيف البلاغات القديمة")
        print("5. تصدير البلاغات إلى ملف")
        print("6. استيراد البلاغات من ملف")
        print("7. الخروج")
        
        choice = input("\n🔢 اختر (1-7): ").strip()
        
        if choice == "1":
            show_all_reports()
        elif choice == "2":
            search_report_by_id()
        elif choice == "3":
            show_statistics()
        elif choice == "4":
            cleanup_old_reports()
        elif choice == "5":
            export_reports()
        elif choice == "6":
            import_reports()
        elif choice == "7":
            print("👋 وداعاً!")
            break
        else:
            print("❌ اختيار غير صحيح")

def show_all_reports():
    """عرض جميع البلاغات المحفوظة"""
    print("\n💾 جميع البلاغات المحفوظة")
    print("-" * 80)
    
    if not saved_reports_manager.saved_data.get("reports"):
        print("📭 لا توجد بلاغات محفوظة")
        return
    
    reports = saved_reports_manager.saved_data["reports"]
    
    print(f"{'المعرف':<10} {'المستخدم':<12} {'القناة':<25} {'النوع':<15} {'العدد':<8} {'الاستخدام'}")
    print("-" * 80)
    
    for report_id, report_data in reports.items():
        user_id = str(report_data.get("user_id", "غير محدد"))
        channel = report_data.get("channel", "غير محدد")[:23]
        report_type = report_data.get("report_type", "غير محدد")[:13]
        count = report_data.get("report_count", 0)
        usage = report_data.get("usage_count", 0)
        
        print(f"{report_id:<10} {user_id:<12} {channel:<25} {report_type:<15} {count:<8} {usage}")

def search_report_by_id():
    """البحث عن بلاغ بالمعرف"""
    print("\n🔍 البحث عن بلاغ")
    print("-" * 30)
    
    report_id = input("أدخل معرف البلاغ: ").strip()
    
    if not report_id:
        print("❌ لم يتم إدخال معرف")
        return
    
    report_data = saved_reports_manager.get_report_by_id(report_id)
    
    if not report_data:
        print("❌ البلاغ غير موجود")
        return
    
    print(f"\n✅ تم العثور على البلاغ:")
    print(f"🆔 المعرف: {report_data.get('report_id')}")
    print(f"👤 المستخدم: {report_data.get('user_id')}")
    print(f"📡 القناة: {report_data.get('channel')}")
    print(f"📝 نوع البلاغ: {report_data.get('report_type')}")
    print(f"🔢 عدد البلاغات: {report_data.get('report_count', 0):,}")
    print(f"⏱️ التأخير: {report_data.get('delay_between_reports', 0)} ثانية")
    print(f"📊 مرات الاستخدام: {report_data.get('usage_count', 0)}")
    print(f"📅 تاريخ الإنشاء: {report_data.get('created_date', 'غير محدد')[:19]}")
    print(f"🕐 آخر استخدام: {report_data.get('last_used', 'غير محدد')[:19]}")
    print(f"📝 رسالة البلاغ:")
    print(f"   {report_data.get('report_message', 'غير محدد')[:100]}...")

def show_statistics():
    """عرض إحصائيات البلاغات"""
    print("\n📊 إحصائيات البلاغات المحفوظة")
    print("-" * 50)
    
    stats = saved_reports_manager.get_stats()
    
    print(f"📈 إجمالي البلاغات: {stats['total_reports']}")
    print(f"🟢 البلاغات النشطة: {stats['active_reports']}")
    print(f"📊 إجمالي الاستخدام: {stats['total_usage']}")
    
    if stats['channels_count']:
        print(f"\n📡 أكثر القنوات حفظاً:")
        sorted_channels = sorted(stats['channels_count'].items(), key=lambda x: x[1], reverse=True)
        for i, (channel, count) in enumerate(sorted_channels[:5], 1):
            print(f"   {i}. {channel}: {count} بلاغ")
    
    if stats['report_types_count']:
        print(f"\n📝 أكثر أنواع البلاغات:")
        sorted_types = sorted(stats['report_types_count'].items(), key=lambda x: x[1], reverse=True)
        for i, (report_type, count) in enumerate(sorted_types[:5], 1):
            print(f"   {i}. {report_type}: {count} بلاغ")
    
    print(f"\n📅 تاريخ الإنشاء: {stats.get('created_date', 'غير محدد')[:10]}")

def cleanup_old_reports():
    """تنظيف البلاغات القديمة"""
    print("\n🧹 تنظيف البلاغات القديمة")
    print("-" * 40)
    
    try:
        days = int(input("عدد الأيام (البلاغات الأقدم من هذا ستُحذف): ").strip() or "30")
    except ValueError:
        days = 30
    
    print(f"\n⚠️ سيتم حذف البلاغات التي لم تُستخدم منذ {days} يوم")
    confirm = input("هل أنت متأكد؟ (نعم/لا): ").strip().lower()
    
    if confirm in ['نعم', 'yes', 'y']:
        deleted_count = saved_reports_manager.cleanup_old_reports(days)
        print(f"✅ تم حذف {deleted_count} بلاغ قديم")
    else:
        print("❌ تم إلغاء العملية")

def export_reports():
    """تصدير البلاغات إلى ملف"""
    print("\n📤 تصدير البلاغات")
    print("-" * 30)
    
    try:
        filename = input("اسم الملف (افتراضي: exported_reports.json): ").strip()
        if not filename:
            filename = f"exported_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        # تصدير البيانات
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_reports": len(saved_reports_manager.saved_data["reports"]),
            "reports": saved_reports_manager.saved_data["reports"]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم تصدير {export_data['total_reports']} بلاغ إلى {filename}")
        
    except Exception as e:
        print(f"❌ خطأ في التصدير: {e}")

def import_reports():
    """استيراد البلاغات من ملف"""
    print("\n📥 استيراد البلاغات")
    print("-" * 30)
    
    filename = input("اسم الملف للاستيراد: ").strip()
    
    if not filename:
        print("❌ لم يتم إدخال اسم الملف")
        return
    
    if not os.path.exists(filename):
        print("❌ الملف غير موجود")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if "reports" not in import_data:
            print("❌ تنسيق الملف غير صحيح")
            return
        
        imported_reports = import_data["reports"]
        
        print(f"📊 الملف يحتوي على {len(imported_reports)} بلاغ")
        print(f"📅 تاريخ التصدير: {import_data.get('export_date', 'غير محدد')[:19]}")
        
        confirm = input("\nهل تريد المتابعة؟ (نعم/لا): ").strip().lower()
        
        if confirm not in ['نعم', 'yes', 'y']:
            print("❌ تم إلغاء العملية")
            return
        
        # دمج البلاغات
        imported_count = 0
        skipped_count = 0
        
        for report_id, report_data in imported_reports.items():
            if report_id not in saved_reports_manager.saved_data["reports"]:
                saved_reports_manager.saved_data["reports"][report_id] = report_data
                imported_count += 1
            else:
                skipped_count += 1
        
        # تحديث العدد الإجمالي
        saved_reports_manager.saved_data["total_saved"] = len(saved_reports_manager.saved_data["reports"])
        
        # حفظ البيانات
        if saved_reports_manager.save_reports_data():
            print(f"✅ تم استيراد {imported_count} بلاغ جديد")
            if skipped_count > 0:
                print(f"⚠️ تم تخطي {skipped_count} بلاغ موجود مسبقاً")
        else:
            print("❌ خطأ في حفظ البيانات")
        
    except Exception as e:
        print(f"❌ خطأ في الاستيراد: {e}")

def show_report_details(report_id: str):
    """عرض تفاصيل البلاغ"""
    report_data = saved_reports_manager.get_report_by_id(report_id)
    
    if not report_data:
        print("❌ البلاغ غير موجود")
        return
    
    print(f"\n📋 تفاصيل البلاغ {report_id}")
    print("=" * 50)
    
    # معلومات أساسية
    print(f"👤 المستخدم: {report_data.get('user_id')}")
    print(f"📡 القناة: {report_data.get('channel')}")
    print(f"📝 نوع البلاغ: {report_data.get('report_type')}")
    print(f"🔢 عدد البلاغات: {report_data.get('report_count', 0):,}")
    print(f"⏱️ التأخير: {report_data.get('delay_between_reports', 0)} ثانية")
    
    # إحصائيات الاستخدام
    print(f"📊 مرات الاستخدام: {report_data.get('usage_count', 0)}")
    print(f"📅 تاريخ الإنشاء: {report_data.get('created_date', 'غير محدد')[:19]}")
    print(f"🕐 آخر استخدام: {report_data.get('last_used', 'غير محدد')[:19]}")
    print(f"🟢 الحالة: {report_data.get('status', 'غير محدد')}")
    
    # رسالة البلاغ
    print(f"\n📝 رسالة البلاغ:")
    print(f"{report_data.get('report_message', 'غير محدد')}")
    
    # معلومات القناة إن وجدت
    channel_info = report_data.get('channel_info', {})
    if channel_info:
        print(f"\n📡 معلومات القناة:")
        print(f"   • العنوان: {channel_info.get('title', 'غير محدد')}")
        print(f"   • اليوزر: {channel_info.get('username', 'غير محدد')}")
    
    # نتائج التحليل الذكي إن وجدت
    analysis = report_data.get('analysis_results')
    if analysis:
        violations_count = len(analysis.get('violations_found', []))
        print(f"\n🧠 نتائج التحليل الذكي:")
        print(f"   • المخالفات المكتشفة: {violations_count}")
        print(f"   • الرسائل المحللة: {analysis.get('messages_analyzed', 0)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")