# -*- coding: utf-8 -*-
"""
Система побочных подработок
"""

import random
from typing import Dict, List, Optional, Tuple
from side_jobs_config import SIDE_JOBS, CATEGORIES


class SideJobManager:
    """Менеджер побочных подработок"""
    
    def __init__(self, get_user_func, save_user_func):
        """
        Args:
            get_user_func: Функция для получения данных пользователя
            save_user_func: Функция для сохранения данных пользователя
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
    
    def generate_daily_jobs(self, user_id: str) -> List[Dict]:
        """
        Генерирует 3-5 случайных подработок на день
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список подработок
        """
        # Получаем пользователя
        user = self.get_user(user_id)
        if not user:
            return []
        
        # Генерируем 3-5 случайных подработок
        count = random.randint(3, 5)
        all_jobs = list(SIDE_JOBS.values())
        selected_jobs = random.sample(all_jobs, min(count, len(all_jobs)))
        
        # Сохраняем ID доступных подработок
        if 'side_jobs' not in user:
            user['side_jobs'] = {}
        
        user['side_jobs']['available'] = [job['id'] for job in selected_jobs]
        user['side_jobs']['completed_today'] = []
        
        self.save_user(user_id, user)
        
        return selected_jobs
    
    def get_available_jobs(self, user_id: str) -> List[Dict]:
        """
        Получает список доступных подработок
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список подработок с информацией о выполнении
        """
        user = self.get_user(user_id)
        if not user:
            return []
        
        # Инициализируем данные если их нет
        if 'side_jobs' not in user:
            return self.generate_daily_jobs(user_id)
        
        if 'available' not in user['side_jobs']:
            return self.generate_daily_jobs(user_id)
        
        # Получаем доступные подработки
        available_ids = user['side_jobs'].get('available', [])
        completed_ids = user['side_jobs'].get('completed_today', [])
        
        jobs = []
        for job_id in available_ids:
            if job_id in SIDE_JOBS:
                job = SIDE_JOBS[job_id].copy()
                job['completed'] = job_id in completed_ids
                
                # Рассчитываем финальные значения с учетом навыков
                job['final_payment'] = self._calculate_payment(job, user)
                job['final_success_rate'] = self._calculate_success_rate(job, user)
                
                jobs.append(job)
        
        return jobs
    
    def execute_job(self, user_id: str, job_id: str) -> Dict:
        """
        Выполняет подработку
        
        Args:
            user_id: ID пользователя
            job_id: ID подработки
            
        Returns:
            Результат выполнения
        """
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'Пользователь не найден'}
        
        # Проверяем что подработка доступна
        if 'side_jobs' not in user or 'available' not in user['side_jobs']:
            return {'success': False, 'error': 'Нет доступных подработок'}
        
        if job_id not in user['side_jobs']['available']:
            return {'success': False, 'error': 'Подработка недоступна'}
        
        # Проверяем что не выполнена
        completed = user['side_jobs'].get('completed_today', [])
        if job_id in completed:
            return {'success': False, 'error': 'Подработка уже выполнена'}
        
        # Получаем конфигурацию подработки
        if job_id not in SIDE_JOBS:
            return {'success': False, 'error': 'Подработка не найдена'}
        
        job = SIDE_JOBS[job_id]
        
        # Проверяем энергию
        current_energy = user.get('energy', 0)
        if current_energy < job['energy_cost']:
            return {
                'success': False,
                'error': f'Недостаточно энергии (нужно {job["energy_cost"]}, есть {current_energy})'
            }
        
        # Списываем энергию
        user['energy'] -= job['energy_cost']
        
        # Рассчитываем шанс успеха
        success_rate = self._calculate_success_rate(job, user)
        
        # Определяем результат
        is_success = random.random() < success_rate
        
        # Инициализируем статистику если её нет
        if 'side_jobs_stats' not in user:
            user['side_jobs_stats'] = {
                'total_completed': 0,
                'total_earned': 0,
                'success_count': 0,
                'fail_count': 0
            }
        
        result = {
            'success': True,
            'job_success': is_success,
            'job_name': job['name'],
            'emoji': job['emoji']
        }
        
        if is_success:
            # Рассчитываем оплату
            payment = self._calculate_payment(job, user)
            user['money'] = user.get('money', 0) + payment
            user['total_earned'] = user.get('total_earned', 0) + payment
            
            user['side_jobs_stats']['success_count'] += 1
            user['side_jobs_stats']['total_earned'] += payment
            
            result['payment'] = payment
            result['message'] = f'{job["emoji"]} Успех! Заработано {payment}₽'
        else:
            user['side_jobs_stats']['fail_count'] += 1
            result['payment'] = 0
            result['message'] = f'{job["emoji"]} Не получилось... Энергия потрачена'
        
        # Отмечаем как выполненную
        user['side_jobs']['completed_today'].append(job_id)
        user['side_jobs_stats']['total_completed'] += 1
        
        # Сохраняем
        self.save_user(user_id, user)
        
        result['user'] = user
        return result
    
    def get_stats(self, user_id: str) -> Dict:
        """
        Получает статистику подработок
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Статистика
        """
        user = self.get_user(user_id)
        if not user:
            return {}
        
        stats = user.get('side_jobs_stats', {
            'total_completed': 0,
            'total_earned': 0,
            'success_count': 0,
            'fail_count': 0
        })
        
        # Рассчитываем процент успеха
        total = stats['total_completed']
        if total > 0:
            stats['success_rate'] = round(stats['success_count'] / total * 100, 1)
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def _calculate_success_rate(self, job: Dict, user: Dict) -> float:
        """
        Рассчитывает шанс успеха с учетом навыков
        
        Args:
            job: Конфигурация подработки
            user: Данные пользователя
            
        Returns:
            Шанс успеха (0.0-0.95)
        """
        base_rate = job['success_rate']
        
        # Бонус от навыка "Удача"
        skills = user.get('skills', {})
        luck_level = skills.get('luck', 1)
        luck_bonus = (luck_level - 1) * 0.05  # +5% за уровень
        
        # Итоговый шанс (максимум 95%)
        final_rate = min(0.95, base_rate + luck_bonus)
        
        return final_rate
    
    def _calculate_payment(self, job: Dict, user: Dict) -> int:
        """
        Рассчитывает оплату с учетом навыков
        
        Args:
            job: Конфигурация подработки
            user: Данные пользователя
            
        Returns:
            Оплата
        """
        base_payment = job['base_payment']
        multiplier = 1.0
        
        skills = user.get('skills', {})
        category = job['category']
        
        # Бонус от навыков в зависимости от категории
        if category == 'social':
            # Харизма увеличивает оплату социальных подработок
            charisma_level = skills.get('charisma', 1)
            multiplier += (charisma_level - 1) * 0.05  # +5% за уровень
        
        elif category == 'mental':
            # Интеллект увеличивает оплату умственных подработок
            intelligence_level = skills.get('intelligence', 1)
            multiplier += (intelligence_level - 1) * 0.05  # +5% за уровень
        
        # Итоговая оплата
        final_payment = int(base_payment * multiplier)
        
        return final_payment
    
    def reset_daily_jobs(self, user_id: str) -> List[Dict]:
        """
        Сбрасывает подработки при переходе на новый день
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Новый список подработок
        """
        return self.generate_daily_jobs(user_id)


# Вспомогательные функции для получения информации
def get_all_jobs() -> Dict:
    """Возвращает все доступные подработки"""
    return SIDE_JOBS


def get_categories() -> Dict:
    """Возвращает все категории"""
    return CATEGORIES


def get_job_by_id(job_id: str) -> Optional[Dict]:
    """Возвращает подработку по ID"""
    return SIDE_JOBS.get(job_id)
