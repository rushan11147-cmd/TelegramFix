@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo   ЗАГРУЗКА ПРОЕКТА НА GITHUB
echo ═══════════════════════════════════════════════════════════════
echo.

echo Проверка Git...
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git не установлен!
    echo.
    echo Установи Git: https://git-scm.com/download/win
    echo Или используй интерфейс редактора ^(Ctrl+Shift+G^)
    echo.
    pause
    exit /b 1
)

echo ✅ Git найден!
echo.

echo Инициализация репозитория...
git init
if %errorlevel% neq 0 (
    echo ⚠️ Репозиторий уже инициализирован
)
echo.

echo Добавление файлов...
git add .
echo ✅ Файлы добавлены
echo.

echo Создание коммита...
git commit -m "Исправлены критические баги (версия 2.1.1)"
if %errorlevel% neq 0 (
    echo ⚠️ Нет изменений для коммита или коммит уже создан
)
echo.

echo Подключение к GitHub...
git remote add origin https://github.com/rushan11147-cmd/TelegramFix.git 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Remote уже существует, обновляем...
    git remote set-url origin https://github.com/rushan11147-cmd/TelegramFix.git
)
echo ✅ Подключено к GitHub
echo.

echo Отправка на GitHub...
git branch -M main
git push -u origin main
if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ✅ УСПЕШНО ЗАГРУЖЕНО!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Проект доступен по адресу:
    echo https://github.com/rushan11147-cmd/TelegramFix
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ❌ ОШИБКА ЗАГРУЗКИ
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Возможные причины:
    echo 1. Нужна аутентификация ^(используй Personal Access Token^)
    echo 2. Репозиторий не существует на GitHub
    echo 3. Нет прав доступа
    echo.
    echo Попробуй загрузить через интерфейс редактора ^(Ctrl+Shift+G^)
    echo.
)

pause
