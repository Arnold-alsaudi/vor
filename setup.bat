@echo off
chcp 65001 >nul
title KEVIN BOT - Setup

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ⚙️ KEVIN BOT - Setup                            ║
echo ║                                                              ║
echo ║                   إعداد سريع للبوت                           ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🚀 بدء إعداد KEVIN BOT...
echo.

REM التحقق من وجود Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.7 أو أحدث من python.org
    pause
    exit /b 1
)

echo ✅ تم العثور على Python
py --version

REM تشغيل سكريبت الإعداد
echo.
echo 📦 جاري تشغيل سكريبت الإعداد...
py setup.py

echo.
echo ✅ تم الانتهاء من الإعداد
echo.
echo 📋 للتشغيل: اضغط مرتين على run_bot.bat
echo 📚 للمساعدة: اقرأ README.md
echo.
pause