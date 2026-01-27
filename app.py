from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import random
import time
import sqlite3
from threading import Lock

load_dotenv()

app = Flask(__name__)
CORS(app)

# База данных SQLite
DB_PATH = 'game_data.db'
db_lock = Lock()

def init_db():
    """Инициализация базы данных"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_user_data(user_id, data):
    """Сохранение данных пользователя в БД"""
    with db_lock:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, data, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, json.dumps(data)))
            conn.commit()

def load_user_data(user_id):
    """Загрузка данных пользователя из БД"""
    with db_lock:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

# Инициализируем БД при старте
init_db()

# Простое хранилище данных пользователей (кэш в памяти)
users_data = {}

def save_and_return(user_id, response_data):
    """Сохранить данные пользователя в БД и вернуть ответ"""
    if user_id in users_data:
        save_user_data(user_id, users_data[user_id])
    return jsonify(response_data)

# События игры
EVENTS = [
    # Негативные события
    {"text": "Уронил доставку", "cost": -250, "emoji": "🍕", "mood": -5},
    {"text": "Купил дошик", "cost": -150, "emoji": "🍜", "mood": 0},
    {"text": "Переплатил ЖКХ", "cost": -1200, "emoji": "📄", "mood": -10},
    {"text": "Штраф за парковку", "cost": -500, "emoji": "🚗", "mood": -8},
    {"text": "Сломался телефон", "cost": -800, "emoji": "📱", "mood": -15},
    {"text": "Штраф за опоздание", "cost": -200, "emoji": "💸", "mood": -5},
    {"text": "Конфликт с начальником", "cost": 0, "emoji": "😤", "mood": -10},
    {"text": "Не выполнил план", "cost": -150, "emoji": "🚫", "mood": -5},
    {"text": "Сломалось оборудование", "cost": -300, "emoji": "💔", "mood": -8},
    {"text": "Пролил кофе на документы", "cost": -100, "emoji": "☕", "mood": -3},
    
    # Позитивные события
    {"text": "Нашел монетку", "cost": 50, "emoji": "🪙", "mood": 2},
    {"text": "Продал старые вещи", "cost": 300, "emoji": "📦", "mood": 5},
    {"text": "Кэшбэк с карты", "cost": 100, "emoji": "💳", "mood": 3},
    {"text": "Премия от босса", "cost": 500, "emoji": "💰", "mood": 15},
    {"text": "Бонус за хорошую работу", "cost": 300, "emoji": "🎁", "mood": 10},
    {"text": "Клиент дал чаевые", "cost": 200, "emoji": "⭐", "mood": 8},
    {"text": "Выиграл в лотерею", "cost": 1000, "emoji": "🎉", "mood": 20},
    {"text": "Помог коллеге, он угостил", "cost": 100, "emoji": "🤝", "mood": 5},
    {"text": "Нашел купон на скидку", "cost": 150, "emoji": "🎫", "mood": 5},
    
    # Нейтральные события
    {"text": "Поболтал с коллегами", "cost": 0, "emoji": "💬", "mood": 2},
    {"text": "Обычный рабочий день", "cost": 0, "emoji": "📧", "mood": 0},
]

# Черты личности
TRAITS = {
    "терпила": {
        "name": "Терпила",
        "description": "Все штрафы −20%, но доход от работы −15%",
        "emoji": "😤",
        "penalty_reduction": 0.2,
        "income_reduction": 0.15
    },
    "рисковый": {
        "name": "Рисковый", 
        "description": "Шанс событий +30%, но негативные события чаще",
        "emoji": "🎲",
        "event_chance_bonus": 0.3,
        "negative_event_multiplier": 1.5
    },
    "экономный": {
        "name": "Экономный",
        "description": "Все покупки дешевле на 10%, но постоянно грустный",
        "emoji": "💰",
        "cost_reduction": 0.1,
        "mood_penalty": True
    },
    "прокрастинатор": {
        "name": "Прокрастинатор", 
        "description": "Иногда день проходит без действий, но усталость не растёт",
        "emoji": "😴",
        "skip_day_chance": 0.15,
        "no_fatigue_on_skip": True
    }
}

# Виды работ
JOBS = {
    "delivery": {
        "name": "Доставка еды",
        "emoji": "🛵",
        "base_income": 80,
        "energy_cost": 5,  # Было 15, стало 5
        "unlock_day": 1,
        "description": "Быстрые деньги, но устаёшь"
    },
    "office": {
        "name": "Офисная работа", 
        "emoji": "💻",
        "base_income": 120,
        "energy_cost": 3,  # Было 10, стало 3
        "unlock_day": 5,
        "description": "Стабильный доход"
    },
    "freelance": {
        "name": "Фриланс",
        "emoji": "🎨", 
        "base_income": 200,
        "energy_cost": 7,  # Было 20, стало 7
        "unlock_day": 10,
        "description": "Высокий доход, но нестабильно"
    },
    "crypto": {
        "name": "Крипто-трейдинг",
        "emoji": "📈",
        "base_income": 300,
        "energy_cost": 10,  # Было 25, стало 10
        "unlock_day": 15,
        "description": "Рискованно, но прибыльно"
    }
}

# Бустеры
BOOSTERS = {
    "coffee": {
        "name": "Кофе",
        "emoji": "☕",
        "cost": 150,
        "effect": "energy",
        "value": 30,
        "duration": 1,
        "description": "+30 энергии на день"
    },
    "energy_drink": {
        "name": "Энергетик",
        "emoji": "🥤",
        "cost": 300,
        "effect": "energy",
        "value": 50,
        "duration": 1,
        "description": "+50 энергии на день"
    },
    "laptop": {
        "name": "Новый ноутбук",
        "emoji": "💻",
        "cost": 2000,
        "effect": "income_multiplier",
        "value": 1.5,
        "duration": -1,  # Постоянный эффект
        "description": "Доход от офисной работы +50%"
    },
    "scooter": {
        "name": "Электросамокат",
        "emoji": "🛴",
        "cost": 1500,
        "effect": "energy_efficiency",
        "value": 0.8,
        "duration": -1,
        "description": "Доставка тратит меньше энергии"
    },
    "course": {
        "name": "Онлайн-курс",
        "emoji": "📚",
        "cost": 1000,
        "effect": "unlock_job",
        "value": "freelance",
        "duration": -1,
        "description": "Открывает фриланс"
    }
}

# Глобальные цели
GLOBAL_GOALS = {
    "first_car": {
        "name": "Первая машина",
        "description": "Купи любую машину",
        "emoji": "🚗",
        "reward_money": 50000,
        "reward_description": "Бонус за первую машину: 50,000₽",
        "check_function": "has_any_car"
    },
    "luxury_car": {
        "name": "Премиум класс",
        "description": "Купи премиум автомобиль",
        "emoji": "🏎️",
        "reward_money": 100000,
        "reward_description": "Бонус за роскошь: 100,000₽",
        "check_function": "has_luxury_car"
    },
    "first_property": {
        "name": "Первая недвижимость",
        "description": "Купи любую недвижимость",
        "emoji": "🏠",
        "reward_money": 100000,
        "reward_description": "Бонус за первую недвижимость: 100,000₽",
        "check_function": "has_any_property"
    },
    "business_empire": {
        "name": "Бизнес-империя",
        "description": "Владей магазином и офисом одновременно",
        "emoji": "🏢",
        "reward_money": 500000,
        "reward_description": "Бонус за бизнес-империю: 500,000₽",
        "check_function": "has_business_empire"
    },
    "millionaire": {
        "name": "Миллионер",
        "description": "Накопи 1,000,000₽",
        "emoji": "💰",
        "reward_money": 200000,
        "reward_description": "Бонус за миллион: 200,000₽",
        "check_function": "is_millionaire"
    },
    "passive_income_king": {
        "name": "Король пассивного дохода",
        "description": "Получай 200,000₽/мес пассивного дохода",
        "emoji": "👑",
        "reward_money": 1000000,
        "reward_description": "Бонус за пассивный доход: 1,000,000₽",
        "check_function": "has_high_passive_income"
    },
    "debt_free": {
        "name": "Без долгов",
        "description": "Погаси все кредиты",
        "emoji": "🆓",
        "reward_money": 150000,
        "reward_description": "Бонус за свободу от долгов: 150,000₽",
        "check_function": "is_debt_free"
    },
    "collector": {
        "name": "Коллекционер",
        "description": "Владей всеми типами машин",
        "emoji": "🏆",
        "reward_money": 300000,
        "reward_description": "Бонус за коллекцию: 300,000₽",
        "check_function": "has_all_cars"
    },
    "real_estate_mogul": {
        "name": "Магнат недвижимости",
        "description": "Владей всеми типами недвижимости",
        "emoji": "🌟",
        "reward_money": 750000,
        "reward_description": "Бонус за недвижимость: 750,000₽",
        "check_function": "has_all_properties"
    },
    "ultimate_goal": {
        "name": "Финансовая свобода",
        "description": "Выполни все остальные цели",
        "emoji": "🎯",
        "reward_money": 2000000,
        "reward_description": "Главный приз: 2,000,000₽ + особый статус",
        "check_function": "has_completed_all_goals"
    }
}

# Машины
CARS = {
    "old_car": {
        "name": "Старая машина",
        "emoji": "🚗",
        "price": 150000,
        "monthly_cost": 8000,  # Бензин, страховка, ТО
        "income_bonus": 0.1,   # +10% к доходу от доставки
        "description": "Дешевая, но надежная"
    },
    "new_car": {
        "name": "Новая машина",
        "emoji": "🚙",
        "price": 800000,
        "monthly_cost": 15000,
        "income_bonus": 0.2,   # +20% к доходу от доставки
        "description": "Комфорт и статус"
    },
    "luxury_car": {
        "name": "Премиум авто",
        "emoji": "🏎️",
        "price": 2500000,
        "monthly_cost": 35000,
        "income_bonus": 0.3,   # +30% к доходу от доставки
        "description": "Для успешных людей"
    }
}

# Недвижимость
REAL_ESTATE = {
    # Жилая недвижимость
    "studio": {
        "name": "Студия",
        "emoji": "🏠",
        "price": 3000000,
        "type": "residential",
        "monthly_income": 0,
        "monthly_cost": -5000,  # Экономия на аренде
        "description": "Своя крыша над головой"
    },
    "apartment": {
        "name": "Квартира",
        "emoji": "🏡",
        "price": 8000000,
        "type": "residential", 
        "monthly_income": 25000,  # Сдача в аренду
        "monthly_cost": -8000,    # Экономия на аренде
        "description": "Можно сдавать в аренду"
    },
    "house": {
        "name": "Дом",
        "emoji": "🏘️",
        "price": 15000000,
        "type": "residential",
        "monthly_income": 50000,
        "monthly_cost": -12000,
        "description": "Престиж и доход"
    },
    
    # Коммерческая недвижимость
    "shop": {
        "name": "Магазин",
        "emoji": "🏪",
        "price": 5000000,
        "type": "commercial",
        "monthly_income": 80000,
        "monthly_cost": 20000,   # Расходы на содержание
        "description": "Стабильный бизнес"
    },
    "office": {
        "name": "Офис",
        "emoji": "🏢",
        "price": 12000000,
        "type": "commercial",
        "monthly_income": 150000,
        "monthly_cost": 40000,
        "description": "Сдача офисных помещений"
    },
    "warehouse": {
        "name": "Склад",
        "emoji": "🏭",
        "price": 20000000,
        "type": "commercial",
        "monthly_income": 200000,
        "monthly_cost": 50000,
        "description": "Логистический бизнес"
    }
}

# Типы кредитов
CREDIT_TYPES = {
    "car_loan": {
        "name": "Автокредит",
        "rate": 0.12,  # 12% годовых
        "max_term": 60,  # 5 лет
        "min_down_payment": 0.2,  # 20% первоначальный взнос
        "description": "Специальные условия для авто"
    },
    "mortgage": {
        "name": "Ипотека",
        "rate": 0.08,  # 8% годовых
        "max_term": 300,  # 25 лет
        "min_down_payment": 0.3,  # 30% первоначальный взнос
        "description": "Льготная ставка для недвижимости"
    },
    "consumer_loan": {
        "name": "Потребительский кредит",
        "rate": 0.18,  # 18% годовых
        "max_term": 60,  # 5 лет
        "min_down_payment": 0.0,  # Без первоначального взноса
        "description": "Быстрое оформление, высокая ставка"
    }
}

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/simple')
def simple():
    return render_template('simple.html')

@app.route('/full')
def full():
    return render_template('index.html')

@app.route('/design')
def design():
    return render_template('game_design.html')

@app.route('/api/user/<user_id>')
def get_user(user_id):
    """Получить данные пользователя"""
    # Сначала проверяем кэш в памяти
    if user_id not in users_data:
        # Пытаемся загрузить из БД
        db_data = load_user_data(user_id)
        if db_data:
            users_data[user_id] = db_data
        else:
            # Создаем нового пользователя
            users_data[user_id] = {
                'money': 500,  # Стартовые деньги
                'day': 1,      # Текущий день
                'max_days': 30, # До зарплаты
                'energy': 100,
                'max_energy': 100,
                'money_per_work': 50,  # За одно нажатие "работать"
                'last_event': None,
                'last_event_time': 0,
                'salary': 25000,  # Зарплата в конце месяца
                'trait': None,    # Черта личности
                'trait_selected': False,  # Выбрана ли черта
                'current_job': 'delivery',  # Текущая работа
                'unlocked_jobs': ['delivery'],  # Открытые работы
                'boosters': {},  # Активные бустеры {booster_id: days_left}
                'owned_items': [],  # Купленные предметы
                'cars': [],  # Купленные машины
                'real_estate': [],  # Купленная недвижимость
                'credits': [],  # Активные кредиты
                'monthly_income': 0,  # Пассивный доход
                'monthly_expenses': 0,  # Ежемесячные расходы
                'completed_goals': [],  # Выполненные цели
                'total_goals_completed': 0,  # Счетчик выполненных целей
                'worked_today': False,  # Работал ли сегодня
                'mood': 50,  # Настроение (0-100)
                'total_earned': 0,  # Всего заработано
                'total_spent': 0,  # Всего потрачено
                'work_count': 0,  # Сколько раз работал
                'health': 100,  # Здоровье (0-100)
                'skills': {  # Навыки
                    'speed': 1,  # Скорость (меньше энергии на работу)
                    'luck': 1,  # Удача (больше шанс позитивных событий)
                    'charisma': 1,  # Харизма (больше доход)
                    'intelligence': 1  # Интеллект (быстрее прокачка)
                },
                'skill_points': 0,  # Очки навыков
                'rest_count': 0,  # Сколько раз отдыхал сегодня
                'had_credits': False  # Брал ли когда-либо кредиты
            }
            # Сохраняем нового пользователя в БД
            save_user_data(user_id, users_data[user_id])
    
    return jsonify(users_data[user_id])

@app.route('/api/reset/<user_id>', methods=['POST'])
def reset_user(user_id):
    """Сбросить данные пользователя (начать заново)"""
    if user_id in users_data:
        del users_data[user_id]
    return jsonify({"message": "User data reset successfully"})

@app.route('/api/jobs')
def get_jobs():
    """Получить список доступных работ"""
    return jsonify(JOBS)

@app.route('/api/boosters')
def get_boosters():
    """Получить список доступных бустеров"""
    return jsonify(BOOSTERS)

@app.route('/api/cars')
def get_cars():
    """Получить список доступных машин"""
    return jsonify(CARS)

@app.route('/api/real_estate')
def get_real_estate():
    """Получить список доступной недвижимости"""
    return jsonify(REAL_ESTATE)

@app.route('/api/credit_types')
def get_credit_types():
    """Получить типы кредитов"""
    return jsonify(CREDIT_TYPES)

@app.route('/api/goals')
def get_goals():
    """Получить список глобальных целей"""
    return jsonify(GLOBAL_GOALS)

@app.route('/api/check_goals', methods=['POST'])
def check_goals():
    """Проверить и выполнить цели пользователя"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    newly_completed = check_and_complete_goals(user)
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'newly_completed_goals': newly_completed
    })

@app.route('/api/change_job', methods=['POST'])
def change_job():
    """Сменить текущую работу"""
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
        
    if job_id not in JOBS:
        return jsonify({"error": "Invalid job"}), 400
        
    user = users_data[user_id]
    
    # Проверяем, открыта ли работа
    if job_id not in user.get('unlocked_jobs', []):
        return jsonify({"error": "Job not unlocked"}), 400
        
    user['current_job'] = job_id
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'job': JOBS[job_id]
    })

@app.route('/api/buy_booster', methods=['POST'])
def buy_booster():
    """Купить бустер"""
    data = request.json
    user_id = data.get('user_id')
    booster_id = data.get('booster_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
        
    if booster_id not in BOOSTERS:
        return jsonify({"error": "Invalid booster"}), 400
        
    user = users_data[user_id]
    booster = BOOSTERS[booster_id]
    
    # Применяем скидку для черты "Экономный"
    cost = booster['cost']
    if user.get('trait') == 'экономный':
        trait_data = TRAITS['экономный']
        cost = int(cost * (1 - trait_data['cost_reduction']))
    
    # Проверяем деньги
    if user['money'] < cost:
        return jsonify({"error": "Not enough money"}), 400
        
    # Покупаем
    user['money'] -= cost
    
    # Применяем эффект
    if booster['effect'] == 'energy':
        user['energy'] = min(user['max_energy'], user['energy'] + booster['value'])
    elif booster['effect'] == 'unlock_job':
        job_to_unlock = booster['value']
        if 'unlocked_jobs' not in user:
            user['unlocked_jobs'] = []
        if job_to_unlock not in user['unlocked_jobs']:
            user['unlocked_jobs'].append(job_to_unlock)
    elif booster['duration'] == -1:  # Постоянный предмет
        if 'owned_items' not in user:
            user['owned_items'] = []
        if booster_id not in user['owned_items']:
            user['owned_items'].append(booster_id)
    else:  # Временный бустер
        if 'boosters' not in user:
            user['boosters'] = {}
        user['boosters'][booster_id] = booster['duration']
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'booster': booster,
        'cost': cost
    })

def calculate_monthly_payment(principal, rate, term_months):
    """Рассчитать ежемесячный платеж по кредиту"""
    if rate == 0:
        return principal / term_months
    
    monthly_rate = rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
    return int(payment)

def check_goal_completion(user, goal_id):
    """Проверить выполнение цели"""
    if goal_id in user.get('completed_goals', []):
        return False  # Уже выполнена
    
    goal = GLOBAL_GOALS.get(goal_id)
    if not goal:
        return False
    
    check_function = goal['check_function']
    
    if check_function == 'has_any_car':
        return len(user.get('cars', [])) > 0
    
    elif check_function == 'has_luxury_car':
        return 'luxury_car' in user.get('cars', [])
    
    elif check_function == 'has_any_property':
        return len(user.get('real_estate', [])) > 0
    
    elif check_function == 'has_business_empire':
        properties = user.get('real_estate', [])
        return 'shop' in properties and 'office' in properties
    
    elif check_function == 'is_millionaire':
        return user.get('money', 0) >= 1000000
    
    elif check_function == 'has_high_passive_income':
        # Рассчитываем пассивный доход
        passive_income = 0
        for property_id in user.get('real_estate', []):
            if property_id in REAL_ESTATE:
                passive_income += REAL_ESTATE[property_id]['monthly_income']
        return passive_income >= 200000
    
    elif check_function == 'is_debt_free':
        # Цель выполняется только если были кредиты раньше
        # Проверяем: нет кредитов сейчас И были кредиты раньше
        has_no_credits = len(user.get('credits', [])) == 0
        had_credits_before = user.get('had_credits', False)  # Флаг что были кредиты
        return has_no_credits and had_credits_before and user.get('money', 0) > 0
    
    elif check_function == 'has_all_cars':
        user_cars = set(user.get('cars', []))
        all_cars = set(CARS.keys())
        return user_cars >= all_cars
    
    elif check_function == 'has_all_properties':
        user_properties = set(user.get('real_estate', []))
        all_properties = set(REAL_ESTATE.keys())
        return user_properties >= all_properties
    
    elif check_function == 'has_completed_all_goals':
        completed = len(user.get('completed_goals', []))
        total_goals = len(GLOBAL_GOALS) - 1  # Исключаем саму эту цель
        return completed >= total_goals
    
    return False

def check_and_complete_goals(user):
    """Проверить и выполнить все возможные цели"""
    newly_completed = []
    
    # Инициализируем список выполненных целей если его нет
    if 'completed_goals' not in user:
        user['completed_goals'] = []
    
    for goal_id in GLOBAL_GOALS.keys():
        # ВАЖНО: Проверяем, что цель еще НЕ выполнена
        if goal_id not in user['completed_goals'] and check_goal_completion(user, goal_id):
            goal = GLOBAL_GOALS[goal_id]
            
            # Добавляем в выполненные
            user['completed_goals'].append(goal_id)
            
            # Даем награду
            user['money'] += goal['reward_money']
            user['total_goals_completed'] = len(user['completed_goals'])
            
            newly_completed.append({
                'id': goal_id,
                'name': goal['name'],
                'emoji': goal['emoji'],
                'reward_description': goal['reward_description']
            })
    
    return newly_completed

@app.route('/api/buy_car', methods=['POST'])
def buy_car():
    """Купить машину"""
    data = request.json
    user_id = data.get('user_id')
    car_id = data.get('car_id')
    payment_type = data.get('payment_type', 'cash')  # cash, credit
    down_payment = data.get('down_payment', 0)
    term_months = data.get('term_months', 12)
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
        
    if car_id not in CARS:
        return jsonify({"error": "Invalid car"}), 400
        
    user = users_data[user_id]
    car = CARS[car_id]
    
    # Проверяем, есть ли уже такая машина
    if car_id in user.get('cars', []):
        return jsonify({"error": "Car already owned"}), 400
    
    if payment_type == 'cash':
        # Покупка за наличные
        cost = car['price']
        
        # Применяем скидку для черты "Экономный"
        if user.get('trait') == 'экономный':
            cost = int(cost * 0.9)
            
        if user['money'] < cost:
            return jsonify({"error": "Not enough money"}), 400
            
        user['money'] -= cost
        if 'cars' not in user:
            user['cars'] = []
        user['cars'].append(car_id)
        user['monthly_expenses'] += car['monthly_cost']
        
        # Проверяем выполнение целей
        newly_completed_goals = check_and_complete_goals(user)
        
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'car': car,
            'cost': cost,
            'payment_type': 'cash',
            'newly_completed_goals': newly_completed_goals
        })
        
    elif payment_type == 'credit':
        # Покупка в кредит
        credit_type = CREDIT_TYPES['car_loan']
        min_down = int(car['price'] * credit_type['min_down_payment'])
        
        if down_payment < min_down:
            return jsonify({"error": f"Minimum down payment: {min_down}₽"}), 400
            
        if user['money'] < down_payment:
            return jsonify({"error": "Not enough money for down payment"}), 400
            
        if term_months > credit_type['max_term']:
            return jsonify({"error": f"Maximum term: {credit_type['max_term']} months"}), 400
            
        # Рассчитываем кредит
        loan_amount = car['price'] - down_payment
        monthly_payment = calculate_monthly_payment(loan_amount, credit_type['rate'], term_months)
        
        # Применяем скидку для черты "Экономный"
        if user.get('trait') == 'экономный':
            down_payment = int(down_payment * 0.9)
            
        user['money'] -= down_payment
        if 'cars' not in user:
            user['cars'] = []
        user['cars'].append(car_id)
        user['monthly_expenses'] += car['monthly_cost'] + monthly_payment
        
        # Добавляем кредит
        credit = {
            'id': f"car_{car_id}_{len(user.get('credits', []))}",
            'type': 'car_loan',
            'item': car_id,
            'principal': loan_amount,
            'monthly_payment': monthly_payment,
            'remaining_months': term_months,
            'rate': credit_type['rate']
        }
        
        if 'credits' not in user:
            user['credits'] = []
        user['credits'].append(credit)
        
        # Устанавливаем флаг что были кредиты (для цели "Без долгов")
        user['had_credits'] = True
        
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'car': car,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'payment_type': 'credit',
            'credit': credit
        })

@app.route('/api/buy_real_estate', methods=['POST'])
def buy_real_estate():
    """Купить недвижимость"""
    data = request.json
    user_id = data.get('user_id')
    property_id = data.get('property_id')
    payment_type = data.get('payment_type', 'cash')
    down_payment = data.get('down_payment', 0)
    term_months = data.get('term_months', 240)  # 20 лет по умолчанию
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
        
    if property_id not in REAL_ESTATE:
        return jsonify({"error": "Invalid property"}), 400
        
    user = users_data[user_id]
    property_data = REAL_ESTATE[property_id]
    
    # Проверяем, есть ли уже такая недвижимость
    if property_id in user.get('real_estate', []):
        return jsonify({"error": "Property already owned"}), 400
    
    if payment_type == 'cash':
        # Покупка за наличные
        cost = property_data['price']
        
        # Применяем скидку для черты "Экономный"
        if user.get('trait') == 'экономный':
            cost = int(cost * 0.9)
            
        if user['money'] < cost:
            return jsonify({"error": "Not enough money"}), 400
            
        user['money'] -= cost
        if 'real_estate' not in user:
            user['real_estate'] = []
        user['real_estate'].append(property_id)
        user['monthly_income'] += property_data['monthly_income']
        user['monthly_expenses'] += abs(property_data['monthly_cost'])
        
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'property': property_data,
            'cost': cost,
            'payment_type': 'cash'
        })
        
    elif payment_type == 'mortgage':
        # Покупка в ипотеку
        credit_type = CREDIT_TYPES['mortgage']
        min_down = int(property_data['price'] * credit_type['min_down_payment'])
        
        if down_payment < min_down:
            return jsonify({"error": f"Minimum down payment: {min_down}₽"}), 400
            
        if user['money'] < down_payment:
            return jsonify({"error": "Not enough money for down payment"}), 400
            
        if term_months > credit_type['max_term']:
            return jsonify({"error": f"Maximum term: {credit_type['max_term']} months"}), 400
            
        # Рассчитываем ипотеку
        loan_amount = property_data['price'] - down_payment
        monthly_payment = calculate_monthly_payment(loan_amount, credit_type['rate'], term_months)
        
        # Применяем скидку для черты "Экономный"
        if user.get('trait') == 'экономный':
            down_payment = int(down_payment * 0.9)
            
        user['money'] -= down_payment
        if 'real_estate' not in user:
            user['real_estate'] = []
        user['real_estate'].append(property_id)
        user['monthly_income'] += property_data['monthly_income']
        user['monthly_expenses'] += abs(property_data['monthly_cost']) + monthly_payment
        
        # Добавляем ипотеку
        credit = {
            'id': f"property_{property_id}_{len(user.get('credits', []))}",
            'type': 'mortgage',
            'item': property_id,
            'principal': loan_amount,
            'monthly_payment': monthly_payment,
            'remaining_months': term_months,
            'rate': credit_type['rate']
        }
        
        if 'credits' not in user:
            user['credits'] = []
        user['credits'].append(credit)
        
        # Устанавливаем флаг что были кредиты (для цели "Без долгов")
        user['had_credits'] = True
        
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'property': property_data,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'payment_type': 'mortgage',
            'credit': credit
        })

@app.route('/api/traits')
def get_traits():
    """Получить список доступных черт личности"""
    return jsonify(TRAITS)

@app.route('/api/select_trait', methods=['POST'])
def select_trait():
    """Выбрать черту личности"""
    data = request.json
    user_id = data.get('user_id')
    trait_id = data.get('trait_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
        
    if trait_id not in TRAITS:
        return jsonify({"error": "Invalid trait"}), 400
        
    user = users_data[user_id]
    if user['trait_selected']:
        return jsonify({"error": "Trait already selected"}), 400
        
    user['trait'] = trait_id
    user['trait_selected'] = True
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'trait': TRAITS[trait_id]
    })

@app.route('/api/buy_food', methods=['POST'])
def buy_food():
    """Купить еду - восстанавливает настроение"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    cost = 200
    
    if user['money'] < cost:
        return jsonify({"error": "Недостаточно денег!"}), 400
    
    user['money'] -= cost
    user['mood'] = min(100, user.get('mood', 50) + 10)
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'message': 'Вкусно поел! +10 настроения'
    })

@app.route('/api/take_rest', methods=['POST'])
def take_rest():
    """Отдохнуть - восстанавливает энергию и настроение"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    # Проверяем сколько раз уже отдыхал сегодня
    rest_count = user.get('rest_count_today', 0)
    if rest_count >= 2:
        return jsonify({"error": "Уже отдыхал 2 раза сегодня! Хватит лениться!"}), 400
    
    user['energy'] = min(user['max_energy'], user['energy'] + 20)
    user['mood'] = min(100, user.get('mood', 50) + 5)
    user['rest_count_today'] = rest_count + 1
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'message': f'Отдохнул! +20 энергии, +5 настроения ({2 - user["rest_count_today"]} раз осталось)'
    })

@app.route('/api/random_event', methods=['POST'])
def random_event():
    """Случайное событие в течение дня"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    # Выбираем случайное событие
    event = random.choice(EVENTS)
    event_cost = event['cost']
    mood_change = event.get('mood', 0)
    
    # Применяем эффекты черт
    if user.get('trait') == 'терпила' and event_cost < 0:
        event_cost = int(event_cost * 0.8)
    if user.get('trait') == 'экономный' and event_cost < 0:
        event_cost = int(event_cost * 0.9)
    if user.get('trait') == 'рисковый' and event_cost < 0:
        event_cost = int(event_cost * 1.5)
    
    user['money'] += event_cost
    user['mood'] = max(0, min(100, user.get('mood', 50) + mood_change))
    
    if user['money'] < 0:
        user['money'] = 0
    
    message = event['emoji'] + ' ' + event['text']
    if event_cost != 0:
        message += ' ' + ('+' if event_cost > 0 else '') + str(event_cost) + '₽'
    if mood_change != 0:
        message += ' ' + ('+' if mood_change > 0 else '') + str(mood_change) + ' настроения'
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'event': event,
        'message': message
    })

@app.route('/api/play_roulette', methods=['POST'])
def play_roulette():
    """Сыграть в рулетку"""
    data = request.json
    user_id = data.get('user_id')
    bet = data.get('bet', 100)
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    if user['money'] < bet:
        return jsonify({"error": "Недостаточно денег!"}), 400
    
    # Вычитаем ставку
    user['money'] -= bet
    
    # Крутим рулетку
    rand = random.random()
    if rand < 0.4:  # 40% шанс - проигрыш
        multiplier = 0
        result_emoji = '😭'
        message = f'Проиграл! -{bet}₽'
    elif rand < 0.7:  # 30% шанс - x2
        multiplier = 2
        result_emoji = '🙂'
        win = bet * multiplier
        user['money'] += win
        message = f'Выиграл x2! +{win}₽'
    elif rand < 0.9:  # 20% шанс - x5
        multiplier = 5
        result_emoji = '😄'
        win = bet * multiplier
        user['money'] += win
        message = f'Выиграл x5! +{win}₽'
    else:  # 10% шанс - x10
        multiplier = 10
        result_emoji = '🤑'
        win = bet * multiplier
        user['money'] += win
        message = f'ДЖЕКПОТ x10! +{win}₽'
    
    # Настроение меняется
    if multiplier == 0:
        user['mood'] = max(0, user.get('mood', 50) - 10)
    elif multiplier >= 5:
        user['mood'] = min(100, user.get('mood', 50) + 15)
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'multiplier': multiplier,
        'result_emoji': result_emoji,
        'message': message
    })

@app.route('/api/upgrade_skill', methods=['POST'])
def upgrade_skill():
    """Прокачать навык"""
    data = request.json
    user_id = data.get('user_id')
    skill = data.get('skill')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    if 'skills' not in user:
        user['skills'] = {'speed': 1, 'luck': 1, 'charisma': 1, 'intelligence': 1}
    
    if skill not in user['skills']:
        return jsonify({"error": "Invalid skill"}), 400
    
    skill_points = user.get('skill_points', 0)
    if skill_points < 1:
        return jsonify({"error": "Недостаточно очков навыков!"}), 400
    
    current_level = user['skills'][skill]
    if current_level >= 10:
        return jsonify({"error": "Максимальный уровень!"}), 400
    
    user['skills'][skill] += 1
    user['skill_points'] -= 1
    
    skill_names = {
        'speed': '🏃 Скорость',
        'luck': '🍀 Удача',
        'charisma': '💬 Харизма',
        'intelligence': '🧠 Интеллект'
    }
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'message': f'{skill_names[skill]} повышена до уровня {user["skills"][skill]}!'
    })

@app.route('/api/work', methods=['POST'])
def work():
    """Обработка нажатия кнопки РАБОТАТЬ"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    # Проверяем энергию
    if user['energy'] <= 0:
        return jsonify({"error": "Нет энергии!"}), 400
    
    # Получаем данные о текущей работе
    current_job_id = user.get('current_job', 'delivery')
    if current_job_id not in JOBS:
        current_job_id = 'delivery'
        user['current_job'] = current_job_id
        
    job = JOBS[current_job_id]
    
    # Базовый доход и трата энергии
    income = job['base_income']
    energy_cost = job['energy_cost']
    
    # Применяем эффекты бустеров
    if 'laptop' in user.get('owned_items', []) and current_job_id == 'office':
        income = int(income * BOOSTERS['laptop']['value'])
        
    if 'scooter' in user.get('owned_items', []) and current_job_id == 'delivery':
        energy_cost = int(energy_cost * BOOSTERS['scooter']['value'])
    
    # Применяем бонусы от машин для доставки
    if current_job_id == 'delivery' and user.get('cars'):
        car_bonus = 0
        for car_id in user['cars']:
            if car_id in CARS:
                car_bonus += CARS[car_id]['income_bonus']
        income = int(income * (1 + car_bonus))
    
    # Применяем эффект черты "Терпила" - снижение дохода
    if user.get('trait') == 'терпила':
        trait_data = TRAITS['терпила']
        income = int(income * (1 - trait_data['income_reduction']))
    
    # Применяем модификатор настроения
    mood = user.get('mood', 50)
    mood_modifier = 1.0
    if mood <= 20:
        mood_modifier = 0.7  # -30% при депрессии
    elif mood <= 40:
        mood_modifier = 0.85  # -15% когда грустно
    elif mood <= 60:
        mood_modifier = 1.0  # 0% нормально
    elif mood <= 80:
        mood_modifier = 1.1  # +10% когда хорошо
    else:
        mood_modifier = 1.25  # +25% когда отлично
    
    income = int(income * mood_modifier)
    
    # Проверяем достаточно ли энергии
    if user['energy'] < energy_cost:
        return jsonify({"error": "Недостаточно энергии!"}), 400
    
    # Работаем
    user['money'] += income
    user['energy'] -= energy_cost
    user['worked_today'] = True  # Отмечаем что работал сегодня
    user['total_earned'] = user.get('total_earned', 0) + income
    user['work_count'] = user.get('work_count', 0) + 1
    
    # Даем очки навыков (1 очко за 5 работ)
    if user['work_count'] % 5 == 0:
        intelligence_bonus = 1 + (user.get('skills', {}).get('intelligence', 1) - 1) * 0.1
        skill_points_earned = int(1 * intelligence_bonus)
        user['skill_points'] = user.get('skill_points', 0) + skill_points_earned
        # Сообщим игроку
        newly_earned_skill_point = True
    else:
        newly_earned_skill_point = False
    
    # Настроение немного падает от работы
    user['mood'] = max(0, user.get('mood', 50) - 2)
    
    # Здоровье падает от работы
    user['health'] = max(0, user.get('health', 100) - 1)
    
    # Определяем шанс события
    event_chance = 0.2  # Базовый шанс 20%
    
    # Применяем эффект черты "Рисковый" - увеличение шанса событий
    if user.get('trait') == 'рисковый':
        trait_data = TRAITS['рисковый']
        event_chance += trait_data['event_chance_bonus']
    
    # Случайное событие
    event = None
    current_time = time.time()
    if (random.random() < event_chance and 
        current_time - user['last_event_time'] > 30):  # Минимум 30 сек между событиями
        
        event = random.choice(EVENTS)
        event_cost = event['cost']
        
        # Применяем эффект черты "Терпила" - снижение штрафов
        if user.get('trait') == 'терпила' and event_cost < 0:
            trait_data = TRAITS['терпила']
            event_cost = int(event_cost * (1 - trait_data['penalty_reduction']))
            
        # Применяем эффект черты "Экономный" - снижение трат
        if user.get('trait') == 'экономный' and event_cost < 0:
            trait_data = TRAITS['экономный']
            event_cost = int(event_cost * (1 - trait_data['cost_reduction']))
            
        # Применяем эффект черты "Рисковый" - больше негативных событий
        if user.get('trait') == 'рисковый' and event_cost < 0:
            trait_data = TRAITS['рисковый']
            event_cost = int(event_cost * trait_data['negative_event_multiplier'])
            if random.random() < 0.3:  # 30% шанс усилить негативное событие
                event_cost = int(event_cost * trait_data['negative_event_multiplier'])
        
        user['money'] += event_cost
        event['cost'] = event_cost  # Обновляем стоимость для отображения
        
        # Применяем изменение настроения от события
        mood_change = event.get('mood', 0)
        user['mood'] = max(0, min(100, user.get('mood', 50) + mood_change))
        
        user['last_event'] = event
        user['last_event_time'] = current_time
        
        # Не даем деньгам уйти в минус
        if user['money'] < 0:
            user['money'] = 0
    
    # Проверяем выполнение целей
    newly_completed_goals = check_and_complete_goals(user)
    
    # Сохраняем изменения в БД
    save_user_data(user_id, user)
    
    return jsonify({
        'user': user,
        'event': event,
        'income': income,
        'job': job,
        'newly_completed_goals': newly_completed_goals,
        'skill_point_earned': newly_earned_skill_point
    })

@app.route('/api/next_day', methods=['POST'])
def next_day():
    """Переход к следующему дню"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        return jsonify({"error": "User not found"}), 404
    
    user = users_data[user_id]
    
    # Сбрасываем флаг работы (если был)
    user['worked_today'] = False
    user['rest_count_today'] = 0  # Сбрасываем счетчик отдыха
    
    # Проверяем черту "Прокрастинатор" - иногда день проходит без действий
    day_skipped = False
    if user.get('trait') == 'прокрастинатор':
        trait_data = TRAITS['прокрастинатор']
        if random.random() < trait_data['skip_day_chance']:
            day_skipped = True
            # Усталость не растёт в пропущенный день
            user['energy'] = user['max_energy']
            user['day'] += 1
            # Сохраняем изменения в БД
            save_user_data(user_id, user)
            return jsonify({
                'user': user,
                'day_skipped': True,
                'message': "Прокрастинировал весь день... Но хотя бы отдохнул! 😴"
            })
    
    # Обновляем бустеры
    expired_boosters = []
    for booster_id, days_left in user.get('boosters', {}).items():
        if days_left > 0:
            user['boosters'][booster_id] = days_left - 1
            if user['boosters'][booster_id] <= 0:
                expired_boosters.append(booster_id)
    
    # Удаляем истёкшие бустеры
    for booster_id in expired_boosters:
        del user['boosters'][booster_id]
    
    # Открываем новые работы по дням
    new_jobs = []
    if 'unlocked_jobs' not in user:
        user['unlocked_jobs'] = []
    for job_id, job_data in JOBS.items():
        if (user['day'] >= job_data['unlock_day'] and 
            job_id not in user['unlocked_jobs']):
            user['unlocked_jobs'].append(job_id)
            new_jobs.append(job_data)
    
    if user['day'] >= user['max_days']:
        # Получаем зарплату!
        user['money'] += user['salary']
        user['day'] = 1
        user['energy'] = user['max_energy']
        
        # Проверяем выполнение целей
        newly_completed_goals = check_and_complete_goals(user)
        
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'salary_received': True,
            'message': f"Поздравляем! Получена зарплата {user['salary']}₽",
            'new_jobs': new_jobs,
            'newly_completed_goals': newly_completed_goals
        })
    else:
        user['day'] += 1
        user['energy'] = user['max_energy']  # Восстанавливаем энергию
        
        # Ежемесячные расходы и доходы (в начале каждого месяца - каждые 30 дней)
        passive_income = 0
        monthly_expenses = 0
        
        if user['day'] % 30 == 1:  # Первый день месяца
            # Пассивный доход от недвижимости
            for property_id in user.get('real_estate', []):
                if property_id in REAL_ESTATE:
                    passive_income += REAL_ESTATE[property_id]['monthly_income']
            
            # Расходы на машины
            for car_id in user.get('cars', []):
                if car_id in CARS:
                    monthly_expenses += CARS[car_id]['monthly_cost']
            
            # Расходы на недвижимость
            for property_id in user.get('real_estate', []):
                if property_id in REAL_ESTATE:
                    monthly_expenses += abs(REAL_ESTATE[property_id]['monthly_cost'])
            
            # Платежи по кредитам
            expired_credits = []
            for i, credit in enumerate(user.get('credits', [])):
                monthly_expenses += credit['monthly_payment']
                credit['remaining_months'] -= 1
                
                if credit['remaining_months'] <= 0:
                    expired_credits.append(i)
            
            # Удаляем погашенные кредиты
            for i in reversed(expired_credits):
                user['credits'].pop(i)
            
            # Применяем пассивный доход и расходы
            user['money'] += passive_income - monthly_expenses
        
        # Ежедневные траты (еда, транспорт)
        daily_cost = random.randint(200, 500)
        
        # Применяем эффект черты "Экономный" - снижение трат
        if user.get('trait') == 'экономный':
            trait_data = TRAITS['экономный']
            daily_cost = int(daily_cost * (1 - trait_data['cost_reduction']))
            
        user['money'] -= daily_cost
        if user['money'] < 0:
            user['money'] = 0
            
        message = f"Потрачено на жизнь: {daily_cost}₽"
        
        # Добавляем информацию о пассивном доходе
        if passive_income > 0:
            message += f"\n💰 Пассивный доход: +{passive_income}₽"
        if monthly_expenses > 0 and user['day'] % 30 == 1:
            message += f"\n💸 Ежемесячные расходы: -{monthly_expenses}₽"
            
        if new_jobs:
            job_names = [job['name'] for job in new_jobs]
            message += f"\n🎉 Открыты новые работы: {', '.join(job_names)}"
            
        # Сохраняем изменения в БД
        save_user_data(user_id, user)
        
        return jsonify({
            'user': user,
            'daily_cost': daily_cost,
            'passive_income': passive_income if user['day'] % 30 == 1 else 0,
            'monthly_expenses': monthly_expenses if user['day'] % 30 == 1 else 0,
            'message': message,
            'new_jobs': new_jobs,
            'expired_boosters': expired_boosters
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)