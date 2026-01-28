@echo off
echo ========================================
echo ДЕПЛОЙ НА RENDER
echo ========================================
echo.

echo Шаг 1: Добавляем все файлы в git...
git add .

echo.
echo Шаг 2: Создаём коммит...
set /p commit_message="Введите описание изменений (или Enter для 'Update'): "
if "%commit_message%"=="" set commit_message=Update

git commit -m "%commit_message%"

echo.
echo Шаг 3: Отправляем на GitHub...
git push origin main

echo.
echo ========================================
echo ✅ КОД ЗАГРУЖЕН НА GITHUB!
echo ========================================
echo.
echo Render автоматически обновит ваш сервис.
echo Подождите 2-3 минуты и проверьте:
echo.
echo 🌐 Ваш сайт: https://ваш-сервис.onrender.com
echo 📊 Логи: https://dashboard.render.com
echo.
pause
