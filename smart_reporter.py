#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام البلاغات الذكية - KEVIN BOT
نظام متقدم لكشف المحتوى المخالف وإنشاء بلاغات حقيقية
"""

import asyncio
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from telethon import TelegramClient
from telethon.tl.types import Message, Channel, User
from telethon.tl.functions.messages import GetHistoryRequest
import config

class ContentAnalyzer:
    """محلل المحتوى المخالف"""
    
    def __init__(self):
        # قوائم الكلمات المخالفة
        self.violation_patterns = {
            "personal_info": {
                "patterns": [
                    r'\b\d{10,15}\b',  # أرقام هواتف
                    r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b',  # أرقام بطاقات
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # إيميلات
                    r'(?:رقم|هاتف|جوال|موبايل|تلفون).*\d{8,}',  # أرقام هواتف عربي
                    r'(?:عنوان|سكن|منزل|شارع|حي).*\d+',  # عناوين
                    r'(?:هوية|جواز|رقم قومي|بطاقة).*\d{8,}',  # وثائق شخصية
                ],
                "keywords": [
                    "رقم هاتف", "جوال", "موبايل", "تلفون", "واتساب", "تليجرام",
                    "عنوان", "سكن", "منزل", "شارع", "حي", "مدينة",
                    "هوية", "جواز سفر", "رقم قومي", "بطاقة شخصية",
                    "حساب بنكي", "رقم حساب", "بطاقة ائتمان"
                ],
                "severity": "high"
            },
            
            "sexual_content": {
                "patterns": [
                    r'(?:سكس|جنس|نيك|زب|كس|طيز)',
                    r'(?:porn|sex|xxx|adult|nude)',
                    r'(?:عاهرة|شرموطة|قحبة|بغي)',
                    r'(?:فيديو|صور).*(?:جنسي|إباحي|عاري)',
                ],
                "keywords": [
                    "محتوى إباحي", "فيديوهات جنسية", "صور عارية",
                    "محتوى للكبار فقط", "مواقع إباحية", "أفلام جنسية"
                ],
                "severity": "high"
            },
            
            "violence": {
                "patterns": [
                    r'(?:قتل|اغتيال|ذبح|تفجير|انتحار)',
                    r'(?:سلاح|مسدس|بندقية|قنبلة|متفجرات)',
                    r'(?:إرهاب|داعش|القاعدة|تنظيم)',
                    r'(?:تهديد|سأقتل|سأذبح|سأفجر)',
                ],
                "keywords": [
                    "عنف", "قتل", "تهديد", "إرهاب", "أسلحة",
                    "تفجير", "انتحار", "تنظيم إرهابي", "عمليات إرهابية"
                ],
                "severity": "high"
            },
            
            "scam": {
                "patterns": [
                    r'(?:ربح|كسب).*(?:مليون|ألف|دولار|ريال)',
                    r'(?:استثمار|تداول).*(?:مضمون|مؤكد|بدون خسارة)',
                    r'(?:عمل من المنزل|وظيفة).*(?:راتب عالي|دخل كبير)',
                    r'(?:حوالة|تحويل|ويسترن يونيون).*(?:عمولة|نسبة)',
                ],
                "keywords": [
                    "احتيال", "نصب", "خداع", "وهمي", "مزيف",
                    "استثمار وهمي", "ربح سريع", "عمولات", "هرمي"
                ],
                "severity": "medium"
            },
            
            "drugs": {
                "patterns": [
                    r'(?:حشيش|ماريجوانا|كوكايين|هيروين)',
                    r'(?:حبوب|كبتاجون|ترامادول|مخدرات)',
                    r'(?:بيع|شراء|توصيل).*(?:مخدرات|حشيش|حبوب)',
                ],
                "keywords": [
                    "مخدرات", "حشيش", "حبوب مخدرة", "مواد مخدرة",
                    "بيع مخدرات", "توصيل مخدرات", "تجارة مخدرات"
                ],
                "severity": "high"
            },
            
            "fake_accounts": {
                "patterns": [
                    r'(?:انتحال|تقليد|مزيف).*(?:شخصية|حساب)',
                    r'(?:أنا|باسم).*(?:مشهور|فنان|سياسي)',
                ],
                "keywords": [
                    "انتحال شخصية", "حساب مزيف", "تقليد شخصية",
                    "ادعاء كاذب", "شخصية وهمية"
                ],
                "severity": "medium"
            },
            
            "child_abuse": {
                "patterns": [
                    r'(?:طفل|أطفال|قاصر).*(?:جنسي|عاري|إباحي)',
                    r'(?:اعتداء|تحرش).*(?:طفل|أطفال|قاصر)',
                ],
                "keywords": [
                    "إساءة للأطفال", "تحرش بالأطفال", "اعتداء على قاصر",
                    "محتوى يضر بالأطفال", "استغلال الأطفال"
                ],
                "severity": "critical"
            }
        }
        
        # قائمة البلاغات الوهمية الشائعة
        self.fake_report_patterns = [
            r'^test\s*\d*$',
            r'^بلاغ\s*\d*$',
            r'^report\s*\d*$',
            r'^spam\s*\d*$',
            r'^fake\s*\d*$',
            r'^اختبار\s*\d*$',
            r'^تجربة\s*\d*$',
            r'هذا بلاغ تجريبي',
            r'this is a test',
            r'just testing',
            r'مجرد اختبار',
        ]
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """تحليل الرسالة للكشف عن المخالفات"""
        if not message:
            return {"violations": [], "severity": "none", "is_violation": False}
        
        message_lower = message.lower()
        violations = []
        max_severity = "none"
        
        for violation_type, data in self.violation_patterns.items():
            # فحص الأنماط
            for pattern in data["patterns"]:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    violations.append({
                        "type": violation_type,
                        "pattern": pattern,
                        "severity": data["severity"]
                    })
                    if self._is_higher_severity(data["severity"], max_severity):
                        max_severity = data["severity"]
            
            # فحص الكلمات المفتاحية
            for keyword in data["keywords"]:
                if keyword.lower() in message_lower:
                    violations.append({
                        "type": violation_type,
                        "keyword": keyword,
                        "severity": data["severity"]
                    })
                    if self._is_higher_severity(data["severity"], max_severity):
                        max_severity = data["severity"]
        
        return {
            "violations": violations,
            "severity": max_severity,
            "is_violation": len(violations) > 0,
            "violation_count": len(violations)
        }
    
    def is_fake_report(self, report_message: str) -> bool:
        """كشف البلاغات الوهمية"""
        if not report_message or len(report_message.strip()) < 10:
            return True
        
        message_lower = report_message.lower().strip()
        
        # فحص الأنماط الوهمية
        for pattern in self.fake_report_patterns:
            if re.match(pattern, message_lower):
                return True
        
        # فحص التكرار المشبوه
        words = message_lower.split()
        if len(set(words)) < len(words) * 0.5:  # أكثر من 50% كلمات مكررة
            return True
        
        # فحص الرسائل القصيرة جداً
        if len(message_lower) < 15:
            return True
        
        # فحص الرسائل التي تحتوي على أرقام فقط
        if re.match(r'^\d+$', message_lower):
            return True
        
        return False
    
    def _is_higher_severity(self, severity1: str, severity2: str) -> bool:
        """مقارنة مستويات الخطورة"""
        severity_levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        return severity_levels.get(severity1, 0) > severity_levels.get(severity2, 0)

class SmartReporter:
    """نظام البلاغات الذكية"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.report_cache = {}  # تخزين مؤقت للبلاغات
        self.analysis_cache = {}  # تخزين مؤقت للتحليلات
    
    async def analyze_channel(self, client: TelegramClient, channel_username: str, limit: int = 50) -> Dict[str, Any]:
        """تحليل قناة للكشف عن المخالفات"""
        try:
            # الحصول على القناة
            entity = await client.get_entity(channel_username)
            
            # الحصول على الرسائل
            messages = await client.get_messages(entity, limit=limit)
            
            analysis_results = {
                "channel_info": {
                    "title": getattr(entity, 'title', 'غير محدد'),
                    "username": getattr(entity, 'username', 'غير محدد'),
                    "participants_count": getattr(entity, 'participants_count', 0),
                    "id": entity.id
                },
                "messages_analyzed": len(messages),
                "violations_found": [],
                "violation_summary": {},
                "severity_distribution": {"none": 0, "low": 0, "medium": 0, "high": 0, "critical": 0},
                "recommended_reports": [],
                "analysis_date": datetime.now().isoformat()
            }
            
            for message in messages:
                if not message.message:
                    continue
                
                # تحليل الرسالة
                message_analysis = self.analyzer.analyze_message(message.message)
                
                if message_analysis["is_violation"]:
                    violation_data = {
                        "message_id": message.id,
                        "message_text": message.message[:200] + "..." if len(message.message) > 200 else message.message,
                        "date": message.date.isoformat() if message.date else None,
                        "violations": message_analysis["violations"],
                        "severity": message_analysis["severity"]
                    }
                    
                    analysis_results["violations_found"].append(violation_data)
                    
                    # تحديث الإحصائيات
                    for violation in message_analysis["violations"]:
                        violation_type = violation["type"]
                        if violation_type not in analysis_results["violation_summary"]:
                            analysis_results["violation_summary"][violation_type] = 0
                        analysis_results["violation_summary"][violation_type] += 1
                
                # تحديث توزيع الخطورة
                analysis_results["severity_distribution"][message_analysis["severity"]] += 1
            
            # إنشاء التوصيات
            analysis_results["recommended_reports"] = self._generate_smart_reports(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            return {
                "error": str(e),
                "channel_info": {"title": "خطأ", "username": channel_username},
                "messages_analyzed": 0,
                "violations_found": [],
                "violation_summary": {},
                "recommended_reports": []
            }
    
    def _generate_smart_reports(self, analysis_results: Dict) -> List[Dict]:
        """إنشاء بلاغات ذكية بناءً على التحليل"""
        reports = []
        violations = analysis_results["violation_summary"]
        
        # قوالب البلاغات الذكية
        report_templates = {
            "personal_info": [
                "تم رصد نشر معلومات شخصية حساسة في هذه القناة تشمل أرقام هواتف وعناوين سكنية مما يشكل انتهاكاً صريحاً لخصوصية الأفراد",
                "القناة تنشر بيانات شخصية خاصة بالمواطنين دون موافقتهم مما يعرضهم لمخاطر أمنية وانتهاك للخصوصية",
                "يتم نشر معلومات حساسة تشمل أرقام الهوية وبيانات شخصية مما يخالف قوانين حماية البيانات والخصوصية"
            ],
            
            "sexual_content": [
                "المحتوى المنشور يحتوي على مواد إباحية صريحة وغير مناسبة للجمهور العام مما يخالف معايير المجتمع",
                "تم رصد نشر محتوى جنسي فاضح وصور غير لائقة تنتهك قوانين النشر والآداب العامة",
                "القناة تروج لمحتوى إباحي وجنسي صريح مما يضر بالقيم المجتمعية ويخالف القوانين"
            ],
            
            "violence": [
                "المحتوى يحتوي على تهديدات مباشرة وتحريض على العنف مما يشكل خطراً على الأمن العام",
                "تم رصد نشر محتوى يروج للعنف والإرهاب ويحتوي على تهديدات صريحة للأفراد والمجتمع",
                "القناة تنشر محتوى عنيف ومحرض على الكراهية مما يهدد السلم المجتمعي والأمن العام"
            ],
            
            "scam": [
                "تم رصد أنشطة احتيالية ونصب مالي من خلال عروض وهمية للاستثمار والربح السريع",
                "القناة تروج لمخططات احتيالية وعمليات نصب مالي تستهدف المواطنين بعروض كاذبة",
                "يتم نشر إعلانات مضللة وعروض احتيالية تهدف لخداع المتابعين والاستيلاء على أموالهم"
            ],
            
            "drugs": [
                "تم رصد ترويج وبيع المواد المخدرة والمواد المحظورة مما يشكل جريمة جنائية صريحة",
                "القناة تستخدم لتجارة المخدرات والمواد المحظورة مما يضر بالصحة العامة والأمن المجتمعي",
                "يتم الترويج لبيع وتوزيع المواد المخدرة والحبوب المحظورة مما يخالف القوانين الجنائية"
            ],
            
            "fake_accounts": [
                "تم رصد انتحال شخصيات مشهورة ومحاولة خداع المتابعين باستخدام هويات مزيفة",
                "القناة تنتحل شخصيات عامة وتنشر محتوى مضلل باسم أشخاص آخرين دون تصريح",
                "يتم استخدام هويات مزيفة وانتحال شخصيات للترويج لمحتوى مضلل وخادع"
            ],
            
            "child_abuse": [
                "تم رصد محتوى يسيء للأطفال ويحتوي على مواد ضارة بالقاصرين مما يشكل جريمة خطيرة",
                "القناة تنشر محتوى يستغل الأطفال ويعرضهم للخطر مما يخالف قوانين حماية الطفل",
                "يتم نشر مواد تضر بالأطفال وتعرضهم للاستغلال مما يتطلب تدخلاً فورياً"
            ]
        }
        
        # إنشاء البلاغات بناءً على المخالفات المكتشفة
        for violation_type, count in violations.items():
            if count > 0 and violation_type in report_templates:
                templates = report_templates[violation_type]
                
                # اختيار قالب عشوائي
                import random
                selected_template = random.choice(templates)
                
                # تخصيص البلاغ
                customized_report = f"{selected_template}. تم رصد {count} حالة مخالفة من هذا النوع في القناة."
                
                reports.append({
                    "violation_type": violation_type,
                    "report_message": customized_report,
                    "evidence_count": count,
                    "priority": self._get_violation_priority(violation_type),
                    "telegram_report_type": self._get_telegram_report_type(violation_type)
                })
        
        # ترتيب البلاغات حسب الأولوية
        reports.sort(key=lambda x: x["priority"], reverse=True)
        
        return reports
    
    def _get_violation_priority(self, violation_type: str) -> int:
        """تحديد أولوية المخالفة"""
        priorities = {
            "child_abuse": 10,
            "personal_info": 9,
            "violence": 8,
            "drugs": 7,
            "sexual_content": 6,
            "scam": 5,
            "fake_accounts": 4
        }
        return priorities.get(violation_type, 1)
    
    def _get_telegram_report_type(self, violation_type: str) -> str:
        """تحديد نوع البلاغ في تليجرام"""
        mapping = {
            "personal_info": "personal_details",
            "sexual_content": "sexual_content",
            "violence": "violence",
            "scam": "scam",
            "drugs": "drug_promotion",
            "fake_accounts": "fake_account",
            "child_abuse": "child_abuse"
        }
        return mapping.get(violation_type, "other")
    
    def validate_report_message(self, message: str) -> Tuple[bool, str, Dict]:
        """التحقق من صحة رسالة البلاغ"""
        if self.analyzer.is_fake_report(message):
            return False, "❌ تم كشف بلاغ وهمي - يرجى كتابة بلاغ حقيقي ومفصل", {}
        
        # تحليل جودة البلاغ
        quality_score = self._calculate_report_quality(message)
        
        if quality_score < 0.3:
            return False, "❌ جودة البلاغ منخفضة - يرجى إضافة تفاصيل أكثر", {"quality_score": quality_score}
        
        suggestions = self._get_report_suggestions(message)
        
        return True, "✅ البلاغ صالح للإرسال", {
            "quality_score": quality_score,
            "suggestions": suggestions
        }
    
    def _calculate_report_quality(self, message: str) -> float:
        """حساب جودة البلاغ"""
        if not message:
            return 0.0
        
        score = 0.0
        
        # طول الرسالة
        if len(message) >= 50:
            score += 0.3
        elif len(message) >= 30:
            score += 0.2
        elif len(message) >= 15:
            score += 0.1
        
        # تنوع الكلمات
        words = message.split()
        unique_words = set(words)
        if len(words) > 0:
            diversity = len(unique_words) / len(words)
            score += diversity * 0.3
        
        # وجود كلمات مفتاحية مهمة
        important_keywords = [
            "ينشر", "يحتوي", "يروج", "مخالف", "ينتهك", "يضر",
            "غير قانوني", "محظور", "مشبوه", "خطير", "ضار"
        ]
        
        keyword_count = sum(1 for keyword in important_keywords if keyword in message.lower())
        score += min(keyword_count * 0.1, 0.4)
        
        return min(score, 1.0)
    
    def _get_report_suggestions(self, message: str) -> List[str]:
        """اقتراحات لتحسين البلاغ"""
        suggestions = []
        
        if len(message) < 30:
            suggestions.append("أضف المزيد من التفاصيل حول المخالفة")
        
        if "ينشر" not in message.lower() and "يحتوي" not in message.lower():
            suggestions.append("وضح ماذا تفعل القناة بالضبط")
        
        if not any(word in message.lower() for word in ["مخالف", "ينتهك", "محظور", "غير قانوني"]):
            suggestions.append("اذكر سبب كون هذا المحتوى مخالفاً")
        
        return suggestions

# إنشاء مثيل عام
smart_reporter = SmartReporter()