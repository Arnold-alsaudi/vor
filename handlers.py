# KEVIN BOT - معالجات الأوامر والرسائل
# وحدة التعامل مع أوامر المستخدم وواجهة البوت

import asyncio
import re
from typing import Dict, List, Optional
from telethon import TelegramClient, events, Button
from telethon.tl.types import User
import config
from reporter import reporter, ReportType
from user_manager import user_manager
from smart_reporter import smart_reporter
from saved_reports_manager import saved_reports_manager
from message_reporter import message_reporter
from direct_reports_handlers import DirectReportsHandlers

class BotState:
    """حالة البوت لكل مستخدم"""
    
    def __init__(self):
        self.user_states: Dict[int, Dict] = {}
    
    def get_user_state(self, user_id: int) -> Dict:
        """الحصول على حالة المستخدم"""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                "step": "start",
                "target_channel": None,
                "report_type": None,
                "report_message": None,
                "report_count": None,
                "delay_between_reports": config.DEFAULT_DELAY_BETWEEN_REPORTS
            }
        return self.user_states[user_id]
    
    def update_user_state(self, user_id: int, **kwargs):
        """تحديث حالة المستخدم"""
        state = self.get_user_state(user_id)
        state.update(kwargs)
    
    def reset_user_state(self, user_id: int):
        """إعادة تعيين حالة المستخدم"""
        if user_id in self.user_states:
            del self.user_states[user_id]

# إنشاء مثيل حالة البوت
bot_state = BotState()

class BotHandlers:
    """معالجات أوامر البوت"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.session_manager = None  # سيتم تعيينه لاحقاً
        self.direct_reports_handler = None  # سيتم تعيينه بعد تعيين session_manager
        self.setup_handlers()
    
    def set_session_manager(self, session_manager):
        """تعيين مدير الجلسات"""
        self.session_manager = session_manager
        # إنشاء معالج البلاغات المباشرة بعد تعيين session_manager
        self.direct_reports_handler = DirectReportsHandlers(self, session_manager)
    
    def setup_handlers(self):
        """إعداد معالجات الأحداث"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.handle_start(event)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await self.handle_help(event)
        
        @self.client.on(events.NewMessage(pattern='/stats'))
        async def stats_handler(event):
            await self.handle_stats(event)
        
        @self.client.on(events.NewMessage(pattern='/reset'))
        async def reset_handler(event):
            await self.handle_reset(event)
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.handle_callback(event)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            await self.handle_message(event)
    
    async def check_authorization(self, event) -> bool:
        """التحقق من صلاحية المستخدم"""
        user_id = event.sender_id
        
        if not user_manager.is_authorized(user_id):
            await event.respond(config.UNAUTHORIZED_MESSAGE)
            return False
        
        # تحديث آخر نشاط
        user_manager.update_user_activity(user_id)
        return True
    
    async def handle_start(self, event):
        """معالج أمر البدء"""
        if not await self.check_authorization(event):
            return
        
        user_id = event.sender_id
        bot_state.reset_user_state(user_id)
        
        # إنشاء لوحة المفاتيح الرئيسية
        buttons = [
            [Button.inline("📡 تحديد القناة المستهدفة", "set_target_channel")],
            [Button.inline("🧠 التحليل الذكي للقناة", "smart_analysis")],
            [Button.inline("🎯 البلاغات المباشرة", "direct_message_reports")],
            [Button.inline("💾 البلاغات المحفوظة", "saved_reports")],
            [Button.inline("👤 إضافة حساب جديد", "add_session")],
            [Button.inline("📊 لوحة التحكم", "dashboard")],
            [Button.inline("ℹ️ المساعدة", "help")]
        ]
        
        # إضافة أزرار إدارة المستخدمين للمالك والمشرفين
        if user_manager.can_add_users(user_id):
            buttons.append([Button.inline("👥 إدارة المستخدمين", "manage_users")])
        
        await event.respond(
            config.WELCOME_MESSAGE,
            buttons=buttons
        )
    
    async def handle_help(self, event):
        """معالج أمر المساعدة"""
        if not await self.check_authorization(event):
            return
        
        help_text = """
🤖 **دليل استخدام KEVIN BOT**

**الأوامر الأساسية:**
• `/start` - بدء البوت وعرض القائمة الرئيسية
• `/help` - عرض هذه المساعدة
• `/stats` - عرض إحصائيات البوت
• `/reset` - إعادة تعيين حالة البوت

**خطوات الاستخدام:**
1️⃣ اضغط على "📡 تحديد القناة المستهدفة"
2️⃣ أدخل رابط أو يوزر القناة (مثال: @spam_channel)
3️⃣ اختر نوع البلاغ المناسب
4️⃣ اكتب رسالة البلاغ
5️⃣ حدد عدد البلاغات والوقت بينها
6️⃣ ابدأ تنفيذ البلاغات

**إضافة حسابات:**
• اضغط على "👤 إضافة حساب جديد"
• أرسل session string للحساب
• سيتم حفظ الحساب تلقائياً

⚠️ **تحذير مهم:**
استخدم البوت فقط ضد القنوات التي تنتهك قوانين تليجرام بوضوح
        """
        
        await event.respond(help_text)
    
    async def handle_stats(self, event):
        """معالج عرض الإحصائيات"""
        if not await self.check_authorization(event):
            return
        
        stats = reporter.get_stats()
        
        stats_text = f"""
📊 **إحصائيات KEVIN BOT**

👥 **الحسابات:**
• الحسابات النشطة: {stats['active_sessions']}
• إجمالي الحسابات: {stats['total_sessions']}

📈 **البلاغات:**
• إجمالي البلاغات: {stats['total_reports']}
• البلاغات الناجحة: {stats['successful_reports']}
• البلاغات الفاشلة: {stats['failed_reports']}

🔄 **معدل النجاح:** {(stats['successful_reports'] / max(stats['total_reports'], 1) * 100):.1f}%
        """
        
        # إضافة تفاصيل الجلسات النشطة
        if stats['session_details']:
            stats_text += "\n\n👤 **تفاصيل الحسابات النشطة:**\n"
            for session in stats['session_details']:
                stats_text += f"• {session['id']}: {session.get('reports_sent', 0)} بلاغ\n"
        
        buttons = [[Button.inline("🔄 تحديث", "refresh_stats")]]
        
        await event.respond(stats_text, buttons=buttons)
    
    async def handle_reset(self, event):
        """معالج إعادة التعيين"""
        if not await self.check_authorization(event):
            return
        
        user_id = event.sender_id
        bot_state.reset_user_state(user_id)
        
        await event.respond("✅ تم إعادة تعيين حالة البوت بنجاح")
        await self.handle_start(event)
    
    async def handle_callback(self, event):
        """معالج أزرار الكيبورد"""
        if not await self.check_authorization(event):
            return
        
        data = event.data.decode('utf-8')
        user_id = event.sender_id
        
        if data == "set_target_channel":
            await self.show_channel_input(event)
        
        elif data == "add_session":
            await self.show_session_input(event)
        
        elif data == "dashboard":
            await self.show_dashboard(event)
        
        elif data == "help":
            await self.handle_help(event)
        
        elif data == "refresh_stats":
            await self.handle_stats(event)
        
        elif data.startswith("report_type_"):
            report_type = data.replace("report_type_", "")
            await self.handle_report_type_selection(event, report_type)
        
        elif data == "start_reporting":
            await self.start_mass_reporting(event)
        
        elif data == "back_to_main":
            await self.handle_start(event)
        
        elif data == "configure_reports":
            await self.show_report_config(event)
        
        # معالجات التحليل الذكي
        elif data == "smart_analysis":
            await self.show_smart_analysis_input(event)
        
        elif data == "start_smart_analysis":
            await self.start_smart_analysis(event)
        
        elif data.startswith("use_smart_report_"):
            report_index = int(data.replace("use_smart_report_", ""))
            await self.use_smart_report(event, report_index)
        
        # معالجات إدارة المستخدمين
        elif data == "manage_users":
            await self.show_user_management(event)
        
        elif data == "add_user":
            await self.show_add_user_input(event)
        
        elif data == "list_users":
            await self.show_users_list(event)
        
        elif data == "user_stats":
            await self.show_user_stats(event)
        
        elif data.startswith("remove_user_"):
            user_to_remove = int(data.replace("remove_user_", ""))
            await self.confirm_remove_user(event, user_to_remove)
        
        elif data.startswith("confirm_remove_"):
            user_to_remove = int(data.replace("confirm_remove_", ""))
            await self.remove_user(event, user_to_remove)
        
        elif data.startswith("change_role_"):
            user_to_change = int(data.replace("change_role_", ""))
            await self.show_role_selection(event, user_to_change)
        
        elif data.startswith("set_role_"):
            parts = data.replace("set_role_", "").split("_")
            user_to_change = int(parts[0])
            new_role = parts[1]
            await self.change_user_role(event, user_to_change, new_role)
        
        elif data == "show_smart_reports":
            await self.show_smart_reports(event)
        
        elif data == "start_auto_reporting":
            await self.start_auto_reporting(event)
        
        elif data == "detailed_analysis":
            await self.show_detailed_analysis(event)
        
        # معالجات البلاغات المحفوظة
        elif data == "saved_reports":
            await self.show_saved_reports(event)
        
        elif data == "save_current_report":
            await self.save_current_report(event)
        
        elif data.startswith("load_saved_"):
            report_id = data.replace("load_saved_", "")
            await self.load_saved_report(event, report_id)
        
        elif data.startswith("delete_saved_"):
            report_id = data.replace("delete_saved_", "")
            await self.confirm_delete_saved_report(event, report_id)
        
        elif data.startswith("confirm_delete_saved_"):
            report_id = data.replace("confirm_delete_saved_", "")
            await self.delete_saved_report(event, report_id)
        
        elif data.startswith("edit_saved_"):
            report_id = data.replace("edit_saved_", "")
            await self.edit_saved_report(event, report_id)
        
        elif data.startswith("edit_message_"):
            report_id = data.replace("edit_message_", "")
            await self.start_edit_message(event, report_id)
        
        elif data.startswith("edit_count_"):
            report_id = data.replace("edit_count_", "")
            await self.start_edit_count(event, report_id)
        
        elif data.startswith("edit_delay_"):
            report_id = data.replace("edit_delay_", "")
            await self.start_edit_delay(event, report_id)
        
        # معالجات البلاغات المباشرة
        elif data == "direct_message_reports":
            await self.show_direct_reports_menu(event)
        
        elif data == "start_direct_reports":
            if self.direct_reports_handler:
                await self.direct_reports_handler.start_direct_reports_input(event)
            else:
                await event.respond("❌ معالج البلاغات المباشرة غير متاح")
        
        elif data.startswith("direct_report_type_"):
            if self.direct_reports_handler:
                report_type = data.replace("direct_report_type_", "")
                await self.direct_reports_handler.set_direct_report_type(event, report_type)
            else:
                await event.respond("❌ معالج البلاغات المباشرة غير متاح")
        
        elif data == "start_direct_reporting":
            if self.direct_reports_handler:
                await self.direct_reports_handler.start_direct_message_reporting(event)
            else:
                await event.respond("❌ معالج البلاغات المباشرة غير متاح")
        
        elif data == "direct_reports_examples":
            await self.show_direct_reports_examples(event)
    
    async def show_channel_input(self, event):
        """عرض واجهة إدخال القناة"""
        user_id = event.sender_id
        bot_state.update_user_state(user_id, step="waiting_channel")
        
        text = """
📡 **تحديد القناة المستهدفة**

أرسل رابط أو يوزر القناة التي تريد الإبلاغ عنها

**أمثلة صحيحة:**
• `@spam_channel`
• `https://t.me/spam_channel`
• `spam_channel`

⚠️ تأكد من أن القناة تنتهك قوانين تليجرام فعلاً
        """
        
        buttons = [[Button.inline("🔙 العودة للقائمة الرئيسية", "back_to_main")]]
        
        await event.edit(text, buttons=buttons)
    
    async def show_session_input(self, event):
        """عرض واجهة إضافة جلسة"""
        user_id = event.sender_id
        bot_state.update_user_state(user_id, step="waiting_session")
        
        text = """
👤 **إضافة حساب جديد**

أرسل session string للحساب الذي تريد إضافته

**كيفية الحصول على session string:**
1. استخدم سكريبت استخراج الجلسة
2. انسخ النص الطويل (session string)
3. أرسله هنا

⚠️ احتفظ بـ session strings في مكان آمن
        """
        
        buttons = [[Button.inline("🔙 العودة للقائمة الرئيسية", "back_to_main")]]
        
        await event.edit(text, buttons=buttons)
    
    async def show_dashboard(self, event):
        """عرض لوحة التحكم"""
        stats = reporter.get_stats()
        user_state = bot_state.get_user_state(event.sender_id)
        
        dashboard_text = f"""
🎛️ **لوحة التحكم - KEVIN BOT**

📊 **الحالة الحالية:**
• الحسابات النشطة: {stats['active_sessions']}
• القناة المستهدفة: {user_state.get('target_channel', 'غير محددة')}
• نوع البلاغ: {self.get_report_type_name(user_state.get('report_type'))}
• عدد البلاغات: {user_state.get('report_count', 'غير محدد')}

📈 **الإحصائيات:**
• إجمالي البلاغات: {stats['total_reports']}
• البلاغات الناجحة: {stats['successful_reports']}
• البلاغات الفاشلة: {stats['failed_reports']}
        """
        
        buttons = [
            [Button.inline("📡 تحديد القناة", "set_target_channel")],
            [Button.inline("⚙️ إعداد البلاغات", "configure_reports")],
            [Button.inline("👤 إضافة حساب", "add_session")],
            [Button.inline("🔄 تحديث", "dashboard")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.edit(dashboard_text, buttons=buttons)
    
    async def show_report_types(self, event):
        """عرض أنواع البلاغات"""
        text = """
⚠️ **اختر نوع البلاغ**

اختر نوع البلاغ المناسب للقناة المستهدفة:
        """
        
        buttons = []
        for report_type, info in ReportType.REPORT_TYPES.items():
            button_text = f"{info['emoji']} {info['name']}"
            buttons.append([Button.inline(button_text, f"report_type_{report_type}")])
        
        buttons.append([Button.inline("🔙 العودة", "back_to_main")])
        
        await event.edit(text, buttons=buttons)
    
    async def handle_report_type_selection(self, event, report_type: str):
        """معالجة اختيار نوع البلاغ"""
        user_id = event.sender_id
        bot_state.update_user_state(user_id, report_type=report_type, step="waiting_message")
        
        report_info = ReportType.REPORT_TYPES.get(report_type, {})
        
        text = f"""
✍️ **كتابة رسالة البلاغ**

تم اختيار: {report_info.get('emoji', '')} **{report_info.get('name', 'غير معروف')}**

اكتب الآن الرسالة التي ستُرسل مع البلاغ:

**أمثلة:**
• "هذه القناة تنشر محتوى مخالف لقوانين تليجرام"
• "القناة تروج للعنف والإرهاب"
• "تنشر معلومات شخصية بدون إذن"

⚠️ اكتب رسالة واضحة ومحددة
        """
        
        buttons = [[Button.inline("🔙 العودة لاختيار النوع", "configure_reports")]]
        
        await event.edit(text, buttons=buttons)
    
    async def show_report_config(self, event):
        """عرض إعدادات البلاغ"""
        user_state = bot_state.get_user_state(event.sender_id)
        
        if not user_state.get('target_channel'):
            await self.show_channel_input(event)
            return
        
        await self.show_report_types(event)
    
    async def handle_message(self, event):
        """معالج الرسائل النصية"""
        if not await self.check_authorization(event):
            return
        
        # تجاهل الأوامر
        if event.text.startswith('/'):
            return
        
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        step = user_state.get('step')
        
        if step == "waiting_channel":
            await self.process_channel_input(event)
        
        elif step == "waiting_session":
            await self.process_session_input(event)
        
        elif step == "waiting_message":
            await self.process_message_input(event)
        
        elif step == "waiting_count":
            await self.process_count_input(event)
        
        elif step == "waiting_delay":
            await self.process_delay_input(event)
        
        # معالجات التحليل الذكي
        elif step == "waiting_analysis_channel":
            await self.process_analysis_channel_input(event)
        
        # معالجات تعديل البلاغات المحفوظة
        elif step == "editing_saved_message":
            await self.process_edit_saved_message(event)
        
        elif step == "editing_saved_count":
            await self.process_edit_saved_count(event)
        
        elif step == "editing_saved_delay":
            await self.process_edit_saved_delay(event)
        
        # معالجات البلاغات المباشرة
        elif step == "waiting_message_links":
            if self.direct_reports_handler:
                await self.direct_reports_handler.process_message_links_input(event)
            else:
                await event.respond("❌ معالج البلاغات المباشرة غير متاح")
        
        elif step == "waiting_direct_reason":
            if self.direct_reports_handler:
                await self.direct_reports_handler.process_direct_reason_input(event)
            else:
                await event.respond("❌ معالج البلاغات المباشرة غير متاح")
        
        # معالجات إدارة المستخدمين
        elif step == "waiting_user_id":
            await self.process_add_user_input(event)
    
    async def process_channel_input(self, event):
        """معالجة إدخال القناة"""
        user_id = event.sender_id
        channel_input = event.text.strip()
        
        # تنظيف رابط القناة
        channel = self.clean_channel_input(channel_input)
        
        if not channel:
            await event.respond("❌ رابط القناة غير صحيح. حاول مرة أخرى.")
            return
        
        bot_state.update_user_state(user_id, target_channel=channel, step="channel_set")
        
        text = f"""
✅ **تم تحديد القناة بنجاح**

القناة المستهدفة: `{channel}`

الآن اختر ما تريد فعله:
        """
        
        buttons = [
            [Button.inline("⚙️ إعداد البلاغات", "configure_reports")],
            [Button.inline("📊 لوحة التحكم", "dashboard")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_session_input(self, event):
        """معالجة إدخال الجلسة"""
        session_string = event.text.strip()
        
        if len(session_string) < 50:  # session string عادة طويل جداً
            await event.respond("❌ session string غير صحيح. تأكد من نسخه كاملاً.")
            return
        
        # إضافة الجلسة
        success, message = reporter.session_manager.add_session(session_string)
        
        await event.respond(message)
        
        if success:
            # العودة للقائمة الرئيسية
            await asyncio.sleep(2)
            await self.handle_start(event)
    
    async def process_message_input(self, event):
        """معالجة إدخال رسالة البلاغ"""
        user_id = event.sender_id
        message = event.text.strip()
        
        # التحقق من صحة البلاغ باستخدام النظام الذكي
        is_valid, validation_message, details = smart_reporter.validate_report_message(message)
        
        if not is_valid:
            await event.respond(f"{validation_message}\n\n💡 **نصائح لكتابة بلاغ فعال:**\n• اكتب على الأقل 30 حرف\n• وضح المخالفة بالتفصيل\n• استخدم كلمات مثل 'ينشر' أو 'يحتوي'\n• اذكر سبب كون المحتوى مخالفاً")
            return
        
        # عرض تقييم جودة البلاغ
        quality_score = details.get("quality_score", 0)
        quality_text = "ممتاز" if quality_score >= 0.8 else "جيد" if quality_score >= 0.6 else "مقبول"
        
        await event.respond(f"✅ {validation_message}\n📊 جودة البلاغ: {quality_text} ({quality_score:.2f}/1.00)")
        
        if details.get("suggestions"):
            suggestions_text = "\n".join([f"• {s}" for s in details["suggestions"]])
            await event.respond(f"💡 **اقتراحات للتحسين:**\n{suggestions_text}")
        
        bot_state.update_user_state(user_id, report_message=message, step="waiting_count")
        
        text = f"""
🔢 **تحديد عدد البلاغات**

تم حفظ رسالة البلاغ: "{message[:50]}..."

أرسل الآن عدد البلاغات التي تريد إرسالها:

📊 **أمثلة:**
• `10` = للاختبار السريع
• `100` = للتأثير المتوسط
• `500` = للتأثير القوي
• `1000` = للتأثير الأقصى
• `2000` = للقنوات الكبيرة

الحد الأقصى: {config.MAX_REPORTS_PER_SESSION} بلاغ

⚠️ **نصائح:**
• ابدأ بعدد صغير للاختبار
• استخدم وقت انتظار مناسب
• كلما زاد العدد، زاد التأثير
        """
        
        await event.respond(text)
    
    async def process_count_input(self, event):
        """معالجة إدخال عدد البلاغات"""
        user_id = event.sender_id
        
        try:
            count = int(event.text.strip())
            if count <= 0 or count > config.MAX_REPORTS_PER_SESSION:
                await event.respond(f"❌ العدد يجب أن يكون بين 1 و {config.MAX_REPORTS_PER_SESSION}")
                return
        except ValueError:
            await event.respond("❌ أدخل رقماً صحيحاً")
            return
        
        bot_state.update_user_state(user_id, report_count=count, step="waiting_delay")
        
        text = f"""
⏱️ **تحديد الوقت بين البلاغات**

عدد البلاغات: {count}

أرسل الوقت بين كل بلاغ والآخر:

📝 **أمثلة:**
• `1` = ثانية واحدة
• `2.5` = ثانيتان ونصف
• `30` = 30 ثانية
• `1.5m` أو `1.5د` = دقيقة ونصف
• `2m` أو `2د` = دقيقتان

الوقت الافتراضي: {config.DEFAULT_DELAY_BETWEEN_REPORTS} ثانية

⚠️ **نصائح:**
• وقت أقل = سرعة أكبر لكن خطر حظر أعلى
• للأمان: استخدم 30 ثانية أو أكثر
• للسرعة: يمكن استخدام 1-5 ثواني
        """
        
        await event.respond(text)
    
    async def process_delay_input(self, event):
        """معالجة إدخال وقت التأخير"""
        user_id = event.sender_id
        input_text = event.text.strip().lower()
        
        try:
            # دعم تنسيقات مختلفة للوقت
            if 's' in input_text or 'ث' in input_text:
                # ثواني
                delay = float(input_text.replace('s', '').replace('ث', '').strip())
            elif 'm' in input_text or 'د' in input_text:
                # دقائق - تحويل لثواني
                minutes = float(input_text.replace('m', '').replace('د', '').strip())
                delay = minutes * 60
            else:
                # رقم عادي (ثواني)
                delay = float(input_text)
            
            # التحقق من الحدود
            if delay < 1 or delay > 600:  # من ثانية واحدة إلى 10 دقائق
                await event.respond("❌ الوقت يجب أن يكون بين 1 ثانية و 10 دقائق")
                return
                
        except ValueError:
            await event.respond("""❌ تنسيق غير صحيح. استخدم:
• `5` = 5 ثواني
• `1.5` = ثانية ونصف
• `30s` أو `30ث` = 30 ثانية
• `2m` أو `2د` = دقيقتان (120 ثانية)""")
            return
        
        bot_state.update_user_state(user_id, delay_between_reports=delay, step="ready_to_report")
        
        user_state = bot_state.get_user_state(user_id)
        
        # تنسيق عرض الوقت
        delay_display = self.format_delay_display(user_state['delay_between_reports'])
        
        # حساب الوقت الإجمالي المتوقع
        total_time_seconds = user_state['report_count'] * user_state['delay_between_reports']
        total_time_display = self.format_delay_display(total_time_seconds)
        
        text = f"""
🚀 **جاهز لبدء البلاغات**

📋 **ملخص الإعدادات:**
• القناة: `{user_state['target_channel']}`
• نوع البلاغ: {self.get_report_type_name(user_state['report_type'])}
• الرسالة: "{user_state['report_message'][:50]}..."
• عدد البلاغات: {user_state['report_count']}
• الوقت بين البلاغات: {delay_display}

⏱️ **الوقت المتوقع للإنجاز:** {total_time_display}

⚠️ **تأكد من صحة المعلومات قبل البدء**
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات", "start_reporting")],
            [Button.inline("📊 لوحة التحكم", "dashboard")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    def format_delay_display(self, delay_seconds: float) -> str:
        """تنسيق عرض الوقت بشكل مفهوم"""
        if delay_seconds < 1:
            return f"{delay_seconds:.1f} ثانية"
        elif delay_seconds < 60:
            if delay_seconds == int(delay_seconds):
                return f"{int(delay_seconds)} ثانية"
            else:
                return f"{delay_seconds:.1f} ثانية"
        else:
            minutes = delay_seconds / 60
            if minutes == int(minutes):
                return f"{int(minutes)} دقيقة"
            else:
                return f"{minutes:.1f} دقيقة"
    
    async def start_mass_reporting(self, event):
        """بدء تنفيذ البلاغات الجماعية"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        
        # التحقق من اكتمال البيانات
        required_fields = ['target_channel', 'report_type', 'report_message', 'report_count']
        for field in required_fields:
            if not user_state.get(field):
                await event.respond(f"❌ البيانات غير مكتملة. يرجى إعادة الإعداد.")
                await self.handle_start(event)
                return
        
        # التحقق من وجود جلسات نشطة
        active_sessions = reporter.session_manager.get_active_sessions()
        if not active_sessions:
            await event.respond("❌ لا توجد حسابات نشطة. أضف حساباً واحداً على الأقل.")
            return
        
        # رسالة البدء
        start_message = await event.respond(f"""
🚀 **بدء تنفيذ البلاغات**

📊 الحسابات النشطة: {len(active_sessions)}
🎯 القناة المستهدفة: `{user_state['target_channel']}`
📝 عدد البلاغات: {user_state['report_count']}

⏳ جاري التنفيذ...
        """)
        
        # دالة تحديث التقدم
        async def progress_callback(current, total, session_id, success, message):
            progress_percent = (current / total) * 100
            status_emoji = "✅" if success else "❌"
            
            progress_text = f"""
🚀 **تقدم البلاغات**

📊 التقدم: {current}/{total} ({progress_percent:.1f}%)
🔄 الجلسة الحالية: {session_id}
{status_emoji} آخر حالة: {message[:50]}...

⏳ يرجى الانتظار...
            """
            
            try:
                await start_message.edit(progress_text)
            except:
                pass  # تجاهل أخطاء التحديث
        
        # تنفيذ البلاغات
        try:
            results = await reporter.execute_mass_report(
                channel_username=user_state['target_channel'],
                report_type=user_state['report_type'],
                message=user_state['report_message'],
                report_count=user_state['report_count'],
                delay_between_reports=user_state['delay_between_reports'],
                progress_callback=progress_callback
            )
            
            # عرض النتائج
            success_rate = (results['successful'] / max(results['total_attempted'], 1)) * 100
            
            result_text = f"""
✅ **تم الانتهاء من البلاغات**

📊 **النتائج:**
• إجمالي المحاولات: {results['total_attempted']}
• البلاغات الناجحة: {results['successful']}
• البلاغات الفاشلة: {results['failed']}
• معدل النجاح: {success_rate:.1f}%

🎯 القناة: `{user_state['target_channel']}`
            """
            
            # إضافة تفاصيل الأخطاء إن وجدت
            if results['errors']:
                result_text += f"\n\n⚠️ **الأخطاء:**\n"
                for error in results['errors'][:3]:  # أول 3 أخطاء فقط
                    result_text += f"• {error}\n"
            
            buttons = [
                [Button.inline("💾 حفظ معلومات البلاغ", "save_current_report")],
                [Button.inline("📊 لوحة التحكم", "dashboard")],
                [Button.inline("🔄 بلاغات جديدة", "back_to_main")]
            ]
            
            await start_message.edit(result_text, buttons=buttons)
            
            # إعادة تعيين حالة المستخدم
            bot_state.reset_user_state(user_id)
            
        except Exception as e:
            error_text = f"""
❌ **خطأ في تنفيذ البلاغات**

الخطأ: {str(e)}

يرجى المحاولة مرة أخرى أو التحقق من الإعدادات.
            """
            
            buttons = [[Button.inline("🔙 القائمة الرئيسية", "back_to_main")]]
            
            await start_message.edit(error_text, buttons=buttons)
    
    def clean_channel_input(self, channel_input: str) -> Optional[str]:
        """تنظيف وتحقق من صحة إدخال القناة"""
        if not channel_input:
            return None
        
        # إزالة المسافات
        channel = channel_input.strip()
        
        # إذا كان رابط كامل
        if channel.startswith('https://t.me/'):
            channel = channel.replace('https://t.me/', '')
        elif channel.startswith('t.me/'):
            channel = channel.replace('t.me/', '')
        
        # إضافة @ إذا لم تكن موجودة
        if not channel.startswith('@'):
            channel = '@' + channel
        
        # التحقق من صحة التنسيق
        if re.match(r'^@[a-zA-Z][a-zA-Z0-9_]{4,31}$', channel):
            return channel
        
        return None
    
    def get_report_type_name(self, report_type: str) -> str:
        """الحصول على اسم نوع البلاغ"""
        if not report_type:
            return "غير محدد"
        
        report_info = ReportType.REPORT_TYPES.get(report_type, {})
        return f"{report_info.get('emoji', '')} {report_info.get('name', 'غير معروف')}"
    
    # ==================== دوال إدارة المستخدمين ====================
    
    async def show_user_management(self, event):
        """عرض لوحة إدارة المستخدمين"""
        user_id = event.sender_id
        
        if not user_manager.can_add_users(user_id):
            await event.respond("❌ ليس لديك صلاحية إدارة المستخدمين")
            return
        
        stats = user_manager.get_stats()
        
        text = f"""
👥 **إدارة المستخدمين**

📊 **الإحصائيات:**
• إجمالي المستخدمين: {stats['total_users']}
• المستخدمين النشطين: {stats['active_users']}
• إجمالي البلاغات: {stats['total_reports']:,}

👑 **الأدوار:**
"""
        
        for role, count in stats['roles_count'].items():
            role_name = {"owner": "مالك", "admin": "مشرف", "moderator": "مراقب", "user": "مستخدم"}.get(role, role)
            text += f"• {role_name}: {count}\n"
        
        buttons = [
            [Button.inline("➕ إضافة مستخدم", "add_user")],
            [Button.inline("📋 قائمة المستخدمين", "list_users")],
            [Button.inline("📊 إحصائيات المستخدمين", "user_stats")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def show_add_user_input(self, event):
        """عرض واجهة إضافة مستخدم"""
        user_id = event.sender_id
        
        if not user_manager.can_add_users(user_id):
            await event.respond("❌ ليس لديك صلاحية إضافة مستخدمين")
            return
        
        bot_state.update_user_state(user_id, step="waiting_user_id")
        
        text = """
➕ **إضافة مستخدم جديد**

أرسل معرف المستخدم (User ID) الذي تريد إضافته:

**كيفية الحصول على معرف المستخدم:**
1. استخدم بوت @userinfobot
2. أرسل له رسالة أو forward من المستخدم
3. سيعطيك User ID

**مثال:** `123456789`
        """
        
        buttons = [
            [Button.inline("🔙 إلغاء", "manage_users")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_add_user_input(self, event):
        """معالجة إدخال معرف المستخدم"""
        user_id = event.sender_id
        input_text = event.text.strip()
        
        try:
            new_user_id = int(input_text)
            
            # محاولة الحصول على معلومات المستخدم
            try:
                user_entity = await self.client.get_entity(new_user_id)
                username = user_entity.first_name or "مجهول"
                if user_entity.username:
                    username += f" (@{user_entity.username})"
            except:
                username = f"مستخدم {new_user_id}"
            
            # إضافة المستخدم بدور افتراضي
            success, message = user_manager.add_user(new_user_id, username, user_id, "user")
            
            await event.respond(message)
            
            if success:
                # عرض خيارات تحديد الدور
                buttons = [
                    [Button.inline("👤 مستخدم عادي", f"set_role_{new_user_id}_user")],
                    [Button.inline("👮 مراقب", f"set_role_{new_user_id}_moderator")],
                    [Button.inline("👑 مشرف", f"set_role_{new_user_id}_admin")],
                    [Button.inline("✅ إبقاء كمستخدم عادي", "manage_users")]
                ]
                
                await event.respond(
                    f"🎯 **تحديد دور المستخدم {username}**\n\nاختر الدور المناسب:",
                    buttons=buttons
                )
            else:
                await asyncio.sleep(2)
                await self.show_user_management(event)
        
        except ValueError:
            await event.respond("❌ معرف المستخدم يجب أن يكون رقماً صحيحاً")
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
    
    async def show_users_list(self, event):
        """عرض قائمة المستخدمين"""
        user_id = event.sender_id
        
        if not user_manager.can_add_users(user_id):
            await event.respond("❌ ليس لديك صلاحية عرض المستخدمين")
            return
        
        users = user_manager.get_all_users()
        
        if not users:
            await event.respond("📭 لا يوجد مستخدمين مسجلين")
            return
        
        text = "📋 **قائمة المستخدمين:**\n\n"
        
        for user in users:
            role_emoji = {"owner": "👑", "admin": "👑", "moderator": "👮", "user": "👤"}.get(user['role'], "👤")
            status_emoji = "🟢" if user['status'] == "active" else "🔴"
            
            text += f"{role_emoji} **{user['username']}**\n"
            text += f"   • ID: `{user['user_id']}`\n"
            text += f"   • الدور: {user['role']}\n"
            text += f"   • الحالة: {status_emoji}\n"
            text += f"   • البلاغات: {user['reports_sent']:,}\n\n"
        
        buttons = []
        
        # إضافة أزرار الإدارة للمشرفين
        if user_manager.can_remove_users(user_id):
            for user in users[:5]:  # أول 5 مستخدمين فقط لتجنب تجاوز حد الأزرار
                if user['user_id'] != user_manager.users_data.get("owner_id"):
                    buttons.append([
                        Button.inline(f"🗑️ حذف {user['username'][:15]}", f"remove_user_{user['user_id']}"),
                        Button.inline(f"⚙️ تغيير دور", f"change_role_{user['user_id']}")
                    ])
        
        buttons.append([Button.inline("🔙 إدارة المستخدمين", "manage_users")])
        
        await event.respond(text, buttons=buttons)
    
    async def show_user_stats(self, event):
        """عرض إحصائيات المستخدمين التفصيلية"""
        user_id = event.sender_id
        
        if not user_manager.can_add_users(user_id):
            await event.respond("❌ ليس لديك صلاحية عرض الإحصائيات")
            return
        
        users = user_manager.get_all_users()
        stats = user_manager.get_stats()
        
        # ترتيب المستخدمين حسب عدد البلاغات
        users_sorted = sorted(users, key=lambda x: x.get('reports_sent', 0), reverse=True)
        
        text = f"""
📊 **إحصائيات المستخدمين التفصيلية**

📈 **الإحصائيات العامة:**
• إجمالي المستخدمين: {stats['total_users']}
• المستخدمين النشطين: {stats['active_users']}
• إجمالي البلاغات: {stats['total_reports']:,}

🏆 **أكثر المستخدمين نشاطاً:**
"""
        
        for i, user in enumerate(users_sorted[:5], 1):
            role_emoji = {"owner": "👑", "admin": "👑", "moderator": "👮", "user": "👤"}.get(user['role'], "👤")
            text += f"{i}. {role_emoji} {user['username']}: {user['reports_sent']:,} بلاغ\n"
        
        text += f"\n📅 **تاريخ الإنشاء:** {stats.get('created_date', 'غير محدد')[:10]}"
        
        buttons = [
            [Button.inline("🔄 تحديث", "user_stats")],
            [Button.inline("🔙 إدارة المستخدمين", "manage_users")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def confirm_remove_user(self, event, user_to_remove: int):
        """تأكيد حذف المستخدم"""
        user_id = event.sender_id
        
        if not user_manager.can_remove_users(user_id):
            await event.respond("❌ ليس لديك صلاحية حذف المستخدمين")
            return
        
        user_info = user_manager.get_user_info(user_to_remove)
        if not user_info:
            await event.respond("❌ المستخدم غير موجود")
            return
        
        text = f"""
⚠️ **تأكيد حذف المستخدم**

هل أنت متأكد من حذف المستخدم التالي؟

👤 **المستخدم:** {user_info['username']}
🆔 **المعرف:** `{user_info['user_id']}`
👑 **الدور:** {user_info['role']}
📊 **البلاغات:** {user_info['reports_sent']:,}

⚠️ **تحذير:** هذا الإجراء لا يمكن التراجع عنه!
        """
        
        buttons = [
            [Button.inline("✅ نعم، احذف", f"confirm_remove_{user_to_remove}")],
            [Button.inline("❌ إلغاء", "list_users")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def remove_user(self, event, user_to_remove: int):
        """حذف المستخدم"""
        user_id = event.sender_id
        
        success, message = user_manager.remove_user(user_to_remove, user_id)
        await event.respond(message)
        
        await asyncio.sleep(2)
        await self.show_users_list(event)
    
    async def show_role_selection(self, event, user_to_change: int):
        """عرض خيارات تغيير الدور"""
        user_id = event.sender_id
        
        if not user_manager.can_add_users(user_id):
            await event.respond("❌ ليس لديك صلاحية تغيير الأدوار")
            return
        
        user_info = user_manager.get_user_info(user_to_change)
        if not user_info:
            await event.respond("❌ المستخدم غير موجود")
            return
        
        text = f"""
⚙️ **تغيير دور المستخدم**

👤 **المستخدم:** {user_info['username']}
👑 **الدور الحالي:** {user_info['role']}

اختر الدور الجديد:
        """
        
        buttons = [
            [Button.inline("👤 مستخدم عادي", f"set_role_{user_to_change}_user")],
            [Button.inline("👮 مراقب", f"set_role_{user_to_change}_moderator")],
            [Button.inline("👑 مشرف", f"set_role_{user_to_change}_admin")],
            [Button.inline("❌ إلغاء", "list_users")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def change_user_role(self, event, user_to_change: int, new_role: str):
        """تغيير دور المستخدم"""
        user_id = event.sender_id
        
        success, message = user_manager.change_user_role(user_to_change, new_role, user_id)
        await event.respond(message)
        
        await asyncio.sleep(2)
        await self.show_users_list(event)
    
    # ==================== دوال التحليل الذكي ====================
    
    async def show_smart_analysis_input(self, event):
        """عرض واجهة التحليل الذكي"""
        user_id = event.sender_id
        bot_state.update_user_state(user_id, step="waiting_analysis_channel")
        
        text = """
🧠 **التحليل الذكي للقناة**

أرسل رابط أو يوزر القناة التي تريد تحليلها:

**المميزات:**
• 🔍 كشف المحتوى المخالف تلقائياً
• 📊 تحليل مستوى الخطورة
• 📝 إنشاء بلاغات ذكية مخصصة
• 🎯 اقتراح أفضل أنواع البلاغات

**أمثلة صحيحة:**
• `@spam_channel`
• `https://t.me/spam_channel`

⚠️ **ملاحظة:** سيتم تحليل آخر 50 رسالة في القناة
        """
        
        buttons = [
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_analysis_channel_input(self, event):
        """معالجة إدخال قناة التحليل"""
        user_id = event.sender_id
        channel_input = event.text.strip()
        
        # تنظيف رابط القناة
        channel = self.clean_channel_input(channel_input)
        
        if not channel:
            await event.respond("❌ رابط القناة غير صحيح. تأكد من الرابط وحاول مرة أخرى.")
            return
        
        # بدء التحليل
        await event.respond("🔍 جاري التحليل الذكي للقناة... قد يستغرق هذا بعض الوقت")
        
        try:
            # تحليل القناة
            analysis = await smart_reporter.analyze_channel(self.client, channel, 50)
            
            if "error" in analysis:
                await event.respond(f"❌ خطأ في التحليل: {analysis['error']}")
                return
            
            # حفظ نتائج التحليل
            bot_state.update_user_state(user_id, 
                                      analysis_results=analysis, 
                                      target_channel=channel,
                                      step="analysis_complete")
            
            # عرض النتائج
            await self.show_analysis_results(event, analysis)
            
        except Exception as e:
            await event.respond(f"❌ خطأ في التحليل: {str(e)}")
    
    async def show_analysis_results(self, event, analysis: dict):
        """عرض نتائج التحليل"""
        
        channel_info = analysis["channel_info"]
        violations_count = len(analysis["violations_found"])
        
        # إنشاء ملخص النتائج
        text = f"""
🧠 **نتائج التحليل الذكي**

📡 **القناة:** {channel_info['title']}
👥 **المشتركين:** {channel_info['participants_count']:,}
📊 **الرسائل المحللة:** {analysis['messages_analyzed']}

🚨 **المخالفات المكتشفة:** {violations_count}
"""
        
        # إضافة توزيع الخطورة
        severity_dist = analysis["severity_distribution"]
        if any(count > 0 for severity, count in severity_dist.items() if severity != "none"):
            text += "\n⚠️ **مستويات الخطورة:**\n"
            severity_emojis = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}
            for severity, count in severity_dist.items():
                if count > 0 and severity != "none":
                    emoji = severity_emojis.get(severity, "⚪")
                    text += f"{emoji} {severity.upper()}: {count}\n"
        
        # إضافة ملخص المخالفات
        if analysis["violation_summary"]:
            text += "\n🔍 **أنواع المخالفات:**\n"
            violation_names = {
                "personal_info": "🧷 معلومات شخصية",
                "sexual_content": "🔞 محتوى جنسي",
                "violence": "💣 عنف وتهديد",
                "scam": "💰 احتيال ونصب",
                "drugs": "🧪 ترويج مخدرات",
                "fake_accounts": "🎭 انتحال شخصية",
                "child_abuse": "👶 إساءة للأطفال"
            }
            
            for violation_type, count in analysis["violation_summary"].items():
                name = violation_names.get(violation_type, violation_type)
                text += f"{name}: {count}\n"
        
        # إنشاء الأزرار
        buttons = []
        
        if analysis["recommended_reports"]:
            text += f"\n📝 **البلاغات الذكية:** {len(analysis['recommended_reports'])} بلاغ مقترح"
            buttons.append([Button.inline("📝 عرض البلاغات الذكية", "show_smart_reports")])
        
        if violations_count > 0:
            buttons.append([Button.inline("🚀 بدء البلاغات التلقائية", "start_auto_reporting")])
        
        buttons.extend([
            [Button.inline("📊 تفاصيل أكثر", "detailed_analysis")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ])
        
        await event.respond(text, buttons=buttons)
    
    async def show_smart_reports(self, event):
        """عرض البلاغات الذكية المقترحة"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        analysis = user_state.get("analysis_results")
        
        if not analysis or not analysis.get("recommended_reports"):
            await event.respond("❌ لا توجد بلاغات ذكية متاحة")
            return
        
        reports = analysis["recommended_reports"]
        
        text = f"""
📝 **البلاغات الذكية المقترحة**

تم إنشاء {len(reports)} بلاغ ذكي بناءً على التحليل:
"""
        
        buttons = []
        
        for i, report in enumerate(reports[:5], 1):  # أول 5 بلاغات
            violation_names = {
                "personal_info": "🧷 معلومات شخصية",
                "sexual_content": "🔞 محتوى جنسي", 
                "violence": "💣 عنف وتهديد",
                "scam": "💰 احتيال ونصب",
                "drugs": "🧪 ترويج مخدرات",
                "fake_accounts": "🎭 انتحال شخصية",
                "child_abuse": "👶 إساءة للأطفال"
            }
            
            name = violation_names.get(report["violation_type"], report["violation_type"])
            text += f"\n{i}. {name}"
            text += f"\n   📊 الأولوية: {report['priority']}/10"
            text += f"\n   🔍 الأدلة: {report['evidence_count']} حالة"
            text += f"\n   📝 البلاغ: {report['report_message'][:100]}..."
            
            buttons.append([Button.inline(f"استخدام البلاغ {i}", f"use_smart_report_{i-1}")])
        
        buttons.append([Button.inline("🔙 نتائج التحليل", "smart_analysis")])
        
        await event.respond(text, buttons=buttons)
    
    async def use_smart_report(self, event, report_index: int):
        """استخدام بلاغ ذكي"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        analysis = user_state.get("analysis_results")
        
        if not analysis or not analysis.get("recommended_reports"):
            await event.respond("❌ لا توجد بلاغات ذكية متاحة")
            return
        
        reports = analysis["recommended_reports"]
        
        if report_index >= len(reports):
            await event.respond("❌ البلاغ المحدد غير موجود")
            return
        
        selected_report = reports[report_index]
        
        # تحديث حالة المستخدم
        bot_state.update_user_state(user_id,
                                  report_type=selected_report["telegram_report_type"],
                                  report_message=selected_report["report_message"],
                                  step="waiting_count")
        
        text = f"""
✅ **تم اختيار البلاغ الذكي**

📝 **نص البلاغ:**
{selected_report["report_message"]}

📊 **الأولوية:** {selected_report['priority']}/10
🔍 **الأدلة:** {selected_report['evidence_count']} حالة

الآن حدد عدد البلاغات التي تريد إرسالها:

📊 **أمثلة:**
• `100` = للتأثير المتوسط
• `500` = للتأثير القوي  
• `1000` = للتأثير الأقصى

الحد الأقصى: {config.MAX_REPORTS_PER_SESSION} بلاغ
        """
        
        await event.respond(text)
    
    async def start_auto_reporting(self, event):
        """بدء البلاغات التلقائية"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        analysis = user_state.get("analysis_results")
        
        if not analysis or not analysis.get("recommended_reports"):
            await event.respond("❌ لا توجد بلاغات ذكية متاحة")
            return
        
        # استخدام أفضل بلاغ (الأول في القائمة)
        best_report = analysis["recommended_reports"][0]
        
        # تحديث حالة المستخدم
        bot_state.update_user_state(user_id,
                                  report_type=best_report["telegram_report_type"],
                                  report_message=best_report["report_message"],
                                  report_count=500,  # عدد افتراضي
                                  delay_between_reports=5,  # 5 ثواني
                                  step="ready_to_report")
        
        text = f"""
🚀 **البلاغات التلقائية جاهزة**

تم اختيار أفضل بلاغ تلقائياً:

📝 **البلاغ:** {best_report["report_message"][:100]}...
📊 **العدد:** 500 بلاغ
⏱️ **الوقت:** 5 ثواني بين البلاغات
🕐 **المدة المتوقعة:** 41.7 دقيقة

هل تريد البدء؟
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات", "start_reporting")],
            [Button.inline("⚙️ تخصيص الإعدادات", "show_smart_reports")],
            [Button.inline("🔙 نتائج التحليل", "smart_analysis")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def show_detailed_analysis(self, event):
        """عرض تفاصيل التحليل"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        analysis = user_state.get("analysis_results")
        
        if not analysis:
            await event.respond("❌ لا توجد نتائج تحليل متاحة")
            return
        
        violations = analysis.get("violations_found", [])
        
        if not violations:
            await event.respond("✅ لم يتم العثور على مخالفات في هذه القناة")
            return
        
        text = f"""
📊 **تفاصيل المخالفات المكتشفة**

🔍 **أمثلة على المخالفات:**
"""
        
        # عرض أول 3 مخالفات كأمثلة
        for i, violation in enumerate(violations[:3], 1):
            text += f"\n{i}. **رسالة رقم {violation['message_id']}**"
            text += f"\n   📅 {violation['date'][:19] if violation['date'] else 'غير محدد'}"
            text += f"\n   ⚠️ خطورة: {violation['severity'].upper()}"
            text += f"\n   📝 المحتوى: {violation['message_text'][:150]}..."
            
            violation_types = [v['type'] for v in violation['violations']]
            text += f"\n   🚨 المخالفات: {', '.join(set(violation_types))}"
        
        if len(violations) > 3:
            text += f"\n\n... و {len(violations) - 3} مخالفة أخرى"
        
        buttons = [
            [Button.inline("📝 عرض البلاغات الذكية", "show_smart_reports")],
            [Button.inline("🔙 نتائج التحليل", "smart_analysis")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    # ==================== دوال البلاغات المحفوظة ====================
    
    async def show_saved_reports(self, event):
        """عرض البلاغات المحفوظة"""
        user_id = event.sender_id
        saved_reports = saved_reports_manager.get_user_saved_reports(user_id)
        
        if not saved_reports:
            text = """
💾 **البلاغات المحفوظة**

📭 لا توجد بلاغات محفوظة حالياً

💡 **كيفية حفظ البلاغ:**
1. قم بإعداد بلاغ جديد
2. بعد إرسال البلاغات، اضغط "💾 حفظ معلومات البلاغ"
3. ستظهر هنا للاستخدام لاحقاً
            """
            
            buttons = [
                [Button.inline("📡 إنشاء بلاغ جديد", "set_target_channel")],
                [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
            ]
            
            await event.respond(text, buttons=buttons)
            return
        
        text = f"""
💾 **البلاغات المحفوظة**

📊 لديك {len(saved_reports)} بلاغ محفوظ:
"""
        
        buttons = []
        
        for i, report in enumerate(saved_reports[:10], 1):  # أول 10 بلاغات
            channel = report.get("channel", "غير محدد")
            report_type = report.get("report_type", "غير محدد")
            usage_count = report.get("usage_count", 0)
            report_id = report.get("report_id")
            
            # تقصير اسم القناة
            display_channel = channel[:20] + "..." if len(channel) > 20 else channel
            
            text += f"\n{i}. 📡 {display_channel}"
            text += f"\n   📝 {report_type} | 📊 استُخدم {usage_count} مرة"
            
            buttons.append([
                Button.inline(f"🚀 استخدام البلاغ {i}", f"load_saved_{report_id}"),
                Button.inline(f"✏️ تعديل", f"edit_saved_{report_id}"),
                Button.inline(f"🗑️ حذف", f"delete_saved_{report_id}")
            ])
        
        if len(saved_reports) > 10:
            text += f"\n\n... و {len(saved_reports) - 10} بلاغ آخر"
        
        buttons.append([Button.inline("🔙 القائمة الرئيسية", "back_to_main")])
        
        await event.respond(text, buttons=buttons)
    
    async def save_current_report(self, event):
        """حفظ البلاغ الحالي"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        
        # التحقق من وجود بيانات البلاغ
        required_fields = ["target_channel", "report_type", "report_message"]
        missing_fields = [field for field in required_fields if not user_state.get(field)]
        
        if missing_fields:
            await event.respond("❌ لا توجد بيانات بلاغ كاملة للحفظ")
            return
        
        # إعداد بيانات البلاغ للحفظ
        report_data = {
            "channel_info": {
                "title": user_state.get("target_channel", ""),
                "username": user_state.get("target_channel", ""),
            },
            "report_type": user_state.get("report_type"),
            "report_message": user_state.get("report_message"),
            "report_count": user_state.get("report_count", 100),
            "delay_between_reports": user_state.get("delay_between_reports", 5),
            "analysis_results": user_state.get("analysis_results"),
            "smart_reports": user_state.get("smart_reports", [])
        }
        
        # حفظ البلاغ
        success, message, report_id = saved_reports_manager.save_report(
            user_id, 
            user_state.get("target_channel"), 
            report_data
        )
        
        if success:
            text = f"""
✅ **تم حفظ البلاغ بنجاح**

📡 **القناة:** {user_state.get("target_channel")}
🆔 **معرف البلاغ:** `{report_id}`
📝 **نوع البلاغ:** {user_state.get("report_type")}

💡 يمكنك الآن الوصول لهذا البلاغ من "💾 البلاغات المحفوظة"
            """
            
            buttons = [
                [Button.inline("💾 عرض البلاغات المحفوظة", "saved_reports")],
                [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
            ]
        else:
            text = message
            buttons = [
                [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
            ]
        
        await event.respond(text, buttons=buttons)
    
    async def load_saved_report(self, event, report_id: str):
        """تحميل بلاغ محفوظ"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data:
            await event.respond("❌ البلاغ المحفوظ غير موجود")
            return
        
        # التحقق من ملكية البلاغ
        if report_data.get("user_id") != user_id:
            await event.respond("❌ ليس لديك صلاحية الوصول لهذا البلاغ")
            return
        
        # تحديث حالة المستخدم بالبيانات المحفوظة
        bot_state.update_user_state(user_id,
                                  target_channel=report_data.get("channel"),
                                  report_type=report_data.get("report_type"),
                                  report_message=report_data.get("report_message"),
                                  report_count=report_data.get("report_count", 100),
                                  delay_between_reports=report_data.get("delay_between_reports", 5),
                                  analysis_results=report_data.get("analysis_results"),
                                  smart_reports=report_data.get("smart_reports", []),
                                  step="ready_to_report")
        
        # تحديث آخر استخدام
        saved_reports_manager.update_report_usage(report_id)
        
        # عرض ملخص البلاغ
        summary = saved_reports_manager.get_report_summary(report_id)
        
        text = f"""
✅ **تم تحميل البلاغ المحفوظ**

{summary}

🚀 البلاغ جاهز للإرسال الآن!
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات", "start_reporting")],
            [Button.inline("⚙️ تعديل الإعدادات", "configure_reports")],
            [Button.inline("💾 البلاغات المحفوظة", "saved_reports")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def confirm_delete_saved_report(self, event, report_id: str):
        """تأكيد حذف البلاغ المحفوظ"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data:
            await event.respond("❌ البلاغ المحفوظ غير موجود")
            return
        
        # التحقق من ملكية البلاغ
        if report_data.get("user_id") != user_id:
            await event.respond("❌ ليس لديك صلاحية حذف هذا البلاغ")
            return
        
        channel = report_data.get("channel", "غير محدد")
        usage_count = report_data.get("usage_count", 0)
        
        text = f"""
⚠️ **تأكيد حذف البلاغ المحفوظ**

📡 **القناة:** {channel}
📊 **مرات الاستخدام:** {usage_count}

هل أنت متأكد من حذف هذا البلاغ المحفوظ؟

⚠️ **تحذير:** لن تتمكن من استرداد البيانات بعد الحذف!
        """
        
        buttons = [
            [Button.inline("✅ نعم، احذف", f"confirm_delete_saved_{report_id}")],
            [Button.inline("❌ إلغاء", "saved_reports")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def delete_saved_report(self, event, report_id: str):
        """حذف البلاغ المحفوظ"""
        user_id = event.sender_id
        
        success, message = saved_reports_manager.delete_report(report_id, user_id)
        await event.respond(message)
        
        await asyncio.sleep(2)
        await self.show_saved_reports(event)
    
    async def edit_saved_report(self, event, report_id: str):
        """تعديل البلاغ المحفوظ"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data:
            await event.respond("❌ البلاغ المحفوظ غير موجود")
            return
        
        # التحقق من ملكية البلاغ
        if report_data.get("user_id") != user_id:
            await event.respond("❌ ليس لديك صلاحية تعديل هذا البلاغ")
            return
        
        # عرض خيارات التعديل
        summary = saved_reports_manager.get_report_summary(report_id)
        
        text = f"""
✏️ **تعديل البلاغ المحفوظ**

{summary}

اختر ما تريد تعديله:
        """
        
        buttons = [
            [Button.inline("📝 تعديل رسالة البلاغ", f"edit_message_{report_id}")],
            [Button.inline("🔢 تعديل عدد البلاغات", f"edit_count_{report_id}")],
            [Button.inline("⏱️ تعديل التأخير", f"edit_delay_{report_id}")],
            [Button.inline("🚀 استخدام البلاغ", f"load_saved_{report_id}")],
            [Button.inline("🔙 البلاغات المحفوظة", "saved_reports")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def start_edit_message(self, event, report_id: str):
        """بدء تعديل رسالة البلاغ"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data or report_data.get("user_id") != user_id:
            await event.respond("❌ البلاغ غير موجود أو ليس لديك صلاحية")
            return
        
        current_message = report_data.get("report_message", "")
        
        bot_state.update_user_state(user_id, 
                                  editing_report_id=report_id,
                                  step="editing_saved_message")
        
        text = f"""
✏️ **تعديل رسالة البلاغ**

📝 **الرسالة الحالية:**
{current_message}

أرسل الرسالة الجديدة:
        """
        
        buttons = [
            [Button.inline("❌ إلغاء", f"edit_saved_{report_id}")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_edit_saved_message(self, event):
        """معالجة تعديل رسالة البلاغ المحفوظ"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        report_id = user_state.get("editing_report_id")
        new_message = event.text.strip()
        
        # التحقق من صحة البلاغ
        is_valid, validation_message, details = smart_reporter.validate_report_message(new_message)
        
        if not is_valid:
            await event.respond(f"{validation_message}\n\nحاول مرة أخرى:")
            return
        
        # تحديث البلاغ المحفوظ
        success, message = saved_reports_manager.update_report_data(
            report_id, user_id, {"report_message": new_message}
        )
        
        if success:
            quality_score = details.get("quality_score", 0)
            quality_text = "ممتاز" if quality_score >= 0.8 else "جيد" if quality_score >= 0.6 else "مقبول"
            
            text = f"""
✅ **تم تحديث رسالة البلاغ**

📝 **الرسالة الجديدة:**
{new_message}

📊 **جودة البلاغ:** {quality_text} ({quality_score:.2f}/1.00)
            """
        else:
            text = message
        
        buttons = [
            [Button.inline("🚀 استخدام البلاغ", f"load_saved_{report_id}")],
            [Button.inline("✏️ تعديل أخرى", f"edit_saved_{report_id}")],
            [Button.inline("💾 البلاغات المحفوظة", "saved_reports")]
        ]
        
        bot_state.reset_user_state(user_id)
        await event.respond(text, buttons=buttons)
    
    async def start_edit_count(self, event, report_id: str):
        """بدء تعديل عدد البلاغات"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data or report_data.get("user_id") != user_id:
            await event.respond("❌ البلاغ غير موجود أو ليس لديك صلاحية")
            return
        
        current_count = report_data.get("report_count", 100)
        
        bot_state.update_user_state(user_id, 
                                  editing_report_id=report_id,
                                  step="editing_saved_count")
        
        text = f"""
🔢 **تعديل عدد البلاغات**

📊 **العدد الحالي:** {current_count:,}

أرسل العدد الجديد:
• الحد الأدنى: 1
• الحد الأقصى: {config.MAX_REPORTS_PER_SESSION:,}

**أمثلة:** `100` أو `500` أو `1000`
        """
        
        buttons = [
            [Button.inline("❌ إلغاء", f"edit_saved_{report_id}")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_edit_saved_count(self, event):
        """معالجة تعديل عدد البلاغات المحفوظ"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        report_id = user_state.get("editing_report_id")
        
        try:
            new_count = int(event.text.strip())
            
            if new_count < 1:
                await event.respond("❌ العدد يجب أن يكون أكبر من 0")
                return
            
            if new_count > config.MAX_REPORTS_PER_SESSION:
                await event.respond(f"❌ العدد يجب أن يكون أقل من {config.MAX_REPORTS_PER_SESSION:,}")
                return
            
            # تحديث البلاغ المحفوظ
            success, message = saved_reports_manager.update_report_data(
                report_id, user_id, {"report_count": new_count}
            )
            
            if success:
                text = f"✅ تم تحديث عدد البلاغات إلى {new_count:,}"
            else:
                text = message
            
            buttons = [
                [Button.inline("🚀 استخدام البلاغ", f"load_saved_{report_id}")],
                [Button.inline("✏️ تعديل أخرى", f"edit_saved_{report_id}")],
                [Button.inline("💾 البلاغات المحفوظة", "saved_reports")]
            ]
            
            bot_state.reset_user_state(user_id)
            await event.respond(text, buttons=buttons)
            
        except ValueError:
            await event.respond("❌ يرجى إدخال رقم صحيح")
    
    async def start_edit_delay(self, event, report_id: str):
        """بدء تعديل التأخير"""
        user_id = event.sender_id
        report_data = saved_reports_manager.get_report_by_id(report_id)
        
        if not report_data or report_data.get("user_id") != user_id:
            await event.respond("❌ البلاغ غير موجود أو ليس لديك صلاحية")
            return
        
        current_delay = report_data.get("delay_between_reports", 5)
        
        bot_state.update_user_state(user_id, 
                                  editing_report_id=report_id,
                                  step="editing_saved_delay")
        
        text = f"""
⏱️ **تعديل التأخير بين البلاغات**

⏰ **التأخير الحالي:** {current_delay} ثانية

أرسل التأخير الجديد بالثواني:
• الحد الأدنى: 1 ثانية
• الحد الأقصى: 300 ثانية (5 دقائق)

**أمثلة:**
• `2` = سريع جداً (خطر)
• `5` = سريع (موصى به)
• `10` = متوسط (آمن)
• `30` = بطيء (آمن جداً)
        """
        
        buttons = [
            [Button.inline("❌ إلغاء", f"edit_saved_{report_id}")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def process_edit_saved_delay(self, event):
        """معالجة تعديل التأخير المحفوظ"""
        user_id = event.sender_id
        user_state = bot_state.get_user_state(user_id)
        report_id = user_state.get("editing_report_id")
        
        try:
            new_delay = int(event.text.strip())
            
            if new_delay < 1:
                await event.respond("❌ التأخير يجب أن يكون ثانية واحدة على الأقل")
                return
            
            if new_delay > 300:
                await event.respond("❌ التأخير يجب أن يكون أقل من 300 ثانية")
                return
            
            # تحديث البلاغ المحفوظ
            success, message = saved_reports_manager.update_report_data(
                report_id, user_id, {"delay_between_reports": new_delay}
            )
            
            if success:
                # حساب الوقت المتوقع الجديد
                report_data = saved_reports_manager.get_report_by_id(report_id)
                report_count = report_data.get("report_count", 100)
                total_time_seconds = report_count * new_delay
                hours = total_time_seconds // 3600
                minutes = (total_time_seconds % 3600) // 60
                
                time_text = ""
                if hours > 0:
                    time_text = f"{hours} ساعة و {minutes} دقيقة"
                else:
                    time_text = f"{minutes} دقيقة"
                
                text = f"""
✅ **تم تحديث التأخير**

⏱️ **التأخير الجديد:** {new_delay} ثانية
🕐 **الوقت المتوقع:** {time_text}
                """
            else:
                text = message
            
            buttons = [
                [Button.inline("🚀 استخدام البلاغ", f"load_saved_{report_id}")],
                [Button.inline("✏️ تعديل أخرى", f"edit_saved_{report_id}")],
                [Button.inline("💾 البلاغات المحفوظة", "saved_reports")]
            ]
            
            bot_state.reset_user_state(user_id)
            await event.respond(text, buttons=buttons)
            
        except ValueError:
            await event.respond("❌ يرجى إدخال رقم صحيح")
    
    # ==================== دوال البلاغات المباشرة ====================
    
    async def show_direct_reports_menu(self, event):
        """عرض قائمة البلاغات المباشرة"""
        user_id = event.sender_id
        bot_state.reset_user_state(user_id)
        
        text = """
🎯 **البلاغات المباشرة على الرسائل**

هذه الميزة تسمح لك بالإبلاغ مباشرة على رسائل محددة بدلاً من القناة كاملة.

✨ **المميزات:**
• 🎯 دقة أعلى - بلاغ مباشر على الرسالة المخالفة
• ⚡ سرعة أكبر - لا حاجة لتحليل القناة
• 🔥 تأثير أقوى - تليجرام يأخذ البلاغات المباشرة بجدية أكبر
• 📊 دعم حتى 150+ رابط في رسالة واحدة

📝 **كيفية الاستخدام:**
1. انسخ روابط الرسائل المخالفة
2. ألصقها هنا (كل رابط في سطر منفصل)
3. اختر نوع المخالفة
4. ابدأ البلاغات

**أمثلة على الروابط:**
• `https://t.me/channel_name/123`
• `t.me/channel_name/456`
• `@channel_name/789`

⚠️ **ملاحظة:** تأكد من أن الروابط تشير لرسائل مخالفة فعلاً
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات المباشرة", "start_direct_reports")],
            [Button.inline("ℹ️ أمثلة على الروابط", "direct_reports_examples")],
            [Button.inline("🔙 القائمة الرئيسية", "back_to_main")]
        ]
        
        await event.respond(text, buttons=buttons)
    
    async def show_direct_reports_examples(self, event):
        """عرض أمثلة على روابط الرسائل"""
        text = """
📚 **أمثلة على روابط الرسائل**

🔗 **الأشكال المدعومة:**

**1. الرابط الكامل:**
```
https://t.me/spam_channel/123
https://telegram.me/bad_channel/456
```

**2. الرابط المختصر:**
```
t.me/spam_channel/123
telegram.me/bad_channel/456
```

**3. تنسيق @ (الأسرع):**
```
@spam_channel/123
@bad_channel/456
```

📝 **مثال كامل للاستخدام:**
```
https://t.me/spam_channel/100
https://t.me/spam_channel/101
https://t.me/spam_channel/102
t.me/another_bad_channel/50
t.me/another_bad_channel/51
@third_channel/200
@third_channel/201
@third_channel/202
```

💡 **نصائح مهمة:**
• ضع كل رابط في سطر منفصل
• تأكد من أن الروابط تشير لرسائل مخالفة فعلاً
• يمكنك خلط الأشكال المختلفة
• الحد الأقصى 200 رابط في الرسالة الواحدة

⚡ **للحصول على رابط الرسالة:**
1. اذهب للرسالة المخالفة
2. اضغط عليها بالزر الأيمن (أو اضغط مطولاً على الهاتف)
3. اختر "نسخ رابط الرسالة"
4. ألصقه هنا
        """
        
        buttons = [
            [Button.inline("🚀 بدء البلاغات المباشرة", "start_direct_reports")],
            [Button.inline("🔙 رجوع", "direct_message_reports")]
        ]
        
        await event.respond(text, buttons=buttons)