@echo off
echo ============================================
echo  ResumeAI - Setup Script
echo ============================================
echo.

echo [1/3] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Setting up Django database...
python manage.py migrate

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo To run the web server:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo To run the Telegram bot:
echo   venv\Scripts\activate
echo   cd bot
echo   python bot.py
echo.
echo NOTE: Add your TELEGRAM_BOT_TOKEN to .env first!
echo ============================================
pause
