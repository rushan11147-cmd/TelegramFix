@echo off
echo ========================================
echo ПЕРЕЗАПУСК FLASK
echo ========================================
echo.
echo Останавливаю старые процессы Flask...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Запускаю Flask на порту 8080...
echo.
set FLASK_APP=app.py
set FLASK_ENV=development
set RUN_BOT=false
python -m flask run --host=0.0.0.0 --port=8080
