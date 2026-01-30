# 🔄 КАК СБРОСИТЬ БАЗУ ДАННЫХ НА RENDER

## СПОСОБ 1: Через скрипт (РЕКОМЕНДУЕТСЯ)

### Локально (для теста):
```bash
python reset_database.py
```

### На Render:
1. Зайди на https://dashboard.render.com
2. Выбери свой сервис
3. Shell → Connect
4. Выполни:
```bash
python reset_database.py
```

## СПОСОБ 2: Через Render Dashboard

### Шаг 1: Найди DATABASE_URL
1. Зайди на https://dashboard.render.com
2. Выбери свой сервис
3. Environment → DATABASE_URL
4. Скопируй значение

### Шаг 2: Подключись к базе
Есть несколько вариантов:

#### Вариант A: Через Render Shell
1. Dashboard → твой сервис → Shell
2. Выполни:
```bash
python -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute('DELETE FROM users')
print(f'Удалено: {cursor.rowcount} пользователей')
conn.commit()
cursor.close()
conn.close()
"
```

#### Вариант B: Через psql (если установлен)
```bash
psql "твой_DATABASE_URL"
DELETE FROM users;
\q
```

#### Вариант C: Через pgAdmin или DBeaver
1. Установи pgAdmin или DBeaver
2. Подключись используя DATABASE_URL
3. Выполни SQL:
```sql
DELETE FROM users;
```

## СПОСОБ 3: Пересоздать базу данных

### На Render:
1. Dashboard → Databases
2. Найди свою базу данных
3. Settings → Delete Database
4. Создай новую базу данных
5. Обнови DATABASE_URL в сервисе

⚠️ **ВНИМАНИЕ**: Это удалит ВСЕ данные!

## СПОСОБ 4: Добавить API endpoint (для будущего)

Можно добавить в `app.py`:

```python
@app.route('/api/admin/reset_database', methods=['POST'])
def admin_reset_database():
    """Сброс базы данных (только для админа)"""
    # Проверка пароля админа
    data = request.get_json()
    admin_password = data.get('password')
    
    if admin_password != os.getenv('ADMIN_PASSWORD'):
        return jsonify({"error": "Неверный пароль"}), 403
    
    # Удаляем всех пользователей
    with db_lock:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users')
            deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
        else:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users')
                deleted = cursor.rowcount
                conn.commit()
    
    return jsonify({
        "success": True,
        "deleted": deleted,
        "message": f"Удалено {deleted} пользователей"
    })
```

Потом можно вызвать через curl:
```bash
curl -X POST https://telegramfix.onrender.com/api/admin/reset_database \
  -H "Content-Type: application/json" \
  -d '{"password":"твой_секретный_пароль"}'
```

## ЧТО ПРОИЗОЙДЕТ ПОСЛЕ СБРОСА?

После сброса базы данных:
- ✅ Все пользователи удалены
- ✅ При следующем входе создастся новый пользователь
- ✅ Все начнут с 500₽, день 1, энергия 100

## ПРОВЕРКА

После сброса проверь:
1. Открой игру в браузере
2. Обнови страницу (Ctrl + F5)
3. Должен начаться новый профиль

## ВАЖНО!

⚠️ **Сброс базы данных необратим!**
⚠️ **Все игроки потеряют прогресс!**
⚠️ **Делай это только если уверен!**

## РЕКОМЕНДАЦИЯ

Для продакшена лучше использовать СПОСОБ 1 (скрипт reset_database.py),
так как он безопаснее и логирует все действия.
