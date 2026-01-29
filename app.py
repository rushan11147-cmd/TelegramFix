from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
import json
import random
import time
import sqlite3
from threading import Lock, Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import hmac
import hashlib
import urllib.parse
import logging

# Import business system
from business_system import (
    BusinessManager, BusinessRepository, BusinessType, EmployeeType,
    UpgradeType, EventType, BUSINESS_CONFIGS, EMPLOYEE_CONFIGS,
    UPGRADE_CONFIGS, EVENT_CONFIGS
)

# Import side jobs system
from side_jobs_system import SideJobManager
from side_jobs_config import SIDE_JOBS, CATEGORIES

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS - только для Telegram
CORS(app, origins=[
    "https://telegramfix.onrender.com",
    "https://telegram.org",
    "http://localhost:5000"  # Для разработки
])

# Rate Limiting
def get_rate_limit_key():
    """Безопасное получение ключа для rate limiting"""
    try:
        data = request.get_json(silent=True)
        if data and 'user_id' in data:
            return data['user_id']
    except:
        pass
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_rate_limit_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# База данных - поддержка PostgreSQL и SQLite
DATABASE_URL = os.getenv('DATABASE_URL')  # PostgreSQL URL от Render
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Render использует postgres://, но psycopg2 требует postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Если есть PostgreSQL - используем его, иначе SQLite
USE_POSTGRES = DATABASE_URL is not None
DB_PATH = os.getenv('DATABASE_PATH', 'game_data.db')  # Для SQLite
db_lock = Lock()

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info("Using PostgreSQL database")
else:
    logger.info("Using SQLite database")

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://telegramfix.onrender.com')

def verify_telegram_webapp_data(init_data_raw):
    """
    Проверка подлинности данных от Telegram WebApp
    Документация: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        # В режиме разработки (demo_user) пропускаем проверку
        if not init_data_raw or init_data_raw == 'demo':
            logger.warning("Skipping validation for demo user")
            return True
        
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not set")
            return False
        
        # Парсим init_data
        parsed_data = urllib.parse.parse_qs(init_data_raw)
        
        # Извлекаем hash
        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            logger.warning("No hash in init_data")
            return False
        
        # Создаем data_check_string (все параметры кроме hash, отсортированные)
        data_check_arr = []
        for key, value in sorted(parsed_data.items()):
            if key != 'hash':
                data_check_arr.append(f"{key}={value[0]}")
        data_check_string = '\n'.join(data_check_arr)
        
        # Вычисляем secret_key
        secret_key = hmac.new(
            "WebAppData".encode(),
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем
        is_valid = calculated_hash == received_hash
        
        if not is_valid:
            logger.warning(f"Invalid hash: expected {calculated_hash}, got {received_hash}")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating Telegram data: {e}")
        return False

def init_db():
    """Инициализация базы данных"""
    if USE_POSTGRES:
        # PostgreSQL
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_updated 
                ON users(last_updated)
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("PostgreSQL database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL: {e}")
            raise
    else:
        # SQLite
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_updated 
                ON users(last_updated)
            ''')
            conn.commit()
            logger.info(f"SQLite database initialized at {DB_PATH}")

def save_user_data(user_id, data):
    """Сохранение данных пользователя в БД"""
    with db_lock:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, data, last_updated)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE 
                SET data = EXCLUDED.data, last_updated = CURRENT_TIMESTAMP
            ''', (user_id, json.dumps(data)))
            conn.commit()
            cursor.close()
            conn.close()
        else:
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
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM users WHERE user_id = %s', (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return json.loads(row[0])
            return None
        else:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None

# Инициализируем БД при старте
init_db()

# Валидация user_id
import re

def validate_user_id(user_id):
    """Валидация user_id для защиты от инъекций"""
    if not user_id or not isinstance(user_id, str):
        return False
    if len(user_id) > 100:
        return False
    # Разрешаем только буквы, цифры, подчеркивание и дефис
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        return False
    return True

def clamp(value, min_val, max_val):
    """Ограничить значение в диапазоне"""
    return max(min_val, min(max_val, value))

def get_user_data_safe(user_id):
    """Получить данные пользователя - всегда из БД, без кэша"""
    # Валидация user_id
    if not validate_user_id(user_id):
        logger.warning(f"Invalid user_id: {user_id}")
        return None
    
    logger.info(f"Loading user data for: {user_id}")
    
    # Загружаем из БД
    db_data = load_user_data(user_id)
    if db_data:
        logger.info(f"User {user_id} found in DB - money: {db_data.get('money', 0)}, energy: {db_data.get('energy', 'NOT SET')}, trait: {db_data.get('trait', 'None')}")
        
        # МИГРАЦИЯ: Если energy не установлена, устанавливаем
        if 'energy' not in db_data:
            db_data['energy'] = 100
            logger.warning(f"MIGRATION: Added energy=100 for user {user_id}")
            save_user_data(user_id, db_data)
        
        # ИСПРАВЛЕНИЕ: Если max_energy не установлен или меньше 100, исправляем
        if 'max_energy' not in db_data or db_data['max_energy'] < 100:
            db_data['max_energy'] = 100
            logger.info(f"Fixed max_energy for user {user_id}")
            save_user_data(user_id, db_data)
        
        # Проверяем что деньги не отрицательные
        if db_data.get('money', 0) < 0:
            logger.error(f"User {user_id} has negative money: {db_data['money']}, fixing")
            db_data['money'] = 0
            save_user_data(user_id, db_data)
        
        return db_data
    else:
        # Создаем нового пользователя
        logger.info(f"Creating new user: {user_id}")
        new_user = {
            'player_name': None,
            'name_set': False,
            'tutorial_completed': False,
            'money': 500,
            'day': 1,
            'max_days': 30,
            'month': 1,
            'energy': 100,
            'max_energy': 100,
            'money_per_work': 50,
            'last_event': None,
            'last_event_time': 0,
            'salary': 25000,
            'trait': None,
            'trait_selected': False,
            'current_job': 'delivery',
            'unlocked_jobs': ['delivery'],
            'boosters': {},
            'owned_items': [],
            'cars': [],
            'real_estate': [],
            'credits': [],
            'monthly_income': 0,
            'monthly_expenses': 0,
            'completed_goals': [],
            'total_goals_completed': 0,
            'worked_today': False,
            'mood': 50,
            'total_earned': 0,
            'total_spent': 0,
            'work_count': 0,
            'health': 100,
            'skills': {
                'speed': 1,
                'luck': 1,
                'charisma': 1,
                'intelligence': 1
            },
            'skill_points': 0,
            'rest_count': 0,
            'had_credits': False
        }
        save_user_data(user_id, new_user)
        logger.info(f"Created new user: {user_id}")
        return new_user

def save_user_data_safe(user_id, user_data):
    """Сохранить данные пользователя с валидацией"""
    # Валидация user_id
    if not validate_user_id(user_id):
        logger.warning(f"Invalid user_id in save: {user_id}")
        return False
    
    logger.info(f"Saving user data for: {user_id} - money: {user_data.get('money', 0)}, trait: {user_data.get('trait', 'None')}")
    
    # Проверяем что деньги не отрицательные
    if user_data.get('money', 0) < 0:
        logger.error(f"Preventing negative money save for user {user_id}: {user_data['money']}")
        user_data['money'] = 0
    
    # Ограничиваем значения в допустимых диапазонах
    user_data['mood'] = clamp(user_data.get('mood', 50), 0, 100)
    user_data['health'] = clamp(user_data.get('health', 100), 0, 100)
    user_data['energy'] = clamp(user_data.get('energy', 100), 0, user_data.get('max_energy', 100))
    
    # Лимит на количество кредитов
    MAX_CREDITS = 10
    if len(user_data.get('credits', [])) > MAX_CREDITS:
        logger.warning(f"User {user_id} has too many credits: {len(user_data['credits'])}")
        user_data['credits'] = user_data['credits'][:MAX_CREDITS]
    
    save_user_data(user_id, user_data)
    logger.info(f"Successfully saved user data for: {user_id}")
    return True


# Инициализируем Business Manager после определения функций
business_repository = BusinessRepository(get_user_data_safe, save_user_data_safe)
business_manager = BusinessManager(business_repository)

# Инициализируем Side Jobs Manager
side_jobs_manager = SideJobManager(get_user_data_safe, save_user_data_safe)


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

@app.route('/health')
def health_check():
    """Health check endpoint для мониторинга"""
    try:
        # Проверяем доступность БД
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            conn.close()
        else:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'PostgreSQL' if USE_POSTGRES else 'SQLite',
            'timestamp': time.time()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

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

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test_simple')
def test_simple():
    return render_template('test_simple.html')

@app.route('/hello')
def hello():
    return render_template('hello.html')

@app.route('/business-test')
def business_test():
    return render_template('business_test.html')

@app.route('/test-button')
def test_button():
    return render_template('test_business_button.html')

@app.route('/api/user/<user_id>')
def get_user(user_id):
    """Получить данные пользователя"""
    try:
        user_data = get_user_data_safe(user_id)
        return jsonify(user_data)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/set_name', methods=['POST'])
@limiter.limit("5 per minute")
def set_player_name():
    """Установить имя игрока"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    player_name = data.get('player_name', '').strip()
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
    if not player_name or len(player_name) < 2:
        return jsonify({"error": "Имя должно быть минимум 2 символа"}), 400
    
    if len(player_name) > 20:
        return jsonify({"error": "Имя слишком длинное (макс 20 символов)"}), 400
    
    user['player_name'] = player_name
    user['name_set'] = True
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'success': True,
        'player_name': player_name,
        'message': f'Добро пожаловать, {player_name}!'
    })

@app.route('/api/complete_tutorial', methods=['POST'])
@limiter.limit("5 per minute")
def complete_tutorial():
    """Отметить гайд как пройденный"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
    user['tutorial_completed'] = True
    save_user_data_safe(user_id, user)
    
    return jsonify({'success': True})

@app.route('/api/leaderboard')
def get_leaderboard():
    """Получить таблицу лидеров"""
    try:
        with db_lock:
            if USE_POSTGRES:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, data FROM users
                    ORDER BY last_updated DESC
                    LIMIT 1000
                ''')
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
            else:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, data FROM users
                    ORDER BY last_updated DESC
                    LIMIT 1000
                ''')
                rows = cursor.fetchall()
                conn.close()
            
            players = []
            for row in rows:
                user_id, data_json = row
                try:
                    user_data = json.loads(data_json)
                    if user_data.get('name_set') and user_data.get('player_name'):
                        players.append({
                            'player_name': user_data['player_name'],
                            'money': user_data.get('money', 0),
                            'month': user_data.get('month', 1),
                            'total_earned': user_data.get('total_earned', 0),
                            'total_goals': user_data.get('total_goals_completed', 0)
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON for user {user_id}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")
                    continue
            
            players.sort(key=lambda x: x['money'], reverse=True)
            return jsonify(players[:50])
            
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({"error": "Failed to load leaderboard"}), 500

@app.route('/api/reset/<user_id>', methods=['POST'])
def reset_user(user_id):
    """Сбросить данные пользователя (начать заново)"""
    # Удаляем из БД
    with db_lock:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
    
    logger.info(f"User {user_id} data reset")
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
@limiter.limit("10 per minute")
def check_goals():
    """Проверить и выполнить цели пользователя"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    newly_completed = check_and_complete_goals(user)
    
    # Сохраняем изменения в БД
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'newly_completed_goals': newly_completed
    })

@app.route('/api/change_job', methods=['POST'])
@limiter.limit("10 per minute")
def change_job():
    """Сменить текущую работу"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
        
    if job_id not in JOBS:
        return jsonify({"error": "Invalid job"}), 400
    
    # Проверяем, открыта ли работа
    if job_id not in user.get('unlocked_jobs', []):
        return jsonify({"error": "Job not unlocked"}), 400
        
    user['current_job'] = job_id
    
    # Сохраняем изменения в БД
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'job': JOBS[job_id]
    })

@app.route('/api/buy_booster', methods=['POST'])
@limiter.limit("10 per minute")
def buy_booster():
    """Купить бустер"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    booster_id = data.get('booster_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
        
    if booster_id not in BOOSTERS:
        return jsonify({"error": "Invalid booster"}), 400
        
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
    save_user_data_safe(user_id, user)
    
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
@limiter.limit("10 per minute")
def buy_car():
    """Купить машину"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    car_id = data.get('car_id')
    payment_type = data.get('payment_type', 'cash')  # cash, credit
    down_payment = data.get('down_payment', 0)
    term_months = data.get('term_months', 12)
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
        
    if car_id not in CARS:
        return jsonify({"error": "Invalid car"}), 400
        
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
        save_user_data_safe(user_id, user)
        
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
        save_user_data_safe(user_id, user)
        
        return jsonify({
            'user': user,
            'car': car,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'payment_type': 'credit',
            'credit': credit
        })

@app.route('/api/buy_real_estate', methods=['POST'])
@limiter.limit("10 per minute")
def buy_real_estate():
    """Купить недвижимость"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    property_id = data.get('property_id')
    payment_type = data.get('payment_type', 'cash')
    down_payment = data.get('down_payment', 0)
    term_months = data.get('term_months', 240)  # 20 лет по умолчанию
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
        
    if property_id not in REAL_ESTATE:
        return jsonify({"error": "Invalid property"}), 400
        
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
        save_user_data_safe(user_id, user)
        
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
        save_user_data_safe(user_id, user)
        
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
@limiter.limit("5 per minute")
def select_trait():
    """Выбрать черту личности"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    trait_id = data.get('trait_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
        
    if trait_id not in TRAITS:
        return jsonify({"error": "Invalid trait"}), 400
        
    if user['trait_selected']:
        return jsonify({"error": "Trait already selected"}), 400
        
    user['trait'] = trait_id
    user['trait_selected'] = True
    
    # Сохраняем изменения в БД
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'trait': TRAITS[trait_id]
    })

@app.route('/api/buy_food', methods=['POST'])
@limiter.limit("20 per minute")
def buy_food():
    """Купить еду - восстанавливает настроение и здоровье"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    cost = 200
    
    if user['money'] < cost:
        return jsonify({"error": "Недостаточно денег!"}), 400
    
    user['money'] -= cost
    user['mood'] = min(100, user.get('mood', 50) + 10)
    user['health'] = min(100, user.get('health', 100) + 15)  # Добавлено восстановление здоровья
    
    # Сохраняем изменения в БД
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'message': 'Вкусно поел! +10 настроения, +15 здоровья'
    })

@app.route('/api/take_rest', methods=['POST'])
@limiter.limit("20 per minute")
def take_rest():
    """Отдохнуть - восстанавливает энергию, настроение и здоровье"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
    # Проверяем сколько раз уже отдыхал сегодня
    rest_count = user.get('rest_count_today', 0)
    if rest_count >= 2:
        return jsonify({"error": "Уже отдыхал 2 раза сегодня! Хватит лениться!"}), 400
    
    user['energy'] = min(user['max_energy'], user['energy'] + 20)
    user['mood'] = min(100, user.get('mood', 50) + 5)
    user['health'] = min(100, user.get('health', 100) + 10)  # Добавлено восстановление здоровья
    user['rest_count_today'] = rest_count + 1
    
    # Сохраняем изменения в БД
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'message': f'Отдохнул! +20 энергии, +5 настроения, +10 здоровья ({2 - user["rest_count_today"]} раз осталось)'
    })

@app.route('/api/random_event', methods=['POST'])
@limiter.limit("20 per minute")
def random_event():
    """Случайное событие в течение дня"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
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
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'event': event,
        'message': message
    })

@app.route('/api/play_roulette', methods=['POST'])
@limiter.limit("10 per minute")
def play_roulette():
    """Сыграть в рулетку"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    bet = data.get('bet', 100)
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
    if user['money'] < bet:
        return jsonify({"error": "Недостаточно денег!"}), 400
    
    # Вычитаем ставку
    user['money'] -= bet
    
    # Крутим рулетку (шансы как в казино - больше проигрышей)
    rand = random.random()
    if rand < 0.60:  # 60% шанс - проигрыш
        multiplier = 0
        result_emoji = '😭'
        message = f'Проиграл! -{bet}₽'
    elif rand < 0.85:  # 25% шанс - x2
        multiplier = 2
        result_emoji = '🙂'
        win = bet * multiplier
        user['money'] += win
        message = f'Выиграл x2! +{win}₽'
    elif rand < 0.95:  # 10% шанс - x5
        multiplier = 5
        result_emoji = '😄'
        win = bet * multiplier
        user['money'] += win
        message = f'Выиграл x5! +{win}₽'
    else:  # 5% шанс - x10
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
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'multiplier': multiplier,
        'result_emoji': result_emoji,
        'message': message
    })

@app.route('/api/upgrade_skill', methods=['POST'])
@limiter.limit("10 per minute")
def upgrade_skill():
    """Прокачать навык"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    skill = data.get('skill')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
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
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'message': f'{skill_names[skill]} повышена до уровня {user["skills"][skill]}!'
    })

@app.route('/api/work', methods=['POST'])
@limiter.limit("30 per minute")  # Макс 30 работ в минуту
def work():
    """Обработка нажатия кнопки РАБОТАТЬ"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
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
    
    # Применяем модификатор здоровья
    health = user.get('health', 100)
    health_modifier = 1.0
    if health <= 20:
        health_modifier = 0.5  # -50% при критическом здоровье
    elif health <= 40:
        health_modifier = 0.7  # -30% при плохом здоровье
    elif health <= 60:
        health_modifier = 0.85  # -15% при усталости
    elif health <= 80:
        health_modifier = 0.95  # -5% при нормальном здоровье
    else:
        health_modifier = 1.0  # 0% при отличном здоровье
    
    income = int(income * health_modifier)
    
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
    save_user_data_safe(user_id, user)
    
    return jsonify({
        'user': user,
        'event': event,
        'income': income,
        'job': job,
        'newly_completed_goals': newly_completed_goals,
        'skill_point_earned': newly_earned_skill_point
    })

@app.route('/api/next_day', methods=['POST'])
@limiter.limit("10 per minute")
def next_day():
    """Переход к следующему дню"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    user_id = data.get('user_id')
    
    user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400
    
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
            save_user_data_safe(user_id, user)
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
        
        # Увеличиваем месяц (уровень) вместо сброса игры
        if 'month' not in user:
            user['month'] = 1
        user['month'] += 1
        
        user['energy'] = user['max_energy']
        user['health'] = min(100, user.get('health', 100) + 30)  # Восстанавливаем здоровье
        
        # Проверяем выполнение целей
        newly_completed_goals = check_and_complete_goals(user)
        
        # Сохраняем изменения в БД
        save_user_data_safe(user_id, user)
        
        return jsonify({
            'user': user,
            'salary_received': True,
            'message': f"🎉 Месяц {user['month']-1} завершен! Получена зарплата {user['salary']}₽",
            'new_jobs': new_jobs,
            'newly_completed_goals': newly_completed_goals
        })
    else:
        user['day'] += 1
        user['energy'] = user['max_energy']  # Восстанавливаем энергию
        user['health'] = min(100, user.get('health', 100) + 30)  # Восстанавливаем здоровье
        
        # ОБРАБОТКА БИЗНЕСОВ - ежедневные операции
        business_report = business_manager.process_daily_operations(user_id)
        
        # ГЕНЕРАЦИЯ НОВЫХ ПОДРАБОТОК
        side_jobs_manager.reset_daily_jobs(user_id)
        
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
        
        # Добавляем информацию о бизнесах
        if business_report.businesses_processed > 0:
            message += f"\n\n🏪 Бизнесы обработаны: {business_report.businesses_processed}"
            message += f"\n💵 Доход от бизнесов: +{int(business_report.total_revenue)}₽"
            message += f"\n💸 Расходы бизнесов: -{int(business_report.total_expenses)}₽"
            message += f"\n💰 Чистая прибыль: {'+' if business_report.total_net_profit >= 0 else ''}{int(business_report.total_net_profit)}₽"
            
            if business_report.new_events:
                message += f"\n⚠️ Новых событий: {len(business_report.new_events)}"
            
        if new_jobs:
            job_names = [job['name'] for job in new_jobs]
            message += f"\n🎉 Открыты новые работы: {', '.join(job_names)}"
            
        # Сохраняем изменения в БД
        save_user_data_safe(user_id, user)
        
        return jsonify({
            'user': user,
            'daily_cost': daily_cost,
            'passive_income': passive_income if user['day'] % 30 == 1 else 0,
            'monthly_expenses': monthly_expenses if user['day'] % 30 == 1 else 0,
            'business_report': {
                'total_revenue': business_report.total_revenue,
                'total_expenses': business_report.total_expenses,
                'total_net_profit': business_report.total_net_profit,
                'businesses_processed': business_report.businesses_processed,
                'new_events_count': len(business_report.new_events)
            } if business_report.businesses_processed > 0 else None,
            'message': message,
            'new_jobs': new_jobs,
            'expired_boosters': expired_boosters
        })


# ============================================
# BUSINESS SYSTEM API ENDPOINTS
# ============================================

@app.route('/api/business/create', methods=['POST'])
@limiter.limit("5 per minute")
def create_business():
    """Создать новый бизнес"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    business_type_str = data.get('business_type')
    
    if not user_id or not business_type_str:
        return jsonify({"error": "Missing user_id or business_type"}), 400
    
    try:
        business_type = BusinessType(business_type_str)
    except ValueError:
        return jsonify({"error": "Invalid business_type"}), 400
    
    result = business_manager.create_business(user_id, business_type)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    return jsonify({
        "success": True,
        "business": result.data.to_dict(),
        "message": f"Бизнес создан! {BUSINESS_CONFIGS[business_type]['emoji']} {BUSINESS_CONFIGS[business_type]['name']}"
    })


@app.route('/api/business/list', methods=['GET'])
def list_businesses():
    """Получить список всех бизнесов пользователя"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    businesses = business_manager.get_user_businesses(user_id)
    
    # Добавляем текущую статистику для каждого бизнеса
    businesses_data = []
    for business in businesses:
        daily_revenue = business_manager.revenue_calculator.calculate_daily_revenue(business)
        daily_expenses = business_manager.revenue_calculator.calculate_daily_expenses(business)
        net_profit = daily_revenue - daily_expenses
        
        business_dict = business.to_dict()
        business_dict['daily_revenue'] = daily_revenue
        business_dict['daily_expenses'] = daily_expenses
        business_dict['net_profit'] = net_profit
        business_dict['config'] = BUSINESS_CONFIGS[business.business_type]
        
        businesses_data.append(business_dict)
    
    return jsonify({
        "businesses": businesses_data,
        "total_count": len(businesses_data)
    })


@app.route('/api/business/<business_id>', methods=['GET'])
def get_business_detail(business_id):
    """Получить детальную информацию о бизнесе"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    # Добавляем статистику
    daily_revenue = business_manager.revenue_calculator.calculate_daily_revenue(business)
    daily_expenses = business_manager.revenue_calculator.calculate_daily_expenses(business)
    net_profit = daily_revenue - daily_expenses
    
    business_dict = business.to_dict()
    business_dict['daily_revenue'] = daily_revenue
    business_dict['daily_expenses'] = daily_expenses
    business_dict['net_profit'] = net_profit
    business_dict['config'] = BUSINESS_CONFIGS[business.business_type]
    
    return jsonify(business_dict)


@app.route('/api/business/<business_id>/hire', methods=['POST'])
@limiter.limit("10 per minute")
def hire_employee(business_id):
    """Нанять сотрудника"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    employee_type_str = data.get('employee_type')
    
    if not user_id or not employee_type_str:
        return jsonify({"error": "Missing user_id or employee_type"}), 400
    
    try:
        employee_type = EmployeeType(employee_type_str)
    except ValueError:
        return jsonify({"error": "Invalid employee_type"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    result = business_manager.employee_manager.hire_employee(business, employee_type)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    # Сохраняем изменения
    business_manager.repository.save_business(business)
    
    return jsonify({
        "success": True,
        "employee": result.data.to_dict(),
        "business": business.to_dict(),
        "message": f"Нанят {EMPLOYEE_CONFIGS[employee_type]['emoji']} {EMPLOYEE_CONFIGS[employee_type]['name']}"
    })


@app.route('/api/business/<business_id>/fire/<employee_id>', methods=['POST'])
@limiter.limit("10 per minute")
def fire_employee(business_id, employee_id):
    """Уволить сотрудника"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    result = business_manager.employee_manager.fire_employee(business, employee_id)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    # Сохраняем изменения
    business_manager.repository.save_business(business)
    
    return jsonify({
        "success": True,
        "business": business.to_dict(),
        "message": "Сотрудник уволен"
    })


@app.route('/api/business/<business_id>/buy-inventory', methods=['POST'])
@limiter.limit("10 per minute")
def buy_inventory(business_id):
    """Купить запасы"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    user_funds = business_manager.repository.get_user_funds(user_id)
    result = business_manager.inventory_manager.purchase_inventory(business, user_funds)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    # Вычитаем деньги
    business_manager.repository.update_user_funds(user_id, -result.data['cost'])
    
    # Сохраняем изменения
    business_manager.repository.save_business(business)
    
    return jsonify({
        "success": True,
        "business": business.to_dict(),
        "cost": result.data['cost'],
        "message": f"Запасы пополнены! -{result.data['cost']}₽"
    })


@app.route('/api/business/<business_id>/upgrade', methods=['POST'])
@limiter.limit("10 per minute")
def purchase_upgrade(business_id):
    """Купить улучшение"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    upgrade_type_str = data.get('upgrade_type')
    
    if not user_id or not upgrade_type_str:
        return jsonify({"error": "Missing user_id or upgrade_type"}), 400
    
    try:
        upgrade_type = UpgradeType(upgrade_type_str)
    except ValueError:
        return jsonify({"error": "Invalid upgrade_type"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    user_funds = business_manager.repository.get_user_funds(user_id)
    result = business_manager.upgrade_manager.purchase_upgrade(business, upgrade_type, user_funds)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    # Вычитаем деньги
    business_manager.repository.update_user_funds(user_id, -result.data['cost'])
    
    # Сохраняем изменения
    business_manager.repository.save_business(business)
    
    return jsonify({
        "success": True,
        "upgrade": result.data['upgrade'].to_dict(),
        "business": business.to_dict(),
        "cost": result.data['cost'],
        "message": f"Куплено улучшение: {UPGRADE_CONFIGS[upgrade_type]['emoji']} {UPGRADE_CONFIGS[upgrade_type]['name']}"
    })


@app.route('/api/business/<business_id>/sell', methods=['POST'])
@limiter.limit("5 per minute")
def sell_business(business_id):
    """Продать бизнес"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    result = business_manager.sell_business(business_id, user_id)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    return jsonify({
        "success": True,
        "sale_price": result.data['sale_price'],
        "total_investment": result.data['total_investment'],
        "message": f"Бизнес продан за {result.data['sale_price']}₽"
    })


@app.route('/api/business/<business_id>/repair', methods=['POST'])
@limiter.limit("10 per minute")
def repair_equipment(business_id):
    """Отремонтировать оборудование"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    
    if not user_id or not event_id:
        return jsonify({"error": "Missing user_id or event_id"}), 400
    
    business = business_manager.get_business(business_id, user_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    user_funds = business_manager.repository.get_user_funds(user_id)
    result = business_manager.event_manager.resolve_event(business, event_id, "repair", user_funds)
    
    if not result.success:
        return jsonify({"error": result.error}), 400
    
    # Вычитаем деньги
    business_manager.repository.update_user_funds(user_id, -result.data['cost'])
    
    # Сохраняем изменения
    business_manager.repository.save_business(business)
    
    return jsonify({
        "success": True,
        "business": business.to_dict(),
        "cost": result.data['cost'],
        "message": f"Оборудование отремонтировано! -{result.data['cost']}₽"
    })


@app.route('/api/business/configs', methods=['GET'])
def get_business_configs():
    """Получить конфигурации бизнесов"""
    return jsonify({
        "business_types": {k.value: v for k, v in BUSINESS_CONFIGS.items()},
        "employee_types": {k.value: v for k, v in EMPLOYEE_CONFIGS.items()},
        "upgrade_types": {k.value: v for k, v in UPGRADE_CONFIGS.items()},
        "event_types": {k.value: v for k, v in EVENT_CONFIGS.items()}
    })


# ============================================
# SIDE JOBS API ENDPOINTS
# ============================================

@app.route('/api/side-jobs/list', methods=['GET'])
def get_side_jobs():
    """Получить список доступных подработок"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        jobs = side_jobs_manager.get_available_jobs(user_id)
        
        return jsonify({
            "success": True,
            "jobs": jobs
        })
    except Exception as e:
        logger.error(f"Error getting side jobs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/side-jobs/execute', methods=['POST'])
@limiter.limit("20 per minute")
def execute_side_job():
    """Выполнить подработку"""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        
        if not user_id or not job_id:
            return jsonify({"error": "user_id and job_id are required"}), 400
        
        logger.info(f"Executing side job: user={user_id}, job={job_id}")
        
        result = side_jobs_manager.execute_job(user_id, job_id)
        
        logger.info(f"Side job result: success={result.get('success')}, error={result.get('error')}")
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing side job: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/side-jobs/stats', methods=['GET'])
def get_side_jobs_stats():
    """Получить статистику подработок"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        stats = side_jobs_manager.get_stats(user_id)
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting side jobs stats: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# TELEGRAM BOT WEBHOOK
# ============================================

# BOT_TOKEN и WEBAPP_URL объявлены в начале файла (строка 73-74)

@app.route(f'/bot_webhook', methods=['POST'])
def telegram_webhook():
    """Обработка webhook от Telegram"""
    if not BOT_TOKEN:
        return jsonify({"error": "Bot token not set"}), 400
    
    try:
        import requests as req
        data = request.get_json()
        
        # Проверяем что это команда /start
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                # Отправляем ответ с кнопкой
                keyboard = {
                    "inline_keyboard": [[
                        {
                            "text": "🎮 Играть в 'Выживи до зарплаты'",
                            "web_app": {"url": WEBAPP_URL}
                        }
                    ]]
                }
                
                response = req.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    json={
                        'chat_id': chat_id,
                        'text': (
                            "🎯 Добро пожаловать в игру 'Выживи до зарплаты'!\n\n"
                            "💼 Твоя задача - дожить до зарплаты, работая и избегая лишних трат.\n"
                            "⚡ Работай, чтобы заработать деньги, но следи за энергией!\n"
                            "📅 Каждый день приносит новые вызовы и случайные события.\n\n"
                            "Нажми кнопку ниже, чтобы начать игру:"
                        ),
                        'reply_markup': keyboard
                    }
                )
                
                logger.info(f"Sent /start response to chat {chat_id}")
        
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка webhook для бота"""
    if not BOT_TOKEN:
        return jsonify({"error": "Bot token not set"}), 400
    
    try:
        import requests as req
        webhook_url = f"{WEBAPP_URL}/bot_webhook"
        
        response = req.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook',
            json={'url': webhook_url}
        )
        
        result = response.json()
        logger.info(f"Webhook set result: {result}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# TELEGRAM BOT (старый код - не используется)
# ============================================

# BOT_TOKEN и WEBAPP_URL объявлены в начале файла

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start (не используется с webhook)"""
    pass
    
    await update.message.reply_text(
        "🎯 Добро пожаловать в игру 'Выживи до зарплаты'!\n\n"
        "💼 Твоя задача - дожить до зарплаты, работая и избегая лишних трат.\n"
        "⚡ Работай, чтобы заработать деньги, но следи за энергией!\n"
        "📅 Каждый день приносит новые вызовы и случайные события.\n\n"
        "Нажми кнопку ниже, чтобы начать игру:",
        reply_markup=reply_markup
    )

def run_bot():
    """Запуск бота в отдельном потоке"""
    if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
        logger.warning("TELEGRAM_BOT_TOKEN не установлен - бот не запущен")
        return
    
    try:
        # Создаем новый event loop для этого потока
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        
        # Добавляем обработчик ошибок
        async def error_handler(update, context):
            logger.error(f"Update {update} caused error {context.error}")
        
        application.add_error_handler(error_handler)
        
        logger.info("🤖 Telegram бот запущен!")
        logger.info(f"🌐 Web App URL: {WEBAPP_URL}")
        
        application.run_polling(drop_pending_updates=True)  # Игнорируем старые обновления
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Запускаем бота только если явно установлена переменная RUN_BOT=true
# ВАЖНО: Бот не может работать с polling в отдельном потоке на Render
# Используйте прямую ссылку: https://telegramfix.onrender.com
if os.getenv('RUN_BOT', 'false').lower() == 'true':
    logger.warning("⚠️ RUN_BOT=true, но бот не может работать с polling в отдельном потоке")
    logger.info("💡 Используйте прямую ссылку для игры: https://telegramfix.onrender.com")
    # bot_thread = Thread(target=run_bot, daemon=True)
    # bot_thread.start()
    # logger.info("Bot thread started")

if __name__ == '__main__':
    # Для локальной разработки - только Flask без бота
    logger.info("🚀 Запуск в режиме разработки (только Flask, без Telegram бота)")
    logger.info("💡 Чтобы запустить бота, установите переменную окружения: RUN_BOT=true")
    port = int(os.environ.get('PORT', 8080))  # Изменили порт на 8080
    logger.info(f"🌐 Запуск на порту {port}")
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)