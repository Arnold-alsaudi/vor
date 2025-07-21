#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة المستخدمين - KEVIN BOT
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import config

class UserManager:
    """مدير المستخدمين المصرح لهم"""
    
    def __init__(self):
        self.users_file = "authorized_users.json"
        self.users_data = self.load_users()
    
    def load_users(self) -> Dict:
        """تحميل بيانات المستخدمين"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # إنشاء ملف جديد مع المالك الأساسي
                default_data = {
                    "owner_id": config.OWNER_ID,
                    "users": {
                        str(config.OWNER_ID): {
                            "user_id": config.OWNER_ID,
                            "username": "المالك الأساسي",
                            "role": "owner",
                            "added_by": "system",
                            "added_date": datetime.now().isoformat(),
                            "permissions": {
                                "can_report": True,
                                "can_add_users": True,
                                "can_remove_users": True,
                                "can_view_stats": True,
                                "can_manage_sessions": True
                            },
                            "status": "active",
                            "reports_sent": 0,
                            "last_activity": datetime.now().isoformat()
                        }
                    },
                    "total_users": 1,
                    "created_date": datetime.now().isoformat()
                }
                self.save_users(default_data)
                return default_data
        except Exception as e:
            print(f"❌ خطأ في تحميل المستخدمين: {e}")
            return {"owner_id": config.OWNER_ID, "users": {}, "total_users": 0}
    
    def save_users(self, data: Dict = None) -> bool:
        """حفظ بيانات المستخدمين"""
        try:
            data_to_save = data if data else self.users_data
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ المستخدمين: {e}")
            return False
    
    def is_authorized(self, user_id: int) -> bool:
        """التحقق من تصريح المستخدم"""
        user_str = str(user_id)
        if user_str in self.users_data.get("users", {}):
            user_info = self.users_data["users"][user_str]
            return user_info.get("status") == "active"
        return False
    
    def is_owner(self, user_id: int) -> bool:
        """التحقق من كون المستخدم مالك"""
        return user_id == self.users_data.get("owner_id") or self.get_user_role(user_id) == "owner"
    
    def can_add_users(self, user_id: int) -> bool:
        """التحقق من صلاحية إضافة مستخدمين"""
        if not self.is_authorized(user_id):
            return False
        
        user_info = self.users_data["users"].get(str(user_id), {})
        permissions = user_info.get("permissions", {})
        return permissions.get("can_add_users", False)
    
    def can_remove_users(self, user_id: int) -> bool:
        """التحقق من صلاحية حذف مستخدمين"""
        if not self.is_authorized(user_id):
            return False
        
        user_info = self.users_data["users"].get(str(user_id), {})
        permissions = user_info.get("permissions", {})
        return permissions.get("can_remove_users", False)
    
    def get_user_role(self, user_id: int) -> str:
        """الحصول على دور المستخدم"""
        user_info = self.users_data["users"].get(str(user_id), {})
        return user_info.get("role", "user")
    
    def add_user(self, user_id: int, username: str, added_by: int, role: str = "user") -> Tuple[bool, str]:
        """إضافة مستخدم جديد"""
        try:
            user_str = str(user_id)
            
            # التحقق من وجود المستخدم مسبقاً
            if user_str in self.users_data["users"]:
                return False, "❌ المستخدم موجود مسبقاً"
            
            # تحديد الصلاحيات حسب الدور
            if role == "admin":
                permissions = {
                    "can_report": True,
                    "can_add_users": True,
                    "can_remove_users": True,
                    "can_view_stats": True,
                    "can_manage_sessions": True
                }
            elif role == "moderator":
                permissions = {
                    "can_report": True,
                    "can_add_users": False,
                    "can_remove_users": False,
                    "can_view_stats": True,
                    "can_manage_sessions": False
                }
            else:  # user
                permissions = {
                    "can_report": True,
                    "can_add_users": False,
                    "can_remove_users": False,
                    "can_view_stats": False,
                    "can_manage_sessions": False
                }
            
            # إضافة المستخدم
            self.users_data["users"][user_str] = {
                "user_id": user_id,
                "username": username,
                "role": role,
                "added_by": added_by,
                "added_date": datetime.now().isoformat(),
                "permissions": permissions,
                "status": "active",
                "reports_sent": 0,
                "last_activity": datetime.now().isoformat()
            }
            
            self.users_data["total_users"] = len(self.users_data["users"])
            
            if self.save_users():
                return True, f"✅ تم إضافة المستخدم {username} بنجاح"
            else:
                return False, "❌ خطأ في حفظ البيانات"
                
        except Exception as e:
            return False, f"❌ خطأ في إضافة المستخدم: {str(e)}"
    
    def remove_user(self, user_id: int, removed_by: int) -> Tuple[bool, str]:
        """حذف مستخدم"""
        try:
            user_str = str(user_id)
            
            # التحقق من وجود المستخدم
            if user_str not in self.users_data["users"]:
                return False, "❌ المستخدم غير موجود"
            
            # منع حذف المالك الأساسي
            if user_id == self.users_data.get("owner_id"):
                return False, "❌ لا يمكن حذف المالك الأساسي"
            
            username = self.users_data["users"][user_str].get("username", "مجهول")
            
            # حذف المستخدم
            del self.users_data["users"][user_str]
            self.users_data["total_users"] = len(self.users_data["users"])
            
            if self.save_users():
                return True, f"✅ تم حذف المستخدم {username} بنجاح"
            else:
                return False, "❌ خطأ في حفظ البيانات"
                
        except Exception as e:
            return False, f"❌ خطأ في حذف المستخدم: {str(e)}"
    
    def update_user_activity(self, user_id: int):
        """تحديث آخر نشاط للمستخدم"""
        user_str = str(user_id)
        if user_str in self.users_data["users"]:
            self.users_data["users"][user_str]["last_activity"] = datetime.now().isoformat()
            self.save_users()
    
    def increment_user_reports(self, user_id: int, count: int = 1):
        """زيادة عدد البلاغات للمستخدم"""
        user_str = str(user_id)
        if user_str in self.users_data["users"]:
            self.users_data["users"][user_str]["reports_sent"] += count
            self.save_users()
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """الحصول على معلومات المستخدم"""
        user_str = str(user_id)
        return self.users_data["users"].get(user_str)
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        return list(self.users_data["users"].values())
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """الحصول على المستخدمين حسب الدور"""
        return [user for user in self.users_data["users"].values() if user.get("role") == role]
    
    def change_user_role(self, user_id: int, new_role: str, changed_by: int) -> Tuple[bool, str]:
        """تغيير دور المستخدم"""
        try:
            user_str = str(user_id)
            
            if user_str not in self.users_data["users"]:
                return False, "❌ المستخدم غير موجود"
            
            # منع تغيير دور المالك الأساسي
            if user_id == self.users_data.get("owner_id"):
                return False, "❌ لا يمكن تغيير دور المالك الأساسي"
            
            old_role = self.users_data["users"][user_str]["role"]
            self.users_data["users"][user_str]["role"] = new_role
            
            # تحديث الصلاحيات
            if new_role == "admin":
                permissions = {
                    "can_report": True,
                    "can_add_users": True,
                    "can_remove_users": True,
                    "can_view_stats": True,
                    "can_manage_sessions": True
                }
            elif new_role == "moderator":
                permissions = {
                    "can_report": True,
                    "can_add_users": False,
                    "can_remove_users": False,
                    "can_view_stats": True,
                    "can_manage_sessions": False
                }
            else:  # user
                permissions = {
                    "can_report": True,
                    "can_add_users": False,
                    "can_remove_users": False,
                    "can_view_stats": False,
                    "can_manage_sessions": False
                }
            
            self.users_data["users"][user_str]["permissions"] = permissions
            
            if self.save_users():
                username = self.users_data["users"][user_str].get("username", "مجهول")
                return True, f"✅ تم تغيير دور {username} من {old_role} إلى {new_role}"
            else:
                return False, "❌ خطأ في حفظ البيانات"
                
        except Exception as e:
            return False, f"❌ خطأ في تغيير الدور: {str(e)}"
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات المستخدمين"""
        total_users = len(self.users_data["users"])
        active_users = len([u for u in self.users_data["users"].values() if u.get("status") == "active"])
        total_reports = sum(u.get("reports_sent", 0) for u in self.users_data["users"].values())
        
        roles_count = {}
        for user in self.users_data["users"].values():
            role = user.get("role", "user")
            roles_count[role] = roles_count.get(role, 0) + 1
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_reports": total_reports,
            "roles_count": roles_count,
            "created_date": self.users_data.get("created_date")
        }

# إنشاء مثيل عام
user_manager = UserManager()