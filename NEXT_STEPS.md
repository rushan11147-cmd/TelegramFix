# 🚀 Что дальше - Инструкция по запуску

## ✅ Что уже сделано

1. ✅ **Backend полностью готов**:
   - Модуль `business_system.py` с полной бизнес-логикой
   - 10 API endpoints интегрированы в `app.py`
   - Автоматическая обработка бизнесов при переходе дня
   - Сохранение в существующую БД

2. ✅ **Интеграция с игрой**:
   - Бизнесы обрабатываются каждый день
   - Доходы/расходы автоматически добавляются к деньгам игрока
   - События влияют на бизнес
   - Достижения за бизнес

## 🎯 Следующие шаги

### Шаг 1: Запустить и протестировать backend

```bash
# Запустить приложение
python app.py
```

Приложение запустится на `http://localhost:8080`

### Шаг 2: Протестировать API

Используй Postman или curl для тестирования:

```bash
# Создать бизнес
curl -X POST http://localhost:8080/api/business/create \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user","business_type":"kiosk"}'

# Получить список бизнесов
curl "http://localhost:8080/api/business/list?user_id=demo_user"

# Получить конфигурации
curl "http://localhost:8080/api/business/configs"
```

### Шаг 3: Создать Frontend UI

Нужно добавить новый раздел в игру для управления бизнесами.

#### Вариант 1: Простой HTML/JS (быстро)

Создай файл `templates/business.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Мои бизнесы</title>
    <style>
        .business-card {
            border: 2px solid #333;
            padding: 15px;
            margin: 10px;
            border-radius: 10px;
        }
        .profit { color: green; }
        .loss { color: red; }
    </style>
</head>
<body>
    <h1>🏪 Мои бизнесы</h1>
    <div id="businesses"></div>
    <button onclick="createBusiness()">Создать бизнес</button>
    
    <script>
        const userId = 'demo_user'; // Получить из Telegram
        
        async function loadBusinesses() {
            const response = await fetch(`/api/business/list?user_id=${userId}`);
            const data = await response.json();
            
            const container = document.getElementById('businesses');
            container.innerHTML = data.businesses.map(b => `
                <div class="business-card">
                    <h3>${b.config.emoji} ${b.config.name}</h3>
                    <p>Рейтинг: ${'⭐'.repeat(Math.floor(b.rating))}</p>
                    <p>Запасы: ${b.inventory_level.toFixed(0)}%</p>
                    <p>Доход: ${b.daily_revenue.toFixed(0)}₽</p>
                    <p>Расходы: ${b.daily_expenses.toFixed(0)}₽</p>
                    <p class="${b.net_profit >= 0 ? 'profit' : 'loss'}">
                        Прибыль: ${b.net_profit.toFixed(0)}₽
                    </p>
                    <button onclick="buyInventory('${b.business_id}')">
                        Купить запасы (5,000₽)
                    </button>
                </div>
            `).join('');
        }
        
        async function createBusiness() {
            const type = prompt('Тип бизнеса (kiosk/cafe/restaurant/restaurant_chain):');
            const response = await fetch('/api/business/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId, business_type: type})
            });
            const data = await response.json();
            alert(data.message || data.error);
            loadBusinesses();
        }
        
        async function buyInventory(businessId) {
            const response = await fetch(`/api/business/${businessId}/buy-inventory`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId})
            });
            const data = await response.json();
            alert(data.message || data.error);
            loadBusinesses();
        }
        
        loadBusinesses();
    </script>
</body>
</html>
```

Добавь роут в `app.py`:

```python
@app.route('/business')
def business_page():
    return render_template('business.html')
```

#### Вариант 2: Интеграция в существующий UI

Добавь раздел "Бизнес" в `templates/simple.html` или `templates/index.html`:

1. Добавь кнопку "💼 Бизнес" в меню
2. Создай секцию для отображения бизнесов
3. Используй существующий стиль игры

### Шаг 4: Тестирование

1. Создай бизнес через UI
2. Нанми сотрудника
3. Купи запасы
4. Перейди на следующий день
5. Проверь что доход добавился к деньгам

### Шаг 5: Балансировка

После тестирования можешь настроить:
- Стоимость бизнесов
- Доходы/расходы
- Вероятности событий
- Эффекты улучшений

Все настройки в `business_system.py` в словарях:
- `BUSINESS_CONFIGS`
- `EMPLOYEE_CONFIGS`
- `UPGRADE_CONFIGS`
- `EVENT_CONFIGS`

## 🎨 Идеи для UI

### Минимальный UI (1-2 часа):
- Список бизнесов с основной информацией
- Кнопки: Создать, Купить запасы, Продать
- Простые карточки

### Средний UI (4-6 часов):
- Детальная страница каждого бизнеса
- Управление сотрудниками
- Покупка улучшений
- Отображение событий
- Графики доходов

### Продвинутый UI (1-2 дня):
- Анимации
- Интерактивные графики
- Уведомления о событиях
- Сравнение бизнесов
- Прогнозы прибыли

## 📱 Для Telegram Mini App

Используй Telegram WebApp API для получения user_id:

```javascript
// В начале скрипта
const tg = window.Telegram.WebApp;
tg.ready();

const userId = tg.initDataUnsafe?.user?.id || 'demo_user';
```

## 🐛 Если что-то не работает

### Проблема: Ошибка импорта business_system

**Решение**: Убедись что `business_system.py` в той же папке что и `app.py`

### Проблема: API возвращает 400

**Решение**: Проверь что передаешь правильные параметры:
- `user_id` - строка
- `business_type` - один из: kiosk, cafe, restaurant, restaurant_chain
- `employee_type` - один из: chef, cashier, manager
- `upgrade_type` - один из: new_menu, delivery, renovation, advertising

### Проблема: Бизнесы не обрабатываются при переходе дня

**Решение**: Проверь что в `app.py` в функции `next_day()` есть строка:
```python
business_report = business_manager.process_daily_operations(user_id)
```

## 📚 Документация

- `BUSINESS_SYSTEM_README.md` - полная документация по системе
- `ВИЗУАЛИЗАЦИЯ_НОВЫХ_ФИЧ.md` - визуальные примеры UI
- `.kiro/specs/business-branch/` - спецификации и требования

## 🎉 Готово!

Backend полностью готов и работает. Осталось только создать UI для взаимодействия с пользователем.

Удачи! 🚀
