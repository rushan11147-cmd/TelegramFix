# -*- coding: utf-8 -*-
"""
Тестовый скрипт для системы развлечений
"""

from entertainment_system import (
    RouletteEngine, DiceEngine, CrashEngine, 
    StatisticsManager, EntertainmentManager
)


def test_roulette():
    """Тест рулетки"""
    print("\n" + "="*50)
    print("🎰 ТЕСТ РУЛЕТКИ")
    print("="*50)
    
    engine = RouletteEngine()
    
    # Тест с разными ставками
    for bet in [100, 500, 1000]:
        print(f"\nСтавка: {bet}₽")
        result = engine.spin(bet, luck_level=1)
        print(f"Барабаны: {' '.join(result['reels'])}")
        print(f"Множитель: x{result['multiplier']}")
        print(f"Выплата: {result['payout']}₽")
        print(f"Настроение: {result['mood_change']:+d}")
        print(f"Результат: {'✅ Выигрыш' if result['won'] else '❌ Проигрыш'}")
    
    # Тест с удачей
    print(f"\n--- С удачей уровня 10 ---")
    result = engine.spin(500, luck_level=10)
    print(f"Барабаны: {' '.join(result['reels'])}")
    print(f"Множитель: x{result['multiplier']}")
    print(f"Выплата: {result['payout']}₽")


def test_dice():
    """Тест костей"""
    print("\n" + "="*50)
    print("🎲 ТЕСТ КОСТЕЙ")
    print("="*50)
    
    engine = DiceEngine()
    
    # Тест всех вариантов ставок
    for choice in ['low', 'seven', 'high']:
        print(f"\nВыбор: {choice.upper()}")
        result = engine.roll(500, choice, luck_level=1)
        print(f"Кубики: {result['dice1']} + {result['dice2']} = {result['sum']}")
        print(f"Выплата: {result['payout']}₽")
        print(f"Настроение: {result['mood_change']:+d}")
        print(f"Результат: {'✅ Выигрыш' if result['won'] else '❌ Проигрыш'}")
    
    # Тест с удачей
    print(f"\n--- С удачей уровня 10 ---")
    result = engine.roll(500, 'seven', luck_level=10)
    print(f"Кубики: {result['dice1']} + {result['dice2']} = {result['sum']}")
    print(f"Результат: {'✅ Выигрыш' if result['won'] else '❌ Проигрыш'}")


def test_crash():
    """Тест краша"""
    print("\n" + "="*50)
    print("📈 ТЕСТ КРАША")
    print("="*50)
    
    engine = CrashEngine()
    
    # Тест успешного забора
    print(f"\n--- Забрал на x2.0 ---")
    result = engine.play(1000, cash_out_multiplier=2.0, luck_level=1)
    print(f"Точка краша: x{result['crash_point']}")
    print(f"Забрал на: x{result['multiplier']}")
    print(f"Выплата: {result['payout']}₽")
    print(f"Настроение: {result['mood_change']:+d}")
    print(f"Результат: {'✅ Успел забрать' if result['cashed_out'] else '❌ Краш'}")
    
    # Тест краша
    print(f"\n--- Не успел забрать (краш) ---")
    result = engine.play(1000, cash_out_multiplier=None, luck_level=1)
    print(f"Точка краша: x{result['crash_point']}")
    print(f"Выплата: {result['payout']}₽")
    print(f"Настроение: {result['mood_change']:+d}")
    print(f"Результат: {'✅ Успел забрать' if result['cashed_out'] else '❌ Краш'}")
    
    # Тест с удачей
    print(f"\n--- С удачей уровня 10 ---")
    result = engine.play(1000, cash_out_multiplier=5.0, luck_level=10)
    print(f"Точка краша: x{result['crash_point']}")
    print(f"Результат: {'✅ Успел забрать' if result['cashed_out'] else '❌ Краш'}")


def test_statistics():
    """Тест статистики"""
    print("\n" + "="*50)
    print("📊 ТЕСТ СТАТИСТИКИ")
    print("="*50)
    
    manager = StatisticsManager()
    
    # Создаем тестовые данные пользователя
    user_data = {}
    
    # Записываем несколько игр
    manager.record_game(user_data, 'roulette', 100, 200, True)
    manager.record_game(user_data, 'roulette', 100, 0, False)
    manager.record_game(user_data, 'dice', 500, 1250, True)
    manager.record_game(user_data, 'dice', 500, 0, False)
    manager.record_game(user_data, 'crash', 1000, 2500, True)
    manager.record_game(user_data, 'crash', 1000, 0, False)
    
    # Получаем статистику
    stats = manager.get_statistics(user_data)
    
    print("\n📊 Статистика по играм:")
    for game_type in ['roulette', 'dice', 'crash']:
        game_stats = stats[game_type]
        print(f"\n{game_type.upper()}:")
        print(f"  Игр: {game_stats['games']}")
        print(f"  Выигрышей: {game_stats['wins']}")
        print(f"  Проигрышей: {game_stats['losses']}")
        print(f"  Поставлено: {game_stats['total_bet']}₽")
        print(f"  Выиграно: {game_stats['total_won']}₽")
        print(f"  Чистая прибыль: {game_stats['net_profit']:+d}₽")
    
    print(f"\n📈 ИТОГО:")
    totals = stats['totals']
    print(f"  Всего игр: {totals['games']}")
    print(f"  Выигрышей: {totals['wins']}")
    print(f"  Проигрышей: {totals['losses']}")
    print(f"  Чистая прибыль: {totals['net_profit']:+d}₽")


def test_probability_distribution():
    """Тест распределения вероятностей"""
    print("\n" + "="*50)
    print("📊 ТЕСТ РАСПРЕДЕЛЕНИЯ ВЕРОЯТНОСТЕЙ")
    print("="*50)
    
    engine = RouletteEngine()
    
    # Запускаем 1000 игр
    results = {'loss': 0, 'x2': 0, 'x5': 0, 'x10': 0}
    n = 1000
    
    print(f"\nЗапуск {n} игр в рулетку...")
    for _ in range(n):
        result = engine.spin(100, luck_level=1)
        if result['multiplier'] == 0:
            results['loss'] += 1
        elif result['multiplier'] == 2:
            results['x2'] += 1
        elif result['multiplier'] == 5:
            results['x5'] += 1
        elif result['multiplier'] == 10:
            results['x10'] += 1
    
    print(f"\n📊 Результаты:")
    print(f"Проигрыш: {results['loss']/n*100:.1f}% (ожидается ~60%)")
    print(f"x2: {results['x2']/n*100:.1f}% (ожидается ~25%)")
    print(f"x5: {results['x5']/n*100:.1f}% (ожидается ~10%)")
    print(f"x10: {results['x10']/n*100:.1f}% (ожидается ~5%)")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎮 ТЕСТИРОВАНИЕ СИСТЕМЫ РАЗВЛЕЧЕНИЙ")
    print("="*50)
    
    try:
        test_roulette()
        test_dice()
        test_crash()
        test_statistics()
        test_probability_distribution()
        
        print("\n" + "="*50)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
