@echo off
chcp 65001 >nul
title KEVIN BOT - Telegram Reporter

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                    🤖 KEVIN BOT                              ║
echo ║                                                              ║
echo ║                بوت البلاغات الاحترافي                        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🚀 بدء تشغيل KEVIN BOT...
echo.

REM التحقق من وجود Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.7 أو أحدث
    pause
    exit /b 1
)

REM التحقق من وجود الملفات المطلوبة
if not exist "main.py" (
    echo ❌ ملف main.py غير موجود
    pause
    exit /b 1
)

if not exist "config.py" (
    echo ❌ ملف config.py غير موجود
    pause
    exit /b 1
)

REM تشغيل البوت
echo ✅ جاري تشغيل البوت...
py main.py

REM في حالة إنهاء البوت
echo.
echo ⏹️ تم إيقاف البوت
pause