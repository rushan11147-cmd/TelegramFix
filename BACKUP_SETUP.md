# 🔒 Настройка автоматических бэкапов БД

## Вариант 1: Скрипт бэкапа (Рекомендуется)

### 1. Создай скрипт backup.py:

```python
#!/usr/bin/env python3
import sqlite3
import shutil
import os
from datetime import datetime

DB_PATH = 'game_data.db'
BACKUP_DIR = 'backups'

# Создаем папку для бэкапов
os.makedirs(BACKUP_DIR, exist_ok=True)

# Создаем имя файла с датой
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = os.path.join(BACKUP_DIR, f'game_data_{timestamp}.db')

# Копируем БД
shutil.copy2(DB_PATH, backup_path)

print(f"✅ Backup created: {backup_path}")

# Удаляем старые бэкапы (оставляем последние 7)
backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
if len(backups) > 7:
    for old_backup in backups[:-7]:
        os.remove(os.path.join(BACKUP_DIR, old_backup))
        print(f"🗑️ Removed old backup: {old_backup}")
```

### 2. На Render добавь Cron Job:

1. Зайди в Dashboard Render
2. Создай новый Cron Job
3. Команда: `python backup.py`
4. Расписание: `0 3 * * *` (каждый день в 3:00)

## Вариант 2: Облачное хранилище (AWS S3)

### 1. Установи boto3:
```bash
pip install boto3
```

### 2. Создай backup_to_s3.py:

```python
import boto3
import sqlite3
from datetime import datetime
import os

s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

DB_PATH = 'game_data.db'
BUCKET_NAME = 'your-bucket-name'

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
s3_key = f'backups/game_data_{timestamp}.db'

# Загружаем в S3
s3.upload_file(DB_PATH, BUCKET_NAME, s3_key)
print(f"✅ Uploaded to S3: {s3_key}")
```

### 3. Добавь переменные окружения на Render:
- AWS_ACCESS_KEY
- AWS_SECRET_KEY

## Вариант 3: Простой бэкап в Git (Не рекомендуется для продакшена)

```bash
# Каждый день
cp game_data.db backups/game_data_$(date +%Y%m%d).db
git add backups/
git commit -m "Backup $(date)"
git push
```

## Восстановление из бэкапа

```bash
# Остановить приложение
# Скопировать бэкап
cp backups/game_data_20260128.db game_data.db
# Запустить приложение
```

## Тестирование бэкапа

```python
import sqlite3

# Проверяем что бэкап работает
conn = sqlite3.connect('backups/game_data_20260128.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
print(f"Users in backup: {count}")
conn.close()
```

## Рекомендации

1. **Частота**: Минимум 1 раз в день
2. **Хранение**: Минимум 7 дней истории
3. **Место**: Облако (S3, Google Cloud) или отдельный сервер
4. **Тестирование**: Раз в неделю проверяй восстановление
5. **Мониторинг**: Настрой алерты если бэкап не создался

## Автоматизация на Render

Render не поддерживает cron jobs на бесплатном плане. Варианты:

1. **GitHub Actions** (бесплатно):
   - Создай workflow который каждый день делает бэкап
   - Сохраняет в GitHub Releases

2. **External Cron** (бесплатно):
   - Используй cron-job.org
   - Настрой вызов endpoint `/api/backup` каждый день

3. **Платный план Render**:
   - Добавь Cron Job сервис
