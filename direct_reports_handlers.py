#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالجات البلاغات المباشرة - KEVIN BOT
"""

import asyncio
from telethon import Button
from message_reporter import message_reporter

class DirectReportsHandlers:
    """معالجات البلاغات المباشرة"""
    
    def __init__(self, bot, session_manager):
        self.bot = bot
        self.session_manager = session_manager
        self.bot_state = {}  # ✅ هذا السطر مهم جداً لتفادي الخطأ

    async def start_direct_reports_input(self, event):
        """بدء إدخال روابط الرسائل"""
        user_id = event.sender_id
        self.bot_state.update_user_state(user_id, step="waiting_message_links")
        
        text = """
📝 **أدخل روابط الرسائل المخالفة**

ألصق روابط الرسائل هنا (كل رابط في سطر منفصل):

**الأشكال المدعومة:**
• `https://t.me/channel_name/123`
• `https://telegram.me/channel_name/123`
• `t.me/channel_name/123`
• `telegram.me/channel_name/123`
• `@channel_name/123`

**مثال:**
```
https://t.me/spam_channel/100
https://t.me/spam_channel/101
t.me/another_channel/50
@bad_channel/200
```

📊 **الحد الأقصى:** 200 رابط في الرسالة الواحدة
⚡ **نصيحة:** كلما زاد عدد الروابط، كان التأثير أقوى
        """
        
        buttons = [
            [Button.inline("❌ إلغاء", "direct_message_reports")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_message_links_input(self, event):
        """معالجة إدخال روابط الرسائل"""
        user_id = event.sender_id
        links_text = event.text.strip()
        
        if not links_text:
            await event.respond("❌ لم يتم إدخال أي روابط. حاول مرة أخرى:")
            return
        
        # استخراج الروابط
        extracted_links = message_reporter.extract_message_links(links_text)
        
        if not extracted_links:
            await event.respond("❌ لم يتم العثور على روابط صحيحة. تأكد من تنسيق الروابط وحاول مرة أخرى:")
            return
        
        # التحقق من صحة الروابط
        valid_links, errors = message_reporter.validate_message_links(extracted_links)
        
        if not valid_links:
            error_text = "❌ جميع الروابط غير صحيحة:\n\n"
            error_text += "\n".join(errors[:5])  # أول 5 أخطاء
            await event.respond(error_text)
            return
        
        # تجميع الروابط حسب القناة
        grouped_links = message_reporter.group_links_by_channel(valid_links)
        
        # حفظ البيانات
        self.bot_state.update_user_state(user_id, 
                                    message_links=valid_links,
                                    grouped_links=grouped_links,
                                    step="choose_report_type")
        
        # عرض ملخص الروابط
        text = f"""
✅ **تم استخراج الروابط بنجاح**

📊 **الإحصائيات:**
• إجمالي الروابط: {len(valid_links)}
• عدد القنوات: {len(grouped_links)}

📡 **القنوات المكتشفة:**
"""
        
        for channel, channel_links in list(grouped_links.items())[:10]:  # أول 10 قنوات
            text += f"• @{channel}: {len(channel_links)} رسالة\n"
        
        if len(grouped_links) > 10:
            text += f"• ... و {len(grouped_links) - 10} قناة أخرى\n"
        
        if errors:
            text += f"\n⚠️ **تم تجاهل {len(errors)} رابط غير صحيح**"
        
        text += "\n\nالآن اختر نوع المخالفة:"
        
        buttons = [
            [Button.inline("😤 I don't like it", "direct_report_type_i_dont_like_it")],
            [Button.inline("👶 Child abuse", "direct_report_type_child_abuse")],
            [Button.inline("💣 Violence", "direct_report_type_violence")],
            [Button.inline("🚫 Illegal goods", "direct_report_type_illegal_goods")],
            [Button.inline("🔞 Illegal adult content", "direct_report_type_illegal_adult_content")],
            [Button.inline("🔒 Personal data", "direct_report_type_personal_data")],
            [Button.inline("💥 Terrorism", "direct_report_type_terrorism")],
            [Button.inline("📧 Scam or spam", "direct_report_type_scam_spam")],
            [Button.inline("©️ Copyright", "direct_report_type_copyright")],
            [Button.inline("⚠️ Other", "direct_report_type_other")],
            [Button.inline("⚖️ Not illegal, but takedown", "direct_report_type_not_illegal_takedown")],
            [Button.inline("🔙 رجوع", "start_direct_reports")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def set_direct_report_type(self, event, report_type: str):
        """تحديد نوع البلاغ المباشر"""
        user_id = event.sender_id
        user_state = self.bot_state.get_user_state(user_id)
        
        if not user_state.get("message_links"):
            await event.respond("❌ لا توجد روابط محفوظة. ابدأ من جديد.")
            return
        
        self.bot_state.update_user_state(user_id, 
                                    direct_report_type=report_type,
                                    step="waiting_report_count")
        
        report_name = message_reporter.report_type_names.get(report_type, "غير محدد")
        
        report_description = message_reporter.report_descriptions.get(report_type, "مخالفة عامة")
        
        text = f"""
🔢 **تحديد عدد البلاغات**

🎯 **نوع المخالفة:** {report_name}
📝 **الوصف:** {report_description}

أدخل عدد البلاغات المطلوب إرسالها:

**الحد الأدنى:** 1 بلاغ
**الحد الأقصى:** 10,000 بلاغ
**الموصى به:** 100-500 بلاغ

💡 **ملاحظة:** سيتم توزيع البلاغات على جميع الرسائل والجلسات المتاحة

أرسل العدد:
        """
        
        buttons = [
            [Button.inline("🔙 تغيير نوع المخالفة", "process_message_links")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_report_count_input(self, event):
        """معالجة إدخال عدد البلاغات"""
        user_id = event.sender_id
        
        try:
            report_count = int(event.text.strip())
            
            if report_count < 1:
                await event.respond("❌ العدد يجب أن يكون أكبر من 0")
                return
            
            if report_count > 10000:
                await event.respond("❌ العدد يجب أن يكون أقل من 10,000")
                return
            
            self.bot_state.update_user_state(user_id, 
                                        report_count=report_count,
                                        step="waiting_direct_reason")
            
            text = f"""
📝 **اكتب سبب البلاغ**

🔢 **عدد البلاغات المختار:** {report_count:,}

اكتب وصفاً مختصراً للمخالفة (اختياري):

**أمثلة:**
• "نشر معلومات شخصية"
• "محتوى إباحي صريح"
• "تهديدات وعنف"
• "احتيال مالي"

📝 **الحد الأقصى:** 200 حرف
⚡ **نصيحة:** اتركه فارغاً للاستخدام السريع

أرسل السبب أو اضغط "تخطي":
            """
            
            buttons = [
                [Button.inline("⏭️ تخطي (بدون سبب)", "start_direct_reporting")],
                [Button.inline("🔙 تغيير العدد", "waiting_report_count")]
            ]
            
            await event.respond(text, buttons=buttons)
            
        except ValueError:
            await event.respond("❌ يرجى إدخال رقم صحيح")
    
    async def process_direct_reason_input(self, event):
        """معالجة إدخال سبب البلاغ المباشر"""
        user_id = event.sender_id
        reason = event.text.strip()[:200]  # حد أقصى 200 حرف
        
        self.bot_state.update_user_state(user_id, direct_reason=reason)
        await self.show_direct_reporting_summary(event)
    
    async def show_direct_reporting_summary(self, event):
        """عرض ملخص البلاغات المباشرة قبل البدء"""
        user_id = event.sender_id
        user_state = self.bot_state.get_user_state(user_id)
        
        message_links = user_state.get("message_links", [])
        grouped_links = user_state.get("grouped_links", {})
        report_type = user_state.get("direct_report_type", "other")
        report_count = user_state.get("report_count", 100)
        reason = user_state.get("direct_reason", "")
        
        # حساب الوقت المتوقع (3 ثواني بين كل بلاغ)
        total_time_seconds = report_count * 3
        hours = total_time_seconds // 3600
        minutes = (total_time_seconds % 3600) // 60
        
        time_text = ""
        if hours > 0:
            time_text = f"{hours} ساعة و {minutes} دقيقة"
        else:
            time_text = f"{minutes} دقيقة"
        
        report_name = message_reporter.report_type_names.get(report_type, "غير محدد")
        
        # حساب توزيع البلاغات
        reports_per_message = report_count // len(message_links) if len(message_links) > 0 else 0
        remaining_reports = report_count % len(message_links)
        
        text = f"""
🎯 **ملخص البلاغات المباشرة**

📊 **الإحصائيات:**
• إجمالي الرسائل: {len(message_links)}
• عدد القنوات: {len(grouped_links)}
• إجمالي البلاغات: {report_count:,}
• البلاغات لكل رسالة: {reports_per_message} + {remaining_reports} إضافي
• نوع المخالفة: {report_name}
• سبب البلاغ: {reason if reason else "بدون سبب محدد"}

⏱️ **التوقيت:**
• التأخير: 3 ثواني بين كل بلاغ
• الوقت المتوقع: {time_text}

🔥 **القوة المتوقعة:**
• بلاغات مباشرة على رسائل محددة
• استخدام جميع الجلسات النشطة
• تأثير أقوى من البلاغات العادية

هل تريد البدء؟
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات المباشرة", "start_direct_reporting")],
            [Button.inline("⚙️ تعديل الإعدادات", "direct_message_reports")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def start_direct_message_reporting(self, event):
        """بدء البلاغات المباشرة"""
        user_id = event.sender_id
        user_state = self.bot_state.get_user_state(user_id)
        
        message_links = user_state.get("message_links", [])
        report_type = user_state.get("direct_report_type", "other")
        report_count = user_state.get("report_count", 100)
        reason = user_state.get("direct_reason", "")
        
        if not message_links:
            await event.respond("❌ لا توجد روابط للإبلاغ عليها")
            return
        
        # التحقق من وجود جلسات نشطة
        sessions_data = self.session_manager.get_all_sessions()
        active_sessions = {
            sid: sdata for sid, sdata in sessions_data.items() 
            if sdata.get('status') == 'active'
        }
        
        if not active_sessions:
            await event.respond("❌ لا توجد جلسات نشطة. أضف جلسات أولاً.")
            return
        
        # بدء البلاغات
        start_message = await event.respond(f"🚀 بدء {report_count:,} بلاغ مباشر على {len(message_links)} رسالة...")
        
        # دالة تحديث التقدم
        async def progress_callback(progress, current, total):
            progress_text = f"""
🎯 **البلاغات المباشرة قيد التنفيذ**

📊 **التقدم:** {current}/{total} ({progress:.1f}%)
🔄 **الحالة:** جاري الإبلاغ على الرسائل...

⏱️ **الوقت المتبقي:** {((total - current) * 3) // 60} دقيقة تقريباً
            """
            
            try:
                await start_message.edit(progress_text)
            except:
                pass
        
        try:
            # تنفيذ البلاغات
            results = await message_reporter.report_multiple_messages(
                sessions_data=active_sessions,
                links=message_links,
                report_type=report_type,
                reason=reason,
                report_count=report_count,
                delay=3,
                progress_callback=progress_callback
            )
            
            # عرض النتائج
            success_rate = (results['successful_reports'] / max(results['total_attempts'], 1)) * 100
            
            result_text = f"""
✅ **تم الانتهاء من البلاغات المباشرة**

📊 **النتائج العامة:**
• إجمالي الرسائل: {results['total_messages']}
• البلاغات المطلوبة: {results['requested_reports']:,}
• المحاولات: {results['total_attempts']:,}
• البلاغات الناجحة: {results['successful_reports']:,}
• البلاغات الفاشلة: {results['failed_reports']:,}
• معدل النجاح: {success_rate:.1f}%

🎯 **نوع المخالفة:** {message_reporter.report_type_names.get(report_type, 'غير محدد')}
            """
            
            # إضافة تفاصيل البلاغات لكل رسالة
            if results.get('message_results'):
                result_text += "\n\n📋 **تفاصيل الرسائل:**\n"
                for i, msg_result in enumerate(results['message_results'][:5], 1):
                    result_text += f"• الرسالة {i}: {msg_result['successful']}/{msg_result['total']} بلاغ\n"
                
                if len(results['message_results']) > 5:
                    result_text += f"• ... و {len(results['message_results']) - 5} رسالة أخرى\n"
            
            buttons = [
                [Button.inline("📊 تفاصيل أكثر", "show_detailed_results")],
                [Button.inline("🔄 بلاغات جديدة", "direct_message_reports")],
                [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
            ]
            
            await start_message.edit(result_text, buttons=buttons)
            
        except Exception as e:
            error_text = f"""
❌ **حدث خطأ أثناء البلاغات**

🔍 **تفاصيل الخطأ:**
{str(e)[:200]}

💡 **الحلول المقترحة:**
• تحقق من اتصال الإنترنت
• تأكد من صحة الجلسات
• جرب تقليل عدد البلاغات
            """
            
            buttons = [
                [Button.inline("🔄 إعادة المحاولة", "start_direct_reporting")],
                [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
            ]
            
            await start_message.edit(error_text, buttons=buttons)