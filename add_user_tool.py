#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إضافة المستخدمين - KEVIN BOT
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_manager import user_manager

def main():
    """الدالة الرئيسية"""
    
    print("👥 أداة إضافة المستخدمين - KEVIN BOT")
    print("=" * 50)
    
    while True:
        print("\n📋 الخيارات المتاحة:")
        print("1. إضافة مستخدم جديد")
        print("2. عرض قائمة المستخدمين")
        print("3. حذف مستخدم")
        print("4. تغيير دور مستخدم")
        print("5. عرض الإحصائيات")
        print("6. الخروج")
        
        choice = input("\n🔢 اختر (1-6): ").strip()
        
        if choice == "1":
            add_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            remove_user()
        elif choice == "4":
            change_role()
        elif choice == "5":
            show_stats()
        elif choice == "6":
            print("👋 وداعاً!")
            break
        else:
            print("❌ اختيار غير صحيح")

def add_user():
    """إضافة مستخدم جديد"""
    print("\n➕ إضافة مستخدم جديد")
    print("-" * 30)
    
    try:
        user_id = int(input("معرف المستخدم (User ID): ").strip())
        username = input("اسم المستخدم: ").strip()
        
        if not username:
            username = f"مستخدم {user_id}"
        
        print("\n👑 اختر الدور:")
        print("1. مستخدم عادي (user)")
        print("2. مراقب (moderator)")
        print("3. مشرف (admin)")
        
        role_choice = input("اختر (1-3): ").strip()
        
        role_map = {"1": "user", "2": "moderator", "3": "admin"}
        role = role_map.get(role_choice, "user")
        
        # إضافة المستخدم (المضاف بواسطة النظام)
        success, message = user_manager.add_user(user_id, username, 0, role)
        
        print(f"\n{message}")
        
    except ValueError:
        print("❌ معرف المستخدم يجب أن يكون رقماً")
    except Exception as e:
        print(f"❌ خطأ: {e}")

def list_users():
    """عرض قائمة المستخدمين"""
    print("\n📋 قائمة المستخدمين")
    print("-" * 50)
    
    users = user_manager.get_all_users()
    
    if not users:
        print("📭 لا يوجد مستخدمين مسجلين")
        return
    
    print(f"{'#':<3} {'المعرف':<12} {'الاسم':<20} {'الدور':<12} {'البلاغات':<10} {'الحالة'}")
    print("-" * 70)
    
    for i, user in enumerate(users, 1):
        user_id = str(user['user_id'])
        username = user['username'][:18] + "..." if len(user['username']) > 18 else user['username']
        role = user['role']
        reports = user['reports_sent']
        status = "🟢" if user['status'] == "active" else "🔴"
        
        print(f"{i:<3} {user_id:<12} {username:<20} {role:<12} {reports:<10} {status}")

def remove_user():
    """حذف مستخدم"""
    print("\n🗑️ حذف مستخدم")
    print("-" * 30)
    
    try:
        user_id = int(input("معرف المستخدم المراد حذفه: ").strip())
        
        user_info = user_manager.get_user_info(user_id)
        if not user_info:
            print("❌ المستخدم غير موجود")
            return
        
        print(f"\n⚠️ هل أنت متأكد من حذف المستخدم: {user_info['username']}؟")
        confirm = input("اكتب 'نعم' للتأكيد: ").strip().lower()
        
        if confirm in ['نعم', 'yes', 'y']:
            success, message = user_manager.remove_user(user_id, 0)
            print(f"\n{message}")
        else:
            print("❌ تم إلغاء العملية")
            
    except ValueError:
        print("❌ معرف المستخدم يجب أن يكون رقماً")
    except Exception as e:
        print(f"❌ خطأ: {e}")

def change_role():
    """تغيير دور مستخدم"""
    print("\n⚙️ تغيير دور مستخدم")
    print("-" * 30)
    
    try:
        user_id = int(input("معرف المستخدم: ").strip())
        
        user_info = user_manager.get_user_info(user_id)
        if not user_info:
            print("❌ المستخدم غير موجود")
            return
        
        print(f"\nالمستخدم: {user_info['username']}")
        print(f"الدور الحالي: {user_info['role']}")
        
        print("\n👑 اختر الدور الجديد:")
        print("1. مستخدم عادي (user)")
        print("2. مراقب (moderator)")
        print("3. مشرف (admin)")
        
        role_choice = input("اختر (1-3): ").strip()
        
        role_map = {"1": "user", "2": "moderator", "3": "admin"}
        new_role = role_map.get(role_choice)
        
        if not new_role:
            print("❌ اختيار غير صحيح")
            return
        
        success, message = user_manager.change_user_role(user_id, new_role, 0)
        print(f"\n{message}")
        
    except ValueError:
        print("❌ معرف المستخدم يجب أن يكون رقماً")
    except Exception as e:
        print(f"❌ خطأ: {e}")

def show_stats():
    """عرض الإحصائيات"""
    print("\n📊 إحصائيات المستخدمين")
    print("-" * 40)
    
    stats = user_manager.get_stats()
    
    print(f"📈 إجمالي المستخدمين: {stats['total_users']}")
    print(f"🟢 المستخدمين النشطين: {stats['active_users']}")
    print(f"📡 إجمالي البلاغات: {stats['total_reports']:,}")
    
    print(f"\n👑 توزيع الأدوار:")
    for role, count in stats['roles_count'].items():
        role_name = {"owner": "مالك", "admin": "مشرف", "moderator": "مراقب", "user": "مستخدم"}.get(role, role)
        print(f"   • {role_name}: {count}")
    
    print(f"\n📅 تاريخ الإنشاء: {stats.get('created_date', 'غير محدد')[:10]}")
    
    # أكثر المستخدمين نشاطاً
    users = user_manager.get_all_users()
    if users:
        users_sorted = sorted(users, key=lambda x: x.get('reports_sent', 0), reverse=True)
        
        print(f"\n🏆 أكثر المستخدمين نشاطاً:")
        for i, user in enumerate(users_sorted[:5], 1):
            print(f"   {i}. {user['username']}: {user['reports_sent']:,} بلاغ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")