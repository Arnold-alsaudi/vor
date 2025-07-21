#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة التحليل الذكي للقنوات - KEVIN BOT
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from telethon.sessions import StringSession
from smart_reporter import smart_reporter
import config

async def analyze_channel_smart(session_string: str, channel: str, message_limit: int = 50):
    """تحليل ذكي للقناة"""
    
    try:
        print(f"🔍 بدء التحليل الذكي للقناة: {channel}")
        print("=" * 60)
        
        # إنشاء العميل
        client = TelegramClient(
            StringSession(session_string),
            config.API_ID,
            config.API_HASH
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ الجلسة غير مفوضة")
            return
        
        # تحليل القناة
        analysis = await smart_reporter.analyze_channel(client, channel, message_limit)
        
        if "error" in analysis:
            print(f"❌ خطأ في التحليل: {analysis['error']}")
            return
        
        # عرض النتائج
        print_analysis_results(analysis)
        
        # حفظ النتائج
        save_analysis_results(analysis, channel)
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def print_analysis_results(analysis: dict):
    """عرض نتائج التحليل"""
    
    channel_info = analysis["channel_info"]
    
    print(f"📊 **تقرير التحليل الذكي**")
    print(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print(f"📡 **معلومات القناة:**")
    print(f"   • الاسم: {channel_info['title']}")
    print(f"   • اليوزر: @{channel_info['username']}")
    print(f"   • المشتركين: {channel_info['participants_count']:,}")
    print(f"   • المعرف: {channel_info['id']}")
    
    print(f"\n🔍 **إحصائيات التحليل:**")
    print(f"   • الرسائل المحللة: {analysis['messages_analyzed']}")
    print(f"   • المخالفات المكتشفة: {len(analysis['violations_found'])}")
    
    # توزيع الخطورة
    severity_dist = analysis["severity_distribution"]
    print(f"\n⚠️ **توزيع مستويات الخطورة:**")
    for severity, count in severity_dist.items():
        if count > 0:
            emoji = {"none": "⚪", "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}.get(severity, "⚪")
            print(f"   {emoji} {severity.upper()}: {count}")
    
    # ملخص المخالفات
    if analysis["violation_summary"]:
        print(f"\n🚨 **أنواع المخالفات المكتشفة:**")
        violation_names = {
            "personal_info": "نشر معلومات شخصية",
            "sexual_content": "محتوى جنسي",
            "violence": "عنف وتهديد",
            "scam": "احتيال ونصب",
            "drugs": "ترويج مخدرات",
            "fake_accounts": "انتحال شخصية",
            "child_abuse": "إساءة للأطفال"
        }
        
        for violation_type, count in analysis["violation_summary"].items():
            name = violation_names.get(violation_type, violation_type)
            print(f"   🔸 {name}: {count} حالة")
    
    # البلاغات المقترحة
    if analysis["recommended_reports"]:
        print(f"\n📝 **البلاغات الذكية المقترحة:**")
        print("=" * 60)
        
        for i, report in enumerate(analysis["recommended_reports"], 1):
            violation_name = {
                "personal_info": "🧷 نشر معلومات شخصية",
                "sexual_content": "🔞 محتوى جنسي",
                "violence": "💣 عنف وتهديد",
                "scam": "💰 احتيال ونصب",
                "drugs": "🧪 ترويج مخدرات",
                "fake_accounts": "🎭 انتحال شخصية",
                "child_abuse": "👶 إساءة للأطفال"
            }.get(report["violation_type"], report["violation_type"])
            
            print(f"\n{i}. {violation_name}")
            print(f"   📊 الأولوية: {report['priority']}/10")
            print(f"   🔍 الأدلة: {report['evidence_count']} حالة")
            print(f"   📝 نص البلاغ:")
            print(f"      {report['report_message']}")
    
    # أمثلة على المخالفات
    if analysis["violations_found"]:
        print(f"\n🔍 **أمثلة على المخالفات المكتشفة:**")
        print("=" * 60)
        
        for i, violation in enumerate(analysis["violations_found"][:3], 1):  # أول 3 أمثلة
            print(f"\n{i}. رسالة رقم {violation['message_id']}")
            print(f"   📅 التاريخ: {violation['date'][:19] if violation['date'] else 'غير محدد'}")
            print(f"   ⚠️ الخطورة: {violation['severity'].upper()}")
            print(f"   📝 المحتوى: {violation['message_text']}")
            print(f"   🚨 المخالفات:")
            for v in violation['violations']:
                print(f"      • {v['type']}: {v.get('keyword', v.get('pattern', 'غير محدد'))}")

def save_analysis_results(analysis: dict, channel: str):
    """حفظ نتائج التحليل"""
    try:
        filename = f"analysis_{channel.replace('@', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير في: {filename}")
        
    except Exception as e:
        print(f"❌ خطأ في حفظ التقرير: {e}")

async def test_report_message():
    """اختبار رسائل البلاغ"""
    
    print("🧪 اختبار جودة رسائل البلاغ")
    print("=" * 40)
    
    test_messages = [
        "test",
        "بلاغ",
        "هذا المحتوى مخالف",
        "القناة تنشر معلومات شخصية خاصة بالمواطنين دون موافقتهم",
        "تم رصد نشر أرقام هواتف وعناوين سكنية مما يشكل انتهاكاً للخصوصية",
        "المحتوى يحتوي على مواد إباحية صريحة تخالف معايير المجتمع",
        "spam 123",
        "اختبار البوت"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. اختبار: '{message}'")
        
        is_valid, result_message, details = smart_reporter.validate_report_message(message)
        
        if is_valid:
            print(f"   ✅ {result_message}")
            if "quality_score" in details:
                print(f"   📊 جودة البلاغ: {details['quality_score']:.2f}/1.00")
        else:
            print(f"   ❌ {result_message}")
            if "quality_score" in details:
                print(f"   📊 جودة البلاغ: {details['quality_score']:.2f}/1.00")
        
        if "suggestions" in details and details["suggestions"]:
            print(f"   💡 اقتراحات:")
            for suggestion in details["suggestions"]:
                print(f"      • {suggestion}")

async def main():
    """الدالة الرئيسية"""
    
    print("🤖 أداة التحليل الذكي - KEVIN BOT")
    print("=" * 50)
    
    while True:
        print("\n📋 الخيارات المتاحة:")
        print("1. تحليل قناة ذكي")
        print("2. اختبار جودة رسائل البلاغ")
        print("3. عرض قوالب البلاغات الذكية")
        print("4. الخروج")
        
        choice = input("\n🔢 اختر (1-4): ").strip()
        
        if choice == "1":
            await analyze_channel_interface()
        elif choice == "2":
            await test_report_message()
        elif choice == "3":
            show_smart_templates()
        elif choice == "4":
            print("👋 وداعاً!")
            break
        else:
            print("❌ اختيار غير صحيح")

async def analyze_channel_interface():
    """واجهة تحليل القناة"""
    
    print("\n🔍 تحليل قناة ذكي")
    print("-" * 30)
    
    session_string = input("أدخل session string: ").strip()
    if not session_string:
        print("❌ لم يتم إدخال session string")
        return
    
    channel = input("أدخل القناة (مثل @oizzi): ").strip()
    if not channel:
        channel = "@oizzi"
    
    try:
        limit = int(input("عدد الرسائل للتحليل (افتراضي 50): ").strip() or "50")
    except ValueError:
        limit = 50
    
    await analyze_channel_smart(session_string, channel, limit)

def show_smart_templates():
    """عرض قوالب البلاغات الذكية"""
    
    print("\n📝 قوالب البلاغات الذكية")
    print("=" * 50)
    
    templates = {
        "🧷 نشر معلومات شخصية": [
            "تم رصد نشر معلومات شخصية حساسة في هذه القناة تشمل أرقام هواتف وعناوين سكنية مما يشكل انتهاكاً صريحاً لخصوصية الأفراد",
            "القناة تنشر بيانات شخصية خاصة بالمواطنين دون موافقتهم مما يعرضهم لمخاطر أمنية وانتهاك للخصوصية"
        ],
        
        "🔞 محتوى جنسي": [
            "المحتوى المنشور يحتوي على مواد إباحية صريحة وغير مناسبة للجمهور العام مما يخالف معايير المجتمع",
            "تم رصد نشر محتوى جنسي فاضح وصور غير لائقة تنتهك قوانين النشر والآداب العامة"
        ],
        
        "💣 عنف وتهديد": [
            "المحتوى يحتوي على تهديدات مباشرة وتحريض على العنف مما يشكل خطراً على الأمن العام",
            "تم رصد نشر محتوى يروج للعنف والإرهاب ويحتوي على تهديدات صريحة للأفراد والمجتمع"
        ],
        
        "💰 احتيال ونصب": [
            "تم رصد أنشطة احتيالية ونصب مالي من خلال عروض وهمية للاستثمار والربح السريع",
            "القناة تروج لمخططات احتيالية وعمليات نصب مالي تستهدف المواطنين بعروض كاذبة"
        ]
    }
    
    for category, template_list in templates.items():
        print(f"\n{category}:")
        for i, template in enumerate(template_list, 1):
            print(f"   {i}. {template}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")