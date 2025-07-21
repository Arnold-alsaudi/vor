#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام البلاغات المباشرة على الرسائل - KEVIN BOT
"""

import asyncio
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from telethon import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (
    InputReportReasonSpam, 
    InputReportReasonViolence, 
    InputReportReasonPornography, 
    InputReportReasonChildAbuse, 
    InputReportReasonOther,
    InputReportReasonCopyright,
    InputReportReasonGeoIrrelevant,
    InputReportReasonFake
)
from telethon.errors import FloodWaitError, ChatAdminRequiredError, MessageIdInvalidError
import config

class MessageReporter:
    """مدير البلاغات المباشرة على الرسائل"""
    
    def __init__(self):
        self.report_types = {
            "i_dont_like_it": InputReportReasonOther(),
            "child_abuse": InputReportReasonChildAbuse(),
            "violence": InputReportReasonViolence(),
            "illegal_goods": InputReportReasonOther(),
            "illegal_adult_content": InputReportReasonPornography(),
            "personal_data": InputReportReasonOther(),
            "terrorism": InputReportReasonViolence(),
            "scam_spam": InputReportReasonSpam(),
            "copyright": InputReportReasonCopyright(),
            "other": InputReportReasonOther(),
            "not_illegal_takedown": InputReportReasonOther()
        }
        
        self.report_type_names = {
            "i_dont_like_it": "😤 I don't like it",
            "child_abuse": "👶 Child abuse",
            "violence": "💣 Violence",
            "illegal_goods": "🚫 Illegal goods",
            "illegal_adult_content": "🔞 Illegal adult content",
            "personal_data": "🔒 Personal data",
            "terrorism": "💥 Terrorism",
            "scam_spam": "📧 Scam or spam",
            "copyright": "©️ Copyright",
            "other": "⚠️ Other",
            "not_illegal_takedown": "⚖️ It's not illegal, but must be taken down"
        }
        
        self.report_descriptions = {
            "i_dont_like_it": "محتوى غير مرغوب فيه",
            "child_abuse": "إساءة معاملة الأطفال أو استغلالهم",
            "violence": "عنف أو تهديدات أو محتوى ضار",
            "illegal_goods": "بيع أو ترويج سلع غير قانونية",
            "illegal_adult_content": "محتوى جنسي غير قانوني أو غير لائق",
            "personal_data": "نشر معلومات شخصية بدون إذن",
            "terrorism": "محتوى إرهابي أو تحريض على العنف",
            "scam_spam": "احتيال أو رسائل مزعجة أو سبام",
            "copyright": "انتهاك حقوق الطبع والنشر",
            "other": "مخالفات أخرى لشروط الخدمة",
            "not_illegal_takedown": "محتوى يجب إزالته رغم عدم كونه غير قانوني"
        }
    
    def extract_message_links(self, text: str) -> List[Dict]:
        """استخراج روابط الرسائل من النص"""
        # أنماط روابط تليجرام المختلفة
        patterns = [
            r'https://t\.me/([^/\s]+)/(\d+)',  # https://t.me/channel/123
            r'https://telegram\.me/([^/\s]+)/(\d+)',  # https://telegram.me/channel/123
            r't\.me/([^/\s]+)/(\d+)',  # t.me/channel/123
            r'telegram\.me/([^/\s]+)/(\d+)',  # telegram.me/channel/123
            r'@([a-zA-Z0-9_]+)/(\d+)',  # @channel/123
        ]
        
        message_links = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                channel = match[0].replace('@', '')
                message_id = int(match[1])
                
                # تجنب التكرار
                link_exists = any(
                    link['channel'].lower() == channel.lower() and link['message_id'] == message_id 
                    for link in message_links
                )
                
                if not link_exists:
                    message_links.append({
                        'channel': channel,
                        'message_id': message_id,
                        'original_link': f"https://t.me/{channel}/{message_id}"
                    })
        
        return message_links
    
    def validate_message_links(self, links: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """التحقق من صحة روابط الرسائل"""
        valid_links = []
        errors = []
        
        for link in links:
            channel = link['channel']
            message_id = link['message_id']
            
            # التحقق من صحة اسم القناة
            if not re.match(r'^[a-zA-Z0-9_]+$', channel):
                errors.append(f"❌ اسم قناة غير صحيح: {channel}")
                continue
            
            # التحقق من صحة معرف الرسالة
            if message_id <= 0 or message_id > 999999999:
                errors.append(f"❌ معرف رسالة غير صحيح: {message_id}")
                continue
            
            valid_links.append(link)
        
        return valid_links, errors
    
    async def report_message_direct(self, client: TelegramClient, channel: str, message_id: int, 
                                  report_type: str = "other", reason: str = "") -> Tuple[bool, str]:
        """إرسال بلاغ مباشر على رسالة محددة"""
        try:
            # الحصول على كائن القناة
            try:
                channel_entity = await client.get_entity(channel)
            except Exception as e:
                return False, f"❌ لا يمكن الوصول للقناة {channel}: {str(e)}"
            
            # الحصول على نوع البلاغ
            report_reason = self.report_types.get(report_type, self.report_types["other"])
            
            # إرسال البلاغ
            await client(ReportRequest(
                peer=channel_entity,
                id=[message_id],
                reason=report_reason,
                message=reason[:200]  # تليجرام يقبل حتى 200 حرف
            ))
            
            return True, "✅ تم إرسال البلاغ بنجاح"
            
        except MessageIdInvalidError:
            return False, f"❌ معرف الرسالة {message_id} غير صحيح"
        except ChatAdminRequiredError:
            return False, f"❌ تحتاج صلاحيات إدارية للإبلاغ في {channel}"
        except FloodWaitError as e:
            return False, f"⏳ يجب الانتظار {e.seconds} ثانية"
        except Exception as e:
            return False, f"❌ خطأ: {str(e)}"
    
    async def report_multiple_messages(self, sessions_data: Dict, links: List[Dict], 
                                     report_type: str = "other", reason: str = "",
                                     report_count: int = 100, delay: int = 3, 
                                     progress_callback=None) -> Dict:
        """إرسال بلاغات على رسائل متعددة من جلسات متعددة"""
        
        results = {
            'total_messages': len(links),
            'requested_reports': report_count,
            'total_attempts': 0,
            'successful_reports': 0,
            'failed_reports': 0,
            'errors': [],
            'success_details': [],
            'session_stats': {},
            'reports_per_message': {}
        }
        
        # فلترة الجلسات النشطة
        active_sessions = {
            session_id: session_data 
            for session_id, session_data in sessions_data.items() 
            if session_data.get('status') == 'active'
        }
        
        if not active_sessions:
            results['errors'].append("❌ لا توجد جلسات نشطة")
            return results
        
        session_ids = list(active_sessions.keys())
        total_sessions = len(session_ids)
        
        # حساب توزيع البلاغات
        reports_per_message = report_count // len(links) if len(links) > 0 else 0
        remaining_reports = report_count % len(links)
        
        print(f"🚀 بدء {report_count} بلاغ على {len(links)} رسالة باستخدام {total_sessions} جلسة")
        print(f"📊 توزيع: {reports_per_message} بلاغ لكل رسالة + {remaining_reports} بلاغ إضافي")
        
        total_operations = 0
        
        # توزيع البلاغات على الرسائل
        for message_idx, link in enumerate(links):
            # حساب عدد البلاغات لهذه الرسالة
            message_reports = reports_per_message
            if message_idx < remaining_reports:
                message_reports += 1
            
            if message_reports == 0:
                continue
            
            results['reports_per_message'][link['original_link']] = {
                'requested': message_reports,
                'successful': 0,
                'failed': 0
            }
            
            # إرسال البلاغات لهذه الرسالة
            for report_idx in range(message_reports):
                session_id = session_ids[total_operations % total_sessions]
                session_data = active_sessions[session_id]
                
                total_operations += 1
                
                # إنشاء عميل تليجرام للجلسة
                try:
                    client = TelegramClient(
                        session_data['session_file'],
                        config.API_ID,
                        config.API_HASH
                    )
                    
                    await client.start()
                    
                    # إرسال البلاغ
                    success, message = await self.report_message_direct(
                        client, link['channel'], link['message_id'], report_type, reason
                    )
                    
                    results['total_attempts'] += 1
                    
                    if success:
                        results['successful_reports'] += 1
                        results['reports_per_message'][link['original_link']]['successful'] += 1
                        results['success_details'].append({
                            'channel': link['channel'],
                            'message_id': link['message_id'],
                            'session': session_id,
                            'link': link['original_link'],
                            'report_number': report_idx + 1
                        })
                        
                        # إحصائيات الجلسة
                        if session_id not in results['session_stats']:
                            results['session_stats'][session_id] = {'success': 0, 'failed': 0}
                        results['session_stats'][session_id]['success'] += 1
                        
                        print(f"✅ [{total_operations}/{report_count}] {link['original_link']} (بلاغ {report_idx+1}/{message_reports}) - {session_id}")
                    else:
                        results['failed_reports'] += 1
                        results['reports_per_message'][link['original_link']]['failed'] += 1
                        results['errors'].append(f"{link['original_link']} (بلاغ {report_idx+1}): {message}")
                        
                        # إحصائيات الجلسة
                        if session_id not in results['session_stats']:
                            results['session_stats'][session_id] = {'success': 0, 'failed': 0}
                        results['session_stats'][session_id]['failed'] += 1
                        
                        print(f"❌ [{total_operations}/{report_count}] {link['original_link']} (بلاغ {report_idx+1}): {message}")
                    
                    await client.disconnect()
                    
                    # تحديث التقدم
                    if progress_callback:
                        progress = total_operations / report_count * 100
                        await progress_callback(progress, total_operations, report_count)
                    
                    # تأخير بين البلاغات
                    if total_operations < report_count:
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    results['failed_reports'] += 1
                    results['reports_per_message'][link['original_link']]['failed'] += 1
                    results['errors'].append(f"{link['original_link']} (بلاغ {report_idx+1}): خطأ في الجلسة {session_id} - {str(e)}")
                    print(f"❌ [{total_operations}/{report_count}] خطأ في الجلسة {session_id}: {e}")
        
        return results
    
    def group_links_by_channel(self, links: List[Dict]) -> Dict[str, List[Dict]]:
        """تجميع الروابط حسب القناة"""
        grouped = {}
        
        for link in links:
            channel = link['channel'].lower()
            if channel not in grouped:
                grouped[channel] = []
            grouped[channel].append(link)
        
        return grouped
    
    def generate_report_summary(self, results: Dict) -> str:
        """إنشاء ملخص نتائج البلاغات"""
        success_rate = (results['successful_reports'] / max(results['total_attempts'], 1)) * 100
        
        summary = f"""
📊 **ملخص البلاغات المباشرة**

🎯 **النتائج العامة:**
• إجمالي الرسائل: {results['total_messages']}
• المحاولات: {results['total_attempts']}
• البلاغات الناجحة: {results['successful_reports']}
• البلاغات الفاشلة: {results['failed_reports']}
• معدل النجاح: {success_rate:.1f}%

📈 **إحصائيات الجلسات:**
"""
        
        for session_id, stats in results['session_stats'].items():
            total = stats['success'] + stats['failed']
            session_rate = (stats['success'] / max(total, 1)) * 100
            summary += f"• {session_id}: {stats['success']}/{total} ({session_rate:.1f}%)\n"
        
        if results['errors']:
            summary += f"\n⚠️ **الأخطاء:** {len(results['errors'])} خطأ"
        
        return summary
    
    def save_report_log(self, results: Dict, report_type: str, reason: str) -> str:
        """حفظ سجل البلاغات"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"message_reports_{timestamp}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "report_type": report_type,
            "reason": reason,
            "results": results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            return filename
        except Exception as e:
            print(f"❌ خطأ في حفظ السجل: {e}")
            return ""

# إنشاء مثيل عام
message_reporter = MessageReporter()