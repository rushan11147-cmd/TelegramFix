# Implementation Plan: Economy Balancing System

## Overview

Реализация системы балансировки экономики для игры "Выживи до зарплаты". План разбит на инкрементальные шаги, каждый из которых добавляет функциональность и может быть протестирован независимо. Система интегрируется с существующими модулями (business_system, side_jobs_system, entertainment_system) и следует их архитектурным паттернам.

## Tasks

- [x] 1. Create configuration module
  - Создать файл balance_config.py с всеми параметрами балансировки
  - Определить константы для расходов, доходов, уровней богатства, событий
  - Добавить документацию для каждого параметра
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 2. Implement ExpenseCalculator
  - [x] 2.1 Create ExpenseCalculator class with expense calculation logic
    - Реализовать calculate_daily_expenses() - расчет всех расходов
    - Реализовать calculate_rent() - расчет аренды (monthly_rent / 30)
    - Реализовать get_base_expenses() - базовые расходы (еда, транспорт)
    - Применить wealth tier multiplier к итоговым расходам
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.8, 6.1_
  
  - [x] 2.2 Write property test for expense calculation correctness
    - **Property 1: Daily expense calculation correctness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 6.1**
  
  - [x] 2.3 Write unit tests for ExpenseCalculator
    - Тест расчета аренды с различными значениями monthly_rent
    - Тест минимальных значений для еды и транспорта
    - Тест применения wealth tier multiplier
    - _Requirements: 1.2, 1.3, 1.4, 4.8_

- [x] 3. Implement WealthTierManager
  - [x] 3.1 Create WealthTierManager class with tier classification
    - Реализовать get_wealth_tier() - определение уровня по балансу
    - Реализовать get_expense_multiplier() - получение множителя
    - Реализовать check_tier_change() - проверка изменения уровня
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [x] 3.2 Write property test for wealth tier classification
    - **Property 7: Wealth tier classification**
    - **Validates: Requirements 4.1**
  
  - [x] 3.3 Write property test for expense multiplier application
    - **Property 8: Expense multiplier application**
    - **Validates: Requirements 4.8**
  
  - [x] 3.4 Write unit tests for tier boundaries
    - Тест граничных значений (0, 3000, 3001, 10000, 10001)
    - Тест корректных множителей для каждого уровня
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 4. Implement DebtTracker
  - [x] 4.1 Create DebtTracker class with debt management
    - Реализовать track_debt() - отслеживание долга и дней в долге
    - Реализовать get_debt_amount() - получение суммы долга
    - Реализовать get_debt_days() - получение дней в долге
    - Реализовать should_trigger_collector() - проверка триггера коллектора
    - Реализовать calculate_collector_cost() - расчет стоимости коллектора
    - Реализовать get_event_probability_modifier() - модификатор вероятности
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 4.2 Write property test for debt tracking
    - **Property 12: Debt tracking**
    - **Validates: Requirements 7.1**
  
  - [x] 4.3 Write property test for negative balance handling
    - **Property 2: Negative balance handling**
    - **Validates: Requirements 1.5, 7.2**
  
  - [x] 4.4 Write property test for debt event probability increase
    - **Property 13: Debt event probability increase**
    - **Validates: Requirements 7.3**
  
  - [x] 4.5 Write unit tests for debt collector trigger
    - Тест триггера после 7 дней в долге
    - Тест расчета стоимости коллектора (20% от долга)
    - _Requirements: 7.4_

- [x] 5. Implement NegativeEventManager
  - [x] 5.1 Create NegativeEventManager class with event logic
    - Реализовать should_trigger_event() - проверка триггера события
    - Реализовать select_random_event() - выбор случайного события
    - Реализовать calculate_event_cost() - расчет стоимости события
    - Реализовать apply_event() - применение события к игроку
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 5.2 Write property test for event probability
    - **Property 4: Negative event probability**
    - **Validates: Requirements 3.1**
  
  - [x] 5.3 Write property test for event pool membership
    - **Property 5: Event pool membership**
    - **Validates: Requirements 3.2**
  
  - [x] 5.4 Write property test for event cost deduction
    - **Property 6: Event cost deduction**
    - **Validates: Requirements 3.7**
  
  - [x] 5.5 Write unit tests for event types
    - Тест наличия всех типов событий (medical, fine, equipment, bill)
    - Тест диапазонов стоимости для каждого типа
    - _Requirements: 3.3, 3.4, 3.5, 3.6_

- [x] 6. Checkpoint - Core components complete
  - Убедиться что все базовые компоненты работают
  - Запустить все тесты
  - Спросить пользователя если возникли вопросы

- [x] 7. Implement FinancialHistoryManager
  - [x] 7.1 Create FinancialHistoryManager class with history tracking
    - Реализовать record_daily_expenses() - запись расходов
    - Реализовать record_daily_income() - запись доходов
    - Реализовать record_negative_event() - запись событий
    - Реализовать record_tier_change() - запись изменений уровня
    - Реализовать get_history() - получение истории за N дней
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 7.2 Write property test for history persistence
    - **Property 15: Financial history persistence**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
  
  - [x] 7.3 Write property test for history retrieval window
    - **Property 16: History retrieval window**
    - **Validates: Requirements 10.5**
  
  - [x] 7.4 Write unit tests for history operations
    - Тест записи каждого типа операции
    - Тест получения истории за разные периоды (7, 14, 30 дней)
    - Тест автоматической очистки старых записей
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 8. Implement BalanceManager (Main Orchestrator)
  - [x] 8.1 Create BalanceManager class with orchestration logic
    - Инициализировать все sub-managers
    - Реализовать process_new_day() - обработка нового дня
    - Реализовать apply_job_income() - применение дохода от работы
    - Реализовать get_financial_summary() - получение финансовой сводки
    - Интегрировать все компоненты в единый workflow
    - _Requirements: 1.1, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.7, 4.1, 4.8, 5.1, 5.5, 6.1, 6.2, 7.1, 7.3, 10.1, 10.2, 10.3, 10.4_
  
  - [x] 8.2 Write property test for job income rates
    - **Property 3: Job income rates**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
  
  - [x] 8.3 Write property test for expense to income ratio
    - **Property 9: Expense to income ratio**
    - **Validates: Requirements 5.1**
  
  - [x] 8.4 Write property test for net income calculation
    - **Property 10: Net income calculation**
    - **Validates: Requirements 5.5**
  
  - [x] 8.5 Write property test for expense breakdown persistence
    - **Property 11: Expense breakdown persistence**
    - **Validates: Requirements 6.2**
  
  - [x] 8.6 Write unit tests for daily cycle
    - Тест полного цикла нового дня
    - Тест применения дохода от работы
    - Тест получения финансовой сводки
    - _Requirements: 1.1, 2.5, 5.5, 6.2_

- [x] 9. Checkpoint - Core system complete
  - Убедиться что BalanceManager корректно координирует все компоненты
  - Запустить все тесты
  - Спросить пользователя если возникли вопросы

- [x] 10. Integration with existing systems
  - [x] 10.1 Integrate with work system
    - Модифицировать обработку работы для использования новых ставок
    - Сохранить существующие затраты энергии
    - Применять доход через BalanceManager.apply_job_income()
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 8.1_
  
  - [x] 10.2 Integrate with property system
    - Использовать monthly_rent для расчета ежедневной аренды
    - Не изменять механику покупки/улучшения недвижимости
    - _Requirements: 1.2, 8.4_
  
  - [x] 10.3 Ensure business system income is not affected
    - Проверить что доход от бизнеса не уменьшается
    - Бизнес-доход должен обходить систему балансировки работы
    - _Requirements: 8.5_
  
  - [x] 10.4 Write property test for business income preservation
    - **Property 14: Business income preservation**
    - **Validates: Requirements 8.5**
  
  - [x] 10.5 Write integration tests
    - Тест интеграции с work system
    - Тест интеграции с property system
    - Тест интеграции с business system
    - Тест что side jobs и entertainment не затронуты
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [x] 11. Add API endpoints to app.py
  - [x] 11.1 Create balance summary endpoint
    - Добавить GET /api/balance/summary
    - Возвращать текущий финансовый статус игрока
    - _Requirements: 6.1, 6.2, 7.1_
  
  - [x] 11.2 Create financial history endpoint
    - Добавить GET /api/balance/history
    - Возвращать историю за последние 30 дней
    - _Requirements: 10.5_
  
  - [x] 11.3 Hook into daily cycle
    - Добавить вызов BalanceManager.process_new_day() в daily cycle
    - Обрабатывать расходы, события, обновление уровня богатства
    - _Requirements: 1.1, 3.1, 4.1, 7.1_
  
  - [x] 11.4 Write API endpoint tests
    - Тест balance summary endpoint
    - Тест financial history endpoint
    - Тест daily cycle integration

- [x] 12. Add UI components for balance display
  - [x] 12.1 Create expense breakdown display
    - Показывать детализацию расходов (аренда, еда, транспорт)
    - Показывать wealth tier и multiplier
    - Показывать итоговые расходы
    - _Requirements: 1.6, 6.3, 6.4, 6.5_
  
  - [x] 12.2 Create debt indicator
    - Показывать сумму долга когда баланс отрицательный
    - Показывать количество дней в долге
    - Визуально выделять критическое состояние (7+ дней)
    - _Requirements: 7.5_
  
  - [x] 12.3 Create financial history view
    - Показывать историю расходов, доходов, событий
    - Показывать изменения wealth tier
    - Добавить фильтры по типу операций
    - _Requirements: 10.5_

- [x] 13. Testing and validation
  - [x] 13.1 Run all property tests
    - Запустить все 16 property tests с минимум 100 итераций
    - Проверить что все properties выполняются
  
  - [x] 13.2 Run all unit tests
    - Запустить все unit tests
    - Проверить покрытие кода (target: 80%+)
  
  - [x] 13.3 Run integration tests
    - Проверить интеграцию со всеми существующими системами
    - Проверить что ничего не сломалось
  
  - [x] 13.4 Manual testing scenarios
    - Тест сценария: игрок не работает 3 дня → отрицательный баланс
    - Тест сценария: игрок не работает 5 дней → долг > 500₽
    - Тест сценария: игрок переходит между wealth tiers
    - Тест сценария: негативные события срабатывают ~25% времени
    - Тест сценария: debt collector появляется после 7 дней
    - _Requirements: 5.2, 5.3_

- [x] 14. Final checkpoint - System complete
  - Убедиться что все тесты проходят
  - Убедиться что все требования выполнены
  - Убедиться что интеграция работает корректно
  - Спросить пользователя о готовности к деплою

## Notes

- Все задачи являются обязательными для комплексной реализации
- Каждая задача ссылается на конкретные требования для отслеживаемости
- Checkpoints обеспечивают инкрементальную валидацию
- Property tests валидируют универсальные свойства корректности
- Unit tests валидируют конкретные примеры и граничные случаи
- Integration tests проверяют совместимость с существующими системами
