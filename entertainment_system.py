# -*- coding: utf-8 -*-
"""
Система развлечений (Entertainment System)
Включает: Рулетка, Кости, Краш
"""

import random
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RouletteEngine:
    """Движок рулетки с 3 барабанами"""
    
    EMOJIS = ['🍒', '🍋', '🍊', '🍉', '⭐', '💎', '7️⃣']
    BET_OPTIONS = [100, 500, 1000]
    
    # Вероятности выигрыша
    PROBABILITIES = {
        'loss': 0.60,    # 60% - проигрыш
        'x2': 0.25,      # 25% - x2
        'x5': 0.10,      # 10% - x5
        'x10': 0.05      # 5% - x10
    }
    
    def spin(self, bet: int, luck_level: int = 1) -> Dict:
        """
        Крутит рулетку
        
        Args:
            bet: Ставка (100, 500, 1000)
            luck_level: Уровень удачи (1-10)
            
        Returns:
            dict с результатом
        """
        if bet not in self.BET_OPTIONS:
            raise ValueError(f"Ставка должна быть {self.BET_OPTIONS}")
        
        # Определяем исход
        outcome = self._determine_outcome(luck_level)
        
        # Генерируем барабаны
        reels = self._generate_reels(outcome)
        
        # Рассчитываем выплату
        multiplier = self._get_multiplier(outcome)
        payout = bet * multiplier if multiplier > 0 else 0
        
        # Изменение настроения
        mood_change = 5 if payout > 0 else -10
        
        return {
            'reels': reels,
            'multiplier': multiplier,
            'payout': payout,
            'mood_change': mood_change,
            'won': payout > 0
        }
    
    def _determine_outcome(self, luck_level: int) -> str:
        """Определяет исход с учетом удачи"""
        rand = random.random()
        
        # Удача немного сдвигает вероятности в пользу игрока
        luck_bonus = (luck_level - 1) * 0.01  # +1% за уровень
        
        if rand < self.PROBABILITIES['loss'] - luck_bonus:
            return 'loss'
        elif rand < self.PROBABILITIES['loss'] + self.PROBABILITIES['x2']:
            return 'x2'
        elif rand < self.PROBABILITIES['loss'] + self.PROBABILITIES['x2'] + self.PROBABILITIES['x5']:
            return 'x5'
        else:
            return 'x10'
    
    def _generate_reels(self, outcome: str) -> list:
        """Генерирует барабаны по исходу"""
        if outcome == 'loss':
            # Разные символы
            return random.sample(self.EMOJIS, 3)
        elif outcome == 'x2':
            # Два одинаковых
            symbol = random.choice(self.EMOJIS)
            reels = [symbol, symbol, random.choice([e for e in self.EMOJIS if e != symbol])]
            random.shuffle(reels)
            return reels
        else:
            # Три одинаковых
            symbol = random.choice(self.EMOJIS)
            return [symbol, symbol, symbol]
    
    def _get_multiplier(self, outcome: str) -> int:
        """Возвращает множитель по исходу"""
        multipliers = {'loss': 0, 'x2': 2, 'x5': 5, 'x10': 10}
        return multipliers.get(outcome, 0)


class DiceEngine:
    """Движок игры в кости"""
    
    MIN_BET = 100
    MAX_BET = 1000
    
    CHOICES = {
        'low': {'range': (2, 6), 'payout': 2.5},
        'seven': {'range': (7, 7), 'payout': 6.0},
        'high': {'range': (8, 12), 'payout': 2.5}
    }
    
    LUCK_BONUS_PER_LEVEL = 0.05  # +5% за уровень
    
    def roll(self, bet: int, choice: str, luck_level: int = 1) -> Dict:
        """
        Бросает кости
        
        Args:
            bet: Ставка (100-1000)
            choice: 'low', 'seven', 'high'
            luck_level: Уровень удачи (1-10)
            
        Returns:
            dict с результатом
        """
        if not self.MIN_BET <= bet <= self.MAX_BET:
            raise ValueError(f"Ставка должна быть {self.MIN_BET}-{self.MAX_BET}₽")
        
        if choice not in self.CHOICES:
            raise ValueError(f"Выбор должен быть: {list(self.CHOICES.keys())}")
        
        # Бросаем кости
        dice1, dice2 = self._roll_dice()
        dice_sum = dice1 + dice2
        
        # Проверяем выигрыш
        won = self._check_win(choice, dice_sum)
        
        # Применяем бонус удачи (шанс "подправить" результат)
        if not won and luck_level > 1:
            luck_chance = (luck_level - 1) * self.LUCK_BONUS_PER_LEVEL
            if random.random() < luck_chance:
                won = True
                logger.info(f"Luck bonus triggered! Level {luck_level}")
        
        # Рассчитываем выплату
        payout = int(bet * self.CHOICES[choice]['payout']) if won else 0
        
        # Изменение настроения
        mood_change = 3 if won else -5
        
        return {
            'dice1': dice1,
            'dice2': dice2,
            'sum': dice_sum,
            'won': won,
            'payout': payout,
            'mood_change': mood_change
        }
    
    def _roll_dice(self) -> Tuple[int, int]:
        """Бросает два кубика"""
        return random.randint(1, 6), random.randint(1, 6)
    
    def _check_win(self, choice: str, dice_sum: int) -> bool:
        """Проверяет выигрыш"""
        range_min, range_max = self.CHOICES[choice]['range']
        return range_min <= dice_sum <= range_max


class CrashEngine:
    """Движок игры Краш"""
    
    MIN_BET = 100
    MAX_BET = 5000
    
    MIN_CRASH = 1.1
    MAX_CRASH = 10.0
    
    def play(self, bet: int, cash_out_multiplier: Optional[float], luck_level: int = 1) -> Dict:
        """
        Играет в краш
        
        Args:
            bet: Ставка (100-5000)
            cash_out_multiplier: Множитель при котором игрок забрал (или None если краш)
            luck_level: Уровень удачи (1-10)
            
        Returns:
            dict с результатом
        """
        if not self.MIN_BET <= bet <= self.MAX_BET:
            raise ValueError(f"Ставка должна быть {self.MIN_BET}-{self.MAX_BET}₽")
        
        # Определяем точку краша
        crash_point = self._determine_crash_point(luck_level)
        
        # Проверяем забрал ли игрок до краша
        if cash_out_multiplier is not None and cash_out_multiplier <= crash_point:
            # Успешно забрал
            payout = int(bet * cash_out_multiplier)
            mood_change = 10 if cash_out_multiplier >= 5.0 else 5
            cashed_out = True
        else:
            # Краш
            payout = 0
            mood_change = -15
            cashed_out = False
        
        return {
            'crash_point': round(crash_point, 2),
            'cashed_out': cashed_out,
            'multiplier': cash_out_multiplier if cashed_out else 0,
            'payout': payout,
            'mood_change': mood_change,
            'won': cashed_out
        }
    
    def _determine_crash_point(self, luck_level: int) -> float:
        """
        Определяет точку краша с учетом удачи
        
        Использует экспоненциальное распределение, сдвинутое удачей
        """
        # Базовое распределение (больше низких значений)
        # Используем экспоненциальное распределение
        base_crash = random.expovariate(0.5)  # Среднее ~2.0
        
        # Удача сдвигает среднее вверх
        luck_bonus = (luck_level - 1) * 0.1  # +10% за уровень
        crash_point = base_crash * (1 + luck_bonus)
        
        # Ограничиваем диапазон
        crash_point = max(self.MIN_CRASH, min(self.MAX_CRASH, crash_point))
        
        return crash_point


class StatisticsManager:
    """Менеджер статистики игр"""
    
    def record_game(self, user_data: Dict, game_type: str, bet: int, payout: int, won: bool) -> None:
        """
        Записывает игру в статистику
        
        Args:
            user_data: Данные пользователя
            game_type: 'roulette', 'dice', 'crash'
            bet: Ставка
            payout: Выплата
            won: Выиграл ли
        """
        if 'entertainment_stats' not in user_data:
            user_data['entertainment_stats'] = {}
        
        if game_type not in user_data['entertainment_stats']:
            user_data['entertainment_stats'][game_type] = {
                'games': 0,
                'wins': 0,
                'losses': 0,
                'total_bet': 0,
                'total_won': 0
            }
        
        stats = user_data['entertainment_stats'][game_type]
        stats['games'] += 1
        stats['total_bet'] += bet
        stats['total_won'] += payout
        
        if won:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
    
    def get_statistics(self, user_data: Dict) -> Dict:
        """
        Получает статистику
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            dict со статистикой
        """
        stats = user_data.get('entertainment_stats', {})
        
        # Рассчитываем общую статистику
        totals = {
            'games': 0,
            'wins': 0,
            'losses': 0,
            'total_bet': 0,
            'total_won': 0,
            'net_profit': 0
        }
        
        result = {}
        for game_type in ['roulette', 'dice', 'crash']:
            game_stats = stats.get(game_type, {
                'games': 0,
                'wins': 0,
                'losses': 0,
                'total_bet': 0,
                'total_won': 0
            })
            
            game_stats['net_profit'] = game_stats['total_won'] - game_stats['total_bet']
            result[game_type] = game_stats
            
            # Добавляем к общей статистике
            for key in totals:
                if key in game_stats:
                    totals[key] += game_stats[key]
        
        result['totals'] = totals
        return result


class EntertainmentManager:
    """Главный менеджер системы развлечений"""
    
    def __init__(self, get_user_func, save_user_func):
        """
        Args:
            get_user_func: Функция для получения данных пользователя
            save_user_func: Функция для сохранения данных пользователя
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
        self.roulette_engine = RouletteEngine()
        self.dice_engine = DiceEngine()
        self.crash_engine = CrashEngine()
        self.stats_manager = StatisticsManager()
    
    def play_roulette(self, user_id: str, bet: int) -> Dict:
        """Играет в рулетку"""
        return self._play_game(user_id, 'roulette', bet, {})
    
    def play_dice(self, user_id: str, bet: int, choice: str) -> Dict:
        """Играет в кости"""
        return self._play_game(user_id, 'dice', bet, {'choice': choice})
    
    def play_crash(self, user_id: str, bet: int, cash_out_multiplier: Optional[float]) -> Dict:
        """Играет в краш"""
        return self._play_game(user_id, 'crash', bet, {'cash_out_multiplier': cash_out_multiplier})
    
    def get_statistics(self, user_id: str) -> Dict:
        """Получает статистику"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'Пользователь не найден'}
        
        stats = self.stats_manager.get_statistics(user)
        return {'success': True, 'stats': stats}
    
    def _play_game(self, user_id: str, game_type: str, bet: int, params: Dict) -> Dict:
        """
        Общая логика игры
        
        Args:
            user_id: ID пользователя
            game_type: Тип игры
            bet: Ставка
            params: Параметры игры
            
        Returns:
            dict с результатом
        """
        # Загружаем пользователя
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'Пользователь не найден'}
        
        # Проверяем баланс
        current_money = user.get('money', 0)
        if current_money < bet:
            return {
                'success': False,
                'error': f'Недостаточно денег! (нужно {bet}₽, есть {current_money}₽)'
            }
        
        # Списываем ставку
        user['money'] -= bet
        
        # Получаем уровень удачи
        luck_level = user.get('skills', {}).get('luck', 1)
        
        # Играем
        if game_type == 'roulette':
            result = self.roulette_engine.spin(bet, luck_level)
        elif game_type == 'dice':
            result = self.dice_engine.roll(bet, params['choice'], luck_level)
        elif game_type == 'crash':
            result = self.crash_engine.play(bet, params.get('cash_out_multiplier'), luck_level)
        else:
            return {'success': False, 'error': 'Неизвестная игра'}
        
        # Добавляем выигрыш
        user['money'] += result['payout']
        
        # Обновляем настроение
        user['mood'] = max(0, min(100, user.get('mood', 50) + result['mood_change']))
        
        # Записываем статистику
        self.stats_manager.record_game(user, game_type, bet, result['payout'], result['won'])
        
        # Сохраняем
        self.save_user(user_id, user)
        
        # Формируем ответ
        return {
            'success': True,
            'result': result,
            'user': {
                'money': user['money'],
                'mood': user['mood']
            },
            'message': self._get_message(game_type, result)
        }
    
    def _get_message(self, game_type: str, result: Dict) -> str:
        """Генерирует сообщение о результате"""
        if game_type == 'roulette':
            if result['won']:
                return f"🎰 Выигрыш x{result['multiplier']}! +{result['payout']}₽"
            else:
                return "🎰 Не повезло... Попробуй еще!"
        
        elif game_type == 'dice':
            if result['won']:
                return f"🎲 Выпало {result['sum']}! Выигрыш +{result['payout']}₽"
            else:
                return f"🎲 Выпало {result['sum']}... Не угадал!"
        
        elif game_type == 'crash':
            if result['cashed_out']:
                return f"📈 Забрал на x{result['multiplier']}! +{result['payout']}₽"
            else:
                return f"📈 Краш на x{result['crash_point']}! Не успел..."
        
        return "Игра завершена"
