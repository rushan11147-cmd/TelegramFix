# -*- coding: utf-8 -*-
"""
Career Progression System Configuration

Defines all professions, career ladders, promotion requirements,
and salary scales for the career progression system.
"""

PROFESSIONS = {
    'courier': {
        'id': 'courier',
        'name': 'Courier',
        'name_ru': 'Курьер',
        'emoji': '📦',
        'description': 'Быстрая доставка, низкая зарплата, быстрый рост',
        'starting_salary': 150,
        'progression_multiplier': 1.5,  # Faster progression
        'primary_skills': ['speed', 'luck'],
        'energy_bonus': 0,  # No energy bonus
        'levels': [
            {
                'id': 0,
                'name': 'Courier',
                'name_ru': 'Курьер',
                'salary': 150,
                'energy_cost_reduction': 0,
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'Senior Courier',
                'name_ru': 'Старший курьер',
                'salary': 250,
                'energy_cost_reduction': 0.05,
                'requirements': {
                    'work_actions': 15,
                    'skills': {'speed': 2, 'luck': 2},
                    'money_earned': 2000,
                    'days_survived': 8
                }
            },
            {
                'id': 2,
                'name': 'Logistics Coordinator',
                'name_ru': 'Координатор логистики',
                'salary': 400,
                'energy_cost_reduction': 0.10,
                'requirements': {
                    'work_actions': 40,
                    'skills': {'speed': 4, 'luck': 3, 'intelligence': 2},
                    'money_earned': 8000,
                    'days_survived': 20
                }
            },
            {
                'id': 3,
                'name': 'Logistics Director',
                'name_ru': 'Директор логистики',
                'salary': 700,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 80,
                    'skills': {'speed': 6, 'luck': 5, 'intelligence': 4},
                    'money_earned': 25000,
                    'days_survived': 40
                }
            }
        ]
    },
    
    'office_worker': {
        'id': 'office_worker',
        'name': 'Office Worker',
        'name_ru': 'Офисный работник',
        'emoji': '💼',
        'description': 'Стабильная работа, средняя зарплата, нормальный рост',
        'starting_salary': 250,
        'progression_multiplier': 1.0,  # Normal progression
        'primary_skills': ['intelligence', 'charisma'],
        'energy_bonus': 0,
        'levels': [
            {
                'id': 0,
                'name': 'Office Worker',
                'name_ru': 'Офисный работник',
                'salary': 250,
                'energy_cost_reduction': 0,
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'Senior Specialist',
                'name_ru': 'Старший специалист',
                'salary': 400,
                'energy_cost_reduction': 0.05,
                'requirements': {
                    'work_actions': 20,
                    'skills': {'intelligence': 3, 'charisma': 2},
                    'money_earned': 4000,
                    'days_survived': 12
                }
            },
            {
                'id': 2,
                'name': 'Team Lead',
                'name_ru': 'Руководитель группы',
                'salary': 650,
                'energy_cost_reduction': 0.10,
                'requirements': {
                    'work_actions': 50,
                    'skills': {'intelligence': 5, 'charisma': 4},
                    'money_earned': 12000,
                    'days_survived': 28
                }
            },
            {
                'id': 3,
                'name': 'Department Manager',
                'name_ru': 'Начальник отдела',
                'salary': 1000,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 100,
                    'skills': {'intelligence': 7, 'charisma': 6},
                    'money_earned': 35000,
                    'days_survived': 50
                }
            }
        ]
    },
    
    'salesperson': {
        'id': 'salesperson',
        'name': 'Salesperson',
        'name_ru': 'Продавец',
        'emoji': '🛒',
        'description': 'Бонус от харизмы, средняя зарплата',
        'starting_salary': 200,
        'progression_multiplier': 1.2,
        'primary_skills': ['charisma', 'luck'],
        'bonus_skill': 'charisma',  # Skill that provides income bonus
        'bonus_multiplier': 0.1,  # 10% bonus per charisma level
        'energy_bonus': 0,
        'levels': [
            {
                'id': 0,
                'name': 'Salesperson',
                'name_ru': 'Продавец',
                'salary': 200,
                'energy_cost_reduction': 0,
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'Senior Salesperson',
                'name_ru': 'Старший продавец',
                'salary': 350,
                'energy_cost_reduction': 0.05,
                'requirements': {
                    'work_actions': 18,
                    'skills': {'charisma': 3, 'luck': 2},
                    'money_earned': 3500,
                    'days_survived': 10
                }
            },
            {
                'id': 2,
                'name': 'Sales Manager',
                'name_ru': 'Менеджер по продажам',
                'salary': 550,
                'energy_cost_reduction': 0.10,
                'requirements': {
                    'work_actions': 45,
                    'skills': {'charisma': 5, 'luck': 4},
                    'money_earned': 10000,
                    'days_survived': 25
                }
            },
            {
                'id': 3,
                'name': 'Regional Director',
                'name_ru': 'Региональный директор',
                'salary': 900,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 90,
                    'skills': {'charisma': 7, 'luck': 6},
                    'money_earned': 30000,
                    'days_survived': 45
                }
            }
        ]
    },
    
    'waiter': {
        'id': 'waiter',
        'name': 'Waiter',
        'name_ru': 'Официант',
        'emoji': '🍽️',
        'description': 'Бонус от настроения, чаевые',
        'starting_salary': 180,
        'progression_multiplier': 1.3,
        'primary_skills': ['charisma', 'speed'],
        'bonus_stat': 'mood',  # Stat that provides income bonus
        'bonus_multiplier': 0.02,  # 2% bonus per mood point
        'energy_bonus': 0,
        'levels': [
            {
                'id': 0,
                'name': 'Waiter',
                'name_ru': 'Официант',
                'salary': 180,
                'energy_cost_reduction': 0,
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'Senior Waiter',
                'name_ru': 'Старший официант',
                'salary': 300,
                'energy_cost_reduction': 0.05,
                'requirements': {
                    'work_actions': 16,
                    'skills': {'charisma': 3, 'speed': 2},
                    'money_earned': 2800,
                    'days_survived': 9
                }
            },
            {
                'id': 2,
                'name': 'Restaurant Supervisor',
                'name_ru': 'Супервайзер ресторана',
                'salary': 480,
                'energy_cost_reduction': 0.10,
                'requirements': {
                    'work_actions': 42,
                    'skills': {'charisma': 5, 'speed': 4, 'intelligence': 2},
                    'money_earned': 9000,
                    'days_survived': 22
                }
            },
            {
                'id': 3,
                'name': 'Restaurant Manager',
                'name_ru': 'Управляющий рестораном',
                'salary': 800,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 85,
                    'skills': {'charisma': 7, 'speed': 6, 'intelligence': 4},
                    'money_earned': 28000,
                    'days_survived': 42
                }
            }
        ]
    },
    
    'security_guard': {
        'id': 'security_guard',
        'name': 'Security Guard',
        'name_ru': 'Охранник',
        'emoji': '🛡️',
        'description': 'Меньше тратит энергии, стабильная работа',
        'starting_salary': 220,
        'progression_multiplier': 1.1,
        'primary_skills': ['speed', 'intelligence'],
        'energy_bonus': 0.10,  # 10% less energy cost from start
        'levels': [
            {
                'id': 0,
                'name': 'Security Guard',
                'name_ru': 'Охранник',
                'salary': 220,
                'energy_cost_reduction': 0.10,  # Base 10% reduction
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'Senior Guard',
                'name_ru': 'Старший охранник',
                'salary': 360,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 22,
                    'skills': {'speed': 3, 'intelligence': 2},
                    'money_earned': 4500,
                    'days_survived': 13
                }
            },
            {
                'id': 2,
                'name': 'Security Supervisor',
                'name_ru': 'Супервайзер безопасности',
                'salary': 580,
                'energy_cost_reduction': 0.20,
                'requirements': {
                    'work_actions': 55,
                    'skills': {'speed': 5, 'intelligence': 4, 'charisma': 2},
                    'money_earned': 13000,
                    'days_survived': 30
                }
            },
            {
                'id': 3,
                'name': 'Security Chief',
                'name_ru': 'Начальник безопасности',
                'salary': 950,
                'energy_cost_reduction': 0.25,
                'requirements': {
                    'work_actions': 110,
                    'skills': {'speed': 7, 'intelligence': 6, 'charisma': 4},
                    'money_earned': 38000,
                    'days_survived': 55
                }
            }
        ]
    },
    
    'it_support': {
        'id': 'it_support',
        'name': 'IT Support',
        'name_ru': 'IT-специалист',
        'emoji': '💻',
        'description': 'Бонус от интеллекта, высокая зарплата',
        'starting_salary': 280,
        'progression_multiplier': 0.9,  # Slower progression, but higher pay
        'primary_skills': ['intelligence', 'luck'],
        'bonus_skill': 'intelligence',  # Skill that provides income bonus
        'bonus_multiplier': 0.12,  # 12% bonus per intelligence level
        'energy_bonus': 0,
        'levels': [
            {
                'id': 0,
                'name': 'IT Support',
                'name_ru': 'IT-специалист',
                'salary': 280,
                'energy_cost_reduction': 0,
                'requirements': {
                    'work_actions': 0,
                    'skills': {},
                    'money_earned': 0,
                    'days_survived': 0
                }
            },
            {
                'id': 1,
                'name': 'System Administrator',
                'name_ru': 'Системный администратор',
                'salary': 450,
                'energy_cost_reduction': 0.05,
                'requirements': {
                    'work_actions': 25,
                    'skills': {'intelligence': 4, 'luck': 2},
                    'money_earned': 6000,
                    'days_survived': 15
                }
            },
            {
                'id': 2,
                'name': 'IT Manager',
                'name_ru': 'IT-менеджер',
                'salary': 720,
                'energy_cost_reduction': 0.10,
                'requirements': {
                    'work_actions': 60,
                    'skills': {'intelligence': 6, 'luck': 4, 'charisma': 3},
                    'money_earned': 18000,
                    'days_survived': 35
                }
            },
            {
                'id': 3,
                'name': 'IT Director',
                'name_ru': 'IT-директор',
                'salary': 1200,
                'energy_cost_reduction': 0.15,
                'requirements': {
                    'work_actions': 120,
                    'skills': {'intelligence': 8, 'luck': 6, 'charisma': 5},
                    'money_earned': 50000,
                    'days_survived': 60
                }
            }
        ]
    }
}


def get_profession(profession_id):
    """Get profession configuration by ID."""
    return PROFESSIONS.get(profession_id)


def get_all_professions():
    """Get list of all available professions."""
    return list(PROFESSIONS.keys())


def get_profession_level(profession_id, level_id):
    """Get specific career level configuration."""
    profession = get_profession(profession_id)
    if not profession:
        return None
    
    for level in profession['levels']:
        if level['id'] == level_id:
            return level
    return None


def get_next_level(profession_id, current_level_id):
    """Get next career level or None if at max."""
    profession = get_profession(profession_id)
    if not profession:
        return None
    
    next_level_id = current_level_id + 1
    return get_profession_level(profession_id, next_level_id)


def get_starting_salary(profession_id):
    """Get starting salary for a profession."""
    profession = get_profession(profession_id)
    return profession['starting_salary'] if profession else 0


def get_profession_display_name(profession_id):
    """Get Russian display name for profession."""
    profession = get_profession(profession_id)
    return profession['name_ru'] if profession else profession_id
