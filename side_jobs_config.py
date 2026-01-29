# -*- coding: utf-8 -*-
"""
Конфигурация побочных подработок
"""

# Все доступные подработки
SIDE_JOBS = {
    # ФИЗИЧЕСКИЕ ПОДРАБОТКИ (высокая оплата, высокие затраты энергии)
    "loader": {
        "id": "loader",
        "name": "Грузчик",
        "description": "Разгрузка фуры с товарами",
        "category": "physical",
        "base_payment": 300,
        "energy_cost": 15,
        "success_rate": 0.80,
        "emoji": "📦"
    },
    "bike_courier": {
        "id": "bike_courier",
        "name": "Курьер на велосипеде",
        "description": "Доставка посылок по городу",
        "category": "physical",
        "base_payment": 250,
        "energy_cost": 12,
        "success_rate": 0.85,
        "emoji": "🚴"
    },
    "flyer_distribution": {
        "id": "flyer_distribution",
        "name": "Раздача листовок",
        "description": "Раздача рекламных листовок",
        "category": "physical",
        "base_payment": 150,
        "energy_cost": 8,
        "success_rate": 0.95,
        "emoji": "📄"
    },
    "apartment_cleaning": {
        "id": "apartment_cleaning",
        "name": "Уборка квартиры",
        "description": "Генеральная уборка квартиры",
        "category": "physical",
        "base_payment": 400,
        "energy_cost": 18,
        "success_rate": 0.90,
        "emoji": "🧹"
    },
    "car_wash": {
        "id": "car_wash",
        "name": "Мойка машин",
        "description": "Мойка и чистка автомобилей",
        "category": "physical",
        "base_payment": 350,
        "energy_cost": 15,
        "success_rate": 0.85,
        "emoji": "🚗"
    },
    
    # УМСТВЕННЫЕ ПОДРАБОТКИ (средняя оплата, низкие затраты энергии)
    "tutoring": {
        "id": "tutoring",
        "name": "Репетиторство",
        "description": "Помощь школьнику с математикой",
        "category": "mental",
        "base_payment": 500,
        "energy_cost": 10,
        "success_rate": 0.70,
        "emoji": "📚"
    },
    "translation": {
        "id": "translation",
        "name": "Перевод текста",
        "description": "Перевод статьи с английского",
        "category": "mental",
        "base_payment": 400,
        "energy_cost": 8,
        "success_rate": 0.75,
        "emoji": "🌐"
    },
    "article_writing": {
        "id": "article_writing",
        "name": "Написание статьи",
        "description": "Статья для блога на 1000 слов",
        "category": "mental",
        "base_payment": 600,
        "energy_cost": 12,
        "success_rate": 0.65,
        "emoji": "✍️"
    },
    "homework_help": {
        "id": "homework_help",
        "name": "Помощь с домашкой",
        "description": "Решение задач по физике",
        "category": "mental",
        "base_payment": 300,
        "energy_cost": 6,
        "success_rate": 0.80,
        "emoji": "📝"
    },
    "document_review": {
        "id": "document_review",
        "name": "Проверка документов",
        "description": "Вычитка и проверка договора",
        "category": "mental",
        "base_payment": 350,
        "energy_cost": 7,
        "success_rate": 0.85,
        "emoji": "📋"
    },
    
    # ТВОРЧЕСКИЕ ПОДРАБОТКИ (высокая оплата, средние затраты, низкий шанс)
    "logo_design": {
        "id": "logo_design",
        "name": "Дизайн логотипа",
        "description": "Создание логотипа для стартапа",
        "category": "creative",
        "base_payment": 800,
        "energy_cost": 10,
        "success_rate": 0.60,
        "emoji": "🎨"
    },
    "photoshoot": {
        "id": "photoshoot",
        "name": "Фотосессия",
        "description": "Фотосъемка для соцсетей",
        "category": "creative",
        "base_payment": 700,
        "energy_cost": 12,
        "success_rate": 0.65,
        "emoji": "📸"
    },
    "video_editing": {
        "id": "video_editing",
        "name": "Монтаж видео",
        "description": "Монтаж ролика для YouTube",
        "category": "creative",
        "base_payment": 900,
        "energy_cost": 15,
        "success_rate": 0.55,
        "emoji": "🎬"
    },
    "custom_drawing": {
        "id": "custom_drawing",
        "name": "Рисунок на заказ",
        "description": "Портрет по фотографии",
        "category": "creative",
        "base_payment": 600,
        "energy_cost": 10,
        "success_rate": 0.70,
        "emoji": "🖌️"
    },
    
    # СОЦИАЛЬНЫЕ ПОДРАБОТКИ (средняя оплата, низкие затраты)
    "promoter": {
        "id": "promoter",
        "name": "Промоутер",
        "description": "Раздача пробников в магазине",
        "category": "social",
        "base_payment": 400,
        "energy_cost": 10,
        "success_rate": 0.80,
        "emoji": "🎁"
    },
    "party_animator": {
        "id": "party_animator",
        "name": "Аниматор на празднике",
        "description": "Развлечение детей на дне рождения",
        "category": "social",
        "base_payment": 600,
        "energy_cost": 15,
        "success_rate": 0.70,
        "emoji": "🎉"
    },
    "dog_walking": {
        "id": "dog_walking",
        "name": "Выгул собак",
        "description": "Прогулка с тремя собаками",
        "category": "social",
        "base_payment": 250,
        "energy_cost": 8,
        "success_rate": 0.95,
        "emoji": "🐕"
    },
    "babysitting": {
        "id": "babysitting",
        "name": "Присмотр за детьми",
        "description": "Посидеть с ребенком 3 часа",
        "category": "social",
        "base_payment": 500,
        "energy_cost": 12,
        "success_rate": 0.75,
        "emoji": "👶"
    }
}

# Категории подработок
CATEGORIES = {
    "physical": {
        "name": "Физические",
        "color": "#e74c3c",  # Красный
        "description": "Требуют физических усилий"
    },
    "mental": {
        "name": "Умственные",
        "color": "#3498db",  # Синий
        "description": "Требуют умственных усилий"
    },
    "creative": {
        "name": "Творческие",
        "color": "#9b59b6",  # Фиолетовый
        "description": "Требуют творческих навыков"
    },
    "social": {
        "name": "Социальные",
        "color": "#f39c12",  # Оранжевый
        "description": "Требуют общения с людьми"
    }
}
