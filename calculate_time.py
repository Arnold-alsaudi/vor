#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حاسبة الوقت للبلاغات الكبيرة
"""

def format_time_display(seconds: float) -> str:
    """تنسيق عرض الوقت بشكل مفهوم"""
    if seconds < 60:
        return f"{seconds:.1f} ثانية"
    elif seconds < 3600:  # أقل من ساعة
        minutes = seconds / 60
        return f"{minutes:.1f} دقيقة"
    elif seconds < 86400:  # أقل من يوم
        hours = seconds / 3600
        return f"{hours:.1f} ساعة"
    else:  # أيام
        days = seconds / 86400
        return f"{days:.1f} يوم"

def calculate_report_time(report_count: int, delay_seconds: float) -> dict:
    """حساب الوقت المطلوب للبلاغات"""
    
    total_seconds = report_count * delay_seconds
    
    # تفصيل الوقت
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    return {
        "total_seconds": total_seconds,
        "display": format_time_display(total_seconds),
        "breakdown": {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }
    }

def main():
    """الدالة الرئيسية"""
    
    print("⏱️ حاسبة الوقت للبلاغات الكبيرة")
    print("=" * 40)
    
    # أمثلة شائعة
    examples = [
        {"count": 100, "delay": 1, "desc": "سريع جداً"},
        {"count": 100, "delay": 5, "desc": "سريع"},
        {"count": 100, "delay": 30, "desc": "آمن"},
        {"count": 500, "delay": 1, "desc": "سريع جداً"},
        {"count": 500, "delay": 5, "desc": "سريع"},
        {"count": 500, "delay": 30, "desc": "آمن"},
        {"count": 1000, "delay": 1, "desc": "سريع جداً"},
        {"count": 1000, "delay": 5, "desc": "سريع"},
        {"count": 1000, "delay": 30, "desc": "آمن"},
        {"count": 2000, "delay": 1, "desc": "سريع جداً"},
        {"count": 2000, "delay": 5, "desc": "سريع"},
        {"count": 2000, "delay": 30, "desc": "آمن"},
    ]
    
    print("📊 أمثلة شائعة:")
    print("-" * 60)
    print(f"{'البلاغات':<8} {'الوقت':<12} {'النوع':<12} {'الوقت المطلوب'}")
    print("-" * 60)
    
    for example in examples:
        time_info = calculate_report_time(example["count"], example["delay"])
        delay_str = f"{example['delay']}ث"
        print(f"{example['count']:<8} {delay_str:<12} {example['desc']:<12} {time_info['display']}")
    
    print("\n" + "=" * 40)
    
    # حاسبة تفاعلية
    print("🧮 حاسبة تفاعلية:")
    
    while True:
        try:
            print("\n" + "-" * 30)
            
            count_input = input("عدد البلاغات (أو 'exit' للخروج): ").strip()
            if count_input.lower() == 'exit':
                break
            
            count = int(count_input)
            if count <= 0:
                print("❌ العدد يجب أن يكون أكبر من صفر")
                continue
            
            delay_input = input("الوقت بين البلاغات (ثانية): ").strip()
            delay = float(delay_input)
            if delay <= 0:
                print("❌ الوقت يجب أن يكون أكبر من صفر")
                continue
            
            # حساب الوقت
            time_info = calculate_report_time(count, delay)
            
            print(f"\n📊 النتائج:")
            print(f"• عدد البلاغات: {count:,}")
            print(f"• الوقت بين البلاغات: {delay} ثانية")
            print(f"• الوقت الإجمالي: {time_info['display']}")
            
            if time_info["breakdown"]["days"] > 0:
                breakdown = time_info["breakdown"]
                print(f"• التفصيل: {breakdown['days']} يوم، {breakdown['hours']} ساعة، {breakdown['minutes']} دقيقة")
            
            # نصائح
            if time_info["total_seconds"] < 300:  # أقل من 5 دقائق
                print("💡 نصيحة: وقت قصير - مناسب للاختبار")
            elif time_info["total_seconds"] < 3600:  # أقل من ساعة
                print("💡 نصيحة: وقت متوسط - مناسب للاستخدام العادي")
            elif time_info["total_seconds"] < 86400:  # أقل من يوم
                print("💡 نصيحة: وقت طويل - تأكد من استقرار الاتصال")
            else:
                print("⚠️ تحذير: وقت طويل جداً - قد تحتاج لتقسيم البلاغات")
            
            # اقتراحات بديلة
            if delay >= 30:
                faster_time = calculate_report_time(count, 5)
                print(f"🚀 للسرعة: استخدم 5 ثواني = {faster_time['display']}")
            
            if delay <= 5:
                safer_time = calculate_report_time(count, 30)
                print(f"🛡️ للأمان: استخدم 30 ثانية = {safer_time['display']}")
        
        except ValueError:
            print("❌ أدخل أرقام صحيحة فقط")
        except KeyboardInterrupt:
            print("\n👋 تم إنهاء البرنامج")
            break

if __name__ == "__main__":
    main()