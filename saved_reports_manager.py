#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير البلاغات المحفوظة - KEVIN BOT
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class SavedReportsManager:
    """مدير البلاغات المحفوظة"""
    
    def __init__(self):
        self.saved_reports_file = "saved_reports.json"
        self.saved_data = self.load_saved_reports()
    
    def load_saved_reports(self) -> Dict:
        """تحميل البلاغات المحفوظة"""
        try:
            if os.path.exists(self.saved_reports_file):
                with open(self.saved_reports_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_data = {
                    "reports": {},
                    "total_saved": 0,
                    "created_date": datetime.now().isoformat()
                }
                self.save_reports_data(default_data)
                return default_data
        except Exception as e:
            print(f"❌ خطأ في تحميل البلاغات المحفوظة: {e}")
            return {"reports": {}, "total_saved": 0}
    
    def save_reports_data(self, data: Dict = None) -> bool:
        """حفظ بيانات البلاغات"""
        try:
            data_to_save = data if data else self.saved_data
            with open(self.saved_reports_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ البلاغات: {e}")
            return False
    
    def generate_report_id(self, channel: str, user_id: int) -> str:
        """إنشاء معرف فريد للبلاغ"""
        unique_string = f"{channel}_{user_id}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:8]
    
    def save_report(self, user_id: int, channel: str, report_data: Dict) -> Tuple[bool, str, str]:
        """حفظ بلاغ جديد"""
        try:
            # إنشاء معرف فريد
            report_id = self.generate_report_id(channel, user_id)
            
            # التحقق من وجود البلاغ مسبقاً
            existing_report = self.find_existing_report(user_id, channel)
            if existing_report:
                return False, f"❌ يوجد بلاغ محفوظ مسبقاً لهذه القناة", existing_report
            
            # إعداد بيانات البلاغ
            saved_report = {
                "report_id": report_id,
                "user_id": user_id,
                "channel": channel,
                "channel_info": report_data.get("channel_info", {}),
                "report_type": report_data.get("report_type"),
                "report_message": report_data.get("report_message"),
                "report_count": report_data.get("report_count"),
                "delay_between_reports": report_data.get("delay_between_reports"),
                "analysis_results": report_data.get("analysis_results"),
                "smart_reports": report_data.get("smart_reports", []),
                "created_date": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "usage_count": 0,
                "status": "active"
            }
            
            # حفظ البلاغ
            self.saved_data["reports"][report_id] = saved_report
            self.saved_data["total_saved"] = len(self.saved_data["reports"])
            
            if self.save_reports_data():
                return True, f"✅ تم حفظ البلاغ بنجاح", report_id
            else:
                return False, "❌ خطأ في حفظ البيانات", ""
                
        except Exception as e:
            return False, f"❌ خطأ في حفظ البلاغ: {str(e)}", ""
    
    def find_existing_report(self, user_id: int, channel: str) -> Optional[str]:
        """البحث عن بلاغ موجود للقناة"""
        for report_id, report_data in self.saved_data["reports"].items():
            if (report_data.get("user_id") == user_id and 
                report_data.get("channel").lower() == channel.lower() and
                report_data.get("status") == "active"):
                return report_id
        return None
    
    def get_user_saved_reports(self, user_id: int) -> List[Dict]:
        """الحصول على البلاغات المحفوظة للمستخدم"""
        user_reports = []
        for report_id, report_data in self.saved_data["reports"].items():
            if (report_data.get("user_id") == user_id and 
                report_data.get("status") == "active"):
                user_reports.append(report_data)
        
        # ترتيب حسب آخر استخدام
        user_reports.sort(key=lambda x: x.get("last_used", ""), reverse=True)
        return user_reports
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict]:
        """الحصول على بلاغ بالمعرف"""
        return self.saved_data["reports"].get(report_id)
    
    def update_report_usage(self, report_id: str) -> bool:
        """تحديث آخر استخدام للبلاغ"""
        try:
            if report_id in self.saved_data["reports"]:
                self.saved_data["reports"][report_id]["last_used"] = datetime.now().isoformat()
                self.saved_data["reports"][report_id]["usage_count"] += 1
                return self.save_reports_data()
            return False
        except Exception as e:
            print(f"❌ خطأ في تحديث البلاغ: {e}")
            return False
    
    def delete_report(self, report_id: str, user_id: int) -> Tuple[bool, str]:
        """حذف بلاغ محفوظ"""
        try:
            if report_id not in self.saved_data["reports"]:
                return False, "❌ البلاغ غير موجود"
            
            report_data = self.saved_data["reports"][report_id]
            
            # التحقق من ملكية البلاغ
            if report_data.get("user_id") != user_id:
                return False, "❌ ليس لديك صلاحية حذف هذا البلاغ"
            
            channel = report_data.get("channel", "غير محدد")
            
            # حذف البلاغ
            del self.saved_data["reports"][report_id]
            self.saved_data["total_saved"] = len(self.saved_data["reports"])
            
            if self.save_reports_data():
                return True, f"✅ تم حذف البلاغ المحفوظ للقناة {channel}"
            else:
                return False, "❌ خطأ في حفظ البيانات"
                
        except Exception as e:
            return False, f"❌ خطأ في حذف البلاغ: {str(e)}"
    
    def update_report_data(self, report_id: str, user_id: int, new_data: Dict) -> Tuple[bool, str]:
        """تحديث بيانات البلاغ"""
        try:
            if report_id not in self.saved_data["reports"]:
                return False, "❌ البلاغ غير موجود"
            
            report_data = self.saved_data["reports"][report_id]
            
            # التحقق من ملكية البلاغ
            if report_data.get("user_id") != user_id:
                return False, "❌ ليس لديك صلاحية تعديل هذا البلاغ"
            
            # تحديث البيانات
            for key, value in new_data.items():
                if key not in ["report_id", "user_id", "created_date"]:  # حماية البيانات الأساسية
                    self.saved_data["reports"][report_id][key] = value
            
            self.saved_data["reports"][report_id]["last_used"] = datetime.now().isoformat()
            
            if self.save_reports_data():
                return True, "✅ تم تحديث البلاغ بنجاح"
            else:
                return False, "❌ خطأ في حفظ البيانات"
                
        except Exception as e:
            return False, f"❌ خطأ في تحديث البلاغ: {str(e)}"
    
    def get_report_summary(self, report_id: str) -> str:
        """الحصول على ملخص البلاغ"""
        report_data = self.get_report_by_id(report_id)
        if not report_data:
            return "❌ البلاغ غير موجود"
        
        channel = report_data.get("channel", "غير محدد")
        report_type = report_data.get("report_type", "غير محدد")
        report_count = report_data.get("report_count", 0)
        delay = report_data.get("delay_between_reports", 0)
        usage_count = report_data.get("usage_count", 0)
        last_used = report_data.get("last_used", "")
        
        # حساب الوقت المتوقع
        total_time_seconds = report_count * delay
        hours = total_time_seconds // 3600
        minutes = (total_time_seconds % 3600) // 60
        
        time_text = ""
        if hours > 0:
            time_text = f"{hours} ساعة و {minutes} دقيقة"
        else:
            time_text = f"{minutes} دقيقة"
        
        # تنسيق تاريخ آخر استخدام
        try:
            last_used_date = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
            last_used_formatted = last_used_date.strftime("%Y-%m-%d %H:%M")
        except:
            last_used_formatted = "غير محدد"
        
        summary = f"""
📡 **القناة:** {channel}
📝 **نوع البلاغ:** {report_type}
🔢 **عدد البلاغات:** {report_count:,}
⏱️ **التأخير:** {delay} ثانية
🕐 **الوقت المتوقع:** {time_text}
📊 **مرات الاستخدام:** {usage_count}
📅 **آخر استخدام:** {last_used_formatted}
        """
        
        return summary.strip()
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات البلاغات المحفوظة"""
        total_reports = len(self.saved_data["reports"])
        active_reports = len([r for r in self.saved_data["reports"].values() if r.get("status") == "active"])
        
        # إحصائيات الاستخدام
        total_usage = sum(r.get("usage_count", 0) for r in self.saved_data["reports"].values())
        
        # أكثر القنوات حفظاً
        channels_count = {}
        for report in self.saved_data["reports"].values():
            channel = report.get("channel", "غير محدد")
            channels_count[channel] = channels_count.get(channel, 0) + 1
        
        # أكثر أنواع البلاغات
        report_types_count = {}
        for report in self.saved_data["reports"].values():
            report_type = report.get("report_type", "غير محدد")
            report_types_count[report_type] = report_types_count.get(report_type, 0) + 1
        
        return {
            "total_reports": total_reports,
            "active_reports": active_reports,
            "total_usage": total_usage,
            "channels_count": channels_count,
            "report_types_count": report_types_count,
            "created_date": self.saved_data.get("created_date")
        }
    
    def cleanup_old_reports(self, days: int = 30) -> int:
        """تنظيف البلاغات القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            reports_to_delete = []
            for report_id, report_data in self.saved_data["reports"].items():
                try:
                    last_used = datetime.fromisoformat(report_data.get("last_used", ""))
                    if last_used < cutoff_date:
                        reports_to_delete.append(report_id)
                except:
                    continue
            
            for report_id in reports_to_delete:
                del self.saved_data["reports"][report_id]
                deleted_count += 1
            
            if deleted_count > 0:
                self.saved_data["total_saved"] = len(self.saved_data["reports"])
                self.save_reports_data()
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ خطأ في تنظيف البلاغات: {e}")
            return 0

# إنشاء مثيل عام
saved_reports_manager = SavedReportsManager()