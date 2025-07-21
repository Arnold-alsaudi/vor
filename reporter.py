# KEVIN BOT - نظام البلاغات الاحترافي
# وحدة تنفيذ البلاغات الحقيقية عبر Telegram API

import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonGeoIrrelevant,
    InputReportReasonFake,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonOther
)
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    FloodWaitError,
    ChannelInvalidError,
    UserBannedInChannelError,
    ChatAdminRequiredError
)
import config

class ReportType:
    """أنواع البلاغات المتاحة في تليجرام"""
    
    SEXUAL_CONTENT = "sexual_content"
    PERSONAL_DETAILS = "personal_details"
    VIOLENCE = "violence"
    SCAM = "scam"
    FAKE_ACCOUNT = "fake_account"
    DRUG_PROMOTION = "drug_promotion"
    CHILD_ABUSE = "child_abuse"
    COPYRIGHT = "copyright"
    OTHER = "other"
    
    # خريطة أنواع البلاغات مع الرموز التعبيرية والأوصاف
    REPORT_TYPES = {
        SEXUAL_CONTENT: {
            "emoji": "🔞",
            "name": "محتوى جنسي",
            "description": "Sexual Content",
            "telegram_type": InputReportReasonPornography
        },
        PERSONAL_DETAILS: {
            "emoji": "🧷",
            "name": "نشر معلومات خاصة",
            "description": "Personal Details",
            "telegram_type": InputReportReasonPersonalDetails
        },
        VIOLENCE: {
            "emoji": "💣",
            "name": "العنف أو الإرهاب",
            "description": "Violence",
            "telegram_type": InputReportReasonViolence
        },
        SCAM: {
            "emoji": "💰",
            "name": "نصب/احتيال",
            "description": "Scam",
            "telegram_type": InputReportReasonSpam
        },
        FAKE_ACCOUNT: {
            "emoji": "🎭",
            "name": "حساب مزيف/انتحال",
            "description": "Fake Account",
            "telegram_type": InputReportReasonFake
        },
        DRUG_PROMOTION: {
            "emoji": "🧪",
            "name": "ترويج مخدرات",
            "description": "Drug Promotion",
            "telegram_type": InputReportReasonIllegalDrugs
        },
        CHILD_ABUSE: {
            "emoji": "👶",
            "name": "إساءة للأطفال",
            "description": "Child Abuse",
            "telegram_type": InputReportReasonChildAbuse
        },
        COPYRIGHT: {
            "emoji": "©️",
            "name": "انتهاك حقوق الطبع",
            "description": "Copyright",
            "telegram_type": InputReportReasonCopyright
        },
        OTHER: {
            "emoji": "✍️",
            "name": "سبب آخر مخصص",
            "description": "Other",
            "telegram_type": InputReportReasonOther
        }
    }

class SessionManager:
    """مدير الجلسات للحسابات المضافة"""
    
    def __init__(self):
        self.sessions_file = config.SESSIONS_JSON
        self.sessions_dir = config.SESSIONS_DIR
        self.active_sessions: Dict[str, Dict] = {}
        self.load_sessions()
    
    def load_sessions(self):
        """تحميل الجلسات المحفوظة"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.active_sessions = json.load(f)
            else:
                self.active_sessions = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل الجلسات: {e}")
            self.active_sessions = {}
    
    def save_sessions(self):
        """حفظ الجلسات"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ الجلسات: {e}")
    
    def add_session(self, session_string: str, phone: str = None) -> Tuple[bool, str]:
        """إضافة جلسة جديدة"""
        try:
            # إنشاء معرف فريد للجلسة
            session_id = f"session_{len(self.active_sessions) + 1}"
            session_file = os.path.join(self.sessions_dir, f"{session_id}.session")
            
            # حفظ معلومات الجلسة
            self.active_sessions[session_id] = {
                "session_string": session_string,
                "phone": phone,
                "session_file": session_file,
                "status": "active",
                "reports_sent": 0,
                "last_used": None,
                "errors": 0
            }
            
            self.save_sessions()
            return True, f"✅ تم إضافة الجلسة بنجاح: {session_id}"
            
        except Exception as e:
            return False, f"❌ خطأ في إضافة الجلسة: {e}"
    
    def get_active_sessions(self) -> List[Dict]:
        """الحصول على الجلسات النشطة"""
        return [
            {"id": sid, **sdata} 
            for sid, sdata in self.active_sessions.items() 
            if sdata.get("status") == "active"
        ]
    
    def update_session_status(self, session_id: str, status: str, error_msg: str = None):
        """تحديث حالة الجلسة"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = status
            if error_msg:
                self.active_sessions[session_id]["last_error"] = error_msg
                self.active_sessions[session_id]["errors"] += 1
            self.save_sessions()

class TelegramReporter:
    """نظام البلاغات الاحترافي"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.report_stats = {
            "total_reports": 0,
            "successful_reports": 0,
            "failed_reports": 0,
            "active_sessions": 0
        }
    
    async def create_client_from_session(self, session_data: Dict) -> Optional[TelegramClient]:
        """إنشاء عميل تليجرام من بيانات الجلسة"""
        try:
            session_string = session_data.get("session_string")
            if not session_string:
                print("❌ session_string فارغ")
                return None
            
            # التحقق من صحة session string
            if len(session_string) < 50:
                print(f"❌ session_string قصير جداً: {len(session_string)} حرف")
                return None
            
            # التحقق من أن session string يبدأ بالتنسيق الصحيح
            if not session_string.startswith('1'):
                print("❌ session_string لا يبدأ بالتنسيق الصحيح")
                return None
            
            print(f"🔄 محاولة إنشاء عميل من session string ({len(session_string)} حرف)")
            
            # إنشاء عميل باستخدام StringSession
            client = TelegramClient(
                StringSession(session_string),
                config.API_ID,
                config.API_HASH
            )
            
            # محاولة الاتصال
            await client.connect()
            print("✅ تم الاتصال بنجاح")
            
            # التحقق من التفويض
            if not await client.is_user_authorized():
                print("❌ الجلسة غير مفوضة أو منتهية الصلاحية")
                await client.disconnect()
                return None
            
            # الحصول على معلومات المستخدم للتأكد
            me = await client.get_me()
            print(f"✅ تم تسجيل الدخول: {me.first_name}")
            
            return client
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء العميل: {e}")
            if 'client' in locals():
                try:
                    await client.disconnect()
                except:
                    pass
            return None
    
    def get_report_reason(self, report_type: str):
        """الحصول على نوع البلاغ المناسب لـ Telegram API"""
        report_info = ReportType.REPORT_TYPES.get(report_type)
        if report_info:
            return report_info["telegram_type"]()
        return InputReportReasonOther()
    
    async def send_single_report(
        self, 
        client: TelegramClient, 
        channel_username: str, 
        report_type: str, 
        message: str,
        session_id: str
    ) -> Tuple[bool, str]:
        """إرسال بلاغ واحد"""
        try:
            print(f"🔄 إرسال بلاغ من {session_id} إلى {channel_username}")
            
            # الحصول على معلومات القناة
            entity = await client.get_entity(channel_username)
            print(f"✅ تم العثور على القناة: {entity.title}")
            
            # إنشاء نوع البلاغ
            reason = self.get_report_reason(report_type)
            print(f"📝 نوع البلاغ: {report_type}")
            
            # الحصول على آخر رسالة في القناة للإبلاغ عنها
            try:
                messages = await client.get_messages(entity, limit=1)
                message_id = messages[0].id if messages else 1
                print(f"📨 معرف الرسالة: {message_id}")
            except Exception as msg_error:
                print(f"⚠️ خطأ في الحصول على الرسائل: {msg_error}")
                message_id = 1
            
            # تحضير رسالة البلاغ
            report_message = message[:200] if message else "محتوى مخالف"
            
            # إرسال البلاغ
            print("📡 إرسال البلاغ...")
            result = await client(ReportRequest(
                peer=entity,
                id=[message_id],
                option=b'',  # استخدام option بدلاً من reason
                message=report_message
            ))
            
            print("✅ تم إرسال البلاغ بنجاح")
            
            # تحديث الإحصائيات
            self.report_stats["successful_reports"] += 1
            self.session_manager.active_sessions[session_id]["reports_sent"] += 1
            
            return True, "✅ تم إرسال البلاغ بنجاح"
            
        except FloodWaitError as e:
            error_msg = f"⏳ انتظار مطلوب: {e.seconds} ثانية"
            return False, error_msg
            
        except ChannelInvalidError:
            error_msg = "❌ القناة غير صحيحة أو غير موجودة"
            return False, error_msg
            
        except UserBannedInChannelError:
            error_msg = "❌ الحساب محظور في هذه القناة"
            self.session_manager.update_session_status(session_id, "banned")
            return False, error_msg
            
        except ChatAdminRequiredError:
            error_msg = "❌ صلاحيات المشرف مطلوبة"
            return False, error_msg
            
        except TypeError as e:
            if "ReportRequest" in str(e):
                error_msg = f"❌ خطأ في معاملات البلاغ: {str(e)}"
                print(f"🔧 محاولة إصلاح معاملات ReportRequest...")
                # محاولة بديلة بمعاملات مبسطة
                try:
                    result = await client(ReportRequest(
                        peer=entity,
                        id=[1],  # استخدام معرف ثابت
                        option=b'',  # استخدام option
                        message="محتوى مخالف"
                    ))
                    print("✅ نجحت المحاولة البديلة")
                    self.report_stats["successful_reports"] += 1
                    return True, "✅ تم إرسال البلاغ بنجاح (طريقة بديلة)"
                except:
                    pass
            error_msg = f"❌ خطأ في النوع: {str(e)}"
            return False, error_msg
            
        except Exception as e:
            error_msg = f"❌ خطأ غير متوقع: {str(e)}"
            print(f"🔍 تفاصيل الخطأ: {type(e).__name__}: {e}")
            self.session_manager.update_session_status(session_id, "error", error_msg)
            return False, error_msg
    
    async def execute_mass_report(
        self,
        channel_username: str,
        report_type: str,
        message: str,
        report_count: int,
        delay_between_reports: float = 30,
        progress_callback=None
    ) -> Dict:
        """تنفيذ البلاغات الجماعية"""
        
        results = {
            "total_attempted": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "session_results": {}
        }
        
        active_sessions = self.session_manager.get_active_sessions()
        
        if not active_sessions:
            results["errors"].append("❌ لا توجد جلسات نشطة")
            return results
        
        print(f"🚀 بدء تنفيذ {report_count} بلاغ باستخدام {len(active_sessions)} جلسة")
        
        reports_per_session = report_count // len(active_sessions)
        remaining_reports = report_count % len(active_sessions)
        
        for i, session_data in enumerate(active_sessions):
            session_id = session_data["id"]
            session_reports = reports_per_session + (1 if i < remaining_reports else 0)
            
            if session_reports == 0:
                continue
            
            results["session_results"][session_id] = {
                "attempted": session_reports,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            try:
                client = await self.create_client_from_session(session_data)
                if not client:
                    error_msg = f"❌ فشل في إنشاء العميل للجلسة {session_id}"
                    results["session_results"][session_id]["errors"].append(error_msg)
                    results["failed"] += session_reports
                    continue
                
                # تنفيذ البلاغات لهذه الجلسة
                for report_num in range(session_reports):
                    results["total_attempted"] += 1
                    
                    success, msg = await self.send_single_report(
                        client, channel_username, report_type, message, session_id
                    )
                    
                    if success:
                        results["successful"] += 1
                        results["session_results"][session_id]["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["session_results"][session_id]["failed"] += 1
                        results["session_results"][session_id]["errors"].append(msg)
                    
                    # تحديث التقدم
                    if progress_callback:
                        await progress_callback(
                            results["total_attempted"], 
                            report_count, 
                            session_id, 
                            success, 
                            msg
                        )
                    
                    # انتظار بين البلاغات
                    if report_num < session_reports - 1:
                        await asyncio.sleep(delay_between_reports)
                
                await client.disconnect()
                
            except Exception as e:
                error_msg = f"❌ خطأ في الجلسة {session_id}: {str(e)}"
                results["session_results"][session_id]["errors"].append(error_msg)
                results["errors"].append(error_msg)
                results["failed"] += session_reports - results["session_results"][session_id]["successful"]
        
        # تحديث الإحصائيات العامة
        self.report_stats["total_reports"] += results["total_attempted"]
        self.report_stats["active_sessions"] = len(active_sessions)
        
        return results
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات البوت"""
        active_sessions = self.session_manager.get_active_sessions()
        
        return {
            "active_sessions": len(active_sessions),
            "total_sessions": len(self.session_manager.active_sessions),
            "total_reports": self.report_stats["total_reports"],
            "successful_reports": self.report_stats["successful_reports"],
            "failed_reports": self.report_stats["failed_reports"],
            "session_details": active_sessions
        }

# إنشاء مثيل عام للمراسل
reporter = TelegramReporter()